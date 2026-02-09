from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from quoded.paths import doc_root, repo_root
from quoded.segment.segmenter import SEGMENT_PATTERN
from quoded.storage import read_json, write_json


@dataclass(frozen=True)
class LineBox:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root(root: Path | None = None) -> Path:
    return root or repo_root()


def _layout_path(doc_id: str, root: Path | None = None) -> Path:
    return doc_root(doc_id, _root(root)) / "layout.json"


def _group_words_into_lines(words: list[dict], y_tolerance: float = 2.0) -> list[LineBox]:
    if not words:
        return []
    words_sorted = sorted(words, key=lambda item: (item.get("top", 0), item.get("x0", 0)))
    lines: list[dict] = []
    for word in words_sorted:
        top = float(word.get("top", 0))
        bottom = float(word.get("bottom", 0))
        x0 = float(word.get("x0", 0))
        x1 = float(word.get("x1", 0))
        text = str(word.get("text", "")).strip()
        if not text:
            continue
        if lines and abs(top - lines[-1]["top"]) <= y_tolerance:
            line = lines[-1]
            line["words"].append(word)
            line["x0"] = min(line["x0"], x0)
            line["x1"] = max(line["x1"], x1)
            line["y0"] = min(line["y0"], top)
            line["y1"] = max(line["y1"], bottom)
        else:
            lines.append({
                "top": top,
                "words": [word],
                "x0": x0,
                "x1": x1,
                "y0": top,
                "y1": bottom,
            })
    output: list[LineBox] = []
    for line in lines:
        words = sorted(line["words"], key=lambda item: item.get("x0", 0))
        line_text = " ".join(str(item.get("text", "")).strip() for item in words if item.get("text"))
        if not line_text:
            continue
        output.append(
            LineBox(
                text=line_text,
                x0=float(line["x0"]),
                y0=float(line["y0"]),
                x1=float(line["x1"]),
                y1=float(line["y1"]),
            )
        )
    return output


def load_layout(doc_id: str, root: Path | None = None) -> dict | None:
    path = _layout_path(doc_id, root)
    if not path.exists():
        return None
    payload = read_json(path)
    if isinstance(payload, dict):
        return payload
    return None


def build_layout(doc_id: str, root: Path | None = None, dpi: int = 144) -> dict:
    try:
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency may be missing in offline env
        raise RuntimeError(
            "pdfplumber is required to build layout highlights. "
            "Run `uv sync` after adding pdfplumber to dependencies."
        ) from exc

    base = doc_root(doc_id, _root(root))
    manifest_path = base / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("Manifest payload invalid")
    source_path = Path(str(manifest.get("source_path", "")))
    if not source_path.exists():
        raise FileNotFoundError(f"PDF not found: {source_path}")

    segments_path = base / "segments.json"
    segments_payload = read_json(segments_path)
    if not isinstance(segments_payload, list):
        raise ValueError("Segments payload invalid")

    segments = [segment for segment in segments_payload if isinstance(segment, dict)]

    scale = dpi / 72
    pages: list[dict] = []
    highlights: list[dict] = []

    segment_index = 0
    mismatches: list[dict] = []

    with pdfplumber.open(str(source_path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            pages.append({
                "page": page_number,
                "width": float(page.width),
                "height": float(page.height),
            })
            words = page.extract_words(
                x_tolerance=2,
                y_tolerance=2,
                keep_blank_chars=False,
                use_text_flow=True,
            )
            lines = _group_words_into_lines(words)
            for line in lines:
                match = SEGMENT_PATTERN.match(line.text.strip())
                if not match:
                    continue
                if segment_index >= len(segments):
                    break
                segment = segments[segment_index]
                segment_index += 1
                kind = str(segment.get("kind", ""))
                title = str(segment.get("title", ""))
                matched_kind = match.group("kind").title() if match.group("kind") else ""
                note = None
                if kind and matched_kind and kind != matched_kind:
                    note = f"kind mismatch: {matched_kind} != {kind}"
                    mismatches.append({
                        "segment_id": segment.get("segment_id"),
                        "page": page_number,
                        "note": note,
                        "line": line.text,
                    })
                highlights.append({
                    "segment_id": int(segment.get("segment_id")),
                    "page": page_number,
                    "kind": kind,
                    "title": title,
                    "text": line.text,
                    "x0": line.x0,
                    "y0": line.y0,
                    "x1": line.x1,
                    "y1": line.y1,
                    "note": note,
                })

    payload = {
        "doc_id": doc_id,
        "generated_at": _now_iso(),
        "dpi": dpi,
        "scale": scale,
        "page_count": int(manifest.get("page_count", len(pages))),
        "pages": pages,
        "highlights": highlights,
        "segment_count": len(segments),
        "highlight_count": len(highlights),
        "unmapped_segments": max(0, len(segments) - len(highlights)),
        "mismatches": mismatches,
    }
    write_json(_layout_path(doc_id, root), payload)
    return payload


def iter_highlights(layout: dict) -> Iterable[dict]:
    for highlight in layout.get("highlights", []) if isinstance(layout, dict) else []:
        if isinstance(highlight, dict):
            yield highlight
