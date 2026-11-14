"""End-to-end RAG pipeline for the emotional wellness companion.

Flow for each user message:
  1. Safety screen (crisis -> immediate human resources, LLM bypassed)
  2. Emotion detection (label + intensity)
  3. Retrieval of relevant wellness knowledge (query expanded with emotion)
  4. Prompt augmentation (excerpts + emotion + message)
  5. Generation with OpenAI (or offline template)
  6. Logging to the private journal/mood log
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .config import Settings, settings as default_settings
from .emotion import detect_emotion
from .journal import Journal
from .llm import OpenAILLM, offline_reply
from .prompts import build_user_turn
from .retriever import Retriever
from .safety import assess_risk, crisis_response

log = logging.getLogger(__name__)


@dataclass
class CompanionResponse:
    text: str
    emotion: str
    intensity: float
    is_crisis: bool = False
    sources: list[dict] = field(default_factory=list)
    model: str = "offline"


class Conversation:
    """Holds the exact messages sent to / received from the API (append-only),
    plus a display transcript for the UI."""

    def __init__(self) -> None:
        self.api_messages: list[dict] = []
        self.transcript: list[dict] = []  # {"role", "content"} plain text for display


class WellnessCompanion:
    def __init__(self, cfg: Settings = default_settings, user_id: str = "local-user",
                 retriever: Retriever | None = None, llm: OpenAILLM | None = None,
                 journal: Journal | None = None) -> None:
        self.cfg = cfg
        self.user_id = user_id
        self.retriever = retriever or Retriever(cfg)
        self.llm = llm or OpenAILLM(cfg)
        self.journal = journal or Journal(cfg.user_data_dir / "journal.db")

    def chat(self, message: str, convo: Conversation, log_to_journal: bool = True) -> CompanionResponse:
        message = message.strip()
        if not message:
            raise ValueError("Empty message")

        emo = detect_emotion(message)
        risk = assess_risk(message)
        if log_to_journal:
            self.journal.add_entry(self.user_id, message, kind="chat")

        convo.transcript.append({"role": "user", "content": message})

        # 1. Safety first: never depend on the model for crisis handling.
        if risk.is_crisis:
            text = crisis_response(risk)
            convo.transcript.append({"role": "assistant", "content": text})
            return CompanionResponse(text, emo.label, emo.intensity, is_crisis=True, model="safety-layer")

        # 2-3. Retrieve knowledge
        hits = self.retriever.retrieve(message, emotion=emo.label)
        excerpts = [(h.source, h.chunk.text) for h in hits]
        sources = [{"title": h.source, "file": h.chunk.metadata.get("source"),
                    "score": round(h.score, 3)} for h in hits]

        # 4-5. Generate
        user_turn = build_user_turn(message, excerpts, emo.label, emo.intensity)
        text, model = None, "offline"
        if self.llm.online:
            try:
                pending = convo.api_messages + [{"role": "user", "content": user_turn}]
                reply = self.llm.generate(pending)
                convo.api_messages = pending + [{"role": "assistant", "content": reply.content}]
                text, model = reply.text, reply.model
            except Exception as exc:  # network/auth/rate-limit -> degrade gracefully
                log.error("OpenAI call failed: %s", exc)
        if text is None:
            text = offline_reply(emo.label, excerpts, Journal.reflection_prompt(emo.label))

        convo.transcript.append({"role": "assistant", "content": text})
        return CompanionResponse(text, emo.label, emo.intensity, sources=sources, model=model)
