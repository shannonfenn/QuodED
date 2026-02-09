from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from quoded.storage import read_jsonl, write_json

SEGMENT_KINDS = [
    "Theorem",
    "Lemma",
    "Definition",
    "Corollary",
    "Proposition",
    "Claim",
    "Remark",
    "Assumption",
    "Step",
]

SEGMENT_LABEL = r"(?:\d+(?:\.\d+)*|[IVXLC]+|[A-Z])"
SEGMENT_LABEL_FOLLOW = r"(?=\s|\.|\)|:)"
SEGMENT_PATTERN = re.compile(
    rf"^(?P<kind>{'|'.join(SEGMENT_KINDS)})\s+(?P<label>{SEGMENT_LABEL}){SEGMENT_LABEL_FOLLOW}(?P<rest>.*)$",
    re.IGNORECASE,
)


@dataclass
class Segment:
    segment_id: int
    kind: str
    title: str
    start_page: int
    end_page: int
    text: str


def segment_pages(pages_path: Path, output_path: Path) -> list[Segment]:
    pages = read_jsonl(pages_path)

    segments: list[Segment] = []
    current: dict | None = None

    def flush() -> None:
        nonlocal current
        if not current:
            return
        segments.append(
            Segment(
                segment_id=len(segments) + 1,
                kind=current["kind"],
                title=current["title"],
                start_page=current["start_page"],
                end_page=current["end_page"],
                text="\n".join(current["lines"]).strip(),
            )
        )
        current = None

    for page in pages:
        page_num = page.get("page")
        for line in (page.get("text") or "").splitlines():
            match = SEGMENT_PATTERN.match(line.strip())
            if match:
                flush()
                kind = match.group("kind").title()
                label = match.group("label").strip()
                rest = match.group("rest").strip()
                rest = rest.lstrip(".:").strip()
                title = f"{label} {rest}".strip()
                if not title:
                    title = f"{kind} {len(segments) + 1}"
                current = {
                    "kind": kind,
                    "title": title,
                    "start_page": page_num,
                    "end_page": page_num,
                    "lines": [line],
                }
            elif current:
                current["lines"].append(line)
                current["end_page"] = page_num

    flush()

    if not segments:
        full_text = []
        start_page = 1
        end_page = 1
        for page in pages:
            page_num = page.get("page")
            end_page = page_num
            full_text.append(page.get("text") or "")
        segments.append(
            Segment(
                segment_id=1,
                kind="Document",
                title="Full Document",
                start_page=start_page,
                end_page=end_page,
                text="\n".join(full_text).strip(),
            )
        )

    payload = [segment.__dict__ for segment in segments]
    write_json(output_path, payload)
    return segments
