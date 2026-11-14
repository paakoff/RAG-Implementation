"""Central configuration. Values can be overridden with environment variables or a .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (avoids an extra dependency). Existing env vars win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    # Paths
    documents_dir: Path = ROOT_DIR / "data" / "wellness_documents"
    embeddings_dir: Path = ROOT_DIR / "embeddings"
    vector_db_dir: Path = ROOT_DIR / "vector_db"
    user_data_dir: Path = ROOT_DIR / "data" / "user_data"

    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "600"))          # characters
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))    # characters

    # Embeddings: "tfidf" (offline, default) or "sentence-transformers"
    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "tfidf")
    st_model_name: str = os.getenv("ST_MODEL_NAME", "all-MiniLM-L6-v2")

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "4"))
    min_similarity: float = float(os.getenv("MIN_SIMILARITY", "0.05"))

    # LLM (OpenAI)
    llm_model: str = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    llm_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
    offline_mode: bool = os.getenv("OFFLINE_MODE", "false").lower() == "true"


settings = Settings()
