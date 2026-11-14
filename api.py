"""REST API (FastAPI).  Run:  uvicorn api:app --reload
Docs at http://127.0.0.1:8000/docs
"""
from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag_pipeline import Conversation, WellnessCompanion

app = FastAPI(title="AI Companion for Emotional Wellness", version="1.0.0")
companion = WellnessCompanion()
_sessions: dict[str, Conversation] = {}  # in-memory; use Redis/DB in production


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None


class JournalRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    mood_rating: int | None = Field(None, ge=1, le=10)


@app.get("/health")
def health():
    return {"status": "ok", "llm_online": companion.llm.online,
            "indexed_chunks": len(companion.retriever.store.chunks)}


@app.post("/chat")
def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    convo = _sessions.setdefault(sid, Conversation())
    r = companion.chat(req.message, convo)
    return {"session_id": sid, "response": r.text, "emotion": r.emotion, "intensity": r.intensity,
            "is_crisis": r.is_crisis, "sources": r.sources, "model": r.model}


@app.post("/journal")
def add_journal(req: JournalRequest):
    entry = companion.journal.add_entry(companion.user_id, req.text, "journal", req.mood_rating)
    entry["reflection_prompt"] = companion.journal.reflection_prompt(entry["emotion"])
    return entry


@app.get("/journal")
def list_journal(days: int = 30):
    return companion.journal.entries(companion.user_id, days, kind="journal")


@app.get("/mood/summary")
def mood_summary(days: int = 7):
    return companion.journal.mood_summary(companion.user_id, days)


@app.delete("/data")
def delete_data():
    return {"deleted": companion.journal.delete_all(companion.user_id)}


@app.delete("/session/{session_id}")
def end_session(session_id: str):
    if _sessions.pop(session_id, None) is None:
        raise HTTPException(404, "session not found")
    return {"ended": session_id}
