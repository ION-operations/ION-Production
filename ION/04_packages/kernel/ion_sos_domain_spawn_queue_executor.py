"""Execute ACTIVE_SOS_DOMAIN_SPAWN_QUEUE rows (Hop3→ACTIVE_DOMAIN_WEB only).

Parent must never invent --domain-id. Domains come only from the ION-written queue.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

# Re-export for domain proof scripts and operator repro.
__all__ = (
    "execute_sos_domain_spawn_queue",
    "resolve_unattended_spawn_carrier_model",
)

from .ion_cf12_directive_scope_expiry_admission_hook import (
    maybe_record_queue_row_cf12_findings,
)
from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_cli_model_selection import (
    judgment_work_class_grants_premium_intent,
    refusal_for_cursor_hosted_claude_model,
    refusal_for_unattended_spawn_model,
    resolve_unattended_spawn_carrier_model,
)
from .ion_domain_cursor_runner import process_domain_once
from .ion_prompt_spawn_admission import PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID
from .ion_sos_active_domain_web_mount import ACTIVE_SOS_DOMAIN_SPAWN_QUEUE_REL
from .ion_sos_durable_inter_domain_spawn_queue import (
    DURABLE_INTER_DOMAIN_SPAWN_QUEUE_REL,
    mark_row_executed,
    pending_spawn_rows,
)

SCHEMA_ID = "ion.sos_domain_spawn_queue_execution.v0_1_candidate"
READY_VERDICT = "ION_SOS_DOMAIN_SPAWN_QUEUE_EXECUTED"
BLOCKED_VERDICT = "ION_SOS_DOMAIN_SPAWN_QUEUE_BLOCKED"
ROUTED_FINDING_VERDICT = "ION_SOS_DOMAIN_SPAWN_QUEUE_ROUTED_FINDING"


def _executor_exit_code(payload: Mapping[str, Any]) -> int:
    """Row-level routed findings are not service crashes."""

    if payload.get("verdict") == READY_VERDICT:
        return 0
    if str(payload.get("reason") or "").strip():
        return 1
    return 0


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute_sos_domain_spawn_queue(
    root: str | Path | None = None,
    *,
    queue_path: str | Path | None = None,
    dry_run: bool = False,
    max_rows: int | None = None,
    timeout_seconds: int = 600,
    work_class: str | None = None,
) -> dict[str, Any]:
    shell_root = resolve_shell_root_from_ion_root(root)
    use_projection = queue_path is not None and Path(str(queue_path)) == ACTIVE_SOS_DOMAIN_SPAWN_QUEUE_REL
    default_path = shell_root / DURABLE_INTER_DOMAIN_SPAWN_QUEUE_REL
    path = shell_root / Path(str(queue_path)) if queue_path else default_path
    queue = _read_json(path)
    if not isinstance(queue, Mapping):
        return {
            "schema_id": SCHEMA_ID,
            "verdict": BLOCKED_VERDICT,
            "reason": "sos_domain_spawn_queue_missing",
            "queue_path": str(path.relative_to(shell_root)),
            "production_authority": False,
            "live_execution_authority": False,
        }

    if use_projection:
        rows = [r for r in (queue.get("rows") or []) if isinstance(r, Mapping) and r.get("spawn")]
    else:
        rows = pending_spawn_rows(queue)
    if max_rows is not None:
        rows = rows[: max(0, int(max_rows))]

    results: list[dict[str, Any]] = []
    for row in rows:
        try:
            maybe_record_queue_row_cf12_findings(shell_root, row=row, write=True)
        except Exception:
            pass
        domain_id = str(row.get("domain_id") or row.get("domain_true_name") or "")
        if not domain_id.startswith("domain."):
            results.append(
                {
                    "ok": False,
                    "domain_id": domain_id,
                    "finding": "invalid_domain_id_on_spawn_row",
                }
            )
            continue
        if str(row.get("source_kind") or "") != "spawn_plan_row":
            results.append(
                {
                    "ok": False,
                    "domain_id": domain_id,
                    "finding": "spawn_row_missing_spawn_plan_row_provenance",
                }
            )
            continue
        directive = str(row.get("objective") or "").strip() or (
            f"SOS front-door domain worker for {domain_id}. "
            "Candidate-only. Prove Hop3→ACTIVE_DOMAIN_WEB binding. No trilogy agents."
        )
        row_work_class = str(row.get("work_class") or "").strip()
        if not row_work_class:
            results.append(
                {
                    "ok": False,
                    "domain_id": domain_id,
                    "index": row.get("index"),
                    "finding": "work_class_absent_on_sos_row",
                    "detects_absence": True,
                }
            )
            continue
        if row_work_class not in PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID:
            results.append(
                {
                    "ok": False,
                    "domain_id": domain_id,
                    "index": row.get("index"),
                    "finding": "work_class_unmapped",
                    "work_class": row_work_class,
                    "detects_absence": True,
                }
            )
            continue
        resolution = resolve_unattended_spawn_carrier_model(shell_root, row_work_class)
        explicit_model = str(row.get("model") or row.get("model_id") or "").strip() or None
        explicit_premium_intent = bool(row.get("explicit_premium_model_intent"))
        if not explicit_premium_intent and judgment_work_class_grants_premium_intent(
            shell_root,
            row_work_class,
            str(resolution.get("carrier_id") or ""),
            str(explicit_model or resolution.get("model_id") or ""),
        ):
            explicit_premium_intent = True
        if explicit_model:
            resolution = {
                **resolution,
                "model_id": explicit_model,
                "resolution_source": "spawn_row_explicit_model",
            }
        hosted_refusal = refusal_for_cursor_hosted_claude_model(
            shell_root,
            carrier_id=str(resolution.get("carrier_id") or ""),
            model_id=str(explicit_model or resolution.get("model_id") or ""),
            domain_id=domain_id,
            row_id=row.get("row_id"),
            index=row.get("index"),
            work_class=row_work_class,
        )
        if hosted_refusal:
            results.append(hosted_refusal)
            continue
        refusal = refusal_for_unattended_spawn_model(
            shell_root,
            resolution,
            row_id=row.get("row_id"),
            index=row.get("index"),
            domain_id=domain_id,
            explicit_model=explicit_model,
            explicit_premium_intent=explicit_premium_intent,
        )
        if refusal:
            results.append(refusal)
            continue
        result = process_domain_once(
            shell_root,
            domain_id=domain_id,
            directive=directive,
            dry_run=dry_run,
            timeout_seconds=timeout_seconds,
            work_class=row_work_class or None,
            carrier=str(resolution.get("carrier_id") or "cursor_cli"),
            model=str(resolution.get("model_id") or "composer-2.5"),
            source_kind="spawn_plan_row",
            spawn_plan_row_ref=str(path.relative_to(shell_root)),
            web_id=str(row.get("web_id") or queue.get("web_id") or ""),
            index=int(row.get("index") or 0) or None,
        )
        item = {
            "ok": bool(result.get("ok")),
            "domain_id": domain_id,
            "index": row.get("index"),
            "row_id": row.get("row_id"),
            "work_class": row_work_class,
            "resolved_carrier_id": resolution.get("carrier_id"),
            "resolved_model_id": resolution.get("model_id"),
            "work_class_map_sha256": resolution.get("work_class_map_sha256"),
            "resolution_source": resolution.get("resolution_source"),
            "explicit_premium_model_intent": explicit_premium_intent,
            "selected_model": result.get("selected_model") or resolution.get("model_id"),
            "result": result.get("result") or result.get("verdict"),
            "finding": result.get("finding") or (result.get("blocked_by") or [None])[0]
            if isinstance(result.get("blocked_by"), list)
            else result.get("finding"),
            "run_id": result.get("run_id"),
            "dry_run": dry_run,
        }
        results.append(item)
        if item.get("ok") and not dry_run and row.get("row_id"):
            item["row_marked_executed"] = mark_row_executed(
                shell_root, row_id=str(row.get("row_id"))
            )

    ok_count = sum(1 for item in results if item.get("ok"))
    all_routed = bool(results) and all(
        isinstance(item, Mapping) and (item.get("ok") or item.get("finding"))
        for item in results
    )
    if results and ok_count == len(results):
        verdict = READY_VERDICT
    elif all_routed and ok_count < len(results):
        verdict = ROUTED_FINDING_VERDICT
    else:
        verdict = BLOCKED_VERDICT
    payload = {
        "schema_id": SCHEMA_ID,
        "verdict": verdict,
        "executed_at": _now(),
        "queue_path": str(path.relative_to(shell_root)),
        "web_id": queue.get("web_id"),
        "dry_run": dry_run,
        "row_count": len(results),
        "ok_count": ok_count,
        "results": results,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "detects_absence": True,
    }
    receipt_dir = shell_root / "ION/05_context/current/sos_domain_spawn_receipts"
    stamp = _now().replace(":", "").replace("+", "Z")
    receipt_path = receipt_dir / f"{stamp}_SOS_DOMAIN_SPAWN_QUEUE_EXECUTION.candidate.json"
    _write_json(receipt_path, payload)
    payload["receipt_path"] = str(receipt_path.relative_to(shell_root))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute ION ACTIVE_SOS_DOMAIN_SPAWN_QUEUE rows.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument(
        "--queue-path",
        default=None,
        help="Defaults to durable inter-domain queue; pass ACTIVE_SOS path only for Hop-3 projection.",
    )
    parser.add_argument(
        "--projection-queue",
        action="store_true",
        help="Execute ACTIVE_SOS_DOMAIN_SPAWN_QUEUE.json projection (not durable handoffs).",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument(
        "--work-class",
        default=None,
        help="Deprecated fallback; each SOS row must declare work_class explicitly.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    qpath = args.queue_path
    if args.projection_queue and not qpath:
        qpath = ACTIVE_SOS_DOMAIN_SPAWN_QUEUE_REL
    payload = execute_sos_domain_spawn_queue(
        args.ion_root,
        queue_path=qpath,
        dry_run=args.dry_run,
        max_rows=args.max_rows,
        timeout_seconds=args.timeout_seconds,
        work_class=args.work_class,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload.get("verdict"), payload.get("ok_count"), "/", payload.get("row_count"))
        print(payload.get("receipt_path"))
    return _executor_exit_code(payload)


if __name__ == "__main__":
    raise SystemExit(main())
