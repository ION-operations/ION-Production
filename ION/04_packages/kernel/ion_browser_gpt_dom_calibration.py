"""Browser GPT DOM selector calibration artifacts.

This module owns the local, receipt-backed selector profile lane for the
ChatGPT web page. It records observed selectors as candidate artifacts only; it
does not grant browser send authority or accepted ION state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.browser_gpt_dom_calibration.v1"
PROFILE_SCHEMA_ID = "ion.browser_gpt_dom_selector_profile.v1"
HEALTH_SCHEMA_ID = "ion.browser_gpt_dom_health.v1"
RECEIPT_SCHEMA_ID = "ion.browser_gpt_dom_calibration_receipt.v1"
SUMMARY_SCHEMA_ID = "ion.browser_gpt_dom_profile_summary.v1"
TWIN_SCHEMA_ID = "ion.browser_gpt_dom_twin.v1"

BASE_DIR = Path("ION/05_context/current/browser_gpt_dom_profiles")
PROFILES_DIR = BASE_DIR / "profiles"
RECEIPTS_DIR = BASE_DIR / "receipts"
SCHEMAS_DIR = BASE_DIR / "schemas"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
PROBE_SNAPSHOTS_DIR = BASE_DIR / "probe_snapshots"
RUNTIME_DIR = BASE_DIR / "runtime"
INDEX_PATH = BASE_DIR / "INDEX.json"
LATEST_PROFILE_PATH = BASE_DIR / "latest.selector_profile.json"
LATEST_HEALTH_PATH = BASE_DIR / "latest.dom_health.json"
LATEST_PROBE_SNAPSHOT_PATH = PROBE_SNAPSHOTS_DIR / "latest_probe_snapshot.json"
LATEST_DEGRADED_PROBE_SNAPSHOT_PATH = PROBE_SNAPSHOTS_DIR / "latest_degraded_probe_snapshot.json"
CHATOPS_NATIVE_DOM_LATEST_PATH = Path("ION/05_context/current/chatops_bridge/runtime/native_dom_snapshots/latest_native_dom_snapshot.json")
CHATOPS_NATIVE_DOM_SNAPSHOTS_DIR = Path("ION/05_context/current/chatops_bridge/runtime/native_dom_snapshots")
NEEDS_ROUTED_NATIVE_DOM_SNAPSHOT_GLOB = "Needs_Routed/ion_native_dom_snapshot_*.json"

DEFAULT_ORIGIN = "https://chatgpt.com"
DEFAULT_PROFILE_ID = "chatgpt_web_20260525_v1"
DEFAULT_DOM_PROBE_EXTENSION_ROOT = Path("browser_extension/browser_gpt_dom_probe/OPERATOR_FINAL")
EXPECTED_CHATOPS_PROBE_BUILD_MARKER = "browser_gpt_dom_auto_probe_20260526T0212Z"

SURFACE_SPECS: dict[str, dict[str, Any]] = {
    "composer": {
        "required": True,
        "kind": "input",
        "hotkeys": ["Shift+Enter inserts newline", "/ opens slash commands"],
        "selectors": [
            "#prompt-textarea",
            "textarea[data-testid='composer-text-input']",
            "[data-testid='composer'] div[contenteditable='true']",
            "[data-testid='composer'] textarea",
            "form textarea",
            "div[contenteditable='true'][data-testid='composer-text-input']",
            "form div[contenteditable='true']",
        ],
        "validated_by": ["visible", "focus", "optional_insert_text_readback"],
    },
    "send_button": {
        "required": True,
        "kind": "button",
        "hotkeys": ["Enter when composer has a draft"],
        "selectors": [
            "[data-testid='send-button']",
            "button[aria-label*='Send' i]",
            "form button[type='submit']",
            "button[data-testid*='send' i]",
        ],
        "validated_by": ["visible", "enabled_state_observed", "click_dry_run_blocked"],
    },
    "stop_button": {
        "required": False,
        "kind": "button",
        "selectors": [
            "[data-testid*='stop' i]",
            "button[aria-label*='Stop' i]",
            "button[aria-label*='stop generating' i]",
        ],
        "validated_by": ["visible_when_streaming"],
    },
    "new_chat_button": {
        "required": False,
        "kind": "button",
        "selectors": [
            "a[aria-label*='New chat' i]",
            "button[aria-label*='New chat' i]",
            "[data-testid*='new-chat' i]",
        ],
        "validated_by": ["visible"],
    },
    "message_list": {
        "required": True,
        "kind": "list",
        "selectors": [
            "main [data-testid^='conversation-turn']",
            "[data-message-author-role]",
            "main article",
            "main",
        ],
        "validated_by": ["visible_messages_present"],
    },
    "latest_assistant_message": {
        "required": False,
        "kind": "message",
        "selectors": [
            "[data-message-author-role='assistant']",
            "[data-testid^='conversation-turn'] [data-message-author-role='assistant']",
            "article",
        ],
        "validated_by": ["visible", "role_hint"],
    },
    "latest_user_message": {
        "required": False,
        "kind": "message",
        "selectors": [
            "[data-message-author-role='user']",
            "[data-testid^='conversation-turn'] [data-message-author-role='user']",
        ],
        "validated_by": ["visible", "role_hint"],
    },
    "file_attach_button": {
        "required": False,
        "kind": "button",
        "hotkeys": ["Ctrl+U"],
        "selectors": [
            "button[aria-label*='Attach' i]",
            "button[aria-label*='Upload' i]",
            "button[aria-label*='Add' i]",
            "[data-testid*='attach' i]",
        ],
        "validated_by": ["visible"],
    },
    "file_upload_menu_option": {
        "required": False,
        "kind": "menuitem",
        "hotkeys": ["Ctrl+U"],
        "selectors": [
            "[role='menuitem']:has-text('Upload')",
            "[role='option']:has-text('Upload')",
            "button:has-text('Upload')",
            "button:has-text('Computer')",
            "[data-testid*='upload' i]",
        ],
        "validated_by": ["visible"],
    },
    "voice_mic_button": {
        "required": False,
        "kind": "button",
        "hotkeys": [],
        "selectors": [
            "button[aria-label*='Voice' i]",
            "button[aria-label*='Mic' i]",
            "button[aria-label*='Microphone' i]",
            "button[aria-label*='Dictate' i]",
            "[data-testid*='voice' i]",
        ],
        "validated_by": ["visible"],
    },
    "model_picker": {
        "required": False,
        "kind": "button",
        "selectors": [
            "button[aria-label*='model' i]",
            "button:has-text('GPT')",
            "[data-testid*='model' i]",
            "[role='button'][aria-label*='model' i]",
        ],
        "validated_by": ["visible"],
    },
    "model_menu_option": {
        "required": False,
        "kind": "menuitem",
        "selectors": [
            "[role='option']:has-text('GPT')",
            "[role='menuitem']:has-text('GPT')",
            "[role='menuitemradio']:has-text('GPT')",
            "button:has-text('GPT')",
            "[data-testid*='model' i]",
        ],
        "validated_by": ["visible"],
    },
    "thinking_mode_control": {
        "required": False,
        "kind": "button",
        "selectors": [
            "button[aria-label*='Think' i]",
            "button[aria-label*='Reason' i]",
            "button:has-text('Think')",
            "button:has-text('Reason')",
            "button:has-text('Deep research')",
        ],
        "validated_by": ["visible"],
    },
    "thinking_effort_option": {
        "required": False,
        "kind": "menuitem",
        "selectors": [
            "[role='option']:has-text('Auto')",
            "[role='menuitem']:has-text('Auto')",
            "[role='menuitemradio']:has-text('Auto')",
            "button:has-text('Fast')",
            "button:has-text('High')",
        ],
        "validated_by": ["visible"],
    },
    "tools_menu_opener": {
        "required": False,
        "kind": "button",
        "selectors": [
            "button[aria-label*='Tools' i]",
            "button[aria-label*='More' i]",
            "button[aria-label*='Add' i]",
            "[data-testid*='tools' i]",
        ],
        "validated_by": ["visible"],
    },
    "tools_menu_option": {
        "required": False,
        "kind": "menuitem",
        "selectors": [
            "[role='menuitem']:has-text('Search')",
            "[role='menuitem']:has-text('Image')",
            "[role='option']:has-text('Search')",
            "button:has-text('Search')",
        ],
        "validated_by": ["visible"],
    },
    "slash_command_menu": {
        "required": False,
        "kind": "composer_command_menu",
        "hotkeys": ["/"],
        "selectors": [
            "[role='listbox']",
            "[role='menu']",
            "[cmdk-list]",
            "[data-radix-popper-content-wrapper]",
        ],
        "validated_by": ["visible_after_slash_in_composer"],
    },
    "slash_command_option": {
        "required": False,
        "kind": "composer_command_option",
        "hotkeys": ["/ then command name"],
        "selectors": [
            "[role='option']",
            "[role='menuitem']",
            "[cmdk-item]",
            "button",
        ],
        "validated_by": ["visible_after_slash_in_composer"],
    },
    "left_sidebar_toggle": {
        "required": False,
        "kind": "button",
        "selectors": [
            "button[aria-label='Open sidebar']",
            "button[aria-controls='stage-slideover-sidebar']",
            "button[aria-label*='sidebar' i]",
        ],
        "validated_by": ["visible"],
    },
    "left_drawer": {
        "required": False,
        "kind": "drawer",
        "selectors": [
            "#stage-slideover-sidebar",
            "[aria-controls='stage-slideover-sidebar']",
        ],
        "validated_by": ["visible_or_known_host"],
    },
    "drawer_surface": {
        "required": False,
        "kind": "drawer",
        "selectors": [
            "[role='dialog']",
            "[data-radix-popper-content-wrapper]",
            "aside",
        ],
        "validated_by": ["visible_or_known_host"],
    },
    "native_action_cards": {
        "required": False,
        "kind": "card",
        "selectors": [
            "[role='dialog'] button",
            "[data-testid*='confirmation' i]",
            "button",
        ],
        "validated_by": ["detect_only"],
    },
}

PLAYWRIGHT_AUTO_INTERACTIONS: tuple[dict[str, Any], ...] = (
    {
        "phase": "sidebar_open",
        "surface_id": "left_sidebar_toggle",
        "description": "Open ChatGPT sidebar/drawer for observation.",
        "allow_file_chooser": False,
    },
    {
        "phase": "attach_menu_open",
        "surface_id": "file_attach_button",
        "description": "Open attach/upload surface or record file chooser trigger.",
        "allow_file_chooser": True,
    },
    {
        "phase": "tools_menu_open",
        "surface_id": "tools_menu_opener",
        "description": "Open ChatGPT tools/menu surface.",
        "allow_file_chooser": False,
    },
    {
        "phase": "model_menu_open",
        "surface_id": "model_picker",
        "description": "Open model picker menu.",
        "allow_file_chooser": False,
    },
    {
        "phase": "thinking_menu_open",
        "surface_id": "thinking_mode_control",
        "description": "Open thinking/reasoning effort menu.",
        "allow_file_chooser": False,
    },
)

PROBE_PHASE_DEPENDENCIES: dict[str, dict[str, str]] = {
    "file_upload_menu_option": {
        "phase": "attach_menu_open",
        "opener_surface_id": "file_attach_button",
        "instruction": "Open the attach/add-files control, then capture the visible upload menu.",
    },
    "tools_menu_option": {
        "phase": "tools_menu_open",
        "opener_surface_id": "tools_menu_opener",
        "instruction": "Open the tools menu, then capture the visible tool options.",
    },
    "model_menu_option": {
        "phase": "model_menu_open",
        "opener_surface_id": "model_picker",
        "instruction": "Open the model picker, then capture the visible model options.",
    },
    "thinking_effort_option": {
        "phase": "thinking_menu_open",
        "opener_surface_id": "thinking_mode_control",
        "instruction": "Open the thinking/reasoning control, then capture the visible effort choices.",
    },
    "slash_command_option": {
        "phase": "slash_command_menu_open",
        "opener_surface_id": "composer",
        "instruction": "Focus the composer, type '/', then capture the visible slash command option.",
    },
    "drawer_surface": {
        "phase": "drawer_open",
        "opener_surface_id": "left_sidebar_toggle",
        "instruction": "Open the sidebar or drawer, then capture the visible drawer surface.",
    },
}

TWIN_CONTROL_ORDER: tuple[str, ...] = (
    "new_chat_button",
    "left_sidebar_toggle",
    "model_picker",
    "model_menu_option",
    "thinking_mode_control",
    "thinking_effort_option",
    "tools_menu_opener",
    "tools_menu_option",
    "slash_command_menu",
    "slash_command_option",
    "file_attach_button",
    "file_upload_menu_option",
    "voice_mic_button",
    "stop_button",
    "send_button",
    "native_action_cards",
)

TWIN_CONTROL_LABELS: dict[str, str] = {
    "new_chat_button": "new chat",
    "left_sidebar_toggle": "sidebar",
    "model_picker": "model",
    "model_menu_option": "model option",
    "thinking_mode_control": "thinking",
    "thinking_effort_option": "effort",
    "tools_menu_opener": "tools",
    "tools_menu_option": "tool option",
    "slash_command_menu": "slash menu",
    "slash_command_option": "slash command",
    "file_attach_button": "upload",
    "file_upload_menu_option": "upload option",
    "voice_mic_button": "voice",
    "stop_button": "stop",
    "send_button": "send",
    "native_action_cards": "action card",
}

TWIN_SURFACE_GROUPS: tuple[dict[str, Any], ...] = (
    {"group_id": "primary", "surface_ids": ["new_chat_button", "left_sidebar_toggle", "model_picker"]},
    {"group_id": "composer_tools", "surface_ids": ["file_attach_button", "tools_menu_opener", "thinking_mode_control", "voice_mic_button", "slash_command_menu"]},
    {"group_id": "menus_drawers", "surface_ids": ["model_menu_option", "thinking_effort_option", "tools_menu_option", "file_upload_menu_option", "slash_command_option", "left_drawer", "drawer_surface"]},
    {"group_id": "conversation", "surface_ids": ["message_list", "latest_user_message", "latest_assistant_message", "stop_button", "send_button"]},
)

PROFILE_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": PROFILE_SCHEMA_ID,
    "type": "object",
    "required": ["schema_id", "profile_id", "origin", "surfaces", "authority"],
    "properties": {
        "schema_id": {"const": PROFILE_SCHEMA_ID},
        "profile_id": {"type": "string"},
        "origin": {"type": "string"},
        "status": {"type": "string"},
        "surfaces": {"type": "object"},
        "authority": {"type": "object"},
    },
}

HEALTH_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": HEALTH_SCHEMA_ID,
    "type": "object",
    "required": ["schema_id", "status", "surfaces", "authority"],
    "properties": {
        "schema_id": {"const": HEALTH_SCHEMA_ID},
        "status": {"type": "string"},
        "surfaces": {"type": "object"},
        "authority": {"type": "object"},
    },
}

RECEIPT_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": RECEIPT_SCHEMA_ID,
    "type": "object",
    "required": ["schema_id", "receipt_id", "status", "artifacts", "authority"],
    "properties": {
        "schema_id": {"const": RECEIPT_SCHEMA_ID},
        "receipt_id": {"type": "string"},
        "status": {"type": "string"},
        "artifacts": {"type": "object"},
        "authority": {"type": "object"},
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_slug(value: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    return "_".join(part for part in normalized.split("_") if part)[:96] or "browser_gpt_profile"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception as exc:  # pragma: no cover - projection must stay fail-soft.
        return {"_read_error": str(exc), "_path": path.as_posix()}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def default_dom_probe_extension_root(root: str | Path = ".") -> Path | None:
    """Return the clean DOM Probe extension path when the operator artifact exists."""

    shell_root = Path(root).resolve()
    candidate = shell_root / DEFAULT_DOM_PROBE_EXTENSION_ROOT
    if (candidate / "manifest.json").is_file() and (candidate / "content.js").is_file():
        return candidate
    return None


def default_authority() -> dict[str, Any]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
        "cookie_read_authority": False,
        "credential_extraction_authority": False,
        "silent_send_authority": False,
        "approved_send_required": True,
        "source_posture": "candidate_observed_dom_profile",
    }


def browser_gpt_detected_selector_is_acceptable(surface_id: str, item: Mapping[str, Any]) -> bool:
    """Reject obvious heuristic false positives from native DOM snapshots."""

    selector = str(item.get("selector") or "").strip()
    if not selector:
        return False
    spec = SURFACE_SPECS.get(surface_id, {})
    kind = str(spec.get("kind") or "")
    tag = str(item.get("tag") or "").lower()
    attrs = item.get("attrs") if isinstance(item.get("attrs"), Mapping) else {}
    role = str(item.get("role") or attrs.get("role") or "").lower()
    selector_lower = selector.lower()
    label = str(item.get("label") or attrs.get("aria-label") or "").lower()

    if surface_id == "send_button":
        haystack = " ".join([selector_lower, label, role, tag])
        if any(term in haystack for term in ["voice", "dictation", "microphone", "mic"]):
            return False
        return any(
            term in haystack
            for term in [
                "composer-submit",
                "send-button",
                "aria-label=\"send",
                "aria-label='send",
                "send prompt",
                "send message",
            ]
        ) or label.startswith("send")

    if surface_id == "composer":
        return (
            "#prompt-textarea" in selector_lower
            or tag == "textarea"
            or role == "textbox"
            or "contenteditable" in selector_lower
            or "prompt" in selector_lower
        )
    if kind == "button":
        return (
            tag == "button"
            or role == "button"
            or selector_lower.startswith("button")
            or "button" in selector_lower
            or "btn" in selector_lower
            or "[role='button" in selector_lower
            or '[role="button' in selector_lower
            or "button" in label
        )
    if kind == "menuitem":
        return (
            "menuitem" in role
            or role == "option"
            or "[role='menuitem" in selector_lower
            or '[role="menuitem' in selector_lower
            or "[role='option" in selector_lower
            or '[role="option' in selector_lower
            or selector_lower.startswith("button")
        )
    return True


def prior_native_dom_evidence(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).resolve()
    candidates: list[Path] = []
    latest = shell_root / CHATOPS_NATIVE_DOM_LATEST_PATH
    if latest.exists():
        candidates.append(latest)
    snapshot_dir = shell_root / CHATOPS_NATIVE_DOM_SNAPSHOTS_DIR
    if snapshot_dir.exists():
        candidates.extend(sorted(snapshot_dir.glob("ion_native_dom_snapshot_*.json"), key=lambda path: path.stat().st_mtime, reverse=True))
    candidates.extend(sorted(shell_root.glob(NEEDS_ROUTED_NATIVE_DOM_SNAPSHOT_GLOB), key=lambda path: path.stat().st_mtime, reverse=True))

    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve(strict=False)
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        payload = read_json(path)
        if not payload:
            continue
        snapshot = payload.get("snapshot") if isinstance(payload.get("snapshot"), Mapping) else payload
        if not isinstance(snapshot, Mapping):
            continue
        detected = snapshot.get("detected") if isinstance(snapshot.get("detected"), Mapping) else {}
        ion_state = snapshot.get("ion_state") if isinstance(snapshot.get("ion_state"), Mapping) else {}
        browser_gpt_dom = snapshot.get("browser_gpt_dom") if isinstance(snapshot.get("browser_gpt_dom"), Mapping) else {}
        browser_gpt_detected = browser_gpt_dom.get("detected") if isinstance(browser_gpt_dom.get("detected"), Mapping) else {}
        browser_gpt_selectors: dict[str, Any] = {}
        browser_gpt_presence = dict(browser_gpt_dom.get("required_surface_presence", {})) if isinstance(browser_gpt_dom.get("required_surface_presence"), Mapping) else {}
        for key, value in browser_gpt_detected.items():
            if isinstance(value, Mapping) and browser_gpt_detected_selector_is_acceptable(str(key), value):
                browser_gpt_selectors[str(key)] = value.get("selector")
            if key == "message_list" and isinstance(value, Mapping):
                anchors = value.get("anchors") if isinstance(value.get("anchors"), list) else []
                anchor_selectors = [anchor.get("selector") for anchor in anchors if isinstance(anchor, Mapping) and anchor.get("selector")]
                if anchor_selectors:
                    browser_gpt_selectors[str(key)] = anchor_selectors[0]
        operator_picks = snapshot.get("browser_gpt_operator_picks") if isinstance(snapshot.get("browser_gpt_operator_picks"), Mapping) else {}
        operator_targets = operator_picks.get("targets") if isinstance(operator_picks.get("targets"), Mapping) else {}
        operator_selectors: dict[str, Any] = {}
        operator_hotkeys: dict[str, list[str]] = {}
        for key, value in operator_targets.items():
            surface_key = str(key)
            if isinstance(value, Mapping) and isinstance(value.get("hotkeys"), list):
                hotkeys = [str(item).strip() for item in value.get("hotkeys", []) if str(item).strip()]
                if hotkeys:
                    operator_hotkeys[surface_key] = hotkeys
            if isinstance(value, Mapping) and value.get("found") is True and value.get("selector"):
                if surface_key == "send_button" and not browser_gpt_detected_selector_is_acceptable(surface_key, value):
                    continue
                operator_selectors[surface_key] = value.get("selector")
                if key in {"composer", "send_button", "message_list"}:
                    browser_gpt_presence[str(key)] = True
        for surface_key, selector in operator_selectors.items():
            if surface_key in {"composer", "send_button"} and browser_gpt_selectors.get(surface_key):
                continue
            browser_gpt_selectors[surface_key] = selector
        selectors: dict[str, Any] = {}
        for key, value in detected.items():
            if isinstance(value, Mapping) and value.get("selector"):
                selectors[str(key)] = value.get("selector")
        source_kind = "daemon_latest_native_dom_snapshot" if path == latest else "native_dom_snapshot_artifact"
        if path.match("Needs_Routed/ion_native_dom_snapshot_*.json"):
            source_kind = "needs_routed_native_dom_snapshot"
        return {
            "schema_id": "ion.browser_gpt_dom_prior_live_evidence.v1",
            "status": "present",
            "source_kind": source_kind,
            "source_path": repo_rel(shell_root, path),
            "captured_at": snapshot.get("captured_at"),
            "url": snapshot.get("url"),
            "detected_keys": sorted(str(key) for key in detected.keys()),
            "selectors": selectors,
            "browser_gpt_status": browser_gpt_dom.get("status"),
            "browser_gpt_required_surface_presence": browser_gpt_presence,
            "browser_gpt_selectors": browser_gpt_selectors,
            "browser_gpt_operator_selectors": operator_selectors,
            "browser_gpt_operator_hotkeys": operator_hotkeys,
            "browser_gpt_operator_pick_count": len(operator_selectors),
            "native_left_mode": ion_state.get("native_left_mode"),
            "native_drawer_is_open": ion_state.get("native_drawer_is_open"),
            "native_drawer_open_panels": ion_state.get("native_drawer_open_panels"),
            "authority": default_authority(),
        }
    return {
        "schema_id": "ion.browser_gpt_dom_prior_live_evidence.v1",
        "status": "missing",
        "checked_paths": [
            CHATOPS_NATIVE_DOM_LATEST_PATH.as_posix(),
            CHATOPS_NATIVE_DOM_SNAPSHOTS_DIR.as_posix(),
            NEEDS_ROUTED_NATIVE_DOM_SNAPSHOT_GLOB,
        ],
        "authority": default_authority(),
    }


def surface_candidates_from_prior_native_dom_evidence(evidence: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    selectors = evidence.get("browser_gpt_selectors") if isinstance(evidence.get("browser_gpt_selectors"), Mapping) else {}
    hotkeys = evidence.get("browser_gpt_operator_hotkeys") if isinstance(evidence.get("browser_gpt_operator_hotkeys"), Mapping) else {}
    required_presence = evidence.get("browser_gpt_required_surface_presence") if isinstance(evidence.get("browser_gpt_required_surface_presence"), Mapping) else {}
    candidates: dict[str, list[dict[str, Any]]] = {}
    if selectors.get("composer") and required_presence.get("composer") is True:
        candidates["composer"] = [{
            "selector": selectors.get("composer"),
            "score": 88,
            "tag": "unknown",
            "role": "composer",
            "label": "",
            "rect": {},
            "unique": None,
            "validated_by": ["native_dom_snapshot", "visible", "composer_present"],
        }]
    if selectors.get("send_button") and required_presence.get("send_button") is True:
        candidates["send_button"] = [{
            "selector": selectors.get("send_button"),
            "score": 86,
            "tag": "button",
            "role": "send_button",
            "label": "",
            "rect": {},
            "unique": None,
            "validated_by": ["native_dom_snapshot", "visible", "send_button_present"],
        }]
    if selectors.get("message_list") and required_presence.get("message_list") is True:
        candidates["message_list"] = [{
            "selector": selectors.get("message_list"),
            "score": 82,
            "tag": "unknown",
            "role": "message_list",
            "label": "",
            "rect": {},
            "unique": None,
            "validated_by": ["native_dom_snapshot", "visible_messages_present"],
        }]
    for surface_id in [
        "stop_button",
        "latest_assistant_message",
        "latest_user_message",
        "file_attach_button",
        "file_upload_menu_option",
        "voice_mic_button",
        "model_picker",
        "model_menu_option",
        "thinking_mode_control",
        "thinking_effort_option",
        "tools_menu_opener",
        "tools_menu_option",
        "slash_command_menu",
        "slash_command_option",
        "new_chat_button",
        "left_sidebar_toggle",
        "left_drawer",
        "drawer_surface",
        "native_action_cards",
    ]:
        if selectors.get(surface_id):
            candidates[surface_id] = [{
                "selector": selectors.get(surface_id),
                "score": 72,
                "tag": "unknown",
                "role": surface_id,
                "label": "",
                "rect": {},
                "unique": None,
                "hotkeys": list(hotkeys.get(surface_id, [])) if isinstance(hotkeys.get(surface_id), list) else list(SURFACE_SPECS.get(surface_id, {}).get("hotkeys", [])),
                "validated_by": ["native_dom_snapshot", "observed"],
            }]
    return candidates


def _safe_probe_snapshot_filename(value: Any, captured_at: str) -> str:
    raw = Path(str(value or "")).name.strip()
    raw = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in raw).strip("._-")
    if not raw:
        token = "".join(ch for ch in captured_at if ch.isalnum())[:18]
        raw = f"ion_browser_gpt_dom_probe_snapshot_{token or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    if not raw.endswith(".json"):
        raw = f"{raw}.json"
    return raw[:180]


def _probe_phase(snapshot: Mapping[str, Any]) -> str:
    phase_sweep = snapshot.get("phase_sweep") if isinstance(snapshot.get("phase_sweep"), Mapping) else {}
    return str(phase_sweep.get("phase") or snapshot.get("capture_reason") or "latest_probe")


def probe_page_state_from_snapshot(snapshot: Mapping[str, Any]) -> str:
    health = snapshot.get("dom_health") if isinstance(snapshot.get("dom_health"), Mapping) else {}
    messages = snapshot.get("visible_messages") if isinstance(snapshot.get("visible_messages"), list) else []
    if messages:
        return "conversation_visible"
    if health.get("send_available") is True:
        return "draft_ready"
    if health.get("composer_present") is True:
        return "fresh_empty_chat"
    return "unknown"


def _probe_candidate(surface_id: str, item: Mapping[str, Any], *, score: int = 84, source: str = "probe_snapshot", phase: str = "latest_probe") -> dict[str, Any]:
    selector = str(item.get("selector") or "").strip()
    return {
        "selector": selector,
        "score": score,
        "tag": str(item.get("tag") or "unknown"),
        "role": str(item.get("role") or ""),
        "label": str(item.get("aria_label") or item.get("accessible_name_hint") or item.get("text_preview") or "")[:180],
        "rect": dict(item.get("rect", {})) if isinstance(item.get("rect"), Mapping) else {},
        "unique": None,
        "source": source,
        "phase": phase,
        "validated_by": ["probe_snapshot", "visible"] + (["operator_pick"] if source == "operator_pick" else []),
        "hotkeys": list(item.get("hotkeys", [])) if isinstance(item.get("hotkeys"), list) else [],
        "text_sha256": sha256_text(str(item.get("text_preview") or "")) if item.get("text_preview") else None,
    }


def probe_control_candidate_is_safe(surface_id: str, item: Mapping[str, Any], snapshot: Mapping[str, Any]) -> bool:
    haystack = " ".join(
        str(item.get(key) or "")
        for key in ["selector", "tag", "role", "aria_label", "data_testid", "text_preview", "source_surface"]
    ).lower()
    health = snapshot.get("dom_health") if isinstance(snapshot.get("dom_health"), Mapping) else {}
    extension_owned_terms = [
        "queued item",
        "queued message",
        "ion queue",
        "chatops",
        "ion-chatops",
        "browser gpt calibration",
    ]
    if any(term in haystack for term in extension_owned_terms):
        return False
    if surface_id == "send_button":
        explicit_send_marker = any(
            term in haystack
            for term in [
                "composer-submit",
                "send-button",
                "data-testid=\"send",
                "data-testid='send",
                "aria-label=\"send",
                "aria-label='send",
                "send prompt",
                "send message",
                "send button",
            ]
        ) or bool(
            str(item.get("aria_label") or "").strip().lower().startswith("send")
            or str(item.get("text_preview") or "").strip().lower() == "send"
            or str(item.get("data_testid") or "").strip().lower().startswith("send")
        )
        if not explicit_send_marker:
            return False
        if "queue" in haystack or "queued" in haystack:
            return False
        controls = snapshot.get("visible_controls") if isinstance(snapshot.get("visible_controls"), list) else []
        visible_composer = any(
            isinstance(control, Mapping)
            and (
                "#prompt-textarea" in " ".join(str(control.get(key) or "") for key in ["selector", "role", "data_testid"]).lower()
                or str(control.get("role") or "").lower() == "textbox"
            )
            for control in controls
        )
        if not health.get("composer_present") and not visible_composer and "#composer-submit-button" not in haystack and "send-button" not in haystack:
            return False
    if surface_id == "model_picker" and any(term in haystack for term in ["drawer", "sidebar", "minimize", "share"]):
        return False
    if surface_id in {"model_menu_option", "tools_menu_opener", "tools_menu_option"} and any(
        term in haystack for term in ["chatgpt drawer", "agent drawer", "open agent drawer", "minimize", "ion-native"]
    ):
        return False
    if surface_id == "slash_command_option":
        label = " ".join(str(item.get(key) or "") for key in ["aria_label", "text_preview"]).strip().lower()
        selector = str(item.get("selector") or "").lower()
        if not (label.startswith("/") or "slash command" in label or "cmdk" in selector or "cmdk" in haystack):
            return False
    if surface_id == "slash_command_menu":
        selector = str(item.get("selector") or "").lower()
        if not ("cmdk" in selector or "listbox" in selector or "slash command" in haystack):
            return False
    return True


def probe_surface_id_from_control(item: Mapping[str, Any]) -> str:
    surface_aliases = {
        "composer_textbox": "composer",
        "send_button": "send_button",
        "stop_generating_button": "stop_button",
        "attach_upload_opener": "file_attach_button",
        "upload_popup_item": "file_upload_menu_option",
        "tools_menu_opener": "tools_menu_opener",
        "tools_menu_option": "tools_menu_option",
        "slash_command_menu": "slash_command_menu",
        "slash_command_option": "slash_command_option",
        "model_picker_opener": "model_picker",
        "model_menu_option": "model_menu_option",
        "thinking_control_opener": "thinking_mode_control",
        "thinking_effort_option": "thinking_effort_option",
        "left_sidebar_toggle": "left_sidebar_toggle",
        "left_drawer_surface": "left_drawer",
        "new_chat_button": "new_chat_button",
        "message_list": "message_list",
        "latest_user_message": "latest_user_message",
        "latest_assistant_message": "latest_assistant_message",
        "native_action_card": "native_action_cards",
    }
    for key in ["source_surface", "target_id", "role"]:
        raw = str(item.get(key) or "").strip()
        if raw in SURFACE_SPECS:
            return raw
        if surface_aliases.get(raw):
            return surface_aliases[raw]

    haystack = " ".join(str(item.get(key) or "") for key in ["selector", "tag", "role", "aria_label", "data_testid", "text_preview"]).lower()
    tag = str(item.get("tag") or "").lower()
    role = str(item.get("role") or "").lower()
    if "#prompt-textarea" in haystack or tag == "textarea" or role == "textbox" or "contenteditable" in haystack:
        return "composer"
    if "send" in haystack and ("button" in tag or role == "button"):
        return "send_button"
    if any(term in haystack for term in ["attach", "upload", "composer-plus", "add files"]):
        return "file_attach_button"
    if any(term in haystack for term in ["model", "gpt", "model-switcher"]):
        return "model_picker"
    if any(term in haystack for term in ["think", "reason"]):
        return "thinking_mode_control"
    if any(term in haystack for term in ["slash command", "prompt starter", "cmdk"]):
        return "slash_command_option"
    if "sidebar" in haystack:
        return "left_sidebar_toggle"
    if any(term in haystack for term in ["voice", "mic", "dictation", "microphone"]):
        return "voice_mic_button"
    return ""


def sanitize_probe_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Remove extension-owned controls before persisting or projecting probe data."""

    clean = dict(snapshot)
    controls = snapshot.get("visible_controls")
    if not isinstance(controls, list):
        return clean

    kept: list[Any] = []
    removed: list[dict[str, Any]] = []
    for item in controls:
        if not isinstance(item, Mapping):
            kept.append(item)
            continue
        surface_id = probe_surface_id_from_control(item)
        if probe_control_candidate_is_safe(surface_id, item, snapshot):
            kept.append(dict(item))
            continue
        removed.append(
            {
                "selector": item.get("selector"),
                "role": item.get("role"),
                "source_surface": item.get("source_surface"),
                "reason": "unsafe_or_extension_owned_control",
            }
        )

    clean["visible_controls"] = kept
    existing = clean.get("sanitization") if isinstance(clean.get("sanitization"), Mapping) else {}
    clean["sanitization"] = {
        **dict(existing),
        "schema_id": "ion.browser_gpt_dom_probe_snapshot_sanitization.v1",
        "visible_controls_input_count": len(controls),
        "visible_controls_kept_count": len(kept),
        "removed_visible_control_count": len(removed),
        "removed_visible_controls": removed[:20],
    }
    return clean


def probe_snapshot_should_update_profile(snapshot: Mapping[str, Any], surface_candidates: Mapping[str, list[dict[str, Any]]]) -> bool:
    health = snapshot.get("dom_health") if isinstance(snapshot.get("dom_health"), Mapping) else {}
    targets = snapshot.get("targets") if isinstance(snapshot.get("targets"), list) else []
    visible_messages = snapshot.get("visible_messages") if isinstance(snapshot.get("visible_messages"), list) else []
    source = snapshot.get("source") if isinstance(snapshot.get("source"), Mapping) else {}
    compatibility_auto_probe = source.get("compatibility_auto_probe") is True
    has_core_candidate = bool(surface_candidates.get("composer") or surface_candidates.get("message_list"))
    has_operator_targets = any(isinstance(item, Mapping) and item.get("selector") for item in targets)
    if compatibility_auto_probe and not health.get("composer_present") and not has_operator_targets and not visible_messages:
        return False
    return has_core_candidate or has_operator_targets or bool(visible_messages)


def probe_surface_coverage_from_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    candidates = surface_candidates_from_probe_snapshot(snapshot)
    found_surface_ids = sorted(candidates.keys())
    found_surface_set = set(found_surface_ids)
    missing_required_surface_ids: list[str] = []
    phase_capture_actions: list[dict[str, Any]] = []
    surface_rows: list[dict[str, Any]] = []

    for surface_id, spec in SURFACE_SPECS.items():
        dependency = PROBE_PHASE_DEPENDENCIES.get(surface_id)
        candidate_count = len(candidates.get(surface_id, []))
        row = {
            "surface_id": surface_id,
            "required": bool(spec.get("required")),
            "kind": spec.get("kind", "unknown"),
            "candidate_count": candidate_count,
            "status": "found" if candidate_count else "not_observed",
        }
        if candidate_count:
            top = candidates[surface_id][0]
            row["selector"] = top.get("selector")
            row["confidence_hint"] = round(float(top.get("score") or 0) / 100, 3)
        elif spec.get("required"):
            row["status"] = "missing_required_in_latest_probe"
            missing_required_surface_ids.append(surface_id)
        elif dependency:
            opener_surface_id = dependency["opener_surface_id"]
            opener_found = opener_surface_id in found_surface_set
            row.update(
                {
                    "status": "needs_phase_capture" if opener_found else "needs_opener_capture",
                    "phase": dependency["phase"],
                    "opener_surface_id": opener_surface_id,
                    "opener_found": opener_found,
                    "instruction": dependency["instruction"],
                }
            )
            phase_capture_actions.append(
                {
                    "surface_id": surface_id,
                    "phase": dependency["phase"],
                    "opener_surface_id": opener_surface_id,
                    "opener_found": opener_found,
                    "instruction": dependency["instruction"],
                }
            )
        surface_rows.append(row)

    return {
        "schema_id": "ion.browser_gpt_dom_probe_surface_coverage.v1",
        "found_surface_ids": found_surface_ids,
        "found_surface_count": len(found_surface_ids),
        "missing_required_surface_ids": missing_required_surface_ids,
        "missing_required_surface_count": len(missing_required_surface_ids),
        "phase_capture_actions": phase_capture_actions,
        "phase_capture_action_count": len(phase_capture_actions),
        "surfaces": surface_rows,
        "authority": default_authority(),
    }


def probe_phase_sweep_projection(root: str | Path = ".", *, limit: int = 48) -> dict[str, Any]:
    shell_root = Path(root).resolve()
    snapshot_dir = shell_root / PROBE_SNAPSHOTS_DIR
    phase_rows: list[dict[str, Any]] = []
    merged_found: set[str] = set()
    if snapshot_dir.exists():
        paths = sorted(
            [path for path in snapshot_dir.glob("*.json") if path.is_file()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        seen: set[tuple[str, str, str]] = set()
        for path in paths[:limit]:
            artifact = read_json(path)
            snapshot = artifact.get("snapshot") if isinstance(artifact.get("snapshot"), Mapping) else {}
            if not isinstance(snapshot, Mapping):
                continue
            phase_sweep = snapshot.get("phase_sweep") if isinstance(snapshot.get("phase_sweep"), Mapping) else {}
            capture_reason = str(snapshot.get("capture_reason") or "")
            if not phase_sweep and not capture_reason.startswith("phase_sweep"):
                continue
            phase = str(phase_sweep.get("phase") or capture_reason or "unknown")
            captured_at = str(artifact.get("captured_at") or snapshot.get("captured_at") or "")
            key = (phase, captured_at, str(phase_sweep.get("status") or ""))
            if key in seen:
                continue
            seen.add(key)
            coverage = probe_surface_coverage_from_snapshot(snapshot)
            for surface_id in coverage.get("found_surface_ids", []):
                merged_found.add(str(surface_id))
            outcome = phase_sweep.get("outcome") if isinstance(phase_sweep.get("outcome"), Mapping) else {}
            phase_rows.append(
                {
                    "phase": phase,
                    "status": phase_sweep.get("status") or "observed",
                    "path": repo_rel(shell_root, path),
                    "captured_at": captured_at,
                    "opener_found": outcome.get("opener_found"),
                    "click_performed": outcome.get("click_performed"),
                    "opener_selector": outcome.get("opener_selector"),
                    "found_surface_ids": coverage.get("found_surface_ids", []),
                    "found_surface_count": coverage.get("found_surface_count", 0),
                    "visible_control_count": len(snapshot.get("visible_controls", [])) if isinstance(snapshot.get("visible_controls"), list) else 0,
                }
            )

    opened_count = sum(1 for row in phase_rows if row.get("click_performed") is True)
    skipped_file_picker = any(row.get("status") == "file_picker_risk" for row in phase_rows)
    return {
        "schema_id": "ion.browser_gpt_dom_probe_phase_sweep_projection.v1",
        "status": "present" if phase_rows else "missing",
        "phase_count": len(phase_rows),
        "opened_phase_count": opened_count,
        "skipped_upload_file_picker": skipped_file_picker,
        "merged_found_surface_ids": sorted(merged_found),
        "merged_found_surface_count": len(merged_found),
        "phases": phase_rows[:16],
        "authority": default_authority(),
    }


def probe_effective_surface_coverage(
    root: str | Path = ".",
    *,
    latest_coverage: Mapping[str, Any] | None = None,
    phase_sweep: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge live probe evidence with the ready selector profile when Chrome runs a stale content script."""

    shell_root = Path(root).resolve()
    latest_coverage = latest_coverage or {}
    phase_sweep = phase_sweep or {}
    profile = read_json(shell_root / LATEST_PROFILE_PATH)
    profile_surfaces = profile.get("surfaces") if isinstance(profile.get("surfaces"), Mapping) else {}

    found: set[str] = set(str(item) for item in latest_coverage.get("found_surface_ids", []) if item)
    found.update(str(item) for item in phase_sweep.get("merged_found_surface_ids", []) if item)
    rows_by_surface: dict[str, dict[str, Any]] = {}
    for row in latest_coverage.get("surfaces", []) if isinstance(latest_coverage.get("surfaces"), list) else []:
        if isinstance(row, Mapping) and row.get("surface_id"):
            rows_by_surface[str(row["surface_id"])] = dict(row)

    profile_backfilled: list[dict[str, Any]] = []
    for surface_id, surface in profile_surfaces.items():
        if not isinstance(surface, Mapping) or surface_id not in SURFACE_SPECS:
            continue
        if not SURFACE_SPECS[surface_id].get("required"):
            continue
        selector = str(surface.get("selector") or "").strip()
        confidence = float(surface.get("confidence") or 0)
        if not selector or confidence < 0.7:
            continue
        if surface_id not in found:
            found.add(str(surface_id))
            profile_backfilled.append(
                {
                    "surface_id": surface_id,
                    "selector": selector,
                    "confidence": confidence,
                    "source": "ready_selector_profile_backfill",
                    "validated_by": surface.get("validated_by") if isinstance(surface.get("validated_by"), list) else [],
                }
            )
        rows_by_surface.setdefault(
            str(surface_id),
            {
                "surface_id": surface_id,
                "required": bool(SURFACE_SPECS[surface_id].get("required")),
                "kind": SURFACE_SPECS[surface_id].get("kind", "unknown"),
                "candidate_count": int(surface.get("candidate_count") or 1),
                "status": "profile_backfilled" if surface_id in {item["surface_id"] for item in profile_backfilled} else "found",
                "selector": selector,
                "confidence_hint": round(confidence, 3),
                "source": "ready_selector_profile",
            },
        )

    missing_required = sorted(surface_id for surface_id, spec in SURFACE_SPECS.items() if spec.get("required") and surface_id not in found)
    surface_rows: list[dict[str, Any]] = []
    for surface_id, spec in SURFACE_SPECS.items():
        row = rows_by_surface.get(surface_id)
        if row:
            if surface_id in found and row.get("status", "").startswith("missing"):
                row["status"] = "found"
            surface_rows.append(row)
        else:
            surface_rows.append(
                {
                    "surface_id": surface_id,
                    "required": bool(spec.get("required")),
                    "kind": spec.get("kind", "unknown"),
                    "candidate_count": 0,
                    "status": "missing_required" if surface_id in missing_required else "not_observed",
                }
            )

    return {
        "schema_id": "ion.browser_gpt_dom_probe_effective_surface_coverage.v1",
        "status": "ready" if not missing_required else "partial",
        "found_surface_ids": sorted(found),
        "found_surface_count": len(found),
        "missing_required_surface_ids": missing_required,
        "missing_required_surface_count": len(missing_required),
        "profile_backfilled_surface_ids": sorted(item["surface_id"] for item in profile_backfilled),
        "profile_backfilled_surface_count": len(profile_backfilled),
        "profile_path": repo_rel(shell_root, shell_root / LATEST_PROFILE_PATH),
        "surfaces": surface_rows,
        "authority": default_authority(),
    }


def probe_issue_resolution_projection(
    *,
    latest_probe: Mapping[str, Any],
    latest_coverage: Mapping[str, Any],
    effective_coverage: Mapping[str, Any],
    phase_sweep: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify probe problems as blocking or already handled so raw drift does not create operator chaos."""

    rows: list[dict[str, Any]] = []
    raw_missing = [str(item) for item in latest_coverage.get("missing_required_surface_ids", []) if item]
    effective_missing = [str(item) for item in effective_coverage.get("missing_required_surface_ids", []) if item]
    backfilled = [str(item) for item in effective_coverage.get("profile_backfilled_surface_ids", []) if item]
    script_status = str(latest_probe.get("source_build_status") or latest_probe.get("source_build_marker") or "unknown")

    if raw_missing and not effective_missing:
        rows.append(
            {
                "finding": "raw_probe_required_surface_gap_compensated",
                "status": "handled",
                "blocking": False,
                "operator_action_required": False,
                "surfaces": raw_missing,
                "resolution": "ready_selector_profile_backfill",
                "detail": "Raw live probe missed required surfaces, but the ready selector profile supplied usable selectors.",
            }
        )
    elif effective_missing:
        rows.append(
            {
                "finding": "required_surface_missing_after_compensation",
                "status": "needs_auto_recalibration",
                "blocking": True,
                "operator_action_required": False,
                "surfaces": effective_missing,
                "resolution": "run_internal_recalibration_or_import_new_probe",
                "detail": "Required surfaces are missing after all available probe/profile evidence was merged.",
            }
        )

    if script_status == "in_page_script_unmarked" and not effective_missing:
        rows.append(
            {
                "finding": "in_page_script_unmarked_but_compensated",
                "status": "handled",
                "blocking": False,
                "operator_action_required": False,
                "surfaces": [],
                "resolution": "continue_using_effective_coverage",
                "detail": "Fresh probes arrived without the current build marker; this is tracked but not blocking because effective coverage is ready.",
            }
        )
    elif script_status == "in_page_script_unmarked":
        rows.append(
            {
                "finding": "in_page_script_unmarked_and_surface_gap_remains",
                "status": "needs_internal_repair",
                "blocking": True,
                "operator_action_required": False,
                "surfaces": effective_missing,
                "resolution": "repair_probe_or_force_internal_extension_reload_path",
                "detail": "The page script is unmarked and required surfaces still need internal repair.",
            }
        )

    if phase_sweep.get("status") != "present":
        rows.append(
            {
                "finding": "phase_sweep_missing",
                "status": "needs_auto_capture",
                "blocking": False,
                "operator_action_required": False,
                "surfaces": [],
                "resolution": "wait_for_or_trigger_internal_phase_sweep",
                "detail": "Menu/drawer phase evidence has not arrived yet; core effective coverage decides readiness.",
            }
        )

    blocking_count = sum(1 for row in rows if row.get("blocking") is True)
    handled_count = sum(1 for row in rows if row.get("status") == "handled")
    operator_count = sum(1 for row in rows if row.get("operator_action_required") is True)
    if blocking_count:
        status = "blocked_internal_repair_required"
        next_action = "internal_repair_required_no_operator_action"
    elif rows:
        status = "handled"
        next_action = "continue"
    else:
        status = "ready"
        next_action = "continue"

    return {
        "schema_id": "ion.browser_gpt_dom_probe_issue_resolution.v1",
        "status": status,
        "issue_count": len(rows),
        "handled_issue_count": handled_count,
        "blocking_issue_count": blocking_count,
        "operator_action_required": operator_count > 0,
        "operator_action_count": operator_count,
        "raw_missing_required_surface_ids": raw_missing,
        "effective_missing_required_surface_ids": effective_missing,
        "profile_backfilled_surface_ids": backfilled,
        "latest_in_page_script_build_status": script_status,
        "next_action": next_action,
        "rows": rows,
        "authority": default_authority(),
    }


def surface_candidates_from_probe_snapshot(snapshot: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    phase = _probe_phase(snapshot)
    surface_map = {
        "composer_textbox": "composer",
        "send_button": "send_button",
        "stop_generating_button": "stop_button",
        "attach_upload_opener": "file_attach_button",
        "upload_popup_item": "file_upload_menu_option",
        "tools_menu_opener": "tools_menu_opener",
        "tools_menu_option": "tools_menu_option",
        "model_picker_opener": "model_picker",
        "model_menu_option": "model_menu_option",
        "thinking_control_opener": "thinking_mode_control",
        "thinking_effort_option": "thinking_effort_option",
        "left_sidebar_toggle": "left_sidebar_toggle",
        "left_drawer_surface": "left_drawer",
        "new_chat_button": "new_chat_button",
        "message_list": "message_list",
        "latest_user_message": "latest_user_message",
        "latest_assistant_message": "latest_assistant_message",
        "native_action_card": "native_action_cards",
    }
    candidates: dict[str, list[dict[str, Any]]] = {}
    targets = snapshot.get("targets") if isinstance(snapshot.get("targets"), list) else []
    for item in targets:
        if not isinstance(item, Mapping):
            continue
        surface_id = surface_map.get(str(item.get("target_id") or ""))
        if not surface_id or not item.get("selector"):
            continue
        candidates.setdefault(surface_id, []).append(_probe_candidate(surface_id, item, score=92, source="operator_pick", phase=phase))

    controls = snapshot.get("visible_controls") if isinstance(snapshot.get("visible_controls"), list) else []
    for item in controls:
        if not isinstance(item, Mapping) or not item.get("selector"):
            continue
        score = 76
        surface_id = probe_surface_id_from_control(item)
        haystack = " ".join(str(item.get(key) or "") for key in ["selector", "tag", "role", "aria_label", "data_testid", "text_preview"]).lower()
        if surface_id == "composer":
            score = 88
        elif surface_id == "send_button":
            score = 86
        elif surface_id == "file_attach_button":
            score = 78
        elif surface_id == "model_picker":
            score = 78
        elif surface_id == "thinking_mode_control":
            score = 78
        elif surface_id == "left_sidebar_toggle":
            score = 78
        elif surface_id == "message_list":
            score = 82
        elif surface_id == "voice_mic_button":
            score = 70
        if surface_id and probe_control_candidate_is_safe(surface_id, item, snapshot):
            candidates.setdefault(surface_id, []).append(_probe_candidate(surface_id, item, score=score, phase=phase))

    messages = snapshot.get("visible_messages") if isinstance(snapshot.get("visible_messages"), list) else []
    if messages:
        first_message = next((item for item in messages if isinstance(item, Mapping) and item.get("selector")), None)
        if first_message:
            candidates.setdefault("message_list", []).append(_probe_candidate("message_list", first_message, score=82, phase=phase))
        for item in messages:
            if not isinstance(item, Mapping) or not item.get("selector"):
                continue
            role = str(item.get("role") or "").lower()
            if "assistant" in role:
                candidates.setdefault("latest_assistant_message", []).append(_probe_candidate("latest_assistant_message", item, score=80, phase=phase))
            elif "user" in role:
                candidates.setdefault("latest_user_message", []).append(_probe_candidate("latest_user_message", item, score=80, phase=phase))

    health = snapshot.get("dom_health") if isinstance(snapshot.get("dom_health"), Mapping) else {}
    if health.get("composer_present") and "composer" not in candidates:
        candidates["composer"] = [{
            "selector": "#prompt-textarea",
            "score": 72,
            "tag": "unknown",
            "role": "textbox",
            "label": "",
            "rect": {},
            "unique": None,
            "source": "probe_dom_health",
            "phase": phase,
            "validated_by": ["probe_snapshot", "composer_present"],
        }]
    return candidates


def surface_candidates_from_recent_probe_snapshots(root: str | Path = ".", *, limit: int = 48) -> dict[str, list[dict[str, Any]]]:
    """Reuse recent phase evidence so fresh-chat probes preserve latent controls."""

    shell_root = Path(root).resolve()
    snapshot_dir = shell_root / PROBE_SNAPSHOTS_DIR
    if not snapshot_dir.exists():
        return {}
    merged: dict[str, list[dict[str, Any]]] = {}
    paths = sorted(
        [path for path in snapshot_dir.glob("*.json") if path.is_file() and path.name != LATEST_DEGRADED_PROBE_SNAPSHOT_PATH.name],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in paths[:limit]:
        artifact = read_json(path)
        snapshot = artifact.get("snapshot") if isinstance(artifact.get("snapshot"), Mapping) else {}
        if not isinstance(snapshot, Mapping):
            continue
        page_state = probe_page_state_from_snapshot(snapshot)
        for surface_id, rows in surface_candidates_from_probe_snapshot(snapshot).items():
            for row in rows:
                copied = dict(row)
                copied["source"] = str(copied.get("source") or "recent_probe_snapshot")
                copied["page_state"] = page_state
                copied["snapshot_path"] = repo_rel(shell_root, path)
                merged.setdefault(surface_id, []).append(copied)
    return merge_surface_candidate_sets(merged)


def record_browser_gpt_dom_probe_snapshot(root: str | Path = ".", packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = Path(root).resolve()
    packet = packet or {}
    snapshot = packet.get("snapshot")
    if not isinstance(snapshot, Mapping):
        return {
            "schema_id": "ion.browser_gpt_dom_probe_snapshot_record_result.v1",
            "ok": False,
            "finding": "snapshot_object_required",
            "authority": default_authority(),
            "production_authority": False,
            "live_execution_authority": False,
        }
    clean_snapshot = sanitize_probe_snapshot(snapshot)
    captured_at = str(clean_snapshot.get("captured_at") or utc_now())
    filename = _safe_probe_snapshot_filename(packet.get("filename"), captured_at)
    snapshot_path = shell_root / PROBE_SNAPSHOTS_DIR / filename
    latest_path = shell_root / LATEST_PROBE_SNAPSHOT_PATH
    degraded_latest_path = shell_root / LATEST_DEGRADED_PROBE_SNAPSHOT_PATH
    source = clean_snapshot.get("source") if isinstance(clean_snapshot.get("source"), Mapping) else {}
    artifact = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot_artifact.v1",
        "artifact_kind": "browser_gpt_dom_probe_snapshot",
        "recorded_at": utc_now(),
        "captured_at": captured_at,
        "source": {
            "extension": source.get("extension") or "ION Browser GPT DOM Probe",
            "compatibility_auto_probe": source.get("compatibility_auto_probe") is True,
            "build_marker": source.get("build_marker"),
            "page_url": clean_snapshot.get("url"),
            "snapshot_schema": clean_snapshot.get("schema_id"),
            "redaction_policy": "visible_labels_and_previews_only",
            "sanitized": True,
        },
        "snapshot": clean_snapshot,
        "authority": default_authority(),
    }
    surface_candidates = surface_candidates_from_probe_snapshot(clean_snapshot)
    write_json(snapshot_path, artifact)
    if not probe_snapshot_should_update_profile(clean_snapshot, surface_candidates):
        write_json(degraded_latest_path, artifact)
        summary = latest_browser_gpt_dom_summary(shell_root)
        return {
            "schema_id": "ion.browser_gpt_dom_probe_snapshot_record_result.v1",
            "ok": True,
            "finding": "probe_snapshot_recorded_profile_preserved_degraded",
            "snapshot_path": repo_rel(shell_root, snapshot_path),
            "latest_degraded_probe_snapshot_path": repo_rel(shell_root, degraded_latest_path),
            "profile_path": summary.get("latest_profile_path"),
            "health_path": summary.get("latest_health_path"),
            "status": summary.get("status"),
            "verdict": summary.get("verdict"),
            "authority": default_authority(),
            "production_authority": False,
            "live_execution_authority": False,
        }
    write_json(latest_path, artifact)
    prior_evidence = prior_native_dom_evidence(shell_root)
    prior_candidates = surface_candidates_from_prior_native_dom_evidence(prior_evidence)
    recent_probe_candidates = surface_candidates_from_recent_probe_snapshots(shell_root)
    profile = build_selector_profile(
        DEFAULT_PROFILE_ID,
        target_url=str(clean_snapshot.get("url") or DEFAULT_ORIGIN),
        surface_candidates=merge_surface_candidate_sets(surface_candidates, recent_probe_candidates, prior_candidates),
        calibration_source="dom_probe_extension_auto_snapshot",
    )
    profile["probe_snapshot_evidence"] = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot_evidence.v1",
        "snapshot_path": repo_rel(shell_root, snapshot_path),
        "latest_path": repo_rel(shell_root, latest_path),
        "captured_at": captured_at,
        "url": clean_snapshot.get("url"),
        "target_count": clean_snapshot.get("target_count"),
        "visible_control_count": len(clean_snapshot.get("visible_controls", [])) if isinstance(clean_snapshot.get("visible_controls"), list) else 0,
        "visible_message_count": len(clean_snapshot.get("visible_messages", [])) if isinstance(clean_snapshot.get("visible_messages"), list) else 0,
        "removed_visible_control_count": clean_snapshot.get("sanitization", {}).get("removed_visible_control_count")
        if isinstance(clean_snapshot.get("sanitization"), Mapping)
        else None,
    }
    profile["page_state_evidence"] = {
        "schema_id": "ion.browser_gpt_dom_page_state_evidence.v1",
        "latest_page_state": probe_page_state_from_snapshot(clean_snapshot),
        "recent_probe_surface_ids": sorted(recent_probe_candidates.keys()),
        "send_selector_can_be_latent_on_fresh_chat": True,
        "current_send_availability_source": "latest_probe_dom_health",
    }
    result = write_profile_artifacts(
        shell_root,
        profile=profile,
        receipt_extra={
            "probe_snapshot": profile["probe_snapshot_evidence"],
            "artifacts_extra": {
                "probe_snapshot": repo_rel(shell_root, snapshot_path),
                "latest_probe_snapshot": repo_rel(shell_root, latest_path),
            },
        },
    )
    return {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot_record_result.v1",
        "ok": True,
        "finding": "probe_snapshot_recorded",
        "snapshot_path": repo_rel(shell_root, snapshot_path),
        "latest_probe_snapshot_path": repo_rel(shell_root, latest_path),
        "profile_path": result.get("profile_path"),
        "health_path": result.get("health_path"),
        "receipt_path": result.get("receipt_path"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "authority": default_authority(),
        "production_authority": False,
        "live_execution_authority": False,
    }


def write_schema_files(root: str | Path = ".") -> dict[str, str]:
    shell_root = Path(root).resolve()
    schema_paths = {
        "selector_profile": shell_root / SCHEMAS_DIR / "browser_gpt_dom_selector_profile.schema.json",
        "dom_health": shell_root / SCHEMAS_DIR / "browser_gpt_dom_health.schema.json",
        "calibration_receipt": shell_root / SCHEMAS_DIR / "browser_gpt_dom_calibration_receipt.schema.json",
    }
    write_json(schema_paths["selector_profile"], PROFILE_JSON_SCHEMA)
    write_json(schema_paths["dom_health"], HEALTH_JSON_SCHEMA)
    write_json(schema_paths["calibration_receipt"], RECEIPT_JSON_SCHEMA)
    return {name: repo_rel(shell_root, path) for name, path in schema_paths.items()}


def candidate_surface_from_spec(surface_id: str, spec: Mapping[str, Any]) -> dict[str, Any]:
    selectors = [str(item) for item in spec.get("selectors", []) if str(item).strip()]
    primary = selectors[0] if selectors else ""
    hotkeys = [str(item) for item in spec.get("hotkeys", []) if str(item).strip()] if isinstance(spec.get("hotkeys"), list) else []
    return {
        "surface_id": surface_id,
        "kind": spec.get("kind", "unknown"),
        "selector": primary,
        "fallbacks": selectors[1:],
        "hotkeys": hotkeys,
        "required": bool(spec.get("required")),
        "confidence": 0.42 if spec.get("required") else 0.28,
        "status": "seed_candidate_needs_live_validation",
        "candidate_count": len(selectors),
        "validated_by": [],
        "expected_validation": list(spec.get("validated_by", [])),
        "last_error": None,
    }


def surface_from_live_candidates(surface_id: str, spec: Mapping[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    seed = candidate_surface_from_spec(surface_id, spec)
    ranked = sorted(
        [candidate for candidate in candidates if isinstance(candidate, dict)],
        key=lambda item: float(item.get("score") or 0),
        reverse=True,
    )
    if not ranked:
        return seed
    top = ranked[0]
    selectors: list[str] = []
    for candidate in ranked:
        selector = str(candidate.get("selector") or "").strip()
        if selector and selector not in selectors:
            selectors.append(selector)
    for selector in spec.get("selectors", []):
        selector = str(selector).strip()
        if selector and selector not in selectors:
            selectors.append(selector)
    score = max(0.0, min(100.0, float(top.get("score") or 0)))
    confidence = round(score / 100, 3)
    validated = list(top.get("validated_by", [])) if isinstance(top.get("validated_by"), list) else []
    candidate_hotkeys = list(top.get("hotkeys", [])) if isinstance(top.get("hotkeys"), list) else []
    hotkeys = candidate_hotkeys or list(seed.get("hotkeys", []))
    return {
        **seed,
        "selector": selectors[0] if selectors else seed["selector"],
        "fallbacks": selectors[1:],
        "hotkeys": hotkeys,
        "confidence": confidence,
        "status": "validated_candidate" if confidence >= 0.7 else "observed_candidate",
        "candidate_count": len(ranked),
        "validated_by": validated,
        "best_candidate": {key: top.get(key) for key in ["selector", "score", "tag", "role", "label", "rect", "unique", "hotkeys"]},
        "observed_candidates": ranked[:8],
    }


def build_selector_profile(
    profile_id: str = DEFAULT_PROFILE_ID,
    *,
    origin: str = DEFAULT_ORIGIN,
    surface_candidates: Mapping[str, list[dict[str, Any]]] | None = None,
    calibration_source: str = "seed_candidate",
    target_url: str | None = None,
) -> dict[str, Any]:
    surface_candidates = surface_candidates or {}
    surfaces: dict[str, Any] = {}
    for surface_id, spec in SURFACE_SPECS.items():
        candidates = surface_candidates.get(surface_id, [])
        surfaces[surface_id] = (
            surface_from_live_candidates(surface_id, spec, candidates)
            if candidates
            else candidate_surface_from_spec(surface_id, spec)
        )
    required_ready = all(surfaces[sid]["confidence"] >= 0.7 for sid, spec in SURFACE_SPECS.items() if spec.get("required"))
    return {
        "schema_id": PROFILE_SCHEMA_ID,
        "profile_id": safe_slug(profile_id),
        "origin": origin,
        "target_url": target_url or origin,
        "created_at": utc_now(),
        "calibration_source": calibration_source,
        "status": "selector_profile_candidate_ready" if required_ready else "selector_profile_seed_candidate",
        "surfaces": surfaces,
        "drift_policy": {
            "degraded_status": "DOM_PROFILE_DEGRADED",
            "recommended_action": "recalibrate_failed_surface",
            "required_surfaces": [sid for sid, spec in SURFACE_SPECS.items() if spec.get("required")],
        },
        "runtime_commands": [
            "READ_DOM_HEALTH",
            "READ_VISIBLE_CONVERSATION",
            "READ_COMPOSER_STATE",
            "SET_DRAFT",
            "FOCUS_COMPOSER",
            "APPLY_SELECTOR_PROFILE",
            "REMOVE_SELECTOR_PROFILE",
            "READ_NATIVE_ACTION_CARDS",
        ],
        "safety_boundaries": [
            "no_cookie_stealing",
            "no_credential_extraction",
            "no_hidden_scraping",
            "no_arbitrary_javascript_from_joc",
            "no_auto_send_without_operator_approval",
            "chatgpt_page_text_is_not_accepted_ion_state",
        ],
        "authority": default_authority(),
    }


def build_dom_health(profile: Mapping[str, Any], receipt_path: str | None = None) -> dict[str, Any]:
    surfaces = profile.get("surfaces") if isinstance(profile.get("surfaces"), Mapping) else {}
    health_surfaces: dict[str, Any] = {}
    failed_required: list[str] = []
    for surface_id, spec in SURFACE_SPECS.items():
        surface = surfaces.get(surface_id) if isinstance(surfaces.get(surface_id), Mapping) else {}
        confidence = float(surface.get("confidence") or 0)
        ok = confidence >= (0.7 if spec.get("required") else 0.35)
        if spec.get("required") and not ok:
            failed_required.append(surface_id)
        health_surfaces[surface_id] = {
            "status": "ok" if ok else ("failed" if spec.get("required") else "unknown"),
            "confidence": round(confidence, 3),
            "selector": surface.get("selector"),
            "validated_by": surface.get("validated_by", []),
            "candidate_count": surface.get("candidate_count", 0),
            "required": bool(spec.get("required")),
        }
    status = "ready" if not failed_required else "degraded"
    return {
        "schema_id": HEALTH_SCHEMA_ID,
        "profile_id": profile.get("profile_id"),
        "generated_at": utc_now(),
        "status": status,
        "verdict": "DOM_PROFILE_READY" if status == "ready" else "DOM_PROFILE_DEGRADED",
        "failed_required_surfaces": failed_required,
        "recommended_action": "none" if not failed_required else f"recalibrate {', '.join(failed_required)}",
        "surfaces": health_surfaces,
        "receipt_path": receipt_path,
        "authority": default_authority(),
    }


def write_profile_artifacts(
    root: str | Path = ".",
    *,
    profile: Mapping[str, Any],
    receipt_extra: Mapping[str, Any] | None = None,
    promote_latest: bool = True,
) -> dict[str, Any]:
    shell_root = Path(root).resolve()
    profile_id = safe_slug(str(profile.get("profile_id") or DEFAULT_PROFILE_ID))
    schema_paths = write_schema_files(shell_root)
    profile_path = shell_root / PROFILES_DIR / f"{profile_id}.selector_profile.json"
    health_path = shell_root / PROFILES_DIR / f"{profile_id}.dom_health.json"
    receipt_path = shell_root / RECEIPTS_DIR / f"{profile_id}.calibration_receipt.json"
    health = build_dom_health(profile, repo_rel(shell_root, receipt_path))
    prior_evidence = prior_native_dom_evidence(shell_root)
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "receipt_id": f"{profile_id}_calibration_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "profile_id": profile_id,
        "created_at": utc_now(),
        "status": "candidate_recorded",
        "artifacts": {
            "selector_profile": repo_rel(shell_root, profile_path),
            "dom_health": repo_rel(shell_root, health_path),
            "schemas": schema_paths,
        },
        "validation": {
            "required_surfaces": [sid for sid, spec in SURFACE_SPECS.items() if spec.get("required")],
            "failed_required_surfaces": health["failed_required_surfaces"],
            "send_click_performed": False,
            "composer_text_mutation_default": "disabled_unless_allow_composer_test",
            "promoted_latest": promote_latest,
        },
        "prior_live_dom_evidence": prior_evidence,
        "authority": default_authority(),
        **dict(receipt_extra or {}),
    }
    write_json(profile_path, dict(profile))
    write_json(health_path, health)
    write_json(receipt_path, receipt)
    if promote_latest:
        write_json(shell_root / LATEST_PROFILE_PATH, dict(profile))
        write_json(shell_root / LATEST_HEALTH_PATH, health)
    index = read_json(shell_root / INDEX_PATH)
    profiles = [item for item in index.get("profiles", []) if isinstance(item, dict)]
    profiles = [item for item in profiles if item.get("profile_id") != profile_id]
    profiles.insert(
        0,
        {
            "profile_id": profile_id,
            "profile_path": repo_rel(shell_root, profile_path),
            "health_path": repo_rel(shell_root, health_path),
            "receipt_path": repo_rel(shell_root, receipt_path),
            "status": health["status"],
            "updated_at": utc_now(),
            "promoted_latest": promote_latest,
        },
    )
    latest_profile_id = profile_id if promote_latest else index.get("latest_profile_id")
    write_json(
        shell_root / INDEX_PATH,
        {
            "schema_id": "ion.browser_gpt_dom_profile_index.v1",
            "generated_at": utc_now(),
            "latest_profile_id": latest_profile_id,
            "profiles": profiles[:24],
            "authority": default_authority(),
        },
    )
    return {
        "ok": True,
        "profile_id": profile_id,
        "profile_path": repo_rel(shell_root, profile_path),
        "health_path": repo_rel(shell_root, health_path),
        "receipt_path": repo_rel(shell_root, receipt_path),
        "index_path": repo_rel(shell_root, shell_root / INDEX_PATH),
        "status": health["status"],
        "verdict": health["verdict"],
        "promoted_latest": promote_latest,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def write_seed_candidate_profile(root: str | Path = ".", profile_id: str = DEFAULT_PROFILE_ID) -> dict[str, Any]:
    evidence = prior_native_dom_evidence(root)
    surface_candidates = surface_candidates_from_prior_native_dom_evidence(evidence)
    profile = build_selector_profile(
        profile_id,
        target_url=str(evidence.get("url") or DEFAULT_ORIGIN),
        surface_candidates=surface_candidates,
        calibration_source="native_dom_snapshot_import" if surface_candidates else "seed_candidate_no_live_browser",
    )
    if evidence.get("status") == "present":
        profile["prior_live_dom_evidence"] = evidence
    return write_profile_artifacts(root, profile=profile)


def probe_snapshot_projection(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).resolve()

    def artifact_row(path: Path) -> dict[str, Any]:
        artifact = read_json(path)
        if not artifact:
            return {
                "status": "missing",
                "path": repo_rel(shell_root, path),
                "present": False,
            }
        snapshot = artifact.get("snapshot") if isinstance(artifact.get("snapshot"), Mapping) else {}
        health = snapshot.get("dom_health") if isinstance(snapshot.get("dom_health"), Mapping) else {}
        source = snapshot.get("source") if isinstance(snapshot.get("source"), Mapping) else {}
        coverage = probe_surface_coverage_from_snapshot(snapshot) if snapshot else {}
        build_marker = source.get("build_marker") or (artifact.get("source", {}).get("build_marker") if isinstance(artifact.get("source"), Mapping) else None)
        return {
            "status": "present",
            "path": repo_rel(shell_root, path),
            "present": True,
            "captured_at": artifact.get("captured_at") or snapshot.get("captured_at"),
            "recorded_at": artifact.get("recorded_at"),
            "url": snapshot.get("url") or source.get("page_url"),
            "capture_reason": snapshot.get("capture_reason"),
            "source_extension": source.get("extension") or artifact.get("source", {}).get("extension")
            if isinstance(artifact.get("source"), Mapping)
            else source.get("extension"),
            "source_build_marker": build_marker,
            "source_build_status": "current" if build_marker == EXPECTED_CHATOPS_PROBE_BUILD_MARKER else "in_page_script_unmarked",
            "compatibility_auto_probe": source.get("compatibility_auto_probe") is True,
            "composer_present": health.get("composer_present"),
            "send_available": health.get("send_available"),
            "visible_button_count": health.get("visible_button_count"),
            "source_status": health.get("source_status"),
            "surface_coverage": coverage,
            "found_surface_count": coverage.get("found_surface_count") if isinstance(coverage, Mapping) else 0,
            "missing_required_surface_count": coverage.get("missing_required_surface_count") if isinstance(coverage, Mapping) else 0,
            "phase_capture_action_count": coverage.get("phase_capture_action_count") if isinstance(coverage, Mapping) else 0,
        }

    latest_usable = artifact_row(shell_root / LATEST_PROBE_SNAPSHOT_PATH)
    latest_degraded = artifact_row(shell_root / LATEST_DEGRADED_PROBE_SNAPSHOT_PATH)
    phase_sweep = probe_phase_sweep_projection(shell_root)
    latest_coverage = (
        latest_usable.get("surface_coverage")
        if isinstance(latest_usable.get("surface_coverage"), Mapping)
        else latest_degraded.get("surface_coverage")
        if isinstance(latest_degraded.get("surface_coverage"), Mapping)
        else {}
    )
    effective_coverage = probe_effective_surface_coverage(shell_root, latest_coverage=latest_coverage, phase_sweep=phase_sweep)
    issue_resolution = probe_issue_resolution_projection(
        latest_probe=latest_usable if latest_usable.get("present") else latest_degraded,
        latest_coverage=latest_coverage,
        effective_coverage=effective_coverage,
        phase_sweep=phase_sweep,
    )
    return {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot_projection.v1",
        "status": "degraded_probe_observed" if latest_degraded.get("present") else "no_degraded_probe",
        "expected_chatops_probe_build_marker": EXPECTED_CHATOPS_PROBE_BUILD_MARKER,
        "latest_in_page_script_build_status": latest_usable.get("source_build_status") or latest_degraded.get("source_build_status"),
        "latest_extension_build_status": latest_usable.get("source_build_status") or latest_degraded.get("source_build_status"),
        "latest_usable_probe": latest_usable,
        "latest_degraded_probe": latest_degraded,
        "latest_surface_coverage": latest_coverage,
        "effective_surface_coverage": effective_coverage,
        "issue_resolution": issue_resolution,
        "phase_sweep": phase_sweep,
        "profile_preservation_guard": "degraded_auto_probe_cannot_overwrite_profile",
        "normal_latest_advances_only_on_usable_probe": True,
        "authority": default_authority(),
    }


def _latest_probe_snapshot_payload(root: Path) -> dict[str, Any]:
    artifact = read_json(root / LATEST_PROBE_SNAPSHOT_PATH)
    snapshot = artifact.get("snapshot") if isinstance(artifact.get("snapshot"), Mapping) else artifact
    return dict(snapshot) if isinstance(snapshot, Mapping) else {}


def _surface_rows_by_id(coverage: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in coverage.get("surfaces", []) if isinstance(coverage.get("surfaces"), list) else []:
        if isinstance(row, Mapping) and row.get("surface_id"):
            rows[str(row["surface_id"])] = dict(row)
    return rows


def _probe_controls_by_surface(snapshot: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = {}
    for item in snapshot.get("visible_controls", []) if isinstance(snapshot.get("visible_controls"), list) else []:
        if not isinstance(item, Mapping) or not item.get("selector"):
            continue
        surface_id = probe_surface_id_from_control(item)
        if not surface_id or surface_id in controls:
            continue
        if not probe_control_candidate_is_safe(surface_id, item, snapshot):
            continue
        controls[surface_id] = dict(item)
    return controls


def _selector_is_safe_for_twin(surface_id: str, selector: str, label: str = "") -> bool:
    normalized = " ".join([selector, label]).lower()
    if not selector.strip():
        return False
    if surface_id == "send_button":
        return any(
            term in normalized
            for term in [
                "composer-submit",
                "send-button",
                "aria-label*='send",
                'aria-label*="send',
                "aria-label='send",
                'aria-label="send',
                "send prompt",
                "send message",
            ]
        ) or label.strip().lower() == "send"
    if surface_id in {"model_picker", "model_menu_option", "tools_menu_opener", "tools_menu_option"}:
        return not any(term in normalized for term in ["chatgpt drawer", "agent drawer", "minimize chatgpt", "open agent drawer"])
    return True


def _profile_selector_for_twin(surface_id: str, surface: Mapping[str, Any]) -> str:
    candidates: list[tuple[str, str]] = []
    best_candidate = surface.get("best_candidate") if isinstance(surface.get("best_candidate"), Mapping) else {}
    candidates.append((str(surface.get("selector") or ""), str(best_candidate.get("label") or "")))
    for row in surface.get("observed_candidates", []) if isinstance(surface.get("observed_candidates"), list) else []:
        if isinstance(row, Mapping):
            candidates.append((str(row.get("selector") or ""), str(row.get("label") or "")))
    for selector in surface.get("fallbacks", []) if isinstance(surface.get("fallbacks"), list) else []:
        candidates.append((str(selector or ""), ""))
    for selector, label in candidates:
        selector = selector.strip()
        if _selector_is_safe_for_twin(surface_id, selector, label):
            return selector
    return ""


def _surface_confidence(surface: Mapping[str, Any], effective_row: Mapping[str, Any] | None = None) -> float:
    values: list[float] = []
    for key in ["confidence", "confidence_hint"]:
        raw = surface.get(key) if key in surface else (effective_row or {}).get(key)
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            pass
    return round(max(values) if values else 0.0, 3)


def _twin_control_row(
    surface_id: str,
    *,
    surface: Mapping[str, Any],
    effective_row: Mapping[str, Any] | None,
    probe_control: Mapping[str, Any] | None,
) -> dict[str, Any]:
    selector = ""
    source = "missing"
    if probe_control and probe_control.get("selector"):
        selector = str(probe_control.get("selector") or "").strip()
        source = "live_probe"
    if not selector:
        selector = _profile_selector_for_twin(surface_id, surface)
        if selector:
            source = str((effective_row or {}).get("source") or "selector_profile")

    confidence = _surface_confidence(surface, effective_row)
    status = str((effective_row or {}).get("status") or surface.get("status") or "")
    present = bool(selector) and (
        confidence >= 0.7
        or source == "live_probe"
        or status in {"found", "profile_backfilled", "validated_candidate"}
    )
    if present and confidence >= 0.7:
        state = "ready"
    elif present:
        state = "observed"
    elif selector:
        state = "seed"
    else:
        state = "missing"
    dependency = PROBE_PHASE_DEPENDENCIES.get(surface_id)
    return {
        "surface_id": surface_id,
        "label": TWIN_CONTROL_LABELS.get(surface_id, surface_id.replace("_", " ")),
        "kind": SURFACE_SPECS.get(surface_id, {}).get("kind", "unknown"),
        "selector": selector,
        "state": state,
        "present": present,
        "confidence": confidence,
        "source": source,
        "required": bool(SURFACE_SPECS.get(surface_id, {}).get("required")),
        "hotkeys": surface.get("hotkeys", SURFACE_SPECS.get(surface_id, {}).get("hotkeys", [])),
        "validated_by": surface.get("validated_by", []),
        "phase_dependency": dict(dependency) if dependency else None,
        "approved_send_required": surface_id == "send_button",
        "live_click_authority": False,
    }


def _twin_messages(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for index, item in enumerate(snapshot.get("visible_messages", []) if isinstance(snapshot.get("visible_messages"), list) else []):
        if not isinstance(item, Mapping):
            continue
        role_raw = str(item.get("role") or "unknown").lower()
        role = "assistant" if "assistant" in role_raw else "user" if "user" in role_raw else role_raw or "unknown"
        full_text = str(item.get("text_full") or item.get("text") or item.get("text_preview") or "").strip()[:60000]
        preview = str(item.get("text_preview") or full_text).strip()[:240]
        if not full_text:
            continue
        messages.append(
            {
                "event_type": "message",
                "role": role,
                "label": role,
                "state": "active" if bool(item.get("streaming")) else "complete",
                "index": index,
                "selector": item.get("selector"),
                "dom_anchor": item.get("dom_anchor") or item.get("selector"),
                "text_sha256": item.get("text_sha256") or (sha256_text(preview) if preview else None),
                "text_full": full_text,
                "text_preview": preview,
                "text_length": item.get("text_length") or len(full_text),
                "has_code_blocks": bool(item.get("code_block_count")),
                "code_block_count": int(item.get("code_block_count") or 0),
                "visible": True,
                "readable": True,
                "streaming": bool(item.get("streaming")),
            }
        )
    return messages


def _twin_timeline_events(snapshot: Mapping[str, Any], messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_events = snapshot.get("timeline_events") if isinstance(snapshot.get("timeline_events"), list) else []
    events: list[dict[str, Any]] = []
    for index, item in enumerate(raw_events):
        if not isinstance(item, Mapping):
            continue
        event_type = str(item.get("event_type") or "message").strip() or "message"
        role_raw = str(item.get("role") or item.get("parent_role") or "unknown").lower()
        role = "assistant_status" if "status" in role_raw else "assistant" if "assistant" in role_raw else "user" if "user" in role_raw else role_raw or "unknown"
        full_text = str(item.get("text_full") or item.get("text") or item.get("text_preview") or item.get("label") or event_type).strip()[:60000]
        preview = str(item.get("text_preview") or full_text).strip()[:240]
        if not full_text:
            continue
        event = {
            "event_type": event_type,
            "event_index": item.get("event_index", index),
            "role": role,
            "label": item.get("label") or role,
            "state": item.get("state") or ("active" if bool(item.get("streaming")) else "complete"),
            "index": item.get("index"),
            "parent_message_index": item.get("parent_message_index"),
            "parent_role": item.get("parent_role"),
            "selector": item.get("selector"),
            "dom_anchor": item.get("dom_anchor") or item.get("selector"),
            "service_name": item.get("service_name"),
            "duration_text": item.get("duration_text"),
            "text_sha256": item.get("text_sha256") or (sha256_text(preview) if preview else None),
            "text_full": full_text,
            "text_preview": preview,
            "text_length": item.get("text_length") or len(full_text),
            "has_code_blocks": bool(item.get("code_block_count")),
            "code_block_count": int(item.get("code_block_count") or 0),
            "visible": bool(item.get("visible", True)),
            "readable": True,
            "streaming": bool(item.get("streaming")),
        }
        events.append({key: value for key, value in event.items() if value is not None})
    if events:
        return events[:500]
    return [
        {
            **message,
            "event_type": "message",
            "event_index": index,
            "label": message.get("role", "message"),
            "state": "active" if bool(message.get("streaming")) else "complete",
        }
        for index, message in enumerate(messages)
    ][:500]


def chatgpt_dom_twin_projection(
    root: str | Path = ".",
    *,
    profile: Mapping[str, Any] | None = None,
    health: Mapping[str, Any] | None = None,
    prior_evidence: Mapping[str, Any] | None = None,
    probe_intake: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = Path(root).resolve()
    profile = profile or {}
    health = health or {}
    prior_evidence = prior_evidence or {}
    probe_intake = probe_intake or probe_snapshot_projection(shell_root)
    surfaces = profile.get("surfaces") if isinstance(profile.get("surfaces"), Mapping) else {}
    effective_coverage = probe_intake.get("effective_surface_coverage") if isinstance(probe_intake.get("effective_surface_coverage"), Mapping) else {}
    effective_rows = _surface_rows_by_id(effective_coverage)
    snapshot = _latest_probe_snapshot_payload(shell_root)
    snapshot_health = snapshot.get("dom_health") if isinstance(snapshot.get("dom_health"), Mapping) else {}
    current_page_state = probe_page_state_from_snapshot(snapshot)
    probe_controls = _probe_controls_by_surface(snapshot)

    control_surface_ids = ["composer", "message_list", "latest_user_message", "latest_assistant_message", *TWIN_CONTROL_ORDER, "left_drawer", "drawer_surface"]
    controls = [
        _twin_control_row(
            surface_id,
            surface=surfaces.get(surface_id) if isinstance(surfaces.get(surface_id), Mapping) else {},
            effective_row=effective_rows.get(surface_id),
            probe_control=probe_controls.get(surface_id),
        )
        for surface_id in control_surface_ids
        if surface_id in SURFACE_SPECS
    ]
    controls_by_id = {row["surface_id"]: row for row in controls}
    composer = controls_by_id.get("composer", {})
    send = controls_by_id.get("send_button", {})
    message_list = controls_by_id.get("message_list", {})
    required_ready = all(controls_by_id.get(surface_id, {}).get("state") in {"ready", "observed"} for surface_id in ["composer", "send_button", "message_list"])
    raw_visible_messages = snapshot.get("visible_messages", []) if isinstance(snapshot.get("visible_messages"), list) else []
    raw_visible_message_count = len(raw_visible_messages)
    messages = _twin_messages(snapshot)
    timeline_events = _twin_timeline_events(snapshot, messages)
    status_event_count = sum(1 for event in timeline_events if str(event.get("event_type") or "") != "message")
    active_event_count = sum(1 for event in timeline_events if str(event.get("state") or "") == "active" or bool(event.get("streaming")))
    tool_event_count = sum(1 for event in timeline_events if str(event.get("event_type") or "").startswith("tool_"))
    unreadable_message_count = max(0, raw_visible_message_count - len(messages))
    latest_user = next((row for row in reversed(messages) if row.get("role") == "user"), None)
    latest_assistant = next((row for row in reversed(messages) if row.get("role") == "assistant"), None)
    issue_resolution = probe_intake.get("issue_resolution") if isinstance(probe_intake.get("issue_resolution"), Mapping) else {}
    status = "missing_profile" if not profile else "ready" if required_ready else "partial"

    return {
        "schema_id": TWIN_SCHEMA_ID,
        "status": status,
        "source": {
            "selector_profile": LATEST_PROFILE_PATH.as_posix(),
            "probe_snapshot": LATEST_PROBE_SNAPSHOT_PATH.as_posix(),
            "effective_coverage_status": effective_coverage.get("status"),
            "profile_id": profile.get("profile_id"),
            "prior_live_dom_evidence_status": prior_evidence.get("status"),
        },
        "composer": {
            "surface_id": "composer",
            "selector": composer.get("selector", ""),
            "present": bool(composer.get("present") or snapshot_health.get("composer_present")),
            "editable": bool(snapshot_health.get("composer_editable") or composer.get("present")),
            "state": composer.get("state", "missing"),
            "confidence": composer.get("confidence", 0),
            "send_available": bool(snapshot_health.get("send_available")),
            "approved_send_required": True,
            "live_send_authority": False,
        },
        "send": {
            "surface_id": "send_button",
            "selector": send.get("selector", ""),
            "present": bool(send.get("present")),
            "state": send.get("state", "missing"),
            "confidence": send.get("confidence", 0),
            "approved_send_required": True,
            "live_send_authority": False,
        },
        "controls": controls,
        "surface_groups": [dict(group) for group in TWIN_SURFACE_GROUPS],
        "transcript": {
            "message_list_selector": message_list.get("selector", ""),
            "message_count": len(messages),
            "raw_visible_message_count": raw_visible_message_count,
            "unreadable_message_count": unreadable_message_count,
            "readability_status": "readable" if messages else "unreadable_anchors" if unreadable_message_count else "empty",
            "latest_user": latest_user,
            "latest_assistant": latest_assistant,
            "messages": messages[:24],
            "timeline_events": timeline_events[:500],
            "timeline_event_count": len(timeline_events),
            "status_event_count": status_event_count,
            "tool_event_count": tool_event_count,
            "active_event_count": active_event_count,
            "latest_activity_state": "active" if bool(snapshot_health.get("response_streaming")) or active_event_count else "complete",
            "empty_transcript": len(messages) == 0,
        },
        "state": {
            "composer_present": bool(snapshot_health.get("composer_present") or composer.get("present")),
            "composer_editable": bool(snapshot_health.get("composer_editable") or composer.get("present")),
            "send_available": bool(snapshot_health.get("send_available")),
            "current_page_state": current_page_state,
            "send_selector_state": "latent_until_draft" if current_page_state == "fresh_empty_chat" and send.get("present") else send.get("state", "missing"),
            "response_streaming": bool(snapshot_health.get("response_streaming")),
            "active_modal": bool(snapshot_health.get("active_dialog_count")),
            "native_action_card_count": int(snapshot_health.get("native_action_card_count") or 0),
            "dom_profile_drifted": status != "ready",
        },
        "issue_resolution": {
            "status": issue_resolution.get("status", "unknown"),
            "blocking_issue_count": int(issue_resolution.get("blocking_issue_count") or 0),
            "operator_action_required": bool(issue_resolution.get("operator_action_required")),
            "next_action": issue_resolution.get("next_action"),
        },
        "operator_action_required": bool(issue_resolution.get("operator_action_required")),
        "authority": default_authority(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "live_send_authority": False,
    }


def latest_browser_gpt_dom_summary(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).resolve()
    index = read_json(shell_root / INDEX_PATH)
    profile = read_json(shell_root / LATEST_PROFILE_PATH)
    health = read_json(shell_root / LATEST_HEALTH_PATH)
    prior_evidence = prior_native_dom_evidence(shell_root)
    probe_intake = probe_snapshot_projection(shell_root)
    chatgpt_dom_twin = chatgpt_dom_twin_projection(
        shell_root,
        profile=profile,
        health=health,
        prior_evidence=prior_evidence,
        probe_intake=probe_intake,
    )
    profiles = [item for item in index.get("profiles", []) if isinstance(item, dict)]
    if not profile:
        return {
            "schema_id": SUMMARY_SCHEMA_ID,
            "status": "missing_profile",
            "profile_count": len(profiles),
            "profile_dir": BASE_DIR.as_posix(),
            "recommended_action": "run_browser_gpt_calibration",
            "commands": ["python3 -S -m kernel.ion_browser_gpt_dom_calibration --ion-root . --write-seed --json"],
            "prior_live_dom_evidence": prior_evidence,
            "probe_intake": probe_intake,
            "chatgpt_dom_twin": chatgpt_dom_twin,
            "authority": default_authority(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    surfaces = profile.get("surfaces") if isinstance(profile.get("surfaces"), Mapping) else {}
    return {
        "schema_id": SUMMARY_SCHEMA_ID,
        "status": health.get("status") or profile.get("status") or "candidate",
        "verdict": health.get("verdict"),
        "profile_count": len(profiles) or 1,
        "latest_profile_id": profile.get("profile_id"),
        "latest_profile_path": LATEST_PROFILE_PATH.as_posix(),
        "latest_health_path": LATEST_HEALTH_PATH.as_posix(),
        "latest_receipt_path": health.get("receipt_path"),
        "origin": profile.get("origin"),
        "target_url": profile.get("target_url"),
        "surfaces": [
            {
                "surface_id": surface_id,
                "kind": SURFACE_SPECS.get(surface_id, {}).get("kind", "unknown"),
                "status": surface.get("status"),
                "health": health.get("surfaces", {}).get(surface_id, {}).get("status") if isinstance(health.get("surfaces"), Mapping) else None,
                "confidence": surface.get("confidence"),
                "selector": surface.get("selector"),
                "fallback_count": len(surface.get("fallbacks", [])) if isinstance(surface.get("fallbacks"), list) else 0,
                "hotkeys": surface.get("hotkeys", SURFACE_SPECS.get(surface_id, {}).get("hotkeys", [])),
                "validated_by": surface.get("validated_by", []),
                "phase_dependency": dict(PROBE_PHASE_DEPENDENCIES[surface_id]) if surface_id in PROBE_PHASE_DEPENDENCIES else None,
                "required": SURFACE_SPECS.get(surface_id, {}).get("required", False),
            }
            for surface_id, surface in surfaces.items()
            if isinstance(surface, Mapping)
        ],
        "runtime_commands": profile.get("runtime_commands", []),
        "safety_boundaries": profile.get("safety_boundaries", []),
        "prior_live_dom_evidence": prior_evidence if prior_evidence.get("status") == "present" else profile.get("prior_live_dom_evidence", prior_evidence),
        "probe_intake": probe_intake,
        "chatgpt_dom_twin": chatgpt_dom_twin,
        "failed_required_surfaces": health.get("failed_required_surfaces", []),
        "recommended_action": health.get("recommended_action", "run_browser_gpt_calibration"),
        "authority": default_authority(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def merge_surface_candidate_sets(
    *candidate_sets: Mapping[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    merged: dict[str, dict[str, dict[str, Any]]] = {}
    for candidate_set in candidate_sets:
        for surface_id, rows in candidate_set.items():
            if not isinstance(rows, list):
                continue
            surface_bucket = merged.setdefault(str(surface_id), {})
            for row in rows:
                if not isinstance(row, dict):
                    continue
                selector = str(row.get("selector") or "").strip()
                if not selector:
                    continue
                rect = row.get("rect") if isinstance(row.get("rect"), Mapping) else {}
                key = "|".join([
                    selector,
                    str(rect.get("left", "")),
                    str(rect.get("top", "")),
                    str(rect.get("width", "")),
                    str(rect.get("height", "")),
                ])
                phase = str(row.get("phase") or "unknown")
                existing = surface_bucket.get(key)
                if existing is None:
                    copied = dict(row)
                    copied["observed_in_phases"] = [phase]
                    surface_bucket[key] = copied
                    continue
                phases = list(existing.get("observed_in_phases", [])) if isinstance(existing.get("observed_in_phases"), list) else []
                if phase not in phases:
                    phases.append(phase)
                existing["observed_in_phases"] = phases
                if float(row.get("score") or 0) > float(existing.get("score") or 0):
                    better = dict(row)
                    better["observed_in_phases"] = phases
                    surface_bucket[key] = better
    return {
        surface_id: sorted(rows.values(), key=lambda item: float(item.get("score") or 0), reverse=True)[:12]
        for surface_id, rows in merged.items()
    }


def playwright_auto_interaction_plan() -> list[dict[str, Any]]:
    return [dict(item) for item in PLAYWRIGHT_AUTO_INTERACTIONS]


def _chrome_executable() -> str | None:
    for candidate in [
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]:
        if candidate:
            return candidate
    return None


def _redact_accessibility_snapshot(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact_accessibility_snapshot(item) for item in value]
    if not isinstance(value, dict):
        return value
    result: dict[str, Any] = {}
    for key, item in value.items():
        if key == "name" and isinstance(item, str):
            result["name_sha256"] = sha256_text(item)
            result["name_length"] = len(item)
            continue
        result[key] = _redact_accessibility_snapshot(item)
    return result


def _playwright_discovery_script(phase: str = "base") -> str:
    surface_specs = {
        sid: {
            "selectors": list(spec.get("selectors", [])),
            "kind": str(spec.get("kind", "unknown")),
            "required": bool(spec.get("required")),
            "hotkeys": list(spec.get("hotkeys", [])) if isinstance(spec.get("hotkeys"), list) else [],
        }
        for sid, spec in SURFACE_SPECS.items()
    }
    script = r"""
(() => {
  const surfaceSpecs = __SURFACE_SPECS__;
  const phase = __PHASE__;
  const bridgePrefixes = ['ion-chatops-', 'ion-browser-gpt-'];
  const textHints = {
    composer: ['message', 'prompt', 'ask'],
    send_button: ['send'],
    stop_button: ['stop', 'stop generating'],
    new_chat_button: ['new chat', 'new'],
    message_list: ['conversation'],
    latest_assistant_message: ['assistant'],
    latest_user_message: ['user'],
    file_attach_button: ['attach', 'upload', 'file', 'add photos', 'add files', 'paperclip'],
    file_upload_menu_option: ['upload', 'computer', 'file'],
    voice_mic_button: ['voice', 'mic', 'microphone', 'dictate'],
    model_picker: ['model', 'gpt', 'chatgpt'],
    model_menu_option: ['gpt', 'model', 'auto'],
    thinking_mode_control: ['think', 'thinking', 'reason', 'reasoning'],
    thinking_effort_option: ['auto', 'fast', 'standard', 'high', 'thinking', 'reasoning'],
    tools_menu_opener: ['tools', 'more', 'add', 'menu'],
    tools_menu_option: ['search', 'image', 'canvas', 'study', 'deep research', 'tools'],
    left_sidebar_toggle: ['sidebar', 'side bar', 'open sidebar', 'close sidebar'],
    left_drawer: ['sidebar', 'chats', 'library', 'projects'],
    drawer_surface: ['dialog', 'menu', 'drawer'],
    native_action_cards: ['allow', 'approve', 'confirm', 'continue', 'run', 'cancel']
  };
  const cssEscape = (value) => {
    if (window.CSS && typeof window.CSS.escape === 'function') return window.CSS.escape(String(value));
    return String(value).replace(/[^a-zA-Z0-9_-]/g, (ch) => '\\' + ch);
  };
  const cssString = (value) => String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  const queryCount = (selector) => {
    try { return document.querySelectorAll(selector).length; } catch (_error) { return 0; }
  };
  const isBridgeElement = (el) => {
    if (!el || !el.closest) return false;
    return bridgePrefixes.some((prefix) => el.id?.startsWith(prefix) || el.closest(`[id^="${prefix}"]`));
  };
  const visible = (el) => {
    if (!el || isBridgeElement(el)) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0
      && rect.width >= 4 && rect.height >= 4 && rect.bottom > 0 && rect.right > 0
      && rect.top < innerHeight && rect.left < innerWidth;
  };
  const stableSelector = (el) => {
    if (el.id && !el.id.startsWith(':') && queryCount(`#${cssEscape(el.id)}`) === 1) return `#${cssEscape(el.id)}`;
    const testId = el.getAttribute('data-testid');
    if (testId) {
      const selector = `${el.tagName.toLowerCase()}[data-testid="${cssString(testId)}"]`;
      if (queryCount(selector) === 1) return selector;
      return `[data-testid="${cssString(testId)}"]`;
    }
    const aria = el.getAttribute('aria-label');
    if (aria && aria.length < 100) {
      const selector = `${el.tagName.toLowerCase()}[aria-label="${cssString(aria)}"]`;
      if (queryCount(selector) === 1) return selector;
    }
    const role = el.getAttribute('role');
    if (role && aria && aria.length < 100) {
      const selector = `[role="${cssString(role)}"][aria-label="${cssString(aria)}"]`;
      if (queryCount(selector) === 1) return selector;
    }
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 5 && node !== document.documentElement) {
      const tag = node.tagName.toLowerCase();
      const parent = node.parentElement;
      if (!parent) {
        parts.unshift(tag);
        break;
      }
      const siblings = Array.from(parent.children).filter((child) => child.tagName === node.tagName);
      const index = siblings.indexOf(node) + 1;
      parts.unshift(siblings.length > 1 ? `${tag}:nth-of-type(${index})` : tag);
      node = parent;
    }
    return parts.join(' > ');
  };
  const rectFor = (el) => {
    const rect = el.getBoundingClientRect();
    return {
      left: Math.round(rect.left),
      top: Math.round(rect.top),
      right: Math.round(rect.right),
      bottom: Math.round(rect.bottom),
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    };
  };
  const textFor = (el) => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
  const labelFor = (el) => [
    el.getAttribute('aria-label') || '',
    el.getAttribute('title') || '',
    el.getAttribute('placeholder') || '',
    el.getAttribute('data-testid') || '',
    el.getAttribute('role') || '',
    textFor(el)
  ].join(' ').replace(/\s+/g, ' ').trim().slice(0, 220);
  const labelLower = (el) => labelFor(el).toLowerCase();
  const hasHint = (surface, el) => {
    const label = labelLower(el);
    return (textHints[surface] || []).some((hint) => label.includes(hint));
  };
  const isButtonLike = (el) => {
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || '';
    return tag === 'button' || role === 'button' || role === 'menuitem' || role === 'option' || role === 'menuitemradio' || role === 'switch' || el.closest('button');
  };
  const hasMessages = (el) => Boolean(el.querySelector('[data-message-author-role], [data-testid^="conversation-turn"], article'));
  const surfaceShapeMatch = (surface, el, spec) => {
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || '';
    if (surface === 'composer') return tag === 'textarea' || el.isContentEditable || role === 'textbox';
    if (surface === 'message_list') return tag === 'main' || hasMessages(el) || el.matches('[data-testid^="conversation-turn"]');
    if (surface === 'latest_assistant_message') return el.getAttribute('data-message-author-role') === 'assistant' || hasHint(surface, el);
    if (surface === 'latest_user_message') return el.getAttribute('data-message-author-role') === 'user' || hasHint(surface, el);
    if (surface === 'left_drawer') return el.id === 'stage-slideover-sidebar' || tag === 'aside' || role === 'navigation';
    if (surface === 'drawer_surface') return tag === 'aside' || role === 'dialog' || role === 'menu' || role === 'listbox' || el.matches('[data-radix-popper-content-wrapper]');
    if (surface === 'native_action_cards') return role === 'dialog' || hasHint(surface, el);
    if (spec.kind === 'button') return isButtonLike(el) && hasHint(surface, el);
    if (spec.kind === 'menuitem') return (isButtonLike(el) || role === 'option' || role === 'menuitemradio') && hasHint(surface, el);
    return hasHint(surface, el);
  };
  const scoreFor = (surface, el, selector, source) => {
    let score = 0;
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || '';
    const label = labelLower(el);
    const rect = el.getBoundingClientRect();
    const unique = queryCount(selector) === 1;
    if (visible(el)) score += 20;
    if (unique) score += 14;
    if (source === 'css_selector') score += 8;
    if (source === 'generic_scan') score += 5;
    if (surface === 'composer' && (tag === 'textarea' || el.isContentEditable || role === 'textbox')) score += 36;
    if (surface === 'composer' && rect.bottom > innerHeight - 320) score += 10;
    if (surface === 'send_button' && isButtonLike(el)) score += 18;
    if (surface === 'send_button' && label.includes('send')) score += 26;
    if (surface === 'stop_button' && label.includes('stop')) score += 26;
    if (surface === 'file_attach_button' && /(attach|upload|file|paperclip|add)/i.test(label)) score += 28;
    if (surface === 'file_upload_menu_option' && /(upload|computer|file)/i.test(label)) score += 28;
    if (surface === 'voice_mic_button' && /(voice|mic|microphone|dictate)/i.test(label)) score += 24;
    if (surface === 'model_picker' && /(model|gpt|chatgpt)/i.test(label)) score += 24;
    if (surface === 'model_menu_option' && /(gpt|model|auto)/i.test(label)) score += 24;
    if (surface === 'thinking_mode_control' && /(think|reason)/i.test(label)) score += 28;
    if (surface === 'thinking_effort_option' && /(auto|fast|standard|high|think|reason)/i.test(label)) score += 24;
    if (surface === 'tools_menu_opener' && /(tools|more|menu|add)/i.test(label)) score += 22;
    if (surface === 'tools_menu_option' && /(search|image|canvas|study|research|tools)/i.test(label)) score += 22;
    if (surface === 'left_sidebar_toggle' && /sidebar|side bar/i.test(label)) score += 30;
    if (surface === 'left_drawer' && (el.id === 'stage-slideover-sidebar' || tag === 'aside')) score += 34;
    if (surface === 'drawer_surface' && (role === 'dialog' || role === 'menu' || role === 'listbox' || tag === 'aside')) score += 26;
    if (surface === 'message_list' && hasMessages(el)) score += 34;
    if (surface.includes('message') && (el.getAttribute('data-message-author-role') || textFor(el).length > 20)) score += 18;
    if (surface === 'native_action_cards' && /(allow|approve|confirm|continue|run|cancel)/i.test(label)) score += 22;
    if (el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true') score -= surface === 'send_button' ? 4 : 8;
    return Math.max(0, Math.min(100, score));
  };
  const candidateRecord = (surface, el, selector, source) => {
    const resolvedSelector = stableSelector(el) || selector;
    const text = textFor(el);
    const validated = [];
    if (visible(el)) validated.push('visible');
    if (queryCount(resolvedSelector) === 1) validated.push('unique_selector');
    if (surface === 'composer' && (el.isContentEditable || el.tagName.toLowerCase() === 'textarea' || el.getAttribute('role') === 'textbox')) validated.push('editable_shape');
    if (surface === 'send_button') validated.push(el.disabled ? 'disabled_state_observed' : 'enabled_state_observed');
    if (source === 'generic_scan') validated.push('generic_accessible_scan');
    if (source === 'css_selector') validated.push('seed_selector_matched');
    return {
      selector: resolvedSelector,
      source_selector: selector,
      source,
      phase,
      score: scoreFor(surface, el, resolvedSelector, source),
      unique: queryCount(resolvedSelector) === 1,
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role') || '',
      label: labelFor(el),
      rect: rectFor(el),
      text_preview: text.slice(0, 160),
      text_length: text.length,
      hotkeys: surfaceSpecs[surface]?.hotkeys || [],
      validated_by: validated
    };
  };
  const genericElements = Array.from(document.querySelectorAll([
    'button',
    'a[role="button"]',
    '[role="button"]',
    '[role="menuitem"]',
    '[role="menuitemradio"]',
    '[role="option"]',
    '[role="textbox"]',
    '[role="dialog"]',
    '[role="menu"]',
    '[role="listbox"]',
    'textarea',
    '[contenteditable="true"]',
    '[data-testid]',
    '[data-message-author-role]',
    '[data-testid^="conversation-turn"]',
    'main',
    'article',
    'aside',
    '[data-radix-popper-content-wrapper]'
  ].join(','))).filter(visible);
  const results = {};
  for (const [surface, spec] of Object.entries(surfaceSpecs)) {
    const rows = [];
    for (const selector of spec.selectors || []) {
      try {
        document.querySelectorAll(selector).forEach((el) => {
          if (visible(el)) rows.push(candidateRecord(surface, el, selector, 'css_selector'));
        });
      } catch (_error) {}
    }
    for (const el of genericElements) {
      if (surfaceShapeMatch(surface, el, spec)) {
        rows.push(candidateRecord(surface, el, stableSelector(el), 'generic_scan'));
      }
    }
    const seen = new Set();
    results[surface] = rows
      .sort((a, b) => b.score - a.score)
      .filter((row) => {
        const key = [row.selector, row.rect.left, row.rect.top, row.rect.width, row.rect.height].join('|');
        if (seen.has(key)) return false;
        seen.add(key);
        return row.score >= 20;
      })
      .slice(0, 12);
  }
  return {
    captured_at: new Date().toISOString(),
    phase,
    url: location.href,
    title: document.title,
    viewport: { width: innerWidth, height: innerHeight, scroll_x: scrollX, scroll_y: scrollY },
    surfaces: results
  };
})()
"""
    return script.replace("__SURFACE_SPECS__", json.dumps(surface_specs)).replace("__PHASE__", json.dumps(phase))


def _playwright_overlay_script(surface_candidates: Mapping[str, list[Mapping[str, Any]]]) -> str:
    overlay_payload = {
        sid: [
            {
                "surface_id": sid,
                "rank": idx,
                "rect": candidate.get("rect", {}),
                "score": candidate.get("score"),
            }
            for idx, candidate in enumerate(candidates[:3])
        ]
        for sid, candidates in surface_candidates.items()
    }
    return f"""
(() => {{
  document.querySelectorAll('[data-ion-browser-gpt-overlay]').forEach((node) => node.remove());
  const payload = {json.dumps(overlay_payload)};
  const colors = ['#23c55e', '#f4c542', '#ef4444'];
  for (const [surface, rows] of Object.entries(payload)) {{
    for (const row of rows) {{
      const rect = row.rect || {{}};
      if (!rect.width || !rect.height) continue;
      const box = document.createElement('div');
      box.dataset.ionBrowserGptOverlay = 'true';
      box.style.cssText = [
        'position:fixed',
        `left:${{rect.left}}px`,
        `top:${{rect.top}}px`,
        `width:${{rect.width}}px`,
        `height:${{rect.height}}px`,
        `border:2px solid ${{colors[row.rank] || '#60a5fa'}}`,
        'z-index:2147483646',
        'pointer-events:none',
        'box-sizing:border-box',
        'background:transparent',
      ].join(';');
      const label = document.createElement('div');
      label.textContent = `${{surface}} ${{Math.round(row.score || 0)}}`;
      label.style.cssText = 'position:absolute;left:0;top:-20px;background:#05070a;color:#fff;font:12px system-ui;padding:2px 5px;border-radius:3px;white-space:nowrap';
      box.appendChild(label);
      document.documentElement.appendChild(box);
    }}
  }}
}})()
"""


def _playwright_isolation_script() -> str:
    return r"""
(() => {
  const styleId = 'ion-browser-gpt-playwright-calibrator-isolation-style';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = [
      '#ion-chatops-bridge-panel',
      '#ion-chatops-bridge-approval',
      '#ion-chatops-settings-control-pad',
      '#ion-chatops-message-queue-float',
      '#ion-chatops-context-workflow-float',
      '#ion-chatgpt-left-icon-dock',
      '#ion-chatgpt-native-left-rail',
      '#ion-chatgpt-native-left-drawer',
      '#ion-browser-gpt-dom-probe-panel',
      '#ion-browser-gpt-dom-probe-highlight',
      '.ion-chatgpt-left-icon-dock-bottom-half',
      '.ion-chatgpt-native-left-control',
      '[id^="ion-chatops-"]',
      '[id^="ion-chatgpt-left-"]',
      '[id^="ion-chatgpt-native-left-"]',
      '[id^="ion-browser-gpt-dom-probe-"]'
    ].join(',') + '{display:none!important;visibility:hidden!important;pointer-events:none!important}';
    (document.head || document.documentElement).appendChild(style);
  }
  ['ion-chatgpt-left-icon-dock', 'ion-chatgpt-native-left-rail', 'ion-chatgpt-native-left-drawer'].forEach((id) => {
    const node = document.getElementById(id);
    if (node) node.remove();
  });
  document.querySelectorAll('.ion-chatgpt-native-left-split-host').forEach((node) => {
    node.classList.remove('ion-chatgpt-native-left-split-host');
  });
  return {
    isolated: true,
    old_chatops_visible_count: Array.from(document.querySelectorAll('[id^="ion-chatops-"], [id^="ion-chatgpt-left-"], [id^="ion-chatgpt-native-left-"]'))
      .filter((node) => {
        const rect = node.getBoundingClientRect();
        const style = getComputedStyle(node);
        return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
      }).length
  };
})()
"""


def _top_candidate_selector(surface_candidates: Mapping[str, list[dict[str, Any]]], surface_id: str) -> str | None:
    rows = surface_candidates.get(surface_id)
    if not isinstance(rows, list) or not rows:
        return None
    ranked = sorted(
        [row for row in rows if isinstance(row, dict) and str(row.get("selector") or "").strip()],
        key=lambda row: float(row.get("score") or 0),
        reverse=True,
    )
    if not ranked:
        return None
    return str(ranked[0].get("selector") or "").strip()


def _playwright_try_interaction(
    page: Any,
    surface_candidates: Mapping[str, list[dict[str, Any]]],
    interaction: Mapping[str, Any],
    timeout_error: Any,
) -> dict[str, Any]:
    surface_id = str(interaction.get("surface_id") or "")
    phase = str(interaction.get("phase") or surface_id or "interaction")
    selector = _top_candidate_selector(surface_candidates, surface_id)
    event: dict[str, Any] = {
        "phase": phase,
        "surface_id": surface_id,
        "description": interaction.get("description"),
        "selector": selector,
        "status": "skipped_missing_candidate" if not selector else "pending",
        "send_click_performed": False,
    }
    if not selector:
        return event
    if surface_id == "send_button":
        event["status"] = "blocked_send_button_never_clicked"
        return event
    try:
        locator = page.locator(selector).first()
        if interaction.get("allow_file_chooser"):
            try:
                with page.expect_file_chooser(timeout=900) as chooser_info:
                    locator.click(timeout=2500)
                _chooser = chooser_info.value
                event["status"] = "file_chooser_triggered_and_recorded"
                event["file_chooser_triggered"] = True
            except timeout_error:
                event["status"] = "clicked_no_file_chooser_event"
                event["file_chooser_triggered"] = False
        else:
            locator.click(timeout=2500)
            event["status"] = "clicked"
        page.wait_for_timeout(650)
    except Exception as exc:  # pragma: no cover - browser/page dependent.
        event["status"] = "click_failed"
        event["error"] = str(exc)[:240]
    return event


def _playwright_try_composer_text_probe(
    page: Any,
    surface_candidates: Mapping[str, list[dict[str, Any]]],
    profile_slug: str,
) -> dict[str, Any]:
    selector = _top_candidate_selector(surface_candidates, "composer")
    event: dict[str, Any] = {
        "phase": "composer_text_probe",
        "surface_id": "composer",
        "selector": selector,
        "status": "skipped_missing_composer" if not selector else "pending",
        "send_click_performed": False,
    }
    if not selector:
        return event
    probe_text = f"ION DOM CALIBRATION DRAFT {profile_slug}"
    try:
        locator = page.locator(selector).first
        existing = locator.evaluate(
            """(el) => {
              if ('value' in el) return el.value || '';
              return el.innerText || el.textContent || '';
            }"""
        )
        event["existing_text_length"] = len(str(existing or ""))
        if str(existing or "").strip():
            event["status"] = "skipped_composer_not_empty"
            return event
        locator.click(timeout=2500)
        locator.fill(probe_text, timeout=2500)
        page.wait_for_timeout(450)
        readback = locator.evaluate(
            """(el) => {
              if ('value' in el) return el.value || '';
              return el.innerText || el.textContent || '';
            }"""
        )
        event["status"] = "draft_inserted"
        event["readback_sha256"] = sha256_text(str(readback or ""))
        event["readback_length"] = len(str(readback or ""))
        return event
    except Exception as exc:  # pragma: no cover - browser/page dependent.
        event["status"] = "draft_insert_failed"
        event["error"] = str(exc)[:240]
        return event


def _playwright_clear_composer_probe(page: Any, selector: str | None) -> dict[str, Any]:
    event: dict[str, Any] = {
        "phase": "composer_text_probe_clear",
        "surface_id": "composer",
        "selector": selector,
        "status": "skipped_missing_composer" if not selector else "pending",
        "send_click_performed": False,
    }
    if not selector:
        return event
    try:
        locator = page.locator(selector).first
        locator.fill("", timeout=2500)
        page.wait_for_timeout(250)
        event["status"] = "cleared"
    except Exception as exc:  # pragma: no cover - browser/page dependent.
        event["status"] = "clear_failed"
        event["error"] = str(exc)[:240]
    return event


def _playwright_wait_for_chatgpt_ready(page: Any, timeout_ms: int = 120_000) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_ms / 1000
    last_state: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            state = page.evaluate(
                r"""
(() => {
  const bodyText = (document.body?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 500);
  const readySelector = [
    '#prompt-textarea',
    'textarea',
    '[contenteditable="true"]',
    '[data-message-author-role]',
    '[data-testid^="conversation-turn"]'
  ].join(',');
  const hasReadyDom = Boolean(document.querySelector(readySelector));
  const cloudflare = /cloudflare|verifying|checking your browser|verify you are human/i.test(bodyText);
  const login = /log in|sign up|continue with/i.test(bodyText);
  return {
    title: document.title,
    url: location.href,
    ready: hasReadyDom && !cloudflare,
    has_ready_dom: hasReadyDom,
    cloudflare,
    login,
    body_preview: bodyText.slice(0, 180)
  };
})()
"""
            )
            last_state = state if isinstance(state, dict) else {"state": state}
            if last_state.get("ready"):
                return {"status": "ready", "waited_ms": int((timeout_ms / 1000 - (deadline - time.monotonic())) * 1000), **last_state}
        except Exception as exc:  # pragma: no cover - browser dependent.
            last_state = {"error": str(exc)[:240]}
        try:
            page.wait_for_timeout(1000)
        except Exception as exc:  # pragma: no cover - page may close during browser challenge.
            return {"status": "target_closed", "waited_ms": int((timeout_ms / 1000 - (deadline - time.monotonic())) * 1000), "error": str(exc)[:240], **last_state}
    return {"status": "timeout", "waited_ms": timeout_ms, **last_state}


def calibrate_with_playwright(
    root: str | Path = ".",
    *,
    profile_id: str = DEFAULT_PROFILE_ID,
    target_url: str = DEFAULT_ORIGIN,
    user_data_dir: str | None = None,
    extension_root: str | None = None,
    headless: bool = True,
    allow_composer_test: bool = False,
    auto_interactions: bool = True,
    use_dom_probe_extension: bool = False,
    ready_timeout_ms: int = 120_000,
    promote_latest: bool = True,
) -> dict[str, Any]:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - environment dependent.
        raise RuntimeError(f"python_playwright_unavailable: {exc}") from exc

    shell_root = Path(root).resolve()
    profile_slug = safe_slug(profile_id)
    run_dir = shell_root / RUNTIME_DIR / profile_slug
    run_dir.mkdir(parents=True, exist_ok=True)
    runtime_user_data_dir = Path(user_data_dir).expanduser().resolve() if user_data_dir else run_dir / "chromium-profile"
    runtime_user_data_dir.mkdir(parents=True, exist_ok=True)
    screenshot_before = shell_root / SCREENSHOTS_DIR / f"{profile_slug}.screenshot_before.png"
    screenshot_candidates = shell_root / SCREENSHOTS_DIR / f"{profile_slug}.screenshot_candidates.png"
    dom_snapshot = shell_root / SNAPSHOTS_DIR / f"{profile_slug}.dom_snapshot_redacted.json"
    accessibility_snapshot = shell_root / SNAPSHOTS_DIR / f"{profile_slug}.accessibility_snapshot_redacted.json"
    candidate_scores = shell_root / PROFILES_DIR / f"{profile_slug}.candidate_scores.json"
    automation_report = shell_root / RECEIPTS_DIR / f"{profile_slug}.playwright_automation_report.json"
    chrome = _chrome_executable()
    launch_args = ["--no-sandbox", "--disable-dev-shm-usage"]
    if use_dom_probe_extension and not extension_root:
        default_extension = default_dom_probe_extension_root(shell_root)
        if default_extension:
            extension_root = default_extension.as_posix()
    if extension_root:
        extension_path = Path(extension_root).expanduser().resolve()
        launch_args.extend([f"--disable-extensions-except={extension_path}", f"--load-extension={extension_path}"])
        headless = False
    if not chrome:
        raise RuntimeError("chrome_executable_not_found")

    phase_discoveries: list[dict[str, Any]] = []
    phase_screenshots: dict[str, str] = {}
    interaction_events: list[dict[str, Any]] = []
    isolation_result: dict[str, Any] = {}
    page_ready_result: dict[str, Any] = {}
    surfaces: dict[str, list[dict[str, Any]]] = {}

    def capture_phase(page: Any, phase: str) -> dict[str, Any]:
        nonlocal surfaces
        discovery = page.evaluate(_playwright_discovery_script(phase))
        if not isinstance(discovery, dict):
            discovery = {"phase": phase, "surfaces": {}, "finding": "discovery_return_not_object"}
        phase_surfaces = discovery.get("surfaces") if isinstance(discovery.get("surfaces"), dict) else {}
        for rows in phase_surfaces.values():
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict) and row.get("text_preview"):
                        text = str(row.get("text_preview", ""))
                        row["text_sha256"] = sha256_text(text)
                        row.pop("text_preview", None)
        phase_discoveries.append(discovery)
        surfaces = merge_surface_candidate_sets(surfaces, {sid: rows for sid, rows in phase_surfaces.items() if isinstance(rows, list)})
        phase_shot = shell_root / SCREENSHOTS_DIR / f"{profile_slug}.{safe_slug(phase)}.png"
        phase_shot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=phase_shot.as_posix(), full_page=False)
        phase_screenshots[phase] = repo_rel(shell_root, phase_shot)
        return discovery

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            runtime_user_data_dir.as_posix(),
            executable_path=chrome,
            headless=headless,
            args=launch_args,
            viewport={"width": 1440, "height": 960},
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
            page_ready_result = _playwright_wait_for_chatgpt_ready(page, timeout_ms=ready_timeout_ms)
            try:
                isolation_result = page.evaluate(_playwright_isolation_script())
                if not isinstance(isolation_result, dict):
                    isolation_result = {"isolated": False, "finding": "isolation_return_not_object"}
            except Exception as exc:  # pragma: no cover - browser dependent.
                isolation_result = {"isolated": False, "error": str(exc)[:240]}
            screenshot_before.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=screenshot_before.as_posix(), full_page=False)
            base_discovery = capture_phase(page, "base")
            if allow_composer_test:
                composer_event = _playwright_try_composer_text_probe(page, surfaces, profile_slug)
                interaction_events.append(composer_event)
                if composer_event.get("status") == "draft_inserted":
                    capture_phase(page, "composer_text_probe")
                    clear_event = _playwright_clear_composer_probe(page, composer_event.get("selector") if isinstance(composer_event.get("selector"), str) else None)
                    interaction_events.append(clear_event)
            if auto_interactions:
                for interaction in PLAYWRIGHT_AUTO_INTERACTIONS:
                    event = _playwright_try_interaction(page, surfaces, interaction, PlaywrightTimeoutError)
                    interaction_events.append(event)
                    if event.get("status") in {"clicked", "clicked_no_file_chooser_event", "file_chooser_triggered_and_recorded"}:
                        capture_phase(page, str(interaction.get("phase") or "interaction"))
                        try:
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(250)
                        except Exception:
                            pass
                        try:
                            page.evaluate(_playwright_isolation_script())
                        except Exception:
                            pass
            write_json(
                candidate_scores,
                {
                    "schema_id": "ion.browser_gpt_dom_candidate_scores.v1",
                    "captured_at": utc_now(),
                    "url": base_discovery.get("url"),
                    "title": base_discovery.get("title"),
                    "viewport": base_discovery.get("viewport"),
                    "phase_count": len(phase_discoveries),
                    "phases": phase_discoveries,
                    "surfaces": surfaces,
                    "automation_interactions": interaction_events,
                    "isolation": isolation_result,
                    "page_ready": page_ready_result,
                },
            )
            page.evaluate(_playwright_overlay_script(surfaces))
            screenshot_candidates.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=screenshot_candidates.as_posix(), full_page=False)
            dom_snapshot.parent.mkdir(parents=True, exist_ok=True)
            write_json(dom_snapshot, {
                "schema_id": "ion.browser_gpt_dom_snapshot_redacted.v1",
                "captured_at": utc_now(),
                "url": base_discovery.get("url"),
                "title": base_discovery.get("title"),
                "viewport": base_discovery.get("viewport"),
                "phase_count": len(phase_discoveries),
                "phase_screenshots": phase_screenshots,
                "page_ready": page_ready_result,
                "surface_candidate_counts": {sid: len(rows) for sid, rows in surfaces.items() if isinstance(rows, list)},
            })
            try:
                ax = page.accessibility.snapshot()
            except Exception as exc:  # pragma: no cover - browser dependent.
                ax = {"_snapshot_error": str(exc)}
            write_json(accessibility_snapshot, {
                "schema_id": "ion.browser_gpt_accessibility_snapshot_redacted.v1",
                "captured_at": utc_now(),
                "snapshot": _redact_accessibility_snapshot(ax),
            })
            write_json(automation_report, {
                "schema_id": "ion.browser_gpt_playwright_automation_report.v1",
                "captured_at": utc_now(),
                "target_url": target_url,
                "auto_interactions": auto_interactions,
                "interaction_plan": playwright_auto_interaction_plan(),
                "interaction_events": interaction_events,
                "phase_screenshots": phase_screenshots,
                "isolation": isolation_result,
                "page_ready": page_ready_result,
                "authority": default_authority(),
            })
        finally:
            context.close()

    profile = build_selector_profile(
        profile_id,
        target_url=target_url,
        surface_candidates={sid: rows for sid, rows in surfaces.items() if isinstance(rows, list)},
        calibration_source="playwright_live_dom_observation",
    )
    result = write_profile_artifacts(
        shell_root,
        profile=profile,
        receipt_extra={
            "artifacts_extra": {
                "screenshot_before": repo_rel(shell_root, screenshot_before),
                "screenshot_candidates": repo_rel(shell_root, screenshot_candidates),
                "candidate_scores": repo_rel(shell_root, candidate_scores),
                "dom_snapshot_redacted": repo_rel(shell_root, dom_snapshot),
                "accessibility_snapshot_redacted": repo_rel(shell_root, accessibility_snapshot),
                "automation_report": repo_rel(shell_root, automation_report),
                "phase_screenshots": phase_screenshots,
            },
            "runtime": {
                "target_url": target_url,
                "extension_root": extension_root,
                "use_dom_probe_extension": use_dom_probe_extension,
                "auto_interactions": auto_interactions,
                "used_existing_profile_path": bool(user_data_dir),
                "user_data_dir_recorded": bool(user_data_dir),
                "allow_composer_test": allow_composer_test,
                "send_click_performed": False,
                "page_ready_status": page_ready_result.get("status"),
                "ready_timeout_ms": ready_timeout_ms,
                "promote_latest": promote_latest,
            },
        },
        promote_latest=promote_latest,
    )
    result["screenshot_candidates"] = repo_rel(shell_root, screenshot_candidates)
    result["candidate_scores"] = repo_rel(shell_root, candidate_scores)
    result["automation_report"] = repo_rel(shell_root, automation_report)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create or run a Browser GPT DOM selector calibration profile.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--target-url", default=DEFAULT_ORIGIN)
    parser.add_argument("--write-seed", action="store_true", help="Write a seed candidate profile without opening a browser.")
    parser.add_argument("--calibrate", action="store_true", help="Run a Playwright live DOM calibration.")
    parser.add_argument("--user-data-dir", default=None, help="Optional Chromium user data dir. Only use an existing logged-in profile with operator approval.")
    parser.add_argument("--extension-root", default=None, help="Optional unpacked extension root to side-load for calibration.")
    parser.add_argument("--use-dom-probe-extension", action="store_true", help="Side-load the clean DOM Probe extension when present.")
    parser.add_argument("--no-auto-interactions", action="store_true", help="Disable safe Playwright menu/drawer opener clicks.")
    parser.add_argument("--headed", action="store_true", help="Run headed Chromium.")
    parser.add_argument("--allow-composer-test", action="store_true", help="Permit reversible composer insert/readback test. Never clicks Send.")
    parser.add_argument("--ready-timeout-ms", type=int, default=120_000, help="Maximum ChatGPT readiness wait before capturing degraded evidence.")
    parser.add_argument("--no-promote-latest", action="store_true", help="Write a comparison profile without updating latest.selector_profile.json.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.calibrate:
        result = calibrate_with_playwright(
            args.ion_root,
            profile_id=args.profile_id,
            target_url=args.target_url,
            user_data_dir=args.user_data_dir,
            extension_root=args.extension_root,
            headless=not args.headed,
            allow_composer_test=args.allow_composer_test,
            auto_interactions=not args.no_auto_interactions,
            use_dom_probe_extension=args.use_dom_probe_extension,
            ready_timeout_ms=args.ready_timeout_ms,
            promote_latest=not args.no_promote_latest,
        )
    elif args.write_seed:
        result = write_seed_candidate_profile(args.ion_root, args.profile_id)
    else:
        result = latest_browser_gpt_dom_summary(args.ion_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict") or result.get("status"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
