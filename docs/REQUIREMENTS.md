# Requirements Specification
**AI Companion for Emotional Wellness and Self-Reflection**

## 1. Stakeholders
| Stakeholder | Interest |
|---|---|
| End users (adult students / young adults) | Accessible, private, supportive tool |
| Campus counseling services | Tool encourages help-seeking and sends crises to them |
| Capstone advisor / evaluators | Technical soundness, ethics, evaluation |
| Developer | Maintainable, testable system |

## 2. User Stories
- As a stressed student, I want to describe how I feel and get a supportive reply with a technique I can try right now.
- As a user, I want the companion to remember what I said earlier in the conversation so I don't have to repeat myself.
- As a user, I want to journal privately and rate my mood so I can see patterns over time.
- As a user, I want reflection prompts that fit what I'm feeling.
- As a user in crisis, I want to be shown how to reach a real person immediately.
- As a privacy-conscious user, I want to export or delete all my data.
- As an evaluator, I want to see which knowledge sources each reply was based on.

## 3. Functional Requirements
| ID | Requirement | Priority | Implemented in |
|---|---|---|---|
| FR-1 | Load wellness documents (.md, .txt, .json, .pdf) with metadata (title, topic, emotions, source) | Must | `src/document_loader.py` |
| FR-1a | Browse and filter structured coping strategies (JSON) by feeling or keyword in a Toolkit view | Should | `app.py` (Toolkit tab), `data/wellness_documents/coping_strategies.json` |
| FR-2 | Split documents into overlapping chunks at paragraph/sentence boundaries | Must | `src/chunking.py` |
| FR-3 | Generate embeddings for chunks and queries (TF-IDF default; sentence-transformers optional) | Must | `src/embedding.py` |
| FR-4 | Store and persist vectors; perform top-k cosine similarity search | Must | `src/vector_store.py` |
| FR-5 | Retrieve relevant chunks, expanding the query with the detected emotion | Must | `src/retriever.py` |
| FR-6 | Screen every user message for crisis language before calling the AI model | Must | `src/safety.py` |
| FR-7 | On crisis detection, return crisis resources (988, 741741, 911, findahelpline.com) and skip the AI model | Must | `src/safety.py`, `src/rag_pipeline.py` |
| FR-8 | Detect the primary emotion and its intensity in each message | Must | `src/emotion.py` |
| FR-9 | Build an augmented prompt (retrieved excerpts + emotion + message) and generate an empathetic reply with an OpenAI model | Must | `src/prompts.py`, `src/llm.py` |
| FR-10 | Keep multi-turn conversation context within a session | Must | `Conversation` in `src/rag_pipeline.py` |
| FR-11 | Show the sources used and the detected emotion with each reply | Should | `app.py`, `api.py` |
| FR-12 | Provide a private journal with optional 1-10 mood rating | Must | `src/journal.py` |
| FR-13 | Generate reflection prompts matched to the detected emotion | Should | `src/journal.py` |
| FR-14 | Show mood and emotion trends (charts, weekly summary) | Should | `app.py` (Insights tab) |
| FR-15 | Export all user data as JSON; delete all user data | Must | `src/journal.py`, `app.py`, `api.py` |
| FR-16 | Require informed consent and an 18+ confirmation before use | Must | `app.py` |
| FR-17 | Work in offline demo mode without an API key | Should | `src/llm.py` |
| FR-18 | Expose a REST API (chat, journal, mood summary, delete) | Could | `api.py` |
| FR-19 | Allow rebuilding the knowledge base index when documents change | Must | `build_index.py` |

## 4. Non-Functional Requirements
| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Safety | Crisis screening must have very high recall on the safety test set (target >= 95%); crisis responses never depend on model or network availability. |
| NFR-2 | Safety | The companion must not diagnose, prescribe, or claim to be a clinician (enforced through the system prompt and checked in evaluation). |
| NFR-3 | Privacy | Journal/mood data is stored locally (SQLite); no user data is sent anywhere except chat text to the LLM API. No accounts or identifying information required. |
| NFR-4 | Security | API keys come from environment variables / `.env` and are never committed (`.gitignore`). API inputs are length-validated. |
| NFR-5 | Performance | Retrieval < 200 ms on a laptop; end-to-end reply typically under ~10 s with the API. |
| NFR-6 | Reliability | If the AI model fails (network, rate limit, auth), the system falls back to a grounded template reply instead of crashing. |
| NFR-7 | Usability | Plain-language, warm tone; replies of about 80-180 words; one reflection question at most per reply. |
| NFR-8 | Accessibility | Web UI usable with keyboard and screen reader (Streamlit defaults); crisis info visible on every screen. |
| NFR-9 | Maintainability | Modular code (one responsibility per module); configuration in one place (`src/config.py`); automated tests. |
| NFR-10 | Transparency | Each reply cites the knowledge-base sources it used. |
| NFR-11 | Portability | Runs on Windows/macOS/Linux with Python 3.10+. |

## 5. System Requirements

### Software
| Component | Version / Notes |
|---|---|
| Python | 3.10+ (tested with 3.12) |
| openai (OpenAI SDK) | >= 1.40 |
| numpy, scikit-learn, pandas | embeddings, similarity, analytics |
| streamlit | web UI |
| fastapi, uvicorn, pydantic | REST API |
| pytest | testing |
| Optional: faiss-cpu, sentence-transformers, pypdf | faster search, dense embeddings, PDF loading |

### Hardware
- Minimum: dual-core CPU, 4 GB RAM, 500 MB disk
- Recommended (with sentence-transformers): 8 GB RAM
- Internet connection for the OpenAI API (not needed for offline demo mode)

### External services
- OpenAI API (model `gpt-5.4-mini` by default; configurable with `OPENAI_MODEL`)

## 6. Constraints and Assumptions
- Users are adults who agree to the disclaimer.
- The knowledge base is general psychoeducation, not clinical guidance.
- Keyword-based screening can miss indirect or coded expressions of risk; this is reduced by the model's own safety instructions and documented as a limitation.
- Crisis line numbers are US-focused, with an international directory link.

## 7. Use Cases
**UC-1: Supportive chat.** The user sends a message. The system screens it for safety, detects emotion, retrieves the top-k excerpts, and generates a reply with source citations. The reply is shown along with the emotion and sources.

**UC-2: Crisis message.** The user sends high-risk text. The safety layer matches it, the AI model is skipped, and a compassionate message with crisis resources is shown right away.

**UC-3: Journaling.** The user writes an entry and rates their mood. The system saves it, detects emotion, and returns a matching reflection prompt.

**UC-4: View insights.** The user opens Insights and sees an emotion distribution chart, a mood trend line, and a weekly summary with a reflection prompt.

**UC-5: Data control.** The user exports their data as JSON or deletes all of it.

## 8. Acceptance Criteria
- All tests in `tests/` pass (`pytest`).
- Every phrase in the crisis test set gives a crisis response that includes 988.
- Retrieval test queries return the expected document in the top 3.
- The app runs in offline mode without an API key.
- Deleting data removes all of the user's journal rows.
