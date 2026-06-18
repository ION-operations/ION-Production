"""Validate parent Cursor carrier-control proof blocks against active packets.

The carrier-control surface must emit a `### CARRIER CONTROL PROOF` block whose
sha256 claims match the current on-disk active carrier packets before continuing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CARRIER_CONTROL_PROOF_HEADING = "### CARRIER CONTROL PROOF"

REQUIRED_LOADED_PATHS: tuple[str, ...] = (
    "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json",
    "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json",
    "ION/05_context/current/ACTIVE_CURSOR_HOOK_STATE.json",
)

TURN_PACKET_REL = "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json"
HOOK_STATE_REL = "ION/05_context/current/ACTIVE_CURSOR_HOOK_STATE.json"

ION_ROLE_SURFACES: frozenset[str] = frozenset(
    {
        "STEWARD",
        "RELAY",
        "PERSONA",
        "PERSONA_INTERFACE",
        "MASON",
        "VIZIER",
        "NEMESIS",
        "IONOLOGIST",
    }
)


_LOADED_LINE_RE = re.compile(
    r"path\s*=\s*(\S+?)(?:\s|$).*?\bsha256\s*=\s*([a-f0-9]{64})",
    re.IGNORECASE,
)
_SPAWN_ROW_RE = re.compile(
    r"index\s*=\s*(\d+)\b.*?\brole\s*=\s*(\S+)",
    re.IGNORECASE,
)

RECEIPT_REL = "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_RECEIPT.json"
LEDGER_REL = "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_LEDGER.json"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _clean_scalar(value: str) -> str:
    text = value.strip()
    if text.startswith("- "):
        text = text[2:].strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = text.strip("`").strip()
    return text


def _proof_section(proof_text: str) -> str:
    text = proof_text.lstrip()
    if not text.startswith(CARRIER_CONTROL_PROOF_HEADING):
        return ""
    rest = text[len(CARRIER_CONTROL_PROOF_HEADING) :]
    match = re.search(r"\n###\s+", rest)
    if match:
        return rest[: match.start()]
    return rest


def _parse_colon_field(section: str, field: str) -> str | None:
    pattern = re.compile(
        rf"^\s*-?\s*{re.escape(field)}\s*:\s*(.+)$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(section)
    if not match:
        return None
    return _clean_scalar(match.group(1))


def _parse_loaded_claims(section: str) -> dict[str, str]:
    claims: dict[str, str] = {}
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _LOADED_LINE_RE.search(line)
        if match:
            path = _clean_scalar(match.group(1))
            sha = match.group(2).lower()
            claims[path] = sha
    return claims


def _parse_spawn_queue_claims(section: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_spawn = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if re.match(r"^spawn_queue\s*:", line, re.IGNORECASE):
            in_spawn = True
            continue
        if in_spawn:
            if re.match(r"^[a-z_]+\s*:", line, re.IGNORECASE) and "index=" not in line.lower():
                break
            match = _SPAWN_ROW_RE.search(line)
            if match:
                rows.append({"index": int(match.group(1)), "role": _clean_scalar(match.group(2))})
    return rows


def _has_spawn_queue_section(section: str) -> bool:
    return bool(re.search(r"^\s*spawn_queue\s*:", section, re.MULTILINE | re.IGNORECASE))


def _spawn_queue_set(rows: list[dict[str, Any]]) -> set[tuple[int, str]]:
    result: set[tuple[int, str]] = set()
    for row in rows:
        index = row.get("index")
        role = row.get("role")
        if isinstance(index, int) and isinstance(role, str):
            result.add((index, role))
    return result


def _actual_spawn_queue(turn_packet: dict[str, Any]) -> list[dict[str, Any]]:
    queue = turn_packet.get("spawn_queue", [])
    rows: list[dict[str, Any]] = []
    if isinstance(queue, list):
        for item in queue:
            if not isinstance(item, dict):
                continue
            index = item.get("index")
            role = item.get("role")
            if isinstance(index, int) and isinstance(role, str):
                rows.append({"index": index, "role": role})
    return rows


def resolve_shell_root(ion_root: str | Path) -> Path:
    candidate = Path(ion_root).expanduser().resolve()
    for path in [candidate, *candidate.parents]:
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
    raise FileNotFoundError(
        "Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md"
    )


def evaluate_carrier_control_proof(*, shell_root: Path, proof_text: str) -> dict[str, Any]:
    """Evaluate whether a carrier-control proof matches current on-disk packets."""

    findings: list[str] = []
    stripped = proof_text.lstrip()
    section = _proof_section(proof_text)

    if not stripped.startswith(CARRIER_CONTROL_PROOF_HEADING):
        findings.append("missing_initial_carrier_control_proof_heading")

    carrier_surface_raw = _parse_colon_field(section, "carrier_surface")
    carrier_surface: str | None = carrier_surface_raw
    if carrier_surface_raw is None:
        findings.append("missing_or_invalid_carrier_surface")
        carrier_surface = None
    else:
        carrier_surface = carrier_surface_raw.upper()
        if carrier_surface in ION_ROLE_SURFACES:
            findings.append(f"carrier_surface_must_not_be_ion_role:{carrier_surface_raw}")
        elif carrier_surface != "CURSOR_CARRIER_CONTROL_SURFACE":
            findings.append("missing_or_invalid_carrier_surface")

    operator_message = _parse_colon_field(section, "operator_message")
    loaded_claims = _parse_loaded_claims(section)

    verified_reads: list[dict[str, Any]] = []
    for rel_path in REQUIRED_LOADED_PATHS:
        claimed_sha = loaded_claims.get(rel_path)
        disk_path = shell_root / rel_path
        exists = disk_path.is_file()
        actual_sha: str | None = None
        byte_count: int | None = None
        match = False

        if rel_path not in section and rel_path not in loaded_claims:
            findings.append(f"missing_required_loaded_path:{rel_path}")
        elif claimed_sha is None:
            if rel_path in section or any(rel_path in line for line in section.splitlines()):
                findings.append(f"missing_sha256_for_path:{rel_path}")
            else:
                findings.append(f"missing_required_loaded_path:{rel_path}")
        else:
            if not exists:
                findings.append(f"required_file_missing_on_disk:{rel_path}")
            else:
                file_bytes = disk_path.read_bytes()
                byte_count = len(file_bytes)
                actual_sha = _sha256_bytes(file_bytes)
                match = claimed_sha.lower() == actual_sha
                if not match:
                    findings.append(f"stale_or_mismatched_sha256:{rel_path}")

        verified_reads.append(
            {
                "path": rel_path,
                "required": True,
                "exists": exists,
                "bytes": byte_count,
                "sha256_claimed": claimed_sha,
                "sha256_actual": actual_sha,
                "match": match,
            }
        )

    hook_state_path = shell_root / HOOK_STATE_REL
    continue_verdict_actual: str | None = None
    if hook_state_path.is_file():
        hook_state = _load_json(hook_state_path)
        raw_verdict = hook_state.get("continue_verdict")
        if isinstance(raw_verdict, str):
            continue_verdict_actual = raw_verdict

    continue_verdict_claimed = _parse_colon_field(section, "continue_verdict")
    if continue_verdict_claimed is None:
        findings.append("missing_continue_verdict_in_proof")
    elif continue_verdict_actual is not None and continue_verdict_claimed != continue_verdict_actual:
        findings.append("continue_verdict_mismatch")

    turn_packet_path = shell_root / TURN_PACKET_REL
    objective_sha256_actual: str | None = None
    turn_packet: dict[str, Any] = {}
    if turn_packet_path.is_file():
        turn_packet = _load_json(turn_packet_path)
        objective = turn_packet.get("objective")
        if isinstance(objective, str):
            objective_sha256_actual = _sha256_bytes(objective.encode("utf-8"))

    objective_sha256_claimed = _parse_colon_field(section, "objective_sha256")
    if objective_sha256_claimed is None:
        findings.append("missing_objective_sha256")
    elif objective_sha256_actual is not None and objective_sha256_claimed.lower() != objective_sha256_actual:
        findings.append("objective_sha256_mismatch")

    spawn_queue_claimed = _parse_spawn_queue_claims(section)
    spawn_queue_actual = _actual_spawn_queue(turn_packet)
    claimed_set = _spawn_queue_set(spawn_queue_claimed)
    actual_set = _spawn_queue_set(spawn_queue_actual)

    if not _has_spawn_queue_section(section) and actual_set:
        findings.append("missing_spawn_queue_in_proof")
    elif claimed_set != actual_set:
        findings.append("spawn_queue_mismatch")

    accepted = not findings
    return {
        "schema_id": "ion.carrier_control_proof_evaluation.v1",
        "accepted": accepted,
        "findings": findings,
        "carrier_surface": carrier_surface_raw,
        "operator_message": operator_message,
        "verified_reads": verified_reads,
        "continue_verdict_claimed": continue_verdict_claimed,
        "continue_verdict_actual": continue_verdict_actual,
        "objective_sha256_claimed": objective_sha256_claimed,
        "objective_sha256_actual": objective_sha256_actual,
        "spawn_queue_claimed": spawn_queue_claimed,
        "spawn_queue_actual": spawn_queue_actual,
        "carrier_control_proof_heading": CARRIER_CONTROL_PROOF_HEADING,
        "integration_decision": (
            "ALLOW_CARRIER_CONTROL_CONTINUE" if accepted else "REJECT_AND_RELOAD_ACTIVE_PACKETS"
        ),
        "production_authority": False,
        "live_execution_authority": False,
    }


def evaluate_carrier_control_proof_file(*, shell_root: Path, proof_path: str | Path) -> dict[str, Any]:
    proof_text = Path(proof_path).read_text(encoding="utf-8", errors="replace")
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    result["proof_path"] = str(proof_path)
    result["shell_root"] = str(shell_root)
    return result


def write_receipt(*, shell_root: Path, evaluation: dict[str, Any], operator_message: str | None) -> Path:
    created_at = _iso_now()
    receipt_path = shell_root / RECEIPT_REL
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    receipt: dict[str, Any] = {
        "created_at": created_at,
        "operator_message": operator_message,
    }
    receipt.update(evaluation)
    receipt["schema_id"] = "ion.carrier_control_proof_receipt.v1"
    receipt["created_at"] = created_at
    receipt["operator_message"] = operator_message
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ledger_path = shell_root / LEDGER_REL
    if ledger_path.is_file():
        ledger = _load_json(ledger_path)
    else:
        ledger = {"schema_id": "ion.carrier_control_proof_ledger.v1", "records": []}

    records = ledger.get("records")
    if not isinstance(records, list):
        records = []
    records.append(
        {
            "created_at": created_at,
            "accepted": evaluation.get("accepted"),
            "finding_count": len(evaluation.get("findings", [])),
            "integration_decision": evaluation.get("integration_decision"),
        }
    )
    ledger["schema_id"] = "ion.carrier_control_proof_ledger.v1"
    ledger["records"] = records
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return receipt_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate ION Cursor carrier-control CARRIER CONTROL PROOF blocks."
    )
    parser.add_argument("--ion-root", default=".", help="Path to search for ION shell root")
    parser.add_argument("--proof", required=True, help="Path to proof text/markdown file")
    parser.add_argument(
        "--write-receipt",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write receipt and append ledger entry (default: true)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        shell_root = resolve_shell_root(args.ion_root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    result = evaluate_carrier_control_proof_file(shell_root=shell_root, proof_path=args.proof)

    if args.write_receipt:
        operator_message = result.get("operator_message")
        if not isinstance(operator_message, str):
            operator_message = None
        receipt_path = write_receipt(
            shell_root=shell_root,
            evaluation=result,
            operator_message=operator_message,
        )
        result["receipt_path"] = str(receipt_path)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "ION_CARRIER_CONTROL_PROOF_ACCEPTED"
            if result["accepted"]
            else "ION_CARRIER_CONTROL_PROOF_REJECTED"
        )
        for finding in result["findings"]:
            print(f"- {finding}")

    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
