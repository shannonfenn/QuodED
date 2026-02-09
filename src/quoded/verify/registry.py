from __future__ import annotations

from quoded.verify.backends.simple import SimpleBackend

BACKENDS = {
    "lean4": SimpleBackend("lean4"),
    "rocq": SimpleBackend("rocq"),
    "isabelle": SimpleBackend("isabelle"),
    "agda": SimpleBackend("agda"),
}


def get_backend(name: str):
    backend = BACKENDS.get(name)
    if not backend:
        raise ValueError(f"Unknown backend '{name}'. Available: {', '.join(BACKENDS)}")
    return backend
