"""Lightweight JSON persistence helpers for local GEO data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def ensure_parent(path: Path) -> None:
    """Create the parent directory if it does not exist."""

    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    """Load JSON content from a file, falling back to the provided default."""

    ensure_parent(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    """Persist JSON content to disk with UTF-8 encoding."""

    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
