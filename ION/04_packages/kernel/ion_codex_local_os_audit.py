"""Read-only local Codex OS audit for the ION Codex carrier domain.

This module inventories the local Codex CLI/App operating surface needed to
power ION from the operator PC. It is deliberately conservative:

- it runs only harmless Codex help/version commands;
- it inventories ``~/.codex`` by path metadata, counts, sizes, and redacted
  TOML key shapes;
- it never exports raw Codex memories, transcripts, sessions, credentials, or
  config values;
- optional local port probes are socket-connect checks only and never start
  services.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - defensive for older runtimes
    tomllib = None  # type: ignore[assignment]

OUTPUT_RELATIVE_PATH = Path("ION/05_context/current/codex_carrier/CODEX_LOCAL_OS_AUDIT.json")
SCHEMA_ID = "ion.codex_local_os_audit.v1"
READY_VERDICT = "ION_CODEX_LOCAL_OS_AUDIT_READY"
BLOCKED_VERDICT = "ION_CODEX_LOCAL_OS_AUDIT_BLOCKED"

DEFAULT_CODEX_HOME = Path("~/.codex")
MAX_INVENTORY_DEPTH = 4
MAX_PATH_SAMPLES = 18
MAX_COMMAND_EXCERPT_CHARS = 2200
COMMAND_TIMEOUT_SECONDS = 8.0

SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret|password|passwd|pwd|credential|cookie|bearer|oauth|session)",
    re.IGNORECASE,
)

CODEX_COMMAND_PROBES: tuple[tuple[str, ...], ...] = (
    ("--version",),
    ("--help",),
    ("resume", "--help"),
    ("mcp", "--help"),
    ("app-server", "--help"),
    ("remote-control", "--help"),
    ("fork", "--help"),
)

CAPABILITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "resume": ("resume",),
    "mcp": ("mcp",),
    "app_server": ("app-server", "app server", "server"),
    "remote_control": ("remote-control", "remote control"),
    "fork": ("fork",),
    "hooks": ("hook", "hooks"),
    "slash_commands": ("slash", "command", "commands"),
    "subagents": ("subagent", "subagents"),
    "memory": ("memory", "memories"),
    "sandbox": ("sandbox",),
}

LOCAL_CODEX_SURFACES: tuple[tuple[str, str, bool], ...] = (
    ("config_toml", "config.toml", False),
    ("agents_md", "AGENTS.md", False),
    ("agents_override_md", "AGENTS.override.md", False),
    ("memories", "memories", True),
    ("sessions", "sessions", True),
    ("commands", "commands", False),
    ("plugins", "plugins", False),
    ("subagents", "subagents", False),
    ("skills", "skills", False),
    ("hooks", "hooks", False),
    ("mcp", "mcp", False),
)

DEFAULT_SERVICE_PORTS: tuple[tuple[int, str], ...] = (
    (8765, "ION MCP preview"),
    (8777, "Action Gateway"),
    (8788, "ION local cockpit"),
    (8795, "dAimon Gemini bridge"),
    (8796, "dAimon reserved secondary"),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    probes = [candidate, *candidate.parents]
    for path in probes:
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file() and (path.parent / "pyproject.toml").is_file():
            return path.parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _redact_for_excerpt(value: str, limit: int = MAX_COMMAND_EXCERPT_CHARS) -> str:
    text = value[:limit]
    # Redact common assignment-looking secret values defensively. Help text
    # should not contain secrets; this prevents accidental leakage if a wrapper
    # prints environment/config snippets.
    patterns = [
        re.compile(r"(?i)(api[_-]?key|token|secret|password|credential|cookie)(\s*[=:]\s*)\S+"),
        re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
        re.compile(r"sk-[A-Za-z0-9]{8,}"),
    ]
    for pattern in patterns:
        text = pattern.sub(lambda match: match.group(1) + "<REDACTED>", text)
    return text


def _surface_status(path: Path, *, include_name_samples: bool = True, max_depth: int = MAX_INVENTORY_DEPTH) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(path.expanduser()),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }
    if not path.exists():
        return payload
    if path.is_file():
        stat = path.stat()
        payload.update({"bytes": stat.st_size, "file_count": 1, "dir_count": 0})
        return payload

    file_count = 0
    dir_count = 0
    total_bytes = 0
    extensions: Counter[str] = Counter()
    samples: list[str] = []
    root_depth = len(path.parts)
    for current, dirs, files in os.walk(path):
        current_path = Path(current)
        depth = len(current_path.parts) - root_depth
        if depth >= max_depth:
            dirs[:] = []
        dir_count += len(dirs)
        for name in files:
            file_path = current_path / name
            file_count += 1
            try:
                total_bytes += file_path.stat().st_size
            except OSError:
                pass
            suffix = file_path.suffix.lower() or "<no_ext>"
            extensions[suffix] += 1
            if include_name_samples and len(samples) < MAX_PATH_SAMPLES:
                try:
                    samples.append(file_path.relative_to(path).as_posix())
                except ValueError:
                    samples.append(file_path.name)
    payload.update(
        {
            "file_count": file_count,
            "dir_count": dir_count,
            "total_bytes": total_bytes,
            "extensions": dict(sorted(extensions.items())),
            "name_samples_redacted": not include_name_samples,
        }
    )
    if include_name_samples:
        payload["samples"] = samples
    return payload


def _toml_shape(value: Any, prefix: str = "") -> dict[str, Any]:
    key_paths: list[str] = []
    secret_like_key_paths: list[str] = []
    table_paths: list[str] = []
    scalar_types: dict[str, str] = {}

    def walk(item: Any, path: str) -> None:
        if isinstance(item, dict):
            if path:
                table_paths.append(path)
            for key, child in sorted(item.items(), key=lambda pair: str(pair[0])):
                key_text = str(key)
                child_path = f"{path}.{key_text}" if path else key_text
                key_paths.append(child_path)
                if SECRET_KEY_RE.search(key_text) or SECRET_KEY_RE.search(child_path):
                    secret_like_key_paths.append(child_path)
                walk(child, child_path)
            return
        if isinstance(item, list):
            scalar_types[path] = "list"
            return
        scalar_types[path] = type(item).__name__

    walk(value, prefix)
    return {
        "values_redacted": True,
        "key_paths": key_paths,
        "table_paths": table_paths,
        "secret_like_key_paths": secret_like_key_paths,
        "scalar_types": scalar_types,
    }


def _redacted_toml_file(path: Path) -> dict[str, Any]:
    status = _surface_status(path)
    status["content_values_exported"] = False
    if not path.exists() or not path.is_file():
        return status
    if tomllib is None:
        status["toml_parse_status"] = "UNAVAILABLE_TOMLLIB"
        return status
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        status["toml_parse_status"] = "PARSE_ERROR"
        status["toml_parse_error_class"] = exc.__class__.__name__
        return status
    status["toml_parse_status"] = "OK"
    status["toml_shape"] = _toml_shape(data)
    return status


def _command_probe(
    codex_binary: str,
    args: Sequence[str],
    *,
    timeout: float,
    include_help_excerpts: bool,
) -> dict[str, Any]:
    command = [codex_binary, *args]
    label = "codex " + " ".join(args)
    binary_path = shutil.which(codex_binary)
    payload: dict[str, Any] = {
        "label": label,
        "argv": command,
        "binary_path": binary_path,
        "available": bool(binary_path),
        "executed": False,
        "content_values_exported": bool(include_help_excerpts),
    }
    if not binary_path:
        payload["error_class"] = "FileNotFoundError"
        return payload
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        payload.update({"executed": True, "timed_out": True, "timeout_seconds": timeout})
        return payload
    except Exception as exc:  # pragma: no cover - environment defensive path
        payload.update({"executed": False, "error_class": exc.__class__.__name__})
        return payload

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    combined = f"{stdout}\n{stderr}".lower()
    capability_hits = {
        name: any(keyword in combined for keyword in keywords)
        for name, keywords in CAPABILITY_KEYWORDS.items()
    }
    payload.update(
        {
            "executed": True,
            "timed_out": False,
            "returncode": result.returncode,
            "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
            "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
            "stdout_line_count": len(stdout.splitlines()),
            "stderr_line_count": len(stderr.splitlines()),
            "stdout_sha256": _sha256_text(stdout),
            "stderr_sha256": _sha256_text(stderr),
            "capability_hits": capability_hits,
        }
    )
    if include_help_excerpts:
        payload["stdout_excerpt_redacted"] = _redact_for_excerpt(stdout)
        payload["stderr_excerpt_redacted"] = _redact_for_excerpt(stderr)
    return payload


def _aggregate_capabilities(command_results: Iterable[Mapping[str, Any]], codex_home_inventory: Mapping[str, Any]) -> dict[str, Any]:
    aggregate = {name: False for name in CAPABILITY_KEYWORDS}
    for item in command_results:
        hits = item.get("capability_hits")
        if isinstance(hits, dict):
            for name, hit in hits.items():
                aggregate[name] = bool(aggregate.get(name)) or bool(hit)

    surface_to_capability = {
        "memories": "memory",
        "commands": "slash_commands",
        "subagents": "subagents",
        "hooks": "hooks",
        "mcp": "mcp",
    }
    for surface, capability in surface_to_capability.items():
        status = codex_home_inventory.get(surface)
        if isinstance(status, dict) and status.get("exists"):
            aggregate[capability] = True
    return aggregate


def _project_codex_surfaces(shell_root: Path) -> dict[str, Any]:
    surfaces: dict[str, Any] = {
        "project_codex_config": _redacted_toml_file(shell_root / ".codex" / "config.toml"),
        "project_codex_hooks": _surface_status(shell_root / ".codex" / "hooks"),
        "root_agents_md": _surface_status(shell_root / "AGENTS.md"),
    }
    agents_files: list[dict[str, Any]] = []
    for path in sorted(shell_root.rglob("AGENTS.md")):
        if ".git" in path.parts or ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            rel = path.relative_to(shell_root).as_posix()
        except ValueError:
            rel = str(path)
        status = _surface_status(path)
        status["relative_path"] = rel
        agents_files.append(status)
        if len(agents_files) >= 50:
            break
    surfaces["agents_md_files"] = agents_files
    return surfaces


def _local_codex_inventory(codex_home: Path) -> dict[str, Any]:
    codex_home = codex_home.expanduser()
    inventory: dict[str, Any] = {"codex_home": _surface_status(codex_home)}
    for label, rel, redact_names in LOCAL_CODEX_SURFACES:
        path = codex_home / rel
        if path.suffix == ".toml":
            inventory[label] = _redacted_toml_file(path)
        else:
            inventory[label] = _surface_status(path, include_name_samples=not redact_names)
    return inventory


def _port_probe(host: str, port: int, *, timeout: float = 0.25) -> dict[str, Any]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            code = sock.connect_ex((host, port))
        except OSError as exc:
            return {"host": host, "port": port, "reachable": False, "error_class": exc.__class__.__name__}
    return {"host": host, "port": port, "reachable": code == 0, "connect_ex": code}


def _service_port_map(*, probe_ports: bool) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for port, owner in DEFAULT_SERVICE_PORTS:
        payload: dict[str, Any] = {"port": port, "owner": owner, "probe_performed": probe_ports}
        if probe_ports:
            payload["localhost_probe"] = _port_probe("127.0.0.1", port)
        items.append(payload)
    return items


def build_codex_local_os_audit(
    root: str | Path | None = None,
    *,
    codex_home: str | Path | None = None,
    codex_binary: str = "codex",
    command_timeout: float = COMMAND_TIMEOUT_SECONDS,
    include_help_excerpts: bool = False,
    probe_ports: bool = False,
) -> dict[str, Any]:
    """Return a read-only local Codex OS audit projection.

    Raw ``~/.codex`` memories, sessions, transcript contents, and config values
    are not exported. Use ``include_help_excerpts`` only for command help text;
    it still redacts secret-looking assignments defensively.
    """
    shell_root = _resolve_shell_root(root)
    local_home = Path(codex_home).expanduser() if codex_home else DEFAULT_CODEX_HOME.expanduser()
    command_results = [
        _command_probe(
            codex_binary,
            args,
            timeout=command_timeout,
            include_help_excerpts=include_help_excerpts,
        )
        for args in CODEX_COMMAND_PROBES
    ]
    local_inventory = _local_codex_inventory(local_home)
    capability_map = _aggregate_capabilities(command_results, local_inventory)
    codex_binary_available = any(
        item.get("label") == "codex --version" and item.get("executed") and item.get("returncode") == 0
        for item in command_results
    )
    findings: list[str] = []
    if not codex_binary_available:
        findings.append("codex_binary_not_available_or_version_failed")
    if not local_inventory.get("codex_home", {}).get("exists"):
        findings.append("local_codex_home_missing")

    project_surfaces = _project_codex_surfaces(shell_root)
    if not project_surfaces["project_codex_config"].get("exists"):
        findings.append("project_codex_config_missing:.codex/config.toml")
    if not project_surfaces["project_codex_hooks"].get("exists"):
        findings.append("project_codex_hooks_missing:.codex/hooks")

    verdict = READY_VERDICT if not findings else BLOCKED_VERDICT
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": verdict == READY_VERDICT,
        "shell_root": str(shell_root),
        "codex_binary": codex_binary,
        "codex_binary_path": shutil.which(codex_binary),
        "codex_home": str(local_home),
        "findings": findings,
        "command_probes": command_results,
        "capability_map": capability_map,
        "local_codex_inventory": local_inventory,
        "project_codex_surfaces": project_surfaces,
        "service_port_map": _service_port_map(probe_ports=probe_ports),
        "privacy_boundary": {
            "raw_codex_memory_contents_exported": False,
            "raw_codex_session_contents_exported": False,
            "raw_codex_config_values_exported": False,
            "secret_like_values_redacted": True,
            "session_and_memory_file_names_redacted": True,
        },
        "authority_boundary": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "starts_workers": False,
            "mutates_files_without_write_flag": False,
        },
        "next_routes": [
            "If READY, initialize/update Codex carrier domain surfaces and register real sessions explicitly.",
            "If BLOCKED, install/repair Codex CLI, project .codex config/hooks, or local ~/.codex posture before broad local-PC operation.",
            "Treat audit output as candidate evidence until proof gate and Steward/human integration accept it.",
        ],
        "non_claims": [
            "Does not read or export raw Codex memories or transcript contents.",
            "Does not start Codex app-server, remote-control, workers, queue runners, or MCP mutation lanes.",
            "Does not prove Google Drive, GitHub, Cloudflare, or live local tunnel state unless separate evidence is attached.",
        ],
    }


def write_codex_local_os_audit(
    root: str | Path | None = None,
    *,
    output: str | Path | None = None,
    codex_home: str | Path | None = None,
    codex_binary: str = "codex",
    command_timeout: float = COMMAND_TIMEOUT_SECONDS,
    include_help_excerpts: bool = False,
    probe_ports: bool = False,
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    audit = build_codex_local_os_audit(
        shell_root,
        codex_home=codex_home,
        codex_binary=codex_binary,
        command_timeout=command_timeout,
        include_help_excerpts=include_help_excerpts,
        probe_ports=probe_ports,
    )
    out = shell_root / (Path(output) if output else OUTPUT_RELATIVE_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only local Codex OS audit for ION.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    parser.add_argument("--codex-home", default=None, help="Codex home directory; defaults to ~/.codex")
    parser.add_argument("--codex-binary", default="codex", help="Codex executable name/path")
    parser.add_argument("--command-timeout", type=float, default=COMMAND_TIMEOUT_SECONDS)
    parser.add_argument("--include-help-excerpts", action="store_true", help="Include redacted Codex help/version excerpts")
    parser.add_argument("--probe-ports", action="store_true", help="Probe canonical localhost service ports")
    parser.add_argument("--write", action="store_true", help=f"Write audit to {OUTPUT_RELATIVE_PATH.as_posix()} or --output")
    parser.add_argument("--output", default=None, help="Output path relative to shell root when --write is used")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = (
            write_codex_local_os_audit(
                args.ion_root,
                output=args.output,
                codex_home=args.codex_home,
                codex_binary=args.codex_binary,
                command_timeout=args.command_timeout,
                include_help_excerpts=args.include_help_excerpts,
                probe_ports=args.probe_ports,
            )
            if args.write
            else build_codex_local_os_audit(
                args.ion_root,
                codex_home=args.codex_home,
                codex_binary=args.codex_binary,
                command_timeout=args.command_timeout,
                include_help_excerpts=args.include_help_excerpts,
                probe_ports=args.probe_ports,
            )
        )
    except Exception as exc:
        payload = {
            "schema_id": "ion.codex_local_os_audit.error.v1",
            "ok": False,
            "verdict": BLOCKED_VERDICT,
            "error_class": exc.__class__.__name__,
            "error": str(exc),
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(payload["verdict"], file=sys.stderr)
            print(payload["error"], file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["verdict"])
        for finding in payload.get("findings", []):
            print(f"- {finding}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
