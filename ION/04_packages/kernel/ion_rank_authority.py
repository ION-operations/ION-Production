"""Rank-bound settlement and sign-off helpers for ION.

Rank is settlement height in the context graph. It is not superiority, identity,
or live authority. This candidate helper validates rank-bound sign-off rules
without granting production, live execution, accepted-state, secret, deploy, or
push authority.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .ion_true_name_binding import parse_true_name


SCHEMA_ID = "ion.rank_authority.v0_1"
RANK_SIGNOFF_SCHEMA_ID = "ion.rank_authority.signoff.v0_1"
RANK_VALIDATION_SCHEMA_ID = "ion.rank_authority.validation.v0_1"
FAN_IN_SCHEMA_ID = "ion.rank_authority.parallel_fan_in.v0_1"

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "deploy_authority": False,
}

RANK_ORDER: tuple[str, ...] = (
    "R0_WITNESS",
    "R1_LOCAL_WORKER",
    "R2_DOMAIN_WORKER",
    "R3_BRANCH_INTEGRATOR",
    "R4_SETTLEMENT_STEWARD",
    "R5_ROOT_GOVERNOR",
    "R6_HUMAN_AUTHORITY",
)

RANK_VECTORS: dict[str, dict[str, Any]] = {
    "R0_WITNESS": {
        "context_level": "artifact_witness",
        "domain_scope": "single_artifact",
        "mutation_class": "none",
        "settlement_power": "observe_only",
        "proof_burden": "source_reference",
        "expiry": "observation_window",
    },
    "R1_LOCAL_WORKER": {
        "context_level": "local_patch",
        "domain_scope": "bounded_paths",
        "mutation_class": "candidate_patch",
        "settlement_power": "return_candidate",
        "proof_burden": "focused_validation",
        "expiry": "worker_shift",
    },
    "R2_DOMAIN_WORKER": {
        "context_level": "domain_packet",
        "domain_scope": "single_domain",
        "mutation_class": "domain_candidate",
        "settlement_power": "recommend_domain_state",
        "proof_burden": "domain_context_and_tests",
        "expiry": "true_name_or_packet",
    },
    "R3_BRANCH_INTEGRATOR": {
        "context_level": "branch_context",
        "domain_scope": "branch_or_wave",
        "mutation_class": "branch_reconciliation",
        "settlement_power": "recommend_branch_promotion_only",
        "proof_burden": "report_ledger_validation_and_scope_note",
        "expiry": "true_name_or_worker_shift",
    },
    "R4_SETTLEMENT_STEWARD": {
        "context_level": "settlement_context",
        "domain_scope": "cross_branch_candidate",
        "mutation_class": "candidate_settlement",
        "settlement_power": "settle_candidate_without_root_or_live_authority",
        "proof_burden": "candidate_evidence_validation_and_rank_gate",
        "expiry": "settlement_packet",
    },
    "R5_ROOT_GOVERNOR": {
        "context_level": "root_governance",
        "domain_scope": "root_profile_or_law",
        "mutation_class": "root_or_profile_change",
        "settlement_power": "prepare_root_governance_change_with_human_gate",
        "proof_burden": "explicit_human_approval_plus_root_evidence",
        "expiry": "human_gate_packet",
    },
    "R6_HUMAN_AUTHORITY": {
        "context_level": "operator_authority",
        "domain_scope": "explicit_operator_scope",
        "mutation_class": "operator_approval",
        "settlement_power": "explicit_human_decision",
        "proof_burden": "human_statement_or_approval_receipt",
        "expiry": "operator_scope",
    },
}

OUTPUT_CLASS_RULES: dict[str, dict[str, Any]] = {
    "witness_only": {
        "required_rank": "R0_WITNESS",
        "required_proof": ("evidence_refs",),
    },
    "local_candidate_patch": {
        "required_rank": "R1_LOCAL_WORKER",
        "required_proof": ("candidate_output_ref", "validation_refs"),
    },
    "domain_candidate": {
        "required_rank": "R2_DOMAIN_WORKER",
        "required_proof": ("candidate_output_ref", "evidence_refs", "validation_refs"),
    },
    "branch_reconciliation_candidate": {
        "required_rank": "R3_BRANCH_INTEGRATOR",
        "required_proof": ("candidate_output_ref", "evidence_refs", "validation_refs"),
    },
    "branch_reconciliation_promotion": {
        "required_rank": "R4_SETTLEMENT_STEWARD",
        "required_proof": ("candidate_output_ref", "evidence_refs", "validation_refs"),
        "promotion_requires": "R4_SETTLEMENT_STEWARD",
    },
    "root_profile_change": {
        "required_rank": "R5_ROOT_GOVERNOR",
        "required_proof": ("candidate_output_ref", "evidence_refs", "human_approval_ref"),
        "human_gate_required": True,
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rank_index(rank_id: str) -> int:
    if rank_id not in RANK_ORDER:
        raise ValueError(f"unknown rank:{rank_id}")
    return RANK_ORDER.index(rank_id)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if item]
    return [value] if value else []


def _proof_value_present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set)):
        return bool([item for item in value if item])
    return value is not None


def rank_vector(rank_id: str, *, expires_at: str | None = None) -> dict[str, Any]:
    """Return the JSON-serializable rank vector for a rank id."""

    base = dict(RANK_VECTORS[rank_id])
    base.update(
        {
            "schema_id": SCHEMA_ID,
            "rank_id": rank_id,
            "rank_order": _rank_index(rank_id),
            "expires_at": expires_at,
            "authority": dict(AUTHORITY_FALSE),
        }
    )
    return base


def rank_meets_or_exceeds(actual_rank: str, required_rank: str) -> bool:
    """Return true when actual rank is at or above required settlement height."""

    return _rank_index(actual_rank) >= _rank_index(required_rank)


def classify_true_name_rank(true_name: str, *, output_class: str | None = None) -> dict[str, Any]:
    """Classify a worker true name into an initial rank vector."""

    parsed = parse_true_name(true_name)
    movement = str(parsed["mission_movement"])
    if output_class == "root_profile_change" or "root_profile" in movement or "root_govern" in movement:
        rank_id = "R5_ROOT_GOVERNOR"
    elif "settlement" in movement or "steward" in movement:
        rank_id = "R4_SETTLEMENT_STEWARD"
    elif "wave_reconcile" in movement or true_name == "codex_c1_wave_reconcile":
        rank_id = "R3_BRANCH_INTEGRATOR"
    elif "rank_authority" in movement or "true_name" in movement:
        rank_id = "R2_DOMAIN_WORKER"
    else:
        rank_id = "R1_LOCAL_WORKER"
    vector = rank_vector(rank_id)
    vector["true_name"] = true_name
    vector["parsed_true_name"] = parsed
    vector["primary_domain"] = parsed["inferred_domain"]
    if true_name == "codex_c1_wave_reconcile":
        vector["primary_domain"] = "context.wave"
        vector["case_id"] = "C1_WAVE_001_002_RECONCILIATION"
    return vector


def required_signoff_rank(output_class: str) -> dict[str, Any]:
    """Return the rank rule for an output class."""

    if output_class not in OUTPUT_CLASS_RULES:
        raise ValueError(f"unknown output_class:{output_class}")
    rule = dict(OUTPUT_CLASS_RULES[output_class])
    rule["output_class"] = output_class
    rule["required_rank_vector"] = rank_vector(rule["required_rank"])
    return rule


def _missing_proof(output_class: str, proof: Mapping[str, Any]) -> list[str]:
    rule = required_signoff_rank(output_class)
    return [field for field in rule["required_proof"] if not _proof_value_present(proof.get(field))]


def validate_rank_lifecycle(
    rank: Mapping[str, Any],
    *,
    true_name_binding: Mapping[str, Any] | None = None,
    worker_shift: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate that rank is still active under true-name and worker-shift lifecycle."""

    reasons: list[dict[str, Any]] = []
    binding_status = str((true_name_binding or {}).get("binding_status") or "ACTIVE")
    if binding_status in {"EXPIRED", "SIGNED_OFF", "SETTLED", "SUPERSEDED", "RELEASED", "FAILED"}:
        reasons.append({"reason": "TRUE_NAME_BINDING_NOT_ACTIVE", "binding_status": binding_status})
    if worker_shift is not None:
        shift_status = str(worker_shift.get("status") or "")
        if shift_status not in {"ACTIVE", "SIGNED_ON", "HEARTBEAT"}:
            reasons.append({"reason": "WORKER_SHIFT_NOT_ACTIVE", "worker_shift_status": shift_status})
    if rank.get("expires_at") == "EXPIRED":
        reasons.append({"reason": "RANK_VECTOR_EXPIRED"})
    return {
        "schema_id": "ion.rank_authority.lifecycle_validation.v0_1",
        "rank_id": rank.get("rank_id"),
        "ok": not reasons,
        "rejections": reasons,
        "authority": dict(AUTHORITY_FALSE),
    }


def validate_ranked_signoff(
    *,
    candidate_true_name: str,
    candidate_rank: Mapping[str, Any],
    signer_true_name: str,
    signer_rank: Mapping[str, Any],
    output_class: str,
    proof: Mapping[str, Any] | None = None,
    requested_authority: Mapping[str, Any] | None = None,
    candidate_binding: Mapping[str, Any] | None = None,
    signer_shift: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate whether a signer rank can sign off a candidate output."""

    proof_payload = dict(proof or {})
    requested = dict(AUTHORITY_FALSE)
    if requested_authority:
        requested.update({key: bool(value) for key, value in requested_authority.items()})
    rule = required_signoff_rank(output_class)
    signer_rank_id = str(signer_rank.get("rank_id") or "")
    candidate_rank_id = str(candidate_rank.get("rank_id") or "")
    rejections: list[dict[str, Any]] = []
    if signer_true_name == candidate_true_name:
        rejections.append({"reason": "SAME_TRUE_NAME_CANNOT_SIGN_OFF_OWN_CANDIDATE"})
    if not rank_meets_or_exceeds(signer_rank_id, rule["required_rank"]):
        rejections.append(
            {
                "reason": "SIGNER_RANK_BELOW_REQUIRED",
                "signer_rank": signer_rank_id,
                "required_rank": rule["required_rank"],
            }
        )
    if output_class == "branch_reconciliation_promotion" and candidate_rank_id == "R3_BRANCH_INTEGRATOR":
        if not rank_meets_or_exceeds(signer_rank_id, "R4_SETTLEMENT_STEWARD"):
            rejections.append({"reason": "R3_BRANCH_RECONCILIATION_REQUIRES_R4_SETTLEMENT"})
    missing = _missing_proof(output_class, proof_payload)
    if missing:
        rejections.append({"reason": "MISSING_PROOF_BURDEN", "missing": missing})
    if _rank_index(signer_rank_id) <= _rank_index("R5_ROOT_GOVERNOR"):
        if requested.get("production_authority") or requested.get("live_execution_authority"):
            rejections.append({"reason": "RANK_CANNOT_GRANT_PRODUCTION_OR_LIVE_AUTHORITY", "signer_rank": signer_rank_id})
    if output_class == "root_profile_change" and not proof_payload.get("human_approval_ref"):
        rejections.append({"reason": "ROOT_PROFILE_CHANGE_REQUIRES_EXPLICIT_HUMAN_APPROVAL"})
    lifecycle = validate_rank_lifecycle(candidate_rank, true_name_binding=candidate_binding, worker_shift=signer_shift)
    if not lifecycle["ok"]:
        rejections.extend(lifecycle["rejections"])
    return {
        "schema_id": RANK_VALIDATION_SCHEMA_ID,
        "output_class": output_class,
        "candidate_true_name": candidate_true_name,
        "candidate_rank": candidate_rank_id,
        "signer_true_name": signer_true_name,
        "signer_rank": signer_rank_id,
        "required_rank": rule["required_rank"],
        "ok": not rejections,
        "decision": "ACCEPT" if not rejections else "REJECT",
        "rejections": rejections,
        "requested_authority": requested,
        "authority": dict(AUTHORITY_FALSE),
    }


def produce_rank_signoff(
    *,
    candidate_true_name: str,
    candidate_rank: Mapping[str, Any],
    signer_true_name: str,
    signer_rank: Mapping[str, Any],
    output_class: str,
    proof: Mapping[str, Any] | None = None,
    requested_authority: Mapping[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Produce a rank-signoff JSON structure with validation embedded."""

    timestamp = now or _now()
    validation = validate_ranked_signoff(
        candidate_true_name=candidate_true_name,
        candidate_rank=candidate_rank,
        signer_true_name=signer_true_name,
        signer_rank=signer_rank,
        output_class=output_class,
        proof=proof,
        requested_authority=requested_authority,
    )
    return {
        "schema_id": RANK_SIGNOFF_SCHEMA_ID,
        "created_at": timestamp,
        "candidate_true_name": candidate_true_name,
        "candidate_rank": candidate_rank.get("rank_id"),
        "signer_true_name": signer_true_name,
        "signer_rank": signer_rank.get("rank_id"),
        "output_class": output_class,
        "proof": dict(proof or {}),
        "validation": validation,
        "decision": validation["decision"],
        "authority": dict(AUTHORITY_FALSE),
    }


def validate_parallel_fan_in(
    child_candidates: Iterable[Mapping[str, Any]],
    *,
    signer_rank: Mapping[str, Any],
    output_class: str,
    proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate lower-rank worker returns fanning into a higher-rank sign-off."""

    required = required_signoff_rank(output_class)
    signer_rank_id = str(signer_rank.get("rank_id") or "")
    rejections: list[dict[str, Any]] = []
    children = [dict(child) for child in child_candidates]
    if not rank_meets_or_exceeds(signer_rank_id, required["required_rank"]):
        rejections.append({"reason": "SIGNER_RANK_BELOW_REQUIRED", "required_rank": required["required_rank"]})
    for child in children:
        child_rank = str(child.get("rank_id") or "")
        if _rank_index(child_rank) >= _rank_index(signer_rank_id):
            rejections.append(
                {
                    "reason": "CHILD_RANK_NOT_LOWER_THAN_SIGNER",
                    "child_true_name": child.get("true_name"),
                    "child_rank": child_rank,
                    "signer_rank": signer_rank_id,
                }
            )
    missing = _missing_proof(output_class, proof)
    if missing:
        rejections.append({"reason": "MISSING_PROOF_BURDEN", "missing": missing})
    return {
        "schema_id": FAN_IN_SCHEMA_ID,
        "output_class": output_class,
        "signer_rank": signer_rank_id,
        "child_count": len(children),
        "ok": not rejections,
        "decision": "ACCEPT" if not rejections else "REJECT",
        "children": children,
        "rejections": rejections,
        "authority": dict(AUTHORITY_FALSE),
    }


def c1_settlement_requirement() -> dict[str, Any]:
    """Return the C1 Wave 001/002 reconciliation settlement requirement."""

    c1 = classify_true_name_rank("codex_c1_wave_reconcile", output_class="branch_reconciliation_candidate")
    return {
        "schema_id": "ion.rank_authority.c1_settlement_requirement.v0_1",
        "candidate": c1,
        "output_class": "branch_reconciliation_promotion",
        "required_signoff_rank": required_signoff_rank("branch_reconciliation_promotion"),
        "can_self_accept": False,
        "promotion_requires": "R4_SETTLEMENT_STEWARD",
        "authority": dict(AUTHORITY_FALSE),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION rank authority helper")
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify")
    classify.add_argument("true_name")
    classify.add_argument("--output-class")

    require = sub.add_parser("required-rank")
    require.add_argument("output_class")

    sub.add_parser("c1-requirement")

    args = parser.parse_args(argv)
    if args.command == "classify":
        result = classify_true_name_rank(args.true_name, output_class=args.output_class)
    elif args.command == "required-rank":
        result = required_signoff_rank(args.output_class)
    else:
        result = c1_settlement_requirement()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
