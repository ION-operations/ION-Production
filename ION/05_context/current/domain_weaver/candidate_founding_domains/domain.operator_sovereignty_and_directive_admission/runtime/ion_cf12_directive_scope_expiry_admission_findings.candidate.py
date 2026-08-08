#!/usr/bin/env python3
"""CF-12 findings-only directive scope/expiry check at admission surfaces (candidate).

Never blocks admission. Reports and routes only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

DOMAIN_ID = "domain.operator_sovereignty_and_directive_admission"
FUNDAMENTAL_ID = "CF-12"
FINDING_SCHEMA_ID = "ion.cf12_directive_scope_expiry_finding.v0_1_candidate"
SUMMARY_SCHEMA_ID = "ion.cf12_directive_scope_expiry_summary.v0_1_candidate"
LEDGER_REL = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.operator_sovereignty_and_directive_admission/"
    "CF12_DIRECTIVE_SCOPE_EXPIRY_FINDINGS_LEDGER.candidate.jsonl"
)
SUMMARY_REL = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.operator_sovereignty_and_directive_admission/"
    "CF12_DIRECTIVE_SCOPE_EXPIRY_LAST_SUMMARY.candidate.json"
)
MAX_STALENESS_SECONDS = 48 * 3600

SCOPE_KEYS = ("directive_scope", "scope", "applies_to", "scope_paths")
EXPIRY_KEYS = (
    "expires_at",
    "expiry",
    "expiry_at",
    "expiry_satisfaction_condition",
    "satisfaction_condition",
    "retire_when",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    text = str(ts).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def assess_directive_payload(payload: Mapping[str, Any]) -> list[str]:
    """Return finding codes for missing scope and/or expiry-or-satisfaction (never blocks)."""

    missing: list[str] = []
    if not any(_non_empty(payload.get(key)) for key in SCOPE_KEYS):
        missing.append("cf12_directive_scope_missing")
    if not any(_non_empty(payload.get(key)) for key in EXPIRY_KEYS):
        missing.append("cf12_directive_expiry_or_satisfaction_missing")
    return missing


def directive_payload_from_mapping(
    payload: Mapping[str, Any],
    *,
    source_kind: str,
    source_ref: str | None = None,
) -> dict[str, Any]:
    merged: dict[str, Any] = dict(payload)
    merged["source_kind"] = source_kind
    if source_ref:
        merged["source_ref"] = source_ref
    if not merged.get("objective") and payload.get("objective") is not None:
        merged["objective"] = payload.get("objective")
    return merged


def _append_ledger(shell: Path, row: Mapping[str, Any], *, write: bool) -> None:
    if not write:
        return
    path = shell / LEDGER_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True) + "\n")


def _write_summary(shell: Path, summary: Mapping[str, Any], *, write: bool) -> None:
    if not write:
        return
    path = shell / SUMMARY_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evaluate_summary_absence(summary: Mapping[str, Any], *, now: datetime | None = None) -> bool:
    """True when the CF-12 check itself has not run recently (absence detector)."""

    now_dt = now or datetime.now(timezone.utc)
    last_at = _parse_iso(str(summary.get("last_check_at") or ""))
    if last_at is None:
        return True
    age = (now_dt - last_at).total_seconds()
    return age > MAX_STALENESS_SECONDS


def record_admission_assessment(
    shell: Path,
    *,
    source_kind: str,
    source_ref: str | None,
    directive_payload: Mapping[str, Any],
    admission_id: str | None = None,
    domain_id: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Emit finding rows and refresh periodic summary; never mutates admission blockers."""

    assessed = directive_payload_from_mapping(
        directive_payload, source_kind=source_kind, source_ref=source_ref
    )
    finding_codes = assess_directive_payload(assessed)
    checked_at = _now()
    ledger_rows: list[dict[str, Any]] = []
    for code in finding_codes:
        row = {
            "schema_id": FINDING_SCHEMA_ID,
            "fundamental_id": FUNDAMENTAL_ID,
            "domain_id": DOMAIN_ID,
            "checked_at": checked_at,
            "source_kind": source_kind,
            "source_ref": source_ref,
            "admission_id": admission_id,
            "target_domain_id": domain_id,
            "finding_code": code,
            "non_blocking": True,
            "never_global_blocker": True,
            "posture": "candidate_only",
        }
        ledger_rows.append(row)
        _append_ledger(shell, row, write=write)

    summary_path = shell / SUMMARY_REL
    prior: dict[str, Any] = {}
    if summary_path.is_file():
        try:
            loaded = json.loads(summary_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                prior = loaded
        except (OSError, json.JSONDecodeError):
            prior = {}

    total_findings = int(prior.get("cumulative_finding_rows") or 0) + len(ledger_rows)
    summary = {
        "schema_id": SUMMARY_SCHEMA_ID,
        "fundamental_id": FUNDAMENTAL_ID,
        "domain_id": DOMAIN_ID,
        "last_check_at": checked_at,
        "last_source_kind": source_kind,
        "last_source_ref": source_ref,
        "last_admission_id": admission_id,
        "last_finding_codes": finding_codes,
        "last_assessment_complete": not finding_codes,
        "checks_recorded_total": int(prior.get("checks_recorded_total") or 0) + 1,
        "cumulative_finding_rows": total_findings,
        "max_staleness_seconds": MAX_STALENESS_SECONDS,
        "absence_present": False,
        "detects_absence": True,
        "absence_meaning": (
            "CF-12 admission findings check has not refreshed "
            f"{SUMMARY_REL.as_posix()} within {MAX_STALENESS_SECONDS}s"
        ),
        "witness_module": (
            "candidate_founding_domains/domain.operator_sovereignty_and_directive_admission/"
            "runtime/ion_cf12_directive_scope_expiry_admission_findings.candidate.py"
        ),
        "ledger_path": LEDGER_REL.as_posix(),
        "non_blocking": True,
        "posture": "candidate_only",
    }
    summary["absence_present"] = evaluate_summary_absence(summary)
    _write_summary(shell, summary, write=write)
    return {
        "finding_codes": finding_codes,
        "ledger_rows_appended": len(ledger_rows),
        "summary_path": SUMMARY_REL.as_posix(),
        "summary": summary,
    }


def record_prompt_spawn_intent_findings(
    shell: Path,
    *,
    intent: Mapping[str, Any],
    spawn_admission: Mapping[str, Any] | None = None,
    write: bool = True,
) -> dict[str, Any]:
    payload = dict(intent)
    for key in SCOPE_KEYS + EXPIRY_KEYS:
        if key in intent:
            payload[key] = intent.get(key)
    return record_admission_assessment(
        shell,
        source_kind="prompt_spawn_intent",
        source_ref=str(intent.get("intent_id") or intent.get("source_ref") or "").strip() or None,
        directive_payload=payload,
        admission_id=(
            str(spawn_admission.get("admission_id") or "").strip() or None
            if isinstance(spawn_admission, Mapping)
            else None
        ),
        domain_id=str(intent.get("domain_id") or "").strip() or None,
        write=write,
    )


def record_durable_queue_row_findings(
    shell: Path,
    *,
    row: Mapping[str, Any],
    write: bool = True,
) -> dict[str, Any]:
    payload = dict(row)
    payload["objective"] = row.get("objective")
    return record_admission_assessment(
        shell,
        source_kind="durable_queue_row",
        source_ref=str(row.get("row_id") or row.get("intent_id") or row.get("index") or "").strip()
        or None,
        directive_payload=payload,
        admission_id=None,
        domain_id=str(row.get("domain_id") or row.get("domain_true_name") or "").strip() or None,
        write=write,
    )
