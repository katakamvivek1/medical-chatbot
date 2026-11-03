# Medical Chatbot (RAG) — work in progress

A chatbot that answers general health questions from a trusted medical source using
Retrieval-Augmented Generation (RAG). Built with Flask, LangChain and a vector database.

> General health information only — not medical advice.

## Progress
- [x] Day 1 — Flask app, chat UI, JSON API, tests
- [ ] Day 2 — Load and chunk medical documents
- [ ] Day 3 — RAG pipeline (embeddings + vector store + LLM)
- [ ] Day 4 — Docker, CI (GitHub Actions), live deployment
- [ ] Day 5 — Demo video and final README

## Run locally
```bash
python -m venv venv
# Windows: venv\Scripts\activate    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
python app.py               # open http://localhost:5000
pytest -q                   # run tests
```

## Project structure
```
app.py              Flask routes (/, /health, /api/chat)
src/chat.py         Chatbot logic (placeholder now, RAG on Day 3)
templates/          HTML page
static/             CSS + JavaScript (calls /api/chat)
tests/              pytest tests
```
