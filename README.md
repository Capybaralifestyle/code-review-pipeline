# Code-Review Pipeline

Real-time, LLM-powered code reviews using:

- **LangGraph** (state-machine)
- **AutoGen** (Assistant + UserProxy agents)
- **Gemma-3** via Ollama (local GPU/CPU)
- **Apache Kafka** (event bus)

## Quick Start

1. **Start Kafka**  
   ```bash
   docker compose -f kafka.yaml up -d

## Pull model

```bash
ollama pull gemma3:4b
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
