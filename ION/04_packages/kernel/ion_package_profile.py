"""Evaluate local ION package profiles.

Profiles are status ceilings and dependency expectations. They do not grant
production, live execution, or accepted-state authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .ion_carrier_onboard import resolve_shell_root_from_ion_root

SCHEMA_ID = "ion.package_profile.v1"
PROFILE_DECLARATION_RELATIVE_PATH = Path("ION/05_context/current/ION_PACKAGE_PROFILE.json")
DEFAULT_PROFILE_ID = "single_carrier_sandbox"

BUILTIN_PROFILES: dict[str, dict[str, Any]] = {
    "single_carrier_sandbox": {
        "profile_id": "single_carrier_sandbox",
        "description": "Local single-carrier sandbox profile for bounded Codex/ION work.",
        "required_paths": [
            "pyproject.toml",
            "ION/REPO_AUTHORITY.md",
            "ION/04_packages/kernel",
        ],
        "optional_sibling_roots": [
            "../mcp",
            "../browser_extension",
            "../ION_GPT",
            "../local_daemon",
        ],
        "status_ceiling": "LOCAL_SANDBOX_READY_ONLY",
        "ready_verdict": "ION_STATUS_SINGLE_CARRIER_READY",
        "full_readiness_proven": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc)}


def evaluate_package_profile(root: str | Path | None = None, *, profile_id: str | None = None) -> dict[str, Any]:
    shell_root = resolve_shell_root_from_ion_root(root)
    declaration = _read_json(shell_root / PROFILE_DECLARATION_RELATIVE_PATH)
    declared_profile = profile_id or declaration.get("profile_id") or DEFAULT_PROFILE_ID
    profile = BUILTIN_PROFILES.get(str(declared_profile))
    blockers: list[dict[str, Any]] = []

    if "_read_error" in declaration:
        blockers.append(
            {
                "finding_id": "PROFILE-0001",
                "category": "profile_declaration_unreadable",
                "path": PROFILE_DECLARATION_RELATIVE_PATH.as_posix(),
                "detail": "profile declaration could not be parsed",
            }
        )
    if profile is None:
        blockers.append(
            {
                "finding_id": f"PROFILE-{len(blockers) + 1:04d}",
                "category": "profile_missing",
                "profile_id": str(declared_profile),
                "detail": "profile_id is not registered",
            }
        )
        profile = {
            "profile_id": str(declared_profile),
            "required_paths": [],
            "optional_sibling_roots": [],
            "status_ceiling": "UNKNOWN_PROFILE_BLOCKED",
            "ready_verdict": None,
            "full_readiness_proven": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }

    missing_required = [
        rel for rel in profile.get("required_paths", []) if not (shell_root / str(rel)).exists()
    ]
    for rel in missing_required:
        blockers.append(
            {
                "finding_id": f"PROFILE-{len(blockers) + 1:04d}",
                "category": "required_profile_path_missing",
                "path": rel,
                "detail": "required profile path is missing",
            }
        )

    optional_siblings = [
        {"path": rel, "present": (shell_root / str(rel)).exists(), "required": False}
        for rel in profile.get("optional_sibling_roots", [])
    ]

    return {
        "schema_id": SCHEMA_ID,
        "status": "PACKAGE_PROFILE_BLOCKED" if blockers else "PACKAGE_PROFILE_READY",
        "accepted": not blockers,
        "profile_id": profile.get("profile_id"),
        "declaration_path": PROFILE_DECLARATION_RELATIVE_PATH.as_posix(),
        "declaration_present": (shell_root / PROFILE_DECLARATION_RELATIVE_PATH).exists(),
        "status_ceiling": profile.get("status_ceiling"),
        "ready_verdict": profile.get("ready_verdict"),
        "full_readiness_proven": profile.get("full_readiness_proven", False),
        "missing_required_paths": missing_required,
        "optional_sibling_roots": optional_siblings,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the local ION package profile.")
    parser.add_argument("--ion-root", default=None)
    parser.add_argument("--profile-id", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = evaluate_package_profile(args.ion_root, profile_id=args.profile_id)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
    return 0 if result["accepted"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
