#!/usr/bin/env python3
"""Scan prompt-spawn runs for reduced execution_tier work; ledger for premium re-audit."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def _shell(ion_root: Path) -> Path:
    p = ion_root.resolve()
    return p.parent if p.name == "ION" else p


def _touched_paths_from_run(run_dir: Path) -> list[str]:
    for name in ("task_return.json", "run.json"):
        path = run_dir / name
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, Mapping):
            direct = payload.get("touched_paths")
            if isinstance(direct, list):
                return [str(item) for item in direct if str(item).strip()]
            template = payload.get("template_action_proof")
            if isinstance(template, Mapping):
                tp = template.get("touched_paths")
                if isinstance(tp, list):
                    return [str(item) for item in tp if str(item).strip()]
    return []


def scan_reduced_runs(shell: Path, *, limit: int = 200) -> dict[str, Any]:
    sys.path.insert(0, str(shell / "ION/04_packages"))
    from kernel import ion_cli_model_selection as selection  # noqa: WPS433

    runs_root = shell / "ION/05_context/current/cursor_connector/prompt_spawn_runs"
    entries: list[dict[str, Any]] = []
    absence_findings: list[str] = []
    if not runs_root.is_dir():
        absence_findings.append("prompt_spawn_runs_root_missing")
        return {
            "schema_id": "ion.reduced_state_work_ledger.v0_1_candidate",
            "entries": entries,
            "absence_findings": absence_findings,
            "scan_root": runs_root.as_posix(),
        }

    run_dirs = sorted(
        [p for p in runs_root.iterdir() if p.is_dir()],
        key=lambda p: p.name,
    )[-limit:]
    for run_dir in run_dirs:
        admission_path = run_dir / "spawn_admission.json"
        if not admission_path.is_file():
            continue
        try:
            admission = json.loads(admission_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        carrier = str(admission.get("carrier_id") or "").strip()
        model = str(admission.get("model") or "").strip()
        tier = str(admission.get("execution_tier") or "").strip()
        if not tier:
            tier = selection.derive_execution_tier(
                carrier,
                model,
                shell_root=shell,
                operation_mode=str(admission.get("operation_mode") or "full"),
                work_class=str(admission.get("work_class") or "") or None,
            )
        if tier != "reduced":
            continue
        touched = _touched_paths_from_run(run_dir)
        entries.append(
            {
                "run_dir": run_dir.relative_to(shell).as_posix(),
                "admission_id": admission.get("admission_id"),
                "domain_id": admission.get("domain_id"),
                "work_class": admission.get("work_class"),
                "carrier_id": carrier,
                "model": model,
                "execution_tier": tier,
                "operation_mode": admission.get("operation_mode") or "full",
                "routing_decision_id": admission.get("routing_decision_id"),
                "touched_paths": touched,
                "reaudit_enqueue_hint": {
                    "when": "premium_model_available",
                    "blocking": False,
                },
            }
        )

    if not entries:
        absence_findings.append("no_reduced_tier_runs_in_window")

    return {
        "schema_id": "ion.reduced_state_work_ledger.v0_1_candidate",
        "domain_id": "domain.model_routing_and_reasoning_economics",
        "scanned_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scan_root": runs_root.relative_to(shell).as_posix(),
        "entry_count": len(entries),
        "entries": entries,
        "absence_findings": absence_findings,
        "blocking_gate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    shell = _shell(Path(args.ion_root))
    out = scan_reduced_runs(shell, limit=args.limit)
    ledger_rel = (
        "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.model_routing_and_reasoning_economics/REDUCED_STATE_WORK_LEDGER.candidate.json"
    )
    if args.write:
        ledger_path = shell / ledger_rel
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        receipt_dir = shell / (
            "ION/05_context/current/domain_weaver/candidate_founding_domains/"
            "domain.model_routing_and_reasoning_economics/receipts"
        )
        receipt_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        receipt_path = receipt_dir / f"REDUCED_STATE_LEDGER_SCAN_{stamp}.candidate.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "schema_id": "ion.reduced_state_ledger_scan_receipt.v0_1_candidate",
                    "ledger_path": ledger_rel,
                    "entry_count": out.get("entry_count"),
                    "absence_findings": out.get("absence_findings"),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        if out.get("absence_findings"):
            alarm_dir = (
                shell
                / "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                "domain.model_routing_and_reasoning_economics"
            )
            alarm_dir.mkdir(parents=True, exist_ok=True)
            alarm_path = alarm_dir / "REDUCED-STATE-LEDGER-ABSENCE.candidate.json"
            alarm_path.write_text(
                json.dumps(
                    {
                        "schema_id": "ion.domain_conformance_absence_alarm.v0_1_candidate",
                        "signal_id": "REDUCED_STATE_LEDGER_ABSENCE",
                        "findings": out.get("absence_findings"),
                        "blocking_gate": False,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
    if args.json:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
