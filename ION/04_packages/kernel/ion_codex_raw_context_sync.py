"""Raw Codex context sync lane for the ION Codex carrier domain.

This module deliberately treats raw Codex session/memory context as useful
local diagnostic continuity, not accepted ION state.  It never exports raw
``~/.codex`` transcripts, memories, or session text.  It can:

- initialize repo-visible policy/manifest scaffolding;
- assert that the private raw-context storage lane is gitignored;
- write public-safe manifests that prove a private snapshot exists;
- bind those manifests to Codex branch capsules when a capsule is provided;
- expose read-only status for cockpit/MCP projection.

Raw content remains local/private unless a separate packet produces a narrow,
redacted excerpt that passes normal ION proof/receipt/settlement gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA_ID = "ion.codex_raw_context_sync_lane.v1"
MANIFEST_SCHEMA_ID = "ion.codex_raw_context_manifest.v1"
LANE_READY_VERDICT = "ION_CODEX_RAW_CONTEXT_SYNC_LANE_READY"
LANE_CANDIDATE_VERDICT = "ION_CODEX_RAW_CONTEXT_SYNC_LANE_CANDIDATE"
LANE_BLOCKED_VERDICT = "ION_CODEX_RAW_CONTEXT_SYNC_LANE_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_CODEX_RAW_CONTEXT_SYNC_WRITE_CONFIRMED"

CONTENT_ROOT_NAME = "ION"
PROTOCOL_PATH = Path("ION/02_architecture/CODEX_RAW_CONTEXT_SYNC_LANE_PROTOCOL.md")
CODEX_CARRIER_DIR = Path("ION/05_context/current/codex_carrier")
POLICY_PATH = CODEX_CARRIER_DIR / "CODEX_RAW_CONTEXT_SYNC_LANE_POLICY.md"
MANIFESTS_DIR = CODEX_CARRIER_DIR / "raw_context_manifests"
MANIFESTS_README_PATH = MANIFESTS_DIR / "README.md"
PRIVATE_RAW_CONTEXT_DIR = Path(".ion_private/codex_raw_context")
BRANCH_CAPSULE_ROOT = Path("ION/05_context/current/agent_context_branches")

GITIGNORE_REQUIRED_PATTERNS = (
    ".ion_private/",
    ".ion_private/codex_raw_context/",
)

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "browser_control_authority": False,
}

SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(sk-[A-Za-z0-9_\-]{8,}|xox[baprs]-[A-Za-z0-9_\-]+|gh[pousr]_[A-Za-z0-9_]+|bearer\s+[A-Za-z0-9._\-]+)"
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return _now().replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: str, fallback: str = "raw_context") -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip().lower()).strip("._-")
    return (slug or fallback)[:96]


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    probes = [candidate, *candidate.parents]
    for path in probes:
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == CONTENT_ROOT_NAME and (path / "REPO_AUTHORITY.md").is_file():
            parent = path.parent
            if (parent / "pyproject.toml").is_file():
                return parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _read_json(path: Path) -> Any | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_file(path: Path, *, max_bytes: int = 50_000_000) -> str:
    stat = path.stat()
    if stat.st_size > max_bytes:
        raise ValueError("raw context snapshot is too large for manifest hashing in this lane")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _surface_status(shell_root: Path, rel: str | Path) -> dict[str, Any]:
    rel_path = Path(rel)
    path = shell_root / rel_path
    return {
        "path": rel_path.as_posix(),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def _gitignore_lines(shell_root: Path) -> list[str]:
    path = shell_root / ".gitignore"
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]


def _gitignore_guard(shell_root: Path) -> dict[str, Any]:
    lines = _gitignore_lines(shell_root)
    present = [pattern for pattern in GITIGNORE_REQUIRED_PATTERNS if pattern in lines]
    missing = [pattern for pattern in GITIGNORE_REQUIRED_PATTERNS if pattern not in lines]
    return {
        "path": ".gitignore",
        "exists": (shell_root / ".gitignore").exists(),
        "required_patterns": list(GITIGNORE_REQUIRED_PATTERNS),
        "present_patterns": present,
        "missing_patterns": missing,
        "ok": not missing,
    }


def _manifest_files(shell_root: Path) -> list[Path]:
    path = shell_root / MANIFESTS_DIR
    if not path.exists():
        return []
    return sorted(p for p in path.glob("*.json") if p.is_file())


def _load_manifest_summaries(shell_root: Path) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for path in _manifest_files(shell_root):
        payload = _read_json(path)
        if not isinstance(payload, dict):
            continue
        summaries.append({
            "manifest_id": payload.get("manifest_id"),
            "path": path.relative_to(shell_root).as_posix(),
            "session_id": payload.get("session_id"),
            "agent_tag": payload.get("agent_tag"),
            "branch_id": payload.get("branch_id"),
            "packet_id": payload.get("packet_id"),
            "snapshot_storage_class": payload.get("snapshot_storage_class"),
            "snapshot_content_committed": payload.get("snapshot_content_committed", False),
            "snapshot_mirrored_externally": payload.get("snapshot_mirrored_externally", False),
            "redaction_status": payload.get("redaction_status"),
            "promotion_state": payload.get("promotion_state"),
            "created_at": payload.get("created_at"),
        })
    return summaries


def _private_path_status(shell_root: Path) -> dict[str, Any]:
    path = shell_root / PRIVATE_RAW_CONTEXT_DIR
    count: int | None = None
    if path.is_dir():
        try:
            count = sum(1 for _ in path.rglob("*"))
        except Exception:
            count = None
    return {
        "path": PRIVATE_RAW_CONTEXT_DIR.as_posix(),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "entry_count_untrusted": count,
        "content_exported": False,
        "gitignored_required": True,
    }


def build_raw_context_sync_lane_status(root: str | Path | None = None) -> dict[str, Any]:
    """Project the raw Codex context sync lane without reading raw content."""
    shell_root = _resolve_shell_root(root)
    surfaces = {
        "protocol": _surface_status(shell_root, PROTOCOL_PATH),
        "policy": _surface_status(shell_root, POLICY_PATH),
        "manifests_dir": _surface_status(shell_root, MANIFESTS_DIR),
        "manifests_readme": _surface_status(shell_root, MANIFESTS_README_PATH),
        "private_raw_context_dir": _private_path_status(shell_root),
    }
    gitignore = _gitignore_guard(shell_root)
    findings: list[str] = []
    if not surfaces["protocol"]["exists"]:
        findings.append(f"missing_raw_context_protocol:{PROTOCOL_PATH.as_posix()}")
    if not surfaces["policy"]["exists"]:
        findings.append(f"missing_raw_context_policy:{POLICY_PATH.as_posix()}")
    if not gitignore["ok"]:
        findings.append("raw_context_private_dir_not_fully_gitignored")
    manifests = _load_manifest_summaries(shell_root)
    verdict = LANE_READY_VERDICT if not findings else LANE_CANDIDATE_VERDICT
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": not findings,
        "shell_root": str(shell_root),
        "policy_ref": POLICY_PATH.as_posix(),
        "protocol_ref": PROTOCOL_PATH.as_posix(),
        "private_storage_ref": PRIVATE_RAW_CONTEXT_DIR.as_posix(),
        "manifest_registry_ref": MANIFESTS_DIR.as_posix(),
        "surfaces": surfaces,
        "gitignore_guard": gitignore,
        "manifest_count": len(manifests),
        "manifests": manifests,
        "raw_content_exported": False,
        "raw_content_committed_by_policy": False,
        "raw_content_mirrored_externally_by_policy": False,
        "promotion_path": [
            "native_codex_session_or_memory",
            "local_private_raw_snapshot",
            "public_safe_manifest",
            "redacted_diagnostic_excerpt_or_summary",
            "proof_gate",
            "receipt_or_settlement",
            "inheritable_ion_state",
        ],
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "findings": findings,
    }


def _policy_text() -> str:
    return "\n".join([
        "# Codex Raw Context Sync Lane Policy",
        "",
        "Status: active candidate policy for the Codex carrier domain.",
        "",
        "Raw Codex context is valuable local diagnostic continuity while ION is still being perfected.",
        "It is not accepted ION state.",
        "",
        "## Rule",
        "",
        "```text",
        "Raw Codex context may diagnose.",
        "Raw Codex context may not govern.",
        "Manifested, redacted, proof-gated excerpts may support settlement.",
        "Receipts and settlement decide inheritance.",
        "```",
        "",
        "## Storage classes",
        "",
        "- Raw snapshots live under `.ion_private/codex_raw_context/` by default.",
        "- Raw snapshots are gitignored and excluded from Drive/context mirrors by default.",
        "- Repo-visible manifests may record hash/provenance without content.",
        "- Redacted excerpts require a packet-bound review and proof path before shared inheritance.",
        "",
        "## Authority",
        "",
        "```json",
        json.dumps({"schema_id": SCHEMA_ID, **AUTHORITY_FALSE, "raw_content_exported": False}, indent=2, sort_keys=True),
        "```",
    ]) + "\n"


def _manifests_readme_text() -> str:
    return "\n".join([
        "# Raw Codex Context Manifests",
        "",
        "This directory may contain public-safe manifests for private Codex raw context snapshots.",
        "",
        "Manifests prove that a local-private snapshot exists and identify its packet/session/agent lane.",
        "They must not contain raw Codex transcript, memory, prompt, private/internal reasoning text, credential, or private operator content.",
    ]) + "\n"


def ensure_raw_context_gitignore_guard(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    path = shell_root / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = [line.strip() for line in existing.splitlines()]
    additions = [pattern for pattern in GITIGNORE_REQUIRED_PATTERNS if pattern not in lines]
    if additions:
        block = "\n# ION private Codex raw context snapshots; manifests only are trackable.\n" + "\n".join(additions) + "\n"
        path.write_text(existing.rstrip() + block, encoding="utf-8")
    return _gitignore_guard(shell_root)


def initialize_raw_context_sync_lane(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    (shell_root / MANIFESTS_DIR).mkdir(parents=True, exist_ok=True)
    (shell_root / POLICY_PATH).parent.mkdir(parents=True, exist_ok=True)
    (shell_root / POLICY_PATH).write_text(_policy_text(), encoding="utf-8")
    (shell_root / MANIFESTS_README_PATH).write_text(_manifests_readme_text(), encoding="utf-8")
    gitignore = ensure_raw_context_gitignore_guard(shell_root)
    status = build_raw_context_sync_lane_status(shell_root)
    return {
        "schema_id": "ion.codex_raw_context_sync_lane_initialization.v1",
        "generated_at": _now(),
        "verdict": status["verdict"],
        "ok": status["ok"],
        "written_paths": [
            POLICY_PATH.as_posix(),
            MANIFESTS_README_PATH.as_posix(),
            ".gitignore",
        ],
        "gitignore_guard": gitignore,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _normalize_private_snapshot(shell_root: Path, snapshot_path: str | Path | None) -> dict[str, Any]:
    if snapshot_path is None:
        return {
            "snapshot_private_relpath": None,
            "snapshot_sha256": None,
            "snapshot_bytes": None,
            "snapshot_path_verified_under_private_dir": None,
        }
    candidate = Path(snapshot_path).expanduser()
    path = candidate.resolve() if candidate.is_absolute() else (shell_root / candidate).resolve()
    private_root = (shell_root / PRIVATE_RAW_CONTEXT_DIR).resolve()
    if not str(path).startswith(str(private_root) + "/") and path != private_root:
        raise ValueError("snapshot_path must be under .ion_private/codex_raw_context for this lane")
    if not path.is_file():
        raise FileNotFoundError("snapshot_path does not exist or is not a file")
    return {
        "snapshot_private_relpath": path.relative_to(shell_root).as_posix(),
        "snapshot_sha256": _sha256_file(path),
        "snapshot_bytes": path.stat().st_size,
        "snapshot_path_verified_under_private_dir": True,
    }


def _validate_no_secret_like_excerpt(value: str | None) -> str | None:
    if not value:
        return None
    if SECRET_VALUE_PATTERN.search(value):
        raise ValueError("diagnostic summary/excerpt appears to contain a secret-like value")
    return value[:4000]


def _safe_branch_capsule_path(shell_root: Path, branch_capsule: str | Path | None) -> Path | None:
    if branch_capsule is None:
        return None
    rel = Path(str(branch_capsule))
    if rel.is_absolute():
        try:
            rel = rel.resolve().relative_to(shell_root)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("branch_capsule must be under the ION shell root") from exc
    if not str(rel).startswith(BRANCH_CAPSULE_ROOT.as_posix() + "/"):
        raise ValueError("branch_capsule must stay under ION/05_context/current/agent_context_branches/")
    path = shell_root / rel
    if not path.exists():
        raise FileNotFoundError("branch_capsule path does not exist; create/register the branch capsule first")
    return path


def create_raw_context_manifest(
    root: str | Path | None = None,
    *,
    agent_tag: str,
    session_id: str,
    branch_id: str,
    packet_id: str,
    snapshot_label: str = "raw Codex context snapshot",
    branch_capsule: str | Path | None = None,
    snapshot_path: str | Path | None = None,
    snapshot_hash: str | None = None,
    diagnostic_summary: str | None = None,
    diagnostic_excerpt_refs: Sequence[str] = (),
    summary_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Write a public-safe manifest for a local-private raw context snapshot."""
    shell_root = _resolve_shell_root(root)
    snapshot = _normalize_private_snapshot(shell_root, snapshot_path)
    if snapshot_hash and snapshot["snapshot_sha256"] and snapshot_hash != snapshot["snapshot_sha256"]:
        raise ValueError("snapshot_hash does not match snapshot_path sha256")
    branch_path = _safe_branch_capsule_path(shell_root, branch_capsule)
    manifest_id = f"rawctx_{_stamp()}_{_slug(agent_tag)}_{_slug(session_id)}"
    manifest_rel = MANIFESTS_DIR / f"{manifest_id}.json"
    branch_manifest_rel: str | None = None
    payload: dict[str, Any] = {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": manifest_id,
        "created_at": _now(),
        "agent_tag": agent_tag,
        "session_id": session_id,
        "branch_id": branch_id,
        "packet_id": packet_id,
        "snapshot_label": snapshot_label,
        "snapshot_storage_class": "local_private_gitignored",
        "snapshot_content_committed": False,
        "snapshot_mirrored_externally": False,
        "snapshot_private_relpath": snapshot["snapshot_private_relpath"],
        "snapshot_sha256": snapshot_hash or snapshot["snapshot_sha256"],
        "snapshot_bytes": snapshot["snapshot_bytes"],
        "snapshot_path_verified_under_private_dir": snapshot["snapshot_path_verified_under_private_dir"],
        "redaction_status": "not_exported",
        "diagnostic_summary": _validate_no_secret_like_excerpt(diagnostic_summary),
        "diagnostic_excerpt_refs": list(diagnostic_excerpt_refs),
        "summary_refs": list(summary_refs),
        "promotion_state": "not_promoted",
        "promotion_requires": [
            "packet_bound_redaction_review",
            "proof_gate",
            "receipt_or_settlement",
        ],
        "authority": dict(AUTHORITY_FALSE),
        "non_claims": [
            "Manifest does not export raw Codex context content.",
            "Manifest does not make Codex memory/session state accepted ION state.",
            "Manifest does not grant production, live execution, secrets, or accepted-state authority.",
        ],
    }
    if branch_path is not None:
        branch_manifest = branch_path / "RAW_CONTEXT_MANIFEST.json"
        branch_manifest_rel = branch_manifest.relative_to(shell_root).as_posix()
        payload["branch_capsule_manifest_ref"] = branch_manifest_rel
    _write_json(shell_root / manifest_rel, payload)
    if branch_path is not None:
        _write_json(branch_path / "RAW_CONTEXT_MANIFEST.json", payload)
    payload["path"] = manifest_rel.as_posix()
    if branch_manifest_rel:
        payload["branch_capsule_manifest_ref"] = branch_manifest_rel
    return payload


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _add_common_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ion-root", default=argparse.SUPPRESS, help="Shell root or ION content root")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage ION Codex raw context sync lane manifests.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Read-only raw context sync lane status")
    _add_common_root_argument(status)
    status.add_argument("--json", action="store_true")

    init = subparsers.add_parser("init", help="Initialize raw context sync lane policy and gitignore guard")
    _add_common_root_argument(init)
    init.add_argument("--confirmation", required=True, help=f"Required token: {WRITE_CONFIRMATION_TOKEN}")
    init.add_argument("--json", action="store_true")

    manifest = subparsers.add_parser("manifest", help="Write a public-safe raw context manifest")
    _add_common_root_argument(manifest)
    manifest.add_argument("--agent-tag", required=True)
    manifest.add_argument("--session-id", required=True)
    manifest.add_argument("--branch-id", required=True)
    manifest.add_argument("--packet-id", required=True)
    manifest.add_argument("--snapshot-label", default="raw Codex context snapshot")
    manifest.add_argument("--branch-capsule", default=None)
    manifest.add_argument("--snapshot-path", default=None)
    manifest.add_argument("--snapshot-hash", default=None)
    manifest.add_argument("--diagnostic-summary", default=None)
    manifest.add_argument("--diagnostic-excerpt-ref", action="append", default=[])
    manifest.add_argument("--summary-ref", action="append", default=[])
    manifest.add_argument("--confirmation", required=True, help=f"Required token: {WRITE_CONFIRMATION_TOKEN}")
    manifest.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "status":
            payload = build_raw_context_sync_lane_status(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
                for finding in payload.get("findings", []):
                    print(f"- {finding}")
            return 0 if payload.get("ok") else 2

        if args.command == "init":
            if args.confirmation != WRITE_CONFIRMATION_TOKEN:
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_raw_context_sync_lane_write_refusal.v1",
                    "refusal_class": "CONFIRMATION_REQUIRED",
                    "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                }
                if args.json:
                    _print_json(payload)
                else:
                    print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                return 3
            payload = initialize_raw_context_sync_lane(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
            return 0 if payload.get("ok") else 2

        if args.command == "manifest":
            if args.confirmation != WRITE_CONFIRMATION_TOKEN:
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_raw_context_manifest_write_refusal.v1",
                    "refusal_class": "CONFIRMATION_REQUIRED",
                    "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                }
                if args.json:
                    _print_json(payload)
                else:
                    print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                return 3
            payload = create_raw_context_manifest(
                args.ion_root,
                agent_tag=args.agent_tag,
                session_id=args.session_id,
                branch_id=args.branch_id,
                packet_id=args.packet_id,
                snapshot_label=args.snapshot_label,
                branch_capsule=args.branch_capsule,
                snapshot_path=args.snapshot_path,
                snapshot_hash=args.snapshot_hash,
                diagnostic_summary=args.diagnostic_summary,
                diagnostic_excerpt_refs=args.diagnostic_excerpt_ref,
                summary_refs=args.summary_ref,
            )
            payload["ok"] = True
            if args.json:
                _print_json(payload)
            else:
                print(payload["manifest_id"])
            return 0
    except Exception as exc:
        payload = {
            "ok": False,
            "schema_id": "ion.codex_raw_context_sync_lane_cli_error.v1",
            "error": str(exc),
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }
        if getattr(args, "json", False):
            _print_json(payload)
        else:
            print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
