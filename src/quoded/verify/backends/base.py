from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class BackendAdapter(Protocol):
    name: str
    extensions: tuple[str, ...]

    def policy_check(self, root: Path) -> list[dict]:
        ...


@dataclass(frozen=True)
class BackendResult:
    backend: str
    ok: bool
    violations: list[dict]
    note: str | None = None
