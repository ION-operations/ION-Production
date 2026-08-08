"""Report-only ION runtime absence surface (never blocks global ION work)."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.runtime_carrier.absence_surface.v0_1_candidate"
SURFACE_REL = Path(
    "ION/05_context/current/runtime_carrier/ION_RUNTIME_ABSENCE_SURFACE.candidate.json"
)
RECEIPTS_DIR_REL = Path("ION/05_context/current/runtime_carrier/receipts")
ACTIVATION_HORIZON_DAYS = 7
DOMAIN_FORMATION_STALL_DAYS = 7
SURFACE_STALE_SECONDS = 7200
OWNER_DOMAIN = "domain.runtime_carrier_and_action_admission"
NEED_BASED_EXPANSION_RECEIPT_GLOB = (
    "ION/05_context/current/domain_weaver/need_based_expansion/"
    "context_materialization_receipts/*.candidate.json"
)
NEED_BASED_EXPANSION_KERNEL_ENTRYPOINTS: list[dict[str, str]] = [
    {
        "route_id": "need_based_expansion_plan",
        "service_handler": "domain_weaver_need_based_expansion_plan",
        "plan_builder": "kernel.ion_domain_weaver_need_based_expansion.build_need_based_domain_agent_expansion_plan",
    },
    {
        "route_id": "need_based_expansion_spawn_request_seed",
        "service_handler": "domain_weaver_need_based_expansion_spawn_request_seed",
        "plan_builder": "kernel.ion_domain_weaver_need_based_expansion.seed_need_based_expansion_spawn_requests",
    },
    {
        "route_id": "need_based_expansion_context_materialize",
        "service_handler": "domain_weaver_need_based_expansion_context_materialize",
        "plan_builder": "kernel.ion_domain_weaver_need_based_expansion.materialize_need_based_expansion_worker_contexts",
    },
]

ROUTE_TO = [
    "ION/05_context/current/operator_seats/AETHER_OPERATOR/RESUME_MANIFEST.candidate.yaml",
    "ION/05_context/current/domain_weaver/dogfood_context_capsule/"
    "DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE.md",
]

OPERATOR_SEAT_CAPSULE = (
    "ION/05_context/current/codex_agent_mounts/"
    "role_lead_steward_operator__domain_externalized_cognition_continuity/"
    ".ion/ION_CONTEXT_CAPSULE.yaml"
)
PROPOSED_CONTEXT_REF = "ion.runtime_carrier.absence_surface"

ARTIFACT_SERIES: list[dict[str, Any]] = [
    {
        "series_id": "generated_mount_freshness_preview",
        "glob": "ION/05_context/current/generated_mount_freshness_remediation/"
        "GENERATED_MOUNT_FRESHNESS_PREVIEW_*.json",
        "expected_interval_seconds": 604800,
        "interpretation": "freshness batch automation stopped mid-July 2026",
        "owner_domain": "domain.context_mount_freshness_and_resolver",
    },
    {
        "series_id": "scheduler_last_tick",
        "glob": "ION/05_context/current/autonomous_goals/scheduler/last_tick.candidate.json",
        "expected_interval_seconds": 7200,
        "interpretation": "scheduler tick not advancing when health lane runs",
        "single_file": True,
    },
    {
        "series_id": "daemon_loop_receipts",
        "glob": "ION/05_context/history/daemon_loop_receipts/*.json",
        "expected_interval_seconds": 86400,
        "interpretation": "daemon loop never produced receipts in this workspace",
        "empty_is_stale": True,
        "owner_domain": "domain.production_daemon_and_graph_event_runtime",
    },
    {
        "series_id": "terminal_worker_maintainer_last_tick",
        "glob": "ION/05_context/current/domain_weaver/terminal_workers/"
        "*/MAINTAINER_LAST_TICK.candidate.json",
        "expected_interval_seconds": 604800,
        "interpretation": "terminal worker maintainer unwired for extended period",
        "owner_domain": "domain.ragtag_domain_heartbeat_and_active_web",
    },
    {
        "series_id": "need_based_expansion_context_materialization_receipt",
        "glob": NEED_BASED_EXPANSION_RECEIPT_GLOB,
        "expected_interval_seconds": DOMAIN_FORMATION_STALL_DAYS * 86400,
        "interpretation": "need-based expansion context materialization receipts stale while necessity open",
        "owner_domain": "domain.domain_weaver_living_self_model",
    },
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _root(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    return p.parent if p.name == "ION" else p


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _rel(shell: Path, path: Path) -> str:
    try:
        return str(path.relative_to(shell))
    except ValueError:
        return str(path)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def check_systemd_ion_units() -> dict[str, Any]:
    """Enumerate ion-* user units; report any in failed state."""
    check: dict[str, Any] = {
        "check_id": "systemd_user_unit_failed",
        "status": "ok",
        "systemctl_available": True,
        "units": [],
        "findings": [],
    }
    try:
        proc = subprocess.run(
            [
                "systemctl",
                "--user",
                "list-units",
                "--all",
                "--no-pager",
                "--plain",
                "ion-*",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        check["systemctl_available"] = False
        check["status"] = "finding"
        check["findings"].append(
            {"kind": "systemctl_unavailable", "detail": str(exc)}
        )
        return check

    if proc.returncode != 0:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "systemctl_list_failed",
                "detail": (proc.stderr or proc.stdout or "").strip()[:500],
            }
        )
        return check

    lines = proc.stdout.splitlines()
    if len(lines) < 2:
        return check

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split(None, 4)
        if len(parts) < 4:
            continue
        unit, _load, active, sub = parts[0], parts[1], parts[2], parts[3]
        if not unit.startswith("ion-"):
            continue
        entry = {
            "unit": unit,
            "active_state": active,
            "sub_state": sub,
            "failed": active == "failed",
        }
        check["units"].append(entry)
        if entry["failed"]:
            check["status"] = "finding"
            check["findings"].append(
                {"kind": "unit_failed", "unit": unit, "active_state": active}
            )

    return check


def check_activation_records(shell: Path, *, now: datetime) -> dict[str, Any]:
    base = shell / "ION/05_context/current/autonomous_goals"
    check: dict[str, Any] = {
        "check_id": "activation_record_expiry_horizon",
        "horizon_days": ACTIVATION_HORIZON_DAYS,
        "status": "ok",
        "records": [],
        "findings": [],
    }
    if not base.is_dir():
        check["status"] = "finding"
        check["findings"].append({"kind": "autonomous_goals_missing", "path": str(base)})
        return check

    paths = sorted(base.rglob("ACTIVATION_RECORD*.candidate.json"))
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        loaded.append((path, data))

    successor_targets: set[str] = set()
    for _path, data in loaded:
        supersedes_id = str(data.get("supersedes_activation_record_id") or "").strip()
        if supersedes_id:
            successor_targets.add(supersedes_id)
        supersedes_path = str(data.get("supersedes_path") or "").strip()
        if supersedes_path:
            successor_targets.add(supersedes_path)

    for path, data in loaded:
        if str(data.get("status") or "").strip().lower() == "superseded":
            continue
        if data.get("superseded_by"):
            continue
        if data.get("schema_id") == "ion.autonomous_goals.activation_record_absence_signal.v0_1_candidate":
            continue
        expires_raw = data.get("expires_at")
        if not expires_raw:
            continue
        expires_at = _parse_ts(str(expires_raw))
        if expires_at is None:
            continue
        delta = expires_at - now
        days_remaining = delta.total_seconds() / 86400.0
        rel_path = _rel(shell, path)
        status = "active"
        if days_remaining < 0:
            status = "expired"
        elif days_remaining <= ACTIVATION_HORIZON_DAYS:
            status = "within_horizon"

        record_id = str(data.get("activation_record_id") or "").strip()
        has_successor = record_id in successor_targets or rel_path in successor_targets

        record = {
            "path": rel_path,
            "expires_at": str(expires_raw),
            "days_remaining": round(days_remaining, 2),
            "status": status,
            "successor_authored": has_successor,
        }
        check["records"].append(record)
        if status in {"expired", "within_horizon"}:
            check["status"] = "finding"
            check["findings"].append(
                {
                    "kind": f"activation_{status}",
                    "path": rel_path,
                    "days_remaining": record["days_remaining"],
                }
            )
            if not has_successor:
                check["findings"].append(
                    {
                        "kind": "activation_successor_missing",
                        "path": rel_path,
                        "days_remaining": record["days_remaining"],
                        "activation_record_id": record_id or None,
                    }
                )

    return check


def _artifact_mtime(path: Path) -> datetime | None:
    if not path.is_file():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _newest_in_glob(shell: Path, pattern: str) -> tuple[Path | None, datetime | None]:
    matches = sorted(shell.glob(pattern), key=lambda p: p.stat().st_mtime if p.is_file() else 0)
    if not matches:
        return None, None
    newest = matches[-1]
    return newest, _artifact_mtime(newest)


def _durable_queue_row_for_series(shell: Path, series_id: str) -> str | None:
    queue_path = (
        shell
        / "ION/05_context/current/domain_weaver/inter_domain_work_queue/"
        "DURABLE_SOS_DOMAIN_SPAWN_QUEUE.json"
    )
    if not queue_path.is_file():
        return None
    try:
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    for row in reversed(queue.get("rows") or []):
        if not isinstance(row, Mapping):
            continue
        prov = row.get("provenance") or {}
        if not isinstance(prov, Mapping):
            continue
        if str(prov.get("absence_series_id") or "") == series_id:
            rid = str(row.get("row_id") or "").strip()
            if rid:
                return rid
    return None


def _finding_enrichment_for_series(shell: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    series_id = str(spec.get("series_id") or "")
    out: dict[str, Any] = {}
    owner = str(spec.get("owner_domain") or "").strip()
    if owner:
        out["owner_domain"] = owner
    row_id = _durable_queue_row_for_series(shell, series_id)
    if row_id:
        out["durable_queue_row_id"] = row_id
    return out


def _expansion_receipt_timestamp(path: Path) -> datetime | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _artifact_mtime(path)
    for key in ("generated_at", "written_at", "materialized_at", "created_at"):
        parsed = _parse_ts(str(data.get(key) or ""))
        if parsed is not None:
            return parsed
    return _artifact_mtime(path)


def _newest_expansion_receipt(shell: Path) -> tuple[Path | None, datetime | None]:
    newest_path: Path | None = None
    newest_ts: datetime | None = None
    for path in sorted(shell.glob(NEED_BASED_EXPANSION_RECEIPT_GLOB)):
        if not path.is_file():
            continue
        if path.name.endswith(".latest.candidate.json"):
            continue
        ts = _expansion_receipt_timestamp(path)
        if ts is None:
            continue
        if newest_ts is None or ts > newest_ts:
            newest_ts = ts
            newest_path = path
    return newest_path, newest_ts


def _read_persisted_need_plan_snapshot(shell: Path) -> dict[str, Any]:
    plan_path = (
        shell
        / "ION/05_context/current/domain_weaver/need_based_expansion/"
        "DOMAIN_WEAVER_NEED_BASED_EXPANSION_PLAN.latest.candidate.json"
    )
    if not plan_path.is_file():
        return {
            "selected_lane_count": 0,
            "need_count": 0,
            "next_action": "",
            "plan_status": "persisted_plan_missing",
        }
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "selected_lane_count": 0,
            "need_count": 0,
            "next_action": "",
            "plan_status": "persisted_plan_unreadable",
            "plan_error": str(exc),
        }
    return {
        "selected_lane_count": int(data.get("selected_lane_count") or 0),
        "need_count": int(data.get("need_count") or 0),
        "next_action": str(data.get("next_action") or ""),
        "plan_status": "persisted_plan_snapshot",
        "persisted_plan_path": _rel(shell, plan_path),
    }


def _need_based_expansion_plan_snapshot(shell: Path) -> dict[str, Any]:
    try:
        from kernel.ion_domain_weaver_need_based_expansion import (
            build_need_based_domain_agent_expansion_plan,
        )

        plan = build_need_based_domain_agent_expansion_plan(shell)
    except (ValueError, OSError, ImportError, ModuleNotFoundError) as exc:
        persisted = _read_persisted_need_plan_snapshot(shell)
        persisted["plan_status"] = "need_based_expansion_plan_fallback_persisted"
        persisted["plan_error"] = str(exc)
        return persisted
    return {
        "selected_lane_count": int(plan.get("selected_lane_count") or 0),
        "need_count": int(plan.get("need_count") or 0),
        "next_action": str(plan.get("next_action") or ""),
        "plan_status": str(plan.get("status") or ""),
        "plan_source": "live_plan_builder",
    }


def check_domain_formation_stall(shell: Path, *, now: datetime) -> dict[str, Any]:
    """Report stall when open necessity persists without a recent expansion receipt."""

    check: dict[str, Any] = {
        "check_id": "domain_formation_stall",
        "series_id": "domain_formation_stall",
        "stall_threshold_days": DOMAIN_FORMATION_STALL_DAYS,
        "status": "ok",
        "open_necessity": False,
        "need_based_expansion_entrypoints": list(NEED_BASED_EXPANSION_KERNEL_ENTRYPOINTS),
        "need_based_expansion_plan": None,
        "last_expansion_receipt_at": None,
        "last_expansion_receipt_path": None,
        "days_without_expansion_receipt": None,
        "findings": [],
        "owner_domain": "domain.domain_mitosis_and_agent_society_formation",
    }
    plan_snapshot = _need_based_expansion_plan_snapshot(shell)
    check["need_based_expansion_plan"] = plan_snapshot
    open_necessity = int(plan_snapshot.get("selected_lane_count") or 0) > 0
    check["open_necessity"] = open_necessity

    newest_path, newest_ts = _newest_expansion_receipt(shell)
    if newest_path is not None and newest_ts is not None:
        check["last_expansion_receipt_at"] = _iso(newest_ts)
        check["last_expansion_receipt_path"] = _rel(shell, newest_path)
        days_without = (now - newest_ts).total_seconds() / 86400.0
        check["days_without_expansion_receipt"] = round(days_without, 2)

    enrichment = _finding_enrichment_for_series(shell, {"series_id": "domain_formation_stall"})

    if not open_necessity:
        return check

    if newest_ts is None:
        check["status"] = "finding"
        finding: dict[str, Any] = {
            "kind": "domain_formation_stall_no_expansion_receipt",
            "series_id": "domain_formation_stall",
            "open_necessity": True,
            "selected_lane_count": plan_snapshot.get("selected_lane_count"),
        }
        finding.update(enrichment)
        check["findings"].append(finding)
        return check

    days_without = float(check["days_without_expansion_receipt"] or 0)
    if days_without >= DOMAIN_FORMATION_STALL_DAYS:
        check["status"] = "finding"
        finding = {
            "kind": "domain_formation_stall_exceeded_threshold",
            "series_id": "domain_formation_stall",
            "open_necessity": True,
            "days_without_expansion_receipt": days_without,
            "stall_threshold_days": DOMAIN_FORMATION_STALL_DAYS,
            "last_expansion_receipt_path": check["last_expansion_receipt_path"],
        }
        finding.update(enrichment)
        check["findings"].append(finding)

    return check


def check_artifact_series(shell: Path, *, now: datetime) -> dict[str, Any]:
    check: dict[str, Any] = {
        "check_id": "stopped_artifact_series",
        "status": "ok",
        "series": [],
        "findings": [],
    }
    for spec in ARTIFACT_SERIES:
        pattern = spec["glob"]
        interval = int(spec["expected_interval_seconds"])
        empty_is_stale = bool(spec.get("empty_is_stale"))
        single_file = bool(spec.get("single_file"))

        if single_file:
            path = shell / pattern
            newest_path = path if path.is_file() else None
            last_seen = _artifact_mtime(path) if newest_path else None
        else:
            newest_path, last_seen = _newest_in_glob(shell, pattern)

        owner_domain = str(spec.get("owner_domain") or "").strip() or None
        series_entry: dict[str, Any] = {
            "series_id": spec["series_id"],
            "artifact_glob": pattern,
            "expected_interval_seconds": interval,
            "interpretation": spec.get("interpretation"),
            "owner_domain": owner_domain,
            "last_seen_at": _iso(last_seen) if last_seen else None,
            "last_seen_path": _rel(shell, newest_path) if newest_path else None,
            "status": "ok",
        }
        enrichment = _finding_enrichment_for_series(shell, spec)

        if last_seen is None:
            if empty_is_stale or not single_file:
                series_entry["status"] = "stale"
                check["status"] = "finding"
                finding: dict[str, Any] = {
                    "kind": "series_never_seen",
                    "series_id": spec["series_id"],
                    "artifact_glob": pattern,
                }
                finding.update(enrichment)
                check["findings"].append(finding)
            elif single_file:
                series_entry["status"] = "missing"
                check["status"] = "finding"
                finding = {
                    "kind": "series_file_missing",
                    "series_id": spec["series_id"],
                    "artifact_glob": pattern,
                }
                finding.update(enrichment)
                check["findings"].append(finding)
        else:
            age_s = (now - last_seen).total_seconds()
            series_entry["age_seconds"] = int(age_s)
            if age_s > interval:
                series_entry["status"] = "stale"
                check["status"] = "finding"
                finding = {
                    "kind": "series_stale",
                    "series_id": spec["series_id"],
                    "age_seconds": int(age_s),
                    "expected_interval_seconds": interval,
                }
                finding.update(enrichment)
                check["findings"].append(finding)

        queue_row = enrichment.get("durable_queue_row_id")
        if queue_row:
            series_entry["durable_queue_row_id"] = queue_row
        check["series"].append(series_entry)

    return check


def check_surface_meta(shell: Path, *, now: datetime) -> dict[str, Any]:
    surface_path = shell / SURFACE_REL
    check: dict[str, Any] = {
        "check_id": "absence_surface_freshness",
        "stale_threshold_seconds": SURFACE_STALE_SECONDS,
        "status": "ok",
        "prior_evaluated_at": None,
        "prior_age_seconds": None,
        "findings": [],
    }
    if not surface_path.is_file():
        check["status"] = "finding"
        check["findings"].append({"kind": "surface_missing", "path": str(SURFACE_REL)})
        return check

    try:
        prior = json.loads(surface_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        check["status"] = "finding"
        check["findings"].append({"kind": "surface_unreadable", "path": str(SURFACE_REL)})
        return check

    evaluated_at = _parse_ts(str(prior.get("evaluated_at") or ""))
    if evaluated_at is None:
        check["status"] = "finding"
        check["findings"].append({"kind": "surface_evaluated_at_missing"})
        return check

    age_s = (now - evaluated_at).total_seconds()
    check["prior_evaluated_at"] = _iso(evaluated_at)
    check["prior_age_seconds"] = int(age_s)
    if age_s > SURFACE_STALE_SECONDS:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "surface_stale",
                "age_seconds": int(age_s),
                "stale_threshold_seconds": SURFACE_STALE_SECONDS,
            }
        )

    return check


def check_carrier_attribution_loss(shell: Path, *, sample_limit: int = 40) -> dict[str, Any]:
    """Report-only: prompt-spawn runs missing resolvable carrier_id + run_id."""

    check: dict[str, Any] = {
        "check_id": "carrier_attribution_loss",
        "status": "ok",
        "sample_limit": sample_limit,
        "runs_scanned": 0,
        "runs_with_resolvable_identity": 0,
        "runs_missing_identity": [],
        "findings": [],
    }
    roots = [
        Path("ION/05_context/current/cursor_connector/prompt_spawn_runs"),
        Path("ION/05_context/current/claude_connector/claude_prompt_spawn_runs"),
        Path("ION/05_context/current/codex_connector/codex_prompt_spawn_runs"),
    ]

    def _resolve_identity(run_dir: Path) -> dict[str, str] | None:
        spawn_row_path = run_dir / "spawn_row.json"
        if spawn_row_path.is_file():
            try:
                row = json.loads(spawn_row_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                row = {}
            carrier_id = str(row.get("carrier_id") or "").strip()
            run_id = str(row.get("run_id") or run_dir.name).strip()
            bundle = str(row.get("execution_bundle_root") or "").strip()
            if carrier_id and run_id:
                return {
                    "carrier_id": carrier_id,
                    "run_id": run_id,
                    "execution_bundle_root": bundle or _rel(shell, run_dir),
                    "source": "spawn_row.json",
                }
        task_return_path = run_dir / "task_return.json"
        if task_return_path.is_file():
            try:
                payload = json.loads(task_return_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = {}
            for key in ("carrier_id", "run_id"):
                if str(payload.get(key) or "").strip():
                    pass
            evaluation = payload.get("evaluation")
            if isinstance(evaluation, dict):
                routing = evaluation.get("routing_decision") or {}
                if isinstance(routing, dict):
                    carrier_id = str(routing.get("carrier_id") or "").strip()
                    if carrier_id:
                        return {
                            "carrier_id": carrier_id,
                            "run_id": run_dir.name,
                            "execution_bundle_root": _rel(shell, run_dir),
                            "source": "task_return.evaluation.routing_decision",
                        }
        return None

    missing: list[dict[str, Any]] = []
    scanned = 0
    resolved = 0
    for rel_root in roots:
        base = shell / rel_root
        if not base.is_dir():
            continue
        run_dirs = sorted(
            (p for p in base.iterdir() if p.is_dir()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for run_dir in run_dirs:
            if scanned >= sample_limit:
                break
            scanned += 1
            identity = _resolve_identity(run_dir)
            if identity:
                resolved += 1
            else:
                missing.append(
                    {
                        "run_dir": _rel(shell, run_dir),
                        "spawn_row_present": (run_dir / "spawn_row.json").is_file(),
                        "task_return_present": (run_dir / "task_return.json").is_file(),
                    }
                )
        if scanned >= sample_limit:
            break

    check["runs_scanned"] = scanned
    check["runs_with_resolvable_identity"] = resolved
    check["runs_missing_identity"] = missing[:20]
    if missing:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "carrier_attribution_unresolvable",
                "count": len(missing),
                "sample": missing[:5],
                "route_to": OWNER_DOMAIN,
            }
        )
    return check


def check_carrier_economics_mode_unset(shell: Path) -> dict[str, Any]:
    """Finding-only: claude_cli spawn rows missing economics_mode witness."""
    check: dict[str, Any] = {
        "check_id": "carrier_economics_mode_unset",
        "status": "clear",
        "findings": [],
        "spawn_rows_scanned": 0,
        "missing_economics_mode": [],
    }
    runs_root = shell / "ION/05_context/current/cursor_connector/prompt_spawn_runs"
    if not runs_root.is_dir():
        return check
    sample_limit = 40
    scanned = 0
    for run_dir in sorted(runs_root.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        spawn_path = run_dir / "spawn_row.json"
        if not spawn_path.is_file():
            continue
        scanned += 1
        try:
            row = json.loads(spawn_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        carrier_id = str(row.get("carrier_id") or row.get("execution_carrier") or "").strip()
        if carrier_id != "claude_cli":
            continue
        admission = row.get("spawn_admission")
        if not isinstance(admission, Mapping):
            admission_path = run_dir / "spawn_admission.json"
            if admission_path.is_file():
                try:
                    admission = json.loads(admission_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    admission = {}
            else:
                admission = {}
        economics_mode = None
        if isinstance(admission, Mapping):
            economics_mode = admission.get("economics_mode") or admission.get(
                "carrier_economics_mode"
            )
        if not economics_mode:
            check["missing_economics_mode"].append(
                {
                    "run_dir": _rel(shell, run_dir),
                    "carrier_id": carrier_id,
                    "route_to": "domain.model_routing_and_reasoning_economics",
                }
            )
        if scanned >= sample_limit:
            break
    check["spawn_rows_scanned"] = scanned
    if check["missing_economics_mode"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "carrier_economics_mode_unset",
                "signal_id": "CARRIER_ECONOMICS_MODE_UNSET",
                "count": len(check["missing_economics_mode"]),
                "sample": check["missing_economics_mode"][:5],
                "route_to": [
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.model_routing_and_reasoning_economics/"
                ],
            }
        )
    return check


def check_spawn_admission_governing_template_join_missing(shell: Path) -> dict[str, Any]:
    """Finding-only: admitted prompt spawns missing T03 governing template join on admission."""
    check: dict[str, Any] = {
        "check_id": "spawn_admission_governing_template_join_missing",
        "status": "clear",
        "findings": [],
        "spawn_rows_scanned": 0,
        "missing_join_fields": [],
    }
    runs_root = shell / "ION/05_context/current/cursor_connector/prompt_spawn_runs"
    if not runs_root.is_dir():
        return check
    required_keys = (
        "template_id",
        "governing_template_id",
        "governing_template_spec_path",
    )
    scanned = 0
    for run_dir in sorted(runs_root.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        admission_path = run_dir / "spawn_admission.json"
        if not admission_path.is_file():
            continue
        scanned += 1
        try:
            admission = json.loads(admission_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not admission.get("carrier_invocation_admitted"):
            continue
        missing = [key for key in required_keys if not str(admission.get(key) or "").strip()]
        if missing:
            check["missing_join_fields"].append(
                {
                    "run_dir": _rel(shell, run_dir),
                    "missing_keys": missing,
                    "route_to": (
                        "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                        "domain.kernel_ownership_runtime_carrier_slice/"
                    ),
                }
            )
        if scanned >= 25:
            break
    check["spawn_rows_scanned"] = scanned
    if check["missing_join_fields"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "spawn_admission_governing_template_join_missing",
                "signal_id": "FINDING_TPL_SPAWN_TEMPLATE_JOIN_DRIFT",
                "count": len(check["missing_join_fields"]),
                "sample": check["missing_join_fields"][:5],
            }
        )
    return check


def check_spawn_admission_row_carrier_readiness_drift(shell: Path) -> dict[str, Any]:
    """Finding-only: spawn_row carrier_readiness disagrees with spawn_admission.json."""
    from kernel.ion_prompt_spawn_admission import carrier_scoped_readiness_blockers

    check: dict[str, Any] = {
        "check_id": "spawn_admission_row_carrier_readiness_drift",
        "status": "clear",
        "findings": [],
        "spawn_rows_scanned": 0,
        "drift_samples": [],
    }
    runs_root = shell / "ION/05_context/current/cursor_connector/prompt_spawn_runs"
    if not runs_root.is_dir():
        return check
    scanned = 0
    for run_dir in sorted(runs_root.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        admission_path = run_dir / "spawn_admission.json"
        row_path = run_dir / "spawn_row.json"
        if not admission_path.is_file() or not row_path.is_file():
            continue
        scanned += 1
        try:
            admission = json.loads(admission_path.read_text(encoding="utf-8"))
            row = json.loads(row_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        carrier_id = str(admission.get("carrier_id") or row.get("carrier_id") or "")
        admission_readiness = admission.get("carrier_readiness")
        row_nested = (
            (row.get("spawn_admission") or {}).get("carrier_readiness")
            if isinstance(row.get("spawn_admission"), dict)
            else None
        )
        row_top = row.get("carrier_readiness")
        issues: list[str] = []
        if not isinstance(admission_readiness, Mapping):
            issues.append("spawn_admission.json:carrier_readiness_missing")
        if not isinstance(row_nested, Mapping):
            issues.append("spawn_row.json:spawn_admission.carrier_readiness_missing")
        if row_top is not None and admission_readiness != row_top:
            issues.append("spawn_row.json:carrier_readiness_top_level_mismatch")
        if (
            isinstance(admission_readiness, Mapping)
            and isinstance(row_nested, Mapping)
            and admission_readiness != row_nested
        ):
            issues.append("spawn_row.json:spawn_admission.carrier_readiness_mismatch")
        if isinstance(admission_readiness, Mapping) and carrier_id:
            scoped = carrier_scoped_readiness_blockers(
                list(admission_readiness.get("blocked_by") or []),
                carrier_id,
            )
            unscoped = list(admission_readiness.get("blocked_by") or [])
            if unscoped and not scoped and admission_readiness.get("verdict") in {
                "ION_PROMPT_SPAWN_EXECUTOR_READY",
            }:
                issues.append(
                    "spawn_admission.json:carrier_readiness_blocked_by_cross_carrier_only"
                )
        if issues:
            check["drift_samples"].append(
                {
                    "run_dir": _rel(shell, run_dir),
                    "carrier_id": carrier_id,
                    "issues": issues,
                    "route_to": (
                        "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                        "domain.runtime_carrier_and_action_admission/"
                    ),
                }
            )
        if scanned >= 25:
            break
    check["spawn_rows_scanned"] = scanned
    if check["drift_samples"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "spawn_admission_row_carrier_readiness_drift",
                "signal_id": "SPAWN_ADMISSION_ROW_CARRIER_READINESS_DRIFT",
                "count": len(check["drift_samples"]),
                "sample": check["drift_samples"][:5],
            }
        )
    return check


def _newest_spawn_admission_paths(shell: Path) -> list[tuple[str, Path]]:
    """Latest spawn_admission.json per carrier lane (cursor + claude)."""
    lanes = (
        ("cursor_cli", shell / "ION/05_context/current/cursor_connector/prompt_spawn_runs"),
        (
            "claude_cli",
            shell / "ION/05_context/current/claude_connector/claude_prompt_spawn_runs",
        ),
    )
    found: list[tuple[str, Path]] = []
    for carrier_id, runs_root in lanes:
        if not runs_root.is_dir():
            continue
        newest: Path | None = None
        for run_dir in sorted(runs_root.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue
            admission_path = run_dir / "spawn_admission.json"
            if admission_path.is_file():
                newest = admission_path
                break
        if newest is not None:
            found.append((carrier_id, newest))
    return found


def check_spawn_admission_hash_verification_mismatch(shell: Path) -> dict[str, Any]:
    """Finding-only: newest per-carrier spawn admission hash does not recompute."""
    from kernel.ion_prompt_spawn_admission import (
        admission_basis_extra_keys,
        admission_basis_missing_keys,
        admission_sha256_matches,
        recompute_admission_sha256,
    )

    check: dict[str, Any] = {
        "check_id": "spawn_admission_hash_verification_mismatch",
        "status": "clear",
        "findings": [],
        "lanes_checked": [],
        "mismatch_samples": [],
    }
    for carrier_id, admission_path in _newest_spawn_admission_paths(shell):
        check["lanes_checked"].append(carrier_id)
        try:
            admission = json.loads(admission_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        extra = admission_basis_extra_keys(admission)
        missing = admission_basis_missing_keys(admission)
        matches = admission_sha256_matches(admission)
        if not matches or extra or missing:
            check["mismatch_samples"].append(
                {
                    "carrier_id": carrier_id,
                    "admission_path": _rel(shell, admission_path),
                    "hash_matches": matches,
                    "basis_extra_keys": extra,
                    "basis_missing_keys": missing,
                    "stored_sha256": admission.get("admission_sha256"),
                    "recomputed_sha256": recompute_admission_sha256(admission),
                    "route_to": OWNER_DOMAIN,
                }
            )
    if check["mismatch_samples"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "spawn_admission_hash_verification_mismatch",
                "signal_id": "SPAWN_ADMISSION_HASH_VERIFICATION_MISMATCH",
                "count": len(check["mismatch_samples"]),
                "sample": check["mismatch_samples"][:5],
                "route_to": [
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ],
            }
        )
    return check


def check_advisory_economics_binding_enforcement_divergence(shell: Path) -> dict[str, Any]:
    """Finding-only: legacy mode-blind governed-model gate disagrees with Gate-A predicate."""

    from kernel.ion_prompt_spawn_admission import (
        is_advisory_economics_governed_model,
        spawn_requires_advisory_economics_binding,
    )

    check: dict[str, Any] = {
        "check_id": "advisory_economics_binding_enforcement_divergence",
        "status": "clear",
        "findings": [],
        "divergence_samples": [],
    }
    scenarios = (
        {
            "carrier_id": "claude_cli",
            "model": "claude-opus-5",
            "work_class": "audit_observation",
            "intent": {"explicit_premium_model": True},
            "economics_mode": "subscription",
        },
        {
            "carrier_id": "claude_cli",
            "model": "claude-opus-5",
            "work_class": "audit_observation",
            "intent": {},
            "economics_mode": "metered",
        },
    )
    for scenario in scenarios:
        model = str(scenario["model"])
        mode_blind_requires = is_advisory_economics_governed_model(model)
        mode_aware_requires = spawn_requires_advisory_economics_binding(
            carrier_id=str(scenario["carrier_id"]),
            model=model,
            work_class=str(scenario["work_class"]),
            intent=scenario["intent"],
            shell_root=shell,
            economics_mode=str(scenario["economics_mode"]),
        )
        if mode_blind_requires != mode_aware_requires:
            check["divergence_samples"].append(
                {
                    **scenario,
                    "mode_blind_requires_binding": mode_blind_requires,
                    "mode_aware_requires_binding": mode_aware_requires,
                    "route_to": OWNER_DOMAIN,
                }
            )
    if check["divergence_samples"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "advisory_economics_binding_enforcement_divergence",
                "signal_id": "ADVISORY_ECONOMICS_BINDING_ENFORCEMENT_DIVERGENCE",
                "count": len(check["divergence_samples"]),
                "sample": check["divergence_samples"][:5],
                "route_to": [
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ],
            }
        )
    return check


def check_wakeup_spawn_admission_gate_alignment(shell: Path) -> dict[str, Any]:
    """Detect when wakeup detached activation gate remains blocked after admission artifacts exist."""
    check: dict[str, Any] = {
        "check_id": "wakeup_spawn_admission_gate_alignment",
        "status": "ok",
        "findings": [],
    }
    from kernel.ion_autonomous_goal_wakeup import evaluate_wakeup_activation_gate

    gate = evaluate_wakeup_activation_gate(shell)
    verdict = str(gate.get("verdict") or "")
    blockers = gate.get("blockers") or []
    check["gate_verdict"] = verdict
    check["blocker_count"] = len(blockers)
    if verdict != "ION_AUTONOMOUS_GOAL_WAKEUP_ACTIVATION_ALLOWED":
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "wakeup_spawn_admission_gate_blocked",
                "signal_id": "WAKEUP_SPAWN_ADMISSION_GATE_BLOCKED",
                "gate_verdict": verdict,
                "blockers": blockers[:8],
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ),
            }
        )
    return check


def check_carrier_workflow_domain_fleet_audit_alignment(shell: Path) -> dict[str, Any]:
    """Detect audit law drift vs ion_carrier_continue domain_fleet_required turn packets."""
    check: dict[str, Any] = {"status": "ok", "findings": []}
    turn_path = shell / "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json"
    plan_path = shell / "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json"
    if not turn_path.is_file():
        check["status"] = "skipped"
        check["reason"] = "missing_active_turn_packet"
        return check
    turn = json.loads(turn_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else {}
    fleet = turn.get("domain_fleet_required") or plan.get("domain_fleet_required")
    if not fleet:
        check["reason"] = "domain_fleet_not_active"
        return check
    from kernel.ion_carrier_workflow_audit import audit_carrier_workflow

    audit = audit_carrier_workflow(shell)
    drift_tags = {
        "active_turn_packet_missing_spawn_queue",
        "active_turn_packet_invalid_return_intake_status:DOMAIN_FLEET_REQUIRED",
        "active_turn_packet_invalid_return_intake_status:SOS_FRONT_DOOR_CLOSED_CANDIDATE",
    }
    drift = [f for f in audit.get("findings", []) if f in drift_tags]
    check["audit_verdict"] = audit.get("verdict")
    if drift:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "carrier_workflow_domain_fleet_audit_drift",
                "signal_id": "CARRIER_WORKFLOW_DOMAIN_FLEET_AUDIT_DRIFT",
                "audit_findings": drift,
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ),
            }
        )
    return check


def check_usage_limit_signal_honesty_regression() -> dict[str, Any]:
    """Regression guard: unmatched CLI output must not normalize to a truthy usage-limit sentinel."""
    from kernel.ion_cli_carrier_gateway import normalize_usage_limit_signal
    from kernel.ion_cli_model_selection import is_usage_limit_failure

    check: dict[str, Any] = {
        "check_id": "usage_limit_signal_honesty_regression",
        "status": "ok",
        "findings": [],
    }
    samples = {
        "random_text": normalize_usage_limit_signal("some random failure text"),
        "empty": normalize_usage_limit_signal(""),
        "real_limit": normalize_usage_limit_signal("you have hit your usage limit"),
    }
    check["samples"] = samples
    if samples["random_text"] is not None or samples["empty"] is not None:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "usage_limit_sentinel_still_truthy",
                "signal_id": "USAGE_LIMIT_SENTINEL_STILL_TRUTHY",
                "samples": samples,
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ),
            }
        )
    if samples["real_limit"] != "usage_limit":
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "usage_limit_pattern_regression",
                "signal_id": "USAGE_LIMIT_PATTERN_REGRESSION",
                "expected": "usage_limit",
                "actual": samples["real_limit"],
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.honest_agency_validation/"
                ),
            }
        )
    if is_usage_limit_failure("ModuleNotFoundError: nope"):
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "usage_limit_finding_without_evidence",
                "signal_id": "USAGE_LIMIT_FINDING_WITHOUT_EVIDENCE",
                "sample_text": "ModuleNotFoundError: nope",
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.honest_agency_validation/"
                ),
            }
        )
    return check


def routing_note() -> dict[str, Any]:
    return {
        "primary_surface_path": str(SURFACE_REL),
        "operator_seat_capsule": OPERATOR_SEAT_CAPSULE,
        "proposed_context_ref_id": PROPOSED_CONTEXT_REF,
        "how_surface_reaches_operator_package": (
            "Surface JSON is written at a stable path listed in route_to. "
            "AETHER_OPERATOR RESUME_MANIFEST and Domain Weaver dogfood capsule are "
            "named sinks per ABSENCE_DETECTOR_SPEC. The lead steward mount capsule "
            "does not yet declare this path; add dynamic_context_ref "
            f"'{PROPOSED_CONTEXT_REF}' -> {SURFACE_REL} via steward/context "
            "maintenance (do not edit operator seat from this worker)."
        ),
        "route_to": list(ROUTE_TO),
        "optional_signal_drop": "ION/05_context/current/signals/",
    }


def run_absence_probe(
    *,
    ion_root: str | Path,
    write: bool = False,
) -> dict[str, Any]:
    shell = _root(ion_root)
    now = _now()
    meta_before = check_surface_meta(shell, now=now)
    systemd = check_systemd_ion_units()
    activation = check_activation_records(shell, now=now)
    artifacts = check_artifact_series(shell, now=now)
    domain_formation_stall = check_domain_formation_stall(shell, now=now)
    carrier_attribution = check_carrier_attribution_loss(shell)
    carrier_economics = check_carrier_economics_mode_unset(shell)
    carrier_fleet_audit = check_carrier_workflow_domain_fleet_audit_alignment(shell)
    spawn_template_join = check_spawn_admission_governing_template_join_missing(shell)
    spawn_readiness_drift = check_spawn_admission_row_carrier_readiness_drift(shell)
    spawn_admission_hash = check_spawn_admission_hash_verification_mismatch(shell)
    advisory_economics_divergence = (
        check_advisory_economics_binding_enforcement_divergence(shell)
    )
    wakeup_gate = check_wakeup_spawn_admission_gate_alignment(shell)
    usage_limit_honesty = check_usage_limit_signal_honesty_regression()
    from kernel.ion_cli_model_selection import (
        probe_judgment_work_class_spawn_admission_streak,
        probe_spawn_model_outside_sovereign_allowlist,
        probe_unattended_premium_sos_spawn_absence,
    )

    unattended_premium_sos = probe_unattended_premium_sos_spawn_absence(shell)
    sovereign_spawn_models = probe_spawn_model_outside_sovereign_allowlist(shell)
    judgment_admission_streak = probe_judgment_work_class_spawn_admission_streak(shell)

    checks = {
        "systemd_user_unit_failed": systemd,
        "activation_record_expiry_horizon": activation,
        "stopped_artifact_series": artifacts,
        "domain_formation_stall": domain_formation_stall,
        "carrier_attribution_loss": carrier_attribution,
        "carrier_economics_mode_unset": carrier_economics,
        "carrier_workflow_domain_fleet_audit_alignment": carrier_fleet_audit,
        "spawn_admission_governing_template_join_missing": spawn_template_join,
        "spawn_admission_row_carrier_readiness_drift": spawn_readiness_drift,
        "spawn_admission_hash_verification_mismatch": spawn_admission_hash,
        "advisory_economics_binding_enforcement_divergence": advisory_economics_divergence,
        "wakeup_spawn_admission_gate_alignment": wakeup_gate,
        "usage_limit_signal_honesty_regression": usage_limit_honesty,
        "unattended_premium_sos_spawn_economics": unattended_premium_sos,
        "judgment_work_class_spawn_admission_streak": judgment_admission_streak,
        "spawn_model_outside_sovereign_allowlist": sovereign_spawn_models,
        "absence_surface_freshness_prior": meta_before,
    }

    has_findings = any(c.get("status") == "finding" for c in checks.values())
    verdict = "ABSENCE_SIGNAL_PRESENT" if has_findings else "ABSENCE_SIGNAL_CLEAR"

    healthy_examples: list[str] = []
    for u in systemd.get("units", []):
        if not u.get("failed") and u.get("active_state") in {"active", "inactive"}:
            healthy_examples.append(f"systemd unit {u['unit']} active_state={u['active_state']}")
    for rec in activation.get("records", []):
        if rec.get("status") == "active" and rec.get("days_remaining", 0) > ACTIVATION_HORIZON_DAYS:
            healthy_examples.append(f"activation {rec['path']} days_remaining={rec['days_remaining']}")

    surface: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "surface_id": "ION_RUNTIME_ABSENCE_SURFACE",
        "owner_domain_id": OWNER_DOMAIN,
        "evaluated_at": _iso(now),
        "evaluator": "kernel.ion_runtime_absence_probe",
        "verdict": verdict,
        "checks": checks,
        "routing": routing_note(),
        "route_to": list(ROUTE_TO),
        "meta_check": {
            "description": "Surface stale if evaluated_at not refreshed within 7200s",
            "stale_threshold_seconds": SURFACE_STALE_SECONDS,
            "this_evaluation_fresh": True,
            "prior_surface_stale": meta_before.get("status") == "finding",
        },
        "healthy_negative_control_samples": healthy_examples[:5],
        "blocking_gate": False,
        "non_claims": ["candidate_only", "report_and_route_only", "no_global_blocker"],
    }

    receipt: dict[str, Any] | None = None
    if write:
        surface_path = shell / SURFACE_REL
        surface_path.parent.mkdir(parents=True, exist_ok=True)
        surface_path.write_text(
            json.dumps(surface, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        receipts_dir = shell / RECEIPTS_DIR_REL
        receipts_dir.mkdir(parents=True, exist_ok=True)
        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        receipt_path = receipts_dir / f"{stamp}_absence_probe.candidate.json"
        receipt = {
            "schema_id": "ion.runtime_carrier.absence_probe_receipt.v0_1_candidate",
            "written_at": _iso(now),
            "surface_path": str(SURFACE_REL),
            "verdict": verdict,
            "finding_count": sum(len(c.get("findings", [])) for c in checks.values()),
        }
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        surface["receipt_path"] = _rel(shell, receipt_path)

    return {
        "schema_id": "ion.runtime_carrier.absence_probe_run.v0_1_candidate",
        "evaluated_at": _iso(now),
        "verdict": verdict,
        "write_performed": write,
        "surface": surface,
        "receipt": receipt,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ION runtime absence probe (report-only, always exit 0)."
    )
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_absence_probe(ion_root=args.ion_root, write=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
