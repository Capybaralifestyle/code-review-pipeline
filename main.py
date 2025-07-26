import asyncio
import json
import logging
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import BaseModel

# ---------- 1. Data models ----------
class ReviewRequest(BaseModel):
    id: str
    code: str
    language: str = "python"

class ReviewResult(BaseModel):
    id: str
    review: str
    status: str = "completed"

# ---------- 2. LangGraph state ----------
class GraphState(TypedDict):
    request: ReviewRequest
    review: str | None
    messages: List[dict]

# ---------- 3. AutoGen agents ----------
OLLAMA_CONFIG = {
    "model": "gemma3:latest",
    "base_url": "http://localhost:11434/v1",
    "api_type": "ollama",
    "api_key": "ollama",
}

reviewer = AssistantAgent(
    name="CodeReviewer",
    system_message="You are a strict code reviewer. "
                   "Return concise bullet points of issues and suggestions.",
    llm_config=OLLAMA_CONFIG,
)

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    llm_config=OLLAMA_CONFIG,
)

# ---------- 4. LangGraph nodes ----------
def ingest(state: GraphState) -> GraphState:
    code = state["request"].code
    prompt = f"Please review the following {state['request'].language} code:\n\n{code}"
    state["messages"] = [{"role": "user", "content": prompt}]
    return state

def run_review(state: GraphState) -> GraphState:
    user_proxy.initiate_chat(
        reviewer,
        message=state["messages"][0]["content"],
        clear_history=True,
    )
    last_message = user_proxy.last_message()["content"]
    state["review"] = last_message
    return state

# ---------- 5. Build the graph ----------
workflow = StateGraph(GraphState)
workflow.add_node("ingest", ingest)
workflow.add_node("run_review", run_review)
workflow.set_entry_point("ingest")
workflow.add_edge("ingest", "run_review")
workflow.add_edge("run_review", END)
app = workflow.compile()

# ---------- 6. Kafka plumbing ----------
KAFKA_BOOTSTRAP = "localhost:9092"
IN_TOPIC = "code_review_requests"
OUT_TOPIC = "code_review_results"

def safe_deserializer(raw):
    """Skip empty / bad JSON."""
    if raw is None:
        return None
    try:
        return json.loads(raw.decode())
    except Exception as e:
        logging.warning("Bad message skipped: %s", e)
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
            if msg.value is None:        # skip empty / bad messages
                continue
            try:
                req = ReviewRequest(**msg.value)
                state = GraphState(request=req, review=None, messages=[])
                final_state = await app.ainvoke(state)
                result = ReviewResult(
                    id=req.id,
                    review=final_state["review"] or "No review returned",
                )
                await producer.send_and_wait(OUT_TOPIC, result.dict())
                logging.info("Processed %s", req.id)
            except Exception as e:
                logging.exception("Error processing message %s", msg.value)
    finally:
        await consumer.stop()
        await producer.stop()

# ---------- 7. Run ----------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_and_process())