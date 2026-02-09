from __future__ import annotations

import hashlib
import re
from pathlib import Path


_slug_re = re.compile(r"[^a-zA-Z0-9_-]+")


def slugify(text: str) -> str:
    cleaned = _slug_re.sub("-", text).strip("-").lower()
    if cleaned:
        return cleaned
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()  # nosec - non-crypto use
    return digest[:10]


def normalize_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()
