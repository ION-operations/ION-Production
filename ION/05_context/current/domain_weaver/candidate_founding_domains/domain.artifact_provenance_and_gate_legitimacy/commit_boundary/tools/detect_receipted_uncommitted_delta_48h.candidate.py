#!/usr/bin/env python3
"""Flag receipted domain_promotions / gate witnesses newer than last commit boundary receipt and older than 48h."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve()
while REPO_ROOT != REPO_ROOT.parent:
    if (REPO_ROOT / "pyproject.toml").is_file() and (REPO_ROOT / "ION" / "REPO_AUTHORITY.md").is_file():
        break
    REPO_ROOT = REPO_ROOT.parent

COMMIT_RECEIPT_GLOB = (
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.artifact_provenance_and_gate_legitimacy/commit_boundary/"
    "COMMIT_BOUNDARY_RECEIPT_*.candidate.json"
)
WATCH_DIRS = [
    "ION/05_context/current/domain_promotions",
    (
        "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.artifact_provenance_and_gate_legitimacy/receipts"
    ),
]


def _parse_ts_from_name(name: str) -> datetime | None:
    # e.g. 20260808T142007Z
    for part in name.replace("-", "").split("_"):
        if len(part) >= 16 and part[8:9] == "T" and part.endswith("Z"):
            try:
                return datetime.strptime(part[:16], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def _last_commit_receipt_time() -> datetime | None:
    base = REPO_ROOT
    receipts = sorted(base.glob(COMMIT_RECEIPT_GLOB))
    if not receipts:
        return None
    latest = receipts[-1]
    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
        return datetime.fromisoformat(data["committed_at"].replace("Z", "+00:00"))
    except (json.JSONDecodeError, KeyError, ValueError):
        return _parse_ts_from_name(latest.name)


def main() -> int:
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=48)
    last_commit = _last_commit_receipt_time()
    findings: list[dict] = []

    for rel in WATCH_DIRS:
        d = REPO_ROOT / rel
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            ts = _parse_ts_from_name(p.name)
            if ts is None:
                continue
            if ts < threshold:
                continue
            if last_commit and ts <= last_commit:
                continue
            try:
                porcelain = subprocess.run(
                    ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", str(p.relative_to(REPO_ROOT))],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                dirty = bool(porcelain.stdout.strip())
            except OSError:
                dirty = True
            if dirty:
                findings.append(
                    {
                        "path": str(p.relative_to(REPO_ROOT)),
                        "artifact_ts": ts.isoformat(),
                        "reason": "receipted_artifact_dirty_or_untracked_after_last_commit_boundary",
                    }
                )

    out = {
        "schema_id": "ion.commit_boundary.absence_probe.v0_1_candidate",
        "checked_at": now.isoformat(),
        "last_commit_boundary_receipt_at": last_commit.isoformat() if last_commit else None,
        "finding_count": len(findings),
        "findings": findings,
        "verdict": "ABSENCE_DETECTED" if findings else "OK",
    }
    print(json.dumps(out, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
