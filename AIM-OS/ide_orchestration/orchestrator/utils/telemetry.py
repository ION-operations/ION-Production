"""Telemetry helpers (placeholder for CMC/HHNI integration)."""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict


def emit_local_log(payload: Dict[str, Any], log_path: str | Path) -> None:
    """Temporary helper that appends telemetry JSON to a file."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp": _dt.datetime.utcnow().isoformat(), **payload}
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload) + "\n")


__all__ = ["emit_local_log"]
