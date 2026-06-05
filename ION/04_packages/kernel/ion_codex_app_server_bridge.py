"""ION-safe bridge over the local Codex app-server JSON-RPC protocol.

This bridge is the preferred control surface for Codex saved sessions because
it talks to Codex's thread API instead of trying to emulate a terminal UI.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import selectors
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.codex_app_server_bridge.v1_candidate"
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
CODEX_APP_SERVER_BINARY_ENV = "ION_CODEX_APP_SERVER_BINARY"
CODEX_APP_SERVER_LISTEN_URL = "stdio://"
THREAD_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$")
CANONICAL_CARRIER_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*_[0-9a-f]{12}$")
RUNS_RELATIVE_ROOT = Path("ION/05_context/current/chatgpt_connector/codex_app_server_runs")
PERSISTENT_CARRIERS_RELATIVE_ROOT = Path("ION/05_context/current/chatgpt_connector/codex_app_server_persistent_carriers")
MAX_TEXT = 4_000
TERMINAL_TURN_STATUSES = {"completed", "failed", "error", "errored", "cancelled", "canceled", "interrupted"}
PERSISTENT_CARRIER_TERMINAL_STATES = {
    "completed",
    "exactturnnotvisible",
    "failed",
    "error",
    "errored",
    "cancelled",
    "canceled",
    "interrupted",
    "processstartfailed",
    "stopped",
    "timeout",
    "usagelimited",
    "visiblenotcompleted",
}
FORBIDDEN_WRITABLE_ROOT_PARTS = {".git", ".ssh", ".gnupg", ".config", ".codex"}

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "materialization_claim": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_push_authority": False,
    "deletion_authority": False,
}

NON_CLAIMS = [
    "This bridge uses Codex app-server JSON-RPC over stdio, not direct TUI control.",
    "Read routes may launch a short-lived local app-server process but do not start a model turn.",
    "turn_start is confirmation-gated because it can append to a Codex thread and execute a model turn.",
    "Receipts are candidate ION evidence only, not accepted state.",
]


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


def _redact(value: Any, *, limit: int = MAX_TEXT) -> str:
    text = str(value or "")
    text = re.sub(r"sk-[A-Za-z0-9_-]{10,}", "sk-***REDACTED***", text)
    text = re.sub(r"gh[pousr]_[A-Za-z0-9_]{16,}", "gh***_***REDACTED***", text)
    text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", "Bearer ***REDACTED***", text)
    text = re.sub(
        r"(?i)\b([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|AUTHORIZATION)[A-Z0-9_]*)\s*[:=]\s*['\"]?[^ \n\r\t,'\"]+",
        lambda match: f"{match.group(1)}=***REDACTED***",
        text,
    )
    if len(text) > limit:
        return text[:limit] + "...[truncated]"
    return text


def _sanitize(value: Any, *, limit: int = MAX_TEXT) -> Any:
    if isinstance(value, Mapping):
        output: dict[str, Any] = {}
        for key, item in value.items():
            key_text = _redact(key, limit=160)
            if key_text in {"baseInstructions", "base_instructions", "instructions", "developerInstructions", "encrypted_content"}:
                output[key_text] = {"omitted": True, "reason": "large_or_sensitive_instruction_surface"}
            else:
                output[key_text] = _sanitize(item, limit=limit)
        return output
    if isinstance(value, list):
        return [_sanitize(item, limit=limit) for item in value[:80]]
    if isinstance(value, str):
        return _redact(value, limit=limit)
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return _redact(value, limit=limit)


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


def _safe_thread_id(value: Any) -> str:
    thread_id = str(value or "").strip()
    if not thread_id:
        raise ValueError("thread_id_required")
    if "/" in thread_id or "\\" in thread_id or ".." in thread_id:
        raise ValueError("unsafe_thread_id")
    if not THREAD_ID_RE.match(thread_id):
        raise ValueError("unsafe_thread_id")
    return thread_id


def _safe_turn_id(value: Any) -> str:
    turn_id = str(value or "").strip()
    if not turn_id:
        raise ValueError("turn_id_required")
    if "/" in turn_id or "\\" in turn_id or ".." in turn_id:
        raise ValueError("unsafe_turn_id")
    if not THREAD_ID_RE.match(turn_id):
        raise ValueError("unsafe_turn_id")
    return turn_id


def _safe_idempotency_key(value: Any) -> str:
    key = str(value or "").strip()
    if not key:
        raise ValueError("idempotency_key_required")
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9_.:-]+", "_", key).strip("._:-") or "key"
    if "/" in slug or "\\" in slug or ".." in slug:
        slug = "key"
    return f"{slug[:80]}_{digest}"


def _require_gate(route_id: str, args: Mapping[str, Any]) -> dict[str, Any] | None:
    if not str(args.get("idempotency_key") or "").strip():
        return _blocked(route_id, "idempotency_key_required", refusal_class="IDEMPOTENCY_KEY_REQUIRED")
    if str(args.get("confirmation") or "") != CONFIRMATION_TOKEN:
        return _blocked(route_id, "confirmation_required", refusal_class="CONFIRMATION_REQUIRED", data={"required_confirmation": CONFIRMATION_TOKEN})
    return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _app_server_env() -> dict[str, str]:
    return {**os.environ, "NO_COLOR": "1", "TERM": os.environ.get("TERM") or "xterm-256color"}


def _resolve_executable_candidate(candidate: str | None) -> str | None:
    if not candidate:
        return None
    path = Path(candidate).expanduser()
    if path.is_file():
        return path.as_posix()
    resolved = shutil.which(candidate)
    if resolved and Path(resolved).is_file():
        return resolved
    return None


def _codex_binary_candidates() -> list[str]:
    raw_candidates = [
        os.environ.get(CODEX_APP_SERVER_BINARY_ENV),
        str(Path.home() / ".npm-global/bin/codex"),
        str(Path.home() / ".local/bin/codex"),
        shutil.which("codex"),
        "/usr/local/bin/codex",
    ]
    candidates: list[str] = []
    seen: set[str] = set()
    for candidate in raw_candidates:
        resolved = _resolve_executable_candidate(candidate)
        if resolved and resolved not in seen:
            candidates.append(resolved)
            seen.add(resolved)
    return candidates


def _codex_binary_supports_app_server_stdio(candidate: str) -> bool:
    try:
        probe = subprocess.run(
            [candidate, "app-server", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=5,
            env=_app_server_env(),
        )
    except Exception:
        return False
    output = probe.stdout or ""
    return probe.returncode == 0 and "--listen" in output and CODEX_APP_SERVER_LISTEN_URL in output


def _codex_binary() -> str:
    candidates = _codex_binary_candidates()
    for candidate in candidates:
        if _codex_binary_supports_app_server_stdio(candidate):
            return candidate
    return candidates[0] if candidates else "codex"


def _app_server_command() -> list[str]:
    return [_codex_binary(), "app-server", "--listen", CODEX_APP_SERVER_LISTEN_URL]


def _jsonrpc_initialize() -> dict[str, Any]:
    return {
        "id": "initialize",
        "method": "initialize",
        "params": {
            "clientInfo": {"name": "ion-codex-app-server-bridge", "version": "0.1"},
            "capabilities": {"experimentalApi": True},
        },
    }


def _run_app_server_jsonrpc(
    requests: list[Mapping[str, Any]],
    *,
    timeout_seconds: int = 12,
    wait_for_methods: set[str] | None = None,
    process_factory: Any | None = None,
    command: list[str] | None = None,
) -> dict[str, Any]:
    request_ids = {request.get("id") for request in requests if request.get("id") is not None}
    command = list(command or _app_server_command())
    factory = process_factory or subprocess.Popen
    proc = factory(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd(),
        env=_app_server_env(),
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None
    for request in requests:
        proc.stdin.write(json.dumps(dict(request), separators=(",", ":")) + "\n")
        proc.stdin.flush()
    responses: list[dict[str, Any]] = []
    notifications: list[dict[str, Any]] = []
    stderr_lines: list[str] = []
    deadline = time.monotonic() + max(1, min(timeout_seconds, 600))
    pending_ids = set(request_ids)
    wait_for_methods = set(wait_for_methods or set())
    seen_methods: set[str] = set()
    selector = selectors.DefaultSelector()
    use_selector = True
    try:
        selector.register(proc.stdout, selectors.EVENT_READ)
    except Exception:
        use_selector = False
    try:
        while time.monotonic() < deadline and (pending_ids or (wait_for_methods - seen_methods)):
            if use_selector:
                ready = selector.select(timeout=0.25)
                if not ready:
                    if proc.poll() is not None:
                        break
                    continue
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                if not use_selector:
                    time.sleep(0.01)
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                notifications.append({"method": "stdout/unparseable", "params": {"line": _redact(line, limit=1_000)}})
                continue
            if isinstance(message, Mapping) and "id" in message:
                responses.append(dict(message))
                pending_ids.discard(message.get("id"))
            elif isinstance(message, Mapping) and "method" in message:
                notifications.append(dict(message))
                seen_methods.add(str(message.get("method") or ""))
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
    finally:
        try:
            selector.close()
        except Exception:
            pass
        try:
            stderr = proc.stderr.read()
        except Exception:
            stderr = ""
        if stderr:
            stderr_lines = [_redact(line, limit=1_000) for line in stderr.splitlines()[:20]]
    response_by_id = {message.get("id"): message for message in responses}
    return {
        "ok": not bool(pending_ids),
        "command_argv": command,
        "responses": responses,
        "response_by_id": response_by_id,
        "notifications": notifications[:80],
        "pending_request_ids": sorted(str(item) for item in pending_ids),
        "stderr_lines": stderr_lines,
        "timed_out": bool(pending_ids or (wait_for_methods - seen_methods)),
    }


def _result_for_id(rpc: Mapping[str, Any], request_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    response = (rpc.get("response_by_id") or {}).get(request_id)
    if not isinstance(response, Mapping):
        return None, {"finding": "app_server_response_missing", "request_id": request_id}
    if response.get("error"):
        return None, {"finding": "app_server_response_error", "request_id": request_id, "error": _sanitize(response.get("error"), limit=1_200)}
    result = response.get("result")
    return (dict(result), None) if isinstance(result, Mapping) else ({}, None)


def _thread_row(thread: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "thread_id": thread.get("id") or thread.get("threadId"),
        "session_id": thread.get("sessionId"),
        "cwd": thread.get("cwd"),
        "status": _sanitize(thread.get("status"), limit=500),
        "title": _redact(thread.get("title"), limit=300),
        "updated_at": thread.get("updatedAt"),
        "created_at": thread.get("createdAt"),
        "source": thread.get("threadSource") or thread.get("originator"),
        "model_provider": thread.get("modelProvider"),
    }


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _raw_writable_roots(args: Mapping[str, Any]) -> list[str]:
    raw = args.get("writable_roots")
    if raw is None:
        raw = args.get("writableRoots")
    return [str(item).strip() for item in raw or [] if str(item).strip()]


def _normalize_writable_roots(args: Mapping[str, Any], *, root: Path | None = None) -> tuple[list[str], list[dict[str, str]]]:
    base = Path(root or args.get("cwd") or ".").expanduser().resolve()
    roots: list[str] = []
    notes: list[dict[str, str]] = []
    for raw in _raw_writable_roots(args):
        raw_path = Path(raw).expanduser()
        resolved = raw_path.resolve(strict=False) if raw_path.is_absolute() else (base / raw_path).resolve(strict=False)
        if not _is_relative_to(resolved, base):
            raise ValueError("writable_root_outside_active_root")
        if any(part in FORBIDDEN_WRITABLE_ROOT_PARTS for part in resolved.parts):
            raise ValueError("forbidden_writable_root")
        roots.append(resolved.as_posix())
        notes.append({"input": raw, "resolved": resolved.as_posix(), "base": base.as_posix()})
    return roots, notes


def _sandbox_policy_details(args: Mapping[str, Any], *, root: Path | None = None) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    sandbox = str(args.get("sandbox") or args.get("sandbox_mode") or "").strip()
    if not sandbox:
        return None, []
    if sandbox == "read-only":
        return {"type": "readOnly", "networkAccess": False}, []
    if sandbox == "workspace-write":
        roots, notes = _normalize_writable_roots(args, root=root)
        return {"type": "workspaceWrite", "writableRoots": roots, "networkAccess": False}, notes
    raise ValueError("unsupported_sandbox_mode")


def _sandbox_policy(args: Mapping[str, Any], *, root: Path | None = None) -> dict[str, Any] | None:
    policy, _notes = _sandbox_policy_details(args, root=root)
    return policy


def _turn_input(prompt: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": prompt, "text_elements": []}]


def _thread_list(args: Mapping[str, Any]) -> dict[str, Any]:
    limit = max(1, min(int(args.get("limit") or 20), 100))
    source_kinds = args.get("source_kinds") or args.get("sourceKinds") or ["cli", "appServer", "exec"]
    rpc = _run_app_server_jsonrpc(
        [
            _jsonrpc_initialize(),
            {
                "id": "thread_list",
                "method": "thread/list",
                "params": {"limit": limit, "sourceKinds": source_kinds, "useStateDbOnly": bool(args.get("use_state_db_only") or False)},
            },
        ],
        timeout_seconds=max(3, min(int(args.get("timeout_seconds") or 12), 60)),
    )
    result, error = _result_for_id(rpc, "thread_list")
    payload = _base("thread_list", ok=not bool(error), finding=(error or {}).get("finding"))
    if error:
        payload.update(error)
        payload["rpc"] = _sanitize(rpc, limit=1_200)
        return payload
    data = result.get("data") if isinstance(result, Mapping) else []
    threads = [_thread_row(item) for item in data if isinstance(item, Mapping)]
    payload.update({"thread_count": len(threads), "threads": threads, "app_server_notifications": _sanitize(rpc.get("notifications"), limit=1_200)})
    return payload


def _thread_loaded_list(args: Mapping[str, Any]) -> dict[str, Any]:
    limit = max(1, min(int(args.get("limit") or 50), 100))
    rpc = _run_app_server_jsonrpc(
        [_jsonrpc_initialize(), {"id": "loaded", "method": "thread/loaded/list", "params": {"limit": limit}}],
        timeout_seconds=max(3, min(int(args.get("timeout_seconds") or 12), 60)),
    )
    result, error = _result_for_id(rpc, "loaded")
    payload = _base("thread_loaded_list", ok=not bool(error), finding=(error or {}).get("finding"))
    if error:
        payload.update(error)
        return payload
    data = result.get("data") if isinstance(result, Mapping) else []
    payload.update({"loaded_thread_count": len(data or []), "threads": [_thread_row(item) for item in data if isinstance(item, Mapping)]})
    return payload


def _thread_resume_preview(args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    params = {
        "threadId": thread_id,
        "excludeTurns": bool(args.get("exclude_turns", True)),
        "initialTurnsPage": {
            "limit": max(1, min(int(args.get("turn_limit") or 3), 20)),
            "sortDirection": "desc",
            "itemsView": str(args.get("items_view") or "summary"),
        },
    }
    payload = _base("thread_resume_preview")
    payload.update({"thread_id": thread_id, "resume_not_executed": True, "jsonrpc_request": {"method": "thread/resume", "params": params}})
    return payload


def _thread_resume(args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    turn_limit = max(1, min(int(args.get("turn_limit") or 3), 20))
    params = {
        "threadId": thread_id,
        "excludeTurns": bool(args.get("exclude_turns", True)),
        "initialTurnsPage": {"limit": turn_limit, "sortDirection": "desc", "itemsView": str(args.get("items_view") or "summary")},
    }
    if args.get("cwd"):
        params["cwd"] = str(args.get("cwd"))
    if args.get("sandbox") or args.get("sandbox_mode"):
        params["sandbox"] = _sandbox_policy(args)
    rpc = _run_app_server_jsonrpc(
        [_jsonrpc_initialize(), {"id": "resume", "method": "thread/resume", "params": params}],
        timeout_seconds=max(3, min(int(args.get("timeout_seconds") or 15), 90)),
    )
    result, error = _result_for_id(rpc, "resume")
    payload = _base("thread_resume", ok=not bool(error), finding=(error or {}).get("finding"))
    if error:
        payload.update(error)
        payload["rpc"] = _sanitize(rpc, limit=1_200)
        return payload
    thread = result.get("thread") if isinstance(result, Mapping) else {}
    initial_page = result.get("initialTurnsPage") if isinstance(result, Mapping) else None
    payload.update(
        {
            "thread": _thread_row(thread if isinstance(thread, Mapping) else {}),
            "model": result.get("model"),
            "model_provider": result.get("modelProvider"),
            "cwd": result.get("cwd"),
            "sandbox": _sanitize(result.get("sandbox"), limit=1_000),
            "initial_turns_count": len((initial_page or {}).get("data") or []) if isinstance(initial_page, Mapping) else 0,
            "initial_turns_page": _sanitize(initial_page, limit=4_000),
            "app_server_notifications": _sanitize(rpc.get("notifications"), limit=1_200),
        }
    )
    return payload


def _thread_read(args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    rpc = _run_app_server_jsonrpc(
        [_jsonrpc_initialize(), {"id": "read", "method": "thread/read", "params": {"threadId": thread_id, "includeTurns": bool(args.get("include_turns") or False)}}],
        timeout_seconds=max(3, min(int(args.get("timeout_seconds") or 15), 90)),
    )
    result, error = _result_for_id(rpc, "read")
    payload = _base("thread_read", ok=not bool(error), finding=(error or {}).get("finding"))
    if error:
        payload.update(error)
        return payload
    thread = result.get("thread") if isinstance(result, Mapping) else {}
    payload.update({"thread": _sanitize(thread, limit=max(2_000, min(int(args.get("max_bytes") or 20_000), 80_000)))})
    return payload


def _thread_turns_list(args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    params = {
        "threadId": thread_id,
        "limit": max(1, min(int(args.get("limit") or 5), 50)),
        "sortDirection": str(args.get("sort_direction") or "desc"),
        "itemsView": str(args.get("items_view") or "summary"),
    }
    rpc = _run_app_server_jsonrpc(
        [_jsonrpc_initialize(), {"id": "turns", "method": "thread/turns/list", "params": params}],
        timeout_seconds=max(3, min(int(args.get("timeout_seconds") or 15), 90)),
    )
    result, error = _result_for_id(rpc, "turns")
    payload = _base("thread_turns_list", ok=not bool(error), finding=(error or {}).get("finding"))
    if error:
        payload.update(error)
        return payload
    turns = (result or {}).get("data") or []
    payload.update({"thread_id": thread_id, "turn_count": len(turns), "turns": _sanitize(turns, limit=max(2_000, min(int(args.get("max_bytes") or 20_000), 80_000)))})
    return payload


def _thread_turn_read_by_id(args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    turn_id = _safe_turn_id(args.get("turn_id"))
    max_bytes = max(2_000, min(int(args.get("max_bytes") or 20_000), 80_000))
    turns_payload = _thread_turns_list(
        {
            "thread_id": thread_id,
            "limit": 50,
            "sort_direction": "desc",
            "items_view": str(args.get("items_view") or "summary"),
            "max_bytes": max_bytes,
            "timeout_seconds": int(args.get("timeout_seconds") or 15),
        }
    )
    turns = turns_payload.get("turns") if isinstance(turns_payload, Mapping) else []
    matched_turn = _match_turn_by_id(turns, turn_id)
    payload = _base("thread_turn_read_by_id", ok=bool(matched_turn), finding=None if matched_turn else "turn_not_found")
    payload.update(
        {
            "thread_id": thread_id,
            "turn_id": turn_id,
            "exact_match_required": True,
            "matched": bool(matched_turn),
            "matched_turn": _sanitize(matched_turn, limit=max_bytes) if matched_turn else None,
            "matched_turn_status": _turn_status_text(matched_turn) if matched_turn else None,
            "source_turn_count": turns_payload.get("turn_count") if isinstance(turns_payload, Mapping) else None,
            "scanned_turn_ids": _scanned_turn_ids(turns)[:50],
            "thread_turns_probe": _sanitize(turns_payload, limit=4_000),
        }
    )
    if not matched_turn:
        payload["refusal_class"] = "NOT_FOUND"
    return payload


def _turn_start_preview(args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    prompt = _redact(args.get("prompt") or "", limit=8_000)
    if not prompt:
        return _blocked("turn_start_preview", "prompt_required")
    params: dict[str, Any] = {"threadId": thread_id, "input": _turn_input(prompt)}
    sandbox = _sandbox_policy(args)
    if sandbox:
        params["sandboxPolicy"] = sandbox
    if args.get("cwd"):
        params["cwd"] = str(args.get("cwd"))
    payload = _base("turn_start_preview")
    payload.update({"thread_id": thread_id, "turn_start_not_executed": True, "jsonrpc_sequence": [{"method": "thread/resume"}, {"method": "turn/start", "params": params}]})
    return payload


def _run_paths(root: Path, thread_id: str, key: str) -> dict[str, Path]:
    run_id = _safe_idempotency_key(key)
    base = root / RUNS_RELATIVE_ROOT / thread_id
    run_dir = base / "runs" / run_id
    return {"base": base, "run_dir": run_dir, "receipt": run_dir / "run_receipt.json", "latest_status": base / "latest_status.json"}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return dict(data) if isinstance(data, Mapping) else None


def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(payload), separators=(",", ":"), sort_keys=True) + "\n")


def _turn_id_from_result(result: Mapping[str, Any] | None) -> str | None:
    turn = (result or {}).get("turn") if isinstance(result, Mapping) else None
    if isinstance(turn, Mapping):
        value = turn.get("id") or turn.get("turnId")
        return str(value) if value else None
    return None


def _turn_id_from_receipt(receipt: Mapping[str, Any]) -> str | None:
    if receipt.get("turn_id"):
        return str(receipt.get("turn_id"))
    result = receipt.get("turn_start_result")
    return _turn_id_from_result(result if isinstance(result, Mapping) else None)


def _turn_id_from_turn(turn: Mapping[str, Any]) -> str | None:
    value = turn.get("id") or turn.get("turnId")
    return str(value) if value else None


def _turn_status_text(turn: Mapping[str, Any]) -> str | None:
    status = turn.get("status")
    if isinstance(status, Mapping):
        value = status.get("type") or status.get("status") or status.get("state")
        return str(value) if value else None
    return str(status) if status is not None else None


def _normalize_turn_status(value: Any) -> str:
    return re.sub(r"[^a-z]+", "", str(value or "").strip().lower())


def _turn_status_is_terminal(value: Any) -> bool:
    return _normalize_turn_status(value) in TERMINAL_TURN_STATUSES


def _match_turn_by_id(turns: Any, turn_id: str) -> dict[str, Any] | None:
    if not isinstance(turns, list):
        return None
    for turn in turns:
        if isinstance(turn, Mapping) and _turn_id_from_turn(turn) == turn_id:
            return dict(turn)
    return None


def _scanned_turn_ids(turns: Any) -> list[str]:
    if not isinstance(turns, list):
        return []
    output: list[str] = []
    for turn in turns:
        if isinstance(turn, Mapping):
            turn_id = _turn_id_from_turn(turn)
            if turn_id:
                output.append(turn_id)
    return output


def _turn_start_receipt_rows(root: Path, thread_id: str) -> list[dict[str, Any]]:
    base = root / RUNS_RELATIVE_ROOT / thread_id
    rows: list[dict[str, Any]] = []
    if not (base / "runs").is_dir():
        return rows
    for item in sorted((base / "runs").glob("*/run_receipt.json"), key=lambda p: (p.stat().st_mtime, p.as_posix()), reverse=True)[:20]:
        try:
            data = json.loads(item.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        turn_id = _turn_id_from_receipt(data)
        submit_state = data.get("submit_state") or ("submitted" if turn_id and not data.get("turn_start_error") else None)
        rows.append(
            {
                "receipt_path": _repo_rel(root, item),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "submit_state": submit_state,
                "submitted": data.get("submitted") if data.get("submitted") is not None else bool(turn_id and not data.get("turn_start_error")),
                "turn_id": turn_id,
                "turn_completed_notification_seen": data.get("turn_completed_notification_seen"),
                "item_completed_notification_seen": data.get("item_completed_notification_seen"),
                "thread_idle_notification_seen": data.get("thread_idle_notification_seen"),
                "completion_inferred_from_notifications": data.get("completion_inferred_from_notifications"),
                "completion_poll_recommended": data.get("completion_poll_recommended"),
                "timed_out": data.get("timed_out"),
                "turn_start_error": data.get("turn_start_error"),
            }
        )
    return rows


def _completion_observation(rpc: Mapping[str, Any]) -> dict[str, Any]:
    notifications = [item for item in rpc.get("notifications") or [] if isinstance(item, Mapping)]
    methods = [str(item.get("method") or "") for item in notifications]
    thread_idle_seen = any(
        item.get("method") == "thread/status/changed"
        and isinstance(item.get("params"), Mapping)
        and isinstance((item.get("params") or {}).get("status"), Mapping)
        and ((item.get("params") or {}).get("status") or {}).get("type") == "idle"
        for item in notifications
    )
    return {
        "turn_completed_notification_seen": "turn/completed" in methods,
        "item_completed_notification_seen": "item/completed" in methods,
        "thread_idle_notification_seen": thread_idle_seen,
        "completion_inferred_from_notifications": bool("turn/completed" in methods or ("item/completed" in methods and thread_idle_seen)),
    }


def _prompt_sha256(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _persistent_carrier_key(thread_id: str, args: Mapping[str, Any]) -> str:
    return _safe_idempotency_key(args.get("carrier_id") or f"persistent-app-server-{thread_id}")


def _carrier_folder_name_is_safe(value: str) -> bool:
    return bool(value and "/" not in value and "\\" not in value and ".." not in value and THREAD_ID_RE.match(value))


def _resolve_persistent_carrier_identity(root: Path, thread_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    input_carrier_id = str(args.get("carrier_id") or f"persistent-app-server-{thread_id}").strip()
    thread_root = root / PERSISTENT_CARRIERS_RELATIVE_ROOT / thread_id
    if _carrier_folder_name_is_safe(input_carrier_id) and (thread_root / input_carrier_id).is_dir():
        canonical = input_carrier_id
        method = "existing_folder_exact"
    elif _carrier_folder_name_is_safe(input_carrier_id) and CANONICAL_CARRIER_ID_RE.match(input_carrier_id):
        canonical = input_carrier_id
        method = "input_already_canonical"
    else:
        canonical = _safe_idempotency_key(input_carrier_id)
        method = "canonicalized_from_base"
    return {
        "input_carrier_id": input_carrier_id,
        "canonical_carrier_id": canonical,
        "carrier_id": canonical,
        "carrier_id_resolution": {
            "input_carrier_id": input_carrier_id,
            "canonical_carrier_id": canonical,
            "method": method,
            "thread_root": _repo_rel(root, thread_root),
            "matched_existing_folder": method == "existing_folder_exact",
        },
    }


def _persistent_carrier_paths(root: Path, thread_id: str, carrier_key: str) -> dict[str, Path]:
    carrier_root = root / PERSISTENT_CARRIERS_RELATIVE_ROOT / thread_id / carrier_key
    return {
        "carrier_root": carrier_root,
        "lock": carrier_root / "carrier.lock.json",
        "heartbeat": carrier_root / "heartbeat.latest.json",
        "run_receipt": carrier_root / "run_receipt.json",
        "stdout_jsonl": carrier_root / "stdout.jsonl",
        "stderr_log": carrier_root / "stderr.log",
        "final_status": carrier_root / "final_status.json",
        "stop_request": carrier_root / "stop_request.json",
        "stop_receipt": carrier_root / "stop_receipt.json",
    }


def _persistent_carrier_path_refs(root: Path, paths: Mapping[str, Path]) -> dict[str, str]:
    return {key: _repo_rel(root, path) for key, path in paths.items()}


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _timestamp_age_seconds(value: Any) -> float | None:
    parsed = _parse_timestamp(value)
    if not parsed:
        return None
    return max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())


def _persistent_carrier_status_data(root: Path, thread_id: str, carrier_key: str, args: Mapping[str, Any] | None = None) -> dict[str, Any]:
    args = args or {}
    paths = _persistent_carrier_paths(root, thread_id, carrier_key)
    lock = _read_json(paths["lock"])
    heartbeat = _read_json(paths["heartbeat"])
    final_status = _read_json(paths["final_status"])
    run_receipt = _read_json(paths["run_receipt"])
    stop_request = _read_json(paths["stop_request"])
    stop_receipt = _read_json(paths["stop_receipt"])
    stale_after = max(30, min(int(args.get("stale_after_seconds") or (heartbeat or {}).get("stale_after_seconds") or (lock or {}).get("stale_after_seconds") or 180), 3600))
    heartbeat_age = _timestamp_age_seconds((heartbeat or {}).get("updated_at"))
    final_state = str((final_status or {}).get("state") or "").strip()
    heartbeat_state = str((heartbeat or {}).get("state") or "").strip()
    if final_state and _normalize_turn_status(final_state) in PERSISTENT_CARRIER_TERMINAL_STATES:
        classification = "terminal"
    elif heartbeat_state and _normalize_turn_status(heartbeat_state) in PERSISTENT_CARRIER_TERMINAL_STATES:
        classification = "terminal"
    elif not lock:
        classification = "missing"
    elif not heartbeat:
        classification = "stale_no_heartbeat"
    elif heartbeat_age is not None and heartbeat_age > stale_after:
        classification = "stale_heartbeat"
    else:
        classification = "live"
    return {
        "thread_id": thread_id,
        "carrier_id": carrier_key,
        "classification": classification,
        "stale_after_seconds": stale_after,
        "heartbeat_age_seconds": heartbeat_age,
        "paths": _persistent_carrier_path_refs(root, paths),
        "lock": _sanitize(lock, limit=4_000),
        "heartbeat": _sanitize(heartbeat, limit=4_000),
        "final_status": _sanitize(final_status, limit=4_000),
        "run_receipt": _sanitize(run_receipt, limit=4_000),
        "stop_request": _sanitize(stop_request, limit=2_000),
        "stop_receipt": _sanitize(stop_receipt, limit=2_000),
    }


def _write_persistent_heartbeat(
    paths: Mapping[str, Path],
    *,
    thread_id: str,
    carrier_key: str,
    idempotency_key_safe: str,
    state: str,
    stale_after_seconds: int,
    turn_id: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> None:
    payload = {
        "schema_id": "ion.codex_app_server_persistent_carrier_heartbeat.v0_1_candidate",
        "updated_at": _now(),
        "thread_id": thread_id,
        "carrier_id": carrier_key,
        "idempotency_key_safe": idempotency_key_safe,
        "state": state,
        "stale_after_seconds": stale_after_seconds,
        "turn_id": turn_id,
        **AUTHORITY_FALSE,
    }
    if extra:
        payload.update(dict(extra))
    _write_json(paths["heartbeat"], payload)


def _write_persistent_final_status(
    paths: Mapping[str, Path],
    *,
    thread_id: str,
    carrier_key: str,
    idempotency_key_safe: str,
    state: str,
    turn_id: str | None = None,
    finding: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_id": "ion.codex_app_server_persistent_carrier_final_status.v0_1_candidate",
        "updated_at": _now(),
        "thread_id": thread_id,
        "carrier_id": carrier_key,
        "idempotency_key_safe": idempotency_key_safe,
        "state": state,
        "turn_id": turn_id,
        "finding": finding,
        **AUTHORITY_FALSE,
    }
    if extra:
        payload.update(dict(extra))
    _write_json(paths["final_status"], payload)
    return payload


def _turn_start(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "turn_start"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    prompt = _redact(args.get("prompt") or "", limit=8_000)
    if not prompt:
        return _blocked(route_id, "prompt_required")
    run_paths = _run_paths(root, thread_id, str(args.get("idempotency_key") or ""))
    if run_paths["receipt"].is_file():
        receipt = json.loads(run_paths["receipt"].read_text(encoding="utf-8"))
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, run_paths["receipt"]), "receipt": receipt})
        return payload
    turn_params: dict[str, Any] = {"threadId": thread_id, "input": _turn_input(prompt)}
    sandbox, writable_root_resolution = _sandbox_policy_details(args, root=root)
    if sandbox:
        turn_params["sandboxPolicy"] = sandbox
    if args.get("cwd"):
        turn_params["cwd"] = str(args.get("cwd"))
    requests = [
        _jsonrpc_initialize(),
        {"id": "resume", "method": "thread/resume", "params": {"threadId": thread_id, "excludeTurns": True}},
        {"id": "turn_start", "method": "turn/start", "params": turn_params},
    ]
    receipt = {
        "schema_id": "ion.codex_app_server_turn_start_receipt.v1_candidate",
        "created_at": _now(),
        "updated_at": _now(),
        "thread_id": thread_id,
        "session_id": thread_id,
        **AUTHORITY_FALSE,
        "source_of_truth_classification": "durable_ion_receipt",
        "non_claims": [*NON_CLAIMS, "This route used Codex app-server turn/start, not terminal key injection."],
        "prompt_redacted": prompt,
        "submit_state": "started",
        "submitted": False,
        "accepted_by_app_server": False,
        "durably_visible": False,
        "completed": False,
        "durable_submit_state": "started",
        "turn_id": None,
        "completion_wait_requested": _truthy(args.get("wait_for_completion")),
        "visibility_wait_requested": _truthy(args.get("wait_until_visible")),
        "completion_poll_recommended": True,
        "turn_start_result": None,
        "turn_start_error": None,
        "writable_root_resolution": writable_root_resolution,
        "post_submit_visibility_probe": None,
        "turn_completed_notification_seen": False,
        "item_completed_notification_seen": False,
        "thread_idle_notification_seen": False,
        "completion_inferred_from_notifications": False,
        "timed_out": False,
        "notifications": [],
        "stderr_lines": [],
    }
    _write_json(run_paths["receipt"], receipt)
    status = {
        "schema_id": "ion.codex_app_server_turn_status.v1_candidate",
        "updated_at": _now(),
        "thread_id": thread_id,
        "latest_run": _repo_rel(root, run_paths["receipt"]),
        "submit_state": "started",
        **AUTHORITY_FALSE,
    }
    _write_json(run_paths["latest_status"], status)

    wait_for_completion = _truthy(args.get("wait_for_completion"))
    wait_until_visible = _truthy(args.get("wait_until_visible"))
    if wait_for_completion:
        timeout_seconds = max(10, min(int(args.get("timeout_seconds") or 180), 600))
        wait_for_methods = {"item/completed"}
    else:
        timeout_seconds = max(5, min(int(args.get("submit_timeout_seconds") or args.get("timeout_seconds") or 30), 60))
        wait_for_methods = None
    try:
        rpc = _run_app_server_jsonrpc(
            requests,
            timeout_seconds=timeout_seconds,
            wait_for_methods=wait_for_methods,
        )
    except Exception as exc:
        receipt.update(
            {
                "updated_at": _now(),
                "submit_state": "blocked",
                "turn_start_error": {"finding": "codex_app_server_exception", "error": _redact(exc, limit=1_000)},
            }
        )
        _write_json(run_paths["receipt"], receipt)
        status.update({"updated_at": _now(), "submit_state": "blocked"})
        _write_json(run_paths["latest_status"], status)
        payload = _base(route_id, ok=False, finding="codex_app_server_exception")
        payload.update({"thread_id": thread_id, "session_id": thread_id, "executed": False, "mutates_active_state": True, "receipt_path": _repo_rel(root, run_paths["receipt"]), "latest_status_path": _repo_rel(root, run_paths["latest_status"])})
        return payload
    result, error = _result_for_id(rpc, "turn_start")
    turn_id = _turn_id_from_result(result)
    observed = _completion_observation(rpc)
    accepted_by_app_server = not bool(error) and bool(turn_id)
    post_submit_visibility_probe = None
    durably_visible = False
    visible_turn_status = None
    if accepted_by_app_server and (wait_for_completion or wait_until_visible):
        post_submit_visibility_probe = _thread_turn_read_by_id(
            {
                "thread_id": thread_id,
                "turn_id": turn_id,
                "items_view": "summary",
                "max_bytes": 12_000,
                "timeout_seconds": 15,
            }
        )
        durably_visible = bool(post_submit_visibility_probe.get("matched"))
        visible_turn_status = post_submit_visibility_probe.get("matched_turn_status")
    completed = bool(observed["completion_inferred_from_notifications"]) or (_normalize_turn_status(visible_turn_status) == "completed")
    if not accepted_by_app_server:
        durable_submit_state = "blocked"
    elif completed and durably_visible:
        durable_submit_state = "completed_and_durably_visible"
    elif durably_visible:
        durable_submit_state = "durably_visible_incomplete"
    elif wait_for_completion or wait_until_visible:
        durable_submit_state = "accepted_but_not_durably_visible"
    else:
        durable_submit_state = "accepted_unverified"
    receipt.update({
        "updated_at": _now(),
        "submit_state": "submitted" if accepted_by_app_server else "blocked",
        "submitted": accepted_by_app_server,
        "accepted_by_app_server": accepted_by_app_server,
        "durably_visible": durably_visible,
        "completed": completed,
        "durable_submit_state": durable_submit_state,
        "turn_id": turn_id,
        "turn_start_result": _sanitize(result, limit=3_000),
        "turn_start_error": _sanitize(error, limit=2_000),
        "post_submit_visibility_probe": _sanitize(post_submit_visibility_probe, limit=6_000),
        **observed,
        "timed_out": bool(rpc.get("timed_out")),
        "notifications": _sanitize(rpc.get("notifications"), limit=6_000),
        "stderr_lines": _sanitize(rpc.get("stderr_lines"), limit=2_000),
    })
    _write_json(run_paths["receipt"], receipt)
    status.update(
        {
            "updated_at": _now(),
            "submit_state": receipt["submit_state"],
            "submitted": accepted_by_app_server,
            "accepted_by_app_server": accepted_by_app_server,
            "durably_visible": durably_visible,
            "completed": completed,
            "durable_submit_state": durable_submit_state,
            "turn_id": turn_id,
        }
    )
    _write_json(run_paths["latest_status"], status)
    finding = (error or {}).get("finding")
    ok = accepted_by_app_server and not bool(error)
    if wait_for_completion:
        ok = ok and completed and durably_visible
        if not ok and not finding:
            finding = "codex_app_server_turn_start_completion_not_durably_visible"
    elif wait_until_visible:
        ok = ok and durably_visible
        if not ok and not finding:
            finding = "codex_app_server_turn_start_not_durably_visible"
    payload = _base(route_id, ok=ok, finding=finding)
    payload.update(
        {
            "thread_id": thread_id,
            "session_id": thread_id,
            "executed": True,
            "mutates_active_state": True,
            "submitted": accepted_by_app_server,
            "accepted_by_app_server": accepted_by_app_server,
            "durably_visible": durably_visible,
            "completed": completed,
            "durable_submit_state": durable_submit_state,
            "turn_id": turn_id,
            "submit_state": receipt["submit_state"],
            "completion_wait_requested": wait_for_completion,
            "visibility_wait_requested": wait_until_visible,
            "completion_poll_recommended": True,
            "writable_root_resolution": writable_root_resolution,
            "post_submit_visibility_probe": _sanitize(post_submit_visibility_probe, limit=6_000),
            **observed,
            "timed_out": bool(rpc.get("timed_out")),
            "receipt_path": _repo_rel(root, run_paths["receipt"]),
            "latest_status_path": _repo_rel(root, run_paths["latest_status"]),
        }
    )
    if payload["ok"] is False and "finding" not in payload:
        payload["finding"] = "codex_app_server_turn_start_incomplete_or_blocked"
    return payload


def _turn_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    receipts = _turn_start_receipt_rows(root, thread_id)
    latest_run = receipts[0] if receipts else None
    requested_turn_id = _safe_turn_id(args.get("turn_id")) if args.get("turn_id") else None
    target_turn_id = requested_turn_id or (str(latest_run.get("turn_id")) if latest_run and latest_run.get("turn_id") else None)
    max_bytes = max(2_000, min(int(args.get("max_bytes") or 12_000), 80_000))
    payload = _base("turn_status")
    payload.update(
        {
            "thread_id": thread_id,
            "run_count": len(receipts),
            "latest_run": latest_run,
            "runs": receipts,
            "target_turn_id": target_turn_id,
            "target_source": "args.turn_id" if requested_turn_id else "latest_run_receipt" if target_turn_id else None,
            "exact_target_match_required": bool(target_turn_id),
        }
    )
    turns_probe = _thread_turns_list(
        {
            "thread_id": thread_id,
            "limit": 50,
            "items_view": str(args.get("items_view") or "summary"),
            "timeout_seconds": int(args.get("timeout_seconds") or 15),
            "max_bytes": max_bytes,
        }
    )
    payload["thread_turns_probe"] = _sanitize(turns_probe, limit=12_000)
    known_turn_ids = {str(item.get("turn_id")) for item in receipts if item.get("turn_id")}
    recent_turns = turns_probe.get("turns") if isinstance(turns_probe, Mapping) else None
    target_turn = _match_turn_by_id(recent_turns, target_turn_id) if target_turn_id else None
    payload.update(
        {
            "target_turn_matched": bool(target_turn),
            "target_turn_match_state": "matched" if target_turn else "not_found" if target_turn_id else "no_target_turn_id",
            "target_matched_turn": _sanitize(target_turn, limit=max_bytes) if target_turn else None,
            "target_turn_status": _turn_status_text(target_turn) if target_turn else None,
        }
    )
    if isinstance(recent_turns, list) and known_turn_ids:
        payload["matched_turns"] = [
            _sanitize(turn, limit=4_000)
            for turn in recent_turns
            if isinstance(turn, Mapping) and (_turn_id_from_turn(turn) or "") in known_turn_ids
        ]
    return payload


def _turn_poll(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    latest = _truthy(args.get("latest"))
    receipt_path = None
    if args.get("turn_id"):
        turn_id = _safe_turn_id(args.get("turn_id"))
        target_source = "args.turn_id"
    elif latest:
        latest_run = (_turn_start_receipt_rows(root, thread_id) or [None])[0]
        turn_id = str(latest_run.get("turn_id")) if latest_run and latest_run.get("turn_id") else ""
        receipt_path = latest_run.get("receipt_path") if latest_run else None
        if not turn_id:
            return _blocked("turn_poll", "latest_turn_id_not_found", refusal_class="NOT_FOUND", data={"thread_id": thread_id, "receipt_path": receipt_path})
        target_source = "latest_run_receipt"
    else:
        return _blocked("turn_poll", "turn_id_or_latest_required")

    timeout_seconds = max(1, min(int(args.get("timeout_seconds") or 30), 300))
    poll_interval = max(0.25, min(float(args.get("poll_interval_seconds") or args.get("poll_interval") or 1.0), 10.0))
    deadline = time.monotonic() + timeout_seconds
    observations: list[dict[str, Any]] = []
    last_read: dict[str, Any] | None = None
    while True:
        read = _thread_turn_read_by_id(
            {
                "thread_id": thread_id,
                "turn_id": turn_id,
                "items_view": str(args.get("items_view") or "summary"),
                "max_bytes": int(args.get("max_bytes") or 20_000),
                "timeout_seconds": min(15, timeout_seconds),
            }
        )
        last_read = read
        observations.append(
            {
                "observed_at": _now(),
                "matched": read.get("matched"),
                "finding": read.get("finding"),
                "status": read.get("matched_turn_status"),
            }
        )
        status_text = read.get("matched_turn_status")
        if read.get("matched") and _turn_status_is_terminal(status_text):
            normalized = _normalize_turn_status(status_text)
            ok = normalized == "completed"
            payload = _base("turn_poll", ok=ok, finding=None if ok else "turn_terminal_non_completed")
            payload.update(
                {
                    "thread_id": thread_id,
                    "turn_id": turn_id,
                    "target_source": target_source,
                    "receipt_path": receipt_path,
                    "poll_state": "completed" if ok else "error",
                    "turn_status": status_text,
                    "matched_turn": read.get("matched_turn"),
                    "observations": observations[-20:],
                    "exact_match_required": True,
                }
            )
            return payload
        if time.monotonic() >= deadline:
            payload = _base("turn_poll", ok=False, finding="turn_poll_timeout" if read.get("matched") else "turn_not_found")
            payload.update(
                {
                    "thread_id": thread_id,
                    "turn_id": turn_id,
                    "target_source": target_source,
                    "receipt_path": receipt_path,
                    "poll_state": "timeout" if read.get("matched") else "not_found",
                    "turn_status": status_text,
                    "matched_turn": read.get("matched_turn"),
                    "last_read": _sanitize(last_read, limit=8_000),
                    "observations": observations[-20:],
                    "exact_match_required": True,
                }
            )
            if not read.get("matched"):
                payload["refusal_class"] = "NOT_FOUND"
            return payload
        time.sleep(poll_interval)


def _persistent_carrier_preview(root: Path, args: Mapping[str, Any], *, route_id: str = "persistent_carrier_preview") -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    prompt = _redact(args.get("prompt") or "", limit=8_000)
    if not prompt:
        return _blocked(route_id, "prompt_required")
    carrier_identity = _resolve_persistent_carrier_identity(root, thread_id, args)
    carrier_key = str(carrier_identity["canonical_carrier_id"])
    sandbox, writable_root_resolution = _sandbox_policy_details(args, root=root)
    cwd = str(args.get("cwd") or root.as_posix())
    paths = _persistent_carrier_paths(root, thread_id, carrier_key)
    turn_params: dict[str, Any] = {"threadId": thread_id, "input": _turn_input(prompt), "cwd": cwd}
    if sandbox:
        turn_params["sandboxPolicy"] = sandbox
    payload = _base(route_id)
    payload.update(
        {
            "thread_id": thread_id,
            **carrier_identity,
            "cwd": cwd,
            "persistent_carrier_not_started": True,
            "would_start_process": False,
            "mutates_active_state": False,
            "chosen_lane": "persistent_app_server_supervisor_first",
            "fallback_lanes": [
                "full_terminal_codex_exec_from_generated_mount_after_usage_reset",
                "queue_runner_exact_request_path_after_queue_hygiene"
            ],
            "sandbox_policy": sandbox,
            "writable_root_resolution": writable_root_resolution,
            "lifecycle_paths": _persistent_carrier_path_refs(root, paths),
            "lifecycle_contract": {
                "lock_required": True,
                "lock_scope": "thread_id + carrier_id + idempotency_key",
                "heartbeat_interval_seconds": max(5, min(int(args.get("heartbeat_interval_seconds") or 15), 120)),
                "stale_after_seconds": max(30, min(int(args.get("stale_after_seconds") or 180), 3600)),
                "cleanup_requires": [
                    "terminal turn status",
                    "timeout with process termination receipt",
                    "operator stop receipt"
                ]
            },
            "jsonrpc_contract": {
                "command": _app_server_command(),
                "startup": [_jsonrpc_initialize(), {"id": "resume", "method": "thread/resume", "params": {"threadId": thread_id, "excludeTurns": True}}],
                "turn_start": {"id": "turn_start", "method": "turn/start", "params": turn_params},
                "supervision_loop": [
                    "keep stdio process alive after turn/start",
                    "record thread/status and item/turn notifications",
                    "poll thread/turns/list for the exact turn_id once known",
                    "only mark durable when exact turn is visible or completed",
                    "write heartbeat and final_status receipts"
                ]
            },
            "duplicate_and_storm_controls": [
                "idempotency key maps to a single carrier_id",
                "existing live lock blocks duplicate turn_start",
                "stale lock requires explicit stale classification before retry",
                "prompt hash must match on idempotent replay",
                "no automatic relaunch loop without a new receipt"
            ],
            "durability_gates": [
                "accepted_by_app_server",
                "exact_turn_id_recorded",
                "durably_visible",
                "completed_or_terminal_error",
                "return_file_observed_when packet expects file output"
            ],
            "stop_conditions": [
                "turn completed",
                "turn terminal non-completed",
                "timeout_seconds elapsed",
                "usage_limit or quota error",
                "operator stop receipt",
                "heartbeat write failure"
            ],
            "non_claims": [
                "Preview does not start codex app-server.",
                "Preview does not submit a turn.",
                "Preview does not claim worker launch or durable execution."
            ]
        }
    )
    return payload


def _persistent_carrier_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    carrier_identity = _resolve_persistent_carrier_identity(root, thread_id, args)
    carrier_key = str(carrier_identity["canonical_carrier_id"])
    payload = _base("persistent_carrier_status")
    payload.update(carrier_identity)
    payload.update(_persistent_carrier_status_data(root, thread_id, carrier_key, args))
    payload["persistent_carrier_not_started"] = True
    return payload


def _usage_limit_signal(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_usage_limit_signal(item) for item in value.values())
    if isinstance(value, list):
        return any(_usage_limit_signal(item) for item in value)
    text = str(value or "").lower()
    return any(marker in text for marker in ("usagelimitexceeded", "usage limit", "usage-limit", "rate limit", "quota"))


def _append_persistent_phase(
    paths: Mapping[str, Path],
    *,
    thread_id: str,
    carrier_key: str,
    idempotency_key_safe: str,
    state: str,
    stale_after_seconds: int,
    turn_id: str | None,
    phases: list[dict[str, Any]],
    extra: Mapping[str, Any] | None = None,
) -> None:
    phase = {"phase": state, "observed_at": _now(), "turn_id": turn_id}
    if extra:
        phase.update(dict(extra))
    phases.append(phase)
    _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "fake_app_server_runner": True, "phase": state, "turn_id": turn_id, **(dict(extra or {}))})
    _write_persistent_heartbeat(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state=state,
        stale_after_seconds=stale_after_seconds,
        turn_id=turn_id,
        extra={"fake_app_server_runner": True, **dict(extra or {})},
    )


def _persistent_carrier_start_fake_real_runner(
    root: Path,
    args: Mapping[str, Any],
    *,
    thread_id: str,
    prompt_raw: str,
    prompt: str,
    carrier_identity: Mapping[str, Any],
    carrier_key: str,
    idempotency_key_safe: str,
    prompt_hash: str,
    sandbox: Mapping[str, Any] | None,
    writable_root_resolution: list[dict[str, str]],
    paths: Mapping[str, Path],
    stale_after_seconds: int,
    heartbeat_interval_seconds: int,
) -> dict[str, Any]:
    route_id = "persistent_carrier_start"
    if not _truthy(args.get("fake_app_server_runner")):
        return _blocked(
            route_id,
            "persistent_carrier_real_runner_process_not_implemented",
            refusal_class="REAL_PROCESS_RUNNER_NOT_IMPLEMENTED",
            data={
                "allow_real_app_server": True,
                "fake_app_server_runner": False,
                "fake_app_server_runner_supported_for_tests": True,
                "real_app_server_process_started": False,
                "turn_submitted_to_real_codex": False,
            },
        )

    turn_id = _safe_turn_id(args.get("fake_turn_id") or args.get("mock_turn_id") or f"fake-turn-{idempotency_key_safe[:16]}")
    fake_stdout = str(args.get("fake_stdout_contains") or "")
    fake_usage_limit = _truthy(args.get("fake_usage_limit")) or _usage_limit_signal(fake_stdout)
    fake_timeout = _truthy(args.get("fake_timeout"))
    fake_turn_visible = _truthy(args.get("fake_turn_visible", True))
    fake_leave_running = _truthy(args.get("fake_leave_running"))
    terminal_status = str(args.get("fake_terminal_status") or "completed").strip() or "completed"
    normalized_terminal = _normalize_turn_status(terminal_status)

    lock = {
        "schema_id": "ion.codex_app_server_persistent_carrier_lock.v0_1_candidate",
        "created_at": _now(),
        "updated_at": _now(),
        "thread_id": thread_id,
        "carrier_id": carrier_key,
        "idempotency_key_safe": idempotency_key_safe,
        "prompt_sha256": prompt_hash,
        "state": "starting",
        "allow_real_app_server": True,
        "fake_app_server_runner": True,
        "real_app_server_process_started": False,
        "heartbeat_interval_seconds": heartbeat_interval_seconds,
        "stale_after_seconds": stale_after_seconds,
        **AUTHORITY_FALSE,
    }
    _write_json(paths["lock"], lock)

    phases: list[dict[str, Any]] = []
    _append_persistent_phase(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="starting",
        stale_after_seconds=stale_after_seconds,
        turn_id=None,
        phases=phases,
        extra={"real_app_server_process_started": False},
    )
    _append_persistent_phase(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="submitted",
        stale_after_seconds=stale_after_seconds,
        turn_id=turn_id,
        phases=phases,
        extra={"accepted_by_app_server": not fake_usage_limit and not fake_timeout},
    )

    if fake_timeout:
        state = "timeout"
        finding = "persistent_carrier_timeout"
        completed = False
        durably_visible = False
        accepted_by_app_server = True
    elif fake_usage_limit:
        state = "usage_limited"
        finding = "persistent_carrier_usage_limit"
        completed = False
        durably_visible = False
        accepted_by_app_server = False
    elif fake_leave_running:
        state = "running"
        finding = None
        completed = False
        durably_visible = fake_turn_visible
        accepted_by_app_server = True
    elif not fake_turn_visible:
        state = normalized_terminal
        finding = "persistent_carrier_exact_turn_not_visible"
        completed = False
        durably_visible = False
        accepted_by_app_server = True
    else:
        state = normalized_terminal
        finding = None if normalized_terminal == "completed" else "persistent_carrier_terminal_non_completed"
        completed = normalized_terminal == "completed"
        durably_visible = True
        accepted_by_app_server = True

    if durably_visible:
        _append_persistent_phase(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state="visible",
            stale_after_seconds=stale_after_seconds,
            turn_id=turn_id,
            phases=phases,
            extra={"durably_visible": True},
        )
    if state != "running":
        _append_persistent_phase(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state=state,
            stale_after_seconds=stale_after_seconds,
            turn_id=turn_id,
            phases=phases,
            extra={"completed": completed, "durably_visible": durably_visible, "finding": finding},
        )

    final_status = None
    if state != "running":
        final_status = _write_persistent_final_status(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state=state,
            turn_id=turn_id,
            finding=finding,
            extra={
                "allow_real_app_server": True,
                "fake_app_server_runner": True,
                "real_app_server_process_started": False,
                "accepted_by_app_server": accepted_by_app_server,
                "durably_visible": durably_visible,
                "completed": completed,
                "lifecycle_phases": phases,
            },
        )
    lock["state"] = state
    lock["updated_at"] = _now()
    _write_json(paths["lock"], lock)

    receipt = {
        "schema_id": "ion.codex_app_server_persistent_carrier_real_runner_receipt.v0_1_candidate",
        "created_at": _now(),
        "updated_at": _now(),
        "thread_id": thread_id,
        "session_id": thread_id,
        **carrier_identity,
        "idempotency_key_safe": idempotency_key_safe,
        "prompt_sha256": prompt_hash,
        "prompt_redacted": prompt,
        "allow_real_app_server": True,
        "fake_app_server_runner": True,
        "mock_app_server": False,
        "dry_run": False,
        "real_app_server_process_started": False,
        "turn_submitted_to_real_codex": False,
        "submitted": True,
        "accepted_by_app_server": accepted_by_app_server,
        "durably_visible": durably_visible,
        "completed": completed,
        "usage_limited": fake_usage_limit,
        "timed_out": fake_timeout,
        "turn_id": turn_id,
        "state": state,
        "finding": finding,
        "lifecycle_phases": phases,
        "sandbox_policy": sandbox,
        "writable_root_resolution": writable_root_resolution,
        "lifecycle_paths": _persistent_carrier_path_refs(root, paths),
        "final_status": _sanitize(final_status, limit=4_000),
        **AUTHORITY_FALSE,
        "non_claims": [
            *NON_CLAIMS,
            "Fake app-server runner did not start a real Codex app-server process.",
            "Fake app-server runner did not submit a real model turn.",
            "Candidate lifecycle artifacts are not accepted state or materialization.",
        ],
    }
    _write_json(paths["run_receipt"], receipt)
    ok = state == "running" or (completed and durably_visible and not fake_usage_limit and not fake_timeout)
    payload = _base(route_id, ok=ok, finding=finding)
    payload.update(
        {
            "thread_id": thread_id,
            "session_id": thread_id,
            **carrier_identity,
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "mock_app_server": False,
            "dry_run": False,
            "real_app_server_process_started": False,
            "turn_submitted_to_real_codex": False,
            "mutates_active_state": True,
            "submitted": True,
            "accepted_by_app_server": accepted_by_app_server,
            "durably_visible": durably_visible,
            "completed": completed,
            "usage_limited": fake_usage_limit,
            "timed_out": fake_timeout,
            "turn_id": turn_id,
            "state": state,
            "lifecycle_phases": phases,
            "receipt_path": _repo_rel(root, paths["run_receipt"]),
            "lock_path": _repo_rel(root, paths["lock"]),
            "heartbeat_path": _repo_rel(root, paths["heartbeat"]),
            "final_status_path": _repo_rel(root, paths["final_status"]) if final_status else None,
            "writable_root_resolution": writable_root_resolution,
            "status": _persistent_carrier_status_data(root, thread_id, carrier_key, args),
        }
    )
    return payload


def _append_persistent_real_phase(
    paths: Mapping[str, Path],
    *,
    thread_id: str,
    carrier_key: str,
    idempotency_key_safe: str,
    state: str,
    stale_after_seconds: int,
    turn_id: str | None,
    phases: list[dict[str, Any]],
    extra: Mapping[str, Any] | None = None,
) -> None:
    phase = {"phase": state, "observed_at": _now(), "turn_id": turn_id}
    if extra:
        phase.update(dict(extra))
    phases.append(phase)
    _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "phase": state, "turn_id": turn_id, **dict(extra or {})})
    _write_persistent_heartbeat(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state=state,
        stale_after_seconds=stale_after_seconds,
        turn_id=turn_id,
        extra={"allow_real_app_server": True, "fake_app_server_runner": False, **dict(extra or {})},
    )


def _write_persistent_rpc_logs(paths: Mapping[str, Path], rpc: Mapping[str, Any]) -> None:
    for response in rpc.get("responses") or []:
        if isinstance(response, Mapping):
            _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "jsonrpc_response": _sanitize(response, limit=4_000)})
    for notification in rpc.get("notifications") or []:
        if isinstance(notification, Mapping):
            _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "jsonrpc_notification": _sanitize(notification, limit=4_000)})
    stderr_lines = [str(line) for line in (rpc.get("stderr_lines") or [])]
    paths["stderr_log"].parent.mkdir(parents=True, exist_ok=True)
    paths["stderr_log"].write_text("\n".join(_redact(line, limit=1_000) for line in stderr_lines) + ("\n" if stderr_lines else ""), encoding="utf-8")


def _persistent_carrier_start_real_runner(
    root: Path,
    args: Mapping[str, Any],
    *,
    thread_id: str,
    prompt_raw: str,
    prompt: str,
    carrier_identity: Mapping[str, Any],
    carrier_key: str,
    idempotency_key_safe: str,
    prompt_hash: str,
    sandbox: Mapping[str, Any] | None,
    writable_root_resolution: list[dict[str, str]],
    paths: Mapping[str, Path],
    stale_after_seconds: int,
    heartbeat_interval_seconds: int,
) -> dict[str, Any]:
    route_id = "persistent_carrier_start"
    cwd = str(args.get("cwd") or root.as_posix())
    turn_params: dict[str, Any] = {"threadId": thread_id, "input": _turn_input(prompt), "cwd": cwd}
    if sandbox:
        turn_params["sandboxPolicy"] = sandbox
    requests = [
        _jsonrpc_initialize(),
        {"id": "resume", "method": "thread/resume", "params": {"threadId": thread_id, "excludeTurns": True}},
        {"id": "turn_start", "method": "turn/start", "params": turn_params},
        {"id": "turns", "method": "thread/turns/list", "params": {"threadId": thread_id, "limit": 20, "itemsView": "summary"}},
    ]
    wait_for_completion = _truthy(args.get("wait_for_completion", True))
    timeout_seconds = max(5, min(int(args.get("timeout_seconds") or 90), 600))
    wait_for_methods = {"item/completed"} if wait_for_completion else None
    command = list(args.get("_command_argv") or _app_server_command())
    lock = {
        "schema_id": "ion.codex_app_server_persistent_carrier_lock.v0_1_candidate",
        "created_at": _now(),
        "updated_at": _now(),
        "thread_id": thread_id,
        "carrier_id": carrier_key,
        "idempotency_key_safe": idempotency_key_safe,
        "prompt_sha256": prompt_hash,
        "state": "starting",
        "allow_real_app_server": True,
        "fake_app_server_runner": False,
        "real_app_server_process_started": False,
        "command_argv": command,
        "heartbeat_interval_seconds": heartbeat_interval_seconds,
        "stale_after_seconds": stale_after_seconds,
        **AUTHORITY_FALSE,
    }
    _write_json(paths["lock"], lock)
    phases: list[dict[str, Any]] = []
    _append_persistent_real_phase(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="starting",
        stale_after_seconds=stale_after_seconds,
        turn_id=None,
        phases=phases,
        extra={"real_app_server_process_started": False, "command_argv": command},
    )

    def finalize(
        *,
        state: str,
        finding: str | None,
        turn_id: str | None,
        accepted_by_app_server: bool,
        durably_visible: bool,
        completed: bool,
        usage_limited: bool,
        timed_out: bool,
        real_app_server_process_started: bool,
        turn_submitted_to_real_codex: bool,
        rpc: Mapping[str, Any] | None = None,
        process_error: Mapping[str, Any] | None = None,
        matched_turn: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if state != "starting":
            _append_persistent_real_phase(
                paths,
                thread_id=thread_id,
                carrier_key=carrier_key,
                idempotency_key_safe=idempotency_key_safe,
                state=state,
                stale_after_seconds=stale_after_seconds,
                turn_id=turn_id,
                phases=phases,
                extra={
                    "accepted_by_app_server": accepted_by_app_server,
                    "durably_visible": durably_visible,
                    "completed": completed,
                    "finding": finding,
                    "real_app_server_process_started": real_app_server_process_started,
                },
            )
        final_status = _write_persistent_final_status(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state=state,
            turn_id=turn_id,
            finding=finding,
            extra={
                "allow_real_app_server": True,
                "fake_app_server_runner": False,
                "real_app_server_process_started": real_app_server_process_started,
                "turn_submitted_to_real_codex": turn_submitted_to_real_codex,
                "accepted_by_app_server": accepted_by_app_server,
                "durably_visible": durably_visible,
                "completed": completed,
                "usage_limited": usage_limited,
                "timed_out": timed_out,
                "lifecycle_phases": phases,
                "matched_turn": _sanitize(matched_turn, limit=3_000),
                "process_error": _sanitize(process_error, limit=1_500),
            },
        )
        lock["state"] = state
        lock["updated_at"] = _now()
        lock["real_app_server_process_started"] = real_app_server_process_started
        _write_json(paths["lock"], lock)
        receipt = {
            "schema_id": "ion.codex_app_server_persistent_carrier_real_process_runner_receipt.v0_1_candidate",
            "created_at": lock["created_at"],
            "updated_at": _now(),
            "thread_id": thread_id,
            "session_id": thread_id,
            **carrier_identity,
            "idempotency_key_safe": idempotency_key_safe,
            "prompt_sha256": prompt_hash,
            "prompt_redacted": prompt,
            "allow_real_app_server": True,
            "fake_app_server_runner": False,
            "mock_app_server": False,
            "dry_run": False,
            "real_app_server_process_started": real_app_server_process_started,
            "turn_submitted_to_real_codex": turn_submitted_to_real_codex,
            "submitted": turn_submitted_to_real_codex,
            "accepted_by_app_server": accepted_by_app_server,
            "durably_visible": durably_visible,
            "completed": completed,
            "usage_limited": usage_limited,
            "timed_out": timed_out,
            "turn_id": turn_id,
            "state": state,
            "finding": finding,
            "command_argv": command,
            "lifecycle_phases": phases,
            "sandbox_policy": sandbox,
            "writable_root_resolution": writable_root_resolution,
            "lifecycle_paths": _persistent_carrier_path_refs(root, paths),
            "final_status": _sanitize(final_status, limit=4_000),
            "rpc_summary": _sanitize(rpc or {}, limit=6_000),
            "process_error": _sanitize(process_error, limit=1_500),
            **AUTHORITY_FALSE,
            "non_claims": [
                *NON_CLAIMS,
                "Real process runner starts Codex app-server only behind confirmation, idempotency, and allow_real_app_server gates.",
                "Candidate lifecycle artifacts are not accepted state or materialization.",
            ],
        }
        _write_json(paths["run_receipt"], receipt)
        ok = completed and durably_visible and not usage_limited and not timed_out and not process_error
        payload = _base(route_id, ok=ok, finding=finding)
        payload.update(
            {
                "thread_id": thread_id,
                "session_id": thread_id,
                **carrier_identity,
                "allow_real_app_server": True,
                "fake_app_server_runner": False,
                "mock_app_server": False,
                "dry_run": False,
                "real_process_runner_implemented": True,
                "real_app_server_process_started": real_app_server_process_started,
                "turn_submitted_to_real_codex": turn_submitted_to_real_codex,
                "mutates_active_state": True,
                "submitted": turn_submitted_to_real_codex,
                "accepted_by_app_server": accepted_by_app_server,
                "durably_visible": durably_visible,
                "completed": completed,
                "usage_limited": usage_limited,
                "timed_out": timed_out,
                "turn_id": turn_id,
                "state": state,
                "lifecycle_phases": phases,
                "receipt_path": _repo_rel(root, paths["run_receipt"]),
                "lock_path": _repo_rel(root, paths["lock"]),
                "heartbeat_path": _repo_rel(root, paths["heartbeat"]),
                "final_status_path": _repo_rel(root, paths["final_status"]),
                "stderr_log_path": _repo_rel(root, paths["stderr_log"]),
                "stdout_jsonl_path": _repo_rel(root, paths["stdout_jsonl"]),
                "writable_root_resolution": writable_root_resolution,
                "status": _persistent_carrier_status_data(root, thread_id, carrier_key, args),
            }
        )
        if payload["ok"] is False and "finding" not in payload:
            payload["finding"] = "persistent_carrier_real_runner_incomplete"
        return payload

    try:
        process_factory = args.get("_process_factory") if callable(args.get("_process_factory")) else None
        rpc = _run_app_server_jsonrpc(
            requests,
            timeout_seconds=timeout_seconds,
            wait_for_methods=wait_for_methods,
            process_factory=process_factory,
            command=command,
        )
    except Exception as exc:
        process_error = {"finding": "persistent_carrier_process_start_failed", "error": _redact(exc, limit=1_000)}
        paths["stderr_log"].parent.mkdir(parents=True, exist_ok=True)
        paths["stderr_log"].write_text(json.dumps(process_error, sort_keys=True) + "\n", encoding="utf-8")
        return finalize(
            state="process_start_failed",
            finding="persistent_carrier_process_start_failed",
            turn_id=None,
            accepted_by_app_server=False,
            durably_visible=False,
            completed=False,
            usage_limited=False,
            timed_out=False,
            real_app_server_process_started=False,
            turn_submitted_to_real_codex=False,
            process_error=process_error,
        )

    _write_persistent_rpc_logs(paths, rpc)
    result, error = _result_for_id(rpc, "turn_start")
    turn_id = _turn_id_from_result(result)
    turns_result, _turns_error = _result_for_id(rpc, "turns")
    turns = (turns_result or {}).get("data") if isinstance(turns_result, Mapping) else None
    matched_turn = _match_turn_by_id(turns, turn_id) if turn_id else None
    visible_turn_status = _turn_status_text(matched_turn or {})
    completion_observed = _completion_observation(rpc)
    usage_limited = _usage_limit_signal({"rpc": rpc, "turn_start_result": result, "turn_start_error": error})
    timed_out = bool(rpc.get("timed_out"))
    accepted_by_app_server = not bool(error) and bool(turn_id) and not usage_limited
    turn_submitted_to_real_codex = accepted_by_app_server
    durably_visible = bool(matched_turn)
    completed = bool(durably_visible and (completion_observed["completion_inferred_from_notifications"] or _normalize_turn_status(visible_turn_status) == "completed"))

    if usage_limited:
        state = "usage_limited"
        finding = "persistent_carrier_usage_limit"
    elif timed_out:
        state = "timeout"
        finding = "persistent_carrier_timeout"
    elif error or not turn_id:
        state = "error"
        finding = (error or {}).get("finding") or "persistent_carrier_turn_start_error"
    elif durably_visible and _turn_status_is_terminal(visible_turn_status) and not completed:
        state = _normalize_turn_status(visible_turn_status) or "error"
        finding = "persistent_carrier_terminal_non_completed"
    elif completed:
        state = "completed"
        finding = None
    elif durably_visible:
        state = "visible_not_completed"
        finding = "persistent_carrier_visible_not_completed"
    else:
        state = "exact_turn_not_visible"
        finding = "persistent_carrier_exact_turn_not_visible"

    _append_persistent_real_phase(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="submitted",
        stale_after_seconds=stale_after_seconds,
        turn_id=turn_id,
        phases=phases,
        extra={
            "accepted_by_app_server": accepted_by_app_server,
            "real_app_server_process_started": True,
            "turn_submitted_to_real_codex": turn_submitted_to_real_codex,
        },
    )
    if durably_visible:
        _append_persistent_real_phase(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state="visible",
            stale_after_seconds=stale_after_seconds,
            turn_id=turn_id,
            phases=phases,
            extra={"durably_visible": True, "matched_turn_status": visible_turn_status},
        )
    return finalize(
        state=state,
        finding=finding,
        turn_id=turn_id,
        accepted_by_app_server=accepted_by_app_server,
        durably_visible=durably_visible,
        completed=completed,
        usage_limited=usage_limited,
        timed_out=timed_out,
        real_app_server_process_started=True,
        turn_submitted_to_real_codex=turn_submitted_to_real_codex,
        rpc=rpc,
        matched_turn=matched_turn,
    )


def _persistent_carrier_start(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "persistent_carrier_start"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    prompt_raw = str(args.get("prompt") or "")
    prompt = _redact(prompt_raw, limit=8_000)
    if not prompt:
        return _blocked(route_id, "prompt_required")
    allow_real_app_server = _truthy(args.get("allow_real_app_server"))
    mock_or_dry_run = _truthy(args.get("mock_app_server")) or _truthy(args.get("dry_run"))
    if not (mock_or_dry_run or allow_real_app_server):
        return _blocked(
            route_id,
            "persistent_carrier_real_start_requires_allow_real_app_server",
            refusal_class="LIVE_EXECUTION_NOT_ENABLED",
            data={"allow_real_app_server_required": True, "mock_app_server_required": True, "dry_run_supported": True},
        )
    carrier_identity = _resolve_persistent_carrier_identity(root, thread_id, args)
    carrier_key = str(carrier_identity["canonical_carrier_id"])
    idempotency_key_safe = _safe_idempotency_key(args.get("idempotency_key"))
    prompt_hash = _prompt_sha256(prompt_raw)
    sandbox, writable_root_resolution = _sandbox_policy_details(args, root=root)
    paths = _persistent_carrier_paths(root, thread_id, carrier_key)
    stale_after_seconds = max(30, min(int(args.get("stale_after_seconds") or 180), 3600))
    heartbeat_interval_seconds = max(5, min(int(args.get("heartbeat_interval_seconds") or 15), 120))

    status_before = _persistent_carrier_status_data(root, thread_id, carrier_key, args)
    existing_receipt = _read_json(paths["run_receipt"])
    if existing_receipt:
        if existing_receipt.get("idempotency_key_safe") == idempotency_key_safe and existing_receipt.get("prompt_sha256") == prompt_hash:
            payload = _base(route_id)
            payload.update(
                {
                    "idempotent_replay": True,
                    "thread_id": thread_id,
                    **carrier_identity,
                    "receipt_path": _repo_rel(root, paths["run_receipt"]),
                    "receipt": _sanitize(existing_receipt, limit=8_000),
                    "status": _persistent_carrier_status_data(root, thread_id, carrier_key, args),
                    "mutates_active_state": True,
                }
            )
            return payload
        if status_before["classification"] == "live":
            return _blocked(
                route_id,
                "persistent_carrier_live_lock_exists",
                refusal_class="LOCK_HELD",
                data={"thread_id": thread_id, **carrier_identity, "status": status_before},
            )
        return _blocked(
            route_id,
            "persistent_carrier_existing_receipt_conflict",
            refusal_class="IDEMPOTENCY_CONFLICT",
            data={"thread_id": thread_id, **carrier_identity, "receipt_path": _repo_rel(root, paths["run_receipt"])},
        )

    if status_before["classification"] == "live":
        return _blocked(
            route_id,
            "persistent_carrier_live_lock_exists",
            refusal_class="LOCK_HELD",
            data={"thread_id": thread_id, **carrier_identity, "status": status_before},
        )
    if str(status_before["classification"]).startswith("stale"):
        return _blocked(
            route_id,
            "persistent_carrier_stale_lock_requires_stop_or_recovery",
            refusal_class="STALE_LOCK_REQUIRES_EXPLICIT_RECOVERY",
            data={"thread_id": thread_id, **carrier_identity, "status": status_before},
        )

    if allow_real_app_server and not mock_or_dry_run:
        if _truthy(args.get("fake_app_server_runner")):
            return _persistent_carrier_start_fake_real_runner(
                root,
                args,
                thread_id=thread_id,
                prompt_raw=prompt_raw,
                prompt=prompt,
                carrier_identity=carrier_identity,
                carrier_key=carrier_key,
                idempotency_key_safe=idempotency_key_safe,
                prompt_hash=prompt_hash,
                sandbox=sandbox,
                writable_root_resolution=writable_root_resolution,
                paths=paths,
                stale_after_seconds=stale_after_seconds,
                heartbeat_interval_seconds=heartbeat_interval_seconds,
            )
        return _persistent_carrier_start_real_runner(
            root,
            args,
            thread_id=thread_id,
            prompt_raw=prompt_raw,
            prompt=prompt,
            carrier_identity=carrier_identity,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            prompt_hash=prompt_hash,
            sandbox=sandbox,
            writable_root_resolution=writable_root_resolution,
            paths=paths,
            stale_after_seconds=stale_after_seconds,
            heartbeat_interval_seconds=heartbeat_interval_seconds,
        )

    turn_id = _safe_turn_id(args.get("mock_turn_id") or f"mock-turn-{idempotency_key_safe[:16]}")
    terminal_status = str(args.get("mock_terminal_status") or "completed")
    leave_running = _truthy(args.get("mock_leave_running"))
    completed = (not leave_running) and _normalize_turn_status(terminal_status) == "completed"
    state = "running" if leave_running else "completed" if completed else terminal_status
    lock = {
        "schema_id": "ion.codex_app_server_persistent_carrier_lock.v0_1_candidate",
        "created_at": _now(),
        "updated_at": _now(),
        "thread_id": thread_id,
        "carrier_id": carrier_key,
        "idempotency_key_safe": idempotency_key_safe,
        "prompt_sha256": prompt_hash,
        "state": "running",
        "mock_app_server": True,
        "heartbeat_interval_seconds": heartbeat_interval_seconds,
        "stale_after_seconds": stale_after_seconds,
        **AUTHORITY_FALSE,
    }
    _write_json(paths["lock"], lock)
    _write_persistent_heartbeat(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="running",
        stale_after_seconds=stale_after_seconds,
        turn_id=turn_id,
        extra={"mock_app_server": True, "completed": False, "durably_visible": False},
    )
    _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "mock": True, "id": "initialize", "result": {"userAgent": "ion-test/mock"}})
    _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "mock": True, "id": "resume", "result": {"thread": {"id": thread_id, "sessionId": thread_id}}})
    _append_jsonl(paths["stdout_jsonl"], {"captured_at": _now(), "mock": True, "id": "turn_start", "result": {"turn": {"id": turn_id, "status": "inProgress" if leave_running else terminal_status}}})
    final_status = None
    if not leave_running:
        _write_persistent_heartbeat(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state=state,
            stale_after_seconds=stale_after_seconds,
            turn_id=turn_id,
            extra={"mock_app_server": True, "completed": completed, "durably_visible": True},
        )
        final_status = _write_persistent_final_status(
            paths,
            thread_id=thread_id,
            carrier_key=carrier_key,
            idempotency_key_safe=idempotency_key_safe,
            state=state,
            turn_id=turn_id,
            finding=None if completed else "mock_terminal_non_completed",
            extra={"mock_app_server": True, "completed": completed, "durably_visible": True},
        )
        lock["state"] = state
        lock["updated_at"] = _now()
        _write_json(paths["lock"], lock)
    receipt = {
        "schema_id": "ion.codex_app_server_persistent_carrier_run_receipt.v0_1_candidate",
        "created_at": _now(),
        "updated_at": _now(),
        "thread_id": thread_id,
        "session_id": thread_id,
        **carrier_identity,
        "idempotency_key_safe": idempotency_key_safe,
        "prompt_sha256": prompt_hash,
        "prompt_redacted": prompt,
        "mock_app_server": True,
        "dry_run": True,
        "submitted": True,
        "accepted_by_app_server": True,
        "durably_visible": not leave_running,
        "completed": completed,
        "turn_id": turn_id,
        "state": state,
        "sandbox_policy": sandbox,
        "writable_root_resolution": writable_root_resolution,
        "lifecycle_paths": _persistent_carrier_path_refs(root, paths),
        "final_status": _sanitize(final_status, limit=4_000),
        **AUTHORITY_FALSE,
        "non_claims": [*NON_CLAIMS, "Mock persistent carrier start did not start Codex app-server.", "Mock persistent carrier start did not submit a real model turn."],
    }
    _write_json(paths["run_receipt"], receipt)
    payload = _base(route_id, ok=completed or leave_running, finding=None if completed or leave_running else "mock_terminal_non_completed")
    payload.update(
        {
            "thread_id": thread_id,
            "session_id": thread_id,
            **carrier_identity,
            "mock_app_server": True,
            "dry_run": True,
            "mutates_active_state": True,
            "submitted": True,
            "accepted_by_app_server": True,
            "durably_visible": not leave_running,
            "completed": completed,
            "turn_id": turn_id,
            "state": state,
            "receipt_path": _repo_rel(root, paths["run_receipt"]),
            "lock_path": _repo_rel(root, paths["lock"]),
            "heartbeat_path": _repo_rel(root, paths["heartbeat"]),
            "final_status_path": _repo_rel(root, paths["final_status"]) if final_status else None,
            "writable_root_resolution": writable_root_resolution,
            "status": _persistent_carrier_status_data(root, thread_id, carrier_key, args),
        }
    )
    return payload


def _persistent_carrier_stop(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "persistent_carrier_stop"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    thread_id = _safe_thread_id(args.get("thread_id") or args.get("session_id"))
    carrier_identity = _resolve_persistent_carrier_identity(root, thread_id, args)
    carrier_key = str(carrier_identity["canonical_carrier_id"])
    idempotency_key_safe = _safe_idempotency_key(args.get("idempotency_key"))
    paths = _persistent_carrier_paths(root, thread_id, carrier_key)
    existing_stop = _read_json(paths["stop_receipt"])
    if existing_stop:
        if existing_stop.get("idempotency_key_safe") == idempotency_key_safe:
            payload = _base(route_id)
            payload.update({"idempotent_replay": True, "thread_id": thread_id, **carrier_identity, "stop_receipt": _sanitize(existing_stop, limit=4_000), "mutates_active_state": True})
            return payload
        return _blocked(route_id, "persistent_carrier_existing_stop_receipt_conflict", refusal_class="IDEMPOTENCY_CONFLICT")
    status_before = _persistent_carrier_status_data(root, thread_id, carrier_key, args)
    if status_before["classification"] == "missing":
        return _blocked(route_id, "persistent_carrier_not_found", refusal_class="NOT_FOUND", data={"thread_id": thread_id, **carrier_identity})
    reason = _redact(args.get("reason") or "operator_stop_requested", limit=1_000)
    stop_request = {
        "schema_id": "ion.codex_app_server_persistent_carrier_stop_request.v0_1_candidate",
        "created_at": _now(),
        "thread_id": thread_id,
        **carrier_identity,
        "idempotency_key_safe": idempotency_key_safe,
        "reason": reason,
        **AUTHORITY_FALSE,
    }
    _write_json(paths["stop_request"], stop_request)
    _write_persistent_heartbeat(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="stopped",
        stale_after_seconds=max(30, min(int(args.get("stale_after_seconds") or 180), 3600)),
        turn_id=((status_before.get("heartbeat") or {}) if isinstance(status_before.get("heartbeat"), Mapping) else {}).get("turn_id"),
        extra={"mock_app_server": True, "stop_requested": True},
    )
    final_status = _write_persistent_final_status(
        paths,
        thread_id=thread_id,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        state="stopped",
        turn_id=((status_before.get("heartbeat") or {}) if isinstance(status_before.get("heartbeat"), Mapping) else {}).get("turn_id"),
        finding="operator_stop_requested",
        extra={"mock_app_server": True, "stop_requested": True, "status_before": _sanitize(status_before, limit=4_000)},
    )
    stop_receipt = {
        "schema_id": "ion.codex_app_server_persistent_carrier_stop_receipt.v0_1_candidate",
        "created_at": _now(),
        "thread_id": thread_id,
        **carrier_identity,
        "idempotency_key_safe": idempotency_key_safe,
        "reason": reason,
        "status_before": _sanitize(status_before, limit=4_000),
        "final_status": _sanitize(final_status, limit=4_000),
        **AUTHORITY_FALSE,
        "non_claims": [*NON_CLAIMS, "Mock stop wrote lifecycle receipts only; no real process was signalled."],
    }
    _write_json(paths["stop_receipt"], stop_receipt)
    payload = _base(route_id)
    payload.update(
        {
            "thread_id": thread_id,
            **carrier_identity,
            "mutates_active_state": True,
            "stopped": True,
            "stop_request_path": _repo_rel(root, paths["stop_request"]),
            "stop_receipt_path": _repo_rel(root, paths["stop_receipt"]),
            "final_status_path": _repo_rel(root, paths["final_status"]),
            "status": _persistent_carrier_status_data(root, thread_id, carrier_key, args),
        }
    )
    return payload


def _app_server_status(args: Mapping[str, Any]) -> dict[str, Any]:
    rpc = _run_app_server_jsonrpc([_jsonrpc_initialize(), {"id": "loaded", "method": "thread/loaded/list", "params": {"limit": 1}}], timeout_seconds=max(3, min(int(args.get("timeout_seconds") or 8), 30)))
    init, error = _result_for_id(rpc, "initialize")
    payload = _base("app_server_status", ok=not bool(error), finding=(error or {}).get("finding"))
    payload.update({"available": not bool(error), "initialize": _sanitize(init, limit=1_500), "notifications": _sanitize(rpc.get("notifications"), limit=1_500), "stderr_lines": _sanitize(rpc.get("stderr_lines"), limit=1_000)})
    return payload


def invoke_codex_app_server_route(root: str | Path | None, *, route_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    try:
        if route_id == "app_server_status":
            return _app_server_status(args)
        if route_id == "thread_list":
            return _thread_list(args)
        if route_id == "thread_loaded_list":
            return _thread_loaded_list(args)
        if route_id == "thread_resume_preview":
            return _thread_resume_preview(args)
        if route_id == "thread_resume":
            return _thread_resume(args)
        if route_id == "thread_read":
            return _thread_read(args)
        if route_id == "thread_turns_list":
            return _thread_turns_list(args)
        if route_id == "thread_turn_read_by_id":
            return _thread_turn_read_by_id(args)
        if route_id == "turn_start_preview":
            return _turn_start_preview(args)
        if route_id == "turn_start":
            return _turn_start(shell_root, args)
        if route_id == "turn_poll":
            return _turn_poll(shell_root, args)
        if route_id == "turn_status":
            return _turn_status(shell_root, args)
        if route_id == "persistent_carrier_preview":
            return _persistent_carrier_preview(shell_root, args)
        if route_id == "persistent_carrier_start_preview":
            return _persistent_carrier_preview(shell_root, args, route_id="persistent_carrier_start_preview")
        if route_id == "persistent_carrier_start":
            return _persistent_carrier_start(shell_root, args)
        if route_id == "persistent_carrier_status":
            return _persistent_carrier_status(shell_root, args)
        if route_id == "persistent_carrier_stop":
            return _persistent_carrier_stop(shell_root, args)
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="SCHEMA_INVALID")
    return _blocked(route_id, "route_not_supported_by_codex_app_server", refusal_class="BRANCH_ROUTE_NOT_FOUND", data={"route_id": route_id})
