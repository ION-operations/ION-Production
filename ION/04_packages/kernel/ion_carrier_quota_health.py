"""Carrier quota exhaustion health surface (domain.carrier_quota_and_config_health).

Candidate-only runtime records persist whole-CLI quota exhaustion across fresh
admissions so ion_cli_model_selection can skip exhausted carriers until reset
time passes or an explicit clear/probe removes the record.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

SCHEMA_ID = "ion.carrier_exhaustion_health.v0_1_candidate"
SIGNAL_WHOLE_CLI_QUOTA_EXHAUSTION = "whole_cli_quota_exhaustion"
SIGNAL_TIER_AVAILABILITY = "tier_availability_blackout"
CARRIER_EXHAUSTION_HEALTH_RELATIVE_PATH = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.carrier_quota_and_config_health/runtime/CARRIER_EXHAUSTION_HEALTH.candidate.json"
)
ROUTING_RELATIVE_PATH = Path(
    "ION/05_context/current/domain_weaver/DOMAIN_LEADER_CARRIER_ROUTING.candidate.yaml"
)

_RESET_HINT_RE = re.compile(r"resets?\s+([^·\n\r]+)", re.IGNORECASE)
_TZ_SUFFIX_RE = re.compile(r"\(([^)]+)\)\s*$")


def _health_path(shell_root: Path) -> Path:
    return shell_root / CARRIER_EXHAUSTION_HEALTH_RELATIVE_PATH


def _utc_now_iso(*, now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat()


def parse_reset_hint(output_text: str | None) -> str | None:
    """Extract provider reset hint text when present."""

    text = str(output_text or "")
    match = _RESET_HINT_RE.search(text)
    if not match:
        return None
    return match.group(1).strip().rstrip(".")


def _normalize_time_token(token: str) -> str:
    normalized = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", token.strip(), flags=re.IGNORECASE)
    normalized = re.sub(r"(\d{1,2})(am|pm)", r"\1 \2", normalized, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", normalized).strip()


def parse_reset_at_iso(
    output_text: str | None,
    *,
    now: datetime | None = None,
) -> str | None:
    """Parse reset datetime from provider quota text when possible."""

    reset_hint = parse_reset_hint(output_text)
    if not reset_hint:
        return None
    tz_name = None
    tz_match = _TZ_SUFFIX_RE.search(reset_hint)
    if tz_match:
        tz_name = tz_match.group(1).strip()
    hint_no_tz = _TZ_SUFFIX_RE.sub("", reset_hint).strip().rstrip(",")
    token = _normalize_time_token(hint_no_tz)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    tzinfo = timezone.utc
    if tz_name:
        try:
            tzinfo = ZoneInfo(tz_name)
        except Exception:
            tzinfo = current.astimezone().tzinfo or timezone.utc
    year = current.astimezone(tzinfo).year
    parsed: datetime | None = None
    for fmt in ("%b %d, %Y %I %p", "%B %d, %Y %I %p", "%b %d, %Y %I:%M %p", "%B %d, %Y %I:%M %p"):
        try:
            parsed = datetime.strptime(f"{token}, {year}", fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        for fmt in ("%b %d, %I %p", "%B %d, %I %p"):
            try:
                parsed = datetime.strptime(token, fmt)
                break
            except ValueError:
                continue
    if parsed is None:
        return None
    parsed = parsed.replace(tzinfo=tzinfo)
    if parsed <= current.astimezone(tzinfo):
        try:
            parsed = parsed.replace(year=year + 1)
        except ValueError:
            parsed = parsed.replace(year=year + 1, day=28)
    return parsed.astimezone(timezone.utc).isoformat()


def _parse_iso_datetime(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _load_routing(shell_root: Path) -> dict[str, Any]:
    path = shell_root / ROUTING_RELATIVE_PATH
    if not path.is_file() or yaml is None:
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _availability_window_by_id(
    shell_root: Path,
    window_id: str | None,
) -> dict[str, Any] | None:
    window_key = str(window_id or "").strip()
    if not window_key:
        return None
    routing = _load_routing(shell_root)
    windows = routing.get("availability_windows")
    if not isinstance(windows, list):
        return None
    for window in windows:
        if not isinstance(window, Mapping):
            continue
        if str(window.get("window_id") or "").strip() == window_key:
            return dict(window)
    return None


def _window_expires_at_iso(shell_root: Path, window_id: str | None) -> str | None:
    window = _availability_window_by_id(shell_root, window_id)
    if window is None:
        return None
    expires = _parse_iso_datetime(str(window.get("expires_at") or ""))
    if expires is None:
        return None
    return expires.astimezone(timezone.utc).isoformat()


def _effective_expiry_iso(record: Mapping[str, Any], shell_root: Path) -> str | None:
    """Parity: earliest of reset_at_iso and linked availability_window expires_at."""

    candidates: list[datetime] = []
    for key in ("reset_at_iso", "expires_at_iso"):
        parsed = _parse_iso_datetime(str(record.get(key) or ""))
        if parsed is not None:
            candidates.append(parsed.astimezone(timezone.utc))
    window_expires = _window_expires_at_iso(
        shell_root,
        str(record.get("availability_window_id") or "").strip() or None,
    )
    parsed_window = _parse_iso_datetime(window_expires)
    if parsed_window is not None:
        candidates.append(parsed_window.astimezone(timezone.utc))
    if not candidates:
        return None
    return min(candidates).isoformat()


def load_carrier_exhaustion_health(shell_root: Path) -> dict[str, Any]:
    path = _health_path(shell_root)
    if not path.is_file():
        return {"schema_id": SCHEMA_ID, "records": {}, "tier_availability": {}}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {"schema_id": SCHEMA_ID, "records": {}, "tier_availability": {}}
    if not isinstance(loaded, dict):
        return {"schema_id": SCHEMA_ID, "records": {}, "tier_availability": {}}
    records = loaded.get("records")
    if not isinstance(records, dict):
        loaded["records"] = {}
    tier_availability = loaded.get("tier_availability")
    if not isinstance(tier_availability, dict):
        loaded["tier_availability"] = {}
    loaded.setdefault("schema_id", SCHEMA_ID)
    return loaded


def _write_health(shell_root: Path, payload: Mapping[str, Any]) -> Path:
    path = _health_path(shell_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(payload)
    body["schema_id"] = SCHEMA_ID
    body["updated_at"] = _utc_now_iso()
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def record_carrier_exhaustion(
    shell_root: Path,
    *,
    carrier_id: str,
    signal_class: str,
    observed_at: str | None = None,
    reset_hint: str | None = None,
    reset_at_iso: str | None = None,
    evidence_run_id: str | None = None,
    output_text: str | None = None,
    availability_window_id: str | None = None,
) -> dict[str, Any]:
    """Persist or update one carrier exhaustion record."""

    carrier = str(carrier_id or "").strip()
    if not carrier:
        raise ValueError("carrier_id_required")
    hint = reset_hint if reset_hint is not None else parse_reset_hint(output_text)
    reset_iso = reset_at_iso if reset_at_iso is not None else parse_reset_at_iso(output_text)
    window_id = str(availability_window_id or "").strip() or None
    window_expires = _window_expires_at_iso(shell_root, window_id)
    health = load_carrier_exhaustion_health(shell_root)
    records = dict(health.get("records") or {})
    record = {
        "carrier_id": carrier,
        "signal_class": str(signal_class or SIGNAL_WHOLE_CLI_QUOTA_EXHAUSTION),
        "observed_at": observed_at or _utc_now_iso(),
        "reset_hint": hint,
        "reset_at_iso": reset_iso,
        "expires_at_iso": window_expires,
        "availability_window_id": window_id,
        "evidence_run_id": str(evidence_run_id or "").strip() or None,
        "exhausted_carriers": [carrier],
    }
    records[carrier] = record
    health["records"] = records
    _write_health(shell_root, health)
    return record


def record_whole_cli_quota_exhaustion(
    shell_root: Path,
    *,
    carrier_id: str,
    output_text: str | None = None,
    evidence_run_id: str | None = None,
) -> dict[str, Any]:
    """Record whole-CLI quota exhaustion aligned with exhausted_carriers stamps."""

    return record_carrier_exhaustion(
        shell_root,
        carrier_id=carrier_id,
        signal_class=SIGNAL_WHOLE_CLI_QUOTA_EXHAUSTION,
        output_text=output_text,
        evidence_run_id=evidence_run_id,
    )


def record_tier_availability(
    shell_root: Path,
    *,
    carrier_id: str,
    blocked_model_patterns: list[str],
    availability_window_id: str,
    reset_hint: str | None = None,
    observed_at: str | None = None,
    evidence_run_id: str | None = None,
) -> dict[str, Any]:
    """Persist tier-level model unavailability aligned with routing availability windows."""

    carrier = str(carrier_id or "").strip()
    window_id = str(availability_window_id or "").strip()
    if not carrier:
        raise ValueError("carrier_id_required")
    if not window_id:
        raise ValueError("availability_window_id_required")
    patterns = [str(pattern).strip() for pattern in blocked_model_patterns if str(pattern).strip()]
    if not patterns:
        raise ValueError("blocked_model_patterns_required")
    window_expires = _window_expires_at_iso(shell_root, window_id)
    health = load_carrier_exhaustion_health(shell_root)
    tier_availability = dict(health.get("tier_availability") or {})
    record = {
        "carrier_id": carrier,
        "signal_class": SIGNAL_TIER_AVAILABILITY,
        "observed_at": observed_at or _utc_now_iso(),
        "blocked_model_patterns": patterns,
        "availability_window_id": window_id,
        "expires_at_iso": window_expires,
        "reset_hint": reset_hint,
        "evidence_run_id": str(evidence_run_id or "").strip() or None,
    }
    tier_availability[carrier] = record
    health["tier_availability"] = tier_availability
    _write_health(shell_root, health)
    return record


def clear_carrier_exhaustion(shell_root: Path, carrier_id: str) -> bool:
    """Remove one carrier record after live probe or operator clear."""

    carrier = str(carrier_id or "").strip()
    health = load_carrier_exhaustion_health(shell_root)
    records = dict(health.get("records") or {})
    if carrier not in records:
        return False
    del records[carrier]
    health["records"] = records
    _write_health(shell_root, health)
    return True


def clear_tier_availability(shell_root: Path, carrier_id: str) -> bool:
    """Remove one tier availability record after window expiry or operator clear."""

    carrier = str(carrier_id or "").strip()
    health = load_carrier_exhaustion_health(shell_root)
    tier_availability = dict(health.get("tier_availability") or {})
    if carrier not in tier_availability:
        return False
    del tier_availability[carrier]
    health["tier_availability"] = tier_availability
    _write_health(shell_root, health)
    return True


def _reset_has_passed(reset_at_iso: str | None, *, now: datetime | None = None) -> bool:
    if not reset_at_iso:
        return False
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    try:
        reset_at = datetime.fromisoformat(str(reset_at_iso))
    except ValueError:
        return False
    if reset_at.tzinfo is None:
        reset_at = reset_at.replace(tzinfo=timezone.utc)
    return current >= reset_at.astimezone(timezone.utc)


def _expiry_has_passed(
    record: Mapping[str, Any],
    shell_root: Path,
    *,
    now: datetime | None = None,
) -> bool:
    effective = _effective_expiry_iso(record, shell_root)
    return _reset_has_passed(effective, now=now)


def is_carrier_quota_exhausted(
    shell_root: Path,
    carrier_id: str,
    *,
    now: datetime | None = None,
) -> tuple[bool, str]:
    """Return whether admission should treat carrier as unavailable."""

    carrier = str(carrier_id or "").strip()
    if not carrier:
        return False, ""
    health = load_carrier_exhaustion_health(shell_root)
    records = health.get("records")
    if not isinstance(records, Mapping):
        return False, ""
    record = records.get(carrier)
    if not isinstance(record, Mapping):
        return False, ""
    if _expiry_has_passed(record, shell_root, now=now):
        clear_carrier_exhaustion(shell_root, carrier)
        return False, "quota_reset_elapsed"
    signal_class = str(record.get("signal_class") or SIGNAL_WHOLE_CLI_QUOTA_EXHAUSTION)
    return True, f"carrier_quota_exhausted:{signal_class}"


def is_tier_model_unavailable(
    shell_root: Path,
    carrier_id: str,
    model: str,
    *,
    now: datetime | None = None,
) -> tuple[bool, str]:
    """Return whether a model tier is blocked by persisted tier_availability records."""

    carrier = str(carrier_id or "").strip()
    model_str = str(model or "").strip()
    if not carrier or not model_str:
        return False, ""
    health = load_carrier_exhaustion_health(shell_root)
    tier_availability = health.get("tier_availability")
    if not isinstance(tier_availability, Mapping):
        return False, ""
    record = tier_availability.get(carrier)
    if not isinstance(record, Mapping):
        return False, ""
    if _expiry_has_passed(record, shell_root, now=now):
        clear_tier_availability(shell_root, carrier)
        return False, "tier_availability_expired"
    patterns = record.get("blocked_model_patterns")
    if not isinstance(patterns, list):
        return False, ""
    for pattern in patterns:
        pattern_str = str(pattern).strip()
        if pattern_str and fnmatch(model_str, pattern_str):
            return True, f"tier_unavailable:{pattern_str}"
    return False, ""


def list_exhausted_carriers(
    shell_root: Path,
    *,
    now: datetime | None = None,
) -> list[str]:
    """Return carrier ids currently blocked by persisted exhaustion records."""

    health = load_carrier_exhaustion_health(shell_root)
    records = health.get("records")
    if not isinstance(records, Mapping):
        return []
    blocked: list[str] = []
    for carrier_id in records:
        exhausted, _detail = is_carrier_quota_exhausted(shell_root, str(carrier_id), now=now)
        if exhausted:
            blocked.append(str(carrier_id))
    return sorted(blocked)
