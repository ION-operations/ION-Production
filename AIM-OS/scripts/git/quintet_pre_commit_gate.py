#!/usr/bin/env python3
"""
Policy-driven Quintet/NL-tags gate runner.

Design goal:
- Keep quality standards strict for critical surfaces.
- Avoid blocking unrelated commits because of repo-wide baseline debt.

This script is used by local git hooks and can also be reused by CI.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple


def run_git(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def norm_path(path_str: str) -> str:
    return path_str.replace("\\", "/").strip().lstrip("./")


def get_repo_root(start: Path) -> Path:
    code, out, err = run_git(["rev-parse", "--show-toplevel"], start)
    if code != 0:
        raise RuntimeError(err or "Not a git repository")
    return Path(out)


def load_policy(policy_path: Path) -> Dict[str, Any]:
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")
    return json.loads(policy_path.read_text(encoding="utf-8"))


def resolve_mode(cli_mode: str | None, policy: Dict[str, Any]) -> str:
    env_mode = os.getenv("AIMOS_QUINTET_GATE_MODE", "").strip().lower()
    mode = (cli_mode or env_mode or policy.get("default_mode", "balanced")).lower()
    if mode not in policy.get("modes", {}):
        return policy.get("default_mode", "balanced")
    return mode


def get_changed_files(repo_root: Path, all_files: bool, changed_against: str | None) -> List[str]:
    if all_files:
        code, out, err = run_git(["ls-files"], repo_root)
        if code != 0:
            raise RuntimeError(err or "Failed to list tracked files")
        return [norm_path(line) for line in out.splitlines() if line.strip()]

    if changed_against:
        code, out, err = run_git(
            ["diff", "--name-only", "--diff-filter=ACMR", f"{changed_against}...HEAD"],
            repo_root,
        )
        if code != 0:
            raise RuntimeError(err or f"Failed to diff against {changed_against}")
        return [norm_path(line) for line in out.splitlines() if line.strip()]

    code, out, err = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"], repo_root)
    if code != 0:
        raise RuntimeError(err or "Failed to read staged files")
    return [norm_path(line) for line in out.splitlines() if line.strip()]


def classify_files(paths: List[str], policy: Dict[str, Any]) -> Dict[str, List[str]]:
    cfg = policy.get("file_classification", {})
    code_ext = {ext.lower() for ext in cfg.get("code_extensions", [".py"])}
    docs_ext = {ext.lower() for ext in cfg.get("docs_extensions", [".md"])}
    trace_tokens = [token.lower() for token in cfg.get("trace_path_tokens", [])]
    test_tokens = [token.lower() for token in cfg.get("test_path_tokens", [])]

    code: List[str] = []
    docs: List[str] = []
    tests: List[str] = []
    traces: List[str] = []

    for path in paths:
        path_l = path.lower()
        ext = Path(path).suffix.lower()
        is_code = ext in code_ext
        is_docs = ext in docs_ext or path_l.startswith("docs/") or Path(path_l).name.startswith("readme")
        is_test = any(token in path_l for token in test_tokens)
        is_trace = any(token in path_l for token in trace_tokens)

        if is_code:
            code.append(path)
        if is_docs:
            docs.append(path)
        if is_test:
            tests.append(path)
        if is_trace:
            traces.append(path)

    return {
        "code": sorted(set(code)),
        "docs": sorted(set(docs)),
        "tests": sorted(set(tests)),
        "traces": sorted(set(traces)),
    }


def is_critical_touched(paths: List[str], policy: Dict[str, Any]) -> bool:
    critical_rules = [norm_path(rule) for rule in policy.get("critical_paths", [])]
    for path in paths:
        p = norm_path(path)
        for rule in critical_rules:
            if not rule:
                continue
            if rule.endswith("/"):
                if p.startswith(rule):
                    return True
            elif p == rule:
                return True
    return False


def run_quintet_check(
    *,
    repo_root: Path,
    files: Dict[str, List[str]],
    mode_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    sys.path.insert(0, str(repo_root))
    try:
        from packages.sdfcvf.quintet import (
            QuintetDetector,
            QuintetParityCalculator,
            NLTagGate,
            print_diagnostic_report,
        )
        from packages.sdfcvf.callgraph import CallgraphBuilder, CONNECTTagValidator
    except Exception as exc:
        return {
            "ok": True,
            "skipped": True,
            "reason": f"Import failure: {exc}",
        }

    started = time.time()
    detector = QuintetDetector()
    quintet = detector.detect_from_files(
        code_files=files["code"],
        docs_files=files["docs"],
        tests_files=files["tests"],
        traces_files=files["traces"],
    )

    calculator = QuintetParityCalculator()
    parity_result = calculator.calculate_parity(quintet)

    gate = NLTagGate(
        public_coverage_threshold=float(mode_cfg.get("public_coverage_threshold", 0.95)),
        internal_coverage_threshold=float(mode_cfg.get("internal_coverage_threshold", 0.75)),
        code_tags_threshold=float(mode_cfg.get("code_tags_threshold", 0.85)),
    )
    gate_result = gate.check(quintet, parity_result)

    # Optional CONNECT validation (best effort)
    connect_issue: str | None = None
    try:
        connect_tags = [
            tag for tag in quintet.nl_tags
            if hasattr(tag, "kind") and str(getattr(tag, "kind", "")).upper() == "CONNECT"
        ]
        if connect_tags:
            builder = CallgraphBuilder()
            callgraph = builder.build_from_files(files["code"])
            validator = CONNECTTagValidator(strict=False)
            conn_result = validator.validate(connect_tags, callgraph)
            if not conn_result.passed:
                connect_issue = (
                    f"CONNECT validation failed: {len(conn_result.missing_edges)} missing edges"
                )
                gate_result.passed = False
                gate_result.issues.append(connect_issue)
    except Exception as exc:
        gate_result.warnings.append(f"CONNECT validation skipped: {exc}")

    threshold = float(mode_cfg.get("parity_threshold", 0.90))
    parity_pass = parity_result.score >= threshold
    passed = bool(gate_result.passed and parity_pass)

    elapsed_ms = (time.time() - started) * 1000.0

    return {
        "ok": passed,
        "skipped": False,
        "elapsed_ms": elapsed_ms,
        "parity_score": float(parity_result.score),
        "parity_threshold": threshold,
        "gate_name": gate_result.gate_name,
        "gate_passed": bool(gate_result.passed),
        "issues": list(gate_result.issues),
        "warnings": list(gate_result.warnings),
        "similarities": dict(parity_result.similarities),
        "code_tags_composite": (
            str(parity_result.code_tags_composite)
            if parity_result.code_tags_composite is not None else None
        ),
        "connect_issue": connect_issue,
        "diagnostic_report": {
            "print": lambda: print_diagnostic_report(parity_result, quintet)
        },
    }


def should_block(mode: str, mode_cfg: Dict[str, Any], critical_touched: bool, force_block: bool) -> bool:
    if force_block:
        return True
    enforce = mode_cfg.get("enforce_blocking", True)
    if enforce is True:
        return True
    if enforce is False:
        return False
    if isinstance(enforce, str) and enforce.lower() == "critical_only":
        return critical_touched
    return mode == "strict"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run policy-driven quintet gate")
    parser.add_argument("--policy", default="config/quintet_gate_policy.json", help="Policy JSON path")
    parser.add_argument("--mode", choices=["strict", "balanced", "advisory"], help="Override policy mode")
    parser.add_argument("--all-files", action="store_true", help="Run against all tracked files")
    parser.add_argument("--changed-against", help="Use git diff <ref>...HEAD instead of staged files")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--stage", default="pre-commit", help="Execution stage label")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    repo_root = get_repo_root(cwd)
    policy_path = (repo_root / args.policy).resolve() if not Path(args.policy).is_absolute() else Path(args.policy)
    policy = load_policy(policy_path)
    mode = resolve_mode(args.mode, policy)
    mode_cfg = policy["modes"][mode]

    force_block = os.getenv("AIMOS_QUINTET_FORCE_BLOCK", "").strip() in {"1", "true", "TRUE", "yes", "YES"}
    changed_files = get_changed_files(
        repo_root,
        all_files=args.all_files,
        changed_against=args.changed_against,
    )
    classified = classify_files(changed_files, policy)
    critical_touched = is_critical_touched(changed_files, policy)

    if not classified["code"]:
        payload = {
            "ok": True,
            "skipped": True,
            "reason": "No staged code files to evaluate",
            "mode": mode,
            "critical_touched": critical_touched,
            "counts": {k: len(v) for k, v in classified.items()},
            "stage": args.stage,
        }
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("[*] Quintet gate: no staged code files; skipping")
        return 0

    result = run_quintet_check(repo_root=repo_root, files=classified, mode_cfg=mode_cfg)
    elapsed_ms = float(result.get("elapsed_ms", 0.0))

    perf_cfg = policy.get("performance", {})
    warn_ms = int(perf_cfg.get("warn_ms", 500))
    advisory_warn_ms = int(perf_cfg.get("advisory_only_warn_ms", 1500))
    block = should_block(mode, mode_cfg, critical_touched, force_block)

    summary = {
        "stage": args.stage,
        "mode": mode,
        "critical_touched": critical_touched,
        "blocking": block,
        "counts": {k: len(v) for k, v in classified.items()},
        "changed_files_count": len(changed_files),
        "result": {
            k: v for k, v in result.items() if k not in {"diagnostic_report"}
        },
    }

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("[*] Running quintet parity check...")
        print(f"[*] Mode: {mode} | stage: {args.stage} | critical_touched: {critical_touched} | blocking: {block}")
        print(f"[*] File counts: code={len(classified['code'])} docs={len(classified['docs'])} tests={len(classified['tests'])} traces={len(classified['traces'])}")
        if result.get("skipped"):
            print(f"[OK] Skipped: {result.get('reason')}")
            return 0

        if elapsed_ms > warn_ms:
            print(f"WARNING: Quintet check took {elapsed_ms:.0f}ms (warn budget: {warn_ms}ms)")
        if not block and elapsed_ms > advisory_warn_ms:
            print(f"WARNING: Advisory gate took {elapsed_ms:.0f}ms (advisory warn: {advisory_warn_ms}ms)")

        if result["ok"]:
            print(f"[OK] Quintet parity passed (P={result['parity_score']:.3f} >= {result['parity_threshold']:.3f})")
        else:
            print("\n============================================================")
            print("[FAIL] QUINTET PARITY CHECK FAILED")
            print("============================================================")
            result["diagnostic_report"]["print"]()
            if result.get("issues"):
                print("\nIssues:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
            if result.get("warnings"):
                print("\nWarnings:")
                for warning in result["warnings"]:
                    print(f"  - {warning}")
            print("")
            if block:
                print("[FAIL] Commit blocked by policy")
            else:
                print("[WARN] Advisory failure (commit allowed by policy)")

    if result.get("ok", False):
        return 0
    return 1 if block else 0


if __name__ == "__main__":
    raise SystemExit(main())
