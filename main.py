import asyncio
import json
import logging
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from autogen import AssistantAgent, UserProxyAgent
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import BaseModel

# ---------- Data models ----------
class ReviewRequest(BaseModel):
    id: str
    code: str
    language: str          # free-form language tag

class ReviewResult(BaseModel):
    id: str
    review: str
    status: str = "completed"

# ---------- LangGraph state ----------
class GraphState(TypedDict):
    request: ReviewRequest
    review: str | None
    messages: List[dict]

# ---------- AutoGen agents ----------
OLLAMA_CONFIG = {
    "model": "gemma3:latest",
    "base_url": "http://localhost:11434/v1",
    "api_type": "ollama",
    "api_key": "ollama",
}

reviewer = AssistantAgent(
    name="CodeReviewer",
    system_message=(
        "You are a senior, language-agnostic code reviewer. "
        "Identify bugs, style issues, security flaws, and suggest concise fixes. "
        "Reply with bullet points and short code snippets when helpful."
    ),
    llm_config=OLLAMA_CONFIG,
)

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    llm_config=OLLAMA_CONFIG,
)

# ---------- LangGraph nodes ----------
def ingest(state: GraphState) -> GraphState:
    lang  = state["request"].language
    code  = state["request"].code
    prompt = (
        f"Review the following {lang} code for correctness, style, security, "
        f"and performance. Provide concise bullet points.\n\n```{lang}\n{code}\n```"
    )
    state["messages"] = [{"role": "user", "content": prompt}]
    return state

def run_review(state: GraphState) -> GraphState:
    user_proxy.initiate_chat(
        reviewer,
        message=state["messages"][0]["content"],
        clear_history=True,
    )
    last = user_proxy.last_message()["content"]
    state["review"] = last
    return state

# ---------- Build workflow ----------
workflow = StateGraph(GraphState)
workflow.add_node("ingest", ingest)
workflow.add_node("run_review", run_review)
workflow.set_entry_point("ingest")
workflow.add_edge("ingest", "run_review")
workflow.add_edge("run_review", END)
app = workflow.compile()

# ---------- Kafka config ----------
KAFKA_BOOTSTRAP = "localhost:9092"
IN_TOPIC  = "code_review_requests"
OUT_TOPIC = "code_review_results"

def safe_deserializer(raw):
    if raw is None:
        return None
    try:
        return json.loads(raw.decode())
    except Exception as e:
        logging.warning("Bad Kafka message skipped: %s", e)
        return None

async def consume_and_process():
    consumer = AIOKafkaConsumer(
        IN_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=safe_deserializer,
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await consumer.start()
    await producer.start()
    logging.info("Kafka consumer/producer started.")

    try:
        async for msg in consumer:
            if msg.value is None:
                continue
            try:
                req = ReviewRequest(**msg.value)
                state = GraphState(request=req, review=None, messages=[])
                final = await app.ainvoke(state)
                result = ReviewResult(
                    id=req.id,
                    review=final["review"] or "No review returned",
                )
                await producer.send_and_wait(OUT_TOPIC, result.model_dump())
                logging.info("Processed %s (%s)", req.id, req.language)
            except Exception as e:
                logging.exception("Error processing message %s", msg.value)
    finally:
        await consumer.stop()
        await producer.stop()

# ---------- Run ----------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_and_process())