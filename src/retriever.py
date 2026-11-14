"""Retriever: builds/loads the index and returns relevant knowledge chunks for a query."""
from __future__ import annotations

from dataclasses import dataclass

from .chunking import Chunk, chunk_documents
from .config import Settings, settings as default_settings
from .document_loader import load_documents
from .embedding import embedder_path, get_embedder, load_embedder
from .vector_store import VectorStore


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float

    @property
    def source(self) -> str:
        return self.chunk.metadata.get("title", self.chunk.metadata.get("source", "unknown"))


def build_index(cfg: Settings = default_settings) -> tuple[object, VectorStore]:
    """Load documents -> chunk -> embed -> persist. Returns (embedder, store)."""
    docs = load_documents(cfg.documents_dir)
    if not docs:
        raise RuntimeError(f"No documents found in {cfg.documents_dir}")
    chunks = chunk_documents(docs, cfg.chunk_size, cfg.chunk_overlap)
    texts = [c.text for c in chunks]

    embedder = get_embedder(cfg.embedding_backend, cfg.st_model_name).fit(texts)
    vectors = embedder.embed(texts)

    store = VectorStore()
    store.add(chunks, vectors)
    store.save(cfg.vector_db_dir)
    embedder.save(embedder_path(cfg.embedding_backend, cfg.embeddings_dir))
    return embedder, store


def index_is_stale(cfg: Settings) -> bool:
    """True if any knowledge-base file was added or changed after the index was built."""
    index_file = cfg.vector_db_dir / "vectors.npy"
    if not index_file.exists():
        return True
    built = index_file.stat().st_mtime
    return any(p.is_file() and p.stat().st_mtime > built for p in cfg.documents_dir.rglob("*"))


class Retriever:
    def __init__(self, cfg: Settings = default_settings, rebuild: bool = False) -> None:
        self.cfg = cfg
        emb_file = embedder_path(cfg.embedding_backend, cfg.embeddings_dir)
        if rebuild or not (VectorStore.exists(cfg.vector_db_dir) and emb_file.exists()) or index_is_stale(cfg):
            self.embedder, self.store = build_index(cfg)
        else:
            self.embedder = load_embedder(cfg.embedding_backend, cfg.embeddings_dir)
            self.store = VectorStore.load(cfg.vector_db_dir)

    def retrieve(self, query: str, k: int | None = None, emotion: str | None = None) -> list[RetrievedChunk]:
        """Return top-k chunks. If an emotion is detected, it is appended to the query
        so that emotion-specific coping content ranks higher."""
        k = k or self.cfg.top_k
        expanded = f"{query} {emotion}" if emotion and emotion != "neutral" else query
        q_vec = self.embedder.embed([expanded])[0]
        hits = self.store.search(q_vec, k=k)
        return [RetrievedChunk(c, s) for c, s in hits if s >= self.cfg.min_similarity]
