"""Operator carrier settings (enable/limit/mode) for CLI spawn lanes.

Candidate-only. Honors REDUCED_STATE_POLICY via file reference, not duplication.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.carrier_settings.v0_1_candidate"
SETTINGS_RELATIVE = Path(
    "ION/05_context/current/carrier_settings/CARRIER_SETTINGS.candidate.json"
)
RECEIPTS_RELATIVE = Path(
    "ION/05_context/current/carrier_settings/receipts"
)
REDUCED_STATE_POLICY_REF = (
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.model_routing_and_reasoning_economics/REDUCED_STATE_POLICY.candidate.yaml"
)
FINDINGS_RELATIVE = Path(
    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
    "domain.cli_carrier_selection_and_usage_fallback"
)
FINDING_STALE_COUNTERS = "FINDING_CARRIER_SETTINGS_STALE_USAGE_COUNTERS.candidate.json"
FINDING_UNREADABLE = "FINDING_CARRIER_SETTINGS_UNREADABLE.candidate.json"

KNOWN_CARRIERS = ("cursor_cli", "claude_cli", "codex_cli")
OPERATION_MODES = frozenset({"full", "reduced", "premium_only"})
DAILY_RUN_LIMIT_MIN = 0
DAILY_RUN_LIMIT_MAX = 10_000
COUNTER_STALE_HOURS = 24
WRITABLE_FIELDS = frozenset({"enabled", "daily_run_limit", "operation_mode", "notes"})

RUNS_ROOTS: dict[str, tuple[str, Path]] = {
    "cursor_cli": (
        "prompt_spawn_",
        Path("ION/05_context/current/cursor_connector/prompt_spawn_runs"),
    ),
    "claude_cli": (
        "claude_prompt_spawn_",
        Path("ION/05_context/current/claude_connector/claude_prompt_spawn_runs"),
    ),
    "codex_cli": (
        "codex_prompt_spawn_",
        Path("ION/05_context/current/codex_connector/codex_prompt_spawn_runs"),
    ),
}

_RUN_DIR_DATE_RE = re.compile(
    r"^(?:prompt_spawn|claude_prompt_spawn|codex_prompt_spawn)_"
    r"(\d{4}-\d{2}-\d{2})T"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    current = dt or _utc_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION/REPO_AUTHORITY.md").is_file():
            return path
    return candidate


def _settings_path(shell_root: Path) -> Path:
    return shell_root / SETTINGS_RELATIVE


def _default_carrier_row() -> dict[str, Any]:
    return {
        "enabled": True,
        "daily_run_limit": 500,
        "operation_mode": "full",
        "notes": "",
    }


def default_settings_payload() -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "updated_at": _iso(),
        "reduced_state_policy_ref": REDUCED_STATE_POLICY_REF,
        "usage_counters_refreshed_at": None,
        "carriers": {carrier_id: _default_carrier_row() for carrier_id in KNOWN_CARRIERS},
        "usage_today": {carrier_id: 0 for carrier_id in KNOWN_CARRIERS},
    }


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    body = json.dumps(dict(payload), indent=2, sort_keys=True) + "\n"
    tmp.write_text(body, encoding="utf-8")
    os.replace(tmp, path)


def _parse_run_dir_utc_date(dirname: str) -> str | None:
    match = _RUN_DIR_DATE_RE.match(dirname)
    if not match:
        return None
    return match.group(1)


def count_runs_today(shell_root: Path, carrier_id: str, *, now: datetime | None = None) -> int:
    """Count prompt-spawn run directories for carrier whose UTC date is today."""

    carrier = str(carrier_id or "").strip()
    spec = RUNS_ROOTS.get(carrier)
    if not spec:
        return 0
    _prefix, rel = spec
    runs_root = shell_root / rel
    if not runs_root.is_dir():
        return 0
    today = (now or _utc_now()).astimezone(timezone.utc).date().isoformat()
    count = 0
    for entry in runs_root.iterdir():
        if not entry.is_dir():
            continue
        run_date = _parse_run_dir_utc_date(entry.name)
        if run_date == today:
            count += 1
    return count


def refresh_usage_counters(payload: dict[str, Any], shell_root: Path) -> dict[str, Any]:
    refreshed = dict(payload)
    usage: dict[str, int] = {}
    for carrier_id in KNOWN_CARRIERS:
        usage[carrier_id] = count_runs_today(shell_root, carrier_id)
    refreshed["usage_today"] = usage
    refreshed["usage_counters_refreshed_at"] = _iso()
    return refreshed


def _load_raw_settings(shell_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    path = _settings_path(shell_root)
    if not path.is_file():
        return None, "settings_file_missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"settings_unreadable:{exc.__class__.__name__}"
    if not isinstance(loaded, dict):
        return None, "settings_invalid_shape"
    return loaded, None


def read_settings(shell_root: str | Path | None = None, *, create_default: bool = True) -> dict[str, Any]:
    """Load settings and refresh usage_today counters (does not persist refresh)."""

    root = _resolve_root(shell_root)
    loaded, err = _load_raw_settings(root)
    if loaded is None:
        if not create_default:
            raise FileNotFoundError(err or "settings_missing")
        loaded = default_settings_payload()
    carriers = loaded.get("carriers")
    if not isinstance(carriers, dict):
        loaded["carriers"] = {cid: _default_carrier_row() for cid in KNOWN_CARRIERS}
    else:
        for cid in KNOWN_CARRIERS:
            row = carriers.get(cid)
            if not isinstance(row, dict):
                carriers[cid] = _default_carrier_row()
    loaded.setdefault("schema_id", SCHEMA_ID)
    loaded.setdefault("reduced_state_policy_ref", REDUCED_STATE_POLICY_REF)
    return refresh_usage_counters(loaded, root)


def _validate_field(field: str, value: Any) -> Any:
    key = str(field or "").strip()
    if key not in WRITABLE_FIELDS:
        raise ValueError(f"field_not_writable:{key}")
    if key == "enabled":
        if not isinstance(value, bool):
            raise ValueError("enabled_must_be_bool")
        return value
    if key == "daily_run_limit":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("daily_run_limit_must_be_int")
        if value < DAILY_RUN_LIMIT_MIN or value > DAILY_RUN_LIMIT_MAX:
            raise ValueError("daily_run_limit_out_of_bounds")
        return value
    if key == "operation_mode":
        mode = str(value or "").strip()
        if mode not in OPERATION_MODES:
            raise ValueError("operation_mode_invalid")
        return mode
    if key == "notes":
        text = str(value if value is not None else "")
        if len(text) > 2000:
            raise ValueError("notes_too_long")
        return text
    raise ValueError(f"unknown_field:{key}")


def write_setting(
    shell_root: str | Path | None,
    *,
    carrier_id: str,
    field: str,
    value: Any,
    write_receipt: bool = True,
) -> dict[str, Any]:
    """Atomically update one carrier field and emit a write receipt."""

    root = _resolve_root(shell_root)
    carrier = str(carrier_id or "").strip()
    if carrier not in KNOWN_CARRIERS:
        raise ValueError("unknown_carrier_id")
    validated = _validate_field(field, value)
    current = read_settings(root, create_default=True)
    carriers = dict(current.get("carriers") or {})
    row = dict(carriers.get(carrier) or _default_carrier_row())
    row[str(field)] = validated
    carriers[carrier] = row
    next_payload = dict(current)
    next_payload["carriers"] = carriers
    next_payload["updated_at"] = _iso()
    next_payload = refresh_usage_counters(next_payload, root)
    settings_path = _settings_path(root)
    before_sha = (
        hashlib.sha256(settings_path.read_bytes()).hexdigest()
        if settings_path.is_file()
        else None
    )
    _atomic_write_json(settings_path, next_payload)
    after_sha = hashlib.sha256(settings_path.read_bytes()).hexdigest()
    receipt: dict[str, Any] | None = None
    if write_receipt:
        receipt_dir = root / RECEIPTS_RELATIVE
        receipt_dir.mkdir(parents=True, exist_ok=True)
        receipt_id = f"carrier_settings_write_{after_sha[:16]}"
        receipt = {
            "schema_id": "ion.carrier_settings.write_receipt.v0_1_candidate",
            "receipt_id": receipt_id,
            "written_at": _iso(),
            "carrier_id": carrier,
            "field": str(field),
            "value": validated,
            "settings_path": SETTINGS_RELATIVE.as_posix(),
            "before_sha256": before_sha,
            "after_sha256": after_sha,
            "production_authority": False,
        }
        receipt_path = receipt_dir / f"{receipt_id}.candidate.json"
        _atomic_write_json(receipt_path, receipt)
    return {
        "ok": True,
        "settings_path": SETTINGS_RELATIVE.as_posix(),
        "carrier_id": carrier,
        "field": str(field),
        "value": validated,
        "after_sha256": after_sha,
        "receipt_path": (
            (RECEIPTS_RELATIVE / f"carrier_settings_write_{after_sha[:16]}.candidate.json").as_posix()
            if write_receipt
            else None
        ),
        "receipt": receipt,
    }


def carrier_settings_gate(
    shell_root: Path,
    carrier_id: str,
    *,
    settings: Mapping[str, Any] | None = None,
) -> tuple[bool, str | None]:
    """Return (blocked, routed_finding_code). blocked=True means skip carrier at selection."""

    carrier = str(carrier_id or "").strip()
    if carrier not in KNOWN_CARRIERS:
        return False, None
    payload = settings if settings is not None else read_settings(shell_root)
    carriers = payload.get("carriers") if isinstance(payload.get("carriers"), Mapping) else {}
    row = carriers.get(carrier) if isinstance(carriers, Mapping) else None
    if not isinstance(row, Mapping):
        return False, None
    if not bool(row.get("enabled", True)):
        return True, "carrier_settings_disabled"
    usage = payload.get("usage_today") if isinstance(payload.get("usage_today"), Mapping) else {}
    runs = int(usage.get(carrier) or 0)
    try:
        limit = int(row.get("daily_run_limit", DAILY_RUN_LIMIT_MAX))
    except (TypeError, ValueError):
        limit = DAILY_RUN_LIMIT_MAX
    if limit >= 0 and runs >= limit:
        return True, "carrier_settings_daily_limit_reached"
    return False, None


def selection_pause_finding(
    shell_root: Path,
    *,
    settings: Mapping[str, Any] | None = None,
) -> str | None:
    """When every executable carrier is blocked by operator settings, return pause finding."""

    payload = settings if settings is not None else read_settings(shell_root)
    carriers = payload.get("carriers") if isinstance(payload.get("carriers"), Mapping) else {}
    usage = payload.get("usage_today") if isinstance(payload.get("usage_today"), Mapping) else {}
    any_enabled = False
    any_under_limit = False
    for carrier_id in KNOWN_CARRIERS:
        row = carriers.get(carrier_id) if isinstance(carriers, Mapping) else None
        if not isinstance(row, Mapping):
            continue
        if not bool(row.get("enabled", True)):
            continue
        any_enabled = True
        try:
            limit = int(row.get("daily_run_limit", DAILY_RUN_LIMIT_MAX))
        except (TypeError, ValueError):
            limit = DAILY_RUN_LIMIT_MAX
        runs = int(usage.get(carrier_id) or 0)
        if runs < limit:
            any_under_limit = True
    if not any_enabled:
        return "all_carriers_disabled_by_operator_settings"
    if not any_under_limit:
        return "all_carriers_daily_limit_reached_by_operator_settings"
    return None


def _counters_stale(payload: Mapping[str, Any], *, now: datetime | None = None) -> bool:
    refreshed = str(payload.get("usage_counters_refreshed_at") or "").strip()
    if not refreshed:
        return True
    try:
        parsed = datetime.fromisoformat(refreshed.replace("Z", "+00:00"))
    except ValueError:
        return True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    age = (now or _utc_now()) - parsed.astimezone(timezone.utc)
    return age > timedelta(hours=COUNTER_STALE_HOURS)


def emit_absence_finding(
    shell_root: Path,
    *,
    kind: str,
    detail: str,
    write: bool = True,
) -> dict[str, Any]:
    finding = {
        "schema_id": "ion.carrier_settings.absence_finding.v0_1_candidate",
        "finding_kind": kind,
        "detail": detail,
        "observed_at": _iso(),
        "settings_path": SETTINGS_RELATIVE.as_posix(),
        "route_to": FINDINGS_RELATIVE.as_posix(),
        "owner_domain_id": "domain.cli_carrier_selection_and_usage_fallback",
    }
    filename = FINDING_STALE_COUNTERS if kind == "stale_usage_counters" else FINDING_UNREADABLE
    out_path = shell_root / FINDINGS_RELATIVE / filename
    if write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(out_path, finding)
    return {"finding": finding, "finding_path": out_path.as_posix() if write else None}


def probe_carrier_settings_absence(shell_root: Path, *, write: bool = True) -> dict[str, Any]:
    """Absence detector: unreadable settings or stale usage counter refresh."""

    loaded, err = _load_raw_settings(shell_root)
    check: dict[str, Any] = {
        "check_id": "carrier_settings_surface",
        "status": "clear",
        "findings": [],
    }
    if loaded is None:
        check["status"] = "finding"
        emitted = emit_absence_finding(
            shell_root,
            kind="settings_unreadable",
            detail=str(err or "settings_unreadable"),
            write=write,
        )
        check["findings"].append(emitted["finding"])
        return check
    if _counters_stale(loaded):
        check["status"] = "finding"
        emitted = emit_absence_finding(
            shell_root,
            kind="stale_usage_counters",
            detail="usage_counters_refreshed_at older than 24h or missing",
            write=write,
        )
        check["findings"].append(emitted["finding"])
    return check


def ensure_default_settings_file(shell_root: Path) -> Path | None:
    path = _settings_path(shell_root)
    if path.is_file():
        return None
    payload = default_settings_payload()
    payload = refresh_usage_counters(payload, shell_root)
    _atomic_write_json(path, payload)
    return path


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ION carrier settings (candidate)")
    parser.add_argument("--ion-root", default=".", help="Shell root")
    sub = parser.add_subparsers(dest="command", required=True)

    read_p = sub.add_parser("read", help="Print settings with refreshed usage counters")
    read_p.add_argument("--json", action="store_true")

    write_p = sub.add_parser("write", help="Update one carrier field")
    write_p.add_argument("--carrier-id", required=True)
    write_p.add_argument("--field", required=True)
    write_p.add_argument("--value", required=True)
    write_p.add_argument("--json", action="store_true")

    probe_p = sub.add_parser("probe-absence", help="Emit absence findings when stale/unreadable")
    probe_p.add_argument("--write", action="store_true")
    probe_p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    root = _resolve_root(args.ion_root)
    if args.command == "read":
        payload = read_settings(root)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(json.dumps(payload.get("carriers"), indent=2))
        return 0
    if args.command == "write":
        raw = args.value
        if args.field == "enabled":
            parsed: Any = raw.lower() in {"1", "true", "yes", "on"}
        elif args.field == "daily_run_limit":
            parsed = int(raw)
        else:
            parsed = raw
        result = write_setting(
            root,
            carrier_id=args.carrier_id,
            field=args.field,
            value=parsed,
        )
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "probe-absence":
        result = probe_carrier_settings_absence(root, write=bool(args.write))
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
