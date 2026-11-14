"""Lightweight lexicon-based emotion detection (offline, explainable).

Returns a primary emotion label + intensity (0-1). Used to (1) steer retrieval toward
relevant coping content, (2) adapt tone, and (3) log mood for self-reflection trends.
Can be swapped for a transformer classifier (e.g. a GoEmotions model) in future work.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

LEXICON: dict[str, set[str]] = {
    "anxiety": {"anxious", "anxiety", "worried", "worry", "nervous", "panic", "panicking", "scared",
                "afraid", "fear", "overthinking", "tense", "restless", "uneasy", "dread", "exam", "deadline"},
    "sadness": {"sad", "down", "depressed", "unhappy", "cry", "crying", "hopeless", "empty", "lonely",
                "alone", "grief", "miss", "heartbroken", "low", "numb", "worthless"},
    "anger": {"angry", "mad", "furious", "annoyed", "frustrated", "irritated", "resent", "hate", "rage",
              "unfair", "pissed"},
    "stress": {"stressed", "stress", "overwhelmed", "pressure", "burnout", "burned", "exhausted",
               "tired", "busy", "swamped", "too much"},
    "joy": {"happy", "glad", "excited", "grateful", "thankful", "proud", "joy", "great", "good",
            "calm", "relieved", "peaceful", "hopeful", "love"},
    "shame": {"ashamed", "embarrassed", "guilty", "guilt", "stupid", "failure", "failed", "useless",
              "not good enough"},
}

INTENSIFIERS = {"very", "so", "really", "extremely", "incredibly", "totally", "completely", "always"}
NEGATIONS = {"not", "no", "never", "don't", "dont", "isn't", "isnt", "wasn't", "wasnt"}

# Mood score per emotion, for a -2..+2 mood trend chart
VALENCE = {"joy": 2, "neutral": 0, "stress": -1, "anxiety": -1, "anger": -1, "shame": -2, "sadness": -2}


@dataclass
class EmotionResult:
    label: str
    intensity: float
    scores: dict[str, float]

    @property
    def valence(self) -> int:
        return VALENCE.get(self.label, 0)


def detect_emotion(text: str) -> EmotionResult:
    lowered = text.lower()
    tokens = re.findall(r"[a-z']+", lowered)
    scores = {k: 0.0 for k in LEXICON}

    for i, tok in enumerate(tokens):
        window = tokens[max(0, i - 3):i]
        negated = any(w in NEGATIONS for w in window)
        boost = 1.5 if any(w in INTENSIFIERS for w in window) else 1.0
        for emo, words in LEXICON.items():
            if tok in words:
                if negated and emo == "joy":
                    scores["sadness"] += 0.5 * boost  # "not happy"
                elif not negated:
                    scores[emo] += boost

    # multi-word phrases
    for emo, words in LEXICON.items():
        for w in words:
            if " " in w and w in lowered:
                scores[emo] += 1.0

    best = max(scores, key=scores.get)
    total = sum(scores.values())
    if scores[best] == 0:
        return EmotionResult("neutral", 0.0, scores)
    intensity = min(1.0, scores[best] / 3.0)
    return EmotionResult(best, round(intensity, 2), {k: round(v / total, 2) for k, v in scores.items()})
