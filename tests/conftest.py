import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import settings  # noqa: E402


@pytest.fixture
def cfg(tmp_path):
    """Settings that write index/journal to a temp dir and never call the API."""
    return replace(settings, embeddings_dir=tmp_path / "emb", vector_db_dir=tmp_path / "vdb",
                   user_data_dir=tmp_path / "user", offline_mode=True)
