"""Sanitized local Codex-PC capability audit for the ION Codex carrier domain.

The audit is deliberately evidence-oriented and secret-averse. It inventories
local Codex CLI availability, project/global Codex configuration shape, known
Codex home directories, and help-surface support without exporting raw
``~/.codex`` memory/session/config contents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:  # Python 3.11+
    import tomllib
except Exception:  # pragma: no cover - defensive for older runtimes
    tomllib = None  # type: ignore[assignment]

SCHEMA_ID = "ion.codex_local_pc_audit.v1"
AUDIT_READY_VERDICT = "ION_CODEX_LOCAL_PC_AUDIT_READY"
AUDIT_CANDIDATE_VERDICT = "ION_CODEX_LOCAL_PC_AUDIT_CANDIDATE"
AUDIT_BLOCKED_VERDICT = "ION_CODEX_LOCAL_PC_AUDIT_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_CODEX_LOCAL_PC_AUDIT_WRITE_CONFIRMED"
AUDIT_OUTPUT_PATH = Path("ION/05_context/current/codex_carrier/LOCAL_CODEX_PC_AUDIT.json")
DEFAULT_CODEX_HOME = Path("~/.codex")
SECRET_KEY_PATTERN = re.compile(
    r"(secret|token|key|credential|password|passwd|cookie|session|oauth|bearer|client_secret|refresh)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(sk-[A-Za-z0-9_\-]{8,}|xox[baprs]-[A-Za-z0-9_\-]+|gh[pousr]_[A-Za-z0-9_]+|bearer\s+[A-Za-z0-9._\-]+)"
)
CODEX_HOME_DIRECTORIES = (
    "sessions",
    "session",
    "history",
    "histories",
    "memory",
    "memories",
    "commands",
    "slash_commands",
    "agents",
    "subagents",
    "hooks",
    "plugins",
    "skills",
)
CODEX_HELP_COMMANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("version", ("--version",)),
    ("help", ("--help",)),
    ("resume_help", ("resume", "--help")),
    ("mcp_help", ("mcp", "--help")),
    ("remote_control_help", ("remote-control", "--help")),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    probes = [candidate, *candidate.parents]
    for path in probes:
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file():
            parent = path.parent
            if (parent / "pyproject.toml").is_file():
                return parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path, *, max_bytes: int = 10_000_000) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        stat = path.stat()
        if stat.st_size > max_bytes:
            return "sha256_omitted_file_too_large"
        return _sha256_bytes(path.read_bytes())
    except Exception:
        return None


def _name_fingerprint(path: Path) -> dict[str, Any]:
    name = path.name
    try:
        stat = path.stat()
        size = stat.st_size if path.is_file() else None
        modified_at = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    except Exception:
        size = None
        modified_at = None
    return {
        "name_sha256_12": _sha256_bytes(name.encode("utf-8", errors="replace"))[:12],
        "suffix": path.suffix or None,
        "kind": "directory" if path.is_dir() else "file" if path.is_file() else "other",
        "bytes": size,
        "modified_at": modified_at,
    }


def _redact_text(value: str, *, max_chars: int = 4000) -> str:
    text = SECRET_VALUE_PATTERN.sub("[REDACTED_SECRET_VALUE]", value)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[truncated]"
    return text


def _redact_scalar(key: str, value: Any) -> Any:
    if SECRET_KEY_PATTERN.search(str(key)):
        return "[REDACTED_SECRET_KEY]"
    if isinstance(value, str):
        return _redact_text(value, max_chars=240)
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return f"[{type(value).__name__}]"


def _redacted_toml_shape(value: Any, *, key_path: str = "", depth: int = 0) -> Any:
    if depth > 4:
        return "[MAX_DEPTH]"
    if isinstance(value, Mapping):
        shaped: dict[str, Any] = {}
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
            skey = str(key)
            dotted = f"{key_path}.{skey}" if key_path else skey
            if SECRET_KEY_PATTERN.search(dotted):
                shaped[skey] = "[REDACTED_SECRET_KEY]"
            else:
                shaped[skey] = _redacted_toml_shape(item, key_path=dotted, depth=depth + 1)
        return shaped
    if isinstance(value, list):
        return [_redacted_toml_shape(item, key_path=key_path, depth=depth + 1) for item in value[:20]]
    return _redact_scalar(key_path, value)


def _summarize_toml_config(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path_ref": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": _file_sha256(path),
        "parse_ok": False,
        "top_level_keys": [],
        "redacted_shape": {},
        "mcp_server_names": [],
        "profile_names": [],
        "secret_like_key_count": 0,
    }
    if not path.is_file():
        return summary
    raw = path.read_bytes()
    summary["secret_like_value_pattern_detected"] = bool(SECRET_VALUE_PATTERN.search(raw.decode("utf-8", errors="replace")))
    if tomllib is None:
        summary["parse_error"] = "tomllib_unavailable"
        return summary
    try:
        parsed = tomllib.loads(raw.decode("utf-8", errors="replace"))
    except Exception as exc:
        summary["parse_error"] = str(exc)
        return summary
    if not isinstance(parsed, Mapping):
        return summary
    top_keys = sorted(str(key) for key in parsed.keys())
    summary["parse_ok"] = True
    summary["top_level_keys"] = top_keys
    summary["redacted_shape"] = _redacted_toml_shape(parsed)
    secret_like_keys: list[str] = []

    def walk_keys(node: Any, prefix: str = "") -> None:
        if isinstance(node, Mapping):
            for key, item in node.items():
                dotted = f"{prefix}.{key}" if prefix else str(key)
                if SECRET_KEY_PATTERN.search(dotted):
                    secret_like_keys.append(dotted)
                walk_keys(item, dotted)

    walk_keys(parsed)
    summary["secret_like_key_count"] = len(secret_like_keys)
    mcp_servers = parsed.get("mcp_servers") if isinstance(parsed, Mapping) else None
    if isinstance(mcp_servers, Mapping):
        summary["mcp_server_names"] = sorted(str(key) for key in mcp_servers.keys())
    profiles = parsed.get("profiles") if isinstance(parsed, Mapping) else None
    if isinstance(profiles, Mapping):
        summary["profile_names"] = sorted(str(key) for key in profiles.keys())
    for scalar_key in ("sandbox_mode", "approval_policy", "model", "profile"):
        if scalar_key in parsed:
            summary[scalar_key] = _redact_scalar(scalar_key, parsed.get(scalar_key))
    return summary


def _summarize_marker_file(path: Path) -> dict[str, Any]:
    return {
        "path_ref": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": _file_sha256(path),
        "content_exported": False,
    }


def _summarize_codex_home(codex_home: Path) -> dict[str, Any]:
    home = codex_home.expanduser().resolve()
    summary: dict[str, Any] = {
        "path_ref": str(home),
        "exists": home.exists(),
        "is_dir": home.is_dir(),
        "config": _summarize_toml_config(home / "config.toml"),
        "agents_md": _summarize_marker_file(home / "AGENTS.md"),
        "agents_override_md": _summarize_marker_file(home / "AGENTS.override.md"),
        "directories": {},
        "raw_memory_or_session_content_exported": False,
        "raw_file_names_exported": False,
    }
    if not home.is_dir():
        return summary
    directories: dict[str, Any] = {}
    for dirname in CODEX_HOME_DIRECTORIES:
        directory = home / dirname
        entry: dict[str, Any] = {
            "path_ref": str(directory),
            "exists": directory.exists(),
            "is_dir": directory.is_dir(),
            "entry_count": 0,
            "sample_fingerprints": [],
        }
        if directory.is_dir():
            try:
                children = sorted(directory.iterdir(), key=lambda item: item.name)
            except Exception:
                children = []
            entry["entry_count"] = len(children)
            entry["sample_fingerprints"] = [_name_fingerprint(child) for child in children[:25]]
        directories[dirname] = entry
    summary["directories"] = directories
    return summary


def _run_codex_command(codex_bin: str, args: Sequence[str], *, timeout: int = 8) -> dict[str, Any]:
    command = [codex_bin, *args]
    payload: dict[str, Any] = {
        "args": list(args),
        "returncode": None,
        "stdout_preview": "",
        "stderr_preview": "",
        "timed_out": False,
    }
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        payload.update({
            "timed_out": True,
            "stdout_preview": _redact_text(exc.stdout or "", max_chars=1600) if isinstance(exc.stdout, str) else "",
            "stderr_preview": _redact_text(exc.stderr or "", max_chars=1600) if isinstance(exc.stderr, str) else "",
        })
        return payload
    except Exception as exc:
        payload["error"] = str(exc)
        return payload
    payload.update({
        "returncode": completed.returncode,
        "stdout_preview": _redact_text(completed.stdout or "", max_chars=2400),
        "stderr_preview": _redact_text(completed.stderr or "", max_chars=1600),
    })
    return payload


def _project_codex_config_summary(shell_root: Path) -> dict[str, Any]:
    config = _summarize_toml_config(shell_root / ".codex" / "config.toml")
    hook_path = shell_root / ".codex" / "hooks" / "ion_session_start_context.py"
    parent_hook_path = shell_root.parent / ".codex" / "hooks" / "ion_parent_session_start_context.py"
    config["session_start_hook"] = _summarize_marker_file(hook_path)
    config["parent_session_start_hook"] = _summarize_marker_file(parent_hook_path)
    return config


def build_codex_local_pc_audit(
    root: str | Path | None = None,
    *,
    codex_home: str | Path | None = None,
    codex_bin: str | None = None,
    run_help: bool = True,
) -> dict[str, Any]:
    """Build a sanitized local PC audit for Codex carrier operation.

    No raw ``~/.codex`` memory/session contents are read. File names are not
    exported; name fingerprints are used for drift detection.
    """
    shell_root = _resolve_shell_root(root)
    home_path = Path(codex_home).expanduser() if codex_home else DEFAULT_CODEX_HOME.expanduser()
    resolved_codex_bin = codex_bin or shutil.which("codex")
    commands: dict[str, Any] = {}
    if resolved_codex_bin and run_help:
        for name, args in CODEX_HELP_COMMANDS:
            commands[name] = _run_codex_command(resolved_codex_bin, args)
    elif resolved_codex_bin:
        commands["skipped"] = {"reason": "run_help_false"}

    project_config = _project_codex_config_summary(shell_root)
    codex_home_summary = _summarize_codex_home(home_path)
    findings: list[str] = []
    if not resolved_codex_bin:
        findings.append("codex_cli_not_found_on_path")
    if not project_config.get("exists"):
        findings.append("project_codex_config_missing")
    if not codex_home_summary.get("exists"):
        findings.append("codex_home_missing")
    if codex_home_summary.get("config", {}).get("secret_like_value_pattern_detected"):
        findings.append("codex_home_config_contains_secret_like_values_redacted")
    if project_config.get("secret_like_value_pattern_detected"):
        findings.append("project_codex_config_contains_secret_like_values_redacted")

    required_help = {"version", "help"}
    help_available = bool(resolved_codex_bin) and all(
        name in commands and commands[name].get("returncode") == 0 for name in required_help
    )
    if not resolved_codex_bin:
        verdict = AUDIT_BLOCKED_VERDICT
    elif not help_available:
        verdict = AUDIT_CANDIDATE_VERDICT
    else:
        verdict = AUDIT_READY_VERDICT

    payload = {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": verdict != AUDIT_BLOCKED_VERDICT,
        "shell_root": str(shell_root),
        "content_root": str(shell_root / "ION"),
        "audit_scope": {
            "project_codex_config": str(shell_root / ".codex" / "config.toml"),
            "codex_home": str(home_path.expanduser().resolve()),
            "codex_binary": resolved_codex_bin,
            "help_commands_ran": bool(resolved_codex_bin and run_help),
        },
        "project_codex_config": project_config,
        "codex_home": codex_home_summary,
        "codex_cli": {
            "available": bool(resolved_codex_bin),
            "binary_ref": resolved_codex_bin,
            "commands": commands,
        },
        "findings": findings,
        "memory_policy": {
            "raw_memory_or_session_content_exported": False,
            "raw_file_names_exported": False,
            "raw_config_values_exported": False,
            "secret_like_values_redacted": True,
            "codex_memory_role": "working_recall_only_not_accepted_state",
        },
        "next_required_action": (
            "Run Codex carrier domain init/register-session after local audit is READY."
            if verdict == AUDIT_READY_VERDICT
            else "Install/repair Codex CLI or local Codex config, then rerun sanitized local audit."
        ),
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    return payload


def write_codex_local_pc_audit(
    root: str | Path | None = None,
    *,
    output: str | Path | None = None,
    codex_home: str | Path | None = None,
    codex_bin: str | None = None,
    run_help: bool = True,
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = build_codex_local_pc_audit(shell_root, codex_home=codex_home, codex_bin=codex_bin, run_help=run_help)
    output_path = Path(output) if output else shell_root / AUDIT_OUTPUT_PATH
    if not output_path.is_absolute():
        output_path = shell_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["written_path"] = output_path.relative_to(shell_root).as_posix() if output_path.is_relative_to(shell_root) else str(output_path)
    return payload


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _require_confirmation(value: str | None) -> bool:
    return value == WRITE_CONFIRMATION_TOKEN


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sanitized ION Codex local-PC capability audit.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    parser.add_argument("--codex-home", default=None, help="Override ~/.codex path for audit/tests")
    parser.add_argument("--codex-bin", default=None, help="Override codex executable path for audit/tests")
    parser.add_argument("--no-help-probe", action="store_true", help="Do not run codex help/version probes")
    parser.add_argument("--write", action="store_true", help=f"Write {AUDIT_OUTPUT_PATH.as_posix()}")
    parser.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.write:
            if not _require_confirmation(args.confirmation):
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_local_pc_audit_write_refusal.v1",
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
            payload = write_codex_local_pc_audit(
                args.ion_root,
                codex_home=args.codex_home,
                codex_bin=args.codex_bin,
                run_help=not args.no_help_probe,
            )
        else:
            payload = build_codex_local_pc_audit(
                args.ion_root,
                codex_home=args.codex_home,
                codex_bin=args.codex_bin,
                run_help=not args.no_help_probe,
            )
        if args.json:
            _print_json(payload)
        else:
            print(payload["verdict"])
            for finding in payload.get("findings", []):
                print(f"- {finding}")
        return 0 if payload.get("ok") else 2
    except Exception as exc:
        payload = {
            "ok": False,
            "schema_id": "ion.codex_local_pc_audit_cli_error.v1",
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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
