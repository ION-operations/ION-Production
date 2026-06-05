"""Read-only Domain Weaver larger-fanout control-plane readiness.

This module turns the current larger-fanout operating envelope into a
machine-checkable gate. It does not spawn workers, enqueue Codex runs, move
registry/materialization state, or claim product acceptance.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.domain_weaver.larger_fanout_control_readiness.v0_1"
DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_OUTPUT_DIR = DEFAULT_CONTEXT_ROOT / "larger_fanout"
DEFAULT_JSON_NAME = "DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.json"
DEFAULT_MARKDOWN_NAME = "DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.md"
MAX_CANDIDATE_LANE_COUNT = 3

OPERATING_ENVELOPE_PATH = (
    DEFAULT_CONTEXT_ROOT
    / "stewarded_autonomy/DOMAIN_WEAVER_LARGER_FANOUT_OPERATING_ENVELOPE_20260604T0410Z.md"
)

REQUIRED_RECEIPTS = {
    "alternate_worker_return_lane": (
        DEFAULT_CONTEXT_ROOT
        / "operator_actions/20260604T035500Z_domain_weaver_alternate_worker_return_lane_patch_and_live_dogfood_settlement.json"
    ),
    "alternate_worker_provenance_receipt_bridge": (
        DEFAULT_CONTEXT_ROOT
        / "operator_actions/20260604T040100Z_domain_weaver_alternate_worker_provenance_receipt_bridge_settlement.json"
    ),
    "native_subagent_transcript_bridge": (
        DEFAULT_CONTEXT_ROOT
        / "operator_actions/20260604T040700Z_domain_weaver_native_subagent_transcript_bridge_live_dogfood_settlement.json"
    ),
    "larger_fanout_operating_envelope": (
        DEFAULT_CONTEXT_ROOT
        / "operator_actions/20260604T041000Z_domain_weaver_larger_fanout_operating_envelope_created.json"
    ),
}

REQUIRED_WORKER_GATES = (
    "explicit_role_domain_packet_contract",
    "target_read_write_scope",
    "worker_shift_lease_status_when_write_possible",
    "native_transcript_receipt_or_codex_queue_run_receipt",
    "provenance_receipt_bound_to_worker_output_hash",
    "proof_gated_task_return",
    "synced_reply_or_fanin_receipt",
    "lead_or_nemesis_settlement_before_state_movement",
)

FORBIDDEN_STATE_MOVEMENT = (
    "accepted_state_claim",
    "product_state_acceptance",
    "production_authority",
    "live_execution_authority",
    "secrets_authority",
    "registry_or_materialization_movement",
    "ui_or_topology_resume",
    "git_push",
)


def build_larger_fanout_control_readiness(
    active_root: str | Path,
    *,
    requested_lane_count: int = MAX_CANDIDATE_LANE_COUNT,
    recursive_native_spawn_requested: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only readiness projection for larger fanout.

    The projection allows at most a three-lane candidate fanout unless a later
    receipt proves a stricter operating envelope. Recursive native spawning is
    blocked until a bounded one-child probe receipt exists.
    """

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or _utc_now()
    root_proof = _active_root_proof(root)
    requested = max(0, int(requested_lane_count))

    receipt_checks = {
        name: _receipt_check(root, rel_path)
        for name, rel_path in REQUIRED_RECEIPTS.items()
    }
    envelope_check = _file_check(root, OPERATING_ENVELOPE_PATH)
    native_bridge = receipt_checks["native_subagent_transcript_bridge"]
    native_payload = _mapping(native_bridge.get("payload"))
    native_live = _mapping(native_payload.get("live_dogfood"))
    native_proof = _mapping(native_payload.get("proof_projection"))

    recursive_probe = _latest_recursive_probe(root)
    recursive_probe_payload = _mapping(recursive_probe.get("payload"))
    recursive_probe_available = bool(
        recursive_probe.get("present")
        and recursive_probe_payload.get("child_spawn_available") is True
        and int(recursive_probe_payload.get("child_spawn_count") or 0) <= 1
        and not bool(recursive_probe_payload.get("product_state_accepted"))
    )

    blockers: list[str] = []
    warnings: list[str] = []
    if not root_proof["proof_ok"]:
        blockers.append("active_root_proof_missing")
    if not envelope_check["present"]:
        blockers.append("larger_fanout_operating_envelope_missing")
    for name, check in receipt_checks.items():
        if not check["present"]:
            blockers.append(f"required_receipt_missing:{name}")

    if requested > MAX_CANDIDATE_LANE_COUNT:
        blockers.append("requested_lane_count_exceeds_candidate_cap")
    if requested == 0:
        blockers.append("requested_lane_count_zero")

    if native_payload:
        if native_payload.get("result") != "active_root_patch_validated_and_native_subagent_bridge_dogfooded":
            blockers.append("native_subagent_bridge_not_validated_dogfooded")
        if not bool(_mapping(native_payload.get("focused_validation")).get("passed")):
            blockers.append("native_subagent_bridge_focused_validation_not_passed")
        if not bool(native_live.get("accepted_for_carrier_intake")):
            blockers.append("native_subagent_bridge_missing_accepted_carrier_intake")
        if not bool(native_live.get("native_subagent_transcript_verified")):
            blockers.append("native_subagent_transcript_not_verified")
        if bool(native_live.get("product_state_accepted")):
            blockers.append("native_subagent_bridge_claims_product_state")
        if not bool(native_proof.get("proof_ok")):
            blockers.append("native_subagent_bridge_proof_not_ok")
        if bool(native_proof.get("automatic_agent_reaction_proven")):
            warnings.append("native_subagent_bridge_claims_original_automatic_reaction")

    if recursive_native_spawn_requested and not recursive_probe_available:
        blockers.append("recursive_native_spawn_requested_without_one_child_probe_receipt")

    candidate_wave = _candidate_wave_from_receipt(
        _mapping(receipt_checks["larger_fanout_operating_envelope"].get("payload"))
    )
    if len(candidate_wave) > MAX_CANDIDATE_LANE_COUNT:
        warnings.append("recorded_candidate_wave_exceeds_default_cap")

    readiness_ok = not blockers
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "context_root": DEFAULT_CONTEXT_ROOT.as_posix(),
        "root_proof": root_proof,
        "readiness_ok": readiness_ok,
        "larger_fanout_candidate_allowed": readiness_ok,
        "max_candidate_lane_count": MAX_CANDIDATE_LANE_COUNT,
        "requested_lane_count": requested,
        "candidate_wave": candidate_wave,
        "recursive_native_spawn_requested": bool(recursive_native_spawn_requested),
        "recursive_native_spawn_allowed": bool(
            recursive_native_spawn_requested and recursive_probe_available and readiness_ok
        ),
        "recursive_probe": {
            "available": recursive_probe_available,
            "receipt_path": recursive_probe.get("path", ""),
            "child_spawn_count": int(recursive_probe_payload.get("child_spawn_count") or 0),
        },
        "required_worker_gates": list(REQUIRED_WORKER_GATES),
        "forbidden_state_movement": list(FORBIDDEN_STATE_MOVEMENT),
        "receipt_checks": receipt_checks,
        "operating_envelope": envelope_check,
        "blockers": blockers,
        "warnings": warnings,
        "next_packet": "PCKT-DOMAIN-WEAVER-LARGER-FANOUT-CONTROL-PLANE-V0_1",
        "settlement_rule": "active_root_patch_or_next_packet_or_blocker_or_operator_decision",
        "authority": _authority(),
        "non_claims": [
            "does_not_spawn_workers",
            "does_not_enqueue_codex_runs",
            "does_not_accept_product_state",
            "does_not_move_registry_or_materialization_state",
        ],
    }


def write_larger_fanout_control_readiness(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    requested_lane_count: int = MAX_CANDIDATE_LANE_COUNT,
    recursive_native_spawn_requested: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Write JSON and Markdown readiness artifacts."""

    root = Path(active_root).expanduser().resolve(strict=False)
    readiness = build_larger_fanout_control_readiness(
        root,
        requested_lane_count=requested_lane_count,
        recursive_native_spawn_requested=recursive_native_spawn_requested,
        generated_at=generated_at,
    )
    out_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / DEFAULT_JSON_NAME
    markdown_path = out_dir / DEFAULT_MARKDOWN_NAME
    json_text = json.dumps(readiness, indent=2, sort_keys=True) + "\n"
    markdown_text = render_larger_fanout_control_readiness_markdown(readiness)
    json_path.write_text(json_text, encoding="utf-8")
    markdown_path.write_text(markdown_text, encoding="utf-8")
    return {
        "schema_id": "ion.domain_weaver.larger_fanout_control_readiness.write_result.v0_1",
        "json_path": _rel(json_path, root),
        "json_sha256": _sha256_text(json_text),
        "markdown_path": _rel(markdown_path, root),
        "markdown_sha256": _sha256_text(markdown_text),
        "readiness_ok": readiness["readiness_ok"],
        "blockers": readiness["blockers"],
    }


def render_larger_fanout_control_readiness_markdown(readiness: Mapping[str, Any]) -> str:
    """Render a compact operator/agent-facing readiness summary."""

    lines = [
        "# Domain Weaver Larger Fanout Control Readiness",
        "",
        f"Generated: `{readiness.get('generated_at')}`",
        "",
        "Authority: candidate read-only gate. It does not spawn workers, enqueue Codex runs, accept product state, or move registry/materialization state.",
        "",
        "## Decision",
        "",
        f"- readiness_ok: `{str(bool(readiness.get('readiness_ok'))).lower()}`",
        f"- larger_fanout_candidate_allowed: `{str(bool(readiness.get('larger_fanout_candidate_allowed'))).lower()}`",
        f"- max_candidate_lane_count: `{readiness.get('max_candidate_lane_count')}`",
        f"- requested_lane_count: `{readiness.get('requested_lane_count')}`",
        f"- recursive_native_spawn_allowed: `{str(bool(readiness.get('recursive_native_spawn_allowed'))).lower()}`",
        "",
        "## Current Candidate Wave",
        "",
    ]
    for lane in readiness.get("candidate_wave") or []:
        lines.append(f"- `{lane}`")
    if not readiness.get("candidate_wave"):
        lines.append("- none recorded")
    lines.extend(["", "## Required Worker Gates", ""])
    for gate in readiness.get("required_worker_gates") or []:
        lines.append(f"- `{gate}`")
    lines.extend(["", "## Blockers", ""])
    blockers = readiness.get("blockers") or []
    for blocker in blockers:
        lines.append(f"- `{blocker}`")
    if not blockers:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    warnings = readiness.get("warnings") or []
    for warning in warnings:
        lines.append(f"- `{warning}`")
    if not warnings:
        lines.append("- none")
    lines.extend(["", "## Receipt Checks", ""])
    lines.append("| Receipt | Present | SHA256 |")
    lines.append("|---|---|---|")
    for name, check in sorted(_mapping(readiness.get("receipt_checks")).items()):
        lines.append(
            f"| `{name}` | `{str(bool(check.get('present'))).lower()}` | `{check.get('sha256', '')}` |"
        )
    lines.extend(["", "## Next Packet", "", f"`{readiness.get('next_packet')}`", ""])
    return "\n".join(lines)


def _receipt_check(root: Path, relative_path: Path) -> dict[str, Any]:
    check = _file_check(root, relative_path)
    if not check["present"]:
        return check
    payload = _read_json(root / relative_path)
    check["payload"] = payload
    check["json_ok"] = bool(payload)
    return check


def _file_check(root: Path, relative_path: Path) -> dict[str, Any]:
    path = root / relative_path
    present = path.is_file()
    return {
        "path": relative_path.as_posix(),
        "present": present,
        "sha256": _sha256_file(path) if present else "",
    }


def _latest_recursive_probe(root: Path) -> dict[str, Any]:
    action_dir = root / DEFAULT_CONTEXT_ROOT / "operator_actions"
    matches = sorted(action_dir.glob("*recursive_native_spawn_probe*.json"))
    if not matches:
        return {"present": False, "path": "", "payload": {}}
    path = matches[-1]
    return {
        "present": True,
        "path": _rel(path, root),
        "sha256": _sha256_file(path),
        "payload": _read_json(path),
    }


def _candidate_wave_from_receipt(payload: Mapping[str, Any]) -> list[str]:
    wave = payload.get("fanout_wave")
    if not isinstance(wave, list):
        return []
    return [str(item) for item in wave if str(item).strip()]


def _active_root_proof(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    repo_authority = root / "ION/REPO_AUTHORITY.md"
    return {
        "schema_id": "ion.active_root_proof.v0_1_candidate",
        "active_root": str(root),
        "required_siblings": {
            "pyproject.toml": pyproject.is_file(),
            "ION/REPO_AUTHORITY.md": repo_authority.is_file(),
        },
        "proof_ok": pyproject.is_file() and repo_authority.is_file(),
    }


def _authority() -> dict[str, bool]:
    return {
        "candidate_context_only": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Active ION root")
    parser.add_argument("--write", action="store_true", help="Write latest JSON/Markdown artifacts")
    parser.add_argument("--requested-lane-count", type=int, default=MAX_CANDIDATE_LANE_COUNT)
    parser.add_argument("--recursive-native-spawn-requested", action="store_true")
    args = parser.parse_args(argv)

    if args.write:
        result = write_larger_fanout_control_readiness(
            args.root,
            requested_lane_count=args.requested_lane_count,
            recursive_native_spawn_requested=args.recursive_native_spawn_requested,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        result = build_larger_fanout_control_readiness(
            args.root,
            requested_lane_count=args.requested_lane_count,
            recursive_native_spawn_requested=args.recursive_native_spawn_requested,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
