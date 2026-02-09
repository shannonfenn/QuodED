from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quoded.verify.policy import POLICIES, scan_policy


@dataclass(frozen=True)
class SimpleBackend:
    name: str

    @property
    def extensions(self) -> tuple[str, ...]:
        policy = POLICIES[self.name]
        return tuple(policy["extensions"])

    def policy_check(self, root: Path) -> list[dict]:
        violations = scan_policy(root, self.name)
        return [violation.__dict__ for violation in violations]
