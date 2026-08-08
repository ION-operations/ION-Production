"""Candidate Cursor CLI packet builder — domain.cursor_packet_builder operating surface.

Builds bounded ``ion.cli_carrier_packet.v0_1`` artifacts from operator/domain objectives
without ChatGPT manual JSON. Candidate-only; no accepted-state or production authority.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any, Mapping

PACKET_SCHEMA_ID = "ion.cli_carrier_packet.v0_1"
BUILDER_SCHEMA_ID = "ion.cursor_packet_builder.v0_1_candidate"
DOMAIN_ID = "domain.cursor_packet_builder"

DEFAULT_ALLOWED_CARRIERS = ("cursor_cli",)
DEFAULT_CARRIER_PREFERENCE = ("cursor_cli",)
DEFAULT_CURSOR_MODEL = "composer-2.5-fast"
OPERATOR_APPROVED_CURSOR_MODELS = frozenset({"composer-2.5-fast", "composer-2.5"})
DEFAULT_ALLOWED_ACTIONS = (
    "source_edit",
    "run_tests",
    "read_files",
    "return_status",
)
DEFAULT_FORBIDDEN_ACTIONS = (
    "codex_usage",
    "accepted_state_claim",
    "production_or_live_authority_claim",
    "secrets_access",
    "git_push",
    "deployment",
    "delete_files",
    "broad_queue_processing",
    "unbounded_loop",
)
DEFAULT_AUTHORITY = {
    "production_authority": False,
    "live_execution_authority": False,
    "accepted_state_authority": False,
    "secrets_authority": False,
}
DEFAULT_STOP_CRITERIA = {
    "max_packets": 1,
    "max_turns": 3,
    "stop_on_failure": True,
    "stop_on_usage_limit": True,
    "codex_carriers_run_enabled": False,
}
STOP_CRITERIA_OVERRIDE_KEYS = (
    "max_packets",
    "max_turns",
    "stop_on_failure",
    "stop_on_usage_limit",
    "codex_carriers_run_enabled",
)
CODEX_CARRIER_IDS = frozenset({"codex_app_server", "codex_cli"})
NON_CLAIMS = [
    "candidate_only",
    "no_accepted_state",
    "no_production_deployment",
    "no_git_push",
    "no_secrets_access",
    "no_codex_default",
    "cursor_packet_builder_domain_candidate",
]

_PACKET_ID_RE = re.compile(r"^pckt-[a-z0-9-]+$")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def _slug(text: str, *, max_len: int = 48) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")
    return (out[:max_len] or "objective").strip("-")


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def bounded_path_ref_problem(value: str) -> str | None:
    """Return a refusal token when *value* is not a bounded repo-relative path."""
    text = str(value or "").strip()
    if not text:
        return "empty_path"
    normalized = text.replace("\\", "/")
    if normalized.startswith("/") or Path(text).is_absolute():
        return "path_absolute_forbidden"
    if normalized.startswith("../") or "/../" in normalized or normalized.endswith("/.."):
        return "path_parent_traversal_forbidden"
    if any(part == ".." for part in PurePath(normalized).parts):
        return "path_parent_traversal_forbidden"
    return None


def validate_bounded_path_fields(
    *,
    allowed_paths: list[str],
    forbidden_paths: list[str],
    evidence_refs: list[str],
) -> str | None:
    for path in allowed_paths:
        problem = bounded_path_ref_problem(path)
        if problem:
            return f"allowed_paths_{problem}"
    for path in forbidden_paths:
        problem = bounded_path_ref_problem(path)
        if problem:
            return f"forbidden_paths_{problem}"
    for path in evidence_refs:
        problem = bounded_path_ref_problem(path)
        if problem:
            return f"evidence_refs_{problem}"
    return None


def _packet_id_from_args(args: Mapping[str, Any]) -> str:
    explicit = str(args.get("packet_id") or "").strip()
    if explicit:
        return explicit
    slug = _slug(str(args.get("objective") or "cursor-packet"))
    return f"pckt-{_now_compact()}-{slug}"


def merge_stop_criteria_args(args: Mapping[str, Any]) -> dict[str, Any]:
    """Merge nested ``stop_criteria`` and route-level override keys from *args*."""
    stop_criteria = dict(DEFAULT_STOP_CRITERIA)
    nested = args.get("stop_criteria")
    if isinstance(nested, Mapping):
        stop_criteria.update({str(k): v for k, v in nested.items()})
    for key in STOP_CRITERIA_OVERRIDE_KEYS:
        if key in args and args.get(key) is not None:
            stop_criteria[key] = args[key]
    return stop_criteria


def _refuses_codex_only(allowed: list[str], preference: list[str]) -> str | None:
    allowed_set = set(allowed)
    pref_set = set(preference)
    if allowed_set and allowed_set <= CODEX_CARRIER_IDS:
        return "codex_only_allowed_carriers_refused"
    if pref_set and pref_set <= CODEX_CARRIER_IDS and "cursor_cli" not in allowed_set:
        return "codex_only_carrier_preference_refused"
    return None


def _compose_prompt(
    *,
    objective: str,
    packet_id: str,
    deliverable_kind: str | None,
    mode: str | None,
    allowed_paths: list[str],
    forbidden_paths: list[str],
    domain_id: str | None,
    role: str | None,
    lane: str | None,
    evidence_refs: list[str],
    prompt_extra: str | None,
    stop_criteria: Mapping[str, Any],
) -> str:
    lines = [
        "ION bounded Cursor CLI carrier packet.",
        "Candidate-only. Do not claim accepted-state, production deployment, git push, deletion, or secrets.",
        "Return a compact result with: mission_satisfied, cycle_gate, artifact_paths, changed_paths, "
        "validation_refs, blocked_reason, and non_claims.",
        "",
        f"packet_id: {packet_id}",
        f"deliverable_kind: {deliverable_kind}",
        f"mode: {mode}",
        "objective:",
        str(objective).strip(),
        "",
        f"allowed_paths: {json.dumps(allowed_paths)}",
        f"forbidden_paths: {json.dumps(forbidden_paths)}",
    ]
    if domain_id:
        lines.extend(["", f"domain_id: {domain_id}"])
    if role:
        lines.append(f"role: {role}")
    if lane:
        lines.append(f"lane: {lane}")
    if evidence_refs:
        lines.extend(["", "evidence_refs:"])
        lines.extend(f"- {ref}" for ref in evidence_refs)
    if prompt_extra and str(prompt_extra).strip():
        lines.extend(["", "operator_notes:", str(prompt_extra).strip()])
    lines.extend(
        [
            "",
            "stop_criteria:",
            json.dumps(dict(stop_criteria), indent=2),
            "",
            "Do NOT call Codex. Work in the active repo under bounded paths only.",
        ]
    )
    return "\n".join(lines)


def build_cursor_packet(args: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    objective = str(args.get("objective") or "").strip()
    if not objective:
        return None, "objective_required"

    allowed_carriers = _as_str_list(args.get("allowed_carriers")) or list(DEFAULT_ALLOWED_CARRIERS)
    carrier_preference = _as_str_list(args.get("carrier_preference")) or list(DEFAULT_CARRIER_PREFERENCE)
    codex_err = _refuses_codex_only(allowed_carriers, carrier_preference)
    if codex_err:
        return None, codex_err
    if "cursor_cli" not in allowed_carriers:
        return None, "cursor_cli_required_in_allowed_carriers"
    requested_model = str(args.get("requested_model") or DEFAULT_CURSOR_MODEL).strip()
    if requested_model not in OPERATOR_APPROVED_CURSOR_MODELS:
        return None, "cursor_model_operator_allowlist_refused"

    packet_id = _packet_id_from_args(args).lower()
    if not _PACKET_ID_RE.match(packet_id):
        return None, "packet_id_format_invalid"

    allowed_paths = _as_str_list(args.get("allowed_paths"))
    forbidden_paths = _as_str_list(args.get("forbidden_paths"))
    evidence_refs = _as_str_list(args.get("evidence_refs"))
    path_err = validate_bounded_path_fields(
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        evidence_refs=evidence_refs,
    )
    if path_err:
        return None, path_err
    domain_id = str(args.get("domain_id") or "").strip() or None
    role = str(args.get("role") or args.get("role_id") or "").strip() or None
    lane = str(args.get("lane") or "").strip() or None
    deliverable_kind = str(args.get("deliverable_kind") or "").strip() or None
    mode = str(args.get("mode") or "").strip() or None
    prompt_extra = str(args.get("prompt_extra") or "").strip() or None

    stop_criteria = merge_stop_criteria_args(args)

    prompt = _compose_prompt(
        objective=objective,
        packet_id=packet_id,
        deliverable_kind=deliverable_kind,
        mode=mode,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        domain_id=domain_id,
        role=role,
        lane=lane,
        evidence_refs=evidence_refs,
        prompt_extra=prompt_extra,
        stop_criteria=stop_criteria,
    )

    packet: dict[str, Any] = {
        "schema_id": PACKET_SCHEMA_ID,
        "packet_id": packet_id,
        "created_at": _now(),
        "created_by": str(args.get("created_by") or "cursor_packet_builder"),
        "builder_schema_id": BUILDER_SCHEMA_ID,
        "builder_domain_id": DOMAIN_ID,
        "allowed_carriers": allowed_carriers,
        "carrier_preference": carrier_preference,
        "requested_model": requested_model,
        "objective": objective,
        "prompt": prompt,
        "cwd": str(args.get("cwd") or ".").strip() or ".",
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "allowed_actions": _as_str_list(args.get("allowed_actions")) or list(DEFAULT_ALLOWED_ACTIONS),
        "forbidden_actions": _as_str_list(args.get("forbidden_actions")) or list(DEFAULT_FORBIDDEN_ACTIONS),
        "authority": dict(DEFAULT_AUTHORITY),
        "stop_criteria": stop_criteria,
        "expected_output": str(args.get("expected_output") or "JSON-like bounded implementation report"),
        "non_claims": list(NON_CLAIMS),
    }
    if domain_id:
        packet["domain_id"] = domain_id
    if role:
        packet["role"] = role
    if lane:
        packet["lane"] = lane
    if deliverable_kind:
        packet["deliverable_kind"] = deliverable_kind
    if mode:
        packet["mode"] = mode
    if evidence_refs:
        packet["evidence_refs"] = evidence_refs

    return packet, None


def packet_preview_metadata(packet: Mapping[str, Any]) -> dict[str, Any]:
    prompt = str(packet.get("prompt") or "")
    body = json.dumps(dict(packet), sort_keys=True, ensure_ascii=False)
    return {
        "packet_id": packet.get("packet_id"),
        "schema_id": packet.get("schema_id"),
        "builder_schema_id": packet.get("builder_schema_id"),
        "builder_domain_id": packet.get("builder_domain_id"),
        "allowed_carriers": list(packet.get("allowed_carriers") or []),
        "carrier_preference": list(packet.get("carrier_preference") or []),
        "stop_criteria": dict(packet.get("stop_criteria") or {}),
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "packet_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "receipt_ready": True,
        "non_claims": list(NON_CLAIMS),
    }


def builder_receipt(
    *,
    operation: str,
    packet: Mapping[str, Any],
    packet_path: str | None = None,
) -> dict[str, Any]:
    meta = packet_preview_metadata(packet)
    return {
        "schema_id": "ion.cli_carrier.receipt.v0_1",
        "receipt_id": f"cli_rcpt_{uuid.uuid4().hex[:12]}",
        "created_at": _now(),
        "operation": operation,
        "packet_id": meta["packet_id"],
        "packet_path": packet_path,
        "sha256": meta["packet_sha256"],
        "builder_schema_id": BUILDER_SCHEMA_ID,
        "builder_domain_id": DOMAIN_ID,
        "non_claims": list(NON_CLAIMS),
    }
