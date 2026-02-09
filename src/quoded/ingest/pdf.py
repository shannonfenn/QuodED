from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from quoded.paths import doc_root
from quoded.storage import write_json, write_jsonl
from quoded.utils import normalize_path, slugify


@dataclass(frozen=True)
class DocumentManifest:
    doc_id: str
    source_path: str
    created_at: str
    page_count: int
    pages_path: str
    segments_path: str
    tasks_path: str


def _page_rows(reader: PdfReader) -> Iterable[dict]:
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        yield {"page": index, "text": text}


def import_pdf(pdf_path: Path, *, doc_id: str | None = None) -> DocumentManifest:
    source = normalize_path(pdf_path)
    if not source.exists():
        raise FileNotFoundError(f"PDF not found: {source}")

    inferred_id = slugify(source.stem)
    doc_id = doc_id or inferred_id
    root = doc_root(doc_id)
    root.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(source))
    pages_path = root / "pages.jsonl"
    write_jsonl(pages_path, _page_rows(reader))

    manifest = DocumentManifest(
        doc_id=doc_id,
        source_path=str(source),
        created_at=datetime.now(timezone.utc).isoformat(),
        page_count=len(reader.pages),
        pages_path=str(pages_path),
        segments_path=str(root / "segments.json"),
        tasks_path=str(root / "tasks.json"),
    )
    write_json(root / "manifest.json", manifest.__dict__)
    return manifest
