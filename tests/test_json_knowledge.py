import json
from dataclasses import replace

from src.config import settings
from src.document_loader import load_documents, load_json_entries
from src.retriever import Retriever, index_is_stale

JSON_FILE = settings.documents_dir / "coping_strategies.json"


def test_json_file_is_valid_and_complete():
    entries = load_json_entries(JSON_FILE)
    assert len(entries) >= 10
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "entry ids must be unique"
    for e in entries:
        assert e["title"] and e["summary"] and e["steps"], e["id"]
        assert isinstance(e["emotions"], list)


def test_json_entries_become_documents():
    docs = [d for d in load_documents(settings.documents_dir) if d.metadata["source"] == JSON_FILE.name]
    assert len(docs) == len(load_json_entries(JSON_FILE))
    panic = next(d for d in docs if d.metadata["entry_id"] == "panic-attack-steps")
    assert panic.metadata["title"] == "Getting Through a Panic Attack"
    assert "Steps to try:" in panic.text


def test_json_content_is_retrieved(cfg):
    r = Retriever(cfg, rebuild=True)
    titles = [h.source for h in r.retrieve("I keep procrastinating on my assignment", k=3)]
    assert "Breaking the Procrastination Cycle" in titles
    titles = [h.source for h in r.retrieve("I feel like an imposter in my program", k=3)]
    assert "Imposter Syndrome" in titles


def test_index_rebuilds_when_documents_change(cfg, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "a.md").write_text("Breathing slowly helps calm anxiety.", encoding="utf-8")
    c = replace(cfg, documents_dir=docs_dir)
    Retriever(c)
    assert not index_is_stale(c)
    (docs_dir / "b.json").write_text(json.dumps({"entries": [
        {"id": "x", "title": "Hiking", "summary": "Hiking in nature lifts mood.", "steps": ["Go outside."]}
    ]}), encoding="utf-8")
    import os, time
    future = time.time() + 5
    os.utime(docs_dir / "b.json", (future, future))
    assert index_is_stale(c)
    r = Retriever(c)
    assert "Hiking" in [h.source for h in r.retrieve("hiking in nature", k=2)]
