"""Bounded bridge over Codex CLI saved session storage.

The bridge exposes bounded, redacted views of Codex's real saved session JSONL
store. Its read/profile routes never execute Codex; the `session_resume_send`
route is the only confirmation-gated local Codex CLI resume/send execution path.
"""
from __future__ import annotations

import hashlib
import fcntl
import json
import os
import pty
import re
import select
import shutil
import shlex
import signal
import subprocess
import struct
import termios
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_ID = "ion.codex_session_store_bridge.v1_candidate"
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$")
ROLLOUT_ID_RE = re.compile(r"([0-9a-f]{4,}-[0-9a-f-]{8,})\.jsonl$")
MAX_LINE_COUNT = 200
MAX_MESSAGE_COUNT = 80
MAX_BYTES = 262_144
MAX_TEXT = 4_000
HARVEST_RELATIVE_ROOT = Path("ION/05_context/current/chatgpt_connector/codex_session_store_harvests")
RUNS_RELATIVE_ROOT = Path("ION/05_context/current/chatgpt_connector/codex_session_store_runs")

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_push_authority": False,
    "deletion_authority": False,
}
NON_CLAIMS = [
    "Read/profile routes inspect Codex saved-session files; session_resume_send is the only bounded local Codex CLI execution route.",
    "Preview/status/harvest routes do not execute codex resume or send prompts.",
    "This bridge does not prove direct live UI control or automatic bidirectional communication.",
    "Harvests and run receipts are candidate ION evidence only, not accepted state.",
]
ACTIVE_ROOT_PATCH_TERMS = (
    "active-root patch",
    "active root patch",
    "active_root_candidate_patch",
    "active_root_write_repair",
    "active-root write repair",
    "workspace-write",
    "source/test patch",
    "source patch",
    "write-capable repair",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION/REPO_AUTHORITY.md").is_file():
            return path
    return candidate


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _base(route_id: str, *, ok: bool = True, finding: str | None = None, refusal_class: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "schema_id": SCHEMA_ID,
        "route_id": route_id,
        "generated_at": _now(),
        "mutates_active_state": False,
        **AUTHORITY_FALSE,
        "authority": dict(AUTHORITY_FALSE),
        "non_claims": list(NON_CLAIMS),
    }
    if finding:
        payload["finding"] = finding
    if refusal_class:
        payload["refusal_class"] = refusal_class
    return payload


def _blocked(route_id: str, finding: str, *, refusal_class: str = "SCHEMA_INVALID", data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = _base(route_id, ok=False, finding=finding, refusal_class=refusal_class)
    if data:
        payload.update(dict(data))
    return payload


def _safe_session_id(value: Any) -> str:
    session_id = str(value or "").strip()
    if not session_id:
        raise ValueError("session_id_required")
    if "/" in session_id or "\\" in session_id or ".." in session_id:
        raise ValueError("unsafe_session_id")
    if not SESSION_ID_RE.match(session_id):
        raise ValueError("unsafe_session_id")
    return session_id


def _safe_idempotency_key(value: Any) -> str:
    key = str(value or "").strip()
    if not key:
        raise ValueError("idempotency_key_required")
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9_.:-]+", "_", key).strip("._:-") or "key"
    if "/" in slug or "\\" in slug or ".." in slug:
        slug = "key"
    return f"{slug[:80]}_{digest}"


def _redact(text: Any, *, limit: int = MAX_TEXT) -> str:
    value = str(text or "")
    value = re.sub(r"sk-[A-Za-z0-9_-]{10,}", "sk-***REDACTED***", value)
    value = re.sub(r"gh[pousr]_[A-Za-z0-9_]{16,}", "gh***_***REDACTED***", value)
    value = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "AIza***REDACTED***", value)
    value = re.sub(r"ya29\.[0-9A-Za-z_.-]+", "ya29.***REDACTED***", value)
    value = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", "Bearer ***REDACTED***", value)
    value = re.sub(
        r"(?i)\b([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|AUTHORIZATION)[A-Z0-9_]*)\s*[:=]\s*['\"]?[^ \n\r\t,'\"]+",
        lambda match: f"{match.group(1)}=***REDACTED***",
        value,
    )
    if len(value) > limit:
        return value[:limit] + "...[truncated]"
    return value


def _sanitize(value: Any, *, limit: int = MAX_TEXT) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text in {"base_instructions", "instructions", "encrypted_content"}:
                sanitized[key_text] = {"omitted": True, "reason": "large_or_sensitive_instruction_surface"}
            else:
                sanitized[_redact(key_text, limit=160)] = _sanitize(item, limit=limit)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item, limit=limit) for item in value[:50]]
    if isinstance(value, str):
        return _redact(value, limit=limit)
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return _redact(value, limit=limit)


def _codex_home_candidates() -> list[Path]:
    roots: list[Path] = []
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        roots.append(Path(env_home).expanduser())
    roots.extend(
        [
            Path.home() / ".codex",
            Path.home() / ".config/codex",
            Path.home() / ".local/share/codex",
        ]
    )
    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve(strict=False)
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def _session_roots() -> list[Path]:
    roots: list[Path] = []
    for codex_home in _codex_home_candidates():
        for child in [codex_home / "sessions", codex_home / "history" / "sessions"]:
            if child.is_dir():
                roots.append(child.resolve(strict=False))
    return roots


def _allowed_session_file(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    if resolved.suffix != ".jsonl":
        return False
    for root in _session_roots():
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _session_id_from_path(path: Path) -> str:
    match = ROLLOUT_ID_RE.search(path.name)
    return match.group(1) if match else ""


def _iter_session_files(limit: int = 5_000) -> list[Path]:
    files: list[Path] = []
    for root in _session_roots():
        files.extend(path for path in root.rglob("*.jsonl") if path.is_file() and _allowed_session_file(path))
    unique = {path.resolve(strict=False): path for path in files}
    return sorted(unique.values(), key=lambda item: (item.stat().st_mtime, item.name), reverse=True)[: max(1, limit)]


def _locate_session(session_id: str) -> Path | None:
    safe_id = _safe_session_id(session_id)
    for path in _iter_session_files():
        if safe_id in path.name:
            return path
    return None


def _read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    if not _allowed_session_file(path):
        raise ValueError("session_path_not_allowed")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                yield line_no, {"type": "unparseable_jsonl_line", "payload": {"redacted_line": _redact(stripped, limit=500)}}
                continue
            if isinstance(value, Mapping):
                yield line_no, dict(value)


def _extract_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, Mapping):
        return ""
    for key in ["message", "text", "output_text", "input_text"]:
        if isinstance(payload.get(key), str):
            return str(payload[key])
    content = payload.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, Mapping):
                for key in ["text", "output_text", "input_text"]:
                    if isinstance(item.get(key), str):
                        parts.append(str(item[key]))
                        break
        return "\n".join(parts)
    item = payload.get("item")
    if isinstance(item, Mapping):
        return _extract_text(item)
    return ""


def _record_role_and_kind(obj: Mapping[str, Any]) -> tuple[str, str]:
    payload = obj.get("payload")
    if isinstance(payload, Mapping):
        role = str(payload.get("role") or "")
        kind = str(payload.get("type") or "")
        item = payload.get("item")
        if isinstance(item, Mapping):
            role = role or str(item.get("role") or "")
            kind = kind or str(item.get("type") or "")
        return role, kind
    return "", ""


def _message_view(line_no: int, obj: Mapping[str, Any], *, text_limit: int = 900) -> dict[str, Any]:
    payload = obj.get("payload") if isinstance(obj.get("payload"), Mapping) else {}
    role, kind = _record_role_and_kind(obj)
    text = _extract_text(payload)
    return {
        "line_no": line_no,
        "timestamp": _redact(obj.get("timestamp"), limit=80),
        "record_type": _redact(obj.get("type"), limit=80),
        "payload_type": _redact(kind, limit=80),
        "role": _redact(role, limit=80),
        "text": _redact(text, limit=text_limit),
        "has_text": bool(text),
    }


def _is_message_record(obj: Mapping[str, Any]) -> bool:
    payload = obj.get("payload")
    if not isinstance(payload, Mapping):
        return False
    if payload.get("type") in {"message", "agent_message", "user_message"}:
        return True
    if payload.get("role") in {"user", "assistant", "developer", "system"}:
        return True
    return bool(_extract_text(payload))


def _metadata_from_file(path: Path) -> dict[str, Any]:
    session_meta: dict[str, Any] = {}
    line_count = 0
    first_timestamp = None
    latest_timestamp = None
    for line_no, obj in _read_jsonl(path):
        line_count = line_no
        timestamp = obj.get("timestamp")
        first_timestamp = first_timestamp or timestamp
        latest_timestamp = timestamp or latest_timestamp
        if obj.get("type") == "session_meta" and isinstance(obj.get("payload"), Mapping):
            payload = dict(obj["payload"])
            session_meta = {
                "id": payload.get("id"),
                "timestamp": payload.get("timestamp"),
                "cwd": payload.get("cwd"),
                "originator": payload.get("originator"),
                "cli_version": payload.get("cli_version"),
                "source": payload.get("source"),
                "thread_source": payload.get("thread_source"),
                "model_provider": payload.get("model_provider"),
                "git": _sanitize(payload.get("git"), limit=500),
                "base_instructions_present": bool(payload.get("base_instructions")),
            }
    stat = path.stat()
    return {
        "found": True,
        "session_id": session_meta.get("id") or _session_id_from_path(path),
        "storage_path": path.as_posix(),
        "allowed_store_root": next((root.as_posix() for root in _session_roots() if path.resolve(strict=False).is_relative_to(root)), None),
        "file_format": "codex_rollout_jsonl",
        "size_bytes": stat.st_size,
        "line_count": line_count,
        "first_timestamp": _redact(first_timestamp, limit=80),
        "latest_timestamp": _redact(latest_timestamp, limit=80),
        "session_meta": _sanitize(session_meta, limit=1_200),
    }


def _latest_messages(path: Path, *, message_count: int = 8, text_limit: int = 900) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for line_no, obj in _read_jsonl(path):
        if _is_message_record(obj):
            view = _message_view(line_no, obj, text_limit=text_limit)
            if view["has_text"] and view["role"] in {"user", "assistant"}:
                messages.append(view)
            elif view["has_text"] and view["payload_type"] in {"user_message", "agent_message", "message"}:
                messages.append(view)
    return messages[-max(1, min(message_count, MAX_MESSAGE_COUNT)) :]


def _profile(path: Path) -> dict[str, Any]:
    types: Counter[str] = Counter()
    payload_types: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    message_count = 0
    for _, obj in _read_jsonl(path):
        types[str(obj.get("type") or "")] += 1
        payload = obj.get("payload")
        if isinstance(payload, Mapping):
            payload_types[str(payload.get("type") or "")] += 1
            if payload.get("role"):
                roles[str(payload.get("role"))] += 1
            item = payload.get("item")
            if isinstance(item, Mapping):
                if item.get("type"):
                    payload_types[str(item.get("type"))] += 1
                if item.get("role"):
                    roles[str(item.get("role"))] += 1
        if _is_message_record(obj):
            message_count += 1
    meta = _metadata_from_file(path)
    meta.update(
        {
            "record_type_counts": dict(types),
            "payload_type_counts": dict(payload_types),
            "role_counts": dict(roles),
            "message_count": message_count,
            "latest_messages": _latest_messages(path, message_count=8),
        }
    )
    return meta


def _require_gate(route_id: str, args: Mapping[str, Any]) -> dict[str, Any] | None:
    if not str(args.get("idempotency_key") or "").strip():
        return _blocked(route_id, "idempotency_key_required", refusal_class="IDEMPOTENCY_KEY_REQUIRED")
    if str(args.get("confirmation") or "") != CONFIRMATION_TOKEN:
        return _blocked(route_id, "confirmation_required", refusal_class="CONFIRMATION_REQUIRED", data={"required_confirmation": CONFIRMATION_TOKEN})
    return None


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _codex_binary() -> str:
    candidates = [
        shutil.which("codex"),
        str(Path.home() / ".npm-global/bin/codex"),
        str(Path.home() / ".local/bin/codex"),
        "/usr/local/bin/codex",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return "codex"


def _stored_cwd(path: Path) -> str | None:
    meta = _metadata_from_file(path)
    cwd = str((meta.get("session_meta") or {}).get("cwd") or "").strip()
    if not cwd:
        return None
    cwd_path = Path(cwd).expanduser().resolve(strict=False)
    if not cwd_path.is_dir():
        return None
    return cwd_path.as_posix()


def _resume_sandbox(args: Mapping[str, Any]) -> str:
    values = {
        str(args.get("sandbox_mode") or "").strip(),
        str(args.get("sandbox") or "").strip(),
    }
    if "workspace-write" in values:
        return "workspace-write"
    return "read-only"


def _resume_driver_mode(args: Mapping[str, Any]) -> str:
    value = str(args.get("driver_mode") or args.get("resume_driver_mode") or "exec").strip().lower()
    aliases = {
        "": "exec",
        "exec": "exec",
        "codex_exec": "exec",
        "codex_exec_resume": "exec",
        "non_interactive": "exec",
        "non-interactive": "exec",
        "tui": "tui_inline",
        "tui_inline": "tui_inline",
        "tui-inline": "tui_inline",
        "interactive": "tui_inline",
        "codex_resume": "tui_inline",
    }
    if value not in aliases:
        raise ValueError("unsupported_resume_driver_mode")
    return aliases[value]


def _prompt_requests_workspace_write(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(term in lowered for term in ACTIVE_ROOT_PATCH_TERMS)


def _resume_sandbox_preflight(route_id: str, prompt: str, sandbox: str) -> dict[str, Any] | None:
    if _prompt_requests_workspace_write(prompt) and sandbox != "workspace-write":
        return _blocked(
            route_id,
            "active_root_patch_requires_workspace_write_sandbox",
            refusal_class="SANDBOX_MISMATCH",
            data={
                "requested_sandbox": sandbox,
                "required_sandbox": "workspace-write",
                "resume_possible": False,
                "send_route": "session_resume_send",
            },
        )
    return None


def _resume_argv(session_id: str, prompt: str, *, sandbox: str = "read-only") -> list[str]:
    return [
        _codex_binary(),
        "exec",
        "--sandbox",
        sandbox,
        "--color",
        "never",
        "resume",
        session_id,
        prompt,
    ]


def _resume_argv_for_driver(session_id: str, prompt: str, *, sandbox: str = "read-only", driver_mode: str = "exec") -> list[str]:
    if driver_mode == "tui_inline":
        return [
            _codex_binary(),
            "resume",
            "--no-alt-screen",
            "--sandbox",
            sandbox,
            session_id,
            prompt,
        ]
    return _resume_argv(session_id, prompt, sandbox=sandbox)


def _resume_driver_label(driver_mode: str) -> str:
    if driver_mode == "tui_inline":
        return "codex_resume_tui_inline_no_alt_screen"
    return "codex_exec_resume_non_interactive"


def _resume_env() -> dict[str, str]:
    return {
        **os.environ,
        "NO_COLOR": "1",
        "TERM": os.environ.get("TERM") if os.environ.get("TERM") not in {None, "", "dumb"} else "xterm-256color",
    }


def _run_tui_inline_pty(argv: list[str], *, cwd: str, timeout_seconds: int, env: Mapping[str, str]) -> tuple[int | None, bool, str, str]:
    master_fd, slave_fd = pty.openpty()
    try:
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 120, 0, 0))
    except Exception:
        pass
    output_chunks: list[bytes] = []
    proc: subprocess.Popen[bytes] | None = None
    timed_out = False
    answered_queries: set[bytes] = set()

    def answer_terminal_queries(chunk: bytes) -> None:
        replies: list[tuple[bytes, bytes]] = [
            (b"\x1b[6n", b"\x1b[1;1R"),
            (b"\x1b[c", b"\x1b[?1;2c"),
            (b"\x1b]10;?\x1b\\", b"\x1b]10;rgb:ffff/ffff/ffff\x1b\\"),
            (b"\x1b]11;?\x1b\\", b"\x1b]11;rgb:0000/0000/0000\x1b\\"),
        ]
        for query, reply in replies:
            if query in chunk and query not in answered_queries:
                try:
                    os.write(master_fd, reply)
                    answered_queries.add(query)
                except OSError:
                    pass
        if b"Hooks need review" in chunk and b"trusting" in chunk and b"hooks_continue_without_trusting" not in answered_queries:
            try:
                os.write(master_fd, b"\x1b[B\x1b[B\r")
                answered_queries.add(b"hooks_continue_without_trusting")
            except OSError:
                pass

    try:
        proc = subprocess.Popen(
            argv,
            cwd=cwd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            env=dict(env),
            start_new_session=True,
        )
        os.close(slave_fd)
        slave_fd = -1
        deadline = time.monotonic() + timeout_seconds
        while True:
            if proc.poll() is not None:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except Exception:
                    proc.terminate()
                break
            readable, _, _ = select.select([master_fd], [], [], min(0.25, max(0.01, remaining)))
            if readable:
                try:
                    chunk = os.read(master_fd, 8192)
                except OSError:
                    break
                if not chunk:
                    break
                output_chunks.append(chunk)
                answer_terminal_queries(chunk)
        drain_deadline = time.monotonic() + 1.0
        while time.monotonic() < drain_deadline:
            readable, _, _ = select.select([master_fd], [], [], 0.05)
            if not readable:
                break
            try:
                chunk = os.read(master_fd, 8192)
            except OSError:
                break
            if not chunk:
                break
            output_chunks.append(chunk)
        if timed_out and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                proc.kill()
        try:
            returncode = proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            returncode = None
        output = b"".join(output_chunks).decode("utf-8", errors="replace")
        return returncode, timed_out, output, ""
    finally:
        if slave_fd >= 0:
            try:
                os.close(slave_fd)
            except OSError:
                pass
        try:
            os.close(master_fd)
        except OSError:
            pass


def _resume_command_preview_payload(args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    prompt = _redact(args.get("prompt") or "", limit=8_000)
    path = _locate_session(session_id)
    payload = _base("session_resume_send_preview")
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found", "resume_possible": False})
        return payload
    cwd = _stored_cwd(path)
    sandbox = _resume_sandbox(args)
    driver_mode = _resume_driver_mode(args)
    sandbox_block = _resume_sandbox_preflight("session_resume_send_preview", prompt, sandbox)
    if sandbox_block:
        sandbox_block.update({"found": True, "session_id": session_id, "storage_path": path.as_posix(), "suggested_workdir": cwd})
        return sandbox_block
    argv = _resume_argv_for_driver(session_id, prompt, sandbox=sandbox, driver_mode=driver_mode)
    shell_command = " ".join(shlex.quote(part) for part in argv)
    payload.update(
        {
            "found": True,
            "session_id": session_id,
            "resume_possible": True,
            "resume_command_not_executed": True,
            "storage_path": path.as_posix(),
            "suggested_workdir": cwd,
            "prompt": prompt,
            "command_argv": argv,
            "shell_command": shell_command,
            "shell_command_with_cd": f"cd {shlex.quote(cwd)} && {shell_command}" if cwd else shell_command,
            "bounded_execution": {
                "mode": _resume_driver_label(driver_mode),
                "driver_mode": driver_mode,
                "sandbox": sandbox,
                "timeout_seconds_default": 180,
                "stdout_stderr_captured": True,
                "notes": [
                    "exec is the default non-interactive Codex resume driver.",
                    "tui_inline uses codex resume --no-alt-screen for cases where interactive continue behavior differs from codex exec resume.",
                ],
            },
        }
    )
    return payload


def _run_resume_command(
    argv: list[str],
    *,
    cwd: str,
    timeout_seconds: int,
    env: Mapping[str, str],
    driver_mode: str,
) -> tuple[int | None, bool, str, str]:
    if driver_mode == "tui_inline":
        return _run_tui_inline_pty(argv, cwd=cwd, timeout_seconds=timeout_seconds, env=env)
    completed = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        env=dict(env),
    )
    return completed.returncode, False, completed.stdout or "", completed.stderr or ""


def _run_paths(root: Path, session_id: str, idempotency_key: str) -> dict[str, Path]:
    run_id = _safe_idempotency_key(idempotency_key)
    base = root / RUNS_RELATIVE_ROOT / session_id
    run_dir = base / "runs" / run_id
    return {
        "base": base,
        "runs": base / "runs",
        "run_dir": run_dir,
        "stdout": run_dir / "stdout.txt",
        "stderr": run_dir / "stderr.txt",
        "receipt": run_dir / "run_receipt.json",
        "latest_status": base / "latest_status.json",
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_status_payload(root: Path, session_id: str) -> dict[str, Any]:
    base = root / RUNS_RELATIVE_ROOT / session_id
    receipts = []
    if (base / "runs").is_dir():
        for item in sorted((base / "runs").glob("*/run_receipt.json"), key=lambda p: (p.stat().st_mtime, p.as_posix()), reverse=True)[:20]:
            try:
                data = json.loads(item.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            receipts.append(
                {
                    "receipt_path": _repo_rel(root, item),
                    "created_at": data.get("created_at"),
                    "returncode": data.get("returncode"),
                    "timed_out": data.get("timed_out"),
                    "line_count_delta": data.get("line_count_delta"),
                    "message_count_delta": data.get("message_count_delta"),
                    "session_reply_found": data.get("session_reply_found"),
                    "stdout_path": data.get("stdout_path"),
                    "stderr_path": data.get("stderr_path"),
                    "driver_mode": data.get("driver_mode"),
                    "driver_label": data.get("driver_label"),
                }
            )
    payload = _base("session_resume_status")
    payload.update(
        {
            "session_id": session_id,
            "run_count": len(receipts),
            "latest_run": receipts[0] if receipts else None,
            "runs": receipts,
            "latest_status_path": _repo_rel(root, base / "latest_status.json"),
        }
    )
    return payload


def _resume_send(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_resume_send"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    session_id = _safe_session_id(args.get("session_id"))
    prompt = _redact(args.get("prompt") or "", limit=8_000)
    if not prompt:
        return _blocked(route_id, "prompt_required")
    sandbox = _resume_sandbox(args)
    sandbox_block = _resume_sandbox_preflight(route_id, prompt, sandbox)
    if sandbox_block:
        return sandbox_block
    path = _locate_session(session_id)
    if not path:
        payload = _base(route_id)
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    run_paths = _run_paths(root, session_id, str(args.get("idempotency_key") or ""))
    if run_paths["receipt"].is_file():
        receipt = json.loads(run_paths["receipt"].read_text(encoding="utf-8"))
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, run_paths["receipt"]), "receipt": receipt})
        return payload
    before = _profile(path)
    before_line_count = int(before.get("line_count") or 0)
    before_message_count = int(before.get("message_count") or 0)
    cwd = _stored_cwd(path) or root.as_posix()
    timeout_seconds = max(10, min(int(args.get("timeout_seconds") or 180), 600))
    driver_mode = _resume_driver_mode(args)
    argv = _resume_argv_for_driver(session_id, prompt, sandbox=sandbox, driver_mode=driver_mode)
    started_at = _now()
    timed_out = False
    returncode: int | None = None
    stdout = ""
    stderr = ""
    try:
        returncode, timed_out, stdout, stderr = _run_resume_command(
            argv,
            cwd=cwd,
            timeout_seconds=timeout_seconds,
            env=_resume_env(),
            driver_mode=driver_mode,
        )
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
    run_paths["run_dir"].mkdir(parents=True, exist_ok=True)
    run_paths["stdout"].write_text(_redact(stdout, limit=120_000), encoding="utf-8")
    run_paths["stderr"].write_text(_redact(stderr, limit=120_000), encoding="utf-8")
    after = _profile(path)
    after_line_count = int(after.get("line_count") or 0)
    after_message_count = int(after.get("message_count") or 0)
    line_delta = after_line_count - before_line_count
    message_delta = after_message_count - before_message_count
    tail_start = max(1, after_line_count - 80)
    tail = _transcript_slice({"session_id": session_id, "start_line": tail_start, "line_count": 90, "max_bytes": 90_000})
    needle = "SESSION_RESUME_BRIDGE_SMOKE_OK"
    reply_found = needle in json.dumps(tail, sort_keys=True) or needle in stdout or needle in stderr
    receipt = {
        "schema_id": "ion.codex_session_resume_run_receipt.v1_candidate",
        "created_at": _now(),
        "started_at": started_at,
        "session_id": session_id,
        **AUTHORITY_FALSE,
        "source_of_truth_classification": "durable_ion_receipt",
        "non_claims": [
            *NON_CLAIMS,
            "This route executed bounded local Codex CLI resume, not direct UI control.",
            f"The resumed Codex session ran through { _resume_driver_label(driver_mode) } with an explicit bounded sandbox.",
            f"The resumed Codex session sandbox was {sandbox}.",
        ],
        "storage_path": path.as_posix(),
        "cwd": cwd,
        "command_argv_redacted": [_redact(part, limit=2_000) for part in argv],
        "shell_command_redacted": " ".join(shlex.quote(_redact(part, limit=2_000)) for part in argv),
        "driver_mode": driver_mode,
        "driver_label": _resume_driver_label(driver_mode),
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "returncode": returncode,
        "stdout_path": _repo_rel(root, run_paths["stdout"]),
        "stderr_path": _repo_rel(root, run_paths["stderr"]),
        "stdout_excerpt": _redact(stdout, limit=2_000),
        "stderr_excerpt": _redact(stderr, limit=2_000),
        "before_line_count": before_line_count,
        "after_line_count": after_line_count,
        "line_count_delta": line_delta,
        "before_message_count": before_message_count,
        "after_message_count": after_message_count,
        "message_count_delta": message_delta,
        "session_reply_found": reply_found,
        "tail_harvest": tail,
    }
    _write_json(run_paths["receipt"], receipt)
    status = _run_status_payload(root, session_id)
    _write_json(run_paths["latest_status"], status)
    payload = _base(route_id, ok=(returncode == 0 and not timed_out))
    payload.update(
        {
            "found": True,
            "session_id": session_id,
            "executed": True,
            "returncode": returncode,
            "timed_out": timed_out,
            "receipt_path": _repo_rel(root, run_paths["receipt"]),
            "stdout_path": _repo_rel(root, run_paths["stdout"]),
            "stderr_path": _repo_rel(root, run_paths["stderr"]),
            "line_count_delta": line_delta,
            "message_count_delta": message_delta,
            "session_reply_found": reply_found,
            "driver_mode": driver_mode,
            "driver_label": _resume_driver_label(driver_mode),
            "latest_status_path": _repo_rel(root, run_paths["latest_status"]),
            "mutates_active_state": True,
        }
    )
    if returncode != 0 or timed_out:
        payload["finding"] = "codex_resume_send_failed_or_timed_out"
    return payload


def _resume_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    return _run_status_payload(root, session_id)


def _resume_harvest(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    status = _run_status_payload(root, session_id)
    latest = status.get("latest_run") if isinstance(status.get("latest_run"), Mapping) else None
    payload = _base("session_resume_harvest")
    payload.update({"session_id": session_id, "latest_run": latest})
    if latest and latest.get("receipt_path"):
        receipt_path = root / str(latest["receipt_path"])
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except Exception:
            receipt = {}
        payload.update(
            {
                "receipt_path": latest.get("receipt_path"),
                "tail_harvest": receipt.get("tail_harvest"),
                "line_count_delta": receipt.get("line_count_delta"),
                "message_count_delta": receipt.get("message_count_delta"),
                "session_reply_found": receipt.get("session_reply_found"),
            }
        )
    else:
        payload["finding"] = "no_resume_runs_recorded"
    return payload


def _discovery(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_store_discovery"
    payload = _base(route_id)
    session_id = str(args.get("session_id") or "").strip()
    if session_id:
        session_id = _safe_session_id(session_id)
    homes = []
    for codex_home in _codex_home_candidates():
        sessions = codex_home / "sessions"
        homes.append(
            {
                "path": codex_home.as_posix(),
                "exists": codex_home.is_dir(),
                "history_jsonl_exists": (codex_home / "history.jsonl").is_file(),
                "session_index_jsonl_exists": (codex_home / "session_index.jsonl").is_file(),
                "sessions_dir_exists": sessions.is_dir(),
                "session_file_count": len(list(sessions.rglob("*.jsonl"))) if sessions.is_dir() else 0,
                "auth_json_ignored": (codex_home / "auth.json").is_file(),
            }
        )
    found_path = _locate_session(session_id) if session_id else None
    payload.update(
        {
            "codex_home_candidates": homes,
            "session_roots": [root.as_posix() for root in _session_roots()],
            "searched_auth_json": False,
            "session_id": session_id or None,
            "session_found": bool(found_path),
            "session_storage_path": found_path.as_posix() if found_path else None,
        }
    )
    return payload


def _session_list(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_list"
    limit = max(1, min(int(args.get("limit") or 50), 200))
    sessions = []
    for path in _iter_session_files(limit=limit):
        try:
            meta = _metadata_from_file(path)
        except Exception:
            continue
        sessions.append(
            {
                "session_id": meta.get("session_id"),
                "storage_path": meta.get("storage_path"),
                "cwd": (meta.get("session_meta") or {}).get("cwd"),
                "originator": (meta.get("session_meta") or {}).get("originator"),
                "cli_version": (meta.get("session_meta") or {}).get("cli_version"),
                "size_bytes": meta.get("size_bytes"),
                "line_count": meta.get("line_count"),
                "latest_timestamp": meta.get("latest_timestamp"),
            }
        )
    payload = _base(route_id)
    payload.update({"session_count": len(sessions), "sessions": sessions})
    return payload


def _metadata(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_metadata"
    session_id = _safe_session_id(args.get("session_id"))
    path = _locate_session(session_id)
    payload = _base(route_id)
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    payload.update(_metadata_from_file(path))
    return payload


def _transcript_profile(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_transcript_profile"
    session_id = _safe_session_id(args.get("session_id"))
    path = _locate_session(session_id)
    payload = _base(route_id)
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    payload.update(_profile(path))
    return payload


def _transcript_slice(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_transcript_slice"
    session_id = _safe_session_id(args.get("session_id"))
    path = _locate_session(session_id)
    payload = _base(route_id)
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    start_line = max(1, int(args.get("start_line") or args.get("start") or 1))
    line_count = max(1, min(int(args.get("line_count") or 50), MAX_LINE_COUNT))
    max_bytes = max(1_000, min(int(args.get("max_bytes") or 64_000), MAX_BYTES))
    records: list[dict[str, Any]] = []
    consumed = 0
    for line_no, obj in _read_jsonl(path):
        if line_no < start_line:
            continue
        if len(records) >= line_count or consumed >= max_bytes:
            break
        view = _message_view(line_no, obj, text_limit=1_200)
        view["payload_summary"] = _sanitize(obj.get("payload"), limit=1_000)
        record_size = len(json.dumps(view, sort_keys=True))
        if consumed + record_size > max_bytes and records:
            break
        consumed += record_size
        records.append(view)
    payload.update(
        {
            "found": True,
            "session_id": session_id,
            "storage_path": path.as_posix(),
            "start_line": start_line,
            "line_count_requested": line_count,
            "max_bytes": max_bytes,
            "returned_record_count": len(records),
            "returned_bytes_approx": consumed,
            "records": records,
            "bounded": True,
        }
    )
    return payload


def _session_find(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_find"
    session_id = _safe_session_id(args.get("session_id"))
    query = str(args.get("query") or "").strip()
    if not query:
        return _blocked(route_id, "query_required")
    path = _locate_session(session_id)
    payload = _base(route_id)
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    max_matches = max(1, min(int(args.get("max_matches") or 20), 100))
    matches: list[dict[str, Any]] = []
    query_lower = query.lower()
    for line_no, obj in _read_jsonl(path):
        payload_obj = obj.get("payload")
        text = json.dumps(_sanitize(payload_obj, limit=2_000), sort_keys=True)
        if query_lower not in text.lower():
            continue
        matches.append(
            {
                "line_no": line_no,
                "timestamp": _redact(obj.get("timestamp"), limit=80),
                "record_type": _redact(obj.get("type"), limit=80),
                "excerpt": _redact(text, limit=1_200),
            }
        )
        if len(matches) >= max_matches:
            break
    payload.update({"found": True, "session_id": session_id, "query": _redact(query, limit=200), "match_count": len(matches), "matches": matches})
    return payload


def _summary(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_summary"
    session_id = _safe_session_id(args.get("session_id"))
    path = _locate_session(session_id)
    payload = _base(route_id)
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    profile = _profile(path)
    latest = _latest_messages(path, message_count=max(1, min(int(args.get("message_count") or 10), MAX_MESSAGE_COUNT)))
    payload.update(
        {
            "found": True,
            "session_id": session_id,
            "storage_path": path.as_posix(),
            "cwd": (profile.get("session_meta") or {}).get("cwd"),
            "originator": (profile.get("session_meta") or {}).get("originator"),
            "cli_version": (profile.get("session_meta") or {}).get("cli_version"),
            "model_provider": (profile.get("session_meta") or {}).get("model_provider"),
            "size_bytes": profile.get("size_bytes"),
            "line_count": profile.get("line_count"),
            "message_count": profile.get("message_count"),
            "role_counts": profile.get("role_counts"),
            "latest_messages": latest,
            "latest_user_message": next((item for item in reversed(latest) if item.get("role") == "user" or item.get("payload_type") == "user_message"), None),
            "latest_assistant_message": next((item for item in reversed(latest) if item.get("role") == "assistant" or item.get("payload_type") == "agent_message"), None),
            "summary_method": "deterministic_metadata_and_latest_message_projection_no_model_call",
        }
    )
    return payload


def _resume_preview(args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_resume_command_preview"
    session_id = _safe_session_id(args.get("session_id"))
    prompt = str(args.get("prompt") or "").strip()
    path = _locate_session(session_id)
    payload = _base(route_id)
    if not path:
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found", "resume_possible": False})
        return payload
    meta = _metadata_from_file(path)
    cwd = str((meta.get("session_meta") or {}).get("cwd") or "")
    argv = ["codex", "resume", session_id]
    if prompt:
        argv.append(_redact(prompt, limit=2_000))
    shell_command = " ".join(shlex.quote(part) for part in argv)
    payload.update(
        {
            "found": True,
            "session_id": session_id,
            "resume_possible": True,
            "resume_command_not_executed": True,
            "command_argv": argv,
            "shell_command": shell_command,
            "suggested_workdir": cwd or None,
            "shell_command_with_cd": f"cd {shlex.quote(cwd)} && {shell_command}" if cwd else shell_command,
            "send_prompt_if_executed": bool(prompt),
            "supports_prompt_argument": True,
            "support_source": "local_codex_resume_help_observed",
        }
    )
    return payload


def _harvest(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "session_harvest_to_ion"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    session_id = _safe_session_id(args.get("session_id"))
    path = _locate_session(session_id)
    if not path:
        payload = _base(route_id)
        payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
        return payload
    key_slug = _safe_idempotency_key(args.get("idempotency_key"))
    harvest_dir = root / HARVEST_RELATIVE_ROOT / session_id
    receipts_dir = harvest_dir / "receipts"
    harvest_dir.mkdir(parents=True, exist_ok=True)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipts_dir / f"session_harvest_to_ion_{key_slug}_receipt.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, receipt_path), "receipt": receipt})
        return payload
    summary = _summary({"session_id": session_id, "message_count": args.get("message_count") or 10})
    slice_payload = _transcript_slice(
        {
            "session_id": session_id,
            "start_line": int(args.get("start_line") or max(1, int(summary.get("line_count") or 1) - 40)),
            "line_count": int(args.get("line_count") or 40),
            "max_bytes": int(args.get("max_bytes") or 80_000),
        }
    )
    harvest_path = harvest_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{key_slug}.json"
    harvest = {
        "schema_id": "ion.codex_session_store_harvest.v1_candidate",
        "created_at": _now(),
        "session_id": session_id,
        **AUTHORITY_FALSE,
        "authority": dict(AUTHORITY_FALSE),
        "source_of_truth_classification": "ui_session_evidence",
        "non_claims": list(NON_CLAIMS),
        "source_storage_path": path.as_posix(),
        "source_sha256": _sha256(path),
        "summary": summary,
        "transcript_slice": slice_payload,
    }
    harvest_path.write_text(json.dumps(harvest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "schema_id": "ion.codex_session_store_harvest_receipt.v1_candidate",
        "created_at": _now(),
        "session_id": session_id,
        **AUTHORITY_FALSE,
        "source_of_truth_classification": "durable_ion_receipt",
        "non_claims": list(NON_CLAIMS),
        "idempotency_key": _redact(args.get("idempotency_key"), limit=200),
        "source_storage_path": path.as_posix(),
        "harvest_path": _repo_rel(root, harvest_path),
        "harvest_sha256": _sha256(harvest_path),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload = _base(route_id)
    payload.update(
        {
            "mutates_active_state": True,
            "found": True,
            "session_id": session_id,
            "harvest_path": _repo_rel(root, harvest_path),
            "receipt_path": _repo_rel(root, receipt_path),
        }
    )
    return payload


def invoke_codex_session_store_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    try:
        if route_id == "session_store_discovery":
            return _discovery(args)
        if route_id == "session_list":
            return _session_list(args)
        if route_id == "session_metadata":
            return _metadata(args)
        if route_id == "session_transcript_profile":
            return _transcript_profile(args)
        if route_id == "session_transcript_slice":
            return _transcript_slice(args)
        if route_id == "session_find":
            return _session_find(args)
        if route_id == "session_summary":
            return _summary(args)
        if route_id == "session_resume_command_preview":
            return _resume_preview(args)
        if route_id == "session_resume_send_preview":
            return _resume_command_preview_payload(args)
        if route_id == "session_resume_send":
            return _resume_send(shell_root, args)
        if route_id == "session_resume_status":
            return _resume_status(shell_root, args)
        if route_id == "session_resume_harvest":
            return _resume_harvest(shell_root, args)
        if route_id == "session_harvest_to_ion":
            return _harvest(shell_root, args)
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="SCHEMA_INVALID")
    return _blocked(route_id, "route_not_supported_by_codex_session_store", refusal_class="BRANCH_ROUTE_NOT_FOUND", data={"route_id": route_id})
