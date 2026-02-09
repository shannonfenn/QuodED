from __future__ import annotations

from pathlib import Path

from quoded.verify.backends.base import BackendResult
from quoded.verify.registry import get_backend


def run_policy_check(backend_name: str, root: Path) -> BackendResult:
    backend = get_backend(backend_name)
    if not root.exists():
        return BackendResult(
            backend=backend_name,
            ok=False,
            violations=[],
            note=f"Formalization path not found: {root}",
        )

    violations = backend.policy_check(root)
    return BackendResult(
        backend=backend_name,
        ok=len(violations) == 0,
        violations=violations,
    )
