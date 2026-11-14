"""Load wellness knowledge-base documents (.md, .txt, .json, optional .pdf) with metadata."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Document:
    text: str
    metadata: dict = field(default_factory=dict)


_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_front_matter(raw: str) -> tuple[dict, str]:
    """Parse simple `key: value` front matter at the top of a markdown file."""
    match = _FRONT_MATTER.match(raw)
    if not match:
        return {}, raw
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, raw[match.end():]


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # optional dependency
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install pypdf to load PDF documents: pip install pypdf") from exc
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_json_entries(path: Path) -> list[dict]:
    """Return the `entries` list from a JSON knowledge file (or the top-level list)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = data.get("entries", []) if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError(f"{path.name}: expected a list of entries")
    return entries


def json_entry_to_text(entry: dict) -> str:
    """Flatten one structured entry into retrievable prose."""
    parts = [entry.get("summary", "")]
    steps = entry.get("steps") or []
    if steps:
        parts.append("Steps to try: " + " ".join(f"{i}. {s}" for i, s in enumerate(steps, 1)))
    if entry.get("when_to_seek_help"):
        parts.append("When to seek help: " + entry["when_to_seek_help"])
    return "\n\n".join(p for p in parts if p)


def _load_json_documents(path: Path) -> list[Document]:
    docs = []
    for entry in load_json_entries(path):
        text = json_entry_to_text(entry)
        if not text.strip():
            continue
        meta = {
            "title": entry.get("title") or entry.get("id", path.stem),
            "topic": entry.get("topic", "general"),
            "emotions": ", ".join(entry.get("emotions", [])),
            "entry_id": entry.get("id", ""),
            "source": path.name,
        }
        docs.append(Document(text=text, metadata=meta))
    return docs


def load_documents(directory: Path) -> list[Document]:
    """Load every supported file in `directory` (recursively)."""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Document directory not found: {directory}")

    docs: list[Document] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in {".md", ".txt"}:
            raw = path.read_text(encoding="utf-8")
            meta, body = _parse_front_matter(raw)
        elif suffix == ".json":
            docs.extend(_load_json_documents(path))  # one Document per entry
            continue
        elif suffix == ".pdf":
            meta, body = {}, _read_pdf(path)
        else:
            continue
        meta.setdefault("title", path.stem.replace("_", " ").title())
        meta.setdefault("topic", "general")
        meta["source"] = path.name
        if body.strip():
            docs.append(Document(text=body.strip(), metadata=meta))
    return docs
