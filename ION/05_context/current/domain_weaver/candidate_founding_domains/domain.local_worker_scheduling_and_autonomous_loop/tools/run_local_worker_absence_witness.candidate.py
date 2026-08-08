#!/usr/bin/env python3
"""Candidate absence witness for domain.local_worker_scheduling_and_autonomous_loop.

Grade-only: never blocks. Writes LOCAL_WORKER_AUTOMATION_ABSENCE_SURFACE.candidate.json
so ignoring agents see loud absence flags on disk.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _root(ion_root: Path) -> Path:
    p = ion_root.resolve()
    return p.parent if p.name == "ION" else p


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


def run_witness(shell: Path, *, write: bool) -> dict:
    probes: list[dict] = []
    now = datetime.now(timezone.utc)

    last_loop = shell / "ION/05_context/current/LAST_ION_AUTONOMOUS_LOOP_RESULT.json"
    loop_age_s: float | None = None
    loop_status: str | None = None
    loop_idle_findings: list[dict] = []
    if last_loop.is_file():
        data = json.loads(last_loop.read_text(encoding="utf-8"))
        loop_status = str(data.get("status") or "")
        created = _parse_iso(str(data.get("created_at") or ""))
        if created:
            loop_age_s = (now - created).total_seconds()
        raw_findings = data.get("loop_absence_findings")
        if isinstance(raw_findings, list):
            loop_idle_findings = [f for f in raw_findings if isinstance(f, dict)]
    idle_streak_path = shell / "ION/05_context/current/autonomous_loop/LOOP_IDLE_STREAK.candidate.json"
    consecutive_idle = 0
    if idle_streak_path.is_file():
        try:
            streak_data = json.loads(idle_streak_path.read_text(encoding="utf-8"))
            consecutive_idle = int(streak_data.get("consecutive_idle_cycles") or 0)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            consecutive_idle = 0
    idle_alert_path = shell / "ION/05_context/current/autonomous_loop/LOOP_IDLE_ABSENCE_ALERT.candidate.json"
    idle_alert_active = False
    if idle_alert_path.is_file():
        try:
            alert_data = json.loads(idle_alert_path.read_text(encoding="utf-8"))
            idle_alert_active = bool(
                alert_data.get("finding_code") == "FINDING_AUTONOMOUS_LOOP_CONSECUTIVE_IDLE_CYCLES"
                or alert_data.get("alert_active") is not False
                and int(alert_data.get("consecutive_idle_cycles") or 0) >= 3
            )
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            idle_alert_active = False
    probes.append(
        {
            "probe_id": "local_autonomous_loop_consecutive_idle_cycles",
            "path": str(idle_streak_path.relative_to(shell)) if idle_streak_path.is_file() else idle_streak_path.as_posix(),
            "exists": idle_streak_path.is_file(),
            "consecutive_idle_cycles": consecutive_idle,
            "absence_present": consecutive_idle >= 3 or idle_alert_active or bool(loop_idle_findings),
            "detects_absence": True,
            "alert_path": idle_alert_path.as_posix(),
            "ignored_agent_sees": "NO_ACCEPTED_LOCAL_DELTA exit 0 but N consecutive idle cycles — loop idle streak absence alert.",
        }
    )
    probes.append(
        {
            "probe_id": "local_autonomous_loop_result",
            "path": str(last_loop.relative_to(shell)),
            "exists": last_loop.is_file(),
            "status": loop_status,
            "age_seconds": loop_age_s,
            "absence_present": not last_loop.is_file() or (loop_age_s is not None and loop_age_s > 86400),
            "ignored_agent_sees": "No LAST_ION_AUTONOMOUS_LOOP_RESULT or stale loop receipt — unwired ion_autonomous_loop.",
        }
    )

    steward_integrate_path = shell / "ION/04_packages/kernel/ion_steward_integrate.py"
    loop_write_disabled = False
    if steward_integrate_path.is_file():
        steward_text = steward_integrate_path.read_text(encoding="utf-8", errors="replace")
        loop_write_disabled = "legacy_return_write_disabled_use_proof_bound_exact_subset_api" in steward_text
    probes.append(
        {
            "probe_id": "local_autonomous_loop_steward_write_path",
            "path": str(steward_integrate_path.relative_to(shell)),
            "exists": steward_integrate_path.is_file(),
            "legacy_return_write_disabled_present": loop_write_disabled,
            "absence_present": loop_write_disabled,
            "detects_absence": True,
            "ignored_agent_sees": "steward_integrate_return(write=True) hard-disabled — loop guaranteed steps_integrated=0.",
            "problem_id": "P_LOOP_INTEGRATION_WRITE_DISABLE",
        }
    )

    tick_path = shell / "ION/05_context/current/autonomous_goals/scheduler/last_tick.candidate.json"
    tick_age_s: float | None = None
    tick_verdict: str | None = None
    if tick_path.is_file():
        tick = json.loads(tick_path.read_text(encoding="utf-8"))
        tick_verdict = str(tick.get("scheduler_status", {}).get("verdict") or tick.get("evaluation", {}).get("verdict") or "")
        created = _parse_iso(str(tick.get("created_at") or ""))
        if created:
            tick_age_s = (now - created).total_seconds()
    probes.append(
        {
            "probe_id": "scheduler_health_tick",
            "path": str(tick_path.relative_to(shell)),
            "exists": tick_path.is_file(),
            "verdict": tick_verdict,
            "age_seconds": tick_age_s,
            "absence_present": not tick_path.is_file() or (tick_age_s is not None and tick_age_s > 900),
            "ignored_agent_sees": "Health tick silent >15m — scheduler dead without this surface.",
        }
    )

    daemon_dir = shell / "ION/05_context/history/daemon_loop_receipts"
    daemon_count = len(list(daemon_dir.glob("*.json"))) if daemon_dir.is_dir() else 0
    probes.append(
        {
            "probe_id": "daemon_loop_receipts",
            "path": str(daemon_dir.relative_to(shell)),
            "receipt_count": daemon_count,
            "absence_present": daemon_count == 0,
            "ignored_agent_sees": "kernel_daemon_loop never produced receipts — production_daemon lane unwired.",
            "owning_domain_note": "domain.production_daemon_and_graph_event_runtime owns daemon_service install",
        }
    )

    drain_tick = shell / (
        "ION/05_context/current/domain_weaver/inter_domain_work_queue/"
        "LAST_DURABLE_SOS_DRAIN_TICK.candidate.json"
    )
    drain_age_s: float | None = None
    drain_verdict: str | None = None
    if drain_tick.is_file():
        drain_data = json.loads(drain_tick.read_text(encoding="utf-8"))
        drain_verdict = str(drain_data.get("verdict") or "")
        created = _parse_iso(str(drain_data.get("tick_at") or ""))
        if created:
            drain_age_s = (now - created).total_seconds()
    probes.append(
        {
            "probe_id": "durable_sos_spawn_queue_drain_tick",
            "path": str(drain_tick.relative_to(shell)),
            "exists": drain_tick.is_file(),
            "verdict": drain_verdict,
            "age_seconds": drain_age_s,
            "absence_present": not drain_tick.is_file()
            or (drain_age_s is not None and drain_age_s > 2700),
            "detects_absence": True,
            "ignored_agent_sees": "Durable SOS queue drain silent >45m — timer unwired or queue-only-growth failure.",
            "coordination": "kernel.ion_runtime_absence_probe + ion_sos_durable_inter_domain_spawn_queue.probe",
        }
    )

    absence_signal = shell / (
        "ION/05_context/current/domain_weaver/inter_domain_work_queue/"
        "DURABLE_QUEUE_ABSENCE_SIGNAL.candidate.json"
    )
    dq_pending: int | None = None
    if absence_signal.is_file():
        sig = json.loads(absence_signal.read_text(encoding="utf-8"))
        dq_pending = int(sig.get("pending_spawn_count") or 0)
    probes.append(
        {
            "probe_id": "durable_queue_depth_growth_only",
            "path": str(absence_signal.relative_to(shell)),
            "exists": absence_signal.is_file(),
            "pending_spawn_count": dq_pending,
            "absence_present": bool(dq_pending and dq_pending > 0 and drain_age_s is not None and drain_age_s > 2700),
            "detects_absence": True,
            "ignored_agent_sees": "Queue has pending rows but drain tick stale — fills without drains.",
        }
    )

    activation_dir = shell / "ION/05_context/current/autonomous_goals"
    activation_paths = sorted(activation_dir.glob("ACTIVATION_RECORD_HEALTH_TICK_*.candidate.json"))
    activation_expired = False
    activation_stale_superseded_live = False
    active_record_rel: str | None = None
    active_expires_at: str | None = None
    live_health_tick_records: list[Path] = []
    for act_path in activation_paths:
        if not act_path.is_file():
            continue
        act = json.loads(act_path.read_text(encoding="utf-8"))
        if str(act.get("status") or "") == "superseded" or act.get("superseded_by"):
            continue
        live_health_tick_records.append(act_path)
    activation_stale_superseded_live = len(live_health_tick_records) > 1
    if live_health_tick_records:
        act_path = live_health_tick_records[-1]
        act = json.loads(act_path.read_text(encoding="utf-8"))
        expires = _parse_iso(str(act.get("expires_at") or ""))
        active_record_rel = str(act_path.relative_to(shell))
        active_expires_at = str(act.get("expires_at") or "")
        if expires and expires < now:
            activation_expired = True
    activation_absence = activation_expired or activation_stale_superseded_live or active_record_rel is None
    activation_signal_rel = Path(
        "ION/05_context/current/autonomous_goals/ACTIVATION_RECORD_ABSENCE_SIGNAL.candidate.json"
    )
    if write:
        sig_payload = {
            "schema_id": "ion.autonomous_goals.activation_record_absence_signal.v0_1_candidate",
            "evaluated_at": _now(),
            "active_record_path": active_record_rel,
            "expires_at": active_expires_at,
            "activation_expired": activation_expired,
            "stale_superseded_record_live": activation_stale_superseded_live,
            "absence_present": activation_absence,
        }
        sig_out = shell / activation_signal_rel
        sig_out.parent.mkdir(parents=True, exist_ok=True)
        sig_out.write_text(json.dumps(sig_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    probes.append(
        {
            "probe_id": "activation_record_expiry",
            "path": activation_signal_rel.as_posix(),
            "active_record_path": active_record_rel,
            "expires_at": active_expires_at,
            "absence_present": activation_absence,
            "detects_absence": True,
            "ignored_agent_sees": "Health-tick activation expired or 20260724 still live without superseded — scheduler silence class P06.",
            "problem_id": "P06",
        }
    )

    srs_tick = shell / (
        "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.local_worker_scheduling_and_autonomous_loop/"
        "LAST_SELF_REPAIR_SUPERVISOR_SCHEDULER_TICK.candidate.json"
    )
    srs_age_s: float | None = None
    srs_verdict: str | None = None
    if srs_tick.is_file():
        srs_data = json.loads(srs_tick.read_text(encoding="utf-8"))
        srs_verdict = str(srs_data.get("verdict") or "")
        created = _parse_iso(str(srs_data.get("tick_at") or ""))
        if created:
            srs_age_s = (now - created).total_seconds()
    probes.append(
        {
            "probe_id": "self_repair_supervisor_scheduler_tick",
            "path": str(srs_tick.relative_to(shell)) if srs_tick.is_file() else srs_tick.as_posix(),
            "exists": srs_tick.is_file(),
            "verdict": srs_verdict,
            "age_seconds": srs_age_s,
            "absence_present": not srs_tick.is_file() or (srs_age_s is not None and srs_age_s > 21600),
            "detects_absence": True,
            "scheduler_entrypoint": (
                "candidate_founding_domains/domain.local_worker_scheduling_and_autonomous_loop/"
                "tools/run_self_repair_supervisor_scheduler_tick.candidate.py"
            ),
            "ignored_agent_sees": "GOAL_REGISTRY references kernel.ion_domain_weaver_self_repair_supervisor but no scheduler tick >6h — P13.",
            "problem_id": "P13",
        }
    )

    drain_timer_active: str | None = None
    try:
        proc = subprocess.run(
            ["systemctl", "--user", "is-active", "ion-durable-sos-spawn-queue-drain.timer"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        drain_timer_active = (proc.stdout or proc.stderr or "").strip() or f"exit_{proc.returncode}"
    except (OSError, subprocess.TimeoutExpired) as exc:
        drain_timer_active = f"probe_error:{type(exc).__name__}"
    drain_timer_probe_rel = Path(
        "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.local_worker_scheduling_and_autonomous_loop/"
        "LAST_DURABLE_DRAIN_TIMER_PROBE.candidate.json"
    )
    timer_unwired = drain_timer_active not in ("active", "activating")
    if write:
        timer_payload = {
            "schema_id": "ion.local_worker.durable_drain_timer_probe.v0_1_candidate",
            "evaluated_at": _now(),
            "systemd_unit": "ion-durable-sos-spawn-queue-drain.timer",
            "is_active": drain_timer_active,
            "candidate_unit_path": (
                "ION/05_context/current/domain_weaver/candidate_founding_domains/"
                "domain.local_worker_scheduling_and_autonomous_loop/components/"
                "ion-durable-sos-spawn-queue-drain.candidate.timer"
            ),
            "absence_present": timer_unwired,
            "problem_id": "P14",
        }
        timer_out = shell / drain_timer_probe_rel
        timer_out.parent.mkdir(parents=True, exist_ok=True)
        timer_out.write_text(json.dumps(timer_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    probes.append(
        {
            "probe_id": "durable_sos_drain_timer_systemd",
            "path": drain_timer_probe_rel.as_posix(),
            "is_active": drain_timer_active,
            "absence_present": timer_unwired,
            "detects_absence": True,
            "ignored_agent_sees": "Durable queue grows but user timer not active — install candidate .timer unit — P14.",
            "problem_id": "P14",
        }
    )

    cli_probe = shell / "ION/05_context/current/domain_weaver/spawn_dispatch/LAST_SPAWN_REQUEST_DISPATCHER_CLI_PROBE.candidate.json"
    cli_age_s: float | None = None
    if cli_probe.is_file():
        cli_data = json.loads(cli_probe.read_text(encoding="utf-8"))
        created = _parse_iso(str(cli_data.get("created_at") or ""))
        if created:
            cli_age_s = (now - created).total_seconds()
    probes.append(
        {
            "probe_id": "spawn_request_dispatcher_cli",
            "path": str(cli_probe.relative_to(shell)),
            "exists": cli_probe.is_file(),
            "age_seconds": cli_age_s,
            "absence_present": not cli_probe.is_file() or (cli_age_s is not None and cli_age_s > 86400),
            "detects_absence": True,
            "ignored_agent_sees": "No spawn_request_dispatcher CLI probe — kernel module had no python -m entrypoint.",
        }
    )

    mf_timer_active: str | None = None
    try:
        mf_proc = subprocess.run(
            ["systemctl", "--user", "is-active", "ion-mount-freshness-scheduler.timer"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        mf_timer_active = (mf_proc.stdout or mf_proc.stderr or "").strip() or f"exit_{mf_proc.returncode}"
    except (OSError, subprocess.TimeoutExpired) as exc:
        mf_timer_active = f"probe_error:{type(exc).__name__}"
    mf_timer_probe_rel = Path(
        "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.local_worker_scheduling_and_autonomous_loop/"
        "LAST_MOUNT_FRESHNESS_TIMER_PROBE.candidate.json"
    )
    mf_timer_unwired = mf_timer_active not in ("active", "activating")
    if write:
        mf_timer_payload = {
            "schema_id": "ion.local_worker.mount_freshness_timer_probe.v0_1_candidate",
            "evaluated_at": _now(),
            "systemd_unit": "ion-mount-freshness-scheduler.timer",
            "is_active": mf_timer_active,
            "candidate_unit_path": (
                "ION/05_context/current/domain_weaver/candidate_founding_domains/"
                "domain.local_worker_scheduling_and_autonomous_loop/components/"
                "ion-mount-freshness-scheduler.candidate.timer"
            ),
            "scheduler_tick_runner": "run_mount_freshness_scheduler_tick.candidate.py",
            "absence_present": mf_timer_unwired,
            "problem_id": "P27",
        }
        mf_timer_out = shell / mf_timer_probe_rel
        mf_timer_out.parent.mkdir(parents=True, exist_ok=True)
        mf_timer_out.write_text(json.dumps(mf_timer_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    probes.append(
        {
            "probe_id": "mount_freshness_scheduler_timer_systemd",
            "path": mf_timer_probe_rel.as_posix(),
            "is_active": mf_timer_active,
            "absence_present": mf_timer_unwired,
            "detects_absence": True,
            "ignored_agent_sees": "P27 mount freshness tick not on user timer — link candidate unit and enable — P27.",
            "problem_id": "P27",
            "scheduler_entrypoint": (
                "candidate_founding_domains/domain.context_mount_freshness_and_resolver/runtime/"
                "run_mount_freshness_scheduler_tick.candidate.py"
            ),
        }
    )

    al_timer_active: str | None = None
    try:
        al_proc = subprocess.run(
            ["systemctl", "--user", "is-active", "ion-autonomous-loop-local-worker.timer"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        al_timer_active = (al_proc.stdout or al_proc.stderr or "").strip() or f"exit_{al_proc.returncode}"
    except (OSError, subprocess.TimeoutExpired) as exc:
        al_timer_active = f"probe_error:{type(exc).__name__}"
    al_timer_probe_rel = Path(
        "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.local_worker_scheduling_and_autonomous_loop/"
        "LAST_AUTONOMOUS_LOOP_LOCAL_WORKER_TIMER_PROBE.candidate.json"
    )
    al_timer_unwired = al_timer_active not in ("active", "activating")
    if write:
        al_timer_payload = {
            "schema_id": "ion.local_worker.autonomous_loop_timer_probe.v0_1_candidate",
            "evaluated_at": _now(),
            "systemd_unit": "ion-autonomous-loop-local-worker.timer",
            "is_active": al_timer_active,
            "candidate_unit_path": (
                "ION/05_context/current/domain_weaver/candidate_founding_domains/"
                "domain.local_worker_scheduling_and_autonomous_loop/components/"
                "ion-autonomous-loop-local-worker.candidate.timer"
            ),
            "kernel_module": "ion_autonomous_loop",
            "absence_present": al_timer_unwired,
            "problem_id": "P28",
        }
        al_timer_out = shell / al_timer_probe_rel
        al_timer_out.parent.mkdir(parents=True, exist_ok=True)
        al_timer_out.write_text(json.dumps(al_timer_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    probes.append(
        {
            "probe_id": "autonomous_loop_local_worker_timer_systemd",
            "path": al_timer_probe_rel.as_posix(),
            "is_active": al_timer_active,
            "absence_present": al_timer_unwired,
            "detects_absence": True,
            "ignored_agent_sees": "ion_autonomous_loop unwired — link candidate local_worker timer and enable — P28.",
            "problem_id": "P28",
            "scheduler_entrypoint": "python3 -S -m kernel.ion_autonomous_loop",
        }
    )

    absence_count = sum(1 for p in probes if p.get("absence_present"))
    surface = {
        "schema_id": "ion.local_worker_automation_absence_surface.v0_1_candidate",
        "domain_id": "domain.local_worker_scheduling_and_autonomous_loop",
        "evaluated_at": _now(),
        "verdict": "ABSENCE_SIGNAL_PRESENT" if absence_count else "MECHANISMS_RECENT",
        "absence_probe_count": absence_count,
        "probes": probes,
        "witness_module": "candidate_founding_domains/domain.local_worker_scheduling_and_autonomous_loop/tools/run_local_worker_absence_witness.candidate.py",
        "posture": "candidate_only",
    }
    out_rel = Path(
        "ION/05_context/current/domain_weaver/candidate_founding_domains/domain.local_worker_scheduling_and_autonomous_loop/LOCAL_WORKER_AUTOMATION_ABSENCE_SURFACE.candidate.json"
    )
    if write:
        out_path = shell / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(surface, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        surface["surface_path"] = str(out_rel)
    return surface


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    shell = _root(Path(args.ion_root))
    result = run_witness(shell, write=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict", "UNKNOWN"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
