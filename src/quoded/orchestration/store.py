from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from quoded.paths import repo_root, work_root
from quoded.storage import read_json, write_json


RUNS_DIR_NAME = "runs"


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    doc_id: str
    backend: str
    status: str
    created_at: str
    updated_at: str
    label: str | None
    notes: str | None


@dataclass(frozen=True)
class RunEvent:
    event_id: str
    run_id: str
    created_at: str
    kind: str
    message: str
    meta: dict


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root(root: Path | None = None) -> Path:
    return root or repo_root()


def runs_root(root: Path | None = None) -> Path:
    return work_root(_root(root)) / RUNS_DIR_NAME


def run_root(run_id: str, root: Path | None = None) -> Path:
    return runs_root(root) / run_id


def _record_from_dict(payload: dict) -> RunRecord:
    return RunRecord(
        run_id=payload["run_id"],
        doc_id=payload["doc_id"],
        backend=payload["backend"],
        status=payload["status"],
        created_at=payload["created_at"],
        updated_at=payload["updated_at"],
        label=payload.get("label"),
        notes=payload.get("notes"),
    )


def _event_from_dict(payload: dict) -> RunEvent:
    return RunEvent(
        event_id=payload["event_id"],
        run_id=payload["run_id"],
        created_at=payload["created_at"],
        kind=payload["kind"],
        message=payload["message"],
        meta=payload.get("meta") or {},
    )


def _new_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid4().hex[:8]
    return f"run-{stamp}-{suffix}"


def _new_event_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid4().hex[:8]
    return f"evt-{stamp}-{suffix}"


def _events_path(run_id: str, root: Path | None = None) -> Path:
    return run_root(run_id, root) / "events.jsonl"


def create_run(
    doc_id: str,
    backend: str,
    label: str | None = None,
    status: str = "running",
    root: Path | None = None,
) -> RunRecord:
    run_id = _new_run_id()
    base = run_root(run_id, root)
    base.mkdir(parents=True, exist_ok=False)
    now = _now_iso()
    record = RunRecord(
        run_id=run_id,
        doc_id=doc_id,
        backend=backend,
        status=status,
        created_at=now,
        updated_at=now,
        label=label,
        notes=None,
    )
    write_json(base / "run.json", record.__dict__)
    return record


def list_runs(root: Path | None = None) -> list[RunRecord]:
    base = runs_root(root)
    if not base.exists():
        return []
    records: list[RunRecord] = []
    for path in base.iterdir():
        if not path.is_dir():
            continue
        run_path = path / "run.json"
        if not run_path.exists():
            continue
        payload = read_json(run_path)
        if isinstance(payload, dict):
            records.append(_record_from_dict(payload))
    records.sort(key=lambda record: record.created_at, reverse=True)
    return records


def get_run(run_id: str, root: Path | None = None) -> RunRecord:
    payload = read_json(run_root(run_id, root) / "run.json")
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid run record: {run_id}")
    return _record_from_dict(payload)


def update_run_status(run_id: str, status: str, root: Path | None = None) -> RunRecord:
    run_path = run_root(run_id, root) / "run.json"
    payload = read_json(run_path)
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid run record: {run_id}")
    payload["status"] = status
    payload["updated_at"] = _now_iso()
    write_json(run_path, payload)
    return _record_from_dict(payload)


def append_event(
    run_id: str,
    kind: str,
    message: str,
    meta: dict | None = None,
    root: Path | None = None,
) -> RunEvent:
    event = RunEvent(
        event_id=_new_event_id(),
        run_id=run_id,
        created_at=_now_iso(),
        kind=kind,
        message=message,
        meta=meta or {},
    )
    path = _events_path(run_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.__dict__, ensure_ascii=False))
        handle.write("\n")
    return event


def list_events(run_id: str, root: Path | None = None) -> list[RunEvent]:
    path = _events_path(run_id, root)
    if not path.exists():
        return []
    events: list[RunEvent] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                events.append(_event_from_dict(payload))
    events.sort(key=lambda event: event.created_at)
    return events


def iter_events(run_id: str, root: Path | None = None) -> Iterable[RunEvent]:
    for event in list_events(run_id, root):
        yield event
