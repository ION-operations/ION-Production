#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ACTIVE_ROOT = Path("/home/sev/ION - Production/ION_Developement").resolve()
PACKAGE_ROOT = ACTIVE_ROOT / "ION" / "04_packages"
EVENT_NAME = "PreCompact"


def _read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    sys.path.insert(0, str(PACKAGE_ROOT))
    try:
        from kernel.ion_codex_carrier_sync import handle_hook_event

        print(json.dumps(handle_hook_event(EVENT_NAME, _read_payload(), root=ACTIVE_ROOT), sort_keys=True))
    except Exception as exc:  # pragma: no cover - live hook must fail visible
        print(json.dumps({
            "continue": True,
            "suppressOutput": False,
            "systemMessage": f"ION_CARRIER_NOT_OPERATIONAL: PreCompact hook error: {exc}",
            "hookSpecificOutput": {
                "hookEventName": EVENT_NAME,
                "additionalContext": "ION_CARRIER_NOT_OPERATIONAL\nmount_truth_state: HOOK_ERROR_BLOCKED",
            },
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
