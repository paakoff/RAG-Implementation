# 🌱 Ember: AI Companion for Emotional Wellness and Self-Reflection

A capstone project that uses **Retrieval-Augmented Generation (RAG)** with an **OpenAI** model to offer empathetic, evidence-informed emotional support. It also includes guided journaling, mood insights, and a safety layer that runs before the AI model.

> **Disclaimer:** Ember is not a therapist or crisis service. In an emergency call **911**; in the US call or text **988**; elsewhere visit **findahelpline.com**.

## Features
- **RAG chat:** retrieves from a curated wellness knowledge base (CBT, grounding, breathing, journaling, self-compassion, stress, sleep, anger, sadness, crisis resources) and cites its sources
- **Safety first:** crisis language is caught before the LLM is called, and crisis resources are returned right away
- **Emotion detection:** tailors tone and retrieval; logs emotions to show trends
- **Journal and insights:** private entries, mood ratings, reflection prompts, charts
- **Privacy:** local SQLite storage, consent screen, export and delete-all
- **Three interfaces:** Streamlit web app, FastAPI REST API, CLI
- **Offline demo mode:** runs without an API key

## Project structure
```
RAG-Implementation/
├── app.py                  # Streamlit web app
├── api.py                  # FastAPI REST API
├── cli.py                  # terminal chat
├── build_index.py          # (re)build the vector index
├── requirements.txt
├── .env.example
├── data/
│   ├── wellness_documents/ # knowledge base (Markdown with front matter)
│   └── user_data/          # local journal DB (git-ignored)
├── embeddings/             # saved embedder
├── vector_db/              # saved vectors + chunks
├── src/
│   ├── config.py
│   ├── document_loader.py
│   ├── chunking.py
│   ├── embedding.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── safety.py
│   ├── emotion.py
│   ├── journal.py
│   ├── prompts.py
│   ├── llm.py
│   └── rag_pipeline.py
├── tests/                  # pytest suite
└── docs/
    ├── PROJECT_PROPOSAL.md # problem, purpose, objectives, RQs, scope, ethics + disclaimer statements
    ├── REQUIREMENTS.md     # functional / non-functional / system requirements, use cases
    ├── ARCHITECTURE.md     # design and data flow
    ├── ETHICS_AND_SAFETY.md
    └── EVALUATION_PLAN.md
```

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

copy .env.example .env      # macOS/Linux: cp .env.example .env
# put your OpenAI API key in .env  (or set OFFLINE_MODE=true for a demo)

python build_index.py       # builds embeddings/ and vector_db/
```

## Run
```bash
streamlit run app.py        # web app at http://localhost:8501
uvicorn api:app --reload    # API docs at http://127.0.0.1:8000/docs
python cli.py               # terminal chat
pytest -q                   # tests
```

## Extend the knowledge base
Add `.md` files to `data/wellness_documents/` with front matter:
```markdown
---
title: Your Document Title
topic: anxiety
---
Content...
```
Or add structured entries to `data/wellness_documents/coping_strategies.json` (or any `.json` file there):
```json
{"entries": [{"id": "unique-id", "title": "Title", "topic": "anxiety",
  "emotions": ["anxiety"], "duration_minutes": 5, "summary": "...",
  "steps": ["...", "..."], "when_to_seek_help": "..."}]}
```
JSON entries are indexed for chat retrieval and shown in the **🧰 Toolkit** tab.

The index rebuilds automatically on startup when any knowledge file changes, or you can run `python build_index.py`.

## Configuration (`.env`)
| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | none | OpenAI API key |
| `OPENAI_MODEL` | `gpt-5.4-mini` | model |
| `OPENAI_MAX_TOKENS` | `4000` | max reply tokens |
| `OFFLINE_MODE` | `false` | template replies, no API |
| `EMBEDDING_BACKEND` | `tfidf` | or `sentence-transformers` |
| `TOP_K` | `4` | chunks retrieved |
