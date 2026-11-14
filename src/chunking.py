"""Split documents into overlapping chunks, respecting paragraph/sentence boundaries."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .document_loader import Document


@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict = field(default_factory=dict)


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_units(text: str) -> list[str]:
    """Break text into paragraphs, and long paragraphs into sentences."""
    units: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(para.split())
        if para:
            units.append(para)
    return units


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    pieces: list[str] = []
    for unit in _split_units(text):
        if len(unit) <= chunk_size:
            pieces.append(unit)
        else:
            pieces.extend(s for s in _SENTENCE_SPLIT.split(unit) if s)

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        # A single sentence longer than chunk_size: hard-wrap it.
        while len(piece) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(piece[:chunk_size])
            piece = piece[chunk_size - overlap:]
        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            # start the tail on a word boundary
            tail = tail[tail.find(" ") + 1:] if " " in tail else tail
            current = f"{tail} {piece}".strip()
    if current:
        chunks.append(current)
    return chunks


def chunk_documents(docs: list[Document], chunk_size: int = 600, overlap: int = 100) -> list[Chunk]:
    out: list[Chunk] = []
    for doc in docs:
        for i, piece in enumerate(chunk_text(doc.text, chunk_size, overlap)):
            meta = dict(doc.metadata, chunk_index=i)
            out.append(Chunk(chunk_id=f"{doc.metadata.get('source', 'doc')}::{i}", text=piece, metadata=meta))
    return out
