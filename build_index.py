"""Build (or rebuild) the vector index from data/wellness_documents.

Usage:  python build_index.py
"""
from src.config import settings
from src.retriever import build_index

if __name__ == "__main__":
    _, store = build_index(settings)
    print(f"Indexed {len(store.chunks)} chunks from {settings.documents_dir}")
    print(f"Vector store -> {settings.vector_db_dir}")
    print(f"Embedder ({settings.embedding_backend}) -> {settings.embeddings_dir}")
