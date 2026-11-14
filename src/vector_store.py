"""A small persistent vector store using cosine similarity over normalized vectors.

Uses FAISS (IndexFlatIP) when installed for speed, otherwise pure NumPy.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .chunking import Chunk

try:  # optional acceleration
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None


class VectorStore:
    def __init__(self) -> None:
        self.vectors: np.ndarray | None = None
        self.chunks: list[Chunk] = []
        self._index = None

    # ---------- build ----------
    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        vectors = vectors.astype(np.float32)
        self.vectors = vectors if self.vectors is None else np.vstack([self.vectors, vectors])
        self.chunks.extend(chunks)
        self._build_index()

    def _build_index(self) -> None:
        if faiss is not None and self.vectors is not None and len(self.vectors):
            self._index = faiss.IndexFlatIP(self.vectors.shape[1])
            self._index.add(self.vectors)

    # ---------- query ----------
    def search(self, query_vector: np.ndarray, k: int = 4) -> list[tuple[Chunk, float]]:
        if self.vectors is None or not len(self.chunks):
            return []
        q = query_vector.reshape(1, -1).astype(np.float32)
        k = min(k, len(self.chunks))
        if self._index is not None:
            scores, idx = self._index.search(q, k)
            pairs = zip(idx[0].tolist(), scores[0].tolist())
        else:
            sims = (self.vectors @ q.T).ravel()
            top = np.argsort(-sims)[:k]
            pairs = ((int(i), float(sims[i])) for i in top)
        return [(self.chunks[i], float(s)) for i, s in pairs if i >= 0]

    # ---------- persistence ----------
    def save(self, directory: Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / "vectors.npy", self.vectors)
        records = [{"chunk_id": c.chunk_id, "text": c.text, "metadata": c.metadata} for c in self.chunks]
        (directory / "chunks.json").write_text(json.dumps(records, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        directory = Path(directory)
        store = cls()
        store.vectors = np.load(directory / "vectors.npy")
        records = json.loads((directory / "chunks.json").read_text(encoding="utf-8"))
        store.chunks = [Chunk(**r) for r in records]
        store._build_index()
        return store

    @staticmethod
    def exists(directory: Path) -> bool:
        directory = Path(directory)
        return (directory / "vectors.npy").exists() and (directory / "chunks.json").exists()
