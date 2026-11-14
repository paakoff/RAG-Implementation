"""Private, local journal + mood log (SQLite). Supports self-reflection features:
journal entries, mood check-ins, trend summaries and data export/deletion.
Data never leaves the device except the text the user sends to the companion chat.
"""
from __future__ import annotations

import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .emotion import detect_emotion

REFLECTION_PROMPTS = {
    "anxiety": ["What is the worry telling you will happen? How likely is it, honestly?",
                "What is one small thing within your control today?"],
    "sadness": ["What would you say to a close friend who felt the way you feel right now?",
                "When did you last feel even slightly lighter? What was different?"],
    "anger": ["What boundary or value of yours feels crossed?",
              "What do you need right now that you are not getting?"],
    "stress": ["If you could drop one task this week, which would it be?",
               "What does 'good enough' look like for the thing stressing you most?"],
    "shame": ["Is this a mistake you made, or something you are? What's the difference?",
              "What would self-compassion sound like here?"],
    "joy": ["What contributed to this good feeling? How could you create more of it?",
            "Who would you like to share this moment with?"],
    "neutral": ["What is one thing you're grateful for today?",
                "What has been taking up the most space in your mind this week?"],
}


class Journal:
    def __init__(self, db_path: Path) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS entries (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id TEXT NOT NULL,
                   created_at TEXT NOT NULL,
                   kind TEXT NOT NULL,            -- 'journal' | 'checkin' | 'chat'
                   text TEXT,
                   mood_rating INTEGER,           -- 1..10 self-reported (optional)
                   emotion TEXT,
                   intensity REAL)"""
        )
        self.conn.commit()

    def add_entry(self, user_id: str, text: str, kind: str = "journal", mood_rating: int | None = None) -> dict:
        emo = detect_emotion(text or "")
        now = datetime.now().isoformat(timespec="seconds")
        cur = self.conn.execute(
            "INSERT INTO entries (user_id, created_at, kind, text, mood_rating, emotion, intensity) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, now, kind, text, mood_rating, emo.label, emo.intensity),
        )
        self.conn.commit()
        return {"id": cur.lastrowid, "created_at": now, "emotion": emo.label, "intensity": emo.intensity}

    def entries(self, user_id: str, days: int = 30, kind: str | None = None) -> list[dict]:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        q = "SELECT id, created_at, kind, text, mood_rating, emotion, intensity FROM entries WHERE user_id=? AND created_at>=?"
        params: list = [user_id, since]
        if kind:
            q += " AND kind=?"
            params.append(kind)
        rows = self.conn.execute(q + " ORDER BY created_at", params).fetchall()
        cols = ["id", "created_at", "kind", "text", "mood_rating", "emotion", "intensity"]
        return [dict(zip(cols, r)) for r in rows]

    def mood_summary(self, user_id: str, days: int = 7) -> dict:
        rows = self.entries(user_id, days)
        if not rows:
            return {"count": 0, "top_emotion": None, "avg_mood": None, "distribution": {}}
        dist: dict[str, int] = {}
        for r in rows:
            dist[r["emotion"]] = dist.get(r["emotion"], 0) + 1
        ratings = [r["mood_rating"] for r in rows if r["mood_rating"] is not None]
        return {
            "count": len(rows),
            "top_emotion": max(dist, key=dist.get),
            "avg_mood": round(sum(ratings) / len(ratings), 1) if ratings else None,
            "distribution": dist,
        }

    @staticmethod
    def reflection_prompt(emotion: str = "neutral") -> str:
        return random.choice(REFLECTION_PROMPTS.get(emotion, REFLECTION_PROMPTS["neutral"]))

    def export(self, user_id: str) -> str:
        return json.dumps(self.entries(user_id, days=36500), indent=2)

    def delete_all(self, user_id: str) -> int:
        cur = self.conn.execute("DELETE FROM entries WHERE user_id=?", (user_id,))
        self.conn.commit()
        return cur.rowcount
