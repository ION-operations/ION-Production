"""Unified CLI/model selection with availability-aware fallback chains.

Consolidates domain leader routing, carrier gateway preference, and model
downgrade ladders into one selection surface. Candidate-only.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Mapping

from . import ion_carrier_quota_health as carrier_quota_health
from . import ion_cli_carrier_settings as carrier_settings
from .ion_cli_carrier_gateway import normalize_usage_limit_signal

SCHEMA_ID = "ion.cli_model_selection.v1"
ROUTING_RELATIVE_PATH = Path(
    "ION/05_context/current/domain_weaver/DOMAIN_LEADER_CARRIER_ROUTING.candidate.yaml"
)
ROUTING_JSON_RELATIVE_PATH = Path(
    "ION/05_context/current/domain_weaver/DOMAIN_LEADER_CARRIER_ROUTING.candidate.json"
)

DEFAULT_LEADER_DOMAINS = frozenset(
    {
        "domain.runtime_carrier_and_action_admission",
        "domain.model_routing_and_reasoning_economics",
        "domain.domain_weaver_living_self_model",
        "domain.swarm_scale_scheduling_and_workload_economics",
        "domain.context_systems",
        "domain.durable_apply_and_substrate_custody",
        "domain.state_rank_and_receipt_truth",
        "domain.artifact_provenance_and_gate_legitimacy",
        "domain.agent_communication_and_settlement",
        "domain.honest_agency_validation",
    }
)

DEFAULT_CARRIER_FALLBACK_ORDER = (
    "claude_cli",
    "cursor_cli",
    "codex_cli",
)

DEFAULT_MODEL_LADDERS: dict[str, tuple[str, ...]] = {
    "claude_cli": ("claude-opus-4-8", "claude-sonnet-5"),
    "cursor_cli": ("composer-2.5-fast", "composer-2.5"),
    "codex_cli": ("gpt-5.6-sol",),
    "codex_app_server": ("gpt-5.6-sol",),
}

# Leader-tier equivalents on cursor_cli: cross-carrier fallbacks for model tiers
# before composer quality downgrade.  Not experimental; eligible for tier fallback.
LEADER_TIER_CURSOR_MODELS: tuple[str, ...] = (
    "claude-opus-4-8-thinking-high",
    "claude-sonnet-5-thinking-high",
    "gpt-5.6-sol-high",
)

# These exact Cursor slugs are available only when the caller explicitly names
# both the model and a bounded work class.  They are deliberately absent from
# DEFAULT_MODEL_LADDERS so they can never become defaults or fallback targets.
EXPERIMENTAL_EXACT_MODELS: dict[str, tuple[str, ...]] = {
    "cursor_cli": (
        "gemini-3.1-pro",
        "cursor-grok-4.5-high",
    ),
}

# Canonical cross-carrier model equivalence map (source model -> carrier -> equivalent).
CROSS_CARRIER_MODEL_EQUIVALENTS: dict[str, dict[str, str]] = {
    "claude-opus-4-8": {"cursor_cli": "claude-opus-4-8-thinking-high"},
    "claude-sonnet-5": {"cursor_cli": "claude-sonnet-5-thinking-high"},
    "gpt-5.6-sol": {"cursor_cli": "gpt-5.6-sol-high"},
}

# Cursor labels Fable 5 as NO ZDR.  Keep the observed slug explicit so a later
# edit cannot accidentally treat it as an ordinary experiment.  A separate,
# privacy-scoped public/synthetic-data lane is required before invocation.
PRIVACY_RESTRICTED_MODELS = frozenset({"claude-fable-5-thinking-high"})

OPERATOR_APPROVED_MODELS = {
    carrier_id: frozenset(models) for carrier_id, models in DEFAULT_MODEL_LADDERS.items()
}

EXECUTION_APPROVED_MODELS = {
    carrier_id: frozenset(
        {
            *OPERATOR_APPROVED_MODELS.get(carrier_id, frozenset()),
            *EXPERIMENTAL_EXACT_MODELS.get(carrier_id, ()),
            *(
                LEADER_TIER_CURSOR_MODELS
                if carrier_id == "cursor_cli"
                else ()
            ),
        }
    )
    for carrier_id in {
        *OPERATOR_APPROVED_MODELS,
        *EXPERIMENTAL_EXACT_MODELS,
        "cursor_cli",
    }
}

CARRIER_PROBE: dict[str, tuple[str, ...]] = {
    "codex_cli": ("codex", "--version"),
    "cursor_cli": ("cursor-agent", "--version"),
    "claude_cli": ("claude", "--version"),
}

USAGE_LIMIT_SIGNALS = frozenset(
    {
        "usage_limit",
        "rate_limit",
        "quota_exceeded",
        "transient_usage_limit",
        "unavailable",
        "login_required",
        "auth_required",
        "carrier_not_ready",
    }
)

PROMPT_SPAWN_EXECUTABLE_CARRIERS = frozenset(
    {"cursor_cli", "claude_cli", "codex_cli"}
)

MATERIAL_EXECUTION_SURFACES = frozenset({"prompt_spawn", "codex_queue"})

KNOWN_EXECUTION_CARRIERS = frozenset(
    {"cursor_cli", "claude_cli", "codex_cli", "codex_app_server"}
)

UNCLASSIFIED_WORK_CLASSES = frozenset(
    {"", "auto", "none", "unknown", "unclassified", "unspecified"}
)


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError:
        return {}
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


WORK_CLASS_CARRIER_DEFAULT_MAP_REL = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.model_routing_and_reasoning_economics/runtime/"
    "WORK_CLASS_CARRIER_DEFAULT_MAP.candidate.yaml"
)
UNATTENDED_BULK_DEFAULT_CARRIER = "cursor_cli"
UNATTENDED_BULK_DEFAULT_MODEL = "composer-2.5"
UNATTENDED_PREMIUM_SPAWN_REFUSAL_FINDING = "unattended_premium_model_spawn_refused"
ABSENCE_SIGNAL_UNATTENDED_PREMIUM_SOS_SPAWN = "UNATTENDED_PREMIUM_SOS_SPAWN_WITHOUT_EXPLICIT_INTENT"
CURSOR_HOSTED_CLAUDE_REFUSAL_FINDING_PREFIX = "cursor_hosted_claude_model_refused"
SPAWN_MODEL_OUTSIDE_SOVEREIGN_ALLOWLIST_FINDING = "spawn_model_outside_sovereign_allowlist"
ABSENCE_SIGNAL_SPAWN_MODEL_OUTSIDE_SOVEREIGN_ALLOWLIST = (
    "SPAWN_MODEL_OUTSIDE_SOVEREIGN_ALLOWLIST"
)
DEFAULT_SOVEREIGN_APPROVED_SPAWN_MODELS = frozenset(
    {"composer-2.5", "composer-2.5-fast", "claude-sonnet-5", "claude-fable-5"}
)
DEFAULT_SOVEREIGN_BANNED_SPAWN_MODELS = frozenset({"claude-opus-5"})
SOVEREIGN_BANNED_SPAWN_MODEL_FINDING = "sovereign_banned_spawn_model"
DEFAULT_CURSOR_HOSTED_CLAUDE_MODELS = frozenset(
    {
        "claude-opus-4-8-thinking-high",
        "claude-sonnet-5-thinking-high",
        "claude-haiku-5-thinking-high",
    }
)


def load_work_class_carrier_default_map(shell_root: Path) -> dict[str, Any]:
    path = shell_root / WORK_CLASS_CARRIER_DEFAULT_MAP_REL
    data = _read_yaml(path)
    if data:
        data = dict(data)
        data["_map_path"] = WORK_CLASS_CARRIER_DEFAULT_MAP_REL.as_posix()
        data["_map_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return data


def judgment_work_classes_from_map(shell_root: Path) -> frozenset[str]:
    map_data = load_work_class_carrier_default_map(shell_root)
    block = map_data.get("judgment_work_classes")
    if isinstance(block, Mapping):
        raw = block.get("work_classes") or []
        return frozenset(str(item).strip() for item in raw if str(item).strip())
    return frozenset()


def sovereign_approved_spawn_models(shell_root: Path) -> frozenset[str]:
    map_data = load_work_class_carrier_default_map(shell_root)
    raw = map_data.get("sovereign_approved_spawn_models") or []
    models = {str(item).strip() for item in raw if str(item).strip()}
    approved = frozenset(models) if models else DEFAULT_SOVEREIGN_APPROVED_SPAWN_MODELS
    return frozenset(m for m in approved if m not in sovereign_banned_spawn_models(shell_root))


def sovereign_banned_spawn_models(shell_root: Path) -> frozenset[str]:
    map_data = load_work_class_carrier_default_map(shell_root)
    raw = map_data.get("sovereign_permanently_banned_spawn_models") or []
    models = {str(item).strip() for item in raw if str(item).strip()}
    return frozenset(models) if models else DEFAULT_SOVEREIGN_BANNED_SPAWN_MODELS


def refusal_for_sovereign_banned_spawn_model(
    model_id: str,
    *,
    shell_root: Path | None = None,
    domain_id: str = "",
    row_id: Any = None,
    index: Any = None,
    work_class: str | None = None,
) -> dict[str, Any] | None:
    model = str(model_id or "").strip()
    banned = (
        sovereign_banned_spawn_models(shell_root)
        if shell_root is not None
        else DEFAULT_SOVEREIGN_BANNED_SPAWN_MODELS
    )
    if model not in banned:
        return None
    return {
        "ok": False,
        "domain_id": domain_id,
        "index": index,
        "row_id": row_id,
        "finding": f"{SOVEREIGN_BANNED_SPAWN_MODEL_FINDING}:{model}",
        "resolved_model": model,
        "work_class": work_class,
        "detects_absence": True,
        "hard_refuse": True,
    }


def cursor_hosted_claude_models(shell_root: Path) -> frozenset[str]:
    map_data = load_work_class_carrier_default_map(shell_root)
    block = map_data.get("cursor_hosted_claude_refusal")
    if isinstance(block, Mapping):
        raw = block.get("models") or []
        models = {str(item).strip() for item in raw if str(item).strip()}
        if models:
            return frozenset(models)
    return DEFAULT_CURSOR_HOSTED_CLAUDE_MODELS


def is_cursor_hosted_claude_model(
    shell_root: Path,
    carrier_id: str,
    model_id: str,
) -> bool:
    carrier = str(carrier_id or "").strip()
    model = str(model_id or "").strip()
    if carrier != "cursor_cli" or not model:
        return False
    if model in cursor_hosted_claude_models(shell_root):
        return True
    lowered = model.lower()
    return lowered.startswith("claude-") and "-thinking-high" in lowered


def refusal_for_cursor_hosted_claude_model(
    shell_root: Path,
    *,
    carrier_id: str,
    model_id: str,
    domain_id: str = "",
    row_id: Any = None,
    index: Any = None,
    work_class: str | None = None,
) -> dict[str, Any] | None:
    model = str(model_id or "").strip()
    if not is_cursor_hosted_claude_model(shell_root, carrier_id, model):
        return None
    return {
        "ok": False,
        "domain_id": domain_id,
        "index": index,
        "row_id": row_id,
        "finding": f"{CURSOR_HOSTED_CLAUDE_REFUSAL_FINDING_PREFIX}:{model}",
        "resolved_model": model,
        "resolved_carrier": str(carrier_id or "").strip() or "cursor_cli",
        "work_class": work_class,
        "detects_absence": True,
        "hard_refuse": True,
    }


def judgment_work_class_grants_premium_intent(
    shell_root: Path,
    work_class: str,
    carrier_id: str,
    model_id: str,
) -> bool:
    normalized = str(work_class or "").strip()
    if normalized not in judgment_work_classes_from_map(shell_root):
        return False
    map_data = load_work_class_carrier_default_map(shell_root)
    if map_data.get("judgment_work_class_is_explicit_premium_intent") is not True:
        return False
    defaults_by = map_data.get("defaults_by_work_class")
    entry = defaults_by.get(normalized) if isinstance(defaults_by, Mapping) else None
    if not isinstance(entry, Mapping):
        return False
    return (
        str(entry.get("carrier_id") or "").strip() == str(carrier_id or "").strip()
        and str(entry.get("model_id") or "").strip() == str(model_id or "").strip()
    )


def resolve_unattended_spawn_carrier_model(
    shell_root: Path,
    work_class: str,
) -> dict[str, Any]:
    """Bind unattended SOS queue spawns to WORK_CLASS_CARRIER_DEFAULT_MAP (bulk fallback)."""

    normalized = str(work_class or "").strip()
    map_data = load_work_class_carrier_default_map(shell_root)
    map_sha = str(map_data.get("_map_sha256") or "")
    defaults_by = map_data.get("defaults_by_work_class")
    entry = defaults_by.get(normalized) if isinstance(defaults_by, Mapping) else None
    if isinstance(entry, Mapping):
        carrier_id = str(entry.get("carrier_id") or UNATTENDED_BULK_DEFAULT_CARRIER).strip()
        model_id = str(entry.get("model_id") or UNATTENDED_BULK_DEFAULT_MODEL).strip()
        tier = str(entry.get("tier") or "")
        source = "work_class_carrier_default_map"
    else:
        carrier_id = UNATTENDED_BULK_DEFAULT_CARRIER
        model_id = UNATTENDED_BULK_DEFAULT_MODEL
        tier = "bulk"
        source = "unattended_bulk_fallback"
    banned = sovereign_banned_spawn_models(shell_root)
    if model_id in banned:
        if tier == "judgment":
            model_id = "claude-sonnet-5"
            carrier_id = "claude_cli"
        else:
            model_id = UNATTENDED_BULK_DEFAULT_MODEL
            carrier_id = UNATTENDED_BULK_DEFAULT_CARRIER
        source = "sovereign_banned_model_hard_override"
    return {
        "carrier_id": carrier_id,
        "model_id": model_id,
        "work_class": normalized,
        "tier": tier,
        "work_class_map_sha256": map_sha,
        "work_class_map_path": WORK_CLASS_CARRIER_DEFAULT_MAP_REL.as_posix(),
        "resolution_source": source,
    }


def model_requires_explicit_intent_for_unattended(
    shell_root: Path,
    carrier_id: str,
    model_id: str,
    *,
    work_class: str | None = None,
) -> bool:
    model = str(model_id or "").strip()
    carrier = str(carrier_id or "").strip()
    if work_class and judgment_work_class_grants_premium_intent(
        shell_root, work_class, carrier, model
    ):
        return False
    if not model:
        return False
    map_data = load_work_class_carrier_default_map(shell_root)
    explicit_list = map_data.get("requires_explicit_premium_intent_for") or []
    if model in {str(item).strip() for item in explicit_list if str(item).strip()}:
        return True
    steward_lane = map_data.get("important_steward_override_lane")
    if isinstance(steward_lane, Mapping):
        premium_models = steward_lane.get("cursor_cli_premium_models") or []
        claude_models = steward_lane.get("claude_cli_models") or []
        if carrier == "cursor_cli" and model in {
            str(item).strip() for item in premium_models if str(item).strip()
        }:
            return True
        if carrier == "claude_cli" and model in {
            str(item).strip() for item in claude_models if str(item).strip()
        }:
            return True
    if is_leader_tier_model(carrier, model):
        return True
    if carrier == "claude_cli" and model in sovereign_banned_spawn_models(shell_root):
        return True
    if carrier == "claude_cli" and "fable" in model.lower():
        return True
    return False


def refusal_for_unattended_spawn_model(
    shell_root: Path,
    resolution: Mapping[str, Any],
    *,
    row_id: Any = None,
    index: Any = None,
    domain_id: str = "",
    explicit_model: str | None = None,
    explicit_premium_intent: bool = False,
) -> dict[str, Any] | None:
    work_class = str(resolution.get("work_class") or "").strip()
    carrier = str(resolution.get("carrier_id") or "").strip()
    model = str(explicit_model or resolution.get("model_id") or "").strip()
    if not explicit_premium_intent and judgment_work_class_grants_premium_intent(
        shell_root, work_class, carrier, model
    ):
        explicit_premium_intent = True
    if explicit_premium_intent:
        return None
    if not model_requires_explicit_intent_for_unattended(
        shell_root, carrier, model, work_class=work_class or None
    ):
        return None
    return {
        "ok": False,
        "domain_id": domain_id,
        "index": index,
        "row_id": row_id,
        "finding": UNATTENDED_PREMIUM_SPAWN_REFUSAL_FINDING,
        "resolved_model": model,
        "resolved_carrier": carrier,
        "work_class": resolution.get("work_class"),
        "work_class_map_sha256": resolution.get("work_class_map_sha256"),
        "detects_absence": True,
    }


def probe_unattended_premium_sos_spawn_absence(shell_root: Path) -> dict[str, Any]:
    """Report-only: recent SOS queue executions that reached premium without map pin."""

    check: dict[str, Any] = {
        "check_id": "unattended_premium_sos_spawn_economics",
        "status": "ok",
        "findings": [],
        "samples": [],
    }
    receipts_dir = shell_root / "ION/05_context/current/sos_domain_spawn_receipts"
    if not receipts_dir.is_dir():
        return check
    paths = sorted(receipts_dir.glob("*_SOS_DOMAIN_SPAWN_QUEUE_EXECUTION.candidate.json"))[-12:]
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for item in payload.get("results") or []:
            if not isinstance(item, Mapping):
                continue
            model = str(
                item.get("resolved_model_id")
                or item.get("selected_model")
                or (
                    (item.get("result") or {}).get("selected_model")
                    if isinstance(item.get("result"), Mapping)
                    else ""
                )
            ).strip()
            carrier = str(item.get("resolved_carrier_id") or "").strip() or "cursor_cli"
            if not model:
                continue
            if not model_requires_explicit_intent_for_unattended(shell_root, carrier, model):
                continue
            if item.get("finding") == UNATTENDED_PREMIUM_SPAWN_REFUSAL_FINDING:
                continue
            if item.get("explicit_premium_intent"):
                continue
            sample = {
                "receipt": path.name,
                "domain_id": item.get("domain_id"),
                "row_id": item.get("row_id"),
                "resolved_model": model,
                "resolved_carrier": carrier,
            }
            check["samples"].append(sample)
    if check["samples"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": "unattended_premium_sos_spawn_without_explicit_intent",
                "signal_id": ABSENCE_SIGNAL_UNATTENDED_PREMIUM_SOS_SPAWN,
                "count": len(check["samples"]),
                "sample": check["samples"][:5],
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ),
            }
        )
    return check


JUDGMENT_SPAWN_ADMISSION_STREAK_FINDING = "judgment_work_class_spawn_admission_streak"


def probe_judgment_work_class_spawn_admission_streak(
    shell_root: Path,
    *,
    min_repeats: int = 3,
    window_receipts: int = 12,
) -> dict[str, Any]:
    """Report-only: repeated identical spawn-admission failures on judgment work classes."""

    check: dict[str, Any] = {
        "check_id": "judgment_work_class_spawn_admission_streak",
        "status": "ok",
        "findings": [],
        "samples": [],
    }
    judgment_classes = judgment_work_classes_from_map(shell_root)
    if not judgment_classes:
        return check
    receipts_dir = shell_root / "ION/05_context/current/sos_domain_spawn_receipts"
    if not receipts_dir.is_dir():
        return check
    paths = sorted(receipts_dir.glob("*_SOS_DOMAIN_SPAWN_QUEUE_EXECUTION.candidate.json"))[
        -window_receipts:
    ]
    streak: dict[tuple[str, str], int] = {}
    last_sample: dict[tuple[str, str], Mapping[str, Any]] = {}
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for item in payload.get("results") or []:
            if not isinstance(item, Mapping) or item.get("ok"):
                continue
            wc = str(item.get("work_class") or "").strip()
            if wc not in judgment_classes:
                continue
            finding = str(item.get("finding") or "").strip()
            if not finding:
                continue
            key = (wc, finding)
            streak[key] = streak.get(key, 0) + 1
            last_sample[key] = {
                "receipt": path.name,
                "domain_id": item.get("domain_id"),
                "row_id": item.get("row_id"),
                "work_class": wc,
                "finding": finding,
                "resolved_carrier_id": item.get("resolved_carrier_id"),
                "resolved_model_id": item.get("resolved_model_id"),
            }
    for (wc, finding), count in streak.items():
        if count < min_repeats:
            continue
        sample = dict(last_sample.get((wc, finding)) or {})
        sample["repeat_count"] = count
        check["samples"].append(sample)
    if check["samples"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": JUDGMENT_SPAWN_ADMISSION_STREAK_FINDING,
                "signal_id": JUDGMENT_SPAWN_ADMISSION_STREAK_FINDING,
                "count": len(check["samples"]),
                "sample": check["samples"][:5],
                "route_to": (
                    "ION/05_context/current/domain_weaver/triad/absence_alarms/"
                    "domain.runtime_carrier_and_action_admission/"
                ),
            }
        )
    return check


def probe_spawn_model_outside_sovereign_allowlist(shell_root: Path) -> dict[str, Any]:
    """Report-only: SOS spawn resolutions outside sovereign approved model set."""

    allowed = sovereign_approved_spawn_models(shell_root)
    check: dict[str, Any] = {
        "check_id": "spawn_model_outside_sovereign_allowlist",
        "status": "ok",
        "allowed_models": sorted(allowed),
        "findings": [],
        "samples": [],
    }
    map_data = load_work_class_carrier_default_map(shell_root)
    absence_cfg = map_data.get("spawn_model_absence")
    route_to = (
        str(absence_cfg.get("route_to") or "").strip()
        if isinstance(absence_cfg, Mapping)
        else ""
    ) or (
        "ION/05_context/current/domain_weaver/triad/absence_alarms/"
        "domain.model_routing_and_reasoning_economics/"
    )
    banned = sovereign_banned_spawn_models(shell_root)
    defaults_by = map_data.get("defaults_by_work_class")
    if isinstance(defaults_by, Mapping):
        for wc, entry in defaults_by.items():
            if not isinstance(entry, Mapping):
                continue
            model = str(entry.get("model_id") or "").strip()
            if model and model in banned:
                check["samples"].append(
                    {
                        "source": "work_class_carrier_default_map",
                        "work_class": str(wc),
                        "model_id": model,
                        "violation": SOVEREIGN_BANNED_SPAWN_MODEL_FINDING,
                    }
                )
            elif model and model not in allowed:
                check["samples"].append(
                    {
                        "source": "work_class_carrier_default_map",
                        "work_class": str(wc),
                        "model_id": model,
                    }
                )
    receipts_dir = shell_root / "ION/05_context/current/sos_domain_spawn_receipts"
    if receipts_dir.is_dir():
        paths = sorted(receipts_dir.glob("*_SOS_DOMAIN_SPAWN_QUEUE_EXECUTION.candidate.json"))[
            -8:
        ]
        for path in paths:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if payload.get("dry_run") is True:
                continue
            if str(payload.get("receipt_purpose") or "").strip() == "negative_control":
                continue
            for item in payload.get("results") or []:
                if not isinstance(item, Mapping):
                    continue
                if item.get("detects_absence") is True and item.get("ok") is False:
                    continue
                row_id = str(item.get("row_id") or "")
                if row_id.startswith("negctrl-"):
                    continue
                model = str(
                    item.get("resolved_model_id")
                    or item.get("resolved_model")
                    or item.get("selected_model")
                    or ""
                ).strip()
                if model and model not in allowed:
                    check["samples"].append(
                        {
                            "source": "sos_spawn_receipt",
                            "receipt": path.name,
                            "model_id": model,
                            "work_class": item.get("work_class"),
                        }
                    )
    if check["samples"]:
        check["status"] = "finding"
        check["findings"].append(
            {
                "kind": SPAWN_MODEL_OUTSIDE_SOVEREIGN_ALLOWLIST_FINDING,
                "signal_id": ABSENCE_SIGNAL_SPAWN_MODEL_OUTSIDE_SOVEREIGN_ALLOWLIST,
                "count": len(check["samples"]),
                "sample": check["samples"][:8],
                "route_to": route_to,
            }
        )
    return check


def load_unified_routing(shell_root: Path) -> dict[str, Any]:
    yaml_path = shell_root / ROUTING_RELATIVE_PATH
    json_path = shell_root / ROUTING_JSON_RELATIVE_PATH
    data = _read_yaml(yaml_path)
    if data:
        json_data: dict[str, Any] | None = None
        json_load_failed = False
        if json_path.is_file():
            try:
                loaded_json = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                json_load_failed = True
            else:
                if isinstance(loaded_json, dict):
                    json_data = loaded_json
                else:
                    json_load_failed = True
        result = dict(data)
        result["_routing_source_path"] = ROUTING_RELATIVE_PATH.as_posix()
        result["_routing_source_sha256"] = hashlib.sha256(yaml_path.read_bytes()).hexdigest()
        result["_routing_source_parity_ok"] = (
            False
            if json_load_failed
            else json_data == data
            if json_data is not None
            else None
        )
        return result
    if json_path.is_file():
        try:
            loaded_json = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            loaded_json = None
        if isinstance(loaded_json, dict) and loaded_json:
            result = dict(loaded_json)
            result["_routing_source_path"] = ROUTING_JSON_RELATIVE_PATH.as_posix()
            result["_routing_source_sha256"] = hashlib.sha256(json_path.read_bytes()).hexdigest()
            result["_routing_source_parity_ok"] = None
            result["_routing_source_canonical_missing"] = True
            return result
    if not data:
        return {
            "schema_id": "ion.domain_leader_carrier_routing.v0_4_candidate",
            "default_carrier": "cursor_cli",
            "leader_carrier": "claude_cli",
            "leader_domains": sorted(DEFAULT_LEADER_DOMAINS),
            "carrier_fallback_order": list(DEFAULT_CARRIER_FALLBACK_ORDER),
            "selection_dynamics": {"default_posture": "availability_first"},
            "model_downgrade_ladders": {
                carrier: list(models) for carrier, models in DEFAULT_MODEL_LADDERS.items()
            },
            "claude_cli": {"default_model": "claude-sonnet-5", "binary": "claude"},
            "codex_cli": {"default_model": "gpt-5.6-sol", "binary": "codex"},
            "cursor_cli": {"default_model": "composer-2.5-fast", "binary": "cursor-agent"},
            "_routing_source_path": None,
            "_routing_source_sha256": None,
            "_routing_source_parity_ok": None,
            "_routing_source_missing": True,
        }
    return data


def _selection_posture(routing: Mapping[str, Any], posture: str | None) -> str:
    dynamics = routing.get("selection_dynamics")
    if not isinstance(dynamics, Mapping):
        return "availability_first"
    default = str(dynamics.get("default_posture") or "availability_first")
    if posture and posture in dynamics.get("postures", {}):
        return str(posture)
    return default


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


def _active_availability_windows(
    routing: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    raw = routing.get("availability_windows")
    if not isinstance(raw, list):
        return []
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    active: list[dict[str, Any]] = []
    for window in raw:
        if not isinstance(window, Mapping):
            continue
        if window.get("active") is not True:
            continue
        expires_at = _parse_iso_datetime(str(window.get("expires_at") or ""))
        if expires_at is not None and current.astimezone(timezone.utc) >= expires_at.astimezone(
            timezone.utc
        ):
            continue
        active.append(dict(window))
    return active


def _model_matches_blocked_pattern(model: str, pattern: str) -> bool:
    model_str = str(model).strip()
    pattern_str = str(pattern).strip()
    if not model_str or not pattern_str:
        return False
    return fnmatch(model_str, pattern_str)


def _is_model_blocked_by_availability_window(
    routing: Mapping[str, Any],
    carrier_id: str,
    model: str,
    *,
    now: datetime | None = None,
) -> bool:
    carrier = str(carrier_id).strip()
    model_str = str(model).strip()
    for window in _active_availability_windows(routing, now=now):
        patterns_map = window.get("blocked_model_patterns")
        if not isinstance(patterns_map, Mapping):
            continue
        patterns = patterns_map.get(carrier)
        if not isinstance(patterns, list):
            continue
        for pattern in patterns:
            if _model_matches_blocked_pattern(model_str, str(pattern)):
                return True
    return False


def _availability_window_codex_redirect(
    routing: Mapping[str, Any],
    *,
    tier: Mapping[str, Any] | None,
    work_class: str | None,
    is_leader_domain: bool = False,
    now: datetime | None = None,
) -> dict[str, str] | None:
    tier_key = str((tier or {}).get("tier_key") or (tier or {}).get("tier_id") or "")
    normalized_work_class = str(work_class or "").strip()
    for window in _active_availability_windows(routing, now=now):
        redirect = window.get("leader_tier_codex_redirect")
        if not isinstance(redirect, Mapping):
            continue
        applies_to = {
            str(item).strip()
            for item in (redirect.get("applies_to_tiers") or [])
            if str(item).strip()
        }
        when_work_classes = {
            str(item).strip()
            for item in (redirect.get("when_work_class_in") or [])
            if str(item).strip()
        }
        work_class_match = bool(
            when_work_classes and normalized_work_class in when_work_classes
        )
        tier_match = bool(
            tier_key
            and applies_to
            and tier_key in applies_to
            and (work_class_match or not when_work_classes)
        )
        if not work_class_match and not tier_match:
            continue
        carrier = str(redirect.get("carrier") or "").strip()
        model = str(redirect.get("model") or "").strip()
        if carrier and model and _approved_model(carrier, model):
            return {
                "carrier_id": carrier,
                "model": model,
                "reasoning_effort": str(redirect.get("reasoning_effort") or "").strip(),
                "availability_window_id": str(window.get("window_id") or "").strip(),
                "availability_window_packet_ref": str(window.get("packet_ref") or "").strip(),
                "selection_override": "availability_window_leader_tier_codex_redirect",
            }
    return None


def _is_composer_blocked_for_leader_during_window(
    routing: Mapping[str, Any],
    carrier_id: str,
    model: str,
    *,
    is_leader_domain: bool,
    now: datetime | None = None,
) -> bool:
    """Composer remains available on cursor_cli during availability windows.

    ``composer_non_leader_only`` scopes codex redirect eligibility; it is not a
    composer ban for leader domains.
    """
    _ = (routing, carrier_id, model, is_leader_domain, now)
    return False


def _disabled_carriers(routing: Mapping[str, Any]) -> set[str]:
    disabled = routing.get("disabled_carriers")
    if not isinstance(disabled, Mapping):
        return set()
    return {str(key) for key in disabled.keys()}


def _carrier_fallback_order(routing: Mapping[str, Any]) -> list[str]:
    raw = routing.get("carrier_fallback_order")
    if isinstance(raw, list) and raw:
        return [str(item) for item in raw if str(item)]
    return list(DEFAULT_CARRIER_FALLBACK_ORDER)


def _model_ladder(routing: Mapping[str, Any], carrier_id: str) -> list[str]:
    approved = OPERATOR_APPROVED_MODELS.get(carrier_id, frozenset())
    ladders = routing.get("model_downgrade_ladders")
    if isinstance(ladders, Mapping):
        raw = ladders.get(carrier_id)
        if isinstance(raw, list) and raw:
            filtered = [str(item) for item in raw if str(item) in approved]
            if filtered:
                return filtered
    return list(DEFAULT_MODEL_LADDERS.get(carrier_id, ()))


def _approved_model(carrier_id: str, model: str) -> bool:
    return is_operator_approved_model(carrier_id, model)


def approved_models_for_carrier(carrier_id: str) -> tuple[str, ...]:
    """Return models eligible for ordinary default and fallback routing."""

    return tuple(DEFAULT_MODEL_LADDERS.get(str(carrier_id), ()))


def experimental_models_for_carrier(carrier_id: str) -> tuple[str, ...]:
    """Return exact explicit-only experimental models for one carrier."""

    return tuple(EXPERIMENTAL_EXACT_MODELS.get(str(carrier_id), ()))


def execution_models_for_carrier(carrier_id: str) -> tuple[str, ...]:
    """Return every exact model admitted at the execution boundary."""

    carrier = str(carrier_id)
    leader_tier = LEADER_TIER_CURSOR_MODELS if carrier == "cursor_cli" else ()
    return tuple(
        dict.fromkeys(
            [
                *DEFAULT_MODEL_LADDERS.get(carrier, ()),
                *leader_tier,
                *EXPERIMENTAL_EXACT_MODELS.get(carrier, ()),
            ]
        )
    )


def is_leader_tier_model(carrier_id: str, model: str) -> bool:
    """Return whether a model is a leader-tier cross-carrier equivalent on cursor_cli."""

    return (
        str(carrier_id) == "cursor_cli"
        and str(model).strip() in frozenset(LEADER_TIER_CURSOR_MODELS)
    )


def is_experimental_model(carrier_id: str, model: str) -> bool:
    """Return whether a model is in the explicit-only experiment roster."""

    if is_leader_tier_model(carrier_id, model):
        return False
    return str(model).strip() in frozenset(
        EXPERIMENTAL_EXACT_MODELS.get(str(carrier_id), ())
    )


def _load_cross_carrier_equivalents(
    routing: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    raw = routing.get("cross_carrier_model_equivalents")
    if isinstance(raw, Mapping):
        result: dict[str, dict[str, str]] = {}
        for source_model, carriers in raw.items():
            if isinstance(carriers, Mapping):
                result[str(source_model)] = {
                    str(carrier): str(equiv)
                    for carrier, equiv in carriers.items()
                    if str(carrier) and str(equiv)
                }
        if result:
            return result
    return dict(CROSS_CARRIER_MODEL_EQUIVALENTS)


def _tier_cross_carrier_entries(
    routing: Mapping[str, Any],
    tier: Mapping[str, Any] | None,
) -> list[tuple[str, str, str]]:
    """Return (carrier_id, model, source_model) for tier cross-carrier equivalents."""

    if not tier:
        return []
    equivalents = _load_cross_carrier_equivalents(routing)
    tier_model = str(tier.get("model") or "")
    entries: list[tuple[str, str, str]] = []
    tier_equiv = tier.get("cross_carrier_equivalents")
    if isinstance(tier_equiv, Mapping):
        for carrier_id, model in tier_equiv.items():
            model_str = str(model).strip()
            carrier_str = str(carrier_id).strip()
            if model_str and carrier_str and _approved_model(carrier_str, model_str):
                entries.append((carrier_str, model_str, tier_model))
    elif tier_model in equivalents:
        for carrier_id, model in equivalents[tier_model].items():
            if _approved_model(carrier_id, model):
                entries.append((carrier_id, model, tier_model))
    return entries


def is_operator_approved_model(carrier_id: str, model: str) -> bool:
    """Fail closed when an execution boundary receives an unapproved model."""

    normalized_model = str(model).strip()
    if normalized_model in PRIVACY_RESTRICTED_MODELS:
        return False
    return normalized_model in EXECUTION_APPROVED_MODELS.get(
        str(carrier_id), frozenset()
    )


def _resolve_model_tier(
    routing: Mapping[str, Any],
    domain_id: str,
    work_class: str | None = None,
) -> dict[str, Any] | None:
    tiers = routing.get("model_tiers")
    if not isinstance(tiers, Mapping):
        return None
    default_tier: dict[str, Any] | None = None
    for tier_key, tier in tiers.items():
        if not isinstance(tier, Mapping):
            continue
        if tier.get("default") is True:
            default_tier = {"tier_key": str(tier_key), **dict(tier)}
        domains = {str(item).strip() for item in (tier.get("domains") or []) if str(item).strip()}
        if domain_id in domains:
            required_work_classes = {
                str(item).strip()
                for item in (tier.get("work_classes") or [])
                if str(item).strip()
            }
            if required_work_classes and str(work_class or "").strip() not in required_work_classes:
                continue
            return {"tier_key": str(tier_key), **dict(tier)}
    return default_tier


def _carrier_cfg(routing: Mapping[str, Any], carrier_id: str) -> dict[str, Any]:
    cfg = routing.get(carrier_id)
    return dict(cfg) if isinstance(cfg, Mapping) else {}


def probe_carrier_available(
    shell_root: Path,
    carrier_id: str,
    *,
    routing: Mapping[str, Any] | None = None,
) -> tuple[bool, str]:
    routing = routing or load_unified_routing(shell_root)
    quota_exhausted, quota_detail = carrier_quota_health.is_carrier_quota_exhausted(
        shell_root, carrier_id
    )
    if quota_exhausted:
        return False, quota_detail
    settings_blocked, settings_finding = carrier_settings.carrier_settings_gate(
        shell_root, carrier_id
    )
    if settings_blocked:
        return False, str(settings_finding or "carrier_settings_blocked")
    if carrier_id in _disabled_carriers(routing):
        return False, "carrier_disabled_by_routing"
    if carrier_id == "codex_app_server":
        try:
            from .ion_codex_app_server_bridge import invoke_codex_app_server_route

            result = invoke_codex_app_server_route(shell_root, route_id="app_server_status", args={})
            available = bool(result.get("ok")) and bool(result.get("available", result.get("ok")))
            return available, str(result.get("finding") or "ok")
        except Exception as exc:
            return False, str(exc)[:240]
    argv = CARRIER_PROBE.get(carrier_id)
    if not argv:
        return False, "no_probe_configured"
    exe = shutil.which(argv[0])
    if not exe:
        return False, "executable_not_on_path"
    cmd = [exe, *argv[1:]]
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(shell_root),
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "probe_timeout"
    except OSError as exc:
        return False, str(exc)[:240]
    combined = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0:
        return False, normalize_usage_limit_signal(combined) or "probe_failed"
    return True, combined[:120] or "ok"


def _infrastructure_fit_bonus(
    routing: Mapping[str, Any],
    carrier_id: str,
) -> float:
    """Score carrier ION infrastructure alignment (rules/skills/hooks/mounts)."""

    law = routing.get("model_access_law")
    if not isinstance(law, Mapping):
        return 0.0
    fit_map = law.get("infrastructure_fit")
    if not isinstance(fit_map, Mapping):
        return 0.0
    factors = fit_map.get(carrier_id)
    if not isinstance(factors, list):
        return 0.0
    bonus = min(len([str(item) for item in factors if str(item)]), 4) * 2.0
    universal = str(
        routing.get("universal_access_carrier")
        or (law.get("universal_access_carrier") if isinstance(law, Mapping) else "")
        or ""
    )
    if str(carrier_id) == universal:
        bonus += 3.0
    return bonus


def _candidate_score(
    *,
    carrier_id: str,
    model: str,
    available: bool,
    tier_rank: int,
    chain_index: int,
    posture: str,
    routing: Mapping[str, Any] | None = None,
) -> float:
    base = 100.0 - chain_index * 8.0 - tier_rank * 3.0
    if not available:
        base -= 50.0
    if routing is not None:
        base += _infrastructure_fit_bonus(routing, carrier_id)
    if posture == "availability_first" and available:
        base += 15.0
    elif posture == "cost_first" and model in {"composer-2.5", "composer-2.5-fast"}:
        base += 10.0
    elif posture == "speed_first" and model == "composer-2.5-fast":
        base += 10.0
    return base


def build_fallback_chain(
    shell_root: Path,
    *,
    primary_carrier: str,
    primary_model: str,
    routing: Mapping[str, Any] | None = None,
    allowed_carriers: list[str] | None = None,
    tier: Mapping[str, Any] | None = None,
    work_class: str | None = None,
    is_leader_domain: bool = False,
    enable_availability_override: bool = True,
) -> list[dict[str, Any]]:
    routing = routing or load_unified_routing(shell_root)
    disabled = _disabled_carriers(routing)
    allowed = set(allowed_carriers) if allowed_carriers is not None else None
    chain: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def _append(
        carrier_id: str,
        model: str,
        *,
        reason: str,
        chain_index: int,
        window_meta: Mapping[str, Any] | None = None,
        bypass_allowed: bool = False,
    ) -> None:
        if _is_model_blocked_by_availability_window(routing, carrier_id, model):
            return
        if _is_composer_blocked_for_leader_during_window(
            routing,
            carrier_id,
            model,
            is_leader_domain=is_leader_domain,
        ):
            return
        if not _approved_model(carrier_id, model):
            return
        key = (carrier_id, model)
        if key in seen:
            return
        if carrier_id in disabled:
            return
        if not bypass_allowed and allowed is not None and carrier_id not in allowed:
            return
        seen.add(key)
        available, detail = probe_carrier_available(shell_root, carrier_id, routing=routing)
        row: dict[str, Any] = {
            "carrier_id": carrier_id,
            "model": model,
            "reason": reason,
            "chain_index": chain_index,
            "available": available,
            "probe_detail": detail[:160],
        }
        if window_meta:
            row.update(
                {
                    "reasoning_effort": window_meta.get("reasoning_effort") or None,
                    "availability_window_id": window_meta.get("availability_window_id") or None,
                    "availability_window_packet_ref": window_meta.get(
                        "availability_window_packet_ref"
                    )
                    or None,
                    "selection_override": window_meta.get("selection_override") or None,
                }
            )
        chain.append(row)

    carriers_to_visit: list[str] = []
    if primary_carrier not in disabled:
        carriers_to_visit.append(primary_carrier)
    for carrier_id in _carrier_fallback_order(routing):
        if carrier_id not in carriers_to_visit:
            carriers_to_visit.append(carrier_id)

    tier_cross_carrier = _tier_cross_carrier_entries(routing, tier)
    tier_equiv_by_carrier: dict[str, list[tuple[str, str]]] = {}
    for carrier_id, model, _source in tier_cross_carrier:
        tier_equiv_by_carrier.setdefault(carrier_id, []).append((model, "cross_carrier_tier_equivalent"))

    index = 0

    def _append_carrier_models(
        carrier_id: str,
        models: list[str],
        reasons_by_model: dict[str, str],
    ) -> None:
        nonlocal index
        for model in models:
            reason = reasons_by_model.get(model)
            if not reason:
                reason = "primary" if carrier_id == primary_carrier and model == primary_model else "fallback"
            _append(carrier_id, model, reason=reason, chain_index=index)
            index += 1

    # Phase 1: primary carrier (primary model + same-carrier ladder)
    if primary_carrier not in disabled:
        ladder = _model_ladder(routing, primary_carrier)
        cfg = _carrier_cfg(routing, primary_carrier)
        default_model = str(cfg.get("default_model") or (ladder[0] if ladder else ""))
        primary_models: list[str] = []
        primary_reasons: dict[str, str] = {}
        if primary_model:
            primary_models.append(primary_model)
            primary_reasons[primary_model] = "primary"
        for model in ladder:
            if model not in primary_models:
                primary_models.append(model)
        if default_model and default_model not in primary_models:
            primary_models.append(default_model)
        _append_carrier_models(primary_carrier, primary_models, primary_reasons)

    # Phase 2: cross-carrier tier equivalents before other-carrier downgrade
    for carrier_id in _carrier_fallback_order(routing):
        if carrier_id == primary_carrier or carrier_id in disabled:
            continue
        equiv_entries = tier_equiv_by_carrier.get(carrier_id, [])
        if not equiv_entries:
            continue
        equiv_models: list[str] = []
        equiv_reasons: dict[str, str] = {}
        for equiv_model, equiv_reason in equiv_entries:
            if equiv_model not in equiv_models:
                equiv_models.append(equiv_model)
                equiv_reasons[equiv_model] = equiv_reason
        _append_carrier_models(carrier_id, equiv_models, equiv_reasons)

    # Phase 2b: availability-window codex redirect (operative override for leader/consequential)
    if enable_availability_override:
        codex_redirect = _availability_window_codex_redirect(
            routing,
            tier=tier,
            work_class=work_class,
            is_leader_domain=is_leader_domain,
        )
        if codex_redirect:
            redirect_carrier = str(codex_redirect["carrier_id"])
            redirect_model = str(codex_redirect["model"])
            if redirect_carrier not in disabled:
                # Operative override: bypass tier/caller allowed_carriers during active window.
                _append(
                    redirect_carrier,
                    redirect_model,
                    reason="availability_window_codex_redirect",
                    chain_index=index,
                    window_meta=codex_redirect,
                    bypass_allowed=True,
                )
                index += 1

    # Phase 3: remaining carriers' downgrade ladders
    for carrier_id in carriers_to_visit:
        if carrier_id == primary_carrier or carrier_id in disabled:
            continue
        ladder = _model_ladder(routing, carrier_id)
        cfg = _carrier_cfg(routing, carrier_id)
        default_model = str(cfg.get("default_model") or (ladder[0] if ladder else ""))
        skip = {model for model, _ in tier_equiv_by_carrier.get(carrier_id, [])}
        models: list[str] = []
        reasons_by_model: dict[str, str] = {}
        for model in ladder:
            if model not in models and model not in skip:
                models.append(model)
        if default_model and default_model not in models and default_model not in skip:
            models.append(default_model)
        _append_carrier_models(carrier_id, models, reasons_by_model)

    return chain


def _pick_from_chain(
    chain: list[dict[str, Any]],
    *,
    required_carriers: frozenset[str] | None = None,
    require_available: bool = True,
) -> dict[str, Any] | None:
    for row in chain:
        carrier_id = str(row.get("carrier_id") or "")
        if required_carriers and carrier_id not in required_carriers:
            continue
        if require_available and not row.get("available"):
            continue
        return row
    for row in chain:
        carrier_id = str(row.get("carrier_id") or "")
        if required_carriers and carrier_id not in required_carriers:
            continue
        return row
    return None


def resolve_execution_selection(
    shell_root: Path,
    *,
    domain_id: str | None = None,
    carrier: str | None = None,
    requested_model: str | None = None,
    work_class: str | None = None,
    posture: str | None = None,
    allowed_carriers: list[str] | None = None,
    execution_surface: str | None = None,
) -> dict[str, Any]:
    routing = load_unified_routing(shell_root)
    normalized_domain = str(domain_id or "").strip()
    normalized_work_class = str(work_class or "").strip()
    normalized_requested_model = str(requested_model or "").strip()
    if (
        normalized_requested_model.lower()
        in CLAUDE_MODEL_ALIASES_REQUIRING_EXPLICIT_ID
    ):
        raise ValueError(
            "alias_forbidden_requires_explicit_model_id:"
            f"{normalized_requested_model}"
        )
    if (
        normalized_requested_model
        and normalized_requested_model in sovereign_banned_spawn_models(shell_root)
    ):
        raise ValueError(
            f"{SOVEREIGN_BANNED_SPAWN_MODEL_FINDING}:{normalized_requested_model}"
        )
    selected_posture = _selection_posture(routing, posture)
    default_carrier = str(routing.get("default_carrier") or "claude_cli")
    leader_carrier = str(routing.get("leader_carrier") or default_carrier)
    leader_domains = {
        str(item).strip()
        for item in (routing.get("leader_domains") or DEFAULT_LEADER_DOMAINS)
        if str(item).strip()
    }
    tier = (
        _resolve_model_tier(routing, normalized_domain, work_class)
        if normalized_domain
        else None
    )
    disabled = _disabled_carriers(routing)
    requested_carrier = str(carrier or "").strip()
    explicit_carrier = requested_carrier in KNOWN_EXECUTION_CARRIERS
    unknown_carrier_request = requested_carrier not in {"", "auto", *KNOWN_EXECUTION_CARRIERS}
    disabled_carrier_request = explicit_carrier and requested_carrier in disabled
    leader_execution_requires_work_class = bool(
        execution_surface in MATERIAL_EXECUTION_SURFACES
        and normalized_domain in leader_domains
    )
    work_class_unclassified = normalized_work_class.lower() in UNCLASSIFIED_WORK_CLASSES
    routing_source_parity_failed = routing.get("_routing_source_parity_ok") is False
    routing_source_missing = bool(
        execution_surface in MATERIAL_EXECUTION_SURFACES
        and not routing.get("_routing_source_sha256")
    )
    routing_source_parity_missing = bool(
        execution_surface in MATERIAL_EXECUTION_SURFACES
        and routing.get("_routing_source_sha256")
        and routing.get("_routing_source_parity_ok") is not True
    )

    if carrier in disabled:
        carrier = "auto"
    if carrier in {None, "", "auto"}:
        if tier and tier.get("carrier") and str(tier.get("carrier")) not in disabled:
            primary_carrier = str(tier.get("carrier"))
            reason = f"model_tier:{tier.get('tier_key') or tier.get('tier_id')}"
        elif normalized_domain in leader_domains:
            primary_carrier = leader_carrier if leader_carrier not in disabled else default_carrier
            reason = "domain_leader_routing"
        else:
            primary_carrier = default_carrier
            reason = "default_routing"
    elif carrier in {"cursor_cli", "codex_cli", "codex_app_server", "claude_cli"}:
        primary_carrier = str(carrier)
        reason = "explicit_carrier"
    else:
        if tier and tier.get("carrier") and str(tier.get("carrier")) not in disabled:
            primary_carrier = str(tier.get("carrier"))
            reason = "unknown_carrier_fallback_to_model_tier"
        elif normalized_domain in leader_domains:
            primary_carrier = leader_carrier if leader_carrier not in disabled else default_carrier
            reason = "unknown_carrier_fallback_to_domain_leader"
        else:
            primary_carrier = default_carrier
            reason = "unknown_carrier_fallback_to_default"

    tier_model = str(tier.get("model") or "") if tier else ""
    if tier_model and not _approved_model(primary_carrier, tier_model):
        tier_model = ""
        tier_equiv = tier.get("cross_carrier_equivalents") if tier else None
        if isinstance(tier_equiv, Mapping):
            mapped = str(tier_equiv.get(primary_carrier) or "")
            if mapped and _approved_model(primary_carrier, mapped):
                tier_model = mapped
    cfg = _carrier_cfg(routing, primary_carrier)
    ladder = _model_ladder(routing, primary_carrier)
    configured_model = str(cfg.get("default_model") or "")
    if configured_model and not _approved_model(primary_carrier, configured_model):
        configured_model = ""
    # An explicit model is execution intent, not a post-routing command-line
    # override.  Bind an approved request into the canonical selection so the
    # decision hash, admission, context package, spawn row, and argv all name
    # the same model.  Unapproved requests remain outside the selection and are
    # refused artifact-free by the caller's exact allowlist boundary.
    requested_model_approved = bool(
        normalized_requested_model
        and (
            _approved_model(primary_carrier, normalized_requested_model)
            or (
                primary_carrier == "claude_cli"
                and is_explicit_only_claude_model(normalized_requested_model)
            )
        )
    )
    experimental_model_requested = bool(
        normalized_requested_model
        and is_experimental_model(primary_carrier, normalized_requested_model)
    )
    leader_tier_model_requested = bool(
        normalized_requested_model
        and is_leader_tier_model(primary_carrier, normalized_requested_model)
    )
    experimental_work_class_denial = bool(
        experimental_model_requested
        and work_class_unclassified
        and not leader_tier_model_requested
    )
    primary_model = (
        normalized_requested_model
        if requested_model_approved
        else tier_model or configured_model or (ladder[0] if ladder else "")
    )
    model_route_missing = not bool(primary_model)

    tier_allowed_carriers = {
        str(item)
        for item in ((tier.get("allowed_carriers") or []) if tier else [])
        if str(item)
    }
    caller_allowed_carriers = (
        {str(item) for item in allowed_carriers if str(item)}
        if allowed_carriers is not None
        else None
    )
    if tier_allowed_carriers and caller_allowed_carriers is not None:
        effective_allowed_set = tier_allowed_carriers & caller_allowed_carriers
    elif tier_allowed_carriers:
        effective_allowed_set = set(tier_allowed_carriers)
    elif caller_allowed_carriers is not None:
        effective_allowed_set = set(caller_allowed_carriers)
    else:
        effective_allowed_set = None
    carrier_constraint_empty = bool(
        effective_allowed_set == set()
        and (tier_allowed_carriers or caller_allowed_carriers is not None)
    )
    explicit_tier_denial = bool(
        explicit_carrier
        and tier_allowed_carriers
        and primary_carrier not in tier_allowed_carriers
    )
    explicit_constraint_denial = bool(
        explicit_carrier
        and effective_allowed_set is not None
        and primary_carrier not in effective_allowed_set
    )
    missing_work_class_denial = bool(
        leader_execution_requires_work_class and work_class_unclassified
    )
    effective_allowed_carriers = (
        sorted(effective_allowed_set) if effective_allowed_set is not None else None
    )
    selection_policy_blocked = bool(
        routing_source_missing
        or routing_source_parity_missing
        or routing_source_parity_failed
        or unknown_carrier_request
        or disabled_carrier_request
        or missing_work_class_denial
        or experimental_work_class_denial
        or carrier_constraint_empty
        or explicit_tier_denial
        or explicit_constraint_denial
        or model_route_missing
    )
    chain = build_fallback_chain(
        shell_root,
        primary_carrier=primary_carrier,
        primary_model=primary_model,
        routing=routing,
        allowed_carriers=[] if selection_policy_blocked else effective_allowed_carriers,
        tier=tier,
        work_class=normalized_work_class or None,
        is_leader_domain=normalized_domain in leader_domains,
        enable_availability_override=not selection_policy_blocked,
    )
    if (
        requested_model_approved
        and normalized_requested_model
        and not selection_policy_blocked
        and not any(
            str(row.get("carrier_id") or "") == primary_carrier
            and str(row.get("model") or "") == normalized_requested_model
            for row in chain
        )
    ):
        available, detail = probe_carrier_available(shell_root, primary_carrier, routing=routing)
        chain.insert(
            0,
            {
                "carrier_id": primary_carrier,
                "model": normalized_requested_model,
                "reason": "explicit_model",
                "chain_index": -1,
                "available": available,
                "probe_detail": detail[:160],
            },
        )
    def _rank_key(row: Mapping[str, Any]) -> float:
        reason = str(row.get("reason") or "")
        tier_rank = (
            0
            if reason == "availability_window_codex_redirect"
            else 0.25
            if reason == "primary"
            else 0.5
            if reason == "cross_carrier_tier_equivalent"
            else 1
        )
        return _candidate_score(
            carrier_id=str(row["carrier_id"]),
            model=str(row["model"]),
            available=bool(row.get("available")),
            tier_rank=int(tier_rank),
            chain_index=int(row.get("chain_index") or 0),
            posture=selected_posture,
            routing=routing,
        )

    ranked = sorted(chain, key=_rank_key, reverse=True)
    required_carriers: frozenset[str] | None = None
    if execution_surface == "prompt_spawn":
        required_carriers = PROMPT_SPAWN_EXECUTABLE_CARRIERS
    selected_row: dict[str, Any] | None = None
    if requested_model_approved and normalized_requested_model:
        for row in chain:
            carrier_match = str(row.get("carrier_id") or "") == primary_carrier
            model_match = str(row.get("model") or "") == normalized_requested_model
            carrier_allowed = required_carriers is None or str(row.get("carrier_id") or "") in required_carriers
            if carrier_match and model_match and carrier_allowed and row.get("available") is not False:
                selected_row = dict(row)
                break
    if selected_row is None:
        selected_row = _pick_from_chain(ranked, required_carriers=required_carriers, require_available=True)
    if selected_row is None:
        selected_row = _pick_from_chain(chain, required_carriers=required_carriers, require_available=False)
    selected = dict(selected_row) if selected_row else None
    if selected is None:
        selected = {
            "carrier_id": primary_carrier,
            "model": primary_model,
            "reason": reason,
            "available": False,
            "probe_detail": "no_candidates",
            "chain_index": 0,
        }

    carrier_id = str(selected["carrier_id"])
    carrier_cfg = _carrier_cfg(routing, carrier_id)
    selected_model = str(selected.get("model") or primary_model)
    window_reasoning_effort = str(selected.get("reasoning_effort") or "").strip()
    availability_window_id = str(selected.get("availability_window_id") or "").strip() or None
    availability_window_packet_ref = (
        str(selected.get("availability_window_packet_ref") or "").strip() or None
    )
    selection_override = str(selected.get("selection_override") or "").strip() or None
    tier_applied = bool(
        tier
        and carrier_id == str(tier.get("carrier") or primary_carrier)
        and selected_model == str(tier.get("model") or primary_model)
    )
    tier_env = str(tier.get("model_env") or "") if tier_applied else ""
    tier_label = str(tier.get("model_label") or "") if tier_applied else ""
    tier_reasoning_effort = (
        str(tier.get("reasoning_effort") or "") if tier_applied else ""
    )
    if str(selected.get("reason") or "") == "availability_window_codex_redirect":
        tier_applied = False
        tier_env = str(_carrier_cfg(routing, carrier_id).get("model_env") or "ION_CODEX_MODEL")
        tier_label = "gpt-5.6-sol-availability-window-redirect"
        tier_reasoning_effort = window_reasoning_effort or "max"
        # Operative window bypass inserts codex into the fallback chain even when
        # tier/caller allowed_carriers omit it. Expand effective_allowed_carriers
        # so spawn-row admission cannot reject the same selected carrier.
        if effective_allowed_carriers is None:
            effective_allowed_carriers = [carrier_id]
        elif carrier_id not in effective_allowed_carriers:
            effective_allowed_carriers = sorted(
                set(effective_allowed_carriers) | {carrier_id}
            )
    if not availability_window_id and _active_availability_windows(routing):
        window_redirect = _availability_window_codex_redirect(
            routing,
            tier=tier,
            work_class=normalized_work_class or None,
            is_leader_domain=normalized_domain in leader_domains,
        )
        if window_redirect:
            redirect_carrier = str(window_redirect.get("carrier_id") or "")
            redirect_model = str(window_redirect.get("model") or "")
            if carrier_id == redirect_carrier and selected_model == redirect_model:
                availability_window_id = (
                    str(window_redirect.get("availability_window_id") or "").strip() or None
                )
                availability_window_packet_ref = (
                    str(window_redirect.get("availability_window_packet_ref") or "").strip()
                    or None
                )
                selection_override = (
                    str(window_redirect.get("selection_override") or "").strip() or None
                )
                if str(selected.get("reason") or "") != "availability_window_codex_redirect":
                    if not tier_reasoning_effort and window_redirect.get("reasoning_effort"):
                        tier_reasoning_effort = str(window_redirect.get("reasoning_effort") or "")
    routing_request_basis = {
        "domain_id": normalized_domain or None,
        "work_class": normalized_work_class or None,
        "requested_carrier": requested_carrier or None,
        "requested_model": normalized_requested_model or None,
        "requested_posture": str(posture or "").strip() or None,
        "allowed_carriers": (
            sorted(caller_allowed_carriers)
            if caller_allowed_carriers is not None
            else None
        ),
        "execution_surface": execution_surface,
    }
    routing_decision_basis = {
        **routing_request_basis,
        "carrier_id": carrier_id,
        "model": selected_model,
        "reasoning_effort": tier_reasoning_effort or None,
        "source_model_tier": tier.get("tier_key") if tier else None,
        "effective_allowed_carriers": effective_allowed_carriers,
        "routing_source_sha256": routing.get("_routing_source_sha256"),
        "availability_window_id": availability_window_id,
        "availability_window_packet_ref": availability_window_packet_ref,
        "selection_override": selection_override,
        "selection_reason": str(selected.get("reason") or reason),
    }
    if experimental_model_requested:
        routing_decision_basis.update(
            {
                "experimental_model": True,
                "experimental_model_explicit_only": True,
            }
        )
    routing_decision_sha256 = hashlib.sha256(
        json.dumps(routing_decision_basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    carrier_settings_pause = False
    pause_finding: str | None = None
    if execution_surface in MATERIAL_EXECUTION_SURFACES:
        pause_finding = carrier_settings.selection_pause_finding(shell_root)
        if pause_finding:
            carrier_settings_pause = True
            selected = {
                **selected,
                "available": False,
                "probe_detail": pause_finding,
            }
            carrier_id = str(selected.get("carrier_id") or primary_carrier)
            selected_model = str(selected.get("model") or primary_model)

    return {
        "schema_id": SCHEMA_ID,
        "carrier_id": carrier_id,
        "model": selected_model,
        "reason": reason,
        "selection_reason": str(selected.get("reason") or reason),
        "domain_id": normalized_domain or None,
        "work_class": normalized_work_class or None,
        "requested_model": normalized_requested_model or None,
        "experimental_model": experimental_model_requested,
        "experimental_model_explicit_only": experimental_model_requested,
        "is_domain_leader": normalized_domain in leader_domains,
        "model_tier": tier.get("tier_key") if tier_applied else None,
        "source_model_tier": tier.get("tier_key") if tier else None,
        "model_tier_label": tier_label or None,
        "reasoning_effort": tier_reasoning_effort or None,
        "selection_posture": selected_posture,
        "availability_window_id": availability_window_id,
        "availability_window_packet_ref": availability_window_packet_ref,
        "selection_override": selection_override,
        "routing_path": ROUTING_RELATIVE_PATH.as_posix(),
        "routing_source_path": routing.get("_routing_source_path"),
        "routing_source_sha256": routing.get("_routing_source_sha256"),
        "routing_source_parity_ok": routing.get("_routing_source_parity_ok"),
        "routing_decision_id": f"route_{routing_decision_sha256[:24]}",
        "routing_decision_sha256": routing_decision_sha256,
        "routing_request_basis": routing_request_basis,
        "routing_decision_basis": routing_decision_basis,
        "binary": str(carrier_cfg.get("binary") or CARRIER_PROBE.get(carrier_id, ("cursor-agent",))[0]),
        "default_model": str(selected.get("model") or primary_model),
        "model_env": tier_env
        or str(
            carrier_cfg.get("model_env")
            or (
                "ION_CODEX_MODEL"
                if carrier_id.startswith("codex")
                else "ION_CLAUDE_MODEL"
                if carrier_id == "claude_cli"
                else "ION_CURSOR_MODEL"
            )
        ),
        "available": bool(selected.get("available")),
        "policy_blocked": selection_policy_blocked,
        "finding": (
            "routing_source_required_for_execution"
            if routing_source_missing
            else "routing_source_json_parity_required_for_execution"
            if routing_source_parity_missing and not routing_source_parity_failed
            else "routing_source_parity_mismatch"
            if routing_source_parity_failed
            else "unsupported_carrier_request"
            if unknown_carrier_request
            else "carrier_disabled_by_routing"
            if disabled_carrier_request
            else "work_class_required_for_leader_execution"
            if missing_work_class_denial
            else "experimental_model_requires_explicit_work_class"
            if experimental_work_class_denial
            else "carrier_constraints_empty_intersection"
            if carrier_constraint_empty
            else "carrier_not_allowed_for_model_tier"
            if explicit_tier_denial
            else "explicit_carrier_not_allowed"
            if explicit_constraint_denial
            else "approved_model_route_required"
            if model_route_missing
            else None
        ),
        "tier_allowed_carriers": sorted(tier_allowed_carriers),
        "caller_allowed_carriers": (
            sorted(caller_allowed_carriers)
            if caller_allowed_carriers is not None
            else None
        ),
        "effective_allowed_carriers": effective_allowed_carriers,
        "work_class_required": leader_execution_requires_work_class,
        "probe_detail": selected.get("probe_detail"),
        "carrier_settings_pause": carrier_settings_pause,
        "carrier_settings_finding": pause_finding,
        "fallback_chain": chain,
        "ranked_candidates": ranked,
        "production_authority": False,
        **execution_tier_fields_for_admission(
            carrier_id,
            selected_model,
            shell_root=shell_root,
            work_class=normalized_work_class or None,
        ),
    }


def is_carrier_whole_quota_exhaustion(
    *,
    usage_signal: str | None = None,
    output_text: str | None = None,
) -> bool:
    """True when provider output indicates whole-CLI quota, not per-model throttling."""

    text = str(output_text or "")
    if re.search(r"weekly\s+limit", text, re.I):
        return True
    if re.search(r"hit\s+your\s+.*limit", text, re.I) and re.search(r"weekly", text, re.I):
        return True
    _ = usage_signal
    return False


def resolve_next_fallback(
    current: Mapping[str, Any],
    *,
    usage_signal: str | None = None,
    output_text: str | None = None,
) -> dict[str, Any] | None:
    if current.get("policy_blocked"):
        return None
    signal = usage_signal
    if not signal and output_text:
        signal = normalize_usage_limit_signal(output_text)
    if not signal:
        return None
    if signal and signal not in USAGE_LIMIT_SIGNALS:
        return None
    chain = current.get("fallback_chain") if isinstance(current.get("fallback_chain"), list) else []
    if not chain:
        return None
    current_carrier = str(current.get("carrier_id") or "")
    current_model = str(current.get("model") or current.get("default_model") or "")
    whole_quota = is_carrier_whole_quota_exhaustion(
        usage_signal=signal,
        output_text=output_text,
    )
    exhausted = {
        str(item)
        for item in (current.get("exhausted_carriers") or [])
        if str(item)
    }
    if whole_quota and current_carrier:
        exhausted.add(current_carrier)
    found = False

    def _row_available(row: Mapping[str, Any]) -> bool:
        return row.get("available") is not False

    def _row_blocked(row: Mapping[str, Any]) -> bool:
        carrier_id = str(row.get("carrier_id") or "")
        if carrier_id in exhausted:
            return True
        if whole_quota and carrier_id == current_carrier:
            return True
        return False

    def _fallback_selection(row: Mapping[str, Any], selection_reason: str) -> dict[str, Any]:
        carrier_id = str(row.get("carrier_id") or "")
        model = str(row.get("model") or "")
        cross_carrier = carrier_id != current_carrier
        nxt = dict(current)
        nxt.update(
            {
                "carrier_id": carrier_id,
                "model": model,
                "default_model": model,
                "selection_reason": selection_reason,
                "fallback_from": {"carrier_id": current_carrier, "model": current_model},
                "usage_signal": signal or "usage_limit",
                "whole_cli_quota_exhaustion": whole_quota,
                "exhausted_carriers": sorted(exhausted),
                "available": bool(row.get("available")),
                "probe_detail": row.get("probe_detail"),
                "binary": CARRIER_PROBE.get(carrier_id, (carrier_id,))[0],
                "model_env": (
                    "ION_CODEX_MODEL"
                    if carrier_id.startswith("codex")
                    else "ION_CLAUDE_MODEL"
                    if carrier_id == "claude_cli"
                    else "ION_CURSOR_MODEL"
                ),
            }
        )
        if cross_carrier or model != current_model:
            nxt.update(
                {
                    "model_tier": None,
                    "model_tier_label": None,
                    "reasoning_effort": None,
                }
            )
        fallback_basis = {
            "parent_routing_decision_id": current.get("routing_decision_id"),
            "from_carrier": current_carrier,
            "from_model": current_model,
            "to_carrier": carrier_id,
            "to_model": model,
            "usage_signal": signal or "usage_limit",
            "whole_cli_quota_exhaustion": whole_quota,
            "exhausted_carriers": sorted(exhausted),
        }
        fallback_sha = hashlib.sha256(
            json.dumps(fallback_basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        nxt["parent_routing_decision_id"] = current.get("routing_decision_id")
        nxt["fallback_decision_id"] = f"fallback_{fallback_sha[:24]}"
        nxt["fallback_decision_sha256"] = fallback_sha
        return nxt

    if whole_quota:
        preferred_equiv = CROSS_CARRIER_MODEL_EQUIVALENTS.get(current_model, {})
        for row in chain:
            if not isinstance(row, Mapping) or _row_blocked(row) or not _row_available(row):
                continue
            carrier_id = str(row.get("carrier_id") or "")
            if carrier_id == current_carrier:
                continue
            if str(row.get("reason") or "") != "cross_carrier_tier_equivalent":
                continue
            preferred_model = preferred_equiv.get(carrier_id)
            if preferred_model and str(row.get("model") or "") != preferred_model:
                continue
            return _fallback_selection(row, "usage_limit_fallback_cross_carrier")
        for row in chain:
            if not isinstance(row, Mapping) or _row_blocked(row) or not _row_available(row):
                continue
            carrier_id = str(row.get("carrier_id") or "")
            if carrier_id == current_carrier:
                continue
            if str(row.get("reason") or "") == "cross_carrier_tier_equivalent":
                return _fallback_selection(row, "usage_limit_fallback_cross_carrier")

    for row in chain:
        if not isinstance(row, Mapping):
            continue
        carrier_id = str(row.get("carrier_id") or "")
        model = str(row.get("model") or "")
        if not found:
            if carrier_id == current_carrier and model == current_model:
                found = True
            continue
        if _row_blocked(row) or not _row_available(row):
            continue
        selection_reason = (
            "usage_limit_fallback_cross_carrier"
            if carrier_id != current_carrier
            else "usage_limit_fallback"
        )
        return _fallback_selection(row, selection_reason)
    for row in chain:
        if not isinstance(row, Mapping):
            continue
        carrier_id = str(row.get("carrier_id") or "")
        model = str(row.get("model") or "")
        if carrier_id == current_carrier and model == current_model:
            continue
        if _row_blocked(row) or not _row_available(row):
            continue
        return _fallback_selection(row, "usage_limit_fallback_cross_carrier")
    return None


def is_usage_limit_failure(*texts: str) -> bool:
    combined = "\n".join(str(text or "") for text in texts)
    signal = normalize_usage_limit_signal(combined)
    return signal in USAGE_LIMIT_SIGNALS


def plan_codex_to_cursor_fallback(
    shell_root: Path,
    *,
    domain_id: str | None = None,
    work_class: str | None = None,
    usage_signal: str = "transient_usage_limit",
) -> dict[str, Any]:
    """Plan next Cursor carrier after Codex usage-limit exhaustion."""

    selection = resolve_execution_selection(
        shell_root,
        domain_id=domain_id,
        work_class=work_class,
        posture="availability_first",
        allowed_carriers=["cursor_cli"],
        execution_surface="prompt_spawn",
    )
    fallback = resolve_next_fallback(selection, usage_signal=usage_signal)
    if fallback is None:
        fallback = selection
    return {
        "schema_id": "ion.cli_model_selection.codex_cursor_fallback_plan.v1",
        "ok": bool(fallback.get("carrier_id") == "cursor_cli"),
        "carrier_id": fallback.get("carrier_id"),
        "model": fallback.get("model") or fallback.get("default_model"),
        "model_env": fallback.get("model_env"),
        "selection_posture": selection.get("selection_posture"),
        "usage_signal": usage_signal,
        "fallback_from": selection.get("carrier_id"),
        "unified_selection": fallback,
        "production_authority": False,
    }


MODEL_CATALOG_RELATIVE_PATH = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.model_routing_and_reasoning_economics/MODEL_CATALOG.candidate.yaml"
)
REDUCED_STATE_POLICY_RELATIVE_PATH = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.model_routing_and_reasoning_economics/REDUCED_STATE_POLICY.candidate.yaml"
)

OPERATION_MODES = frozenset({"full", "reduced", "premium_only"})
EXECUTION_TIERS = frozenset({"full", "reduced"})

# Default reduced-tier tagging when catalog file is absent (mirrors MODEL_CATALOG.candidate.yaml).
DEFAULT_REDUCED_TIER_MODELS: dict[str, frozenset[str]] = {
    "cursor_cli": frozenset({"composer-2.5", "composer-2.5-fast"}),
    "claude_cli": frozenset({"claude-fable-5"}),
    "codex_cli": frozenset(),
}


def enumerate_carrier_models_from_code() -> dict[str, tuple[str, ...]]:
    """Snapshot of execution-boundary models per carrier from this module (not memory)."""

    return {
        carrier_id: execution_models_for_carrier(carrier_id)
        for carrier_id in ("cursor_cli", "claude_cli", "codex_cli")
    }


def load_model_catalog(shell_root: Path) -> dict[str, Any]:
    path = shell_root / MODEL_CATALOG_RELATIVE_PATH
    data = _read_yaml(path)
    if data:
        data = dict(data)
        data["_catalog_path"] = MODEL_CATALOG_RELATIVE_PATH.as_posix()
        if path.is_file():
            data["_catalog_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return data


def reduced_tier_models_for_carrier(
    shell_root: Path | None,
    carrier_id: str,
) -> frozenset[str]:
    carrier = str(carrier_id or "").strip()
    if shell_root is not None:
        catalog = load_model_catalog(shell_root)
        carriers = catalog.get("carriers")
        if isinstance(carriers, Mapping):
            block = carriers.get(carrier)
            if isinstance(block, Mapping):
                reduced = block.get("reduced_tier_models") or []
                if isinstance(reduced, list) and reduced:
                    return frozenset(str(item).strip() for item in reduced if str(item).strip())
    return DEFAULT_REDUCED_TIER_MODELS.get(carrier, frozenset())


def resolve_operation_mode(
    *,
    intent_operation_mode: str | None = None,
    env_value: str | None = None,
) -> str:
    for candidate in (intent_operation_mode, env_value, "full"):
        mode = str(candidate or "").strip().lower()
        if mode in OPERATION_MODES:
            return mode
    return "full"


def derive_execution_tier(
    carrier_id: str,
    model_id: str,
    *,
    shell_root: Path | None = None,
    operation_mode: str = "full",
    work_class: str | None = None,
) -> str:
    """Tag runs as full or reduced from catalog + admitted model (findings-only downstream)."""

    _ = work_class
    mode = resolve_operation_mode(intent_operation_mode=operation_mode)
    model = str(model_id or "").strip()
    carrier = str(carrier_id or "").strip()
    if mode == "premium_only":
        return "full"
    reduced_models = reduced_tier_models_for_carrier(shell_root, carrier)
    if model in reduced_models:
        return "reduced"
    if mode == "reduced" and carrier == "cursor_cli" and model in reduced_models:
        return "reduced"
    return "full"


def execution_tier_fields_for_admission(
    carrier_id: str,
    model_id: str,
    *,
    shell_root: Path | None = None,
    operation_mode: str | None = None,
    work_class: str | None = None,
) -> dict[str, str]:
    mode = resolve_operation_mode(intent_operation_mode=operation_mode)
    tier = derive_execution_tier(
        carrier_id,
        model_id,
        shell_root=shell_root,
        operation_mode=mode,
        work_class=work_class,
    )
    return {"operation_mode": mode, "execution_tier": tier}


def selection_status(shell_root: Path) -> dict[str, Any]:
    routing = load_unified_routing(shell_root)
    tiers = routing.get("model_tiers") if isinstance(routing.get("model_tiers"), Mapping) else {}
    return {
        "schema_id": "ion.cli_model_selection_status.v1",
        "routing_path": ROUTING_RELATIVE_PATH.as_posix(),
        "routing_present": (shell_root / ROUTING_RELATIVE_PATH).is_file(),
        "routing_schema": routing.get("schema_id"),
        "default_carrier": routing.get("default_carrier"),
        "leader_carrier": routing.get("leader_carrier"),
        "carrier_fallback_order": _carrier_fallback_order(routing),
        "disabled_carriers": sorted(_disabled_carriers(routing)),
        "selection_posture": _selection_posture(routing, None),
        "leader_domain_count": len(routing.get("leader_domains") or []),
        "model_tier_keys": list(tiers.keys())[:12],
        "production_authority": False,
    }

# ION R3 explicit-only Claude execution allowlist
# Automatic ladders remain governed by the unchanged routing mirrors.
EXPLICIT_ONLY_CLAUDE_EXECUTION_MODELS = frozenset({"claude-fable-5"})
CLAUDE_MODEL_ALIASES_REQUIRING_EXPLICIT_ID = frozenset(
    {
        "opus",
        "fable",
        "sonnet",
        "haiku",
        "opus-5",
        "fable-5",
        "sonnet-5",
        "claude-opus",
        "claude-fable",
        "claude-sonnet",
        "claude-haiku",
    }
)
def is_explicit_only_claude_model(model: str) -> bool:
    return str(model).strip() in EXPLICIT_ONLY_CLAUDE_EXECUTION_MODELS
