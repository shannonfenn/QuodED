from __future__ import annotations

from pathlib import Path


WORK_DIR_NAME = ".quoded"
DOCS_DIR_NAME = "docs"


def repo_root() -> Path:
    # Assumes CLI is invoked from repo root or a subdir.
    return Path.cwd()


def work_root(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / WORK_DIR_NAME


def docs_root(root: Path | None = None) -> Path:
    return work_root(root) / DOCS_DIR_NAME


def doc_root(doc_id: str, root: Path | None = None) -> Path:
    return docs_root(root) / doc_id
