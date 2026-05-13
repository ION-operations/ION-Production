"""Small env-file loader for local scripts.

The project avoids adding python-dotenv as a required dependency. This helper
supports simple KEY=VALUE lines from a local ignored `.env` file.
"""
from __future__ import annotations

import os
from pathlib import Path


def load_local_env(path: Path) -> list[str]:
    loaded: list[str] = []
    if not path.exists():
        return loaded
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded
