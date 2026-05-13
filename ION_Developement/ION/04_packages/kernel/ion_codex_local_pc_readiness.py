"""Read-only Codex/local-PC readiness audit for ION.

This module answers one practical question: can the current local machine carry
ION work through Codex CLI under ION law?  It does not read hidden Codex
memories, print secrets, start services, enqueue work, mutate Git, or call
GitHub/MCP.  It only inspects repo surfaces, safe command availability, local
service ports, and carrier fallback posture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_ID = "ion.codex_local_pc_readiness.v1"
READY_VERDICT = "ION_CODEX_LOCAL_PC_READY"
PARTIAL_VERDICT = "ION_CODEX_LOCAL_PC_PARTIAL"
BLOCKED_VERDICT = "ION_CODEX_LOCAL_PC_BLOCKED"
OUTPUT_RELATIVE_PATH = Path("ION/05_context/current/codex_local_pc/CODEX_LOCAL_PC_READINESS.json")

CORE_SURFACES: dict[str, str] = {
    "repo_authority": "ION/REPO_AUTHORITY.md",
    "mount_contract": "ION/02_architecture/ION_MOUNT_CONTRACT.md",
    "current_operating_packet": "ION/docs/setup/ION_CURRENT_OPERATING_PACKET_V119.md",
    "codex_cli_setup": "ION/docs/setup/CODEX_CLI_ION_DOGFOOD_SETUP_V125.md",
    "codex_cli_protocol": "ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md",
    "codex_carrier_domain_protocol": "ION/02_architecture/CODEX_CARRIER_DOMAIN_PROTOCOL.md",
    "codex_carrier_domain_module": "ION/04_packages/kernel/ion_codex_carrier_domain.py",
    "codex_cli_audit_module": "ION/04_packages/kernel/ion_codex_cli_carrier_audit.py",
    "codex_solo_context_module": "ION/04_packages/kernel/ion_codex_solo_context.py",
    "mcp_local_bridge_module": "ION/04_packages/kernel/ion_mcp_local_bridge.py",
    "project_codex_config": ".codex/config.toml",
    "session_start_hook": ".codex/hooks/ion_session_start_context.py",
    "codex_solo_hot_context": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
    "codex_solo_status": "ION/05_context/current/codex_solo/STATUS.json",
    "codex_solo_route": "ION/05_context/current/codex_solo/ROUTE.json",
    "github_data_plane_protocol": "ION/02_architecture/ION_GITHUB_DATA_PLANE_PROTOCOL.md",
}

SERVICE_PORTS: tuple[tuple[str, int], ...] = (
    ("ion_mcp_preview", 8765),
    ("action_gateway", 8777),
    ("ion_local_cockpit", 8788),
    ("daimon_gemini_bridge", 8795),
    ("daimon_reserved_secondary", 8796),
)

WORK_BRANCH_PREFIXES = ("work/", "docs/", "agent/", "data-plane/", "feature/")
SECRETISH_ENV_NAMES = ("TOKEN", "SECRET", "KEY", "PASSWORD", "COOKIE", "CREDENTIAL")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file() and (path.parent / "pyproject.toml").is_file():
            return path.parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _surface_status(shell_root: Path, label: str, rel: str) -> dict[str, Any]:
    path = shell_root / rel
    return {
        "label": label,
        "path": rel,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": _sha256_file(path),
    }


def _run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 8,
    max_output_chars: int = 4000,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            list(command),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"command": list(command), "available": False, "returncode": None, "stdout": "", "stderr": "not_found"}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": list(command),
            "available": True,
            "returncode": None,
            "timeout": timeout,
            "stdout": (exc.stdout or "")[:max_output_chars] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[:max_output_chars] if isinstance(exc.stderr, str) else "timeout_expired",
        }
    return {
        "command": list(command),
        "available": True,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[:max_output_chars],
        "stderr": (proc.stderr or "")[:max_output_chars],
    }


def _sanitize_remote(value: str | None) -> str | None:
    if not value:
        return value
    if "://" in value and "@" in value.split("://", 1)[1].split("/", 1)[0]:
        scheme, rest = value.split("://", 1)
        host_path = rest.split("@", 1)[1]
        return f"{scheme}://<redacted>@{host_path}"
    return value


def _git_summary(shell_root: Path) -> dict[str, Any]:
    branch = _run(["git", "branch", "--show-current"], cwd=shell_root, timeout=5)
    status = _run(["git", "status", "--porcelain=v1", "--branch"], cwd=shell_root, timeout=5, max_output_chars=12000)
    remote = _run(["git", "remote", "get-url", "origin"], cwd=shell_root, timeout=5)
    head = _run(["git", "rev-parse", "--short", "HEAD"], cwd=shell_root, timeout=5)

    status_lines = [line for line in status.get("stdout", "").splitlines() if line.strip()]
    porcelain_lines = [line for line in status_lines if not line.startswith("##")]
    staged = [line for line in porcelain_lines if len(line) >= 2 and line[0] not in {" ", "?"}]
    unstaged = [line for line in porcelain_lines if len(line) >= 2 and line[1] not in {" ", "?"}]
    untracked = [line for line in porcelain_lines if line.startswith("??")]
    branch_name = branch.get("stdout", "").strip() or None
    allowed_branch = bool(branch_name == "main" or (branch_name and branch_name.startswith(WORK_BRANCH_PREFIXES)))
    remote_url = remote.get("stdout", "").strip() or None

    return {
        "git_available": bool(branch.get("available") and status.get("available")),
        "branch": branch_name,
        "head_short": head.get("stdout", "").strip() or None if head.get("returncode") == 0 else None,
        "remote_origin": _sanitize_remote(remote_url),
        "allowed_branch_pattern": allowed_branch,
        "dirty": bool(porcelain_lines),
        "porcelain_count": len(porcelain_lines),
        "staged_count": len(staged),
        "unstaged_count": len(unstaged),
        "untracked_count": len(untracked),
        "porcelain_sample": porcelain_lines[:60],
        "status_returncode": status.get("returncode"),
    }


def _probe_local_port(port: int, *, host: str = "127.0.0.1", timeout: float = 0.25) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"host": host, "port": port, "listening": True, "error": None}
    except OSError as exc:
        return {"host": host, "port": port, "listening": False, "error": exc.__class__.__name__}


def _codex_probe(*, include_help: bool = False) -> dict[str, Any]:
    codex_path = shutil.which("codex")
    payload: dict[str, Any] = {
        "codex_on_path": codex_path is not None,
        "codex_path": codex_path,
        "version": None,
        "help_probe": None,
        "resume_help_probe": None,
        "feature_help_probes": {},
        "not_claimed": ["hidden Codex memories", "session transcript contents", "provider account state"],
    }
    if not codex_path:
        return payload

    version = _run([codex_path, "--version"], timeout=8, max_output_chars=1000)
    payload["version"] = version
    if include_help:
        payload["help_probe"] = _run([codex_path, "--help"], timeout=8, max_output_chars=8000)
        payload["resume_help_probe"] = _run([codex_path, "resume", "--help"], timeout=8, max_output_chars=4000)
        for feature in ("fork", "app-server", "remote-control"):
            payload["feature_help_probes"][feature] = _run([codex_path, feature, "--help"], timeout=8, max_output_chars=4000)
    return payload


def _github_fallback_probe() -> dict[str, Any]:
    gh_path = shutil.which("gh")
    payload: dict[str, Any] = {
        "gh_on_path": gh_path is not None,
        "gh_path": gh_path,
        "version": None,
        "auth_status_checked": False,
        "auth_status": None,
        "network_access_used": False,
        "mutation_performed": False,
        "token_value_read": False,
    }
    if not gh_path:
        return payload
    # Version probing is local and non-mutating.  We intentionally do not run
    # ``gh auth status`` here because authentication checks can vary by host
    # configuration and are not needed to draft fallback communications.
    payload["version"] = _run([gh_path, "--version"], timeout=5, max_output_chars=1000)
    return payload


def _secret_env_presence() -> dict[str, bool]:
    # This intentionally returns only coarse presence through common env names.
    # Values are never read or serialized.
    import os

    result: dict[str, bool] = {}
    for name in sorted(os.environ):
        if any(marker in name.upper() for marker in SECRETISH_ENV_NAMES):
            result[name] = True
    return result


def audit_codex_local_pc_readiness(
    root: str | Path | None = None,
    *,
    include_help: bool = False,
    include_secret_env_names: bool = False,
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    surfaces = {label: _surface_status(shell_root, label, rel) for label, rel in CORE_SURFACES.items()}
    missing_surfaces = [label for label, status in surfaces.items() if not status["exists"]]

    codex = _codex_probe(include_help=include_help)
    git = _git_summary(shell_root)
    services = {
        name: {"owner": name, **_probe_local_port(port)}
        for name, port in SERVICE_PORTS
    }
    github_fallback = _github_fallback_probe()

    blockers: list[str] = []
    warnings: list[str] = []
    if missing_surfaces:
        blockers.extend([f"missing_surface:{label}" for label in missing_surfaces])
    if not codex["codex_on_path"]:
        blockers.append("codex_cli_not_found_on_path")
    if not git["git_available"]:
        blockers.append("git_not_available")
    if not git.get("branch"):
        blockers.append("git_branch_unresolved")
    elif not git.get("allowed_branch_pattern"):
        warnings.append(f"git_branch_not_in_default_ion_patterns:{git.get('branch')}")
    if git.get("dirty"):
        warnings.append("git_worktree_dirty")
    if not services["ion_mcp_preview"]["listening"]:
        warnings.append("ion_mcp_preview_not_listening_8765")
    if not services["action_gateway"]["listening"]:
        warnings.append("action_gateway_not_listening_8777")
    if not services["ion_local_cockpit"]["listening"]:
        warnings.append("ion_local_cockpit_not_listening_8788")
    if not github_fallback["gh_on_path"]:
        warnings.append("gh_cli_not_found_for_github_comms_fallback")

    if blockers:
        verdict = BLOCKED_VERDICT
    elif warnings:
        verdict = PARTIAL_VERDICT
    else:
        verdict = READY_VERDICT

    next_actions = []
    if "codex_cli_not_found_on_path" in blockers:
        next_actions.append("Install/repair Codex CLI on the local PC, then rerun this readiness audit.")
    if any(item.startswith("missing_surface:") for item in blockers):
        next_actions.append("Sync or restore missing ION repo surfaces before registering Codex sessions.")
    if "ion_mcp_preview_not_listening_8765" in warnings:
        next_actions.append("Start or refresh the ION MCP preview service if ChatGPT/MCP live comms are required.")
    if "gh_cli_not_found_for_github_comms_fallback" in warnings:
        next_actions.append("Install or configure GitHub CLI only if MCP fallback via GitHub issue/PR drafts is needed.")
    if git.get("dirty"):
        next_actions.append("Classify dirty files by stage manifest before treating the uploaded tree as merge-clean.")

    payload: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": verdict == READY_VERDICT,
        "partial": verdict == PARTIAL_VERDICT,
        "shell_root": str(shell_root),
        "content_root": str(shell_root / "ION"),
        "core_surfaces": surfaces,
        "missing_surfaces": missing_surfaces,
        "codex_cli": codex,
        "git": git,
        "local_services": services,
        "github_comms_fallback": github_fallback,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": next_actions,
        "capability_boundaries": {
            "network_access_used": False,
            "mcp_mutation_performed": False,
            "github_mutation_performed": False,
            "git_mutation_performed": False,
            "codex_session_started": False,
            "hidden_codex_memory_read": False,
            "secret_values_read": False,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
        "recommended_local_commands": [
            "PYTHONPATH=ION/04_packages python3 -m kernel.ion_status --ion-root . --json",
            "PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_cli_carrier_audit --ion-root . --json",
            "PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_carrier_domain status --ion-root . --json",
            "PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_local_pc_readiness --ion-root . --json --write",
            "PYTHONPATH=ION/04_packages python3 -m kernel.ion_github_comms_fallback status --ion-root . --json",
        ],
    }
    if include_secret_env_names:
        payload["secretish_env_name_presence"] = _secret_env_presence()
    return payload


def write_codex_local_pc_readiness(
    root: str | Path | None = None,
    *,
    output: str | Path | None = None,
    include_help: bool = False,
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = audit_codex_local_pc_readiness(shell_root, include_help=include_help)
    out = shell_root / (Path(output) if output else OUTPUT_RELATIVE_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit ION Codex/local-PC readiness without mutation.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--include-help", action="store_true", help="Also run safe Codex help probes if codex is on PATH.")
    args = parser.parse_args(argv)

    payload = (
        write_codex_local_pc_readiness(args.ion_root, output=args.output, include_help=args.include_help)
        if args.write
        else audit_codex_local_pc_readiness(args.ion_root, include_help=args.include_help)
    )
    if args.json:
        _print_json(payload)
    else:
        print(payload["verdict"])
        for item in payload.get("blockers", []):
            print(f"BLOCKER {item}")
        for item in payload.get("warnings", []):
            print(f"WARNING {item}")
    return 0 if payload["verdict"] in {READY_VERDICT, PARTIAL_VERDICT} else 2


if __name__ == "__main__":
    raise SystemExit(main())
