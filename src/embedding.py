"""Embedding backends.

- TfidfEmbedder (default): fully offline, no model download, good for a capstone demo.
- SentenceTransformerEmbedder: dense semantic embeddings (pip install sentence-transformers).
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np


def _normalize(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


class TfidfEmbedder:
    name = "tfidf"

    def __init__(self) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import FeatureUnion

        # Word n-grams capture phrases; character n-grams (within word boundaries) match
        # different forms of a word, e.g. "procrastinating" ~ "procrastination".
        self.vectorizer = FeatureUnion([
            ("words", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)),
            ("chars", TfidfVectorizer(analyzer="char_wb", ngram_range=(4, 5), sublinear_tf=True)),
        ])
        self._fitted = False

    def fit(self, texts: list[str]) -> "TfidfEmbedder":
        self.vectorizer.fit(texts)
        self._fitted = True
        return self

    def embed(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("TfidfEmbedder must be fit before embedding")
        return _normalize(self.vectorizer.transform(texts).toarray().astype(np.float32))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    @classmethod
    def load(cls, path: Path) -> "TfidfEmbedder":
        obj = cls()
        with open(path, "rb") as f:
            obj.vectorizer = pickle.load(f)
        obj._fitted = True
        return obj


class SentenceTransformerEmbedder:
    name = "sentence-transformers"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def fit(self, texts: list[str]) -> "SentenceTransformerEmbedder":
        return self  # pretrained; nothing to fit

    def embed(self, texts: list[str]) -> np.ndarray:
        vecs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return _normalize(vecs.astype(np.float32))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_name, encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "SentenceTransformerEmbedder":
        return cls(path.read_text(encoding="utf-8").strip())


def get_embedder(backend: str, st_model_name: str = "all-MiniLM-L6-v2"):
    if backend == "tfidf":
        return TfidfEmbedder()
    if backend == "sentence-transformers":
        return SentenceTransformerEmbedder(st_model_name)
    raise ValueError(f"Unknown embedding backend: {backend}")


def load_embedder(backend: str, embeddings_dir: Path):
    path = Path(embeddings_dir) / f"{backend}_embedder.pkl"
    if backend == "tfidf":
        return TfidfEmbedder.load(path)
    if backend == "sentence-transformers":
        return SentenceTransformerEmbedder.load(path)
    raise ValueError(f"Unknown embedding backend: {backend}")


def embedder_path(backend: str, embeddings_dir: Path) -> Path:
    return Path(embeddings_dir) / f"{backend}_embedder.pkl"
