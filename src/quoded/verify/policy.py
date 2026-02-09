from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path


@dataclass(frozen=True)
class PolicyViolation:
    file: str
    line: int
    rule: str
    text: str


POLICIES = {
    "lean4": {
        "extensions": [".lean"],
        "forbidden": [r"\bsorry\b", r"\baxiom\b", r"\badmit\b", r"\bunsafe\b"],
    },
    "rocq": {
        "extensions": [".v"],
        "forbidden": [r"\bAdmitted\b", r"\bAdmit\b", r"\bAxiom\b", r"\badmit\b", r"\bunsafe\b"],
    },
    "isabelle": {
        "extensions": [".thy"],
        "forbidden": [r"\bsorry\b", r"\baxiomatization\b"],
    },
    "agda": {
        "extensions": [".agda"],
        "forbidden": [r"\bpostulate\b", r"\{-#\s*TERMINATING\s*#-\}"],
    },
}


def scan_policy(root: Path, backend: str) -> list[PolicyViolation]:
    policy = POLICIES.get(backend)
    if not policy:
        raise ValueError(f"Unknown backend: {backend}")

    extensions = tuple(policy["extensions"])
    forbidden = [(rule, re.compile(rule)) for rule in policy["forbidden"]]

    violations: list[PolicyViolation] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if not path.name.endswith(extensions):
            continue
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for rule, pattern in forbidden:
                if pattern.search(line):
                    violations.append(
                        PolicyViolation(
                            file=str(path),
                            line=idx,
                            rule=rule,
                            text=line.strip(),
                        )
                    )
    return violations
