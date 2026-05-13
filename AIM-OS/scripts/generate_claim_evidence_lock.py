#!/usr/bin/env python3
"""
Generate claim-to-evidence lock artifacts from live command outputs.

Outputs:
- 09_CLAIM_EVIDENCE_LOCK.json
- 09_CLAIM_EVIDENCE_LOCK.md
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
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_audit_dir() -> Path:
    candidates = sorted(ROOT_DIR.glob("audit/*_aimos_restart_audit"))
    if candidates:
        return candidates[-1]
    return ROOT_DIR / "audit"


def _run_command(
    cmd: List[str],
    *,
    env: Dict[str, str] | None = None,
    timeout_seconds: int = 1800,
) -> Dict[str, Any]:
    start = time.time()
    proc = subprocess.run(
        cmd,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_seconds,
        check=False,
    )
    duration = round(time.time() - start, 3)
    combined = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "duration_seconds": duration,
        "stdout_tail": (proc.stdout or "").splitlines()[-40:],
        "stderr_tail": (proc.stderr or "").splitlines()[-40:],
        "combined_output": combined,
    }


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


def _parse_mcp_parity(output: str) -> Dict[str, Any]:
    try:
        payload = json.loads(output.strip())
        return {
            "listed_count": payload.get("listed_count"),
            "callable_count": payload.get("callable_count"),
            "parity_ok": bool(payload.get("parity_ok")),
        }
    except Exception:
        return {
            "listed_count": None,
            "callable_count": None,
            "parity_ok": False,
        }


def _parse_source_of_truth_preview(output: str) -> Dict[str, Any]:
    def parse_int(name: str) -> int | None:
        match = re.search(rf"{re.escape(name)}:\s*(\d+)", output)
        return int(match.group(1)) if match else None

    parity_match = re.search(r"MCP Parity OK:\s*(True|False)", output)
    parity_ok = parity_match.group(1) == "True" if parity_match else False
    return {
        "mcp_listed": parse_int("MCP Tools (listed)"),
        "mcp_callable": parse_int("MCP Tools (callable)"),
        "mcp_parity_ok": parity_ok,
        "systems": parse_int("Systems"),
        "documentation_files": parse_int("Documentation Files"),
        "test_files": parse_int("Test Files"),
    }


def _build_claims(evidence: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    claims: List[Dict[str, Any]] = []

    if "mcp_parity" in evidence:
        mcp = evidence["mcp_parity"]["parsed"]
        claims.append(
            {
                "id": "CLM-001",
                "statement": "MCP tools/list surface matches tools/call surface.",
                "status": "supported" if mcp.get("parity_ok") else "unsupported",
                "evidence_command_id": "mcp_parity",
                "observed": f"listed={mcp.get('listed_count')} callable={mcp.get('callable_count')} parity_ok={mcp.get('parity_ok')}",
            }
        )

    if "tagged_policy" in evidence:
        tagged = evidence["tagged_policy"]["parsed"]
        claims.append(
            {
                "id": "CLM-002",
                "statement": "Coverage policy excludes tagged mirror files from coverage parsing scope.",
                "status": "supported" if tagged.get("policy_ok") else "unsupported",
                "evidence_command_id": "tagged_policy",
                "observed": f"policy_ok={tagged.get('policy_ok')} tagged_count={tagged.get('tagged_file_count')} parse_failures={tagged.get('parse_failure_count')}",
            }
        )

    if "apoe_tests" in evidence:
        apoe = evidence["apoe_tests"]["parsed"]
        claims.append(
            {
                "id": "CLM-003",
                "statement": "APOE package test suite passes in controlled environment.",
                "status": "supported" if apoe["failed"] == 0 and apoe["errors"] == 0 and apoe["passed"] > 0 else "unsupported",
                "evidence_command_id": "apoe_tests",
                "observed": f"passed={apoe['passed']} failed={apoe['failed']} skipped={apoe['skipped']} errors={apoe['errors']}",
            }
        )

    if "hhni_tests" in evidence:
        hhni = evidence["hhni_tests"]["parsed"]
        claims.append(
            {
                "id": "CLM-004",
                "statement": "HHNI package test suite passes in controlled environment.",
                "status": "supported" if hhni["failed"] == 0 and hhni["errors"] == 0 and hhni["passed"] > 0 else "unsupported",
                "evidence_command_id": "hhni_tests",
                "observed": f"passed={hhni['passed']} failed={hhni['failed']} skipped={hhni['skipped']} errors={hhni['errors']}",
            }
        )

    if "seg_tests" in evidence:
        seg = evidence["seg_tests"]["parsed"]
        claims.append(
            {
                "id": "CLM-005",
                "statement": "SEG package test suite passes in controlled environment.",
                "status": "supported" if seg["failed"] == 0 and seg["errors"] == 0 and seg["passed"] > 0 else "unsupported",
                "evidence_command_id": "seg_tests",
                "observed": f"passed={seg['passed']} failed={seg['failed']} errors={seg['errors']}",
            }
        )

    if "sdfcvf_tests" in evidence:
        sdfcvf = evidence["sdfcvf_tests"]["parsed"]
        claims.append(
            {
                "id": "CLM-006",
                "statement": "SDF-CVF package test suite passes in controlled environment.",
                "status": "supported" if sdfcvf["failed"] == 0 and sdfcvf["errors"] == 0 and sdfcvf["passed"] > 0 else "unsupported",
                "evidence_command_id": "sdfcvf_tests",
                "observed": f"passed={sdfcvf['passed']} failed={sdfcvf['failed']} warnings={sdfcvf['warnings']}",
            }
        )

    if "mcp_parity_tests" in evidence:
        parity_tests = evidence["mcp_parity_tests"]["parsed"]
        claims.append(
            {
                "id": "CLM-007",
                "statement": "MCP parity pytest guardrails are passing.",
                "status": "supported" if parity_tests["failed"] == 0 and parity_tests["errors"] == 0 and parity_tests["passed"] > 0 else "unsupported",
                "evidence_command_id": "mcp_parity_tests",
                "observed": f"passed={parity_tests['passed']} failed={parity_tests['failed']} errors={parity_tests['errors']}",
            }
        )

    if "source_of_truth" in evidence:
        detector = evidence["source_of_truth"]["parsed"]
        claims.append(
            {
                "id": "CLM-008",
                "statement": "Source-of-truth dry-run reports parity and current inventory metrics.",
                "status": "supported" if detector.get("mcp_parity_ok") else "unsupported",
                "evidence_command_id": "source_of_truth",
                "observed": (
                    f"mcp_listed={detector.get('mcp_listed')} "
                    f"mcp_callable={detector.get('mcp_callable')} "
                    f"systems={detector.get('systems')} docs={detector.get('documentation_files')} tests={detector.get('test_files')}"
                ),
            }
        )

    return claims


def _render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Claim-Evidence Lock")
    lines.append("")
    lines.append(f"- Generated UTC: {report['generated_utc']}")
    lines.append(f"- Repo root: `{report['repo_root']}`")
    lines.append(f"- Controlled env: `PYTHONPATH=.;packages`")
    lines.append("")
    lines.append("## Claims")
    lines.append("")
    lines.append("| ID | Statement | Status | Observed | Evidence Command |")
    lines.append("|---|---|---|---|---|")
    for claim in report["claims"]:
        lines.append(
            f"| {claim['id']} | {claim['statement']} | {claim['status']} | {claim['observed']} | `{claim['evidence_command_id']}` |"
        )

    lines.append("")
    lines.append("## Command Evidence")
    lines.append("")
    for command_id, payload in report["evidence"].items():
        lines.append(f"### {command_id}")
        lines.append(f"- Command: `{payload['command']}`")
        lines.append(f"- Return code: `{payload['returncode']}`")
        lines.append(f"- Duration seconds: `{payload['duration_seconds']}`")
        lines.append(f"- Parsed summary: `{json.dumps(payload['parsed'], sort_keys=True)}`")
        lines.append("- Stdout tail:")
        lines.append("```text")
        lines.extend(payload["stdout_tail"][-20:] or ["<no output>"])
        lines.append("```")
        if payload["stderr_tail"]:
            lines.append("- Stderr tail:")
            lines.append("```text")
            lines.extend(payload["stderr_tail"][-20:])
            lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate claim-to-evidence lock report")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=_default_audit_dir(),
        help="Output directory for generated artifacts",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip long package test suites and only run parity/policy checks",
    )
    args = parser.parse_args()

    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    path_entries = [".", "packages"]
    if existing_pythonpath:
        path_entries.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(path_entries)

    command_plan: Dict[str, List[str]] = {
        "mcp_parity": [sys.executable, "scripts/check_mcp_tool_parity.py"],
        "source_of_truth": [
            sys.executable,
            "scripts/detect_source_of_truth.py",
            "--dry-run",
            "--check-mcp-parity",
        ],
        "tagged_policy": [sys.executable, "scripts/check_tagged_coverage_policy.py"],
        "mcp_parity_tests": [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_mcp_tool_surface_parity.py",
            "-q",
            "-o",
            "addopts=''",
        ],
    }

    if not args.quick:
        command_plan.update(
            {
                "apoe_tests": [
                    sys.executable,
                    "-m",
                    "pytest",
                    "packages/apoe/tests",
                    "-q",
                    "-o",
                    "addopts=''",
                ],
                "hhni_tests": [
                    sys.executable,
                    "-m",
                    "pytest",
                    "packages/hhni/tests",
                    "-q",
                    "-o",
                    "addopts=''",
                ],
                "seg_tests": [
                    sys.executable,
                    "-m",
                    "pytest",
                    "packages/seg/tests",
                    "-q",
                    "-o",
                    "addopts=''",
                ],
                "sdfcvf_tests": [
                    sys.executable,
                    "-m",
                    "pytest",
                    "packages/sdfcvf/tests",
                    "-q",
                    "-o",
                    "addopts=''",
                ],
            }
        )

    evidence: Dict[str, Dict[str, Any]] = {}
    for command_id, cmd in command_plan.items():
        result = _run_command(cmd, env=env)
        parsed: Dict[str, Any]
        if command_id == "mcp_parity":
            parsed = _parse_mcp_parity(result["combined_output"])
        elif command_id == "source_of_truth":
            parsed = _parse_source_of_truth_preview(result["combined_output"])
        elif command_id == "tagged_policy":
            try:
                tagged_payload = json.loads(result["combined_output"])
            except Exception:
                tagged_payload = {}
            parsed = {
                "policy_ok": bool(tagged_payload.get("status", {}).get("policy_ok")),
                "parse_clean": bool(tagged_payload.get("status", {}).get("parse_clean")),
                "tagged_file_count": tagged_payload.get("inventory", {}).get("tagged_file_count"),
                "parse_failure_count": tagged_payload.get("inventory", {}).get("parse_failure_count"),
            }
        else:
            parsed = _parse_pytest_summary(result["combined_output"])

        evidence[command_id] = {
            "command": result["command"],
            "returncode": result["returncode"],
            "duration_seconds": result["duration_seconds"],
            "stdout_tail": result["stdout_tail"],
            "stderr_tail": result["stderr_tail"],
            "parsed": parsed,
        }

    claims = _build_claims(evidence)
    report = {
        "generated_utc": _utc_now(),
        "repo_root": str(ROOT_DIR),
        "claims": claims,
        "evidence": evidence,
    }

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "09_CLAIM_EVIDENCE_LOCK.json"
    md_path = out_dir / "09_CLAIM_EVIDENCE_LOCK.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")

    print(f"[OK] Wrote {json_path}")
    print(f"[OK] Wrote {md_path}")

    if any(claim["status"] != "supported" for claim in claims):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
