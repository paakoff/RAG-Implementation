import pytest

from src.chunking import chunk_documents, chunk_text
from src.document_loader import Document, load_documents
from src.config import settings


def test_chunks_respect_size():
    text = " ".join(f"Sentence number {i} is here." for i in range(200))
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)


def test_short_text_single_chunk():
    assert chunk_text("Hello there.", 600, 100) == ["Hello there."]


def test_overlap_must_be_smaller():
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=100, overlap=100)


def test_chunk_metadata_preserved():
    docs = [Document("Para one.\n\nPara two.", {"title": "T", "source": "t.md"})]
    chunks = chunk_documents(docs, 600, 100)
    assert chunks[0].metadata["title"] == "T"
    assert chunks[0].chunk_id == "t.md::0"


def test_knowledge_base_loads_with_front_matter():
    docs = load_documents(settings.documents_dir)
    assert len(docs) >= 10
    titles = {d.metadata["title"] for d in docs}
    assert "Grounding Techniques" in titles
    assert all(not d.text.startswith("---") for d in docs)
