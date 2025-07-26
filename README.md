# Code-Review Pipeline

Real-time, LLM-powered code reviews using:

- **LangGraph** (state-machine)
- **AutoGen** (Assistant + UserProxy agents)
- **Gemma-3** via Ollama (local GPU/CPU)
- **Apache Kafka** (event bus)

## One-Sentence Pitch
A lightweight, event-driven code-review engine that turns any code snippet into instant, AI-generated feedback using **Gemma-3**, **LangGraph**, **AutoGen** agents, and **Apache Kafka**.

## What it does
1. **Ingest** – Drop a file or snippet into Kafka topic `code_review_requests`.
2. **Orchestrate** – LangGraph spins up two AutoGen agents (Reviewer + UserProxy).
3. **Analyse** – Gemma-3 (local LLM) produces bullet-point reviews.
4. **Deliver** – Results land in `code_review_results` as JSON, ready for webhooks, CI, or dashboards.

## Core Tech Stack

| Layer | Tool |
|-------|------|
| Workflow Engine | LangGraph |
| Agents | AutoGen AssistantAgent + UserProxyAgent |
| LLM | Gemma-3 via Ollama |
| Message Bus | Apache Kafka |
| Language | Python 3.10+ |
| Deployment | Docker Compose |

## Key Features
* **100% local** – no cloud keys, runs on Windows / macOS / Linux.
* **Scalable** – add more reviewers, queues, or GPU workers at will.
* **Extensible** – swap Gemma-3 for any Ollama model in one line.
* **CI-friendly** – JSON output integrates with GitHub Actions, Jenkins, or webhooks.

## Use-Cases
* Pre-commit hooks
* IDE extensions
* Classroom auto-grading
* OSS maintainers' nightly review batch

## Status
v1.0.0 – fully working on Windows 11; published under MIT license.

## Quick Start

1. **Start Kafka**  
   ```bash
   docker compose -f kafka.yaml up -d

## Pull model

```bash
ollama pull gemma3:latest
```

## 1. Run consumer

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 2. Send code

```bash
python send_file.py my_file.py
```

## Topics
* `code_review_requests` — incoming code
* `code_review_results` — JSON reviews

Create `requirements.txt`:

```text
pyautogen<0.4
langgraph
aiokafka
pydantic
ollama
```

Commit again:

```powershell
git add README.md requirements.txt
git commit -m "Add README and requirements"
git push
```

## 7️⃣ Verify on GitHub
Open https://github.com/Capybaralifestyle/code-review-pipeline – you should see:
* All files
* README rendered nicely
* Release `v1.0.0` under *Releases*

## 8️⃣ Share / Expand
* **Codespaces**: click "Code ▼ → Codespaces → New" → instant dev env
* **Docker Hub**: `docker build -t capybara/code-review .` → push
* **GitHub Actions**: add `.github/workflows/ci.yml` to test PRs

Done! 🎉
pydantic
ollama
Commit again:
powershell
Copy

git add README.md requirements.txt
git commit -m "Add README and requirements"
git push
7️⃣ Verify on GitHub
Open https://github.com/Capybaralifestyle/code-review-pipeline – you should see:
* All files
* README rendered nicely
* Release v1.0.0 under Releases
8️⃣ Share / Expand
* Codespaces: click “Code ▼ → Codespaces → New” → instant dev env
* Docker Hub: docker build -t capybara/code-review . → push
* GitHub Actions: add .github/workflows/ci.yml to test PRs
Done! 🎉
