"""OpenAI chat model wrapper with an offline fallback for demos without an API key."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from .config import Settings, settings as default_settings
from .prompts import SYSTEM_PROMPT

log = logging.getLogger(__name__)

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


@dataclass
class LLMReply:
    text: str
    content: str = ""          # assistant message content to append to history
    model: str = "offline"
    stop_reason: str | None = None


class OpenAILLM:
    def __init__(self, cfg: Settings = default_settings) -> None:
        self.cfg = cfg
        self.client = None
        if cfg.offline_mode or openai is None:
            return
        if not os.getenv("OPENAI_API_KEY"):
            log.warning("OPENAI_API_KEY not set; using offline mode")
            return
        # Reads OPENAI_API_KEY from the environment. Request gzip rather than brotli:
        # older `brotli` packages are incompatible with the SDK's HTTP layer
        # ("process() takes no keyword arguments").
        self.client = openai.OpenAI(default_headers={"Accept-Encoding": "gzip, deflate"})

    @property
    def online(self) -> bool:
        return self.client is not None

    def generate(self, messages: list[dict]) -> LLMReply:
        """`messages` is the conversation so far (user/assistant turns, no system message)."""
        if not self.online:
            raise RuntimeError("offline")

        response = self.client.chat.completions.create(
            model=self.cfg.llm_model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            max_completion_tokens=self.cfg.llm_max_tokens,
        )
        choice = response.choices[0]
        refusal = getattr(choice.message, "refusal", None)
        if refusal:
            text = ("I'm not able to help with that one, but I'm still here for you. "
                    "Would you like to tell me more about how you're feeling?")
            return LLMReply(text=text, content=text, model=response.model, stop_reason="refusal")

        text = (choice.message.content or "").strip()
        if not text:
            raise RuntimeError(f"Empty response (finish_reason={choice.finish_reason})")
        return LLMReply(text=text, content=text, model=response.model, stop_reason=choice.finish_reason)



def offline_reply(emotion: str, excerpts: list[tuple[str, str]], reflection_question: str) -> str:
    """Template response used when no API key is available (demo/testing)."""
    openers = {
        "anxiety": "It sounds like there's a lot of worry sitting with you right now.",
        "sadness": "I'm sorry you're feeling this low. That sounds really heavy.",
        "anger": "It makes sense to feel frustrated when something feels unfair.",
        "stress": "It sounds like you're carrying a lot at the moment.",
        "shame": "It sounds like you're being really hard on yourself.",
        "joy": "That's wonderful to hear - I'm glad something is going well.",
        "neutral": "Thank you for sharing that with me.",
    }
    parts = [openers.get(emotion, openers["neutral"])]
    if excerpts:
        title, text = excerpts[0]
        snippet = text if len(text) < 350 else text[:350].rsplit(" ", 1)[0] + "..."
        parts.append(f"Here's something that might help [{title}]: {snippet}")
    parts.append(reflection_question)
    parts.append("_(Offline demo mode: set OPENAI_API_KEY in .env for full conversational responses.)_")
    return "\n\n".join(parts)
