"""Fail-closed ION truth gates for local status readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_package_profile import evaluate_package_profile
from .ion_security_boundary import scan_security_boundary

SCHEMA_ID = "ion.truth_gates.v1"
TRUTH_GATE_STATE_RELATIVE_PATH = Path("ION/05_context/current/ION_TRUTH_GATE_STATE.json")

BAD_DEPENDENCY_STATES = {"blocked", "fail", "failed", "missing", "red"}
BAD_TEST_STATES = {"blocked", "fail", "failed", "failing", "red"}
BAD_CURRENTNESS_STATES = {"blocked", "expired", "outdated", "stale"}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc)}


def _state_text(payload: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return ""


def _blocker(finding_id: str, category: str, gate: str, detail: str, path: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "finding_id": finding_id,
        "category": category,
        "gate": gate,
        "detail": detail,
        "blocker": True,
    }
    if path:
        result["path"] = path
    return result


def _dependency_gate(shell_root: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    required_paths = ["pyproject.toml", "ION/REPO_AUTHORITY.md", "ION/04_packages/kernel"]
    for rel in required_paths:
        if not (shell_root / rel).exists():
            blockers.append(_blocker(f"DEP-{len(blockers) + 1:04d}", "dependency_path_missing", "dependency", "required dependency surface is missing", rel))
    dependency_state = state.get("dependencies") if isinstance(state.get("dependencies"), Mapping) else {}
    status = _state_text(dependency_state, "status", "verdict")
    if status in BAD_DEPENDENCY_STATES:
        blockers.append(_blocker(f"DEP-{len(blockers) + 1:04d}", "dependency_state_blocked", "dependency", f"dependency state is {status}"))
    return {
        "status": "DEPENDENCY_BLOCKED" if blockers else "DEPENDENCY_READY",
        "accepted": not blockers,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }


def _test_gate(state: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    tests = state.get("tests") if isinstance(state.get("tests"), Mapping) else {}
    status = _state_text(tests, "status", "verdict")
    if status in BAD_TEST_STATES or tests.get("red") is True:
        blockers.append(_blocker("TEST-0001", "test_state_red", "test", f"test state is {status or 'red'}"))
    return {
        "status": "TEST_BLOCKED" if blockers else "TEST_READY",
        "accepted": not blockers,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }


def _currentness_gate(state: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    currentness = state.get("currentness") if isinstance(state.get("currentness"), Mapping) else {}
    status = _state_text(currentness, "status", "verdict")
    if status in BAD_CURRENTNESS_STATES or currentness.get("current") is False or currentness.get("is_current") is False:
        blockers.append(_blocker("CURRENT-0001", "currentness_stale", "currentness", f"currentness state is {status or 'not_current'}"))
    return {
        "status": "CURRENTNESS_BLOCKED" if blockers else "CURRENTNESS_READY",
        "accepted": not blockers,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }


def evaluate_truth_gates(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = resolve_shell_root_from_ion_root(root)
    state = _read_json(shell_root / TRUTH_GATE_STATE_RELATIVE_PATH)
    state_parse_blocker = "_read_error" in state
    security = scan_security_boundary(shell_root)
    package_profile = evaluate_package_profile(shell_root)
    dependency = _dependency_gate(shell_root, state)
    tests = _test_gate(state)
    currentness = _currentness_gate(state)
    blockers: list[dict[str, Any]] = []

    for finding in security.get("findings", []):
        if finding.get("blocker") is True:
            blockers.append(
                {
                    "finding_id": finding.get("finding_id"),
                    "category": "security",
                    "gate": "security",
                    "path": finding.get("path"),
                    "rule_id": finding.get("rule_id"),
                    "blocker": True,
                }
            )
    for finding in package_profile.get("blockers", []):
        blockers.append({**finding, "gate": "profile", "blocker": True})
    for gate in (dependency, tests, currentness):
        blockers.extend(gate.get("blockers", []))
    if state_parse_blocker:
        blockers.append(
            _blocker(
                f"TRUTH-{len(blockers) + 1:04d}",
                "truth_gate_state_unreadable",
                "truth_gate_state",
                "truth gate state could not be parsed",
                TRUTH_GATE_STATE_RELATIVE_PATH.as_posix(),
            )
        )

    if any(item.get("gate") == "security" for item in blockers):
        verdict = "ION_STATUS_SECURITY_BLOCKED"
    elif any(item.get("gate") == "profile" for item in blockers):
        verdict = "ION_STATUS_PROFILE_BLOCKED"
    elif any(item.get("gate") == "dependency" for item in blockers):
        verdict = "ION_STATUS_DEPENDENCY_BLOCKED"
    elif any(item.get("gate") == "test" for item in blockers):
        verdict = "ION_STATUS_TEST_BLOCKED"
    elif any(item.get("gate") == "currentness" for item in blockers):
        verdict = "ION_STATUS_CURRENTNESS_BLOCKED"
    elif blockers:
        verdict = "ION_STATUS_TRUTH_BLOCKED"
    else:
        verdict = "ION_STATUS_TRUTH_GATES_READY"

    return {
        "schema_id": SCHEMA_ID,
        "status": "TRUTH_GATES_BLOCKED" if blockers else "TRUTH_GATES_READY",
        "verdict": verdict,
        "accepted": not blockers,
        "state_path": TRUTH_GATE_STATE_RELATIVE_PATH.as_posix(),
        "state_present": (shell_root / TRUTH_GATE_STATE_RELATIVE_PATH).exists(),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "security_boundary": security,
        "package_profile": package_profile,
        "dependency_gate": dependency,
        "test_gate": tests,
        "currentness_gate": currentness,
        "secret_values_emitted": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate ION truth gates for local status readiness.")
    parser.add_argument("--ion-root", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = evaluate_truth_gates(args.ion_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["verdict"])
    return 0 if result["accepted"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
