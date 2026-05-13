#!/usr/bin/env python3
"""
Run and compare reproducible AIM-OS benchmark packs for external evaluation.

Primary goals:
1. Execute a manifest-driven benchmark profile for a chosen variant.
2. Emit stable, machine-readable run artifacts (JSON + raw task logs).
3. Compare baseline vs AIM-OS-assisted runs with explicit delta reporting.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT_DIR / "benchmarks" / "openai_eval" / "benchmark_manifest.json"
DEFAULT_RESULTS_DIR = ROOT_DIR / "benchmarks" / "openai_eval" / "results"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_run_id(variant: str, profile: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{variant}_{profile}"


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _parse_env_overrides(items: List[str]) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --set-env value '{item}'. Expected KEY=VALUE.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --set-env value '{item}'. Empty key.")
        env[key] = value
    return env


def _build_run_env(extra: Dict[str, str]) -> Dict[str, str]:
    env = dict(os.environ)
    package_path = str(ROOT_DIR / "packages")
    root_path = str(ROOT_DIR)
    current = env.get("PYTHONPATH", "")
    if current:
        env["PYTHONPATH"] = os.pathsep.join([root_path, package_path, current])
    else:
        env["PYTHONPATH"] = os.pathsep.join([root_path, package_path])
    env.update(extra)
    return env


def _extract_count(text: str, label: str) -> int:
    matches = re.findall(rf"(\d+)\s+{re.escape(label)}", text)
    return int(matches[-1]) if matches else 0


def _parse_pytest_summary(output: str) -> Dict[str, int]:
    return {
        "passed": _extract_count(output, "passed"),
        "failed": _extract_count(output, "failed"),
        "skipped": _extract_count(output, "skipped"),
        "errors": _extract_count(output, "errors"),
        "warnings": _extract_count(output, "warnings"),
        "xfailed": _extract_count(output, "xfailed"),
        "xpassed": _extract_count(output, "xpassed"),
    }


def _parse_json_stdout(output: str) -> Dict[str, Any]:
    text = output.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass

    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        if not (line.startswith("{") or line.startswith("[")):
            continue
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                return data
        except Exception:
            continue
    return {}


def _resolve_command(
    command_tokens: List[str],
    *,
    python_exe: str,
    workspace: Path,
    run_dir: Path,
    task_output: Path | None,
) -> List[str]:
    values = {
        "python": python_exe,
        "workspace": str(workspace),
        "results_dir": str(run_dir),
        "task_output": str(task_output) if task_output else "",
    }
    resolved: List[str] = []
    for token in command_tokens:
        resolved.append(token.format(**values))
    return resolved


def _run_command(
    cmd: List[str],
    *,
    env: Dict[str, str],
    timeout_seconds: int,
) -> Dict[str, Any]:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_seconds,
        check=False,
    )
    duration = round(time.time() - started, 3)
    combined_output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return {
        "returncode": proc.returncode,
        "duration_seconds": duration,
        "stdout_tail": (proc.stdout or "").splitlines()[-40:],
        "stderr_tail": (proc.stderr or "").splitlines()[-40:],
        "combined_output": combined_output,
    }


def _task_metric_extractors(task_id: str, output_json: Dict[str, Any]) -> Dict[str, float]:
    metrics: Dict[str, float] = {}

    if task_id.startswith("hhni_perf"):
        results = output_json.get("results", {})
        cmc = results.get("atom_creation_cmc", {})
        hhni = results.get("atom_creation_hhni", {})
        metrics["cmc_write_p99_ms"] = float(cmc.get("p99_ms", 0.0))
        metrics["cmc_write_error_rate"] = float(cmc.get("error_rate", 0.0))
        metrics["hhni_write_p99_ms"] = float(hhni.get("p99_ms", 0.0))
        metrics["hhni_write_error_rate"] = float(hhni.get("error_rate", 0.0))

    if task_id.startswith("hhni_retrieval"):
        results = output_json.get("results", {})
        metrics["hhni_retrieval_p95_ms"] = float(results.get("p95_latency_ms", 0.0))
        metrics["hhni_retrieval_mean_relevance"] = float(results.get("mean_relevance", 0.0))
        metrics["hhni_retrieval_p99_ms"] = float(results.get("p99_latency_ms", 0.0))

    return metrics


def _aggregate_run(task_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    pytest_totals = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "warnings": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    command_failures = 0
    duration_seconds = 0.0
    perf: Dict[str, float] = {}

    for task in task_results:
        duration_seconds += float(task.get("duration_seconds", 0.0))
        if task.get("returncode", 0) != 0:
            command_failures += 1

        parsed = task.get("parsed", {})
        if task.get("parse") == "pytest":
            for key in pytest_totals:
                pytest_totals[key] += int(parsed.get(key, 0))

        for key, value in task.get("extracted_metrics", {}).items():
            perf[key] = float(value)

    return {
        "commands_total": len(task_results),
        "commands_failed": command_failures,
        "commands_passed": len(task_results) - command_failures,
        "duration_seconds_total": round(duration_seconds, 3),
        "pytest_totals": pytest_totals,
        "performance_metrics": perf,
    }


def run_profile(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).resolve()
    manifest = _read_json(manifest_path)
    profiles = manifest.get("profiles", {})

    if args.profile not in profiles:
        valid = ", ".join(sorted(profiles.keys()))
        raise ValueError(f"Profile '{args.profile}' not found. Valid profiles: {valid}")

    run_id = _safe_run_id(args.variant, args.profile)
    run_dir = Path(args.out_dir).resolve() / run_id
    logs_dir = run_dir / "logs"
    artifacts_dir = run_dir / "artifacts"
    logs_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    env_overrides = _parse_env_overrides(args.set_env)
    run_env = _build_run_env(env_overrides)
    python_exe = args.python_exe or sys.executable

    tasks = profiles[args.profile]
    task_results: List[Dict[str, Any]] = []

    print(f"[INFO] Run ID: {run_id}")
    print(f"[INFO] Profile: {args.profile}")
    print(f"[INFO] Variant: {args.variant}")
    print(f"[INFO] Tasks: {len(tasks)}")
    print(f"[INFO] Output: {run_dir}")
    if args.dry_run:
        print("[INFO] Dry run enabled; commands will not execute.")

    for index, task in enumerate(tasks, 1):
        task_id = task["id"]
        timeout_seconds = int(task.get("timeout_seconds", 1800))
        parse_mode = task.get("parse", "none")
        output_json_rel = task.get("output_json")
        task_output = (run_dir / output_json_rel) if output_json_rel else None
        if task_output:
            task_output.parent.mkdir(parents=True, exist_ok=True)

        cmd = _resolve_command(
            task["command"],
            python_exe=python_exe,
            workspace=ROOT_DIR,
            run_dir=run_dir,
            task_output=task_output,
        )

        print(f"[TASK {index}/{len(tasks)}] {task_id}: {' '.join(cmd)}")

        if args.dry_run:
            task_record = {
                "id": task_id,
                "name": task.get("name", task_id),
                "command": cmd,
                "parse": parse_mode,
                "timeout_seconds": timeout_seconds,
                "returncode": 0,
                "duration_seconds": 0.0,
                "parsed": {},
                "stdout_tail": [],
                "stderr_tail": [],
                "not_executed": True,
                "log_path": str(logs_dir / f"{task_id}.log"),
                "output_json_path": str(task_output) if task_output else None,
                "output_json_loaded": False,
                "extracted_metrics": {},
            }
            task_results.append(task_record)
            continue

        result = _run_command(cmd, env=run_env, timeout_seconds=timeout_seconds)
        combined_output = result["combined_output"]

        log_path = logs_dir / f"{task_id}.log"
        log_path.write_text(combined_output, encoding="utf-8")

        if parse_mode == "pytest":
            parsed = _parse_pytest_summary(combined_output)
        elif parse_mode == "json_stdout":
            parsed = _parse_json_stdout(combined_output)
        else:
            parsed = {}

        output_json_loaded = False
        output_json_payload: Dict[str, Any] = {}
        extracted_metrics: Dict[str, float] = {}
        if task_output and task_output.exists():
            try:
                output_json_payload = _read_json(task_output)
                output_json_loaded = True
                extracted_metrics = _task_metric_extractors(task_id, output_json_payload)
            except Exception:
                output_json_loaded = False

        task_record = {
            "id": task_id,
            "name": task.get("name", task_id),
            "command": cmd,
            "parse": parse_mode,
            "timeout_seconds": timeout_seconds,
            "returncode": result["returncode"],
            "duration_seconds": result["duration_seconds"],
            "parsed": parsed,
            "stdout_tail": result["stdout_tail"],
            "stderr_tail": result["stderr_tail"],
            "not_executed": False,
            "log_path": str(log_path),
            "output_json_path": str(task_output) if task_output else None,
            "output_json_loaded": output_json_loaded,
            "extracted_metrics": extracted_metrics,
        }
        task_results.append(task_record)

    aggregate = _aggregate_run(task_results)
    run_payload = {
        "run_id": run_id,
        "generated_utc": _utc_now(),
        "repo_root": str(ROOT_DIR),
        "manifest_path": str(manifest_path),
        "manifest_name": manifest.get("name", ""),
        "profile": args.profile,
        "variant": args.variant,
        "notes": args.notes or "",
        "dry_run": bool(args.dry_run),
        "python_exe": python_exe,
        "env_overrides": env_overrides,
        "tasks": task_results,
        "aggregate": aggregate,
    }

    run_json_path = run_dir / "run.json"
    _write_json(run_json_path, run_payload)

    print(f"[OK] Wrote run artifact: {run_json_path}")
    print(
        "[SUMMARY] "
        f"commands_failed={aggregate['commands_failed']} "
        f"pytest_failed={aggregate['pytest_totals']['failed']} "
        f"pytest_warnings={aggregate['pytest_totals']['warnings']}"
    )
    return 0


def _compare_metric(
    name: str,
    baseline_value: float,
    candidate_value: float,
) -> Dict[str, Any]:
    lower_is_better = {
        "cmc_write_p99_ms",
        "cmc_write_error_rate",
        "hhni_write_p99_ms",
        "hhni_write_error_rate",
        "hhni_retrieval_p95_ms",
        "hhni_retrieval_p99_ms",
    }
    higher_is_better = {
        "hhni_retrieval_mean_relevance",
    }

    delta = candidate_value - baseline_value
    if name in lower_is_better:
        improved = delta < 0
    elif name in higher_is_better:
        improved = delta > 0
    else:
        improved = False

    return {
        "metric": name,
        "baseline": baseline_value,
        "candidate": candidate_value,
        "delta": delta,
        "improved": improved,
    }


def _build_comparison_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# OpenAI Eval Pack Comparison")
    lines.append("")
    lines.append(f"- Generated UTC: {report['generated_utc']}")
    lines.append(f"- Baseline run: `{report['baseline_run_id']}`")
    lines.append(f"- Candidate run: `{report['candidate_run_id']}`")
    lines.append(f"- Profile: `{report['profile']}`")
    lines.append(f"- Verdict: `{report['verdict']}`")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    lines.append("| Metric | Baseline | Candidate | Delta |")
    lines.append("|---|---:|---:|---:|")
    for row in report["aggregate_rows"]:
        lines.append(f"| {row['metric']} | {row['baseline']} | {row['candidate']} | {row['delta']} |")

    lines.append("")
    lines.append("## Performance Deltas")
    lines.append("")
    if report["performance_rows"]:
        lines.append("| Metric | Baseline | Candidate | Delta | Improved |")
        lines.append("|---|---:|---:|---:|---|")
        for row in report["performance_rows"]:
            lines.append(
                f"| {row['metric']} | {row['baseline']:.6f} | {row['candidate']:.6f} | "
                f"{row['delta']:+.6f} | {str(row['improved'])} |"
            )
    else:
        lines.append("No overlapping performance metrics were found between runs.")

    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Type | Passed | Details |")
    lines.append("|---|---|---|---|")
    for check in report["checks"]:
        lines.append(f"| {check['name']} | {check.get('type', 'advisory')} | {str(check['passed'])} | {check['details']} |")
    lines.append("")
    return "\n".join(lines)


def compare_runs(args: argparse.Namespace) -> int:
    baseline_path = Path(args.baseline).resolve()
    candidate_path = Path(args.candidate).resolve()
    baseline = _read_json(baseline_path)
    candidate = _read_json(candidate_path)

    base_agg = baseline.get("aggregate", {})
    cand_agg = candidate.get("aggregate", {})

    base_py = base_agg.get("pytest_totals", {})
    cand_py = cand_agg.get("pytest_totals", {})

    aggregate_rows = [
        {
            "metric": "commands_failed",
            "baseline": int(base_agg.get("commands_failed", 0)),
            "candidate": int(cand_agg.get("commands_failed", 0)),
            "delta": int(cand_agg.get("commands_failed", 0)) - int(base_agg.get("commands_failed", 0)),
        },
        {
            "metric": "pytest_passed",
            "baseline": int(base_py.get("passed", 0)),
            "candidate": int(cand_py.get("passed", 0)),
            "delta": int(cand_py.get("passed", 0)) - int(base_py.get("passed", 0)),
        },
        {
            "metric": "pytest_failed",
            "baseline": int(base_py.get("failed", 0)),
            "candidate": int(cand_py.get("failed", 0)),
            "delta": int(cand_py.get("failed", 0)) - int(base_py.get("failed", 0)),
        },
        {
            "metric": "pytest_warnings",
            "baseline": int(base_py.get("warnings", 0)),
            "candidate": int(cand_py.get("warnings", 0)),
            "delta": int(cand_py.get("warnings", 0)) - int(base_py.get("warnings", 0)),
        },
        {
            "metric": "duration_seconds_total",
            "baseline": float(base_agg.get("duration_seconds_total", 0.0)),
            "candidate": float(cand_agg.get("duration_seconds_total", 0.0)),
            "delta": round(float(cand_agg.get("duration_seconds_total", 0.0)) - float(base_agg.get("duration_seconds_total", 0.0)), 3),
        },
    ]

    base_perf = base_agg.get("performance_metrics", {})
    cand_perf = cand_agg.get("performance_metrics", {})
    shared_perf = sorted(set(base_perf.keys()) & set(cand_perf.keys()))
    perf_rows = [
        _compare_metric(name, float(base_perf[name]), float(cand_perf[name]))
        for name in shared_perf
    ]

    hard_checks = [
        {
            "name": "candidate has zero command failures",
            "passed": int(cand_agg.get("commands_failed", 0)) == 0,
            "type": "hard_gate",
            "details": f"commands_failed={cand_agg.get('commands_failed', 0)}",
        },
        {
            "name": "candidate pytest failures <= baseline",
            "passed": int(cand_py.get("failed", 0)) <= int(base_py.get("failed", 0)),
            "type": "hard_gate",
            "details": f"baseline={base_py.get('failed', 0)} candidate={cand_py.get('failed', 0)}",
        },
        {
            "name": "candidate pytest warnings <= baseline",
            "passed": int(cand_py.get("warnings", 0)) <= int(base_py.get("warnings", 0)),
            "type": "hard_gate",
            "details": f"baseline={base_py.get('warnings', 0)} candidate={cand_py.get('warnings', 0)}",
        },
    ]
    perf_checks = []
    for row in perf_rows:
        perf_checks.append(
            {
                "name": f"performance metric improved: {row['metric']}",
                "passed": bool(row["improved"]),
                "type": "advisory",
                "details": f"baseline={row['baseline']:.6f} candidate={row['candidate']:.6f} delta={row['delta']:+.6f}",
            }
        )

    checks = hard_checks + perf_checks
    verdict = "pass" if all(item["passed"] for item in hard_checks) else "fail"

    comparison = {
        "generated_utc": _utc_now(),
        "baseline_run_id": baseline.get("run_id"),
        "candidate_run_id": candidate.get("run_id"),
        "profile": candidate.get("profile", ""),
        "baseline_path": str(baseline_path),
        "candidate_path": str(candidate_path),
        "aggregate_rows": aggregate_rows,
        "performance_rows": perf_rows,
        "checks": checks,
        "hard_gate_passed": all(item["passed"] for item in hard_checks),
        "performance_improved_count": sum(1 for item in perf_checks if item["passed"]),
        "performance_metric_count": len(perf_checks),
        "verdict": verdict,
    }

    out_dir = Path(args.out_dir).resolve() if args.out_dir else candidate_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "comparison.json"
    out_md = out_dir / "comparison.md"
    _write_json(out_json, comparison)
    out_md.write_text(_build_comparison_markdown(comparison), encoding="utf-8")

    print(f"[OK] Wrote comparison JSON: {out_json}")
    print(f"[OK] Wrote comparison Markdown: {out_md}")
    print(f"[SUMMARY] verdict={verdict}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run/compare AIM-OS OpenAI benchmark pack.")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Execute benchmark profile and emit run artifact.")
    run_p.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to benchmark manifest JSON.")
    run_p.add_argument("--profile", default="smoke", help="Manifest profile to execute.")
    run_p.add_argument("--variant", default="baseline", help="Variant label (e.g., baseline, aimos_assisted).")
    run_p.add_argument("--out-dir", default=str(DEFAULT_RESULTS_DIR), help="Directory for run artifacts.")
    run_p.add_argument("--python-exe", default="", help="Python executable path for task commands.")
    run_p.add_argument("--set-env", action="append", default=[], help="Environment override KEY=VALUE (repeatable).")
    run_p.add_argument("--notes", default="", help="Optional free-text notes embedded in run artifact.")
    run_p.add_argument("--dry-run", action="store_true", help="Resolve commands but do not execute.")
    run_p.set_defaults(func=run_profile)

    cmp_p = sub.add_parser("compare", help="Compare two run artifacts.")
    cmp_p.add_argument("--baseline", required=True, help="Path to baseline run.json.")
    cmp_p.add_argument("--candidate", required=True, help="Path to candidate run.json.")
    cmp_p.add_argument("--out-dir", default="", help="Output directory for comparison artifacts.")
    cmp_p.set_defaults(func=compare_runs)

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
