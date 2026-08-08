"""Unified prompt-spawn executor: comms directives + domains → approved CLI carrier.

Candidate-only. Carrier/model selection via unified ion_cli_model_selection with
usage-limit fallback chains.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import inspect
import json
import os
import re
import subprocess
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms_directives import DIRECTIVE_LEDGER_PATH
from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_carrier_spawn_stop import evaluate_carrier_spawn_stop
from .ion_claude_cli_runner import (
    CLAUDE_PROMPT_WRAPPER,
    DEFAULT_CLAUDE_BINARY,
    DEFAULT_MODEL as DEFAULT_CLAUDE_MODEL,
    RUNS_DIR as CLAUDE_RUNS_DIR,
    READY_VERDICT as CLAUDE_READY_VERDICT,
    build_claude_command,
    build_claude_cli_runner_status,
    execute_claude_prompt_once,
)
from .ion_codex_cli_runner import (
    CODEX_PROMPT_WRAPPER,
    DEFAULT_CODEX_BINARY,
    DEFAULT_MODEL as DEFAULT_CODEX_MODEL,
    DEFAULT_REASONING_EFFORT as DEFAULT_CODEX_REASONING_EFFORT,
    RUNS_DIR as CODEX_RUNS_DIR,
    READY_VERDICT as CODEX_READY_VERDICT,
    build_codex_cli_runner_status,
    build_codex_command,
    execute_codex_prompt_once,
    resolve_codex_domain_mount,
)
from .ion_cursor_queue_runner import (
    DEFAULT_CURSOR_BINARY,
    DEFAULT_MODE,
    DEFAULT_MODEL as DEFAULT_CURSOR_MODEL,
    DEFAULT_TIMEOUT_SECONDS,
    PROMPT_WRAPPER,
    _build_cursor_command,
    _cursor_auth_status,
    _cursor_binary_ready,
    decode_cursor_cli_output,
)
from .ion_carrier_failure_signal_classification import (
    maybe_record_whole_cli_quota_exhaustion_after_classification,
    stamp_p21_workflow_honesty_on_run_packet,
)
from .ion_cli_model_selection import (
    execution_models_for_carrier,
    execution_tier_fields_for_admission,
    is_experimental_model,
    is_operator_approved_model,
    is_usage_limit_failure,
    resolve_next_fallback,
)
from .ion_prompt_spawn_carrier_routing import resolve_carrier_for_domain, routing_status
from .ion_advisory_economics_store import (
    CancelUnstartedRequest,
    EconomicsStoreError,
    OrphanLeaseRequest,
    ReserveRequest,
    TRUTH_CONSTANTS as ADVISORY_ECONOMICS_TRUTH_CONSTANTS,
    cancel_unstarted_reservation,
    hold_orphaned_lease,
    open_existing_economics_store,
    reserve_advisory_call,
)
from .ion_cf12_directive_scope_expiry_admission_hook import (
    maybe_record_prompt_spawn_cf12_findings,
)
from .ion_prompt_spawn_admission import (
    carrier_scoped_readiness_blockers,
    advisory_economics_binding_sha256,
    advisory_economics_truth_constants,
    build_advisory_economics_binding,
    derive_directive_provenance_class,
    extract_handoff_source_ref,
    is_advisory_economics_governed_model,
    spawn_requires_advisory_economics_binding,
    merge_advisory_economics_binding_into_admission,
    recompute_admission_sha256,
    resolve_prompt_spawn_read_only_posture,
    resolve_prompt_spawn_template_id,
    resolve_spawn_admission_authority_lexicon,
    resolve_spawn_admission_template_fields,
    validate_advisory_economics_admission_prerequisites,
    validate_advisory_economics_binding_handoff,
    validate_directive_provenance_on_admission,
    validate_prompt_spawn_binding,
    validate_prompt_spawn_route_authority,
)
from .ion_prompt_spawn_context_package_relay_prose_scrub import (
    scrub_context_package_relay_prose,
)
from .ion_prompt_spawn_proof_rejection_coaching import (
    append_proof_rejection_coaching_to_package_text,
)
from .ion_prompt_spawn_runtime_locks import prompt_spawn_runtime_lock
from .ion_context_proof_gate import context_receipt_attestation_sha256
from .ion_directive_transport import (
    DirectiveTransportConflict,
    DirectiveTransportInlineRejected,
    DirectiveTransportMissingSource,
    assert_mutating_prompt_spawn_transport_allowed,
    resolve_directive_transport,
    validate_directive_transport_binding,
)

SCHEMA_ID = "ion.prompt_spawn_executor.v1"
READY_VERDICT = "ION_PROMPT_SPAWN_EXECUTOR_READY"
BLOCKED_VERDICT = "ION_PROMPT_SPAWN_EXECUTOR_BLOCKED"
QUEUE_RELATIVE_PATH = Path("ION/05_context/current/cursor_connector/runtime/prompt_spawn_queue.json")
QUEUE_LOCK_RELATIVE_PATH = Path(
    "ION/05_context/current/cursor_connector/runtime/prompt_spawn_queue.lock"
)
RUNS_DIR = Path("ION/05_context/current/cursor_connector/prompt_spawn_runs")
STATE_PATH = Path("ION/05_context/current/cursor_connector/runtime/prompt_spawn_executor_state.json")
NO_AUTO_CHAIN_ROLES = frozenset({"steward", "vizier", "mason"})
MAX_USAGE_LIMIT_FALLBACK_ATTEMPTS = 4
INTAKE_LEDGER_RELATIVE_PATH = Path(
    "ION/05_context/current/cursor_connector/runtime/prompt_spawn_return_intake_ledger.json"
)
EVIDENCE_RUN_ROOTS: tuple[tuple[str, Path], ...] = (
    ("cursor_cli", RUNS_DIR),
    ("claude_cli", CLAUDE_RUNS_DIR),
    ("codex_cli", CODEX_RUNS_DIR),
)

_ADVISORY_RESERVE_REQUEST_FIELDS = frozenset(
    {
        "idempotency_key",
        "run_id",
        "call_window_id",
        "slot_id",
        "lineage_id",
        "owning_domain_id",
        "budget_window_id",
        "economics_policy_id",
        "policy_sha256",
        "exact_model_id",
        "requested_usd_micros",
        "reservation_id",
        "lease_id",
        "lease_expires_at",
        "occurred_at",
        "evidence_ref",
    }
)
_EXTERNAL_NO_PROVIDER_START_CLASS = "positive_no_provider_process_start"
_RUNTIME_ECONOMICS_DOMAIN_ID = "domain.runtime_carrier_and_action_admission"


def _advisory_economics_authority_payload() -> dict[str, Any]:
    return {
        **dict(ADVISORY_ECONOMICS_TRUTH_CONSTANTS),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _is_sha256_hex(value: Any) -> bool:
    normalized = str(value or "").strip().lower()
    return len(normalized) == 64 and all(
        character in "0123456789abcdef" for character in normalized
    )


def _governed_advisory_max_budget_usd(
    binding: Mapping[str, Any] | None,
) -> tuple[float | None, list[str]]:
    """Derive provider-posthoc CLI input only from a complete sealed binding."""

    if not isinstance(binding, Mapping):
        return None, ["advisory_economics_governed_budget_binding_required"]
    if binding.get("binding_sha256") != advisory_economics_binding_sha256(binding):
        return None, ["advisory_economics_governed_budget_binding_hash_mismatch"]
    blockers: list[str] = []
    for truth_field, expected in ADVISORY_ECONOMICS_TRUTH_CONSTANTS.items():
        if binding.get(truth_field) != expected:
            blockers.append(
                f"advisory_economics_governed_budget_{truth_field}_truth_mismatch"
            )
    reserved_usd_micros = binding.get("reserved_usd_micros")
    if (
        not isinstance(reserved_usd_micros, int)
        or isinstance(reserved_usd_micros, bool)
        or reserved_usd_micros <= 0
    ):
        blockers.append(
            "advisory_economics_governed_budget_reserved_usd_micros_nonpositive"
        )
    if blockers:
        return None, list(dict.fromkeys(blockers))
    max_budget_usd = reserved_usd_micros / 1_000_000.0
    if max_budget_usd <= 0:
        return None, ["advisory_economics_governed_budget_usd_nonpositive"]
    return max_budget_usd, []


def _external_no_provider_start_attestation(
    evidence: Mapping[str, Any] | None,
    *,
    binding: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    """Validate caller-supplied positive no-process evidence without inventing it."""

    if not isinstance(evidence, Mapping):
        return None, ["external_no_provider_process_start_evidence_required"]
    row = dict(evidence)
    blockers: list[str] = []
    if row.get("attestation_class") != _EXTERNAL_NO_PROVIDER_START_CLASS:
        blockers.append("external_no_provider_process_start_attestation_class_invalid")
    if row.get("no_provider_process_started") is not True:
        blockers.append("external_no_provider_process_start_positive_attestation_required")
    if row.get("externally_supplied") is not True:
        blockers.append("external_no_provider_process_start_external_supply_not_attested")
    issuer_domain_id = str(row.get("issuer_domain_id") or "").strip()
    if not issuer_domain_id:
        blockers.append("external_no_provider_process_start_issuer_domain_required")
    elif issuer_domain_id == _RUNTIME_ECONOMICS_DOMAIN_ID:
        blockers.append("external_no_provider_process_start_self_attestation_forbidden")
    proof_digest = str(row.get("proof_digest") or "").strip().lower()
    if not _is_sha256_hex(proof_digest):
        blockers.append("external_no_provider_process_start_proof_digest_invalid")
    evidence_ref = str(row.get("evidence_ref") or "").strip()
    if not evidence_ref:
        blockers.append("external_no_provider_process_start_evidence_ref_required")
    for field in ("run_id", "reservation_id", "lease_id"):
        if str(row.get(field) or "").strip() != str(binding.get(field) or "").strip():
            blockers.append(f"external_no_provider_process_start_{field}_mismatch")
    if blockers:
        return None, list(dict.fromkeys(blockers))
    return {
        "proof_digest": proof_digest,
        "evidence_ref": evidence_ref,
        "issuer_domain_id": issuer_domain_id,
        "attestation_class": _EXTERNAL_NO_PROVIDER_START_CLASS,
    }, []


def _hold_advisory_economics_reservation(
    connection: Any,
    *,
    binding: Mapping[str, Any],
    outcome: str,
    evidence_ref: str,
    occurred_at: str,
    reason_suffix: str,
) -> dict[str, Any]:
    request = OrphanLeaseRequest(
        idempotency_key=(
            f"{binding.get('idempotency_key')}:orphan:{outcome}:{reason_suffix}"
        ),
        reservation_id=str(binding.get("reservation_id") or ""),
        lease_id=str(binding.get("lease_id") or ""),
        run_id=str(binding.get("run_id") or ""),
        reason=f"{outcome}:{reason_suffix}",
        occurred_at=occurred_at,
        evidence_ref=evidence_ref,
    )
    try:
        result = hold_orphaned_lease(connection, request)
        return {
            "ok": True,
            "action": "hold_orphaned_lease",
            "result": result.to_dict(),
            "quarantine_required": True,
            **_advisory_economics_authority_payload(),
        }
    except Exception as exc:
        return {
            "ok": False,
            "action": "hold_orphaned_lease_refused_quarantine_required",
            "blockers": [
                f"advisory_economics_orphan_hold_refused:{type(exc).__name__}"
            ],
            "quarantine_required": True,
            **_advisory_economics_authority_payload(),
        }


def _reconcile_executor_advisory_economics_before_provider_start(
    *,
    binding: Mapping[str, Any] | None,
    outcome: str,
    evidence_ref: str,
    occurred_at: str,
    external_no_start_evidence: Mapping[str, Any] | None = None,
    provider_start_uncertain: bool = False,
) -> dict[str, Any]:
    """Cancel only with external positive proof; otherwise retain and quarantine."""

    if not isinstance(binding, Mapping):
        return {
            "ok": False,
            "action": "binding_missing_quarantine_required",
            "blockers": ["advisory_economics_reconcile_binding_missing"],
            "quarantine_required": True,
            **_advisory_economics_authority_payload(),
        }
    database_path = str(binding.get("economics_database_path") or "").strip()
    if not database_path:
        return {
            "ok": False,
            "action": "database_binding_missing_quarantine_required",
            "blockers": ["advisory_economics_reconcile_database_binding_missing"],
            "quarantine_required": True,
            **_advisory_economics_authority_payload(),
        }
    try:
        connection = open_existing_economics_store(database_path)
    except Exception as exc:
        return {
            "ok": False,
            "action": "database_unavailable_quarantine_required",
            "blockers": [
                f"advisory_economics_reconcile_database_unavailable:{type(exc).__name__}"
            ],
            "quarantine_required": True,
            **_advisory_economics_authority_payload(),
        }
    try:
        proof, proof_blockers = _external_no_provider_start_attestation(
            external_no_start_evidence,
            binding=binding,
        )
        if provider_start_uncertain or proof is None:
            suffix = (
                "provider_start_uncertain"
                if provider_start_uncertain
                else "external_no_start_evidence_absent_or_invalid"
            )
            hold = _hold_advisory_economics_reservation(
                connection,
                binding=binding,
                outcome=outcome,
                evidence_ref=evidence_ref,
                occurred_at=occurred_at,
                reason_suffix=suffix,
            )
            if proof_blockers:
                hold["cancellation_blockers"] = proof_blockers
            return hold

        cancel_request = CancelUnstartedRequest(
            idempotency_key=f"{binding.get('idempotency_key')}:cancel:{outcome}",
            reservation_id=str(binding.get("reservation_id") or ""),
            lease_id=str(binding.get("lease_id") or ""),
            run_id=str(binding.get("run_id") or ""),
            no_process_proof_digest=str(proof["proof_digest"]),
            no_process_attested=True,
            occurred_at=occurred_at,
            evidence_ref=str(proof["evidence_ref"]),
        )
        try:
            result = cancel_unstarted_reservation(connection, cancel_request)
            return {
                "ok": True,
                "action": "cancel_unstarted_reservation",
                "result": result.to_dict(),
                "external_no_start_attestation": {
                    "issuer_domain_id": proof["issuer_domain_id"],
                    "attestation_class": proof["attestation_class"],
                    "evidence_ref": proof["evidence_ref"],
                    "proof_digest": proof["proof_digest"],
                },
                "quarantine_required": False,
                **_advisory_economics_authority_payload(),
            }
        except Exception as exc:
            hold = _hold_advisory_economics_reservation(
                connection,
                binding=binding,
                outcome=outcome,
                evidence_ref=evidence_ref,
                occurred_at=occurred_at,
                reason_suffix="cancellation_refused",
            )
            hold["cancellation_blockers"] = [
                f"advisory_economics_cancel_refused:{type(exc).__name__}"
            ]
            return hold
    finally:
        connection.close()


def _attempt_executor_advisory_economics_reservation(
    *,
    shell_root: Path,
    intent: Mapping[str, Any],
    model: str,
    run_id: str,
    domain_id: str | None,
) -> dict[str, Any]:
    """Reserve through one existing-only connection and seal the R3 handoff."""

    blockers = validate_advisory_economics_admission_prerequisites(
        intent=intent,
        model=model,
        domain_id=domain_id,
        shell_root=shell_root,
    )
    source_request = intent.get("advisory_economics_reservation_request")
    if source_request is None:
        source_request = intent.get("reservation_request")
    request_mapping = dict(source_request) if isinstance(source_request, Mapping) else {}
    intent_id = str(intent.get("intent_id") or "").strip()
    intent_semantic_digest = str(_stored_intent_semantic_digest(intent) or "").strip()
    for store_owned_field in (
        "attempt_id",
        "reserve_receipt_sha256",
        "reservation_receipt_sha256",
    ):
        if store_owned_field in request_mapping:
            blockers.append(
                f"advisory_economics_caller_supplied_{store_owned_field}_forbidden"
            )
    if not intent_id:
        blockers.append("advisory_economics_intent_id_required")
    if not _is_sha256_hex(intent_semantic_digest):
        blockers.append("advisory_economics_intent_semantic_digest_invalid")

    request_mapping["run_id"] = run_id
    request_mapping["exact_model_id"] = str(model).strip()
    requested_domain_id = str(request_mapping.get("owning_domain_id") or "").strip()
    if requested_domain_id != str(domain_id or "").strip():
        blockers.append("advisory_economics_domain_id_binding_mismatch")
    concurrency_binding = {
        "call_id": str(request_mapping.get("call_window_id") or ""),
        "slot_id": str(request_mapping.get("slot_id") or ""),
        "lineage_id": str(request_mapping.get("lineage_id") or ""),
        "domain_id": requested_domain_id,
        "budget_window_id": str(request_mapping.get("budget_window_id") or ""),
        "lease_id": str(request_mapping.get("lease_id") or ""),
    }
    supplied_concurrency = request_mapping.get("concurrency_binding")
    if supplied_concurrency is not None and supplied_concurrency != concurrency_binding:
        blockers.append("advisory_economics_concurrency_binding_mismatch")
    if blockers:
        return {
            "ok": False,
            "blockers": list(dict.fromkeys(blockers)),
            **_advisory_economics_authority_payload(),
        }

    database_path = Path(str(intent.get("economics_database_path") or "").strip())
    if not database_path.is_absolute():
        database_path = shell_root.resolve() / database_path
    database_path = database_path.resolve()
    store_request_mapping = {
        key: request_mapping.get(key) for key in _ADVISORY_RESERVE_REQUEST_FIELDS
    }
    try:
        reserve_request = ReserveRequest(**store_request_mapping)
        connection = open_existing_economics_store(database_path)
        try:
            reserve_result = reserve_advisory_call(connection, reserve_request)
        finally:
            connection.close()
    except EconomicsStoreError as exc:
        return {
            "ok": False,
            "blockers": [
                f"spawn_admission_advisory_economics_reserve_refused:{type(exc).__name__}"
            ],
            "error": exc.to_dict(),
            **_advisory_economics_authority_payload(),
        }
    except (TypeError, ValueError) as exc:
        return {
            "ok": False,
            "blockers": [
                f"spawn_admission_advisory_economics_reserve_request_invalid:{type(exc).__name__}"
            ],
            **_advisory_economics_authority_payload(),
        }

    reserve_payload = reserve_result.to_dict()
    store_attempt_id = str(reserve_payload.get("attempt_id") or "")
    store_reservation_receipt_sha256 = str(
        reserve_payload.get("reserve_receipt_sha256") or ""
    )
    intent_for_binding = dict(intent)
    intent_for_binding["intent_semantic_digest"] = intent_semantic_digest
    binding = build_advisory_economics_binding(
        economics_database_path=database_path,
        intent=intent_for_binding,
        reservation_request=store_request_mapping,
        run_id=run_id,
        reserve_result=reserve_payload,
    )
    immutable_values = {
        "economics_database_path": str(database_path),
        "reservation_id": reserve_payload.get("reservation_id"),
        "lease_id": reserve_payload.get("lease_id"),
        "attempt_id": store_attempt_id,
        "idempotency_key": request_mapping.get("idempotency_key"),
        "run_id": reserve_payload.get("run_id"),
        "intent_id": intent_id,
        "intent_semantic_digest": intent_semantic_digest,
        "requested_model_id": str(model).strip(),
        "reserved_usd_micros": reserve_payload.get("requested_usd_micros"),
        "call_id": request_mapping.get("call_window_id"),
        "slot_id": request_mapping.get("slot_id"),
        "domain_id": requested_domain_id,
        "lineage_id": request_mapping.get("lineage_id"),
        "concurrency_binding": concurrency_binding,
        "lease_expires_at": request_mapping.get("lease_expires_at"),
        "reservation_receipt_sha256": store_reservation_receipt_sha256,
    }
    binding_blockers: list[str] = []
    if not store_attempt_id:
        binding_blockers.append(
            "advisory_economics_store_attempt_id_required"
        )
    if not _is_sha256_hex(store_reservation_receipt_sha256):
        binding_blockers.append(
            "advisory_economics_store_reservation_receipt_sha256_invalid"
        )
    for field, value in immutable_values.items():
        if binding.get(field) != value:
            binding_blockers.append(
                f"advisory_economics_binding_{field}_immutable_mismatch"
            )
    for truth_field, truth_value in advisory_economics_truth_constants().items():
        if truth_value != ADVISORY_ECONOMICS_TRUTH_CONSTANTS.get(truth_field):
            binding_blockers.append(
                f"advisory_economics_binding_{truth_field}_authority_mismatch"
            )
        if binding.get(truth_field) != truth_value:
            binding_blockers.append(
                f"advisory_economics_binding_{truth_field}_immutable_mismatch"
            )
    if binding.get("reserve_receipt_sha256") != store_reservation_receipt_sha256:
        binding_blockers.append(
            "advisory_economics_binding_reserve_receipt_sha256_immutable_mismatch"
        )
    if binding.get("binding_sha256") != advisory_economics_binding_sha256(binding):
        binding_blockers.append(
            "advisory_economics_binding_sha256_seal_mismatch"
        )
    if binding_blockers:
        reconcile = _reconcile_executor_advisory_economics_before_provider_start(
            binding=binding,
            outcome="executor_immutable_binding_mismatch",
            evidence_ref=f"evidence://prompt_spawn/{run_id}/binding_blocked",
            occurred_at=_now(),
            external_no_start_evidence=(
                intent.get("no_provider_process_start_evidence")
                if isinstance(intent.get("no_provider_process_start_evidence"), Mapping)
                else None
            ),
        )
        return {
            "ok": False,
            "blockers": list(dict.fromkeys(binding_blockers)),
            "binding": binding,
            "reconcile": reconcile,
            **_advisory_economics_authority_payload(),
        }
    return {
        "ok": True,
        "blockers": [],
        "binding": binding,
        "reserve_result": reserve_payload,
        **_advisory_economics_authority_payload(),
    }

RETRY_POSTURE_EXECUTABLE = "executable"
RETRY_POSTURE_TRANSIENT = "transient"
RETRY_POSTURE_SUPERSEDED = "superseded"
RETRY_POSTURE_STRUCTURAL_QUARANTINE = "structural_proof_quarantine"
RETRY_POSTURES = frozenset(
    {
        RETRY_POSTURE_EXECUTABLE,
        RETRY_POSTURE_TRANSIENT,
        RETRY_POSTURE_SUPERSEDED,
        RETRY_POSTURE_STRUCTURAL_QUARANTINE,
    }
)
COLLECTIBLE_RETRY_POSTURES = frozenset(
    {RETRY_POSTURE_EXECUTABLE, RETRY_POSTURE_TRANSIENT}
)
TRANSIENT_ONLY_FINDINGS = frozenset(
    {
        "prompt_spawn_intent_execution_already_claimed",
        "experimental_cursor_concurrency_limit",
        "carrier_unavailable",
        "authentication_required",
        "usage_limit",
        "run_returncode_nonzero",
        "provider_timeout",
        "carrier_not_ready",
        "cursor_binary_missing",
        "cursor_auth_unverified",
    }
)
STRUCTURAL_STANDALONE_FINDINGS = frozenset(
    {
        "raw_return_gates_not_accepted",
        "missing_required_read_path",
        "required_read_source_sha256_mismatch",
        "no_matching_hash_line_excerpt_evidence",
        "context_receipt_machine_attestation_mismatch",
    }
)
INTENT_ID_SEMANTIC_MISMATCH = "INTENT_ID_SEMANTIC_MISMATCH"
INTENT_DEQUEUE_SEMANTIC_MISMATCH = "INTENT_DEQUEUE_SEMANTIC_MISMATCH"
COLLISION_RESTORE_SEMANTIC_CONFLICT = "COLLISION_RESTORE_SEMANTIC_CONFLICT"
COLLISION_RESTORE_VALIDATION_FAILED = "COLLISION_RESTORE_VALIDATION_FAILED"
COLLISION_RECEIPTS_RELATIVE_PATH = Path(
    "ION/05_context/current/cursor_connector/runtime/receipts"
)
COLLISION_RESTORE_PROVENANCE_ORIGIN = "collision_restore_20260721"
COLLISION_RESTORE_STRIP_FIELDS = frozenset(
    {
        "bundle",
        "carrier_resolution",
        "execution_carrier",
        "spawn_admission",
        "spawn_admission_path",
        "spawn_admission_id",
        "spawn_admission_sha256",
        "work_class",
        "risk_level",
        "context_need",
        "requested_carrier",
        "requested_model",
        "requested_reasoning_effort",
        "routing_decision",
        "routing_decision_id",
        "routing_decision_sha256",
        "routing_packet_sha256",
        "routing_source_sha256",
        "selected_model",
        "selected_reasoning_effort",
        "selection_reason",
        "budget_pool",
        "reviewer",
        "review_required_by",
        "escalation_triggers",
        "experimental_model",
        "experimental_model_explicit_only",
        "template_id",
    }
)
INTENT_SEMANTIC_DIGEST_FIELDS = (
    "domain_id",
    "index",
    "objective",
    "role",
    "source_kind",
    "source_ref",
)


def _stable_findings_digest(findings: list[str]) -> str:
    normalized = sorted({str(item).strip() for item in findings if str(item).strip()})
    return hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _has_trusted_fresh_provenance(intent: Mapping[str, Any]) -> bool:
    return (
        str(intent.get("intent_provenance") or "") == "fresh"
        and bool(str(intent.get("provenance_origin") or "").strip())
        and not intent.get("retry_of_run_id")
    )


def _has_structural_findings(
    findings: list[str],
    *,
    provider_execution_ok: bool | None = None,
) -> bool:
    for finding in findings:
        text = str(finding or "").strip()
        if not text:
            continue
        if text.startswith("template_action:"):
            return True
        if text.startswith("context_proof:"):
            if (
                text == "context_proof:leading_preamble_stripped"
                and provider_execution_ok is True
            ):
                continue
            return True
        if text in STRUCTURAL_STANDALONE_FINDINGS:
            return True
        if "witness_demotion" in text:
            return True
    return False


def _is_exclusively_transient_findings(
    findings: list[str],
    *,
    provider_execution_ok: bool | None = None,
) -> bool:
    if _has_structural_findings(findings, provider_execution_ok=provider_execution_ok):
        return False
    if not findings:
        return provider_execution_ok is False
    normalized: list[str] = []
    for finding in findings:
        text = str(finding or "").strip()
        if not text:
            continue
        if text.startswith("context_proof:") or text.startswith("template_action:"):
            return False
        normalized.append(text)
    if not normalized:
        return provider_execution_ok is False
    return all(item in TRANSIENT_ONLY_FINDINGS for item in normalized)


def _load_intake_ledger_for_evidence(shell_root: Path) -> dict[str, Any]:
    ledger = _read_json(shell_root / INTAKE_LEDGER_RELATIVE_PATH)
    if not ledger:
        return {"schema_id": "ion.prompt_spawn_return_intake_ledger.v1", "records": []}
    if not isinstance(ledger.get("records"), list):
        ledger["records"] = []
    return ledger


def _expected_semantic_digest(
    expected_intent: Mapping[str, Any] | str | None,
    *,
    intent_id: str,
) -> str | None:
    if isinstance(expected_intent, str):
        digest = expected_intent.strip()
        return digest or None
    if isinstance(expected_intent, Mapping):
        stored = str(expected_intent.get("intent_semantic_digest") or "").strip()
        if stored:
            return stored
        if str(expected_intent.get("intent_id") or "").strip() in ("", intent_id):
            return intent_semantic_digest(expected_intent)
    return None


def _run_intent_from_artifact(run: Mapping[str, Any]) -> dict[str, Any]:
    intent = run.get("intent") if isinstance(run.get("intent"), Mapping) else {}
    spawn_row = run.get("spawn_row") if isinstance(run.get("spawn_row"), Mapping) else {}
    if intent:
        return dict(intent)
    if spawn_row:
        return {
            "intent_id": spawn_row.get("intent_id"),
            "domain_id": spawn_row.get("domain_id"),
            "index": spawn_row.get("index"),
            "objective": spawn_row.get("objective"),
            "role": spawn_row.get("role"),
            "source_kind": spawn_row.get("source_kind"),
            "source_ref": spawn_row.get("source_ref"),
        }
    return {}


def _build_run_semantic_digest_index(shell_root: Path) -> dict[str, str]:
    digest_by_run_id: dict[str, str] = {}
    for _carrier_id, rel_root in EVIDENCE_RUN_ROOTS:
        runs_root = shell_root / rel_root
        if not runs_root.is_dir():
            continue
        for run_path in sorted(runs_root.glob("*/run.json")):
            run = _read_json(run_path)
            if not run:
                continue
            run_id = str(run.get("run_id") or run_path.parent.name).strip()
            if not run_id:
                continue
            intent = _run_intent_from_artifact(run)
            if not intent:
                continue
            digest_by_run_id[run_id] = _stored_intent_semantic_digest(intent)
    return digest_by_run_id


def _build_intent_evidence_snapshot(shell_root: Path) -> dict[str, Any]:
    """Index queue, ledger, and run evidence once for bulk retry classification."""

    queue = load_prompt_spawn_queue(shell_root)
    ledger = _load_intake_ledger_for_evidence(shell_root)
    queue_by_intent_id: dict[str, list[dict[str, Any]]] = {}
    for item in queue.get("pending") or []:
        if not isinstance(item, Mapping):
            continue
        intent_id = str(item.get("intent_id") or "").strip()
        if intent_id:
            queue_by_intent_id.setdefault(intent_id, []).append(dict(item))

    run_digest_by_run_id: dict[str, str] = {}
    run_artifacts_by_key: dict[str, list[dict[str, Any]]] = {}
    for carrier_id, rel_root in EVIDENCE_RUN_ROOTS:
        runs_root = shell_root / rel_root
        if not runs_root.is_dir():
            continue
        for run_path in sorted(runs_root.glob("*/run.json")):
            run = _read_json(run_path)
            if not run:
                continue
            intent = _run_intent_from_artifact(run)
            run_id = str(run.get("run_id") or run_path.parent.name).strip()
            intent_id = str(intent.get("intent_id") or "").strip()
            semantic_digest = _stored_intent_semantic_digest(intent) if intent else ""
            if run_id and semantic_digest:
                run_digest_by_run_id[run_id] = semantic_digest
            artifact = {
                "carrier_id": carrier_id,
                "run_id": run_id,
                "run_json_path": _rel(shell_root, run_path),
                "provider_execution_ok": run.get("provider_execution_ok"),
                "intent_semantic_digest": semantic_digest or None,
                "findings": list(
                    ((run.get("intake") or {}).get("evaluation") or {}).get("findings")
                    or []
                ),
            }
            for key in {intent_id, run_id} - {""}:
                run_artifacts_by_key.setdefault(key, []).append(artifact)

    return {
        "queue_by_intent_id": queue_by_intent_id,
        "ledger": ledger,
        "run_digest_by_run_id": run_digest_by_run_id,
        "run_artifacts_by_key": run_artifacts_by_key,
    }


def _ledger_record_semantic_digest(
    record: Mapping[str, Any],
    *,
    run_digest_by_run_id: Mapping[str, str],
) -> str:
    stored = str(record.get("intent_semantic_digest") or "").strip()
    if stored:
        return stored
    run_id = str(record.get("run_id") or "").strip()
    if run_id:
        bound = str(run_digest_by_run_id.get(run_id) or "").strip()
        if bound:
            return bound
    basis = {
        field: record.get(field)
        for field in INTENT_SEMANTIC_DIGEST_FIELDS
        if str(record.get(field) or "").strip()
    }
    if len(basis) >= 3:
        return intent_semantic_digest(basis)
    return ""


def _semantic_collision_detail(
    *,
    intent_id: str,
    digest_run_ids: Mapping[str, list[str]],
    expected_digest: str | None,
) -> dict[str, Any]:
    return {
        "intent_id": intent_id,
        "distinct_semantic_digests": sorted(digest_run_ids.keys()),
        "semantic_digest_run_ids": {
            digest: sorted(run_ids)
            for digest, run_ids in sorted(digest_run_ids.items())
        },
        "expected_semantic_digest": expected_digest,
    }


def _invoke_evidence_resolver(
    resolver: Any,
    shell_root: Path,
    intent_id: str,
    intent: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        positional = [
            parameter
            for parameter in inspect.signature(resolver).parameters.values()
            if parameter.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
    except (TypeError, ValueError):
        positional = []
    if len(positional) >= 3:
        return resolver(shell_root, intent_id, intent)
    return resolver(shell_root, intent_id)


def _resolve_intent_evidence(
    shell_root: Path,
    intent_id: str,
    expected_intent: Mapping[str, Any] | str | None = None,
    *,
    evidence_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic intent crosswalk over queue, ledger, and run artifacts."""

    normalized_id = str(intent_id or "").strip()
    empty = {
        "intent_id": "",
        "resolved": False,
        "ambiguous": False,
        "queue_intent": None,
        "ledger_records": [],
        "latest_rejection": None,
        "latest_rejection_findings": [],
        "provider_execution_ok": None,
        "run_artifacts": [],
        "evidence_link": None,
        "semantic_collision_detail": None,
    }
    if not normalized_id:
        return empty

    snapshot = (
        evidence_snapshot
        if isinstance(evidence_snapshot, Mapping)
        else _build_intent_evidence_snapshot(shell_root)
    )
    expected_digest = _expected_semantic_digest(
        expected_intent,
        intent_id=normalized_id,
    )
    run_digest_by_run_id = snapshot.get("run_digest_by_run_id") or {}

    queue_matches = [
        dict(item)
        for item in ((snapshot.get("queue_by_intent_id") or {}).get(normalized_id) or [])
        if isinstance(item, Mapping)
    ]
    queue_intent: Mapping[str, Any] | None
    if len(queue_matches) == 1:
        queue_intent = queue_matches[0]
    elif not queue_matches:
        queue_intent = None
    else:
        queue_intent = None
    if expected_digest and queue_matches:
        semantic_queue_matches = [
            item
            for item in queue_matches
            if _stored_intent_semantic_digest(item) == expected_digest
        ]
        if len(semantic_queue_matches) == 1:
            queue_intent = semantic_queue_matches[0]
        else:
            queue_intent = None

    ledger = snapshot.get("ledger") or {}
    ledger_records: list[dict[str, Any]] = []
    for record in ledger.get("records") or []:
        if not isinstance(record, Mapping):
            continue
        record_intent_id = str(record.get("intent_id") or "").strip()
        run_id = str(record.get("run_id") or "").strip()
        if record_intent_id != normalized_id and run_id != normalized_id:
            continue
        record_copy = dict(record)
        digest = _ledger_record_semantic_digest(
            record_copy,
            run_digest_by_run_id=run_digest_by_run_id,
        )
        if digest:
            record_copy["intent_semantic_digest"] = digest
        ledger_records.append(record_copy)

    run_artifacts = [
        dict(item)
        for item in (
            (snapshot.get("run_artifacts_by_key") or {}).get(normalized_id) or []
        )
        if isinstance(item, Mapping)
    ]

    digest_run_ids: dict[str, list[str]] = {}
    for record in ledger_records:
        digest = str(record.get("intent_semantic_digest") or "").strip()
        run_id = str(record.get("run_id") or "").strip()
        if digest and run_id:
            digest_run_ids.setdefault(digest, []).append(run_id)
    for artifact in run_artifacts:
        digest = str(artifact.get("intent_semantic_digest") or "").strip()
        run_id = str(artifact.get("run_id") or "").strip()
        if digest and run_id and run_id not in digest_run_ids.get(digest, []):
            digest_run_ids.setdefault(digest, []).append(run_id)

    distinct_digests = {
        digest for digest in digest_run_ids if str(digest).strip()
    }
    semantic_collision_detail = None
    if len(distinct_digests) > 1:
        semantic_collision_detail = _semantic_collision_detail(
            intent_id=normalized_id,
            digest_run_ids=digest_run_ids,
            expected_digest=expected_digest,
        )

    if expected_digest:
        ledger_records = [
            record
            for record in ledger_records
            if str(record.get("intent_semantic_digest") or "").strip() == expected_digest
        ]
        run_artifacts = [
            artifact
            for artifact in run_artifacts
            if str(artifact.get("intent_semantic_digest") or "").strip() == expected_digest
        ]

    rejected_records = [
        record for record in ledger_records if record.get("accepted") is False
    ]
    latest_rejection: dict[str, Any] | None = None
    if len(rejected_records) == 1:
        latest_rejection = rejected_records[0]
    elif len(rejected_records) > 1:
        latest_rejection = max(
            rejected_records,
            key=lambda item: (
                str(item.get("intake_at") or ""),
                str(item.get("run_id") or ""),
            ),
        )

    crosswalk_rejection_records = [
        record
        for record in ledger_records
        if record.get("accepted") is False
        and (
            str(record.get("intent_id") or "").strip() == normalized_id
            or str(record.get("run_id") or "").strip() == normalized_id
        )
    ]
    ambiguous = len(distinct_digests) > 1 and expected_digest is None
    if len(crosswalk_rejection_records) > 1 and latest_rejection is None:
        ambiguous = True
    if len(crosswalk_rejection_records) > 1:
        distinct_run_ids = {
            str(record.get("run_id") or "")
            for record in crosswalk_rejection_records
            if str(record.get("run_id") or "").strip()
        }
        if len(distinct_run_ids) > 1 and not any(
            str(record.get("intent_id") or "").strip() == normalized_id
            for record in crosswalk_rejection_records
        ):
            ambiguous = True

    latest_findings = list((latest_rejection or {}).get("findings") or [])
    if not latest_findings and run_artifacts:
        latest_run = max(
            run_artifacts,
            key=lambda item: str(item.get("run_json_path") or ""),
        )
        latest_findings = list(latest_run.get("findings") or [])

    provider_execution_ok = None
    if latest_rejection is not None:
        provider_execution_ok = latest_rejection.get("provider_execution_ok")
    elif run_artifacts:
        provider_execution_ok = run_artifacts[-1].get("provider_execution_ok")

    evidence_link = None
    if latest_rejection is not None:
        evidence_link = str(
            latest_rejection.get("task_return_path")
            or latest_rejection.get("output_path")
            or ""
        ).strip() or None
    elif run_artifacts:
        evidence_link = str(run_artifacts[-1].get("run_json_path") or "").strip() or None

    resolved = bool(ledger_records or run_artifacts or crosswalk_rejection_records)
    return {
        "intent_id": normalized_id,
        "resolved": resolved,
        "ambiguous": ambiguous,
        "queue_intent": dict(queue_intent) if isinstance(queue_intent, Mapping) else None,
        "ledger_records": ledger_records,
        "latest_rejection": latest_rejection,
        "latest_rejection_findings": latest_findings,
        "provider_execution_ok": provider_execution_ok,
        "run_artifacts": run_artifacts,
        "evidence_link": evidence_link,
        "semantic_collision_detail": semantic_collision_detail,
    }


def classify_prompt_spawn_retry_posture(
    shell_root: Path,
    intent: Mapping[str, Any],
    *,
    evidence_resolver: Any | None = None,
) -> dict[str, Any]:
    """Classify one queue intent using immutable evidence keyed by intent semantics."""

    intent_id = str(intent.get("intent_id") or "").strip()
    resolver = evidence_resolver or _resolve_intent_evidence
    evidence = (
        _invoke_evidence_resolver(resolver, shell_root, intent_id, intent)
        if intent_id
        else {
            "resolved": False,
            "ambiguous": False,
            "latest_rejection": None,
            "latest_rejection_findings": [],
            "provider_execution_ok": None,
            "evidence_link": None,
        }
    )

    def _result(posture: str, *, reason: str) -> dict[str, Any]:
        return {
            "intent_id": intent_id or None,
            "posture": posture,
            "reason": reason,
            "evidence_link": evidence.get("evidence_link"),
            "findings_digest": _stable_findings_digest(
                list(evidence.get("latest_rejection_findings") or [])
            ),
            "crosswalk_resolved": evidence.get("resolved") is True
            and evidence.get("ambiguous") is not True,
            "production_authority": False,
        }

    if (
        intent.get("superseded") is True
        or str(intent.get("supersession_ref") or "").strip()
        or str(intent.get("retry_posture") or "").strip() == RETRY_POSTURE_SUPERSEDED
    ):
        return _result(RETRY_POSTURE_SUPERSEDED, reason="explicit_superseded_signal")

    if intent_id and evidence.get("ambiguous"):
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="crosswalk_ambiguous",
        )

    if intent.get("retry_of_run_id") and not str(intent.get("retry_posture") or "").strip():
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="retry_derived_postureless",
        )

    findings = list(evidence.get("latest_rejection_findings") or [])
    provider_execution_ok = evidence.get("provider_execution_ok")

    if _has_structural_findings(findings, provider_execution_ok=provider_execution_ok):
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="structural_context_or_template_finding",
        )

    if findings or evidence.get("latest_rejection") is not None:
        if _is_exclusively_transient_findings(
            findings,
            provider_execution_ok=provider_execution_ok,
        ):
            return _result(RETRY_POSTURE_TRANSIENT, reason="exclusive_transient_failure")
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="non_transient_or_mixed_rejection",
        )

    if _has_trusted_fresh_provenance(intent):
        return _result(RETRY_POSTURE_EXECUTABLE, reason="trusted_fresh_provenance")

    if intent_id and evidence.get("resolved") is not True:
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="crosswalk_unresolved",
        )

    explicit_posture = str(intent.get("retry_posture") or "").strip()
    if explicit_posture in RETRY_POSTURES:
        if explicit_posture == RETRY_POSTURE_TRANSIENT:
            if _is_exclusively_transient_findings(
                findings,
                provider_execution_ok=provider_execution_ok,
            ):
                return _result(
                    RETRY_POSTURE_TRANSIENT,
                    reason="exclusive_transient_failure",
                )
            return _result(
                RETRY_POSTURE_STRUCTURAL_QUARANTINE,
                reason="transient_annotation_without_exclusive_findings",
            )
        if explicit_posture == RETRY_POSTURE_EXECUTABLE:
            if _has_trusted_fresh_provenance(intent):
                return _result(
                    RETRY_POSTURE_EXECUTABLE,
                    reason="trusted_fresh_provenance",
                )
            return _result(
                RETRY_POSTURE_STRUCTURAL_QUARANTINE,
                reason="executable_annotation_without_trusted_provenance",
            )
        return _result(explicit_posture, reason="intent_retry_posture_annotation")

    if intent.get("retry_of_run_id"):
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="retry_derived_without_rejection_history",
        )

    if not intent_id:
        return _result(
            RETRY_POSTURE_STRUCTURAL_QUARANTINE,
            reason="missing_intent_id",
        )

    return _result(
        RETRY_POSTURE_STRUCTURAL_QUARANTINE,
        reason="postureless_without_trusted_provenance",
    )


def classify_pending_prompt_spawn_intents(
    shell_root: Path,
    *,
    orchestration_allowed: bool = False,
) -> dict[str, Any]:
    """Non-mutating posture report and histogram for queue intents."""

    queue = load_prompt_spawn_queue(shell_root)
    histogram = {
        RETRY_POSTURE_EXECUTABLE: 0,
        RETRY_POSTURE_TRANSIENT: 0,
        RETRY_POSTURE_SUPERSEDED: 0,
        RETRY_POSTURE_STRUCTURAL_QUARANTINE: 0,
        "blocked": 0,
    }
    rows: list[dict[str, Any]] = []
    evidence_snapshot = _build_intent_evidence_snapshot(shell_root)

    def evidence_resolver(
        resolved_root: Path,
        intent_id: str,
        intent: Mapping[str, Any],
    ) -> dict[str, Any]:
        return _resolve_intent_evidence(
            resolved_root,
            intent_id,
            intent,
            evidence_snapshot=evidence_snapshot,
        )

    for item in queue.get("pending") or []:
        if not isinstance(item, Mapping):
            continue
        intent = dict(item)
        role = _normalize_role(str(intent.get("role") or ""))
        if (
            not orchestration_allowed
            and role in NO_AUTO_CHAIN_ROLES
        ):
            histogram["blocked"] += 1
            rows.append(
                {
                    "intent_id": intent.get("intent_id"),
                    "posture": "blocked",
                    "reason": "orchestration_role_requires_explicit_packet",
                }
            )
            continue
        classification = classify_prompt_spawn_retry_posture(
            shell_root,
            intent,
            evidence_resolver=evidence_resolver,
        )
        posture = str(classification.get("posture") or "")
        if posture in histogram:
            histogram[posture] += 1
        rows.append(classification)
    total_pending = len(rows)
    blocked_count = histogram["blocked"]
    return {
        "schema_id": "ion.prompt_spawn_pending_posture_report.v1",
        "generated_at": _now(),
        "total_pending": total_pending,
        "histogram": histogram,
        "executable_count": histogram[RETRY_POSTURE_EXECUTABLE],
        "transient_count": histogram[RETRY_POSTURE_TRANSIENT],
        "superseded_count": histogram[RETRY_POSTURE_SUPERSEDED],
        "quarantine_count": histogram[RETRY_POSTURE_STRUCTURAL_QUARANTINE],
        "blocked_count": blocked_count,
        "intents": rows,
        "production_authority": False,
    }


def _requested_execution_model(
    carrier_id: str,
    carrier_resolution: Mapping[str, Any],
    explicit_model: str | None,
) -> str:
    if explicit_model is not None:
        return str(explicit_model).strip()
    default_model = {
        "claude_cli": DEFAULT_CLAUDE_MODEL,
        "codex_cli": DEFAULT_CODEX_MODEL,
        "cursor_cli": DEFAULT_CURSOR_MODEL,
    }.get(carrier_id, DEFAULT_CURSOR_MODEL)
    configured = str(
        carrier_resolution.get("model")
        or carrier_resolution.get("default_model")
        or default_model
    )
    # Environment defaults must never mutate an already-hashed route.  Callers
    # that need another approved model provide it explicitly so selection can
    # include it in the canonical decision.
    return configured.strip()


def _model_allowlist_refusal(carrier_id: str, requested_model: str) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "ok": False,
        "result": "BLOCKED",
        "finding": "operator_model_allowlist_refused",
        "carrier_id": carrier_id,
        "requested_model": requested_model,
        "approved_models": list(execution_models_for_carrier(carrier_id)),
        "artifact_writes": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _carrier_ready(
    shell_root: Path,
    carrier_id: str,
    *,
    cursor_binary: str,
    claude_binary: str,
    codex_binary: str,
    domain_id: str | None,
) -> tuple[bool, dict[str, Any]]:
    if carrier_id == "claude_cli":
        status = build_claude_cli_runner_status(shell_root, claude_binary=claude_binary)
        return status.get("verdict") == CLAUDE_READY_VERDICT, status
    if carrier_id == "codex_cli":
        status = build_codex_cli_runner_status(
            shell_root,
            codex_binary=codex_binary,
            domain_id=domain_id,
        )
        return status.get("verdict") == CODEX_READY_VERDICT, status
    status = build_prompt_spawn_executor_status(shell_root, cursor_binary=cursor_binary)
    blockers = carrier_scoped_readiness_blockers(
        list(status.get("blocked_by") or []),
        "cursor_cli",
    )
    return not blockers, status


def _apply_carrier_fallback(
    carrier_resolution: dict[str, Any],
    *,
    shell_root: Path,
    cursor_binary: str,
    claude_binary: str,
    codex_binary: str,
    domain_id: str | None,
    reason: str,
) -> tuple[dict[str, Any], str | None]:
    current = dict(carrier_resolution.get("unified_selection") or carrier_resolution)
    for _ in range(MAX_USAGE_LIMIT_FALLBACK_ATTEMPTS):
        nxt = resolve_next_fallback(current, usage_signal=reason)
        if nxt is None:
            break
        carrier_id = str(nxt.get("carrier_id") or "")
        if carrier_id not in {"cursor_cli", "claude_cli", "codex_cli"}:
            current = nxt
            continue
        ready, _status = _carrier_ready(
            shell_root,
            carrier_id,
            cursor_binary=cursor_binary,
            claude_binary=claude_binary,
            codex_binary=codex_binary,
            domain_id=domain_id,
        )
        if ready:
            merged = dict(carrier_resolution)
            merged.update(
                {
                    "carrier_id": carrier_id,
                    "default_model": nxt.get("model") or nxt.get("default_model"),
                    "model": nxt.get("model"),
                    "model_env": nxt.get("model_env"),
                    "binary": nxt.get("binary"),
                    "reasoning_effort": nxt.get("reasoning_effort"),
                    "model_tier": nxt.get("model_tier"),
                    "model_tier_label": nxt.get("model_tier_label"),
                    "source_model_tier": nxt.get("source_model_tier"),
                    "selection_reason": nxt.get("selection_reason"),
                    "fallback_decision_id": nxt.get("fallback_decision_id"),
                    "fallback_decision_sha256": nxt.get("fallback_decision_sha256"),
                    "parent_routing_decision_id": nxt.get("parent_routing_decision_id"),
                    "reason": nxt.get("selection_reason") or reason,
                    "unified_selection": nxt,
                }
            )
            return merged, None
        current = nxt
    return carrier_resolution, reason


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary_path.unlink(missing_ok=True)


def _write_prompt_spawn_run_json(
    run_dir: Path,
    run_packet: dict[str, Any],
    *,
    output_text: str | None = None,
) -> None:
    stamp_p21_workflow_honesty_on_run_packet(
        run_packet, output_text=str(output_text or "")
    )
    _write_json(run_dir / "run.json", run_packet)


def _resolve_root(root: str | Path | None) -> Path:
    return resolve_shell_root_from_ion_root(root)


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "prompt_spawn"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _context_snapshot_evidence(path: Path) -> dict[str, Any]:
    """Capture the complete first non-empty physical line without normalization.

    The receipt is machine-attested and later used as lifecycle-drift evidence.
    Stripping or truncating here would make the proof gate unable to distinguish
    the source bytes the carrier actually received from a normalized lookalike.
    Line terminators are structural and are not part of the physical-line value;
    all other whitespace and source-language quoting is preserved.
    """

    text = path.read_text(encoding="utf-8", errors="replace")
    excerpt_line: int | None = None
    excerpt = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            excerpt_line = line_number
            excerpt = line
            break
    return {
        "bytes": path.stat().st_size,
        "excerpt_line": excerpt_line,
        "excerpt": excerpt,
    }


def _prompt_spawn_template_id(intent: Mapping[str, Any]) -> str:
    return resolve_prompt_spawn_template_id(
        str(intent.get("work_class") or "") or None,
        intent_template_id=str(intent.get("template_id") or "").strip() or None,
    )


def _return_contract_lines(
    *,
    template_id: str,
    mutation_target_paths: list[str] | None = None,
) -> list[str]:
    mutation_paths = [
        path.strip()
        for path in (mutation_target_paths or [])
        if str(path).strip() and str(path).strip().lower() != "none"
    ]
    lines = [
        "## Return contract",
        "Your output MUST start with ### CONTEXT PROOF as the first line.",
        "Include one proof block per required file using path:, line:, excerpt:.",
        "The line value is the 1-based source line containing the excerpt; it is NEVER the file's total line count.",
        "Deterministically use the first non-empty physical line of each file: obtain it with a numbered-line read, copy the complete line as excerpt: including leading/trailing whitespace and source quotes, never truncate it, and copy its exact 1-based number as line:. Do not select a later excerpt.",
        "Do not retype sha256 digests in worker proof; sha256 verification is gate-owned against the context-load receipt.",
        "Required proof paths include this context_package.md AND every path listed under Required reads.",
    ]
    if mutation_paths:
        lines.extend(
            [
                "Self-evolution missions may mutate required-read surfaces listed under mutation_target_paths.",
                "For each mutation_target_paths entry, proof may be semantic-only receipt snapshot match (path, line, excerpt from read-time receipt) OR labeled proof whose sha256 equals the current post-mutation bytes while line/excerpt still match the read-time receipt anchor.",
                "mutation_target_paths:",
            ]
        )
        lines.extend(f"- {path}" for path in mutation_paths)
    lines.extend(
        [
            "",
            "### TEMPLATE ACTION PROOF must use plain scalar lines only (no markdown bold/bullets on keys):",
            f"template_id: {template_id}",
            "action_id: <your_action_id>",
            "result: <text>",
            "touched_paths:",
            "- <path>",
            "For read-only/no-write tasks, touched_paths must be exactly one item: none. Inspected files are not touched paths.",
            "List every repository path this carrier actually wrote under touched_paths; self-evolution missions must include each mutation_target_paths entry they modified.",
            "",
            "### RESULT on its own heading with a short summary.",
            f"Approved template_id for this spawn: {template_id}",
            "If no further agent is needed, end with ion-agent-decision no_followup fence.",
            "To call another agent, use ion-agent-comms directive fence with carrier_id cursor_cli.",
        ]
    )
    return lines


def _infer_mutation_target_paths(
    *,
    mission: str,
    required_reads: list[str],
    explicit_paths: list[str] | None = None,
) -> list[str]:
    if explicit_paths:
        return [
            path.strip()
            for path in explicit_paths
            if str(path).strip() and str(path).strip().lower() != "none"
        ]
    mission_lower = mission.lower()
    if "evolve" not in mission_lower and "evolution" not in mission_lower:
        return []
    targets: list[str] = []
    for path in required_reads:
        normalized = str(path).strip()
        if not normalized:
            continue
        basename = Path(normalized).name
        if basename.lower() in mission_lower or normalized.lower() in mission_lower:
            targets.append(normalized)
    return targets


def _apply_evolution_return_contract(
    package_text: str,
    *,
    template_id: str,
    mutation_target_paths: list[str],
) -> str:
    if not mutation_target_paths:
        return package_text
    contract_lines = _return_contract_lines(
        template_id=template_id,
        mutation_target_paths=mutation_target_paths,
    )
    contract_block = "\n".join(contract_lines)
    for marker in ("## Proof contract", "## Return contract"):
        if marker not in package_text:
            continue
        prefix, remainder = package_text.split(marker, 1)
        for tail_marker in ("## Non-claims", "## Model routing decision proof"):
            if tail_marker in remainder:
                suffix = tail_marker + remainder.split(tail_marker, 1)[1]
                return prefix.rstrip() + "\n\n" + contract_block + "\n\n" + suffix
        return prefix.rstrip() + "\n\n" + contract_block + "\n"
    return package_text + "\n\n" + contract_block + "\n"


def _inject_self_read_into_context_package(package_path: Path, package_rel: str) -> None:
    text = package_path.read_text(encoding="utf-8")
    if package_rel in text:
        return
    for marker in ("## Required reads (use file tools in order)", "## Required reads"):
        if marker in text:
            package_path.write_text(
                text.replace(marker, f"{marker}\n- {package_rel}", 1),
                encoding="utf-8",
            )
            return
    package_path.write_text(text + f"\n## Required reads\n- {package_rel}\n", encoding="utf-8")


def _normalize_role(role: str) -> str:
    text = str(role or "").strip().lower()
    return text.replace("role.", "").replace(" ", "_")


def _routing_proof_from_intent(intent: Mapping[str, Any]) -> dict[str, Any]:
    resolution = (
        intent.get("carrier_resolution")
        if isinstance(intent.get("carrier_resolution"), Mapping)
        else {}
    )
    carrier_id = str(
        resolution.get("carrier_id") or intent.get("execution_carrier") or ""
    ).strip()
    source_tier = str(resolution.get("source_model_tier") or "").strip()
    consequential = source_tier == "codex_sol_max"
    risk_level = str(intent.get("risk_level") or ("high" if consequential else "low"))
    context_need = str(intent.get("context_need") or "bounded_domain_context")
    experimental_model = bool(resolution.get("experimental_model"))
    budget_pool = {
        "codex_cli": "codex_sol_observed",
        "claude_cli": "claude_cli_operator_usage",
        "cursor_cli": (
            "cursor_cli_experimental_usage"
            if experimental_model
            else "cursor_cli_operator_usage"
        ),
    }.get(carrier_id, "unassigned_carrier_budget")
    escalation_triggers = [
        "carrier_unavailable",
        "authentication_required",
        "usage_limit",
        "return_gate_failure",
    ]
    if consequential:
        escalation_triggers.append("consequential_route_must_not_fallback_to_cursor")
    proof = {
        "schema_id": "ion.prompt_spawn_routing_decision_proof.v1",
        "routing_decision_id": resolution.get("routing_decision_id"),
        "routing_decision_sha256": resolution.get("routing_decision_sha256"),
        "routing_request_basis": resolution.get("routing_request_basis"),
        "routing_decision_basis": resolution.get("routing_decision_basis"),
        "routing_source_path": resolution.get("routing_source_path"),
        "routing_source_sha256": resolution.get("routing_source_sha256"),
        "routing_source_parity_ok": resolution.get("routing_source_parity_ok"),
        "domain_id": intent.get("domain_id"),
        "work_class": resolution.get("work_class") or intent.get("work_class"),
        "risk_level": risk_level,
        "risk_source": "intent" if intent.get("risk_level") else "model_tier_default",
        "context_need": context_need,
        "carrier_id": carrier_id,
        "selected_model": resolution.get("model") or resolution.get("default_model"),
        "experimental_model": experimental_model,
        "experimental_model_explicit_only": bool(
            resolution.get("experimental_model_explicit_only")
        ),
        "selected_reasoning_effort": resolution.get("reasoning_effort"),
        "model_tier": resolution.get("model_tier"),
        "source_model_tier": resolution.get("source_model_tier"),
        "selection_reason": resolution.get("selection_reason") or resolution.get("reason"),
        "effective_allowed_carriers": resolution.get("effective_allowed_carriers"),
        "reviewer": "role.steward_candidate_intake_required",
        "review_required_by": "role.steward_candidate_intake_required",
        "budget_pool": budget_pool,
        "escalation_triggers": escalation_triggers,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }
    proof_sha256 = hashlib.sha256(
        json.dumps(proof, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    proof["routing_packet_sha256"] = proof_sha256
    return proof


def _resolve_executor_directive_transport(
    *,
    directive: str | None,
    directive_file: str | Path | None,
    directive_stdin: bool,
    work_class: str | None,
    dry_run: bool,
    status_only: bool,
) -> dict[str, Any]:
    if directive_file and directive_stdin:
        return {
            "ok": False,
            "finding": "DirectiveTransportConflict",
            "message": "directive file and stdin are mutually exclusive",
        }
    if directive_file and directive is not None:
        return {
            "ok": False,
            "finding": "DirectiveTransportConflict",
            "message": "directive inline and file are mutually exclusive",
        }
    if directive_stdin and directive is not None:
        return {
            "ok": False,
            "finding": "DirectiveTransportConflict",
            "message": "directive inline and stdin are mutually exclusive",
        }
    try:
        if directive_file:
            transport = resolve_directive_transport(
                file_path=directive_file,
                allow_inline=False,
            )
        elif directive_stdin:
            transport = resolve_directive_transport(
                stdin=True,
                allow_inline=False,
            )
        elif directive is not None:
            transport = resolve_directive_transport(
                inline=directive,
                allow_inline=True,
            )
            assert_mutating_prompt_spawn_transport_allowed(
                transport,
                work_class=work_class,
                dry_run=dry_run,
                status_only=status_only,
            )
        else:
            return {"ok": True, "payload": None, "transport_mode": None, "receipt": None}
    except (
        DirectiveTransportConflict,
        DirectiveTransportMissingSource,
        DirectiveTransportInlineRejected,
    ) as exc:
        return {
            "ok": False,
            "finding": exc.__class__.__name__,
            "message": str(exc),
        }
    return {
        "ok": True,
        "payload": transport.payload,
        "transport_mode": transport.transport_mode,
        "receipt": transport.receipt,
    }


def _build_prompt_spawn_admission(
    *,
    intent: Mapping[str, Any],
    carrier_resolution: Mapping[str, Any],
    carrier_id: str,
    model: str,
    reasoning_effort: str | None,
    carrier_ready_status: Mapping[str, Any],
    mount: Mapping[str, Any] | None = None,
    directive_transport_receipt: Mapping[str, Any] | None = None,
    ion_root: Path | None = None,
) -> dict[str, Any]:
    work_class = str(
        carrier_resolution.get("work_class") or intent.get("work_class") or ""
    ).strip()
    blockers: list[str] = []
    required_route_fields = (
        "routing_decision_id",
        "routing_decision_sha256",
        "routing_source_sha256",
    )
    for field in required_route_fields:
        if not str(carrier_resolution.get(field) or "").strip():
            blockers.append(f"spawn_admission_{field}_required")
    if not str(intent.get("domain_id") or "").strip():
        blockers.append("spawn_admission_domain_id_required")
    if not work_class:
        blockers.append("spawn_admission_work_class_required")
    if carrier_resolution.get("policy_blocked"):
        blockers.append("spawn_admission_routing_policy_blocked")
    if carrier_resolution.get("routing_source_parity_ok") is not True:
        blockers.append("spawn_admission_routing_source_parity_required")
    if str(carrier_resolution.get("carrier_id") or "") != carrier_id:
        blockers.append("spawn_admission_carrier_binding_mismatch")
    if str(carrier_resolution.get("model") or "") != model:
        blockers.append("spawn_admission_model_binding_mismatch")
    if not is_operator_approved_model(carrier_id, model):
        blockers.append("spawn_admission_model_allowlist_refused")
    if not carrier_ready_status:
        blockers.append("spawn_admission_carrier_readiness_evidence_required")
    source_tier = str(carrier_resolution.get("source_model_tier") or "")
    if source_tier == "codex_sol_max" and carrier_id == "cursor_cli":
        blockers.append("spawn_admission_consequential_cursor_fallback_forbidden")
    if carrier_id == "codex_cli":
        if model != DEFAULT_CODEX_MODEL or reasoning_effort != DEFAULT_CODEX_REASONING_EFFORT:
            blockers.append("spawn_admission_codex_sol_max_required")
        if not isinstance(mount, Mapping) or not mount.get("ok"):
            blockers.append("spawn_admission_current_codex_mount_required")
        elif not mount.get("active_context_fresh"):
            blockers.append("spawn_admission_codex_mount_context_not_fresh")
        elif not isinstance(mount.get("mount_context_proof"), Mapping):
            blockers.append("spawn_admission_codex_mount_context_proof_required")
    routing_proof = _routing_proof_from_intent(intent)
    if str(routing_proof.get("selected_model") or "") != model:
        blockers.append("spawn_admission_routing_proof_model_mismatch")
    if str(routing_proof.get("carrier_id") or "") != carrier_id:
        blockers.append("spawn_admission_routing_proof_carrier_mismatch")
    objective = str(intent.get("objective") or "")
    routing_request_basis = (
        carrier_resolution.get("routing_request_basis")
        if isinstance(carrier_resolution.get("routing_request_basis"), Mapping)
        else routing_proof.get("routing_request_basis")
    )
    operator_routing_override_attested = bool(
        intent.get("operator_routing_override_attested")
    )
    handoff_source_ref = extract_handoff_source_ref(intent=intent, objective=objective)
    directive_provenance_class = derive_directive_provenance_class(
        source_kind=str(intent.get("source_kind") or ""),
        intent=intent,
        objective=objective,
        directive_transport_receipt=(
            dict(directive_transport_receipt)
            if isinstance(directive_transport_receipt, Mapping)
            else None
        ),
        routing_request_basis=(
            routing_request_basis if isinstance(routing_request_basis, Mapping) else None
        ),
        operator_routing_override_attested=operator_routing_override_attested,
    )
    if directive_transport_receipt is not None:
        blockers.extend(
            validate_directive_transport_binding(
                objective=objective,
                directive_transport_receipt=directive_transport_receipt,
                work_class=work_class,
            )
        )
    blockers.extend(
        validate_directive_provenance_on_admission(
            directive_provenance_class=directive_provenance_class,
            objective=objective,
            directive_transport_receipt=(
                dict(directive_transport_receipt)
                if isinstance(directive_transport_receipt, Mapping)
                else None
            ),
            routing_request_basis=(
                routing_request_basis if isinstance(routing_request_basis, Mapping) else None
            ),
            operator_routing_override_attested=operator_routing_override_attested,
            work_class=work_class,
            source_kind=str(intent.get("source_kind") or "") or None,
        )
    )
    resolved_economics_mode = str(
        intent.get("carrier_economics_mode") or intent.get("economics_mode") or ""
    ).strip().lower() or None
    economics_governed = spawn_requires_advisory_economics_binding(
        carrier_id=carrier_id,
        model=model,
        work_class=work_class,
        intent=intent,
        shell_root=ion_root,
        economics_mode=resolved_economics_mode,
    )
    if economics_governed:
        blockers.extend(
            validate_advisory_economics_admission_prerequisites(
                intent=intent,
                model=model,
                domain_id=str(intent.get("domain_id") or "").strip() or None,
                shell_root=ion_root,
                carrier_id=carrier_id,
                work_class=work_class,
                economics_mode=resolved_economics_mode,
            )
        )
    carrier_readiness = {
        "verdict": carrier_ready_status.get("verdict"),
        "finding": carrier_ready_status.get("finding"),
        "blocked_by": carrier_scoped_readiness_blockers(
            list(carrier_ready_status.get("blocked_by") or []),
            carrier_id,
        ),
    }
    template_fields = resolve_spawn_admission_template_fields(
        ion_root=ion_root,
        domain_id=str(intent.get("domain_id") or "").strip() or None,
        work_class=work_class,
        intent_template_id=str(intent.get("template_id") or "").strip() or None,
    )
    admission_basis = {
        "schema_id": "ion.prompt_spawn_admission.v1",
        **template_fields,
        "routing_decision_id": carrier_resolution.get("routing_decision_id"),
        "routing_decision_sha256": carrier_resolution.get("routing_decision_sha256"),
        "routing_source_sha256": carrier_resolution.get("routing_source_sha256"),
        "routing_packet_sha256": routing_proof.get("routing_packet_sha256"),
        "fallback_decision_id": carrier_resolution.get("fallback_decision_id"),
        "fallback_decision_sha256": carrier_resolution.get("fallback_decision_sha256"),
        "domain_id": intent.get("domain_id"),
        "work_class": work_class,
        "carrier_id": carrier_id,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "mount_id": (mount or {}).get("mount_id") if isinstance(mount, Mapping) else None,
        "mount_active_context_age_seconds": (
            (mount or {}).get("active_context_age_seconds")
            if isinstance(mount, Mapping)
            else None
        ),
        "mount_context_proof": (
            (mount or {}).get("mount_context_proof")
            if isinstance(mount, Mapping)
            else None
        ),
        "carrier_readiness": carrier_readiness,
        "blockers": blockers,
        "ok": not blockers,
        "carrier_invocation_admitted": not blockers,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
        **resolve_spawn_admission_authority_lexicon(work_class),
        "directive_transport_receipt": (
            dict(directive_transport_receipt)
            if directive_transport_receipt is not None
            else None
        ),
        "directive_provenance_class": directive_provenance_class,
        "handoff_source_ref": handoff_source_ref,
        "operator_routing_override_attested": operator_routing_override_attested,
        "advisory_economics_governed": economics_governed,
        "explicit_premium_model": bool(intent.get("explicit_premium_model")),
        **execution_tier_fields_for_admission(
            carrier_id,
            model,
            shell_root=ion_root,
            operation_mode=str(intent.get("operation_mode") or "").strip() or None,
            work_class=work_class or None,
        ),
        "advisory_economics_binding_sha256": None,
        "economics_database_path": (
            str(intent.get("economics_database_path") or "").strip() or None
            if economics_governed
            else None
        ),
    }
    admission_sha256 = recompute_admission_sha256(admission_basis)
    return {
        "admission_id": f"spawn_admission_{admission_sha256[:24]}",
        "admission_sha256": admission_sha256,
        **admission_basis,
        "authorization_basis": "current_operator_directive_for_bounded_ion_cli_carrier_work",
    }


def directive_to_prompt_spawn_intent(directive: Mapping[str, Any], *, index: int = 9001) -> dict[str, Any]:
    agent = _normalize_role(str(directive.get("agent") or "mason"))
    directive_id = str(directive.get("directive_id") or directive.get("id") or "")
    intent = {
        "schema_id": "ion.prompt_spawn_intent.v1",
        "intent_id": directive_id or f"directive_{agent}_{index}",
        "source_kind": "agent_comms_directive",
        "source_ref": directive_id,
        "role": agent,
        "index": index,
        "objective": str(directive.get("objective") or "").strip(),
        "domain_id": str(directive.get("domain_id") or "").strip() or None,
        "required_reads": [str(item) for item in (directive.get("source_refs") or []) if str(item).strip()],
        "orchestration_allowed": False,
        "followup_contract": True,
    }
    for key in (
        "work_class",
        "risk_level",
        "route_family",
        "requested_model",
        "requested_reasoning_effort",
    ):
        value = str(directive.get(key) or "").strip()
        if value:
            intent[key] = value
    return intent


def _intent_semantic_basis(intent: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "domain_id": str(intent.get("domain_id") or "").strip(),
        "index": int(intent.get("index") or 0),
        "objective": str(intent.get("objective") or "").strip(),
        "role": str(intent.get("role") or "").strip(),
        "source_kind": str(intent.get("source_kind") or "").strip(),
        "source_ref": str(intent.get("source_ref") or "").strip(),
    }


def intent_semantic_digest(intent: Mapping[str, Any]) -> str:
    """Canonical digest over stable invocation semantics (excludes retry/routing/runtime)."""

    return hashlib.sha256(
        json.dumps(_intent_semantic_basis(intent), sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _domain_intent_id(domain_id: str, semantic_digest: str) -> str:
    return f"domain_{_safe_slug(domain_id)}_{semantic_digest[:12]}"


def domain_to_prompt_spawn_intent(
    bundle: Mapping[str, Any],
    *,
    directive: str | None = None,
    index: int = 9100,
    work_class: str | None = None,
    source_kind: str | None = None,
    spawn_plan_row_ref: str | None = None,
    web_id: str | None = None,
    operator_approved: bool = False,
) -> dict[str, Any]:
    domain_id = str(bundle.get("domain_id") or "")
    objective = (
        directive
        or bundle.get("default_directive")
        or f"Run domain diagnostic for {domain_id}"
    )
    normalized_work_class = str(work_class or bundle.get("work_class") or "").strip()
    normalized_source_kind = str(source_kind or "explicit_domain").strip() or "explicit_domain"
    semantic_basis = {
        "source_kind": normalized_source_kind,
        "source_ref": domain_id,
        "role": "domain_worker",
        "index": index,
        "objective": objective,
        "domain_id": domain_id,
    }
    semantic_digest = intent_semantic_digest(semantic_basis)
    intent: dict[str, Any] = {
        "schema_id": "ion.prompt_spawn_intent.v1",
        "intent_id": _domain_intent_id(domain_id, semantic_digest),
        "intent_semantic_digest": semantic_digest,
        "source_kind": normalized_source_kind,
        "source_ref": domain_id,
        "role": "domain_worker",
        "index": index,
        "objective": objective,
        "domain_id": domain_id,
        "required_reads": list(bundle.get("required_reads") or []),
        "orchestration_allowed": False,
        "followup_contract": False,
        "bundle": dict(bundle),
    }
    if operator_approved or bool(bundle.get("operator_approved")):
        intent["operator_approved"] = True
    if spawn_plan_row_ref:
        intent["spawn_plan_row_ref"] = spawn_plan_row_ref
        intent["spawn_plan_row"] = True
    if web_id:
        intent["active_domain_web_id"] = web_id
    if normalized_work_class:
        intent["work_class"] = normalized_work_class
        intent["template_id"] = resolve_prompt_spawn_template_id(normalized_work_class)
    return intent


def load_prompt_spawn_queue(shell_root: Path) -> dict[str, Any]:
    return _read_json(shell_root / QUEUE_RELATIVE_PATH) or {"pending": []}


@contextmanager
def _prompt_spawn_queue_lock(shell_root: Path):
    """Serialize queue read-modify-write across threads and CLI processes."""

    lock_path = shell_root / QUEUE_LOCK_RELATIVE_PATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0) | getattr(
        os, "O_NOFOLLOW", 0
    )
    descriptor = os.open(lock_path, flags, 0o600)
    try:
        stat = os.fstat(descriptor)
        if stat.st_nlink != 1:
            raise ValueError("prompt-spawn queue lock must be a single-link file")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _stored_intent_semantic_digest(intent: Mapping[str, Any]) -> str:
    stored = str(intent.get("intent_semantic_digest") or "").strip()
    if stored:
        return stored
    return intent_semantic_digest(intent)


def enqueue_prompt_spawn_intent(
    shell_root: Path,
    intent: Mapping[str, Any],
    *,
    replace_existing: bool = False,
) -> str:
    with _prompt_spawn_queue_lock(shell_root):
        queue = load_prompt_spawn_queue(shell_root)
        pending = [item for item in queue.get("pending") or [] if isinstance(item, Mapping)]
        intent_id = str(intent.get("intent_id") or "")
        incoming = dict(intent)
        incoming_digest = intent_semantic_digest(incoming)
        incoming["intent_semantic_digest"] = incoming_digest
        matching_indexes = [
            index
            for index, item in enumerate(pending)
            if intent_id and str(item.get("intent_id") or "") == intent_id
        ]
        if matching_indexes:
            first = matching_indexes[0]
            existing = pending[first]
            existing_digest = _stored_intent_semantic_digest(existing)
            if existing_digest != incoming_digest:
                raise ValueError(
                    f"{INTENT_ID_SEMANTIC_MISMATCH}: intent_id={intent_id!r} "
                    f"existing_digest={existing_digest} incoming_digest={incoming_digest}"
                )
            if not replace_existing:
                return QUEUE_RELATIVE_PATH.as_posix()
            pending[first] = incoming
            pending = [
                item
                for index, item in enumerate(pending)
                if index == first
                or str(item.get("intent_id") or "") != intent_id
            ]
        else:
            fresh_intent = incoming
            if not str(fresh_intent.get("retry_of_run_id") or "").strip():
                if str(fresh_intent.get("intent_provenance") or "") != "fresh":
                    fresh_intent["intent_provenance"] = "fresh"
                if not str(fresh_intent.get("provenance_origin") or "").strip():
                    fresh_intent["provenance_origin"] = str(
                        fresh_intent.get("source_kind") or "fresh_enqueue"
                    )
                if not str(fresh_intent.get("retry_posture") or "").strip():
                    fresh_intent["retry_posture"] = RETRY_POSTURE_EXECUTABLE
            pending.append(fresh_intent)
        payload = {
            "schema_id": "ion.prompt_spawn_queue.v1",
            "updated_at": _now(),
            "pending": pending,
            "production_authority": False,
        }
        _write_json(shell_root / QUEUE_RELATIVE_PATH, payload)
    return QUEUE_RELATIVE_PATH.as_posix()


def build_prompt_spawn_retry_intent(
    intent: Mapping[str, Any],
    *,
    carrier_id: str,
    model: str,
    reasoning_effort: str | None,
    fallback_intent_id: str | None = None,
    retry_of_run_id: str | None = None,
    findings: list[str] | None = None,
    evidence_link: str | None = None,
    retry_posture: str | None = None,
) -> dict[str, Any]:
    """Return a retry intent bound to the exact failed execution lane."""

    retry_intent = {
        key: value
        for key, value in intent.items()
        if key
        not in {
            "carrier_resolution",
            "execution_carrier",
            "spawn_admission",
            "spawn_admission_path",
        }
    }
    if not str(retry_intent.get("intent_id") or "").strip() and fallback_intent_id:
        retry_intent["intent_id"] = str(fallback_intent_id)
    retry_intent["requested_carrier"] = str(carrier_id).strip()
    retry_intent["requested_model"] = str(model).strip()
    retry_intent["requested_reasoning_effort"] = (
        str(reasoning_effort or "").strip() or None
    )
    if retry_of_run_id:
        retry_intent["retry_of_run_id"] = str(retry_of_run_id).strip()
        prior_count = int(intent.get("retry_count") or 0)
        retry_intent["retry_count"] = prior_count + 1
    normalized_findings = [str(item) for item in (findings or []) if str(item).strip()]
    if normalized_findings:
        retry_intent["last_findings_digest"] = _stable_findings_digest(normalized_findings)
        retry_intent["last_rejection_findings"] = list(normalized_findings)
    if evidence_link:
        retry_intent["evidence_link"] = str(evidence_link).strip()
    if retry_posture:
        retry_intent["retry_posture"] = str(retry_posture).strip()
    return retry_intent


def handle_prompt_spawn_rejection_retry(
    shell_root: Path,
    intent: Mapping[str, Any],
    *,
    carrier_id: str,
    model: str,
    reasoning_effort: str | None,
    retry_of_run_id: str,
    findings: list[str] | None = None,
    evidence_link: str | None = None,
    fallback_intent_id: str | None = None,
) -> dict[str, Any]:
    """Upsert queue rows for all rejection postures; auto-retry only transient."""

    normalized_findings = [str(item) for item in (findings or []) if str(item).strip()]
    classification = classify_prompt_spawn_retry_posture(
        shell_root,
        intent,
        evidence_resolver=lambda root, intent_id, expected=None: {
            **_resolve_intent_evidence(root, intent_id, intent),
            "latest_rejection": {
                "findings": normalized_findings,
                "accepted": False,
            },
            "latest_rejection_findings": normalized_findings,
            "provider_execution_ok": False,
            "evidence_link": evidence_link,
            "resolved": True,
            "ambiguous": False,
        },
    )
    posture = str(classification.get("posture") or "")
    retry_intent = build_prompt_spawn_retry_intent(
        intent,
        carrier_id=carrier_id,
        model=model,
        reasoning_effort=reasoning_effort,
        fallback_intent_id=fallback_intent_id,
        retry_of_run_id=retry_of_run_id,
        findings=normalized_findings,
        evidence_link=evidence_link,
        retry_posture=posture,
    )
    auto_retry_eligible = posture == RETRY_POSTURE_TRANSIENT
    retry_queue_path = enqueue_prompt_spawn_intent(
        shell_root,
        retry_intent,
        replace_existing=True,
    )
    _, coaching_meta = append_proof_rejection_coaching_to_package_text(
        shell_root,
        retry_intent,
        "",
    )
    return {
        "retry_posture": posture,
        "classification": classification,
        "retry_intent": retry_intent,
        "enqueued": True,
        "auto_retry_eligible": auto_retry_eligible,
        "auto_retry_enqueued": auto_retry_eligible,
        "work_retained": True,
        "queue_row_retained": True,
        "retry_queue_path": retry_queue_path,
        **coaching_meta,
    }


def dequeue_prompt_spawn_intent(
    shell_root: Path,
    intent_id: str,
    *,
    run_id: str,
    executing_intent: Mapping[str, Any],
) -> bool:
    """Remove one queued intent only when run binding and semantic digest match."""

    normalized_intent_id = str(intent_id or "").strip()
    normalized_run_id = str(run_id or "").strip()
    if not normalized_intent_id:
        raise ValueError("dequeue_prompt_spawn_intent requires intent_id")
    if not normalized_run_id:
        raise ValueError("dequeue_prompt_spawn_intent requires run_id")
    if not isinstance(executing_intent, Mapping):
        raise ValueError("dequeue_prompt_spawn_intent requires executing_intent")
    executing_digest = intent_semantic_digest(dict(executing_intent))

    with _prompt_spawn_queue_lock(shell_root):
        queue = load_prompt_spawn_queue(shell_root)
        existing = [item for item in (queue.get("pending") or []) if isinstance(item, Mapping)]
        matching = [
            item
            for item in existing
            if str(item.get("intent_id") or "") == normalized_intent_id
        ]
        if not matching:
            return False
        queued_digest = _stored_intent_semantic_digest(matching[0])
        if queued_digest != executing_digest:
            raise ValueError(
                f"{INTENT_DEQUEUE_SEMANTIC_MISMATCH}: intent_id={normalized_intent_id!r} "
                f"run_id={normalized_run_id!r} queued_digest={queued_digest} "
                f"executing_digest={executing_digest}"
            )
        pending = [
            item
            for item in existing
            if str(item.get("intent_id") or "") != normalized_intent_id
        ]
        _write_json(
            shell_root / QUEUE_RELATIVE_PATH,
            {
                "schema_id": "ion.prompt_spawn_queue.v1",
                "updated_at": _now(),
                "pending": pending,
                "production_authority": False,
            },
        )
        return True


COLLISION_RECEIPT_SCHEMA_ID = "ion.prompt_spawn_intent_collision_receipt.v1_candidate"
COLLISION_RESTORE_PRESERVE_FIELDS = frozenset(
    {
        "schema_id",
        "intent_id",
        "domain_id",
        "index",
        "objective",
        "role",
        "source_kind",
        "source_ref",
        "required_reads",
        "orchestration_allowed",
        "followup_contract",
    }
)


def _resolve_run_json_path(path: Path) -> Path:
    if path.is_dir():
        return path / "run.json"
    if path.name == "run.json":
        return path
    if (path / "run.json").is_file():
        return path / "run.json"
    return path


def _relative_shell_path(shell_root: Path, path: Path) -> str:
    resolved = path.resolve()
    root = shell_root.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return resolved.as_posix()


def _load_prompt_spawn_run_artifact(path: Path) -> dict[str, Any]:
    run_path = _resolve_run_json_path(path)
    payload = _read_json(run_path)
    if not payload:
        raise ValueError(f"prompt_spawn run artifact missing: {run_path}")
    return payload


def _run_return_accepted(run: Mapping[str, Any]) -> bool:
    if run.get("return_intake_accepted") is True:
        return True
    intake = run.get("intake") if isinstance(run.get("intake"), Mapping) else {}
    if intake.get("accepted") is True:
        return True
    evaluation = intake.get("evaluation") if isinstance(intake.get("evaluation"), Mapping) else {}
    if evaluation.get("accepted") is True:
        return True
    return False


def _validate_collision_restore_runs(
    *,
    source_run: Mapping[str, Any],
    collision_run: Mapping[str, Any],
) -> dict[str, Any]:
    source_intent = _run_intent_from_artifact(source_run)
    collision_intent = _run_intent_from_artifact(collision_run)
    if not source_intent:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: source_run_missing_intent"
        )
    if not collision_intent:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: collision_run_missing_intent"
        )
    source_intent_id = str(source_intent.get("intent_id") or "").strip()
    collision_intent_id = str(collision_intent.get("intent_id") or "").strip()
    if not source_intent_id or source_intent_id != collision_intent_id:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: intent_id_mismatch "
            f"source={source_intent_id!r} collision={collision_intent_id!r}"
        )
    source_digest = _stored_intent_semantic_digest(source_intent)
    collision_digest = _stored_intent_semantic_digest(collision_intent)
    if source_digest == collision_digest:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: semantic_digest_not_distinct "
            f"digest={source_digest}"
        )
    if _run_return_accepted(source_run):
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: source_return_must_be_rejected"
        )
    if source_run.get("intent_dequeued") is not False:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: source_intent_must_not_be_dequeued"
        )
    if source_run.get("intent_retained_for_retry") is not True:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: source_intent_must_be_retained_for_retry"
        )
    if not _run_return_accepted(collision_run):
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: collision_return_must_be_accepted"
        )
    if collision_run.get("intent_dequeued") is not True:
        raise ValueError(
            f"{COLLISION_RESTORE_VALIDATION_FAILED}: collision_intent_must_be_dequeued"
        )
    return {
        "intent_id": source_intent_id,
        "source_intent_semantic_digest": source_digest,
        "collision_intent_semantic_digest": collision_digest,
        "source_intent": source_intent,
        "collision_intent": collision_intent,
    }


def _reconstruct_collision_restored_intent(
    *,
    source_run: Mapping[str, Any],
    source_run_path: Path,
    collision_run: Mapping[str, Any],
    collision_run_path: Path,
    restoration_key: str,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    source_intent = dict(validation["source_intent"])
    source_run_id = str(source_run.get("run_id") or source_run_path.parent.name).strip()
    collision_run_id = str(
        collision_run.get("run_id") or collision_run_path.parent.name
    ).strip()
    task_return_path = source_run_path.parent / "task_return.json"
    restored: dict[str, Any] = {
        key: source_intent[key]
        for key in COLLISION_RESTORE_PRESERVE_FIELDS
        if key in source_intent
    }
    restored["schema_id"] = str(
        restored.get("schema_id") or "ion.prompt_spawn_intent.v1"
    )
    restored["required_reads"] = list(restored.get("required_reads") or [])
    restored["retry_posture"] = RETRY_POSTURE_STRUCTURAL_QUARANTINE
    restored["retry_of_run_id"] = source_run_id
    restored["intent_provenance"] = "retry"
    restored["provenance_origin"] = COLLISION_RESTORE_PROVENANCE_ORIGIN
    restored["evidence_link"] = task_return_path.as_posix()
    restored["collision_restoration"] = {
        "restoration_key": restoration_key,
        "source_run_id": source_run_id,
        "source_run_path": source_run_path.as_posix(),
        "collision_run_id": collision_run_id,
        "collision_run_path": collision_run_path.as_posix(),
        "source_intent_semantic_digest": validation["source_intent_semantic_digest"],
        "collision_intent_semantic_digest": validation["collision_intent_semantic_digest"],
    }
    for field in COLLISION_RESTORE_STRIP_FIELDS:
        restored.pop(field, None)
    restored.pop("bundle", None)
    restored["intent_semantic_digest"] = intent_semantic_digest(restored)
    return restored


def _collision_receipt_path(shell_root: Path, restoration_key: str) -> Path:
    safe_key = re.sub(r"[^A-Za-z0-9._-]+", "_", str(restoration_key or "").strip())
    if not safe_key:
        raise ValueError(f"{COLLISION_RESTORE_VALIDATION_FAILED}: restoration_key_required")
    return (
        shell_root
        / COLLISION_RECEIPTS_RELATIVE_PATH
        / f"{safe_key}.candidate.json"
    )


def _build_collision_receipt(
    *,
    restoration_key: str,
    source_run_path: str,
    collision_run_path: str,
    validation: Mapping[str, Any],
    restored_intent: Mapping[str, Any],
) -> dict[str, Any]:
    collision_meta = restored_intent.get("collision_restoration")
    if not isinstance(collision_meta, Mapping):
        collision_meta = {}
    return {
        "schema_id": COLLISION_RECEIPT_SCHEMA_ID,
        "restoration_key": restoration_key,
        "intent_id": validation["intent_id"],
        "source_run_id": collision_meta.get("source_run_id"),
        "collision_run_id": collision_meta.get("collision_run_id"),
        "source_run_path": source_run_path,
        "collision_run_path": collision_run_path,
        "source_intent_semantic_digest": validation["source_intent_semantic_digest"],
        "collision_intent_semantic_digest": validation["collision_intent_semantic_digest"],
        "restored_intent_semantic_digest": restored_intent.get("intent_semantic_digest"),
        "restored_intent_id": restored_intent.get("intent_id"),
        "restored_retry_posture": restored_intent.get("retry_posture"),
        "restored_retry_of_run_id": restored_intent.get("retry_of_run_id"),
        "restored_evidence_link": restored_intent.get("evidence_link"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "candidate_only": True,
        "updated_at": _now(),
    }


def _receipt_matches_restoration(
    receipt: Mapping[str, Any],
    *,
    restoration_key: str,
    restored_intent: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> bool:
    expected = _build_collision_receipt(
        restoration_key=restoration_key,
        source_run_path=str(
            restored_intent.get("collision_restoration", {}).get("source_run_path")
            if isinstance(restored_intent.get("collision_restoration"), Mapping)
            else ""
        ),
        collision_run_path=str(
            restored_intent.get("collision_restoration", {}).get("collision_run_path")
            if isinstance(restored_intent.get("collision_restoration"), Mapping)
            else ""
        ),
        validation=validation,
        restored_intent=restored_intent,
    )
    comparable_fields = (
        "schema_id",
        "restoration_key",
        "intent_id",
        "source_intent_semantic_digest",
        "collision_intent_semantic_digest",
        "restored_intent_semantic_digest",
        "restored_intent_id",
        "restored_retry_posture",
        "restored_retry_of_run_id",
    )
    return all(receipt.get(field) == expected.get(field) for field in comparable_fields)


def restore_collided_prompt_spawn_intent(
    shell_root: Path,
    source_run_path: str | Path,
    collision_run_path: str | Path,
    restoration_key: str,
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Restore one collided legacy queue intent from explicit source/collision runs."""

    normalized_key = str(restoration_key or "").strip()
    if not normalized_key:
        raise ValueError(f"{COLLISION_RESTORE_VALIDATION_FAILED}: restoration_key_required")

    source_path = Path(source_run_path)
    collision_path = Path(collision_run_path)
    source_run = _load_prompt_spawn_run_artifact(source_path)
    collision_run = _load_prompt_spawn_run_artifact(collision_path)
    validation = _validate_collision_restore_runs(
        source_run=source_run,
        collision_run=collision_run,
    )
    source_rel = _relative_shell_path(shell_root, _resolve_run_json_path(source_path))
    collision_rel = _relative_shell_path(
        shell_root, _resolve_run_json_path(collision_path)
    )
    restored_intent = _reconstruct_collision_restored_intent(
        source_run=source_run,
        source_run_path=Path(source_rel),
        collision_run=collision_run,
        collision_run_path=Path(collision_rel),
        restoration_key=normalized_key,
        validation=validation,
    )
    restored_digest = str(restored_intent["intent_semantic_digest"])
    receipt_path = _collision_receipt_path(shell_root, normalized_key)
    receipt_rel = _relative_shell_path(shell_root, receipt_path)
    receipt_payload = _build_collision_receipt(
        restoration_key=normalized_key,
        source_run_path=source_rel,
        collision_run_path=collision_rel,
        validation=validation,
        restored_intent=restored_intent,
    )

    queue_path = shell_root / QUEUE_RELATIVE_PATH
    queue_before = queue_path.read_bytes() if queue_path.is_file() else None
    receipt_before = receipt_path.read_bytes() if receipt_path.is_file() else None

    result: dict[str, Any] = {
        "ok": True,
        "dry_run": dry_run,
        "finding": None,
        "restoration_key": normalized_key,
        "intent_id": validation["intent_id"],
        "source_run_path": source_rel,
        "collision_run_path": collision_rel,
        "source_intent_semantic_digest": validation["source_intent_semantic_digest"],
        "collision_intent_semantic_digest": validation["collision_intent_semantic_digest"],
        "restored_intent": restored_intent,
        "restored_intent_semantic_digest": restored_digest,
        "queue_action": "none",
        "queue_mutated": False,
        "receipt_path": receipt_rel,
        "receipt_written": False,
        "receipt_repaired": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "candidate_only": True,
    }

    with _prompt_spawn_queue_lock(shell_root):
        queue = load_prompt_spawn_queue(shell_root)
        pending = [item for item in queue.get("pending") or [] if isinstance(item, Mapping)]
        matching = [
            item
            for item in pending
            if str(item.get("intent_id") or "") == validation["intent_id"]
        ]
        if matching:
            existing_digest = _stored_intent_semantic_digest(matching[0])
            if existing_digest != restored_digest:
                raise ValueError(
                    f"{COLLISION_RESTORE_SEMANTIC_CONFLICT}: intent_id="
                    f"{validation['intent_id']!r} existing_digest={existing_digest} "
                    f"restored_digest={restored_digest}"
                )
            result["queue_action"] = "idempotent_replay"
        else:
            result["queue_action"] = "append"
            if not dry_run:
                pending.append(restored_intent)
                _write_json(
                    queue_path,
                    {
                        "schema_id": "ion.prompt_spawn_queue.v1",
                        "updated_at": _now(),
                        "pending": pending,
                        "production_authority": False,
                    },
                )
                result["queue_mutated"] = True

        existing_receipt = _read_json(receipt_path)
        receipt_ok = (
            isinstance(existing_receipt, Mapping)
            and _receipt_matches_restoration(
                existing_receipt,
                restoration_key=normalized_key,
                restored_intent=restored_intent,
                validation=validation,
            )
        )
        if receipt_ok:
            result["receipt_written"] = False
        elif result["queue_action"] == "idempotent_replay":
            result["receipt_repaired"] = True
            if not dry_run:
                _write_json(receipt_path, receipt_payload)
                result["receipt_written"] = True
        elif result["queue_action"] == "append" and not dry_run:
            _write_json(receipt_path, receipt_payload)
            result["receipt_written"] = True

    if dry_run:
        queue_after = queue_path.read_bytes() if queue_path.is_file() else None
        receipt_after = receipt_path.read_bytes() if receipt_path.is_file() else None
        if queue_before != queue_after or receipt_before != receipt_after:
            raise ValueError(
                f"{COLLISION_RESTORE_VALIDATION_FAILED}: dry_run_mutated_artifacts"
            )
    return result


def filter_blocked_roles(
    intents: list[dict[str, Any]],
    *,
    orchestration_allowed: bool = False,
) -> list[dict[str, Any]]:
    if orchestration_allowed:
        return intents
    filtered: list[dict[str, Any]] = []
    for intent in intents:
        role = _normalize_role(str(intent.get("role") or ""))
        if role in NO_AUTO_CHAIN_ROLES:
            intent = dict(intent)
            intent["blocked_auto_chain"] = True
            intent["block_reason"] = "orchestration_role_requires_explicit_packet"
            continue
        filtered.append(intent)
    return filtered


def collect_pending_prompt_spawn_intents(
    shell_root: Path,
    *,
    limit: int = 1,
    orchestration_allowed: bool = False,
) -> list[dict[str, Any]]:
    intents: list[dict[str, Any]] = []
    seen_intent_ids: set[str] = set()

    def _append_once(value: Mapping[str, Any]) -> None:
        normalized = dict(value)
        intent_id = str(normalized.get("intent_id") or "").strip()
        if intent_id and intent_id in seen_intent_ids:
            return
        if intent_id:
            seen_intent_ids.add(intent_id)
        intents.append(normalized)

    queue = load_prompt_spawn_queue(shell_root)
    for item in queue.get("pending") or []:
        if isinstance(item, Mapping):
            _append_once(item)
    ledger = _read_json(shell_root / DIRECTIVE_LEDGER_PATH) or {}
    processed = ledger.get("processed") or {}
    for directive_id, record in processed.items():
        if not isinstance(record, Mapping):
            continue
        pending_backend = str(record.get("execution_backend") or "")
        if pending_backend not in {"cursor_cli_pending", "claude_cli_pending"}:
            continue
        if record.get("prompt_spawn_completed"):
            continue
        directive = {
            "directive_id": directive_id,
            "agent": record.get("agent") or record.get("target_agent"),
            "objective": record.get("objective") or record.get("spawn_status"),
            "source_refs": record.get("source_refs") or [],
            "domain_id": record.get("domain_id"),
            "work_class": record.get("work_class"),
            "risk_level": record.get("risk_level"),
            "route_family": record.get("route_family"),
            "requested_model": record.get("requested_model"),
            "requested_reasoning_effort": record.get(
                "requested_reasoning_effort"
            ),
        }
        recovered_intent = directive_to_prompt_spawn_intent(
            directive, index=9000 + len(intents)
        )
        recovered_intent["requested_carrier"] = (
            "claude_cli" if pending_backend == "claude_cli_pending" else "cursor_cli"
        )
        recovered_intent["intent_provenance"] = "fresh"
        recovered_intent["provenance_origin"] = "agent_comms_directive_recovery"
        recovered_intent["retry_posture"] = RETRY_POSTURE_EXECUTABLE
        _append_once(recovered_intent)
    filtered = filter_blocked_roles(intents, orchestration_allowed=orchestration_allowed)
    collectible: list[dict[str, Any]] = []
    evidence_snapshot = _build_intent_evidence_snapshot(shell_root)

    def evidence_resolver(
        resolved_root: Path,
        intent_id: str,
        intent: Mapping[str, Any],
    ) -> dict[str, Any]:
        return _resolve_intent_evidence(
            resolved_root,
            intent_id,
            intent,
            evidence_snapshot=evidence_snapshot,
        )

    for intent in filtered:
        classification = classify_prompt_spawn_retry_posture(
            shell_root,
            intent,
            evidence_resolver=evidence_resolver,
        )
        if classification.get("posture") in COLLECTIBLE_RETRY_POSTURES:
            collectible.append(intent)
    return collectible[:limit]


def materialize_prompt_spawn_context_package(
    shell_root: Path,
    intent: Mapping[str, Any],
    run_root: Path,
) -> dict[str, Any]:
    from .ion_domain_cursor_runner import build_domain_context_package_markdown, resolve_domain_execution_bundle

    source_kind = str(intent.get("source_kind") or "")
    admission_read = str(intent.get("spawn_admission_path") or "").strip()

    def _proof_reads(values: Any) -> list[str]:
        reads = [str(item) for item in (values or []) if str(item).strip()]
        if admission_read and admission_read not in reads:
            reads.append(admission_read)
        return reads

    bundle: dict[str, Any] | None = None
    work_class = str(intent.get("work_class") or "").strip() or None
    intent_template_id = str(intent.get("template_id") or "").strip() or None
    if source_kind == "explicit_domain" and intent.get("bundle"):
        bundle = dict(intent["bundle"]) if isinstance(intent.get("bundle"), Mapping) else None
        if bundle is None:
            raise ValueError("explicit domain bundle must be a mapping")
        bundle["required_reads"] = _proof_reads(bundle.get("required_reads"))
        package_text = build_domain_context_package_markdown(
            shell_root,
            bundle,
            directive=str(intent.get("objective") or ""),
            carrier_id=str(intent.get("execution_carrier") or "cursor_cli"),
            work_class=work_class,
            intent_template_id=intent_template_id,
        )
    elif source_kind == "explicit_domain" and intent.get("domain_id"):
        bundle = resolve_domain_execution_bundle(shell_root, domain_id=str(intent["domain_id"]))
        if not bundle.get("ok"):
            raise ValueError(str(bundle.get("finding") or "domain_bundle_failed"))
        bundle["required_reads"] = _proof_reads(bundle.get("required_reads"))
        package_text = build_domain_context_package_markdown(
            shell_root,
            bundle,
            directive=str(intent.get("objective") or ""),
            carrier_id=str(intent.get("execution_carrier") or "cursor_cli"),
            work_class=work_class,
            intent_template_id=intent_template_id,
        )
    else:
        reads = _proof_reads(intent.get("required_reads"))
        objective = str(intent.get("objective") or "Execute bounded comms directive work.")
        template_id = _prompt_spawn_template_id(intent)
        read_only = resolve_prompt_spawn_read_only_posture(
            work_class,
            intent_template_id=intent_template_id,
            mission_text=objective,
            codex_sandbox_mode=str(intent.get("codex_sandbox_mode") or "") or None,
            workload_posture=str(intent.get("workload_posture") or "") or None,
        )
        lines = [
            "# ION Prompt Spawn Context Package",
            "",
            f"role: {intent.get('role')}",
            f"source_kind: {source_kind}",
            f"execution_carrier: {intent.get('execution_carrier') or 'cursor_cli'}",
            "posture: candidate-only",
            "",
            "## Mission",
            objective,
            "",
            "## Deliverable",
            (
                "Read-only audit: do not write a return artifact; return findings through stdout proof only."
                if read_only
                else "Candidate return through the carrier task-return contract."
            ),
            "",
            "## Required reads",
        ]
        lines.extend(f"- {item}" for item in reads)
        mutation_target_paths = _infer_mutation_target_paths(
            mission=objective,
            required_reads=reads,
            explicit_paths=[
                str(item)
                for item in (intent.get("mutation_target_paths") or [])
                if str(item).strip()
            ]
            or None,
        )
        lines.extend(
            [
                "",
                *_return_contract_lines(
                    template_id=template_id,
                    mutation_target_paths=mutation_target_paths or None,
                ),
            ]
        )
        package_text = "\n".join(lines) + "\n"

    template_id = resolve_prompt_spawn_template_id(
        work_class,
        intent_template_id=intent_template_id,
    )
    mission_text = str(intent.get("objective") or "")
    required_reads = _proof_reads(
        (bundle or {}).get("required_reads") if bundle else intent.get("required_reads")
    )
    mutation_target_paths = _infer_mutation_target_paths(
        mission=mission_text,
        required_reads=required_reads,
        explicit_paths=[
            str(item)
            for item in (intent.get("mutation_target_paths") or [])
            if str(item).strip()
        ]
        or None,
    )
    if mutation_target_paths:
        package_text = _apply_evolution_return_contract(
            package_text,
            template_id=template_id,
            mutation_target_paths=mutation_target_paths,
        )

    routing_proof = _routing_proof_from_intent(intent)
    spawn_admission = (
        dict(intent.get("spawn_admission"))
        if isinstance(intent.get("spawn_admission"), Mapping)
        else None
    )
    package_text += "\n".join(
        [
            "",
            "## Model routing decision proof",
            f"- decision_id: {routing_proof.get('routing_decision_id')}",
            f"- decision_sha256: {routing_proof.get('routing_decision_sha256')}",
            f"- routing_packet_sha256: {routing_proof.get('routing_packet_sha256')}",
            f"- routing_source_sha256: {routing_proof.get('routing_source_sha256')}",
            f"- domain_id: {routing_proof.get('domain_id')}",
            f"- work_class: {routing_proof.get('work_class')}",
            f"- risk_level: {routing_proof.get('risk_level')}",
            f"- context_need: {routing_proof.get('context_need')}",
            f"- carrier_id: {routing_proof.get('carrier_id')}",
            f"- selected_model: {routing_proof.get('selected_model')}",
            f"- selected_reasoning_effort: {routing_proof.get('selected_reasoning_effort')}",
            f"- selection_reason: {routing_proof.get('selection_reason')}",
            f"- reviewer: {routing_proof.get('reviewer')}",
            f"- review_required_by: {routing_proof.get('review_required_by')}",
            f"- budget_pool: {routing_proof.get('budget_pool')}",
            "- authority: candidate-only; no accepted-state or production authority",
            "",
        ]
    )
    if spawn_admission:
        package_text += "\n".join(
            [
                "## Spawn admission proof",
                f"- admission_id: {spawn_admission.get('admission_id')}",
                f"- admission_sha256: {spawn_admission.get('admission_sha256')}",
                f"- admission_path: {intent.get('spawn_admission_path')}",
                f"- carrier_invocation_admitted: {spawn_admission.get('carrier_invocation_admitted')}",
                f"- mount_id: {spawn_admission.get('mount_id')}",
                "- mount_context_proof_sha256: "
                f"{((spawn_admission.get('mount_context_proof') or {}).get('proof_sha256') if isinstance(spawn_admission.get('mount_context_proof'), Mapping) else None)}",
                "",
            ]
        )

    package_text, coaching_meta = append_proof_rejection_coaching_to_package_text(
        shell_root,
        intent,
        package_text,
    )

    package_path = run_root / "context_package.md"
    receipt_path = run_root / "context_load_receipt.json"
    package_path.write_text(package_text, encoding="utf-8")
    package_rel = _rel(shell_root, package_path)
    _inject_self_read_into_context_package(package_path, package_rel)
    scrubbed_text, scrub_meta = scrub_context_package_relay_prose(
        package_path.read_text(encoding="utf-8")
    )
    if scrub_meta.get("scrubbed"):
        package_path.write_text(scrubbed_text, encoding="utf-8")
    receipt_read_paths: list[str] = []
    if bundle and bundle.get("required_reads"):
        receipt_read_paths.extend(str(item) for item in bundle["required_reads"] if str(item).strip())
    else:
        receipt_read_paths.extend(str(item) for item in (intent.get("required_reads") or []) if str(item).strip())
    if admission_read and admission_read not in receipt_read_paths:
        receipt_read_paths.append(admission_read)
    required_reads = []
    for rel in receipt_read_paths:
        path = shell_root / rel
        row = {"path": rel, "kind": "file", "required": True, "status": "READY" if path.is_file() else "MISSING"}
        if path.is_file():
            row["sha256"] = _sha256_file(path)
            row.update(_context_snapshot_evidence(path))
        required_reads.append(row)
    package_row = {
        "path": package_rel,
        "kind": "file",
        "required": True,
        "status": "READY",
        "sha256": _sha256_file(package_path),
    }
    package_row.update(_context_snapshot_evidence(package_path))
    required_reads.insert(0, package_row)
    receipt = {
        "schema_id": "ion.cursor_task_context_load_receipt.v1",
        "created_at": _now(),
        "generated_by": "runner_or_control_plane",
        "worker_authored": False,
        "request_path": package_rel,
        "role": intent.get("role"),
        "index": intent.get("index"),
        "required_context_reads": required_reads,
        "routing_decision": routing_proof,
        "spawn_admission": spawn_admission,
        "directive_transport_receipt": intent.get("directive_transport_receipt"),
        "context_proof_return_gate": "kernel.ion_context_proof_gate",
        "production_authority": False,
    }
    receipt["machine_attestation_sha256"] = context_receipt_attestation_sha256(receipt)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spawn_row = {
        "role": intent.get("role"),
        "index": intent.get("index"),
        "context_package_path": package_rel,
        "context_load_receipt_path": _rel(shell_root, receipt_path),
        "orchestration_allowed": bool(intent.get("orchestration_allowed")),
        "source_kind": source_kind,
        "intent_id": intent.get("intent_id"),
        "execution_bundle_root": _rel(shell_root, run_root),
        "run_id": run_root.name,
        "carrier_id": routing_proof.get("carrier_id"),
        "work_class": routing_proof.get("work_class"),
        "risk_level": routing_proof.get("risk_level"),
        "context_need": routing_proof.get("context_need"),
        "selected_model": routing_proof.get("selected_model"),
        "experimental_model": routing_proof.get("experimental_model"),
        "experimental_model_explicit_only": routing_proof.get(
            "experimental_model_explicit_only"
        ),
        "selected_reasoning_effort": routing_proof.get("selected_reasoning_effort"),
        "selection_reason": routing_proof.get("selection_reason"),
        "routing_decision_id": routing_proof.get("routing_decision_id"),
        "routing_decision_sha256": routing_proof.get("routing_decision_sha256"),
        "routing_packet_sha256": routing_proof.get("routing_packet_sha256"),
        "routing_source_sha256": routing_proof.get("routing_source_sha256"),
        "reviewer": routing_proof.get("reviewer"),
        "review_required_by": routing_proof.get("review_required_by"),
        "budget_pool": routing_proof.get("budget_pool"),
        "escalation_triggers": routing_proof.get("escalation_triggers"),
        "routing_decision": routing_proof,
        "spawn_admission_id": (spawn_admission or {}).get("admission_id"),
        "spawn_admission_sha256": (spawn_admission or {}).get("admission_sha256"),
        "spawn_admission_path": intent.get("spawn_admission_path"),
        "spawn_admission": spawn_admission,
        "objective": str(intent.get("objective") or ""),
        "directive_transport_receipt": intent.get("directive_transport_receipt"),
        "directive_provenance_class": (spawn_admission or {}).get(
            "directive_provenance_class"
        ),
        "handoff_source_ref": (spawn_admission or {}).get("handoff_source_ref"),
        "operator_routing_override_attested": (spawn_admission or {}).get(
            "operator_routing_override_attested"
        ),
        "carrier_readiness": (spawn_admission or {}).get("carrier_readiness"),
        "advisory_economics_binding": intent.get("advisory_economics_binding"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }
    if coaching_meta.get("coaching_addendum_emitted"):
        spawn_row["proof_rejection_coaching"] = coaching_meta
    _write_json(run_root / "spawn_row.json", spawn_row)
    return {
        "context_package_path": package_rel,
        "context_load_receipt_path": _rel(shell_root, receipt_path),
        "spawn_row": spawn_row,
        "proof_rejection_coaching": coaching_meta,
    }


def _render_machine_context_proof_manifest(
    shell_root: Path, spawn_row: Mapping[str, Any]
) -> str:
    """Render runner-attested hashes so read-only carriers need no shell tool."""

    receipt_rel = str(spawn_row.get("context_load_receipt_path") or "").strip()
    receipt = _read_json(shell_root / receipt_rel) if receipt_rel else None
    rows = (
        receipt.get("required_context_reads")
        if isinstance(receipt, Mapping)
        and isinstance(receipt.get("required_context_reads"), list)
        else []
    )
    lines = [
        "## ION machine-attested context proof manifest",
        "Emit path:, line:, excerpt: proof blocks only; sha256 verification is gate-owned against the context-load receipt.",
        "Paths, lines, and excerpts below were captured by the admitted runner; copy excerpt text exactly, do not retype hashes.",
    ]
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        path = str(row.get("path") or "").strip()
        excerpt_line = row.get("excerpt_line")
        excerpt = str(row.get("excerpt") or "").strip()
        if not path:
            continue
        lines.append(f"path: {path}")
        if excerpt_line is not None:
            lines.append(f"line: {excerpt_line}")
        if excerpt:
            lines.append(f"excerpt: {excerpt}")
    return "\n".join(lines) + "\n"


def build_prompt_spawn_executor_status(
    root: str | Path | None = None,
    *,
    cursor_binary: str = DEFAULT_CURSOR_BINARY,
    claude_binary: str = DEFAULT_CLAUDE_BINARY,
    codex_binary: str = DEFAULT_CODEX_BINARY,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    cursor_status = {
        "binary_ok": _cursor_binary_ready(cursor_binary)[0],
        "auth": _cursor_auth_status(cursor_binary) if _cursor_binary_ready(cursor_binary)[0] else {"ok": False},
    }
    claude_status = build_claude_cli_runner_status(shell_root, claude_binary=claude_binary)
    codex_status = build_codex_cli_runner_status(shell_root, codex_binary=codex_binary)
    pending = collect_pending_prompt_spawn_intents(shell_root, limit=10)
    posture_report = classify_pending_prompt_spawn_intents(shell_root)
    blockers: list[str] = []
    if not cursor_status["binary_ok"]:
        blockers.append("cursor_binary_missing")
    elif not cursor_status["auth"].get("ok"):
        blockers.append("cursor_auth_unverified")
    if claude_status.get("verdict") != CLAUDE_READY_VERDICT:
        blockers.extend([f"claude:{item}" for item in claude_status.get("blocked_by") or []])
    if codex_status.get("verdict") != CODEX_READY_VERDICT:
        blockers.extend([f"codex:{item}" for item in codex_status.get("blocked_by") or []])
    stop = evaluate_carrier_spawn_stop(shell_root)
    if stop.get("blocked"):
        blockers.extend([f"spawn_stop:{reason}" for reason in stop.get("reasons") or []])
    carriers_ready = (
        cursor_status["binary_ok"] and cursor_status["auth"].get("ok")
    ) or claude_status.get("verdict") == CLAUDE_READY_VERDICT or codex_status.get("verdict") == CODEX_READY_VERDICT
    return {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT if carriers_ready and not stop.get("blocked") else BLOCKED_VERDICT,
        "generated_at": _now(),
        "pending_intent_count": len(pending),
        "pending_intents_sample": pending[:3],
        "posture_report": posture_report,
        "total_pending": posture_report.get("total_pending"),
        "executable_count": posture_report.get("executable_count"),
        "transient_count": posture_report.get("transient_count"),
        "blocked_count": posture_report.get("blocked_count"),
        "blocked_by": blockers,
        "cursor_cli": cursor_status,
        "claude_cli": claude_status,
        "codex_cli": codex_status,
        "carrier_routing": routing_status(shell_root),
        "queue_path": QUEUE_RELATIVE_PATH.as_posix(),
        "runs_dir": RUNS_DIR.as_posix(),
        "claude_runs_dir": CLAUDE_RUNS_DIR.as_posix(),
        "codex_runs_dir": CODEX_RUNS_DIR.as_posix(),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _execute_prompt_spawn_once_impl(
    root: str | Path | None = None,
    *,
    intent: Mapping[str, Any] | None = None,
    domain_id: str | None = None,
    directive: str | None = None,
    directive_file: str | Path | None = None,
    directive_stdin: bool = False,
    carrier: str = "auto",
    cursor_binary: str = DEFAULT_CURSOR_BINARY,
    claude_binary: str = DEFAULT_CLAUDE_BINARY,
    codex_binary: str = DEFAULT_CODEX_BINARY,
    model: str | None = None,
    reasoning_effort: str | None = None,
    work_class: str | None = None,
    mode: str | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    force: bool = True,
    dry_run: bool = False,
    record_return: bool = False,
    operator_message: str | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    stop = evaluate_carrier_spawn_stop(shell_root, operator_message=operator_message)
    if stop.get("blocked"):
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": "spawn_stop_active",
            "spawn_stop": stop,
        }

    preliminary_work_class = str(work_class or "").strip() or None
    directive_transport = _resolve_executor_directive_transport(
        directive=directive,
        directive_file=directive_file,
        directive_stdin=directive_stdin,
        work_class=preliminary_work_class,
        dry_run=dry_run,
        status_only=False,
    )
    if not directive_transport["ok"]:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": directive_transport.get("finding"),
            "message": directive_transport.get("message"),
            "artifact_writes": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    resolved_directive = directive_transport.get("payload")

    if intent is None and domain_id:
        from .ion_domain_cursor_runner import resolve_domain_execution_bundle

        bundle = resolve_domain_execution_bundle(shell_root, domain_id=domain_id)
        if not bundle.get("ok"):
            return {"schema_id": SCHEMA_ID, "ok": False, "result": "BLOCKED", **bundle}
        intent = domain_to_prompt_spawn_intent(bundle, directive=resolved_directive)
    elif intent is None:
        pending = collect_pending_prompt_spawn_intents(shell_root, limit=1)
        if not pending:
            return {
                "schema_id": SCHEMA_ID,
                "ok": True,
                "result": "NO_PENDING_INTENTS",
                "finding": "no_pending_prompt_spawn_intents",
            }
        intent = pending[0]

    intent = dict(intent)
    if resolved_directive is not None:
        intent["objective"] = resolved_directive
    if directive_transport.get("receipt") is not None:
        intent["directive_transport_receipt"] = directive_transport["receipt"]
    if work_class:
        intent["work_class"] = str(work_class)
    if carrier == "auto" and str(intent.get("requested_carrier") or "").strip():
        carrier = str(intent["requested_carrier"]).strip()
    if model is None and str(intent.get("requested_model") or "").strip():
        model = str(intent["requested_model"]).strip()
    if (
        reasoning_effort is None
        and str(intent.get("requested_reasoning_effort") or "").strip()
    ):
        reasoning_effort = str(intent["requested_reasoning_effort"]).strip()
    resolved_domain = str(intent.get("domain_id") or domain_id or "")
    carrier_resolution = resolve_carrier_for_domain(
        shell_root,
        domain_id=resolved_domain or None,
        carrier=carrier,
        requested_model=model,
        work_class=str(intent.get("work_class") or "") or None,
    )
    carrier_id = str(carrier_resolution.get("carrier_id") or "cursor_cli")
    if carrier_resolution.get("carrier_settings_pause"):
        return {
            "schema_id": SCHEMA_ID,
            "ok": True,
            "result": "PENDING",
            "finding": carrier_resolution.get("carrier_settings_finding")
            or "all_carriers_unavailable_by_operator_settings",
            "carrier_resolution": carrier_resolution,
            "artifact_writes": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    if carrier_resolution.get("policy_blocked"):
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": carrier_resolution.get("finding")
            or "carrier_not_allowed_for_model_tier",
            "carrier_resolution": carrier_resolution,
            "artifact_writes": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    intent["execution_carrier"] = carrier_id
    intent["carrier_resolution"] = carrier_resolution
    chosen_model = _requested_execution_model(carrier_id, carrier_resolution, model)
    if not is_operator_approved_model(carrier_id, chosen_model):
        return _model_allowlist_refusal(carrier_id, chosen_model)
    experimental_cursor_model = bool(
        carrier_id == "cursor_cli"
        and is_experimental_model("cursor_cli", chosen_model)
    )
    effective_cursor_mode = (
        "ask"
        if experimental_cursor_model
        else mode if mode is not None else DEFAULT_MODE
    )
    effective_cursor_force = False if experimental_cursor_model else force
    required_reasoning_effort = str(
        carrier_resolution.get("reasoning_effort") or ""
    ).strip()
    if (
        carrier_id == "codex_cli"
        and required_reasoning_effort
        and reasoning_effort
        and str(reasoning_effort).strip() != required_reasoning_effort
    ):
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": "model_tier_reasoning_effort_mismatch",
            "requested_reasoning_effort": str(reasoning_effort).strip(),
            "required_reasoning_effort": required_reasoning_effort,
            "carrier_resolution": carrier_resolution,
            "artifact_writes": False,
            "production_authority": False,
            "live_execution_authority": False,
        }

    carrier_ready_status: dict[str, Any] = {}
    if not dry_run:
        ready, status = _carrier_ready(
            shell_root,
            carrier_id,
            cursor_binary=cursor_binary,
            claude_binary=claude_binary,
            codex_binary=codex_binary,
            domain_id=resolved_domain or None,
        )
        if not ready:
            if model is not None:
                return {
                    **status,
                    "ok": False,
                    "result": "BLOCKED",
                    "finding": "explicit_model_carrier_not_ready",
                    "carrier_resolution": carrier_resolution,
                    "requested_model": chosen_model,
                }
            carrier_resolution, fallback_err = _apply_carrier_fallback(
                carrier_resolution,
                shell_root=shell_root,
                cursor_binary=cursor_binary,
                claude_binary=claude_binary,
                codex_binary=codex_binary,
                domain_id=resolved_domain or None,
                reason="carrier_not_ready",
            )
            carrier_id = str(carrier_resolution.get("carrier_id") or "cursor_cli")
            intent["execution_carrier"] = carrier_id
            intent["carrier_resolution"] = carrier_resolution
            chosen_model = _requested_execution_model(carrier_id, carrier_resolution, None)
            if not is_operator_approved_model(carrier_id, chosen_model):
                return _model_allowlist_refusal(carrier_id, chosen_model)
            ready, status = _carrier_ready(
                shell_root,
                carrier_id,
                cursor_binary=cursor_binary,
                claude_binary=claude_binary,
                codex_binary=codex_binary,
                domain_id=resolved_domain or None,
            )
            if not ready:
                return {
                    **status,
                    "ok": False,
                    "result": "BLOCKED",
                    "finding": f"{carrier_id}_not_ready_after_fallback",
                    "carrier_resolution": carrier_resolution,
                    "fallback_exhausted": fallback_err,
                }
        carrier_ready_status = dict(status)
        experimental_cursor_model = bool(
            carrier_id == "cursor_cli"
            and is_experimental_model("cursor_cli", chosen_model)
        )
        effective_cursor_mode = (
            "ask"
            if experimental_cursor_model
            else mode if mode is not None else DEFAULT_MODE
        )
        effective_cursor_force = False if experimental_cursor_model else force

    if dry_run:
        if carrier_id == "codex_cli":
            mount = resolve_codex_domain_mount(shell_root, domain_id=resolved_domain)
            if not mount.get("ok"):
                return {
                    **mount,
                    "schema_id": "ion.prompt_spawn_preview.v1",
                    "ok": False,
                    "result": "BLOCKED",
                    "artifact_writes": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                }
            chosen_effort = str(
                required_reasoning_effort
                or reasoning_effort
                or DEFAULT_CODEX_REASONING_EFFORT
            )
            command = build_codex_command(
                codex_binary=codex_binary,
                model=chosen_model,
                reasoning_effort=chosen_effort,
                mount_path=Path(str(mount["mount_abspath"])),
            )
        elif carrier_id == "claude_cli":
            command = build_claude_command(
                claude_binary=claude_binary,
                model=chosen_model,
            )
        else:
            command = _build_cursor_command(
                cursor_binary=cursor_binary,
                model=chosen_model,
                mode=effective_cursor_mode,
                force=effective_cursor_force,
            )
        return {
            "schema_id": "ion.prompt_spawn_preview.v1",
            "run_id": None,
            "generated_at": _now(),
            "carrier_id": carrier_id,
            "carrier_resolution": carrier_resolution,
            "intent": intent,
            "directive_transport_receipt": intent.get("directive_transport_receipt"),
            "command": command,
            "model": chosen_model,
            "reasoning_effort": chosen_effort if carrier_id == "codex_cli" else None,
            "experimental_model": experimental_cursor_model,
            "experimental_read_only_enforced": experimental_cursor_model,
            "dry_run": True,
            "result": "DRY_RUN",
            "ok": True,
            "artifact_writes": False,
            "production_authority": False,
            "live_execution_authority": False,
        }

    chosen_effort = (
        str(
            carrier_resolution.get("reasoning_effort")
            or reasoning_effort
            or DEFAULT_CODEX_REASONING_EFFORT
        )
        if carrier_id == "codex_cli"
        else None
    )
    current_mount = (
        dict(carrier_ready_status.get("domain_mount") or {})
        if carrier_id == "codex_cli"
        else None
    )
    if carrier_id == "codex_cli" and isinstance(current_mount, Mapping):
        mount_context_proof = current_mount.get("mount_context_proof")
        mount_reads = [
            str(item.get("path") or "").strip()
            for item in (
                mount_context_proof.get("files")
                if isinstance(mount_context_proof, Mapping)
                and isinstance(mount_context_proof.get("files"), list)
                else []
            )
            if isinstance(item, Mapping) and str(item.get("path") or "").strip()
        ]
        intent["required_reads"] = list(
            dict.fromkeys([*list(intent.get("required_reads") or []), *mount_reads])
        )
        if isinstance(intent.get("bundle"), Mapping):
            bundle = dict(intent["bundle"])
            bundle["required_reads"] = list(
                dict.fromkeys([*list(bundle.get("required_reads") or []), *mount_reads])
            )
            intent["bundle"] = bundle
    spawn_admission = _build_prompt_spawn_admission(
        intent=intent,
        carrier_resolution=carrier_resolution,
        carrier_id=carrier_id,
        model=chosen_model,
        reasoning_effort=chosen_effort,
        carrier_ready_status=carrier_ready_status,
        mount=current_mount,
        directive_transport_receipt=intent.get("directive_transport_receipt"),
        ion_root=shell_root,
    )
    try:
        maybe_record_prompt_spawn_cf12_findings(
            shell_root,
            intent=intent,
            spawn_admission=spawn_admission,
            write=True,
        )
    except Exception:
        pass
    if not spawn_admission.get("ok"):
        blockers = list(spawn_admission.get("blockers") or [])
        primary_finding = blockers[0] if blockers else "prompt_spawn_admission_blocked"
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": primary_finding,
            "blockers": spawn_admission.get("blockers"),
            "spawn_admission": spawn_admission,
            "carrier_resolution": carrier_resolution,
            "artifact_writes": False,
            "production_authority": False,
            "live_execution_authority": False,
        }

    slug = _safe_slug(str(intent.get("role")))
    stamp = _now().replace(":", "").replace("+00:00", "Z")
    if carrier_id == "codex_cli":
        run_prefix = f"codex_prompt_spawn_{stamp}_{slug}"
        runs_parent = shell_root / CODEX_RUNS_DIR
    elif carrier_id == "claude_cli":
        run_prefix = f"claude_prompt_spawn_{stamp}_{slug}"
        runs_parent = shell_root / CLAUDE_RUNS_DIR
    else:
        run_prefix = f"prompt_spawn_{stamp}_{slug}"
        runs_parent = shell_root / RUNS_DIR
    runs_parent.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix=f"{run_prefix}_", dir=runs_parent))
    run_id = run_dir.name
    advisory_economics_binding: dict[str, Any] | None = None
    if spawn_requires_advisory_economics_binding(
        carrier_id=carrier_id,
        model=chosen_model,
        work_class=str(intent.get("work_class") or "").strip() or None,
        intent=intent,
        shell_root=shell_root,
        economics_mode=str(intent.get("carrier_economics_mode") or "").strip().lower() or None,
    ):
        reserve_outcome = _attempt_executor_advisory_economics_reservation(
            shell_root=shell_root,
            intent=intent,
            model=chosen_model,
            run_id=run_id,
            domain_id=resolved_domain or None,
        )
        if not reserve_outcome.get("ok"):
            return {
                "schema_id": SCHEMA_ID,
                "ok": False,
                "result": "BLOCKED",
                "finding": "prompt_spawn_advisory_economics_reserve_blocked",
                "blockers": reserve_outcome.get("blockers"),
                "advisory_economics_reserve": reserve_outcome,
                "carrier_resolution": carrier_resolution,
                "artifact_writes": True,
                "provider_contacted": False,
                "production_authority": False,
                "live_execution_authority": False,
            }
        advisory_economics_binding = dict(reserve_outcome.get("binding") or {})
    try:
        if advisory_economics_binding is not None:
            spawn_admission = merge_advisory_economics_binding_into_admission(
                spawn_admission,
                advisory_economics_binding,
            )
            intent["advisory_economics_binding"] = advisory_economics_binding
        admission_path = run_dir / "spawn_admission.json"
        spawn_admission["admission_path"] = _rel(shell_root, admission_path)
        _write_json(admission_path, spawn_admission)
        intent["spawn_admission"] = spawn_admission
        intent["spawn_admission_path"] = _rel(shell_root, admission_path)
        materialized = materialize_prompt_spawn_context_package(
            shell_root, intent, run_dir
        )
        if advisory_economics_binding is not None:
            materialized_spawn_row = dict(materialized["spawn_row"])
            materialized_spawn_row["advisory_economics_binding"] = dict(
                advisory_economics_binding
            )
            materialized["spawn_row"] = materialized_spawn_row
        wrapper = (
            CODEX_PROMPT_WRAPPER
            if carrier_id == "codex_cli"
            else CLAUDE_PROMPT_WRAPPER
            if carrier_id == "claude_cli"
            else PROMPT_WRAPPER
        )
        prompt = (
            wrapper
            + "\n"
            + (run_dir / "context_package.md").read_text(encoding="utf-8")
            + "\n"
            + _render_machine_context_proof_manifest(
                shell_root, materialized["spawn_row"]
            )
        )
    except Exception as exc:
        reconcile = None
        if advisory_economics_binding is not None:
            reconcile = _reconcile_executor_advisory_economics_before_provider_start(
                binding=advisory_economics_binding,
                outcome="executor_pre_provider_materialization_failure",
                evidence_ref=f"evidence://prompt_spawn/{run_id}/materialization_failed",
                occurred_at=_now(),
                external_no_start_evidence=(
                    intent.get("no_provider_process_start_evidence")
                    if isinstance(
                        intent.get("no_provider_process_start_evidence"), Mapping
                    )
                    else None
                ),
            )
        return {
            "schema_id": SCHEMA_ID,
            "run_id": run_id,
            "carrier_id": carrier_id,
            "ok": False,
            "result": "BLOCKED",
            "finding": "prompt_spawn_pre_provider_materialization_failed",
            "blockers": [f"pre_provider_materialization_failed:{type(exc).__name__}"],
            "advisory_economics_reconcile": reconcile,
            "artifact_writes": True,
            "provider_contacted": False,
            "production_authority": False,
            "live_execution_authority": False,
        }

    if carrier_id == "codex_cli":
        run_packet = execute_codex_prompt_once(
            shell_root,
            prompt=prompt,
            run_dir=run_dir,
            run_id=run_id,
            domain_id=resolved_domain,
            codex_binary=codex_binary,
            model=chosen_model,
            reasoning_effort=str(chosen_effort),
            timeout_seconds=timeout_seconds,
            spawn_row=materialized["spawn_row"],
            intent=intent,
        )
        run_packet["carrier_resolution"] = carrier_resolution
        _write_json(
            shell_root / STATE_PATH,
            {"schema_id": "ion.prompt_spawn_executor_state.v1", "updated_at": _now(), "latest_run": run_packet},
        )
    elif carrier_id == "claude_cli":
        handoff_blockers: list[str] = []
        governed_claude_budget_usd: float | None = None
        if advisory_economics_binding is not None:
            handoff_blockers.extend(
                validate_advisory_economics_binding_handoff(
                    binding=advisory_economics_binding,
                    admission=spawn_admission,
                    spawn_row=materialized["spawn_row"],
                    model=chosen_model,
                    blocker_prefix="claude",
                )
            )
            governed_claude_budget_usd, budget_blockers = (
                _governed_advisory_max_budget_usd(
                    advisory_economics_binding
                )
            )
            handoff_blockers.extend(budget_blockers)
        if handoff_blockers:
            reconcile = _reconcile_executor_advisory_economics_before_provider_start(
                binding=advisory_economics_binding,
                outcome="executor_handoff_binding_mismatch",
                evidence_ref=f"evidence://prompt_spawn/{run_id}/handoff_blocked",
                occurred_at=_now(),
                external_no_start_evidence=(
                    intent.get("no_provider_process_start_evidence")
                    if isinstance(
                        intent.get("no_provider_process_start_evidence"), Mapping
                    )
                    else None
                ),
            )
            return {
                "schema_id": SCHEMA_ID,
                "run_id": run_id,
                "carrier_id": "claude_cli",
                "ok": False,
                "result": "BLOCKED",
                "finding": "claude_advisory_economics_binding_handoff_blocked",
                "blockers": handoff_blockers,
                "advisory_economics_reconcile": reconcile,
                "artifact_writes": True,
                "provider_contacted": False,
                "production_authority": False,
                "live_execution_authority": False,
            }
        claude_runner_kwargs: dict[str, Any] = {
            "root": shell_root,
            "prompt": prompt,
            "run_dir": run_dir,
            "run_id": run_id,
            "claude_binary": claude_binary,
            "model": chosen_model,
            "max_budget_usd": governed_claude_budget_usd,
            "timeout_seconds": timeout_seconds,
            "dry_run": False,
            "spawn_row": materialized["spawn_row"],
            "intent": intent,
        }
        try:
            run_packet = execute_claude_prompt_once(**claude_runner_kwargs)
        except Exception as exc:
            reconcile = _reconcile_executor_advisory_economics_before_provider_start(
                binding=advisory_economics_binding,
                outcome="claude_runner_provider_start_or_settlement_uncertain",
                evidence_ref=f"evidence://prompt_spawn/{run_id}/runner_exception",
                occurred_at=_now(),
                provider_start_uncertain=True,
            )
            return {
                "schema_id": SCHEMA_ID,
                "run_id": run_id,
                "carrier_id": "claude_cli",
                "ok": False,
                "result": "BLOCKED",
                "finding": "claude_provider_start_or_settlement_uncertain",
                "blockers": [f"claude_runner_exception:{type(exc).__name__}"],
                "advisory_economics_reconcile": reconcile,
                "artifact_writes": True,
                "provider_contacted": None,
                "production_authority": False,
                "live_execution_authority": False,
            }
        run_packet["carrier_resolution"] = carrier_resolution
        output_rel = run_packet.get("output_path")
        if not run_packet.get("ok") and output_rel:
            output_text = (shell_root / str(output_rel)).read_text(encoding="utf-8")
            if is_usage_limit_failure(output_text):
                quota_record = maybe_record_whole_cli_quota_exhaustion_after_classification(
                    shell_root,
                    carrier_id="claude_cli",
                    output_text=output_text,
                    evidence_run_id=run_id,
                    run_packet=run_packet,
                )
                run_packet["whole_cli_quota_exhaustion_record"] = quota_record
                nxt = resolve_next_fallback(
                    dict(carrier_resolution.get("unified_selection") or carrier_resolution),
                    output_text=output_text,
                )
                if nxt is not None:
                    run_packet["usage_limit_fallback_attempts"] = [
                        {
                            "attempt": 1,
                            "from_carrier": carrier_resolution.get("carrier_id"),
                            "from_model": chosen_model,
                            "to_carrier": nxt.get("carrier_id"),
                            "to_model": nxt.get("model"),
                            "usage_signal": nxt.get("usage_signal"),
                            "whole_cli_quota_exhaustion": nxt.get(
                                "whole_cli_quota_exhaustion"
                            ),
                            "exhausted_carriers": nxt.get("exhausted_carriers"),
                            "execution_deferred": True,
                        }
                    ]
                    if str(nxt.get("carrier_id") or "") != "claude_cli":
                        run_packet["cross_carrier_handoff"] = {
                            "required": True,
                            "carrier_id": nxt.get("carrier_id"),
                            "model": nxt.get("model"),
                            "reason": "fresh_carrier_context_package_required",
                            "fallback_decision_id": nxt.get("fallback_decision_id"),
                            "fallback_decision_sha256": nxt.get(
                                "fallback_decision_sha256"
                            ),
                        }
                    else:
                        run_packet["same_carrier_model_handoff"] = {
                            "required": True,
                            "carrier_id": "claude_cli",
                            "model": nxt.get("model"),
                            "reason": "fresh_routing_admission_context_required",
                            "fallback_decision_id": nxt.get("fallback_decision_id"),
                            "fallback_decision_sha256": nxt.get(
                                "fallback_decision_sha256"
                            ),
                        }
                    _write_prompt_spawn_run_json(
                        run_dir, run_packet, output_text=output_text
                    )
        _write_json(
            shell_root / STATE_PATH,
            {"schema_id": "ion.prompt_spawn_executor_state.v1", "updated_at": _now(), "latest_run": run_packet},
        )
    else:
        cursor_binding = validate_prompt_spawn_binding(
            materialized["spawn_row"],
            carrier_id="cursor_cli",
            model=chosen_model,
            reasoning_effort=None,
            blocker_prefix="cursor",
            ready_verdicts=(READY_VERDICT,),
            domain_id=resolved_domain,
        )
        cursor_route_authority = validate_prompt_spawn_route_authority(
            materialized["spawn_row"],
            source_root=shell_root,
            blocker_prefix="cursor",
        )
        if not cursor_binding.get("ok") or not cursor_route_authority.get("ok"):
            binding_blockers = [
                *list(cursor_binding.get("blockers") or []),
                *list(cursor_route_authority.get("blockers") or []),
            ]
            primary_finding = (
                str(binding_blockers[0])
                if binding_blockers
                else "cursor_spawn_route_authority_blocked"
            )
            return {
                "schema_id": SCHEMA_ID,
                "run_id": run_id,
                "carrier_id": "cursor_cli",
                "ok": False,
                "result": "BLOCKED",
                "finding": primary_finding,
                "blockers": binding_blockers,
                "spawn_binding": cursor_binding,
                "route_authority": cursor_route_authority,
                "artifact_writes": True,
                "provider_contacted": False,
                "production_authority": False,
                "live_execution_authority": False,
            }
        chosen_mode = effective_cursor_mode
        command = _build_cursor_command(
            cursor_binary=cursor_binary,
            model=chosen_model,
            mode=chosen_mode,
            force=effective_cursor_force,
        )
        run_packet = {
            "schema_id": "ion.prompt_spawn_run.v1",
            "run_id": run_id,
            "generated_at": _now(),
            "carrier_id": carrier_id,
            "carrier_resolution": carrier_resolution,
            "intent": intent,
            "spawn_row": materialized["spawn_row"],
            "directive_transport_receipt": intent.get("directive_transport_receipt"),
            "command": command,
            "model": chosen_model,
            "mode": chosen_mode,
            "force": effective_cursor_force,
            "experimental_model": experimental_cursor_model,
            "experimental_read_only_enforced": experimental_cursor_model,
            "dry_run": False,
            "production_authority": False,
        }
        fallback_attempts: list[dict[str, Any]] = []
        active_resolution = dict(carrier_resolution)
        active_resolution["model"] = chosen_model
        active_resolution["default_model"] = chosen_model
        completed = None
        output_text = ""
        provider_attempts: list[dict[str, Any]] = []
        provider_telemetry: dict[str, Any] = {}
        for attempt in range(MAX_USAGE_LIMIT_FALLBACK_ATTEMPTS):
            chosen_model = str(
                active_resolution.get("model")
                or active_resolution.get("default_model")
                or DEFAULT_CURSOR_MODEL
            ).strip()
            if not is_operator_approved_model("cursor_cli", chosen_model):
                run_packet.update(_model_allowlist_refusal("cursor_cli", chosen_model))
                _write_prompt_spawn_run_json(run_dir, run_packet, output_text=output_text)
                return run_packet
            command = _build_cursor_command(
                cursor_binary=cursor_binary,
                model=chosen_model,
                mode=chosen_mode,
                force=effective_cursor_force,
            )
            run_packet["command"] = command
            run_packet["carrier_resolution"] = active_resolution
            run_packet["model"] = chosen_model
            provider_started_at = _now()
            provider_started = time.monotonic()
            try:
                completed = subprocess.run(
                    [*command, prompt],
                    cwd=str(shell_root),
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                run_packet.update(
                    {
                        "ok": False,
                        "result": "FAILED",
                        "error": str(exc),
                        "provider_started_at": provider_started_at,
                        "provider_ended_at": _now(),
                        "provider_duration_seconds": round(
                            time.monotonic() - provider_started, 6
                        ),
                    }
                )
                _write_prompt_spawn_run_json(run_dir, run_packet, output_text=output_text)
                return run_packet
            provider_ended_at = _now()
            provider_duration_seconds = round(
                time.monotonic() - provider_started, 6
            )
            output_text, provider_telemetry = decode_cursor_cli_output(
                completed.stdout or ""
            )
            if completed.stderr and completed.returncode != 0:
                output_text += "\n" + completed.stderr
            provider_attempts.append(
                {
                    "attempt": attempt + 1,
                    "model": chosen_model,
                    "started_at": provider_started_at,
                    "ended_at": provider_ended_at,
                    "duration_seconds": provider_duration_seconds,
                    "returncode": completed.returncode,
                    "telemetry": provider_telemetry,
                }
            )
            if completed.returncode == 0 or not is_usage_limit_failure(output_text):
                break
            if is_usage_limit_failure(output_text):
                quota_record = maybe_record_whole_cli_quota_exhaustion_after_classification(
                    shell_root,
                    carrier_id="cursor_cli",
                    output_text=output_text,
                    evidence_run_id=run_id,
                    run_packet=run_packet,
                )
                run_packet["whole_cli_quota_exhaustion_record"] = quota_record
            nxt = resolve_next_fallback(
                dict(active_resolution.get("unified_selection") or active_resolution),
                output_text=output_text,
            )
            if nxt is None:
                break
            if str(nxt.get("carrier_id") or "") != "cursor_cli":
                run_packet["cross_carrier_handoff"] = {
                    "required": True,
                    "carrier_id": nxt.get("carrier_id"),
                    "model": nxt.get("model"),
                    "reason": "fresh_carrier_context_package_required",
                }
                break
            # A model change is a new execution decision.  Do not reuse the
            # already-materialized admission, spawn row, or context package for
            # a second provider call.  Leave the intent pending so a fresh
            # prompt-spawn invocation can bind and hash the fallback model.
            fallback_attempts.append(
                {
                    "attempt": attempt + 1,
                    "from_carrier": active_resolution.get("carrier_id"),
                    "from_model": chosen_model,
                    "to_carrier": nxt.get("carrier_id"),
                    "to_model": nxt.get("model"),
                    "usage_signal": nxt.get("usage_signal"),
                    "whole_cli_quota_exhaustion": nxt.get(
                        "whole_cli_quota_exhaustion"
                    ),
                    "exhausted_carriers": nxt.get("exhausted_carriers"),
                    "execution_deferred": True,
                }
            )
            active_resolution = dict(
                active_resolution.get("unified_selection") or active_resolution
            )
            active_resolution.update(nxt)
            active_resolution["unified_selection"] = nxt
            run_packet["same_carrier_model_handoff"] = {
                "required": True,
                "carrier_id": "cursor_cli",
                "model": nxt.get("model"),
                "reason": "fresh_routing_admission_context_required",
                "fallback_decision_id": nxt.get("fallback_decision_id"),
                "fallback_decision_sha256": nxt.get("fallback_decision_sha256"),
            }
            break
        if fallback_attempts:
            run_packet["usage_limit_fallback_attempts"] = fallback_attempts
            run_packet["carrier_resolution"] = active_resolution
        output_path = run_dir / "output.md"
        output_path.write_text(output_text, encoding="utf-8")
        run_packet.update(
            {
                "ok": completed.returncode == 0 if completed else False,
                "result": "COMPLETED" if completed and completed.returncode == 0 else "NONZERO_EXIT",
                "returncode": completed.returncode if completed else None,
                "output_path": _rel(shell_root, output_path),
                "output_bytes": len(output_text.encode("utf-8")),
                "output_sha256": hashlib.sha256(
                    output_text.encode("utf-8")
                ).hexdigest(),
                "provider_attempts": provider_attempts,
                "provider_duration_seconds": round(
                    sum(
                        float(item.get("duration_seconds") or 0.0)
                        for item in provider_attempts
                    ),
                    6,
                ),
                "provider_telemetry": provider_telemetry,
            }
        )
        _write_prompt_spawn_run_json(run_dir, run_packet, output_text=output_text)
        _write_json(
            shell_root / STATE_PATH,
            {"schema_id": "ion.prompt_spawn_executor_state.v1", "updated_at": _now(), "latest_run": run_packet},
        )

    provider_execution_ok = run_packet.get("ok") is True
    run_packet["provider_execution_ok"] = provider_execution_ok
    run_packet["return_intake_required"] = bool(record_return)
    run_packet["return_intake_accepted"] = None
    run_packet["workflow_complete"] = False
    intake_result = None
    if record_return and run_packet.get("ok") and run_packet.get("output_path"):
        from .ion_carrier_task_return import record_task_return
        from .ion_prompt_spawn_return_intake import (
            execute_template_contract_intake_on_prompt_spawn_return,
            get_prompt_spawn_return_intake_ledger_record,
            record_prompt_spawn_return_intake_ledger,
        )

        output_path = shell_root / str(run_packet["output_path"])
        with prompt_spawn_runtime_lock(
            shell_root,
            namespace="return_intake",
            identity=str(run_packet.get("run_id") or ""),
            blocking=True,
        ):
            existing_intake_record = get_prompt_spawn_return_intake_ledger_record(
                shell_root, str(run_packet.get("run_id") or "")
            )
            if existing_intake_record is not None:
                intake_result = _read_json(output_path.parent / "task_return.json")
                if not intake_result:
                    intake_result = {
                        "accepted": False,
                        "verdict": "ION_TASK_RETURN_REJECTED_RERUN_REQUIRED",
                        "evaluation": {
                            "findings": [
                                "intake_ledger_record_missing_task_return_artifact"
                            ]
                        },
                    }
                intake_ledger_result = {
                    "recorded": False,
                    "already_recorded": True,
                    "record": existing_intake_record,
                    "path": (
                        "ION/05_context/current/cursor_connector/runtime/"
                        "prompt_spawn_return_intake_ledger.json"
                    ),
                }
            else:
                intake_result = record_task_return(
                    shell_root,
                    role=str(intent.get("role")),
                    index=int(intent.get("index") or 0),
                    task_output_path=output_path,
                    spawn_row_override=materialized["spawn_row"],
                    enqueue_steward_integration=bool(intent.get("orchestration_allowed")),
                )
                intake_evaluation = (
                    intake_result.get("evaluation")
                    if isinstance(intake_result.get("evaluation"), Mapping)
                    else {}
                )
                intake_ledger_result = record_prompt_spawn_return_intake_ledger(
                    shell_root,
                    {
                        "run_id": run_packet.get("run_id"),
                        "intent_id": str(intent.get("intent_id") or ""),
                        "intent_semantic_digest": _stored_intent_semantic_digest(intent),
                        "carrier_id": carrier_id,
                        "domain_id": resolved_domain or None,
                        "output_path": run_packet.get("output_path"),
                        "accepted": intake_result.get("accepted") is True,
                        "verdict": intake_result.get("verdict"),
                        "findings": list(intake_evaluation.get("findings") or []),
                        "intake_mode": "inline_record_return",
                        "intake_at": _now(),
                    },
                )
                template_intake = execute_template_contract_intake_on_prompt_spawn_return(
                    shell_root,
                    template_id=str(spawn_admission.get("template_id") or ""),
                    worker_output_path=output_path,
                )
                run_packet["template_contract_intake"] = template_intake
        run_packet["intake"] = intake_result
        intake_accepted = intake_result.get("accepted") is True
        run_packet["return_intake_accepted"] = intake_accepted
        run_packet["return_intake_ledger"] = intake_ledger_result
        if intake_accepted:
            run_packet["workflow_complete"] = True
            run_packet["retry_required"] = False
            if str(intent.get("source_kind") or "") == "agent_comms_directive":
                from .ion_agent_comms_directives import (
                    mark_prompt_spawn_directive_completed,
                )

                run_packet["directive_completion"] = (
                    mark_prompt_spawn_directive_completed(
                        shell_root,
                        directive_id=str(
                            intent.get("source_ref") or intent.get("intent_id") or ""
                        ),
                        run_id=str(run_packet.get("run_id") or ""),
                        verdict=str(intake_result.get("verdict") or "") or None,
                    )
                )
        else:
            retry_result = handle_prompt_spawn_rejection_retry(
                shell_root,
                intent,
                carrier_id=carrier_id,
                model=chosen_model,
                reasoning_effort=(
                    str(run_packet.get("reasoning_effort") or reasoning_effort or "").strip()
                    or None
                ),
                retry_of_run_id=str(run_packet.get("run_id") or ""),
                findings=list(intake_evaluation.get("findings") or []),
                evidence_link=str(run_packet.get("output_path") or "") or None,
                fallback_intent_id=str(run_packet.get("run_id") or ""),
            )
            run_packet.update(
                {
                    "ok": False,
                    "result": "RETURN_REJECTED",
                    "workflow_complete": False,
                    "retry_required": True,
                    "work_retained": retry_result.get("work_retained") is True,
                    "retry_posture": retry_result.get("retry_posture"),
                    "intent_retained_for_retry": retry_result.get("work_retained") is True,
                    "queue_row_retained": retry_result.get("queue_row_retained") is True,
                    "auto_retry_eligible": retry_result.get("auto_retry_eligible") is True,
                    "auto_retry_enqueued": retry_result.get("auto_retry_enqueued") is True,
                    "retry_queue_path": retry_result.get("retry_queue_path"),
                }
            )
    elif provider_execution_ok:
        run_packet["return_intake_status"] = "PENDING"
        run_packet["intent_retained_for_intake"] = True

    intent_id = str(intent.get("intent_id") or "")
    intent_dequeued = False
    if intent_id and run_packet.get("return_intake_accepted") is True:
        intent_dequeued = dequeue_prompt_spawn_intent(
            shell_root,
            intent_id,
            run_id=str(run_packet.get("run_id") or ""),
            executing_intent=intent,
        )
    run_packet["intent_dequeued"] = intent_dequeued
    final_output_text = ""
    output_rel_final = str(run_packet.get("output_path") or "")
    if output_rel_final:
        final_output_path = shell_root / output_rel_final
        if final_output_path.is_file():
            final_output_text = final_output_path.read_text(encoding="utf-8", errors="replace")
    _write_prompt_spawn_run_json(
        run_dir, run_packet, output_text=final_output_text
    )
    _write_json(
        shell_root / STATE_PATH,
        {
            "schema_id": "ion.prompt_spawn_executor_state.v1",
            "updated_at": _now(),
            "latest_run": run_packet,
        },
    )

    return run_packet


def execute_prompt_spawn_once(
    root: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Execute once while excluding duplicate live execution of one intent."""

    shell_root = _resolve_root(root)
    dry_run = bool(kwargs.get("dry_run"))
    intent = kwargs.get("intent")
    domain_id = str(kwargs.get("domain_id") or "").strip()

    def _invoke_impl() -> dict[str, Any]:
        explicit_model = str(
            kwargs.get("model")
            or (
                intent.get("requested_model")
                if isinstance(intent, Mapping)
                else ""
            )
            or ""
        ).strip()
        if dry_run or not is_experimental_model("cursor_cli", explicit_model):
            return _execute_prompt_spawn_once_impl(root, **kwargs)
        with prompt_spawn_runtime_lock(
            shell_root,
            namespace="experimental_cursor_execution",
            identity="singleton",
            blocking=False,
        ) as claim:
            if not claim["acquired"]:
                return {
                    "schema_id": SCHEMA_ID,
                    "ok": False,
                    "result": "BLOCKED",
                    "finding": "experimental_cursor_concurrency_limit",
                    "requested_model": explicit_model,
                    "experimental_execution_claim": claim,
                    "artifact_writes": False,
                    "provider_contacted": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                }
            result = _execute_prompt_spawn_once_impl(root, **kwargs)
            result["experimental_execution_claim"] = {
                **claim,
                "released_after_call": True,
            }
            return result

    if intent is None and not domain_id and not dry_run:
        pending = collect_pending_prompt_spawn_intents(shell_root, limit=1)
        if not pending:
            return {
                "schema_id": SCHEMA_ID,
                "ok": True,
                "result": "NO_PENDING_INTENTS",
                "finding": "no_pending_prompt_spawn_intents",
            }
        intent = pending[0]
        kwargs["intent"] = intent

    intent_id = (
        str(intent.get("intent_id") or "").strip()
        if isinstance(intent, Mapping)
        else ""
    )
    if dry_run or not intent_id:
        return _invoke_impl()

    with prompt_spawn_runtime_lock(
        shell_root,
        namespace="intent_execution",
        identity=intent_id,
        blocking=False,
    ) as claim:
        if not claim["acquired"]:
            return {
                "schema_id": SCHEMA_ID,
                "ok": False,
                "result": "BLOCKED",
                "finding": "prompt_spawn_intent_execution_already_claimed",
                "intent_id": intent_id,
                "intent_execution_claim": claim,
                "artifact_writes": False,
                "provider_contacted": False,
                "production_authority": False,
                "live_execution_authority": False,
            }
        result = _invoke_impl()
        result["intent_execution_claim"] = {
            **claim,
            "released_after_call": True,
        }
        return result


def process_prompt_spawn_once(
    root: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return execute_prompt_spawn_once(root, **kwargs)


def _collision_restore_cli_mode_selected(args: argparse.Namespace) -> bool:
    return bool(args.restore_intent_collision)


def _process_once_cli_mode_selected(args: argparse.Namespace) -> bool:
    return bool(args.process_once or args.domain_id)


def _validate_collision_restore_cli_args(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> None:
    collision_args = (
        args.collision_source_run,
        args.collision_run,
        args.collision_restoration_key,
    )
    if _collision_restore_cli_mode_selected(args):
        missing = [
            flag
            for flag, value in (
                ("--collision-source-run", args.collision_source_run),
                ("--collision-run", args.collision_run),
                ("--collision-restoration-key", args.collision_restoration_key),
            )
            if not str(value or "").strip()
        ]
        if missing:
            parser.error(
                "restore-intent-collision requires "
                + ", ".join(missing)
            )
    elif any(str(value or "").strip() for value in collision_args):
        parser.error(
            "collision restore arguments require --restore-intent-collision"
        )
    if args.apply_intent_collision_restoration and not _collision_restore_cli_mode_selected(
        args
    ):
        parser.error(
            "apply-intent-collision-restoration requires --restore-intent-collision"
        )

    mode_count = sum(
        1
        for selected in (
            args.status,
            args.classify_pending_only,
            _process_once_cli_mode_selected(args),
            _collision_restore_cli_mode_selected(args),
        )
        if selected
    )
    if mode_count > 1:
        parser.error("mutually inconsistent process modes")


def _build_collision_restore_cli_result(
    shell_root: Path,
    *,
    source_run_path: str,
    collision_run_path: str,
    restoration_key: str,
    dry_run: bool,
) -> dict[str, Any]:
    result = restore_collided_prompt_spawn_intent(
        shell_root,
        source_run_path,
        collision_run_path,
        restoration_key,
        dry_run=dry_run,
    )
    receipt_rel = str(result.get("receipt_path") or "")
    receipt_path = shell_root / receipt_rel if receipt_rel else None
    receipt_sha256 = (
        _sha256_file(receipt_path)
        if receipt_path is not None and receipt_path.is_file()
        else None
    )
    queue_action = str(result.get("queue_action") or "none")
    queue_mutated = bool(result.get("queue_mutated"))
    already_restored = queue_action == "idempotent_replay"
    restored = queue_action == "append" and queue_mutated
    cli_result = dict(result)
    cli_result.update(
        {
            "result": "COLLISION_RESTORE_DRY_RUN" if dry_run else "COLLISION_RESTORE_APPLIED",
            "restored": restored,
            "already_restored": already_restored,
            "queue_path": QUEUE_RELATIVE_PATH.as_posix(),
            "receipt_sha256": receipt_sha256,
            "source_intent_semantic_digest": result.get("source_intent_semantic_digest"),
            "collision_intent_semantic_digest": result.get(
                "collision_intent_semantic_digest"
            ),
            "restored_intent_semantic_digest": result.get(
                "restored_intent_semantic_digest"
            ),
            "candidate_only": bool(result.get("candidate_only", True)),
            "production_authority": bool(result.get("production_authority", False)),
            "live_execution_authority": bool(
                result.get("live_execution_authority", False)
            ),
            "accepted_state_authority": bool(
                result.get("accepted_state_authority", False)
            ),
        }
    )
    return cli_result


def execute_collision_restore_cli(
    root: str | Path | None,
    *,
    collision_source_run: str,
    collision_run: str,
    collision_restoration_key: str,
    apply: bool = False,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    try:
        return _build_collision_restore_cli_result(
            shell_root,
            source_run_path=collision_source_run,
            collision_run_path=collision_run,
            restoration_key=collision_restoration_key,
            dry_run=not apply,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "result": "COLLISION_RESTORE_FAILED",
            "finding": str(exc),
            "dry_run": not apply,
            "restored": False,
            "already_restored": False,
            "queue_path": QUEUE_RELATIVE_PATH.as_posix(),
            "receipt_path": None,
            "receipt_sha256": None,
            "candidate_only": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Unified ION prompt-spawn executor.")
    parser.add_argument("--ion-root", default=None)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--classify-pending-only", action="store_true")
    parser.add_argument("--process-once", action="store_true")
    parser.add_argument(
        "--restore-intent-collision",
        action="store_true",
        help=(
            "Preview or apply collision intent restoration using explicit "
            "source/collision run artifacts."
        ),
    )
    parser.add_argument(
        "--collision-source-run",
        default=None,
        help="Path to the rejected retained source prompt-spawn run.json.",
    )
    parser.add_argument(
        "--collision-run",
        default=None,
        help="Path to the accepted dequeued collision prompt-spawn run.json.",
    )
    parser.add_argument(
        "--collision-restoration-key",
        default=None,
        help="Deterministic restoration key for queue/receipt idempotency.",
    )
    parser.add_argument(
        "--apply-intent-collision-restoration",
        action="store_true",
        help=(
            "Apply queue/receipt mutation for --restore-intent-collision; "
            "default is dry-run preview."
        ),
    )
    parser.add_argument("--domain-id", default=None)
    parser.add_argument("--directive", default=None)
    parser.add_argument("--directive-file", default=None)
    parser.add_argument("--directive-stdin", action="store_true")
    parser.add_argument(
        "--model",
        default=None,
        help="Exact operator-approved model for the selected carrier.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--record-return", action="store_true")
    parser.add_argument(
        "--reasoning-effort",
        default=None,
        help="Exact Codex CLI reasoning effort; consequential Sol tiers route to max.",
    )
    parser.add_argument(
        "--work-class",
        default=None,
        help="Explicit bounded work class used by importance-sensitive model tiers.",
    )
    parser.add_argument(
        "--carrier",
        default="auto",
        choices=("auto", "cursor_cli", "claude_cli", "codex_cli"),
        help="Execution carrier; auto follows the candidate domain/model tiers.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    _validate_collision_restore_cli_args(parser, args)

    if args.classify_pending_only:
        shell_root = _resolve_root(args.ion_root)
        result = classify_pending_prompt_spawn_intents(shell_root)
    elif _collision_restore_cli_mode_selected(args):
        result = execute_collision_restore_cli(
            args.ion_root,
            collision_source_run=str(args.collision_source_run),
            collision_run=str(args.collision_run),
            collision_restoration_key=str(args.collision_restoration_key),
            apply=args.apply_intent_collision_restoration,
        )
    elif args.status:
        result = build_prompt_spawn_executor_status(args.ion_root)
    elif _process_once_cli_mode_selected(args):
        result = execute_prompt_spawn_once(
            args.ion_root,
            domain_id=args.domain_id,
            directive=args.directive,
            directive_file=args.directive_file,
            directive_stdin=bool(args.directive_stdin),
            carrier=args.carrier,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            work_class=args.work_class,
            dry_run=args.dry_run,
            record_return=args.record_return,
        )
    else:
        result = build_prompt_spawn_executor_status(args.ion_root)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict") or result.get("result"))
    return 0 if result.get("ok", True) and result.get("verdict") != BLOCKED_VERDICT else 1


if __name__ == "__main__":
    raise SystemExit(main())
