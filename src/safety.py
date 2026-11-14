"""Crisis / risk detection. Runs BEFORE the LLM so that high-risk messages always get
human crisis resources, regardless of model availability.

This is a keyword/regex screen, intentionally tuned toward recall (it is better to show
resources unnecessarily than to miss a crisis). It is NOT a clinical risk assessment.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_PATTERNS: dict[str, list[str]] = {
    "suicide": [
        r"\bkill(ing)? my ?self\b", r"\bsuicid(e|al)\b", r"\bend (it all|my life)\b",
        r"\bwant(ed)? to die\b", r"\bdon'?t want to (live|be alive|exist)\b",
        r"\bbetter off (dead|without me)\b", r"\bno reason to live\b", r"\btake my (own )?life\b",
        r"\bnot wake up\b", r"\bgoodbye forever\b",
    ],
    "self_harm": [
        r"\b(cut|cutting|burn|burning|hurt|hurting|harm|harming) my ?self\b", r"\bself[- ]harm\b",
        r"\boverdos(e|ing)\b",
    ],
    "harm_to_others": [
        r"\b(kill|hurt|harm|shoot|stab) (him|her|them|someone|somebody|people|my \w+)\b",
    ],
    "abuse": [
        r"\b(he|she|they|my \w+) (hits|beats|abuses|hurts) me\b", r"\bbeing abused\b",
        r"\bsexually assaulted\b", r"\bnot safe at home\b",
    ],
}

_COMPILED = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in _PATTERNS.items()}

CRISIS_RESOURCES = (
    "**If you are in immediate danger, call 911 (or your local emergency number) now.**\n\n"
    "- **988 Suicide & Crisis Lifeline (US):** call or text **988**, or chat at 988lifeline.org\n"
    "- **Crisis Text Line (US/UK/CA/IE):** text **HOME** to **741741** (US/CA), 85258 (UK), 50808 (IE)\n"
    "- **Domestic violence (US):** 1-800-799-7233 or text START to 88788\n"
    "- **Outside the US:** find a local line at **findahelpline.com**\n"
    "- **On campus:** your university counseling center often offers same-day crisis appointments."
)


@dataclass
class SafetyResult:
    is_crisis: bool
    categories: list[str]
    matched: list[str]


def assess_risk(text: str) -> SafetyResult:
    cats, matched = [], []
    for cat, patterns in _COMPILED.items():
        for p in patterns:
            m = p.search(text)
            if m:
                cats.append(cat)
                matched.append(m.group(0))
                break
    return SafetyResult(is_crisis=bool(cats), categories=cats, matched=matched)


def crisis_response(result: SafetyResult) -> str:
    if "abuse" in result.categories and len(result.categories) == 1:
        opener = ("I'm really sorry this is happening to you. You deserve to be safe, "
                  "and what you're describing is not your fault.")
    elif "harm_to_others" in result.categories:
        opener = ("It sounds like you're carrying a lot of intense feelings right now. "
                  "Before anyone gets hurt, please reach out to someone who can help immediately.")
    else:
        opener = ("I'm really glad you told me, and I'm sorry you're hurting this much. "
                  "You don't have to go through this alone, and you deserve support from a person right now.")
    return (
        f"{opener}\n\nI'm an AI companion, not a crisis service, so please contact one of these "
        f"right away:\n\n{CRISIS_RESOURCES}\n\n"
        "If you can, reach out to someone you trust and let them know how you're feeling. "
        "I'm still here to talk with you while you get connected to help."
    )
