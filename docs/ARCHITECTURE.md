# System Architecture

## Overview
```
                    ┌──────────────────────────── Offline (indexing) ───────────────────────────┐
                    │  data/wellness_documents/*.md                                              │
                    │        │ document_loader.py  (front-matter metadata)                       │
                    │        ▼                                                                    │
                    │  chunking.py  (600-char chunks, 100 overlap, paragraph/sentence aware)     │
                    │        ▼                                                                    │
                    │  embedding.py (TF-IDF or sentence-transformers, L2-normalized)             │
                    │        ▼                                                                    │
                    │  vector_store.py  -> vector_db/vectors.npy + chunks.json (FAISS optional) │
                    └────────────────────────────────────────────────────────────────────────────┘

 User (Streamlit app.py / FastAPI api.py / cli.py)
   │ message
   ▼
 rag_pipeline.WellnessCompanion.chat()
   ├─1─► safety.assess_risk() ── crisis? ──► crisis_response()  (988 / 741741 / 911)  ──► user
   ├─2─► emotion.detect_emotion()  → label + intensity
   ├─3─► retriever.retrieve(query + emotion, top_k=4)  → excerpts + similarity scores
   ├─4─► prompts.build_user_turn(excerpts, emotion, message)
   ├─5─► llm.OpenAILLM.generate(append-only conversation)  ──(failure)──► offline_reply()
   └─6─► journal.add_entry()  (local SQLite mood/emotion log)
   ▼
 Reply + detected emotion + cited sources
```

## Components
| Module | Responsibility |
|---|---|
| `config.py` | All settings; reads `.env` |
| `document_loader.py` | Reads .md/.txt/.pdf, parses `title`/`topic` front matter |
| `chunking.py` | Overlapping chunks that respect boundaries |
| `embedding.py` | Pluggable embedders; saves and loads the fitted model |
| `vector_store.py` | Cosine search (NumPy or FAISS), persistence |
| `retriever.py` | Builds/loads the index; emotion-aware query expansion; similarity threshold |
| `safety.py` | Regex crisis screen + resources (runs before the LLM) |
| `emotion.py` | Lexicon emotion classifier with negation and intensifiers |
| `prompts.py` | System prompt (persona, boundaries, citation rule) + augmented user turn |
| `llm.py` | OpenAI Chat Completions call, refusal handling, offline template fallback |
| `journal.py` | SQLite journal, mood summary, reflection prompts, export/delete |
| `rag_pipeline.py` | Orchestrates the six steps; holds the conversation state |

## Key design decisions
1. **Safety outside the model.** Crisis handling is deterministic and runs first, so it works even if the API is down or the model misreads the message. The system prompt adds a second layer for indirect cases.
2. **Grounding with citations.** Excerpts are given to the model in `<knowledge_base>` tags, and it is told to cite titles in brackets and not invent facts when nothing relevant is retrieved.
3. **Emotion-aware retrieval.** Adding the detected emotion to the query moves emotion-specific coping content higher in the results.
4. **Offline-first embeddings.** TF-IDF needs no model download, so the project runs anywhere. The design allows switching to dense embeddings (`EMBEDDING_BACKEND=sentence-transformers`) as an experiment.
5. **Append-only conversation history.** Each turn's exact request and response blocks are kept unchanged, which keeps multi-turn context consistent.
6. **Model configuration.** The default is OpenAI `gpt-5.4-mini`, a low-cost model suited to short conversational replies. Refusals are caught and answered gently. The model can be changed with `OPENAI_MODEL` in `.env`.
7. **Graceful degradation.** Any API error produces a grounded template reply, not a crash.

## Data model (SQLite `entries`)
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| user_id | TEXT | local pseudonymous id |
| created_at | TEXT | ISO timestamp |
| kind | TEXT | `journal` / `chat` / `checkin` |
| text | TEXT | entry content |
| mood_rating | INTEGER | 1-10, optional |
| emotion | TEXT | detected label |
| intensity | REAL | 0-1 |

## Future work
- Transformer emotion classifier (e.g., trained on GoEmotions)
- Hybrid search (BM25 + dense) and cross-encoder re-ranking
- LLM-based secondary risk classifier, evaluated against the regex screen
- Encrypted-at-rest journal; multi-user authentication
- Localized crisis resources by region
