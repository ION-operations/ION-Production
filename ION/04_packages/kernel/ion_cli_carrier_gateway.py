"""Universal CLI Carrier Gateway — bounded multi-carrier routing for ChatGPT Browser lead.

Candidate-only. No arbitrary shell, secrets, accepted-state, or production authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from . import ion_cursor_packet_builder as _cpb

SCHEMA_ID = "ion.cli_carrier_gateway.v1_candidate"
REGISTRY_RELATIVE = Path("ION/03_registry/ion_cli_carrier_registry.yaml")
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
PACKET_SCHEMA_ID = "ion.cli_carrier_packet.v0_1"
RUN_ROUTES_ENABLED = True
RUN_ENABLED_CARRIERS = frozenset({"cursor_cli"})
LOOP_STATE_SCHEMA_ID = "ion.cli_carrier.loop_state.v0_1"
LOOP_DEFAULT_MAX_PACKETS = 1
LOOP_MAX_PACKETS_CEILING = 10
LOOP_MAX_TURNS_CEILING = 20
BATCH_DEFAULT_MAX_OBJECTIVES = 5
BATCH_MAX_OBJECTIVES_CEILING = 10

_BATCH_ROUTE_SHARED_KEYS = (
    "domain_id",
    "role",
    "lane",
    "allowed_paths",
    "forbidden_paths",
    "evidence_refs",
    "deliverable_kind",
    "mode",
    "cwd",
    "prompt_extra",
    "max_packets",
    "max_turns",
    "stop_on_failure",
    "stop_on_usage_limit",
    "allowed_carriers",
    "carrier_preference",
)

USAGE_LIMIT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"weekly\s+limit", re.I), "usage_limit"),
    (re.compile(r"hit\s+your\s+.*limit", re.I), "usage_limit"),
    (re.compile(r"usage.?limit", re.I), "usage_limit"),
    (re.compile(r"rate.?limit", re.I), "rate_limit"),
    (re.compile(r"quota.?exceeded", re.I), "quota_exceeded"),
    (re.compile(r"auth.?required", re.I), "auth_required"),
    (re.compile(r"failed\s+to\s+authenticate", re.I), "auth_required"),
    (re.compile(r"oauth\s+access\s+token\s+has\s+expired", re.I), "auth_required"),
    (re.compile(r"authentication\s+failed", re.I), "auth_required"),
    (re.compile(r"login.?required", re.I), "login_required"),
    (re.compile(r"not\s+logged\s+in", re.I), "login_required"),
    (re.compile(r"unavailable", re.I), "unavailable"),
    (re.compile(r"transient", re.I), "transient_usage_limit"),
)

FORBIDDEN_CWD_PARTS = frozenset({".git", ".ssh", ".gnupg", "node_modules"})
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9_]{16,}|Bearer\s+[A-Za-z0-9._~+/=-]{12,})"
)

NON_CLAIMS = [
    "candidate_only",
    "no_proven_true",
    "no_accepted_state",
    "no_live_execution_unless_explicitly_enabled",
    "cursor_cli_run_route_enabled_candidate_only",
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
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _redact(text: str, *, limit: int = 2000) -> str:
    out = SECRET_RE.sub("***REDACTED***", str(text or ""))
    return out[:limit] + ("...[truncated]" if len(out) > limit else "")


def _load_yaml(path: Path) -> dict[str, Any]:
    from .ion_action_mcp_branch_leaders import _load_yaml_mapping

    return _load_yaml_mapping(path.read_text(encoding="utf-8"))


def _resolve_executable(binary: str, *, extra_env_keys: tuple[str, ...] = ()) -> str | None:
    """Resolve a bounded carrier executable for non-login service environments.

    ION often runs from a service/tunnel environment whose PATH does not match
    the operator's interactive Pop!_OS shell. Cursor's agent binary is commonly
    installed into per-user bin directories, so PATH-only probing can falsely
    report cursor_cli unavailable. This resolver preserves PATH lookup first,
    then checks explicit env overrides and a small allowlisted set of common
    per-user/system binary locations. It does not invoke a shell or scan broad
    filesystem trees.
    """
    name = str(binary or "").strip()
    if not name:
        return None
    direct = Path(name).expanduser()
    if direct.is_absolute() and direct.is_file() and os.access(direct, os.X_OK):
        return str(direct)
    found = shutil.which(name)
    if found:
        return found
    for key in extra_env_keys:
        value = os.environ.get(key)
        if not value:
            continue
        candidate = Path(value).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    home = Path.home()
    candidates = [
        home / ".local" / "bin" / name,
        home / "bin" / name,
        home / ".cursor" / "bin" / name,
        home / ".config" / "Cursor" / "bin" / name,
        Path("/usr/local/bin") / name,
        Path("/usr/bin") / name,
        Path("/opt/Cursor") / name,
        Path("/opt/cursor") / name,
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    if name == "cursor-agent":
        cursor_roots = [
            home / ".cursor",
            home / ".cursor-server",
            home / ".config" / "Cursor",
            home / ".cache" / "Cursor",
            home / ".cache" / "cursor",
            Path("/opt/Cursor"),
            Path("/opt/cursor"),
            Path("/usr/share/cursor"),
        ]
        for cursor_root in cursor_roots:
            if not cursor_root.is_dir():
                continue
            checked = 0
            for candidate in cursor_root.glob("**/cursor-agent"):
                checked += 1
                if checked > 50:
                    break
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    return str(candidate)
    return None


def _resolve_cursor_agent() -> str | None:
    return _resolve_executable(
        "cursor-agent",
        extra_env_keys=("ION_CURSOR_AGENT_BIN", "CURSOR_AGENT_BIN", "CURSOR_CLI_BIN"),
    )


def load_registry(root: Path) -> dict[str, Any]:
    path = root / REGISTRY_RELATIVE
    if not path.is_file():
        raise FileNotFoundError(str(REGISTRY_RELATIVE))
    return _load_yaml(path)


def runtime_dirs(root: Path, registry: Mapping[str, Any]) -> dict[str, Path]:
    roots = registry.get("runtime_roots") if isinstance(registry.get("runtime_roots"), Mapping) else {}
    out: dict[str, Path] = {}
    for key, rel in roots.items():
        p = (root / str(rel)).resolve()
        p.mkdir(parents=True, exist_ok=True)
        out[str(key)] = p
    return out


def _blocked(route_id: str, finding: str, *, refusal_class: str = "SCHEMA_INVALID", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "operation": route_id,
        "ok": False,
        "finding": finding,
        "refusal_class": refusal_class,
        "mutates_active_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
        "packet_path": None,
        "result_path": None,
    }
    payload.update(extra)
    return payload


def _schema_refusal(route_id: str, finding: str, **extra: Any) -> dict[str, Any]:
    return _blocked(
        route_id,
        finding,
        refusal_class="SCHEMA_INVALID",
        packet_path=None,
        result_path=None,
        builder_receipt_path=None,
        **extra,
    )


def _ok(route_id: str, **data: Any) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "operation": route_id,
        "ok": True,
        "generated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "non_claims": list(NON_CLAIMS),
        **data,
    }


def normalize_usage_limit_signal(text: str) -> str:
    for pattern, label in USAGE_LIMIT_PATTERNS:
        if pattern.search(text):
            return label
    return "unknown_failure"


def refuse_shell_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    if any(ch in value for ch in (";", "|", "&", "`", "$", "\n", "\r")):
        return "shell_metacharacters_forbidden"
    if value.strip().startswith("sudo ") or " bash -c " in value:
        return "shell_invocation_forbidden"
    return None


def validate_cwd(root: Path, cwd: str) -> tuple[Path | None, str | None]:
    if not cwd or not str(cwd).strip():
        return None, "cwd_required"
    shell_err = refuse_shell_string(cwd)
    if shell_err:
        return None, shell_err
    rel = Path(str(cwd).strip())
    if rel.is_absolute():
        target = rel.resolve()
    else:
        target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None, "cwd_not_under_ion_root"
    parts = {p.lower() for p in target.parts}
    if parts & FORBIDDEN_CWD_PARTS:
        return None, "cwd_forbidden_part"
    if not target.is_dir():
        return None, "cwd_not_directory"
    return target, None


def _probe_argv(root: Path, carrier: Mapping[str, Any]) -> tuple[bool, str, str]:
    probe = carrier.get("executable_probe")
    if probe is None and carrier.get("carrier_id") == "codex_app_server":
        try:
            from .ion_codex_app_server_bridge import invoke_codex_app_server_route

            result = invoke_codex_app_server_route(root, route_id="app_server_status", args={})
            available = bool(result.get("ok")) and bool(result.get("available", result.get("ok")))
            return available, _redact(str(result.get("finding") or "ok")), "codex_app_server_bridge"
        except Exception as exc:
            return False, _redact(str(exc)), "codex_app_server_bridge_error"
    argv = carrier.get("version_argv")
    if isinstance(argv, list) and argv:
        cmd = [str(x) for x in argv]
    elif probe:
        exe = _resolve_executable(str(probe))
        if not exe:
            return False, "executable_not_on_path", str(probe)
        cmd = [exe, "--version"]
    else:
        return False, "no_probe_configured", str(carrier.get("carrier_id"))
    exe = _resolve_executable(cmd[0]) if not Path(cmd[0]).is_file() else cmd[0]
    if not exe:
        return False, "executable_not_on_path", cmd[0]
    cmd[0] = exe
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "probe_timeout", cmd[0]
    except OSError as exc:
        return False, _redact(str(exc)), cmd[0]
    combined = _redact((completed.stdout or "") + (completed.stderr or ""))
    if completed.returncode != 0:
        signal = normalize_usage_limit_signal(combined)
        return False, signal, cmd[0]
    return True, combined[:240] or "ok", cmd[0]


def carrier_manifest(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    carriers = []
    for row in registry.get("carriers") or []:
        if not isinstance(row, dict):
            continue
        carriers.append(
            {
                "carrier_id": row.get("carrier_id"),
                "family": row.get("family"),
                "packet_modes": row.get("packet_modes"),
                "allowed_operations": row.get("allowed_operations"),
                "authority_ceiling": row.get("authority_ceiling"),
                "run_route_enabled": bool(RUN_ROUTES_ENABLED and row.get("carrier_id") in RUN_ENABLED_CARRIERS),
            }
        )
    return _ok(
        "carrier_manifest",
        registry_schema=registry.get("schema_id"),
        carriers=carriers,
        run_routes_enabled=RUN_ROUTES_ENABLED,
    )


def carrier_status(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    dirs = runtime_dirs(root, registry)
    registered_ids = {
        str(row.get("carrier_id") or "")
        for row in registry.get("carriers") or []
        if isinstance(row, Mapping) and row.get("carrier_id")
    }
    pruned_status_cache: list[str] = []
    for status_path in dirs["status"].glob("*.json"):
        if status_path.stem in registered_ids or status_path.is_symlink() or not status_path.is_file():
            continue
        status_path.unlink()
        pruned_status_cache.append(_repo_rel(root, status_path))
    rows = []
    for row in registry.get("carriers") or []:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("carrier_id") or "")
        available, detail, probe_cmd = _probe_argv(root, row)
        status_path = dirs["status"] / f"{cid}.json"
        status_payload = {
            "carrier_id": cid,
            "available": available,
            "detail": detail,
            "probe_cmd": probe_cmd,
            "updated_at": _now(),
        }
        status_path.write_text(json.dumps(status_payload, indent=2) + "\n", encoding="utf-8")
        rows.append(status_payload)
    return _ok(
        "carrier_status",
        carriers=rows,
        status_dir=_repo_rel(root, dirs["status"]),
        pruned_status_cache=sorted(pruned_status_cache),
    )


def carrier_select_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    preference = args.get("carrier_preference")
    pref_list = [str(x) for x in preference] if isinstance(preference, list) else []
    posture = str(args.get("selection_posture") or args.get("posture") or "").strip() or None
    domain_id = str(args.get("domain_id") or "").strip() or None
    work_class = str(args.get("work_class") or "").strip() or None
    try:
        from .ion_cli_model_selection import resolve_execution_selection

        selection = resolve_execution_selection(
            root,
            domain_id=domain_id,
            carrier=str(args.get("carrier") or "auto"),
            work_class=work_class,
            posture=posture,
            allowed_carriers=pref_list or None,
        )
        chain = selection.get("fallback_chain") if isinstance(selection.get("fallback_chain"), list) else []
        ranked = selection.get("ranked_candidates") if isinstance(selection.get("ranked_candidates"), list) else []
        blocked = [
            {
                "carrier_id": row.get("carrier_id"),
                "model": row.get("model"),
                "blocker": row.get("probe_detail") or "unavailable",
            }
            for row in chain
            if isinstance(row, Mapping) and not row.get("available")
        ]
        fallback = [
            f"{row.get('carrier_id')}:{row.get('model')}"
            for row in chain
            if isinstance(row, Mapping)
        ][1:]
        return _ok(
            "carrier_select_preview",
            selected_carrier=selection.get("carrier_id"),
            selected_model=selection.get("model"),
            selection_posture=selection.get("selection_posture"),
            ranked_candidates=ranked,
            blocked_carriers=blocked,
            fallback_order=fallback,
            unified_selection_schema=selection.get("schema_id"),
        )
    except Exception:
        pass
    if not pref_list:
        pref_list = [str(c.get("carrier_id")) for c in registry.get("carriers") or [] if isinstance(c, dict)]
    by_id = {
        str(c.get("carrier_id")): c for c in registry.get("carriers") or [] if isinstance(c, dict) and c.get("carrier_id")
    }
    ranked: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for cid in pref_list:
        carrier = by_id.get(cid)
        if not carrier:
            blocked.append({"carrier_id": cid, "blocker": "unknown_carrier_id"})
            continue
        available, detail, _ = _probe_argv(root, carrier)
        if available:
            ranked.append({"carrier_id": cid, "score": 100 - len(ranked), "detail": detail[:120]})
        else:
            blocked.append({"carrier_id": cid, "blocker": normalize_usage_limit_signal(detail) if detail else "unavailable"})
    selected = ranked[0]["carrier_id"] if ranked else None
    fallback = [r["carrier_id"] for r in ranked[1:]] + [b["carrier_id"] for b in blocked]
    return _ok(
        "carrier_select_preview",
        selected_carrier=selected,
        ranked_candidates=ranked,
        blocked_carriers=blocked,
        fallback_order=fallback,
    )


def _cursor_packet_model(packet: Mapping[str, Any]) -> tuple[str | None, str | None]:
    model = str(
        packet.get("requested_model")
        or packet.get("model")
        or _cpb.DEFAULT_CURSOR_MODEL
    ).strip()
    try:
        from .ion_cli_model_selection import is_operator_approved_model
    except ImportError:
        return None, "cursor_model_allowlist_unavailable"
    if (
        model not in _cpb.OPERATOR_APPROVED_CURSOR_MODELS
        or not is_operator_approved_model("cursor_cli", model)
    ):
        return None, "cursor_model_operator_allowlist_refused"
    return model, None


def _validate_packet(packet: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    if str(packet.get("schema_id") or "") != PACKET_SCHEMA_ID:
        return None, "packet_schema_id_mismatch"
    if not str(packet.get("objective") or "").strip():
        return None, "objective_required"
    authority = packet.get("authority") if isinstance(packet.get("authority"), Mapping) else {}
    for flag in ("production_authority", "live_execution_authority", "accepted_state_authority", "secrets_authority"):
        if authority.get(flag) is not False:
            return None, f"authority_must_be_false:{flag}"
    model, model_error = _cursor_packet_model(packet)
    if model_error or not model:
        return None, model_error or "cursor_model_operator_allowlist_refused"
    path_err = _cpb.validate_bounded_path_fields(
        allowed_paths=[str(item).strip() for item in (packet.get("allowed_paths") or []) if str(item).strip()]
        if isinstance(packet.get("allowed_paths"), list)
        else [],
        forbidden_paths=[str(item).strip() for item in (packet.get("forbidden_paths") or []) if str(item).strip()]
        if isinstance(packet.get("forbidden_paths"), list)
        else [],
        evidence_refs=[str(item).strip() for item in (packet.get("evidence_refs") or []) if str(item).strip()]
        if isinstance(packet.get("evidence_refs"), list)
        else [],
    )
    if path_err:
        return None, path_err
    validated = dict(packet)
    validated["requested_model"] = model
    return validated, None


def packet_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    packet = args.get("packet") if isinstance(args.get("packet"), Mapping) else args
    validated, err = _validate_packet(packet)
    if err or validated is None:
        return _blocked("packet_preview", err or "invalid_packet")
    cwd, cerr = validate_cwd(root, str(validated.get("cwd") or "."))
    if cerr:
        return _blocked("packet_preview", cerr)
    sel = carrier_select_preview(
        {"carrier_preference": validated.get("carrier_preference") or []},
        root=root,
        registry=registry,
    )
    return _ok(
        "packet_preview",
        packet_id=validated.get("packet_id"),
        cwd=_repo_rel(root, cwd) if cwd else None,
        selection=sel,
        deliverable_kind=validated.get("deliverable_kind"),
        mode=validated.get("mode"),
    )


def _require_mutation_fields(args: Mapping[str, Any]) -> str | None:
    if str(args.get("confirmation") or "") != CONFIRMATION_TOKEN:
        return "confirmation_required"
    if not str(args.get("idempotency_key") or "").strip():
        return "idempotency_key_required"
    if not str(args.get("agent_id") or "").strip():
        return "agent_id_required"
    if not str(args.get("lease_id") or "").strip():
        return "lease_id_required"
    return None


def packet_enqueue(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    err = _require_mutation_fields(args)
    if err:
        return _blocked("packet_enqueue", err, refusal_class="CONFIRMATION_REQUIRED")
    packet = args.get("packet") if isinstance(args.get("packet"), Mapping) else {}
    validated, perr = _validate_packet(packet)
    if perr or validated is None:
        return _blocked("packet_enqueue", perr or "invalid_packet")
    cwd, cerr = validate_cwd(root, str(validated.get("cwd") or "."))
    if cerr:
        return _blocked("packet_enqueue", cerr)
    dirs = runtime_dirs(root, registry)
    packet_id = str(validated.get("packet_id") or f"pkt_{uuid.uuid4().hex[:12]}")
    validated["packet_id"] = packet_id
    validated["enqueued_at"] = _now()
    path = dirs["packets"] / f"{packet_id}.json"
    if path.exists() and not args.get("overwrite"):
        return _blocked("packet_enqueue", "packet_exists", refusal_class="IDEMPOTENCY_REPLAY_BLOCKED")
    path.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema_id": "ion.cli_carrier.receipt.v0_1",
        "receipt_id": f"cli_rcpt_{uuid.uuid4().hex[:12]}",
        "created_at": _now(),
        "operation": "packet_enqueue",
        "packet_id": packet_id,
        "packet_path": _repo_rel(root, path),
        "sha256": _sha256_file(path),
        "non_claims": list(NON_CLAIMS),
    }
    receipt_path = dirs["receipts"] / f"{receipt['receipt_id']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return _ok(
        "packet_enqueue",
        packet_id=packet_id,
        packet_path=_repo_rel(root, path),
        receipt_path=_repo_rel(root, receipt_path),
        sha256=receipt["sha256"],
    )


def _blocked_run_route(route_id: str, *, finding: str = "blocked_live_execution_route_not_enabled", **extra: Any) -> dict[str, Any]:
    return _blocked(
        route_id,
        finding,
        refusal_class="LIVE_EXECUTION_AUTHORITY_REFUSED",
        run_routes_enabled=RUN_ROUTES_ENABLED,
        tranche_note="cursor_cli_only_tranche_2_gate",
        **extra,
    )


def _selected_carrier_for_packet(root: Path, registry: Mapping[str, Any], packet: Mapping[str, Any]) -> tuple[str | None, dict[str, Any]]:
    allowed = [str(c) for c in (packet.get("allowed_carriers") or []) if str(c)]
    preference = [str(c) for c in (packet.get("carrier_preference") or allowed) if str(c)]
    selection = carrier_select_preview(
        {"carrier_preference": preference},
        root=root,
        registry=registry,
    )
    selected = selection.get("selected_carrier")
    if allowed and selected not in set(allowed):
        allowed_set = set(allowed)
        ranked = selection.get("ranked_candidates") if isinstance(selection.get("ranked_candidates"), list) else []
        selected = next((row.get("carrier_id") for row in ranked if row.get("carrier_id") in allowed_set), None)
        selection = dict(selection)
        selection["allowed_carriers"] = allowed
        selection["selected_carrier"] = selected
        if selected is None:
            selection["finding"] = "no_allowed_carrier_available"
    return selected, selection


def _cursor_prompt(packet: Mapping[str, Any]) -> str:
    return (
        "ION bounded Cursor CLI carrier packet.\n"
        "Candidate-only. Do not claim accepted-state, production deployment, git push, deletion, or secrets.\n"
        "Return a compact result with: mission_satisfied, cycle_gate, artifact_paths, changed_paths, "
        "validation_refs, blocked_reason, and non_claims.\n\n"
        f"packet_id: {packet.get('packet_id')}\n"
        f"deliverable_kind: {packet.get('deliverable_kind')}\n"
        f"mode: {packet.get('mode')}\n"
        f"objective:\n{packet.get('objective')}\n\n"
        f"allowed_paths: {json.dumps(packet.get('allowed_paths') or [])}\n"
        f"forbidden_paths: {json.dumps(packet.get('forbidden_paths') or [])}\n"
    )


def _cursor_argv(model: str) -> list[str] | None:
    exe = _resolve_cursor_agent()
    if not exe:
        return None
    approved, error = _cursor_packet_model({"requested_model": model})
    if error or not approved:
        return None
    return [exe, "-fp", "--output-format", "text", "--model", approved]


def _cursor_packet_execution_admission(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build an artifact-free direct-gateway admission before provider contact."""

    validated, validation_error = _validate_packet(packet)
    blockers = [validation_error] if validation_error else []
    selected_model = (
        str((validated or {}).get("requested_model") or "").strip()
        if validated is not None
        else None
    )
    allowed = {
        str(item) for item in (packet.get("allowed_carriers") or []) if str(item)
    }
    if allowed and "cursor_cli" not in allowed:
        blockers.append("cursor_cli_not_allowed_by_packet")
    basis = {
        "schema_id": "ion.cli_carrier_gateway.cursor_execution_admission.v1",
        "packet_id": packet.get("packet_id"),
        "packet_sha256": hashlib.sha256(
            json.dumps(
                {key: value for key, value in packet.items() if not str(key).startswith("_")},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "carrier_id": "cursor_cli",
        "model": selected_model,
        "blockers": [item for item in blockers if item],
        "direct_execution_admitted": not blockers,
        "authorization_membrane": "direct_cursor_packet_admission",
        "prompt_spawn_binding_applicable": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    digest = hashlib.sha256(
        json.dumps(basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "admission_id": f"cursor_gateway_admission_{digest[:24]}",
        "admission_sha256": digest,
        **basis,
        "ok": not blockers,
    }


def _load_packet_for_run(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None, dict[str, Path] | None]:
    dirs = runtime_dirs(root, registry)
    packet_obj = args.get("packet") if isinstance(args.get("packet"), Mapping) else None
    packet_id = str(args.get("packet_id") or "").strip()
    if packet_obj is None and packet_id:
        packet_path = dirs["packets"] / f"{packet_id}.json"
        if not packet_path.is_file():
            return None, "packet_not_found", dirs
        packet_obj = json.loads(packet_path.read_text(encoding="utf-8"))
    if packet_obj is None:
        return None, "packet_or_packet_id_required", dirs
    validated, perr = _validate_packet(packet_obj)
    if perr or validated is None:
        return None, perr or "invalid_packet", dirs
    cwd, cerr = validate_cwd(root, str(validated.get("cwd") or "."))
    if cerr:
        return None, cerr, dirs
    validated["_resolved_cwd"] = str(cwd)
    return validated, None, dirs


def packet_run_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("packet_run_preview")
    packet, err, _dirs = _load_packet_for_run(args, root=root, registry=registry)
    if err or packet is None:
        return _blocked("packet_run_preview", err or "invalid_packet")
    selected, selection = _selected_carrier_for_packet(root, registry, packet)
    if selected != "cursor_cli":
        return _blocked_run_route("packet_run_preview", finding="selected_carrier_run_not_enabled", selected_carrier=selected, selection=selection)
    admission = _cursor_packet_execution_admission(packet)
    if not admission.get("ok"):
        return _blocked_run_route(
            "packet_run_preview",
            finding="cursor_gateway_execution_admission_blocked",
            blockers=admission.get("blockers"),
            gateway_admission=admission,
            artifact_writes=False,
            provider_contacted=False,
        )
    argv = _cursor_argv(str(admission.get("model") or ""))
    if not argv:
        return _blocked_run_route(
            "packet_run_preview",
            finding="cursor_cli_executable_not_on_path",
            gateway_admission=admission,
            artifact_writes=False,
            provider_contacted=False,
        )
    return _ok(
        "packet_run_preview",
        packet_id=packet.get("packet_id"),
        selected_carrier=selected,
        argv_preview=[Path(argv[0]).name, *argv[1:]],
        cwd=_repo_rel(root, Path(str(packet["_resolved_cwd"]))),
        stdin_prompt_sha256=hashlib.sha256(_cursor_prompt(packet).encode("utf-8")).hexdigest(),
        selection=selection,
        model=admission.get("model"),
        gateway_admission=admission,
        run_routes_enabled=RUN_ROUTES_ENABLED,
    )


def _loop_bounds(args: Mapping[str, Any]) -> tuple[int, int, bool, bool]:
    max_packets = min(max(int(args.get("max_packets") or LOOP_DEFAULT_MAX_PACKETS), 1), LOOP_MAX_PACKETS_CEILING)
    max_turns = min(max(int(args.get("max_turns") or max_packets), 1), LOOP_MAX_TURNS_CEILING)
    stop_on_failure = bool(args.get("stop_on_failure", True))
    stop_on_usage_limit = bool(args.get("stop_on_usage_limit", True))
    return max_packets, max_turns, stop_on_failure, stop_on_usage_limit


def _packet_is_cursor_eligible(root: Path, registry: Mapping[str, Any], packet: Mapping[str, Any]) -> tuple[bool, str | None, str | None]:
    allowed = [str(c) for c in (packet.get("allowed_carriers") or []) if str(c)]
    if allowed and "cursor_cli" not in set(allowed):
        return False, "codex_or_non_cursor_packet_skipped", None
    for forbidden in ("codex_cli", "codex_app_server", "gemini_cli", "claude_cli"):
        if forbidden in allowed and "cursor_cli" not in allowed:
            return False, "codex_or_non_cursor_packet_skipped", None
    selected, _selection = _selected_carrier_for_packet(root, registry, packet)
    if selected != "cursor_cli":
        return False, "selected_carrier_run_not_enabled", selected
    return True, None, selected


def _list_queued_cursor_packets(
    root: Path,
    registry: Mapping[str, Any],
    dirs: Mapping[str, Path],
    *,
    packet_ids: list[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    queued: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    id_filter = {pid.strip() for pid in (packet_ids or []) if str(pid).strip()}
    paths = sorted(dirs["packets"].glob("*.json"), key=lambda p: p.stat().st_mtime)
    for path in paths:
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            skipped.append({"packet_path": _repo_rel(root, path), "blocker": "invalid_packet_json"})
            continue
        if not isinstance(packet, dict):
            skipped.append({"packet_path": _repo_rel(root, path), "blocker": "invalid_packet_shape"})
            continue
        packet_id = str(packet.get("packet_id") or path.stem)
        if id_filter and packet_id not in id_filter:
            continue
        result_path = dirs["results"] / f"{packet_id}.json"
        if result_path.is_file():
            skipped.append({"packet_id": packet_id, "blocker": "result_already_exists"})
            continue
        validated, err = _validate_packet(packet)
        if err or validated is None:
            skipped.append({"packet_id": packet_id, "blocker": err or "invalid_packet"})
            continue
        cwd, cerr = validate_cwd(root, str(validated.get("cwd") or "."))
        if cerr:
            skipped.append({"packet_id": packet_id, "blocker": cerr})
            continue
        validated["_resolved_cwd"] = str(cwd)
        validated["packet_id"] = packet_id
        ok, blocker, selected = _packet_is_cursor_eligible(root, registry, validated)
        if not ok:
            skipped.append({"packet_id": packet_id, "blocker": blocker, "selected_carrier": selected})
            continue
        queued.append(validated)
    return queued, skipped


def _loop_state_path(dirs: Mapping[str, Path], loop_id: str) -> Path:
    return dirs["loops"] / f"{loop_id}.json"


def _load_loop_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def _save_loop_state(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(state), indent=2) + "\n", encoding="utf-8")


def _latest_loop_state(dirs: Mapping[str, Path]) -> tuple[str | None, dict[str, Any] | None]:
    paths = sorted(dirs["loops"].glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not paths:
        return None, None
    state = _load_loop_state(paths[0])
    return paths[0].stem, state


def _execute_cursor_packet(
    *,
    root: Path,
    registry: Mapping[str, Any],
    dirs: Mapping[str, Path],
    packet: Mapping[str, Any],
    dry_run: bool = False,
) -> dict[str, Any]:
    packet_id = str(packet.get("packet_id") or f"pkt_{uuid.uuid4().hex[:12]}")
    admission = _cursor_packet_execution_admission(packet)
    if not admission.get("ok"):
        return {
            "packet_id": packet_id,
            "terminal_status": "blocked",
            "usage_signal": "cursor_gateway_execution_admission_blocked",
            "blockers": list(admission.get("blockers") or []),
            "gateway_admission": admission,
            "artifact_writes": False,
            "provider_contacted": False,
            "blocked": True,
        }
    selected_model = str(admission.get("model") or "")
    argv = _cursor_argv(selected_model) if not dry_run else None
    if not dry_run and not argv:
        return {
            "packet_id": packet_id,
            "terminal_status": "blocked",
            "usage_signal": "cursor_cli_executable_not_on_path",
            "gateway_admission": admission,
            "artifact_writes": False,
            "provider_contacted": False,
            "blocked": True,
        }
    packet_path = dirs["packets"] / f"{packet_id}.json"
    if not packet_path.exists():
        packet_path.write_text(
            json.dumps({k: v for k, v in packet.items() if not str(k).startswith("_")}, indent=2) + "\n",
            encoding="utf-8",
        )
    result_path = dirs["results"] / f"{packet_id}.json"
    receipt_id = f"cli_run_rcpt_{uuid.uuid4().hex[:12]}"
    receipt_path = dirs["receipts"] / f"{receipt_id}.json"
    if dry_run:
        result = {
            "schema_id": "ion.cli_carrier.result.v0_1",
            "packet_id": packet_id,
            "carrier_id": "cursor_cli",
            "model": selected_model,
            "gateway_admission": admission,
            "started_at": _now(),
            "completed_at": _now(),
            "returncode": 0,
            "terminal_status": "dry_run",
            "usage_signal": None,
            "stdout": "dry_run",
            "stderr": "",
            "non_claims": list(NON_CLAIMS),
        }
        result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "schema_id": "ion.cli_carrier.receipt.v0_1",
            "receipt_id": receipt_id,
            "created_at": _now(),
            "operation": "packet_run",
            "carrier_id": "cursor_cli",
            "model": selected_model,
            "gateway_admission_id": admission.get("admission_id"),
            "gateway_admission_sha256": admission.get("admission_sha256"),
            "packet_id": packet_id,
            "packet_path": _repo_rel(root, packet_path),
            "result_path": _repo_rel(root, result_path),
            "result_sha256": _sha256_file(result_path),
            "terminal_status": result["terminal_status"],
            "usage_signal": None,
            "dry_run": True,
            "non_claims": list(NON_CLAIMS),
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return {
            "packet_id": packet_id,
            "result_path": _repo_rel(root, result_path),
            "receipt_path": _repo_rel(root, receipt_path),
            "terminal_status": result["terminal_status"],
            "usage_signal": None,
            "dry_run": True,
        }
    prompt = _cursor_prompt(packet)
    timeout = min(max(int(packet.get("max_runtime_seconds") or 120), 1), 600)
    assert argv is not None
    started_at = _now()
    try:
        completed = subprocess.run(
            argv,
            input=prompt,
            cwd=str(packet["_resolved_cwd"]),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        stdout = _redact(completed.stdout or "", limit=12000)
        stderr = _redact(completed.stderr or "", limit=6000)
        combined = f"{stdout}\n{stderr}"
        usage_signal = normalize_usage_limit_signal(combined) if completed.returncode != 0 else None
        terminal_status = (
            "usage_limited"
            if usage_signal in {"usage_limit", "rate_limit", "quota_exceeded", "transient_usage_limit"}
            else ("completed" if completed.returncode == 0 else "failed")
        )
        result = {
            "schema_id": "ion.cli_carrier.result.v0_1",
            "packet_id": packet_id,
            "carrier_id": "cursor_cli",
            "model": selected_model,
            "gateway_admission": admission,
            "started_at": started_at,
            "completed_at": _now(),
            "returncode": completed.returncode,
            "terminal_status": terminal_status,
            "usage_signal": usage_signal,
            "stdout": stdout,
            "stderr": stderr,
            "non_claims": list(NON_CLAIMS),
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "schema_id": "ion.cli_carrier.result.v0_1",
            "packet_id": packet_id,
            "carrier_id": "cursor_cli",
            "model": selected_model,
            "gateway_admission": admission,
            "started_at": started_at,
            "completed_at": _now(),
            "returncode": None,
            "terminal_status": "timeout",
            "usage_signal": "timeout",
            "stdout": _redact(getattr(exc, "stdout", "") or "", limit=12000),
            "stderr": _redact(getattr(exc, "stderr", "") or "", limit=6000),
            "non_claims": list(NON_CLAIMS),
        }
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema_id": "ion.cli_carrier.receipt.v0_1",
        "receipt_id": receipt_id,
        "created_at": _now(),
        "operation": "packet_run",
        "carrier_id": "cursor_cli",
        "model": selected_model,
        "gateway_admission_id": admission.get("admission_id"),
        "gateway_admission_sha256": admission.get("admission_sha256"),
        "packet_id": packet_id,
        "packet_path": _repo_rel(root, packet_path),
        "result_path": _repo_rel(root, result_path),
        "result_sha256": _sha256_file(result_path),
        "terminal_status": result["terminal_status"],
        "usage_signal": result.get("usage_signal"),
        "non_claims": list(NON_CLAIMS),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {
        "packet_id": packet_id,
        "result_path": _repo_rel(root, result_path),
        "receipt_path": _repo_rel(root, receipt_path),
        "result_sha256": receipt["result_sha256"],
        "terminal_status": result["terminal_status"],
        "usage_signal": result.get("usage_signal"),
    }


def cursor_autonomy_loop_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("cursor_autonomy_loop_preview")
    dirs = runtime_dirs(root, registry)
    max_packets, max_turns, stop_on_failure, stop_on_usage_limit = _loop_bounds(args)
    packet_ids = [str(x) for x in args.get("packet_ids") or [] if str(x)]
    queued, skipped = _list_queued_cursor_packets(root, registry, dirs, packet_ids=packet_ids or None)
    planned = queued[:max_packets]
    return _ok(
        "cursor_autonomy_loop_preview",
        selected_carrier="cursor_cli",
        queued_count=len(queued),
        planned_count=len(planned),
        skipped_count=len(skipped),
        planned_packet_ids=[p.get("packet_id") for p in planned],
        skipped=skipped[:20],
        stop_criteria={
            "max_packets": max_packets,
            "max_turns": max_turns,
            "stop_on_failure": stop_on_failure,
            "stop_on_usage_limit": stop_on_usage_limit,
            "codex_carriers_run_enabled": False,
        },
        run_routes_enabled=RUN_ROUTES_ENABLED,
    )


def cursor_autonomy_loop_run(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("cursor_autonomy_loop_run")
    err = _require_mutation_fields(args)
    if err:
        return _blocked("cursor_autonomy_loop_run", err, refusal_class="CONFIRMATION_REQUIRED")
    dirs = runtime_dirs(root, registry)
    max_packets, max_turns, stop_on_failure, stop_on_usage_limit = _loop_bounds(args)
    dry_run = bool(args.get("dry_run"))
    packet_ids = [str(x) for x in args.get("packet_ids") or [] if str(x)]
    queued, skipped = _list_queued_cursor_packets(root, registry, dirs, packet_ids=packet_ids or None)
    loop_id = str(args.get("loop_id") or f"loop_{uuid.uuid4().hex[:12]}")
    loop_path = _loop_state_path(dirs, loop_id)
    if loop_path.exists() and not args.get("overwrite"):
        return _blocked("cursor_autonomy_loop_run", "loop_exists", refusal_class="IDEMPOTENCY_REPLAY_BLOCKED")
    stop_criteria = {
        "max_packets": max_packets,
        "max_turns": max_turns,
        "stop_on_failure": stop_on_failure,
        "stop_on_usage_limit": stop_on_usage_limit,
        "codex_carriers_run_enabled": False,
    }
    state: dict[str, Any] = {
        "schema_id": LOOP_STATE_SCHEMA_ID,
        "loop_id": loop_id,
        "status": "running",
        "started_at": _now(),
        "completed_at": None,
        "selected_carrier": "cursor_cli",
        "max_packets": max_packets,
        "max_turns": max_turns,
        "turns_used": 0,
        "packets_attempted": 0,
        "packets_completed": 0,
        "stop_criteria": stop_criteria,
        "stop_reason": None,
        "pause_requested": False,
        "stop_requested": False,
        "dry_run": dry_run,
        "packet_results": [],
        "skipped": skipped[:50],
        "non_claims": list(NON_CLAIMS),
    }
    _save_loop_state(loop_path, state)
    stop_reason: str | None = None
    for packet in queued[:max_packets]:
        if state["turns_used"] >= max_turns:
            stop_reason = "max_turns_reached"
            break
        if state.get("pause_requested"):
            stop_reason = "pause_requested"
            state["status"] = "paused"
            break
        if state.get("stop_requested"):
            stop_reason = "stop_requested"
            state["status"] = "stopped"
            break
        state["turns_used"] += 1
        state["packets_attempted"] += 1
        run_result = _execute_cursor_packet(root=root, registry=registry, dirs=dirs, packet=packet, dry_run=dry_run)
        state["packet_results"].append(run_result)
        terminal = str(run_result.get("terminal_status") or "")
        if run_result.get("blocked"):
            stop_reason = str(run_result.get("usage_signal") or "blocked")
            state["status"] = "stopped"
            break
        if terminal in {"completed", "dry_run"}:
            state["packets_completed"] += 1
        if stop_on_usage_limit and terminal == "usage_limited":
            stop_reason = "usage_limit"
            state["status"] = "stopped"
            break
        if stop_on_failure and terminal in {"failed", "timeout", "blocked"}:
            stop_reason = f"packet_{terminal}"
            state["status"] = "stopped"
            break
        _save_loop_state(loop_path, state)
    else:
        if state["packets_attempted"] >= max_packets or len(queued[:max_packets]) <= state["packets_attempted"]:
            stop_reason = "max_packets_reached" if state["packets_attempted"] else "queue_empty"
        elif not queued:
            stop_reason = "queue_empty"
        else:
            stop_reason = "bounded_loop_complete"
    if state["status"] == "running":
        state["status"] = "completed" if stop_reason in {"max_packets_reached", "bounded_loop_complete", "queue_empty"} else "stopped"
    state["stop_reason"] = stop_reason
    state["completed_at"] = _now()
    _save_loop_state(loop_path, state)
    receipt = {
        "schema_id": "ion.cli_carrier.receipt.v0_1",
        "receipt_id": f"cli_loop_rcpt_{uuid.uuid4().hex[:12]}",
        "created_at": _now(),
        "operation": "cursor_autonomy_loop_run",
        "carrier_id": "cursor_cli",
        "loop_id": loop_id,
        "loop_path": _repo_rel(root, loop_path),
        "loop_sha256": _sha256_file(loop_path),
        "terminal_status": state["status"],
        "stop_reason": stop_reason,
        "dry_run": dry_run,
        "non_claims": list(NON_CLAIMS),
    }
    receipt_path = dirs["receipts"] / f"{receipt['receipt_id']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return _ok(
        "cursor_autonomy_loop_run",
        loop_id=loop_id,
        loop_path=_repo_rel(root, loop_path),
        loop_sha256=receipt["loop_sha256"],
        receipt_path=_repo_rel(root, receipt_path),
        selected_carrier="cursor_cli",
        terminal_status=state["status"],
        stop_reason=stop_reason,
        stop_criteria=stop_criteria,
        packets_attempted=state["packets_attempted"],
        packets_completed=state["packets_completed"],
        packet_results=state["packet_results"],
        dry_run=dry_run,
    )


def cursor_autonomy_loop_status(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    dirs = runtime_dirs(root, registry)
    loop_id = str(args.get("loop_id") or "").strip()
    if loop_id:
        state = _load_loop_state(_loop_state_path(dirs, loop_id))
        if state is None:
            return _ok("cursor_autonomy_loop_status", loop_id=loop_id, watch_status="not_found", loop_path=None)
        return _ok(
            "cursor_autonomy_loop_status",
            loop_id=loop_id,
            watch_status=state.get("status"),
            loop_path=_repo_rel(root, _loop_state_path(dirs, loop_id)),
            loop_sha256=_sha256_file(_loop_state_path(dirs, loop_id)),
            stop_reason=state.get("stop_reason"),
            stop_criteria=state.get("stop_criteria"),
            packets_attempted=state.get("packets_attempted"),
            packets_completed=state.get("packets_completed"),
            pause_requested=state.get("pause_requested"),
            stop_requested=state.get("stop_requested"),
            packet_results=state.get("packet_results"),
        )
    latest_id, state = _latest_loop_state(dirs)
    if state is None:
        return _ok("cursor_autonomy_loop_status", watch_status="no_loops", loop_id=None)
    return _ok(
        "cursor_autonomy_loop_status",
        loop_id=latest_id,
        watch_status=state.get("status"),
        loop_path=_repo_rel(root, _loop_state_path(dirs, str(latest_id))),
        stop_reason=state.get("stop_reason"),
        stop_criteria=state.get("stop_criteria"),
        packets_attempted=state.get("packets_attempted"),
        packets_completed=state.get("packets_completed"),
        pause_requested=state.get("pause_requested"),
        stop_requested=state.get("stop_requested"),
    )


def cursor_autonomy_loop_pause(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    err = _require_mutation_fields(args)
    if err:
        return _blocked("cursor_autonomy_loop_pause", err, refusal_class="CONFIRMATION_REQUIRED")
    dirs = runtime_dirs(root, registry)
    loop_id = str(args.get("loop_id") or "").strip()
    if not loop_id:
        loop_id, _ = _latest_loop_state(dirs)
    if not loop_id:
        return _blocked("cursor_autonomy_loop_pause", "loop_id_required")
    loop_path = _loop_state_path(dirs, loop_id)
    state = _load_loop_state(loop_path)
    if state is None:
        return _blocked("cursor_autonomy_loop_pause", "loop_not_found")
    state["pause_requested"] = True
    if state.get("status") == "running":
        state["status"] = "pause_requested"
    state["pause_requested_at"] = _now()
    _save_loop_state(loop_path, state)
    return _ok(
        "cursor_autonomy_loop_pause",
        loop_id=loop_id,
        loop_path=_repo_rel(root, loop_path),
        watch_status=state.get("status"),
        pause_requested=True,
    )


def cursor_autonomy_loop_stop(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    err = _require_mutation_fields(args)
    if err:
        return _blocked("cursor_autonomy_loop_stop", err, refusal_class="CONFIRMATION_REQUIRED")
    dirs = runtime_dirs(root, registry)
    loop_id = str(args.get("loop_id") or "").strip()
    if not loop_id:
        loop_id, _ = _latest_loop_state(dirs)
    if not loop_id:
        return _blocked("cursor_autonomy_loop_stop", "loop_id_required")
    loop_path = _loop_state_path(dirs, loop_id)
    state = _load_loop_state(loop_path)
    if state is None:
        return _blocked("cursor_autonomy_loop_stop", "loop_not_found")
    state["stop_requested"] = True
    if state.get("status") in {"running", "paused", "pause_requested"}:
        state["status"] = "stop_requested"
    state["stop_requested_at"] = _now()
    _save_loop_state(loop_path, state)
    return _ok(
        "cursor_autonomy_loop_stop",
        loop_id=loop_id,
        loop_path=_repo_rel(root, loop_path),
        watch_status=state.get("status"),
        stop_requested=True,
        stop_criteria=state.get("stop_criteria"),
    )


def cursor_autonomy_watch(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    status = cursor_autonomy_loop_status(args, root=root, registry=registry)
    preview = cursor_autonomy_loop_preview(
        {"max_packets": args.get("max_packets"), "max_turns": args.get("max_turns"), "packet_ids": args.get("packet_ids")},
        root=root,
        registry=registry,
    )
    return _ok(
        "cursor_autonomy_watch",
        loop=status,
        queue_preview={
            "queued_count": preview.get("queued_count"),
            "planned_count": preview.get("planned_count"),
            "planned_packet_ids": preview.get("planned_packet_ids"),
            "stop_criteria": preview.get("stop_criteria"),
        },
        selected_carrier="cursor_cli",
    )


def packet_run(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("packet_run")
    err = _require_mutation_fields(args)
    if err:
        return _blocked("packet_run", err, refusal_class="CONFIRMATION_REQUIRED")
    packet, perr, dirs = _load_packet_for_run(args, root=root, registry=registry)
    if perr or packet is None or dirs is None:
        return _blocked("packet_run", perr or "invalid_packet")
    selected, selection = _selected_carrier_for_packet(root, registry, packet)
    if selected != "cursor_cli":
        return _blocked_run_route("packet_run", finding="selected_carrier_run_not_enabled", selected_carrier=selected, selection=selection)
    admission = _cursor_packet_execution_admission(packet)
    if not admission.get("ok"):
        return _blocked_run_route(
            "packet_run",
            finding="cursor_gateway_execution_admission_blocked",
            blockers=admission.get("blockers"),
            gateway_admission=admission,
            artifact_writes=False,
            provider_contacted=False,
        )
    if not _cursor_argv(str(admission.get("model") or "")):
        return _blocked_run_route(
            "packet_run",
            finding="cursor_cli_executable_not_on_path",
            gateway_admission=admission,
            artifact_writes=False,
            provider_contacted=False,
        )
    run_result = _execute_cursor_packet(root=root, registry=registry, dirs=dirs, packet=packet, dry_run=bool(args.get("dry_run")))
    if run_result.get("blocked"):
        return _blocked_run_route(
            "packet_run",
            finding=str(run_result.get("usage_signal") or "blocked"),
            blockers=run_result.get("blockers"),
            gateway_admission=run_result.get("gateway_admission") or admission,
            artifact_writes=bool(run_result.get("artifact_writes")),
            provider_contacted=bool(run_result.get("provider_contacted")),
        )
    return _ok(
        "packet_run",
        packet_id=run_result.get("packet_id"),
        selected_carrier="cursor_cli",
        result_path=run_result.get("result_path"),
        receipt_path=run_result.get("receipt_path"),
        result_sha256=run_result.get("result_sha256"),
        terminal_status=run_result.get("terminal_status"),
        usage_signal=run_result.get("usage_signal"),
    )


def packet_poll(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("packet_poll")
    dirs = runtime_dirs(root, registry)
    packet_id = str(args.get("packet_id") or "").strip()
    if not packet_id:
        return _blocked("packet_poll", "packet_id_required")
    result_path = dirs["results"] / f"{packet_id}.json"
    if not result_path.is_file():
        return _ok("packet_poll", packet_id=packet_id, terminal_status="not_found", result_path=None)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return _ok(
        "packet_poll",
        packet_id=packet_id,
        terminal_status=result.get("terminal_status"),
        result_path=_repo_rel(root, result_path),
        result_sha256=_sha256_file(result_path),
        usage_signal=result.get("usage_signal"),
    )


def packet_result(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    dirs = runtime_dirs(root, registry)
    packet_id = str(args.get("packet_id") or "").strip()
    if not packet_id:
        return _blocked("packet_result", "packet_id_required")
    packet_path = dirs["packets"] / f"{packet_id}.json"
    if not packet_path.is_file():
        return _blocked("packet_result", "packet_not_found")
    result_path = dirs["results"] / f"{packet_id}.json"
    payload = {
        "packet_id": packet_id,
        "packet_path": _repo_rel(root, packet_path),
        "packet_sha256": _sha256_file(packet_path),
        "result_path": _repo_rel(root, result_path) if result_path.is_file() else None,
        "run_status": "enqueued_only" if not result_path.is_file() else "result_available",
    }
    return _ok("packet_result", **payload)


def carrier_capability_matrix(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    manifest = carrier_manifest(args, root=root, registry=registry)
    status = carrier_status(args, root=root, registry=registry)
    rows = []
    for c in manifest.get("carriers") or []:
        cid = c.get("carrier_id")
        st = next((x for x in status.get("carriers") or [] if x.get("carrier_id") == cid), {})
        rows.append({**c, "available": st.get("available"), "blocker": None if st.get("available") else st.get("detail")})
    return _ok("carrier_capability_matrix", matrix=rows, run_routes_enabled=RUN_ROUTES_ENABLED)


def cursor_packet_builder_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    built, err = _cpb.build_cursor_packet(args)
    if err or built is None:
        return _schema_refusal("cursor_packet_builder_preview", err or "build_failed")
    validated, verr = _validate_packet(built)
    if verr or validated is None:
        return _schema_refusal("cursor_packet_builder_preview", verr or "invalid_packet")
    cwd, cerr = validate_cwd(root, str(validated.get("cwd") or "."))
    if cerr:
        return _schema_refusal("cursor_packet_builder_preview", cerr)
    sel = carrier_select_preview(
        {"carrier_preference": validated.get("carrier_preference") or []},
        root=root,
        registry=registry,
    )
    preview = packet_preview({"packet": validated}, root=root, registry=registry)
    return _ok(
        "cursor_packet_builder_preview",
        cursor_packet_builder_domain_candidate_ok=True,
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
        packet=validated,
        builder_metadata=_cpb.packet_preview_metadata(validated),
        gateway_packet_preview=preview,
        selection=sel,
        cwd=_repo_rel(root, cwd) if cwd else None,
    )


def _objective_cycle_loop_args(args: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    stop = packet.get("stop_criteria") if isinstance(packet.get("stop_criteria"), Mapping) else {}
    return {
        "max_packets": args.get("max_packets", stop.get("max_packets", 1)),
        "max_turns": args.get("max_turns", stop.get("max_turns")),
        "stop_on_failure": args.get("stop_on_failure", stop.get("stop_on_failure", True)),
        "stop_on_usage_limit": args.get("stop_on_usage_limit", stop.get("stop_on_usage_limit", True)),
        "dry_run": args.get("dry_run"),
        "loop_id": args.get("loop_id"),
        "overwrite": args.get("overwrite"),
    }


def _objective_cycle_normalized_stop_criteria(args: Mapping[str, Any]) -> dict[str, Any]:
    max_packets, max_turns, stop_on_failure, stop_on_usage_limit = _loop_bounds(_cpb.merge_stop_criteria_args(args))
    return {
        "max_packets": max_packets,
        "max_turns": max_turns,
        "stop_on_failure": stop_on_failure,
        "stop_on_usage_limit": stop_on_usage_limit,
        "codex_carriers_run_enabled": False,
    }


def _objective_cycle_builder_args(args: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(args)
    out["stop_criteria"] = _objective_cycle_normalized_stop_criteria(args)
    return out


def _objective_cycle_stop_criteria(args: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    _ = packet
    return _objective_cycle_normalized_stop_criteria(args)


def _batch_stop_criteria_summary(
    route_args: Mapping[str, Any],
    planned_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Derive batch-level stop_criteria from route args or planned objective specs."""
    route_has_override = any(
        key in route_args and route_args.get(key) is not None
        for key in ("max_packets", "max_turns", "stop_on_failure", "stop_on_usage_limit", "stop_criteria")
    )
    if route_has_override:
        summary = _objective_cycle_normalized_stop_criteria(route_args)
        summary["derivation"] = "route_level"
        return summary

    per_objective: list[dict[str, Any]] = []
    for index, spec in enumerate(planned_specs):
        merged = _merge_objective_spec(route_args, spec, index=index)
        per_objective.append(_objective_cycle_normalized_stop_criteria(merged))

    if not per_objective:
        summary = _objective_cycle_normalized_stop_criteria(route_args)
        summary["derivation"] = "default_global"
        return summary

    summary: dict[str, Any] = {"codex_carriers_run_enabled": False, "derivation": "objectives_derived"}
    mixed = False
    for key in ("max_packets", "max_turns", "stop_on_failure", "stop_on_usage_limit"):
        values = {row[key] for row in per_objective}
        if len(values) == 1:
            summary[key] = next(iter(values))
        else:
            mixed = True
            summary[key] = "per_objective"
    if mixed:
        summary["derivation"] = "objectives_mixed"
        summary["per_objective_stop_criteria"] = [
            {
                "index": index,
                "max_packets": row["max_packets"],
                "max_turns": row["max_turns"],
                "stop_on_failure": row["stop_on_failure"],
                "stop_on_usage_limit": row["stop_on_usage_limit"],
            }
            for index, row in enumerate(per_objective)
        ]
    return summary


def _batch_bounds(args: Mapping[str, Any]) -> tuple[int, bool, bool]:
    max_objectives = min(
        max(int(args.get("max_objectives") or BATCH_DEFAULT_MAX_OBJECTIVES), 1),
        BATCH_MAX_OBJECTIVES_CEILING,
    )
    stop_on_failure = bool(args.get("stop_on_failure", True))
    stop_on_usage_limit = bool(args.get("stop_on_usage_limit", True))
    return max_objectives, stop_on_failure, stop_on_usage_limit


def _parse_objectives(args: Mapping[str, Any]) -> tuple[list[dict[str, Any]] | None, str | None]:
    raw = args.get("objectives")
    if raw is None:
        return None, "objectives_required"
    if not isinstance(raw, list):
        return None, "objectives_must_be_array"
    if not raw:
        return None, "objectives_empty"
    specs: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            return None, f"objective_spec_invalid_at_index_{index}"
        objective = str(item.get("objective") or "").strip()
        if not objective:
            return None, f"objective_required_at_index_{index}"
        specs.append(dict(item))
    return specs, None


def _merge_objective_spec(route_args: Mapping[str, Any], spec: Mapping[str, Any], *, index: int) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key in _BATCH_ROUTE_SHARED_KEYS:
        if key in route_args and route_args.get(key) is not None:
            merged[key] = route_args[key]
    merged.update(dict(spec))
    merged["objective"] = str(spec.get("objective") or "").strip()
    merged.setdefault("max_packets", 1)
    merged.setdefault("max_turns", 1)
    explicit_pid = str(spec.get("packet_id") or route_args.get("packet_id") or "").strip()
    if explicit_pid:
        merged["packet_id"] = explicit_pid.lower()
    elif "packet_id" not in merged:
        merged["packet_id"] = f"pckt-batch-{uuid.uuid4().hex[:10]}-obj-{index}"
    return merged


def _summarize_cycle_result(cycle_result: Mapping[str, Any], *, index: int) -> dict[str, Any]:
    loop = cycle_result.get("loop") if isinstance(cycle_result.get("loop"), Mapping) else {}
    packet_results = loop.get("packet_results") if isinstance(loop.get("packet_results"), list) else cycle_result.get("packet_results")
    first_result = packet_results[0] if isinstance(packet_results, list) and packet_results else {}
    usage_signal = cycle_result.get("usage_signal") or loop.get("usage_signal") or first_result.get("usage_signal")
    return {
        "index": index,
        "ok": bool(cycle_result.get("ok")),
        "packet_id": cycle_result.get("packet_id"),
        "packet_path": cycle_result.get("packet_path"),
        "builder_receipt_path": cycle_result.get("builder_receipt_path"),
        "loop_id": cycle_result.get("loop_id"),
        "loop_path": cycle_result.get("loop_path"),
        "loop_receipt_path": cycle_result.get("loop_receipt_path"),
        "terminal_status": cycle_result.get("terminal_status"),
        "stop_reason": cycle_result.get("stop_reason"),
        "finding": cycle_result.get("finding"),
        "usage_signal": usage_signal,
        "result_path": first_result.get("result_path") if isinstance(first_result, Mapping) else None,
        "receipt_path": first_result.get("receipt_path") if isinstance(first_result, Mapping) else None,
    }


def _summarize_objective_preview(spec: Mapping[str, Any], validated: Mapping[str, Any]) -> dict[str, Any]:
    stop = validated.get("stop_criteria") if isinstance(validated.get("stop_criteria"), Mapping) else {}
    return {
        "objective": spec.get("objective"),
        "packet_id": validated.get("packet_id"),
        "allowed_carriers": validated.get("allowed_carriers"),
        "forbidden_actions": validated.get("forbidden_actions"),
        "stop_criteria": stop,
        "builder_schema_id": validated.get("builder_schema_id"),
    }


def cursor_objective_batch_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    specs, err = _parse_objectives(args)
    if err or specs is None:
        return _blocked("cursor_objective_batch_preview", err or "objectives_invalid")
    max_objectives, stop_on_failure, stop_on_usage_limit = _batch_bounds(args)
    planned = specs[:max_objectives]
    stop_criteria = _batch_stop_criteria_summary(args, planned)
    skipped_objectives = [
        {
            "index": index,
            "objective": specs[index].get("objective"),
            "reason": "max_objectives_clamped",
        }
        for index in range(max_objectives, len(specs))
    ]
    previews: list[dict[str, Any]] = []
    refused_objectives: list[dict[str, Any]] = []
    for index, spec in enumerate(planned):
        merged = _merge_objective_spec(args, spec, index=index)
        built, berr = _cpb.build_cursor_packet(_objective_cycle_builder_args(merged))
        if berr or built is None:
            refused_objectives.append(
                {"index": index, "objective": spec.get("objective"), "reason": berr or "build_failed"}
            )
            if stop_on_failure:
                break
            continue
        validated, verr = _validate_packet(built)
        if verr or validated is None:
            refused_objectives.append(
                {"index": index, "objective": spec.get("objective"), "reason": verr or "invalid_packet"}
            )
            if stop_on_failure:
                break
            continue
        previews.append(_summarize_objective_preview(spec, validated))
    return _ok(
        "cursor_objective_batch_preview",
        objective_batch_runner_ok=True,
        route_ids=["cursor_objective_batch_preview", "cursor_objective_batch_run"],
        composed_routes=["cursor_objective_cycle_preview"],
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
        selected_carrier="cursor_cli",
        codex_carriers_run_enabled=False,
        queue_processing_mode="explicit_objectives_only",
        objectives_total=len(specs),
        objectives_planned=len(planned),
        objectives_clamped=len(specs) > max_objectives,
        max_objectives=max_objectives,
        stop_on_failure=stop_on_failure,
        stop_on_usage_limit=stop_on_usage_limit,
        stop_criteria=stop_criteria,
        packet_ids=[str(preview.get("packet_id") or "") for preview in previews if preview.get("packet_id")],
        skipped_objectives=skipped_objectives,
        refused_objectives=refused_objectives,
        objective_previews=previews,
    )


def cursor_objective_batch_run(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("cursor_objective_batch_run")
    err = _require_mutation_fields(args)
    if err:
        return _blocked("cursor_objective_batch_run", err, refusal_class="CONFIRMATION_REQUIRED")
    specs, parse_err = _parse_objectives(args)
    if parse_err or specs is None:
        return _blocked("cursor_objective_batch_run", parse_err or "objectives_invalid")
    max_objectives, stop_on_failure, stop_on_usage_limit = _batch_bounds(args)
    planned = specs[:max_objectives]
    batch_id = str(args.get("batch_id") or f"batch_{uuid.uuid4().hex[:12]}")
    dry_run = bool(args.get("dry_run"))
    overwrite = bool(args.get("overwrite"))
    objective_results: list[dict[str, Any]] = []
    refused_objectives: list[dict[str, Any]] = []
    stop_reason: str | None = None
    objectives_attempted = 0
    objectives_completed = 0
    for index, spec in enumerate(planned):
        merged = _merge_objective_spec(args, spec, index=index)
        merged.update(
            {
                "confirmation": args.get("confirmation"),
                "idempotency_key": f"{args.get('idempotency_key')}_obj_{index}",
                "agent_id": args.get("agent_id"),
                "lease_id": args.get("lease_id"),
                "dry_run": dry_run,
                "overwrite": overwrite,
                "loop_id": str(spec.get("loop_id") or merged.get("loop_id") or f"loop_{batch_id}_obj_{index}"),
            }
        )
        built, berr = _cpb.build_cursor_packet(_objective_cycle_builder_args(merged))
        if berr or built is None:
            reason = berr or "build_failed"
            refused_objectives.append({"index": index, "objective": spec.get("objective"), "reason": reason})
            objective_results.append(
                {
                    "index": index,
                    "ok": False,
                    "packet_id": merged.get("packet_id"),
                    "packet_path": None,
                    "builder_receipt_path": None,
                    "loop_id": merged.get("loop_id"),
                    "loop_path": None,
                    "loop_receipt_path": None,
                    "terminal_status": "blocked",
                    "stop_reason": reason,
                    "finding": reason,
                    "usage_signal": None,
                    "result_path": None,
                    "receipt_path": None,
                }
            )
            stop_reason = reason
            if stop_on_failure:
                break
            continue
        objectives_attempted += 1
        cycle_result = cursor_objective_cycle_run(merged, root=root, registry=registry)
        summary = _summarize_cycle_result(cycle_result, index=index)
        objective_results.append(summary)
        if not cycle_result.get("ok"):
            stop_reason = str(summary.get("finding") or f"objective_failed_at_index_{index}")
            if stop_on_failure:
                break
            continue
        terminal = str(cycle_result.get("terminal_status") or "")
        if terminal in {"completed", "dry_run"}:
            objectives_completed += 1
        if stop_on_usage_limit and terminal == "usage_limited":
            stop_reason = "usage_limit"
            break
        if stop_on_failure and terminal in {"failed", "timeout", "blocked", "stopped"}:
            stop_reason = f"objective_{terminal}_at_index_{index}"
            break
    else:
        if len(specs) > max_objectives:
            stop_reason = "max_objectives_reached"
        else:
            stop_reason = "batch_complete"
    batch_terminal = (
        "completed"
        if stop_reason == "batch_complete" and objectives_completed == objectives_attempted
        else "stopped"
    )
    stop_criteria = _batch_stop_criteria_summary(args, planned)
    return _ok(
        "cursor_objective_batch_run",
        objective_batch_runner_ok=True,
        route_ids=["cursor_objective_batch_preview", "cursor_objective_batch_run"],
        composed_routes=["cursor_objective_cycle_run"],
        batch_id=batch_id,
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
        selected_carrier="cursor_cli",
        codex_carriers_run_enabled=False,
        queue_processing_mode="explicit_objectives_only",
        objectives_total=len(specs),
        objectives_planned=len(planned),
        objectives_attempted=objectives_attempted,
        objectives_completed=objectives_completed,
        objectives_clamped=len(specs) > max_objectives,
        max_objectives=max_objectives,
        stop_on_failure=stop_on_failure,
        stop_on_usage_limit=stop_on_usage_limit,
        stop_criteria=stop_criteria,
        stop_reason=stop_reason,
        terminal_status=batch_terminal,
        dry_run=dry_run,
        refused_objectives=refused_objectives,
        objective_results=objective_results,
    )


def cursor_objective_cycle_preview(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    built, err = _cpb.build_cursor_packet(_objective_cycle_builder_args(args))
    if err or built is None:
        return _schema_refusal("cursor_objective_cycle_preview", err or "build_failed")
    validated, verr = _validate_packet(built)
    if verr or validated is None:
        return _schema_refusal("cursor_objective_cycle_preview", verr or "invalid_packet")
    cwd, cerr = validate_cwd(root, str(validated.get("cwd") or "."))
    if cerr:
        return _schema_refusal("cursor_objective_cycle_preview", cerr)
    stop_criteria = _objective_cycle_stop_criteria(args, validated)
    sel = carrier_select_preview(
        {"carrier_preference": validated.get("carrier_preference") or []},
        root=root,
        registry=registry,
    )
    return _ok(
        "cursor_objective_cycle_preview",
        cursor_objective_cycle_route_ok=True,
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
        composed_routes=["cursor_packet_builder_enqueue", "cursor_autonomy_loop_run"],
        packet=validated,
        builder_metadata=_cpb.packet_preview_metadata(validated),
        stop_criteria=stop_criteria,
        selected_carrier="cursor_cli",
        selection=sel,
        cwd=_repo_rel(root, cwd) if cwd else None,
    )


def cursor_objective_cycle_run(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not RUN_ROUTES_ENABLED:
        return _blocked_run_route("cursor_objective_cycle_run")
    err = _require_mutation_fields(args)
    if err:
        return _blocked("cursor_objective_cycle_run", err, refusal_class="CONFIRMATION_REQUIRED")
    objective = str(args.get("objective") or "").strip()
    if not objective:
        return _schema_refusal("cursor_objective_cycle_run", "objective_required")
    builder_args = _objective_cycle_builder_args(args)
    enqueue_result = cursor_packet_builder_enqueue(builder_args, root=root, registry=registry)
    if not enqueue_result.get("ok"):
        return enqueue_result
    packet_id = str(enqueue_result.get("packet_id") or "")
    built, berr = _cpb.build_cursor_packet(builder_args)
    if berr or built is None:
        return _schema_refusal("cursor_objective_cycle_run", berr or "build_failed", enqueue=enqueue_result)
    loop_args: dict[str, Any] = {
        "confirmation": args.get("confirmation"),
        "idempotency_key": args.get("idempotency_key"),
        "agent_id": args.get("agent_id"),
        "lease_id": args.get("lease_id"),
        "packet_ids": [packet_id],
        **_objective_cycle_loop_args(args, built),
    }
    if not str(loop_args.get("loop_id") or "").strip():
        loop_args["loop_id"] = f"loop_obj_{uuid.uuid4().hex[:12]}"
    loop_result = cursor_autonomy_loop_run(loop_args, root=root, registry=registry)
    if not loop_result.get("ok"):
        return {
            **loop_result,
            "cursor_objective_cycle_route_ok": False,
            "enqueue": enqueue_result,
            "composed_routes": ["cursor_packet_builder_enqueue", "cursor_autonomy_loop_run"],
        }
    return _ok(
        "cursor_objective_cycle_run",
        cursor_objective_cycle_route_ok=True,
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
        composed_routes=["cursor_packet_builder_enqueue", "cursor_autonomy_loop_run"],
        packet_id=packet_id,
        packet_path=enqueue_result.get("packet_path"),
        builder_receipt_path=enqueue_result.get("receipt_path"),
        enqueue=enqueue_result,
        loop=loop_result,
        loop_id=loop_result.get("loop_id"),
        loop_path=loop_result.get("loop_path"),
        loop_receipt_path=loop_result.get("receipt_path"),
        selected_carrier="cursor_cli",
        terminal_status=loop_result.get("terminal_status"),
        stop_reason=loop_result.get("stop_reason"),
        stop_criteria=loop_result.get("stop_criteria"),
        packets_attempted=loop_result.get("packets_attempted"),
        packets_completed=loop_result.get("packets_completed"),
        packet_results=loop_result.get("packet_results"),
        dry_run=loop_result.get("dry_run"),
    )


def cursor_packet_builder_enqueue(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    err = _require_mutation_fields(args)
    if err:
        return _blocked("cursor_packet_builder_enqueue", err, refusal_class="CONFIRMATION_REQUIRED")
    built, berr = _cpb.build_cursor_packet(args)
    if berr or built is None:
        return _schema_refusal("cursor_packet_builder_enqueue", berr or "build_failed")
    enqueue_args = {
        "confirmation": args.get("confirmation"),
        "idempotency_key": args.get("idempotency_key"),
        "agent_id": args.get("agent_id"),
        "lease_id": args.get("lease_id"),
        "overwrite": args.get("overwrite"),
        "packet": built,
    }
    result = packet_enqueue(enqueue_args, root=root, registry=registry)
    if not result.get("ok"):
        return result
    receipt = _cpb.builder_receipt(
        operation="cursor_packet_builder_enqueue",
        packet=built,
        packet_path=str(result.get("packet_path") or ""),
    )
    dirs = runtime_dirs(root, registry)
    receipt_path = dirs["receipts"] / f"{receipt['receipt_id']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return _ok(
        "cursor_packet_builder_enqueue",
        cursor_packet_builder_domain_candidate_ok=True,
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
        packet_id=result.get("packet_id"),
        packet_path=result.get("packet_path"),
        receipt_path=_repo_rel(root, receipt_path),
        builder_metadata=_cpb.packet_preview_metadata(built),
        enqueue_receipt_path=result.get("receipt_path"),
    )


CURSOR_FIRST_ROUTE_SURFACES = (
    "cursor_packet_builder_preview",
    "cursor_packet_builder_enqueue",
    "cursor_objective_cycle_preview",
    "cursor_objective_cycle_run",
    "cursor_objective_batch_preview",
    "cursor_objective_batch_run",
    "cursor_carrier_stack_status",
)

CURSOR_STACK_STATUS_NON_CLAIMS = (
    "candidate_only",
    "no_accepted_state",
    "no_domain_weaver_projection_mutation",
    "no_production_deployment",
    "no_git_push",
    "no_secrets_access",
    "no_codex",
)

CURSOR_STACK_ROUTE_IDS = CURSOR_FIRST_ROUTE_SURFACES + (
    "cursor_autonomy_loop_preview",
    "cursor_autonomy_loop_run",
    "cursor_autonomy_loop_status",
    "cursor_autonomy_watch",
)


def _cursor_first_routes_availability() -> dict[str, str]:
    return {
        route_id: "available" if route_id in ROUTE_HANDLERS else "missing_handler"
        for route_id in CURSOR_FIRST_ROUTE_SURFACES
    }


def cursor_carrier_stack_status(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    routes = _cursor_first_routes_availability()
    missing = [route_id for route_id, status in routes.items() if status != "available"]
    if missing:
        return _blocked(
            "cursor_carrier_stack_status",
            "cursor_first_route_handler_missing",
            refusal_class="BRANCH_ROUTE_NOT_FOUND",
            routes=routes,
            missing_handlers=missing,
        )
    raw_limit = args.get("receipt_limit")
    if raw_limit is None:
        receipt_limit = 5
    else:
        receipt_limit = min(max(int(raw_limit), 0), 20)
    recent_receipts: list[dict[str, str]] = []
    if receipt_limit:
        receipt_result = carrier_receipts({"limit": receipt_limit}, root=root, registry=registry)
        for row in receipt_result.get("receipts") or []:
            if isinstance(row, Mapping):
                recent_receipts.append(
                    {
                        "path": str(row.get("path") or ""),
                        "sha256": str(row.get("sha256") or ""),
                        "summary": str(row.get("summary") or ""),
                    }
                )
    return _ok(
        "cursor_carrier_stack_status",
        mutates_active_state=False,
        candidate_only=True,
        selected_carrier="cursor_cli",
        codex_carriers_run_enabled=False,
        queue_processing_mode="explicit_objectives_only",
        routes=routes,
        recent_receipts=recent_receipts,
        non_claims=list(CURSOR_STACK_STATUS_NON_CLAIMS),
        builder_schema_id=_cpb.BUILDER_SCHEMA_ID,
        builder_domain_id=_cpb.DOMAIN_ID,
    )


def carrier_receipts(args: Mapping[str, Any], *, root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    dirs = runtime_dirs(root, registry)
    limit = min(max(int(args.get("limit") or 20), 1), 100)
    receipts = []
    for path in sorted(dirs["receipts"].glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        data = json.loads(path.read_text(encoding="utf-8"))
        receipts.append({"path": _repo_rel(root, path), "sha256": _sha256_file(path), "summary": data.get("operation")})
    return _ok("carrier_receipts", receipts=receipts, count=len(receipts))


ROUTE_HANDLERS = {
    "carrier_manifest": carrier_manifest,
    "carrier_status": carrier_status,
    "carrier_capability_matrix": carrier_capability_matrix,
    "carrier_select_preview": carrier_select_preview,
    "packet_preview": packet_preview,
    "packet_enqueue": packet_enqueue,
    "packet_run_preview": packet_run_preview,
    "packet_run": packet_run,
    "packet_poll": packet_poll,
    "packet_result": packet_result,
    "carrier_receipts": carrier_receipts,
    "cursor_autonomy_loop_preview": cursor_autonomy_loop_preview,
    "cursor_autonomy_loop_run": cursor_autonomy_loop_run,
    "cursor_autonomy_loop_status": cursor_autonomy_loop_status,
    "cursor_autonomy_loop_pause": cursor_autonomy_loop_pause,
    "cursor_autonomy_loop_stop": cursor_autonomy_loop_stop,
    "cursor_autonomy_watch": cursor_autonomy_watch,
    "cursor_packet_builder_preview": cursor_packet_builder_preview,
    "cursor_packet_builder_enqueue": cursor_packet_builder_enqueue,
    "cursor_objective_cycle_preview": cursor_objective_cycle_preview,
    "cursor_objective_cycle_run": cursor_objective_cycle_run,
    "cursor_objective_batch_preview": cursor_objective_batch_preview,
    "cursor_objective_batch_run": cursor_objective_batch_run,
    "cursor_carrier_stack_status": cursor_carrier_stack_status,
}


def _assert_cursor_first_route_handler_parity() -> None:
    missing = [route_id for route_id in CURSOR_FIRST_ROUTE_SURFACES if route_id not in ROUTE_HANDLERS]
    if missing:
        raise RuntimeError(f"CURSOR_FIRST_ROUTE_SURFACES missing ROUTE_HANDLERS entries: {missing}")


_assert_cursor_first_route_handler_parity()


def invoke_multi_carrier_cli_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    try:
        registry = load_registry(shell_root)
    except FileNotFoundError:
        return _blocked(route_id, "cli_carrier_registry_missing", refusal_class="BRANCH_CONTEXT_NOT_MATERIALIZABLE")
    except RuntimeError as exc:
        return _blocked(route_id, str(exc))
    handler = ROUTE_HANDLERS.get(route_id)
    if not handler:
        if route_id in CURSOR_FIRST_ROUTE_SURFACES:
            return _blocked(
                route_id,
                "cursor_first_route_handler_missing",
                refusal_class="BRANCH_ROUTE_NOT_FOUND",
                routes=_cursor_first_routes_availability(),
            )
        return _blocked(route_id, "route_not_supported", refusal_class="BRANCH_ROUTE_NOT_FOUND")
    for key, value in args.items():
        if isinstance(value, str):
            shell_err = refuse_shell_string(value)
            if shell_err:
                return _blocked(route_id, shell_err)
    return handler(args, root=shell_root, registry=registry)
