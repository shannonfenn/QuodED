from __future__ import annotations

from pathlib import Path

from quoded.storage import read_json, write_json


def build_tasks(segments_path: Path, output_path: Path) -> list[dict]:
    segments = read_json(segments_path)
    tasks: list[dict] = []
    for segment in segments:
        tasks.append(
            {
                "task_id": segment["segment_id"],
                "segment_id": segment["segment_id"],
                "title": segment["title"],
                "kind": segment["kind"],
                "status": "todo",
                "backend": None,
                "assignee": None,
                "notes": "",
            }
        )
    write_json(output_path, tasks)
    return tasks
