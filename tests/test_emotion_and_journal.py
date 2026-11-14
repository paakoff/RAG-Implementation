from src.emotion import detect_emotion
from src.journal import Journal


def test_detects_anxiety():
    assert detect_emotion("I'm so anxious and worried about my exam").label == "anxiety"


def test_detects_sadness():
    assert detect_emotion("I feel really lonely and sad").label == "sadness"


def test_negated_joy_is_not_joy():
    assert detect_emotion("I am not happy at all").label != "joy"


def test_neutral():
    assert detect_emotion("I went to the store").label == "neutral"


def test_journal_roundtrip(tmp_path):
    j = Journal(tmp_path / "j.db")
    j.add_entry("u1", "I felt grateful and calm today", mood_rating=8)
    j.add_entry("u1", "Stressed and overwhelmed by deadlines", mood_rating=4)
    s = j.mood_summary("u1")
    assert s["count"] == 2 and s["avg_mood"] == 6.0
    assert j.delete_all("u1") == 2
    assert j.entries("u1") == []
