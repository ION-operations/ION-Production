"""Carrier mount receipt and persona presentation helpers for ION.

The receipt is the authority surface. Persona is presentation only. This module
does not expose hidden reasoning, start workers, grant production authority, or
merge accepted state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.carrier_mount_receipt.v1"
PERSONA_SCHEMA_ID = "ion.persona_presentation.v1"
READY_VERDICT = "ION_CARRIER_MOUNT_READY"
BLOCKED_VERDICT = "ION_CARRIER_MOUNT_BLOCKED"
DEFAULT_PARENT_CONTEXT_ID = "ION_MAIN_CURRENT_CONTEXT"
DEFAULT_SETTLEMENT_INBOX = "ION/05_context/current/context_settlement/inbox"
DEFAULT_MOUNT_RECEIPT_DIR = "ION/05_context/current/carrier_mount_receipts"
ALLOWED_SOURCE_TYPES = {"package", "repo", "mcp", "memory", "user", "inferred"}
PRESENTATION_MODES = {"full_persona", "partial_persona", "receipt_only"}
DEFAULT_FALLBACK_BEHAVIOR = (
    "show_mount_receipt",
    "show_source_posture",
    "show_authority",
    "show_blockers",
    "operate_receipt_only",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return f"{prefix}-{digest.hexdigest()[:16]}"


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: str | Path, root: Path | None = None) -> str:
    p = Path(path)
    if root is not None and p.is_absolute():
        try:
            p = p.relative_to(root)
        except ValueError:
            return p.as_posix()
    return p.as_posix().lstrip("./")


def _default_source_posture() -> dict[str, list[str]]:
    return {
        "mcp_observed": [],
        "repo_observed": [],
        "package_observed": [],
        "user_reported": [],
        "inferred": [],
    }


def _default_return_target(branch_id: str) -> dict[str, str]:
    return {
        "parent_lane": "local_codex",
        "settlement_inbox": DEFAULT_SETTLEMENT_INBOX,
        "branch_return_path": f"ION/05_context/current/agent_context_branches/{branch_id}/returns",
    }


def build_loaded_ref(root: str | Path, path: str | Path, *, source_type: str = "repo") -> dict[str, Any]:
    root_path = Path(root).resolve()
    rel = _rel(path, root_path)
    absolute = Path(path)
    if not absolute.is_absolute():
        absolute = root_path / rel
    return {
        "path": rel,
        "sha256": _sha256_file(absolute),
        "source_type": source_type,
    }


def degrade_to_receipt_only(reason: str = "persona_or_context_not_proven") -> dict[str, Any]:
    return {
        "schema_id": PERSONA_SCHEMA_ID,
        "persona_id": None,
        "persona_mounted": False,
        "presentation_mode": "receipt_only",
        "public_voice": "direct_receipt",
        "gesture_state": "neutral",
        "visible_stance": "source_posture_first",
        "public_working_state": f"receipt_only: {reason}",
        "hidden_reasoning_exposed": False,
        "fallback_behavior": list(DEFAULT_FALLBACK_BEHAVIOR),
        "blockers": [reason],
    }


def build_persona_presentation(
    *,
    persona_id: str | None = None,
    public_working_state: str | None = None,
    public_voice: str = "direct_pragmatic",
    gesture_state: str = "neutral_operational",
    visible_stance: str = "source_posture_first",
    presentation_mode: str | None = None,
    hidden_reasoning_exposed: bool = False,
    fallback_behavior: Sequence[str] | None = None,
) -> dict[str, Any]:
    if hidden_reasoning_exposed:
        mode = presentation_mode or "partial_persona"
    elif not persona_id or not public_working_state:
        return degrade_to_receipt_only("persona_id_or_public_working_state_missing")
    else:
        mode = presentation_mode or "full_persona"

    return {
        "schema_id": PERSONA_SCHEMA_ID,
        "persona_id": persona_id,
        "persona_mounted": mode == "full_persona",
        "presentation_mode": mode,
        "public_voice": public_voice,
        "gesture_state": gesture_state,
        "visible_stance": visible_stance,
        "public_working_state": public_working_state,
        "hidden_reasoning_exposed": hidden_reasoning_exposed,
        "fallback_behavior": list(fallback_behavior or DEFAULT_FALLBACK_BEHAVIOR),
        "blockers": [],
    }


def validate_persona_presentation(persona: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    if persona.get("schema_id") != PERSONA_SCHEMA_ID:
        findings.append({"code": "persona_schema_id_invalid"})
    mode = persona.get("presentation_mode")
    if mode not in PRESENTATION_MODES:
        findings.append({"code": "persona_presentation_mode_invalid", "mode": mode})
    if persona.get("hidden_reasoning_exposed") is not False:
        findings.append({"code": "hidden_reasoning_exposed_forbidden"})
    if mode == "full_persona":
        if not persona.get("persona_id"):
            findings.append({"code": "full_persona_requires_persona_id"})
        if not persona.get("public_working_state"):
            findings.append({"code": "full_persona_requires_public_working_state"})
    if not isinstance(persona.get("fallback_behavior"), list):
        findings.append({"code": "fallback_behavior_must_be_list"})
    return {
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "findings": findings,
    }


def build_mount_receipt(
    *,
    agent_tag: str,
    carrier: str,
    carrier_instance_id: str,
    conversation_tag: str,
    context_instance_id: str,
    branch_id: str,
    current_packet: str,
    model_lane: str,
    loaded_refs: Sequence[Mapping[str, Any]],
    write_scope: Sequence[str] | None = None,
    root: str | Path | None = None,
    parent_context_id: str = DEFAULT_PARENT_CONTEXT_ID,
    source_posture: Mapping[str, Sequence[str]] | None = None,
    return_target: Mapping[str, str] | None = None,
    persona_presentation: Mapping[str, Any] | None = None,
    settlement_required: bool = True,
    created_at: str | None = None,
) -> dict[str, Any]:
    timestamp = created_at or _now()
    receipt_id = _stable_id(
        "carrier-mount-receipt",
        agent_tag,
        carrier,
        carrier_instance_id,
        conversation_tag,
        context_instance_id,
        branch_id,
        current_packet,
        timestamp,
    )
    posture = _default_source_posture()
    for key, values in (source_posture or {}).items():
        if key in posture:
            posture[key] = [str(value) for value in values]
    receipt = {
        "schema_id": SCHEMA_ID,
        "receipt_id": receipt_id,
        "created_at": timestamp,
        "root": Path(root).resolve().as_posix() if root is not None else None,
        "carrier_mount": {
            "agent_tag": agent_tag,
            "carrier": carrier,
            "carrier_instance_id": carrier_instance_id,
            "conversation_tag": conversation_tag,
            "context_instance_id": context_instance_id,
            "branch_id": branch_id,
            "parent_context_id": parent_context_id,
            "current_packet": current_packet,
            "model_lane": model_lane,
            "loaded_refs": [dict(ref) for ref in loaded_refs],
            "authority": {
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "write_scope": list(write_scope or []),
                "settlement_required": settlement_required,
            },
            "source_posture": posture,
            "return_target": dict(return_target or _default_return_target(branch_id)),
        },
        "persona_presentation": dict(persona_presentation or degrade_to_receipt_only()),
        "non_claims": [
            "persona is presentation, not authority",
            "mount receipt is candidate evidence until settled",
            "hidden chain-of-thought is not exposed",
            "no production deployment",
            "no accepted-state claim",
        ],
    }
    return receipt


def validate_mount_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    if receipt.get("schema_id") != SCHEMA_ID:
        findings.append({"code": "receipt_schema_id_invalid"})
    mount = receipt.get("carrier_mount")
    if not isinstance(mount, Mapping):
        return {"ok": False, "verdict": BLOCKED_VERDICT, "findings": [{"code": "carrier_mount_missing"}]}

    required = (
        "agent_tag",
        "carrier",
        "carrier_instance_id",
        "conversation_tag",
        "context_instance_id",
        "branch_id",
        "parent_context_id",
        "current_packet",
        "model_lane",
        "loaded_refs",
        "authority",
        "source_posture",
        "return_target",
    )
    for key in required:
        if mount.get(key) in (None, "", []):
            findings.append({"code": "carrier_mount_required_field_missing", "field": key})

    authority = mount.get("authority") or {}
    if authority.get("production_authority") is not False:
        findings.append({"code": "production_authority_must_be_false"})
    if authority.get("live_execution_authority") is not False:
        findings.append({"code": "live_execution_authority_must_be_false"})
    if authority.get("accepted_state_authority") is not False:
        findings.append({"code": "accepted_state_authority_must_be_false"})
    if authority.get("settlement_required") is not True:
        findings.append({"code": "settlement_required_must_be_true"})
    if not isinstance(authority.get("write_scope"), list):
        findings.append({"code": "write_scope_must_be_list"})

    loaded_refs = mount.get("loaded_refs")
    if not isinstance(loaded_refs, list) or not loaded_refs:
        findings.append({"code": "loaded_refs_required"})
    else:
        for index, ref in enumerate(loaded_refs):
            if not isinstance(ref, Mapping):
                findings.append({"code": "loaded_ref_must_be_object", "index": index})
                continue
            if not ref.get("path"):
                findings.append({"code": "loaded_ref_path_required", "index": index})
            source_type = ref.get("source_type")
            if source_type not in ALLOWED_SOURCE_TYPES:
                findings.append({"code": "loaded_ref_source_type_invalid", "index": index, "source_type": source_type})
            sha = ref.get("sha256")
            if source_type in {"package", "repo", "mcp"} and (not isinstance(sha, str) or len(sha) != 64):
                findings.append({"code": "loaded_ref_sha256_required", "index": index, "path": ref.get("path")})

    posture = mount.get("source_posture") or {}
    for key in ("mcp_observed", "repo_observed", "package_observed", "user_reported", "inferred"):
        if not isinstance(posture.get(key), list):
            findings.append({"code": "source_posture_field_must_be_list", "field": key})

    target = mount.get("return_target") or {}
    for key in ("parent_lane", "settlement_inbox", "branch_return_path"):
        if not target.get(key):
            findings.append({"code": "return_target_field_missing", "field": key})

    persona_result = validate_persona_presentation(receipt.get("persona_presentation") or {})
    for finding in persona_result["findings"]:
        findings.append({"code": "persona_presentation_invalid", "finding": finding})

    return {
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "receipt_id": receipt.get("receipt_id"),
        "context_instance_id": mount.get("context_instance_id"),
        "branch_id": mount.get("branch_id"),
        "findings": findings,
    }


def render_mount_identity_card(receipt: Mapping[str, Any]) -> str:
    mount = receipt.get("carrier_mount") or {}
    authority = mount.get("authority") or {}
    posture = mount.get("source_posture") or {}
    persona = receipt.get("persona_presentation") or {}
    loaded = "\n".join(
        f"- {ref.get('path')} [{ref.get('source_type')}] {ref.get('sha256') or 'no_sha'}"
        for ref in mount.get("loaded_refs", [])
    )
    write_scope = "\n".join(f"- {path}" for path in authority.get("write_scope", []))
    posture_lines = "\n".join(
        f"- {key}: {', '.join(values) if values else 'none'}"
        for key, values in posture.items()
    )
    return (
        "## ION CARRIER MOUNT RECEIPT\n"
        f"- AGENT_TAG: {mount.get('agent_tag')}\n"
        f"- CARRIER: {mount.get('carrier')}\n"
        f"- CARRIER_INSTANCE_ID: {mount.get('carrier_instance_id')}\n"
        f"- CONTEXT_INSTANCE_ID: {mount.get('context_instance_id')}\n"
        f"- BRANCH_ID: {mount.get('branch_id')}\n"
        f"- CURRENT_PACKET: {mount.get('current_packet')}\n"
        f"- MODEL_LANE: {mount.get('model_lane')}\n"
        f"- PRODUCTION_AUTHORITY: {authority.get('production_authority')}\n"
        f"- LIVE_EXECUTION_AUTHORITY: {authority.get('live_execution_authority')}\n"
        f"- ACCEPTED_STATE_AUTHORITY: {authority.get('accepted_state_authority')}\n"
        f"- SETTLEMENT_REQUIRED: {authority.get('settlement_required')}\n"
        f"- PERSONA_PRESENTATION_MODE: {persona.get('presentation_mode')}\n"
        f"- HIDDEN_REASONING_EXPOSED: {persona.get('hidden_reasoning_exposed')}\n"
        "\n### WRITE_SCOPE\n"
        f"{write_scope or '- none'}\n"
        "\n### LOADED_REFS\n"
        f"{loaded or '- none'}\n"
        "\n### SOURCE_POSTURE\n"
        f"{posture_lines or '- none'}\n"
        "\n### RETURN_TARGET\n"
        f"- parent_lane: {(mount.get('return_target') or {}).get('parent_lane')}\n"
        f"- settlement_inbox: {(mount.get('return_target') or {}).get('settlement_inbox')}\n"
        f"- branch_return_path: {(mount.get('return_target') or {}).get('branch_return_path')}\n"
    )


def render_public_working_state(persona: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "## PUBLIC WORKING STATE",
            f"- presentation_mode: {persona.get('presentation_mode')}",
            f"- public_voice: {persona.get('public_voice')}",
            f"- gesture_state: {persona.get('gesture_state')}",
            f"- visible_stance: {persona.get('visible_stance')}",
            f"- public_working_state: {persona.get('public_working_state')}",
            "- hidden_reasoning_exposed: false",
        ]
    )


def detect_mount_drift(receipt: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_mount_receipt(receipt)
    drift = list(validation["findings"])
    mount = receipt.get("carrier_mount") or {}
    persona = receipt.get("persona_presentation") or {}
    if persona.get("presentation_mode") == "full_persona" and persona.get("persona_mounted") is not True:
        drift.append({"code": "full_persona_mode_but_not_mounted"})
    if mount.get("agent_tag") in {"", None, "unknown"}:
        drift.append({"code": "agent_tag_unknown"})
    return {
        "ok": not drift,
        "verdict": READY_VERDICT if not drift else BLOCKED_VERDICT,
        "receipt_id": receipt.get("receipt_id"),
        "drift_findings": drift,
    }


def compare_mount_to_branch_capsule(
    receipt: Mapping[str, Any],
    branch_capsule: Mapping[str, Any],
) -> dict[str, Any]:
    mount = receipt.get("carrier_mount") or {}
    findings: list[dict[str, Any]] = []
    pairs = (
        ("context_instance_id", "context_instance_id"),
        ("branch_id", "branch_id"),
        ("agent_tag", "agent_tag"),
        ("conversation_tag", "conversation_tag"),
        ("parent_context_id", "parent_context_id"),
    )
    for mount_key, branch_key in pairs:
        if mount.get(mount_key) != branch_capsule.get(branch_key):
            findings.append(
                {
                    "code": "mount_branch_capsule_mismatch",
                    "field": mount_key,
                    "mount_value": mount.get(mount_key),
                    "branch_value": branch_capsule.get(branch_key),
                }
            )
    authority = mount.get("authority") or {}
    branch_scope = set(branch_capsule.get("write_scope") or [])
    mount_scope = set(authority.get("write_scope") or [])
    if mount_scope and not mount_scope.issubset(branch_scope):
        findings.append({"code": "mount_write_scope_not_subset_of_branch_capsule"})
    return {
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "findings": findings,
    }


def write_mount_receipt_candidate(
    root: str | Path,
    receipt: Mapping[str, Any],
    *,
    output_dir: str | Path = DEFAULT_MOUNT_RECEIPT_DIR,
) -> dict[str, str]:
    root_path = Path(root).resolve()
    validation = validate_mount_receipt(receipt)
    context_instance_id = (receipt.get("carrier_mount") or {}).get("context_instance_id") or "unknown_context"
    out_dir = root_path / output_dir / str(context_instance_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{receipt.get('receipt_id', 'carrier_mount_receipt')}.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "path": _rel(path, root_path),
        "verdict": validation["verdict"],
        "ok": str(validation["ok"]).lower(),
    }


def build_codex_startup_mount_receipt(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    refs = [
        build_loaded_ref(root_path, "ION/REPO_AUTHORITY.md"),
        build_loaded_ref(root_path, "ION/02_architecture/ION_MOUNT_CONTRACT.md"),
        build_loaded_ref(root_path, "ION/02_architecture/ION_CARRIER_MOUNT_AND_PERSONA_PRESENTATION_PROTOCOL_V0_1.md"),
        build_loaded_ref(root_path, "ION/04_packages/kernel/ion_carrier_mount_receipt.py"),
    ]
    persona = degrade_to_receipt_only("startup_persona_package_not_bound")
    return build_mount_receipt(
        root=root_path,
        agent_tag="codex_local_carrier",
        carrier="codex_cli",
        carrier_instance_id="codex_session_start",
        conversation_tag="codex_solo_boot_context",
        context_instance_id="ctx_codex_startup_receipt_only",
        branch_id="branch_codex_startup_receipt_only",
        current_packet="startup_context_reference_only",
        model_lane="codex_local",
        loaded_refs=refs,
        write_scope=[],
        source_posture={
            "repo_observed": [
                "ION/REPO_AUTHORITY.md",
                "ION/02_architecture/ION_MOUNT_CONTRACT.md",
                "ION/02_architecture/ION_CARRIER_MOUNT_AND_PERSONA_PRESENTATION_PROTOCOL_V0_1.md",
            ],
            "inferred": ["startup context is receipt-only until a packet mounts explicit branch identity"],
        },
        return_target={
            "parent_lane": "codex_solo_boot_context",
            "settlement_inbox": DEFAULT_SETTLEMENT_INBOX,
            "branch_return_path": "ION/05_context/current/agent_context_branches/UNMOUNTED/returns",
        },
        persona_presentation=persona,
    )


def _cli_render(args: argparse.Namespace) -> dict[str, Any]:
    receipt = build_codex_startup_mount_receipt(args.ion_root)
    return {
        "ok": validate_mount_receipt(receipt)["ok"],
        "identity_card": render_mount_identity_card(receipt),
        "receipt": receipt,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ION carrier mount receipt helper")
    parser.add_argument("--ion-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    render = sub.add_parser("render-startup")
    render.set_defaults(func=_cli_render)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = args.func(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
