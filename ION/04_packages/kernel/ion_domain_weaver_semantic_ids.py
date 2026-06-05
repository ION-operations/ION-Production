"""Read-time semantic ID normalization for Domain Weaver candidates."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


SCHEMA_ID = "ion.domain_weaver.semantic_ids.v0_1_candidate"
VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID = "domain.vnext_front_door"
VNEXT_FRONT_DOOR_ALIASES = (
    "ion_vnext_front_door",
    "domain.ion_vnext_front_door",
    "domain.ion_vnext_front_door_authority",
)

AUTHORITY = {
    "candidate_context_only": True,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "registry_write_performed": False,
    "projection_write_performed": False,
    "mount_write_performed": False,
}


def canonicalize_domain_weaver_domain_id(
    raw_id: Any,
    *,
    mount_id: str = "",
    source: str = "",
) -> dict[str, Any]:
    """Return candidate canonical identity metadata without mutating sources."""

    raw_text = str(raw_id or "").strip()
    alias_inputs = set(VNEXT_FRONT_DOOR_ALIASES)
    if mount_id.endswith("__ion_vnext_front_door"):
        alias_inputs.add("")
    if raw_text in alias_inputs:
        canonical = VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
        alias_detected = raw_text != canonical
        alias_family = "vnext_front_door"
    else:
        canonical = raw_text
        alias_detected = False
        alias_family = ""
    return {
        "schema_id": SCHEMA_ID,
        "raw_domain_id": raw_text,
        "canonical_domain_id": canonical,
        "alias_detected": alias_detected,
        "alias_family": alias_family,
        "mount_id": mount_id,
        "source": source,
        "authority": dict(AUTHORITY),
    }


def canonicalize_codex_mount_identity(mount_id: str, manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Derive role/domain identity from mount name plus manifest evidence."""

    manifest = manifest if isinstance(manifest, Mapping) else {}
    raw_role_id, raw_domain_id = ids_from_mount_name(mount_id)
    manifest_domain_id = str(manifest.get("domain_id") or manifest.get("domain") or "").strip()
    manifest_role_id = str(manifest.get("role_id") or manifest.get("role") or "").strip()
    selected_domain = manifest_domain_id or raw_domain_id
    selected_role = manifest_role_id or raw_role_id
    canonical = canonicalize_domain_weaver_domain_id(
        selected_domain,
        mount_id=mount_id,
        source="codex_agent_mount_manifest" if manifest_domain_id else "codex_agent_mount_name",
    )
    return {
        "schema_id": "ion.domain_weaver.codex_mount_identity.v0_1_candidate",
        "mount_id": mount_id,
        "role_id": selected_role,
        "domain_id": canonical["canonical_domain_id"],
        "raw_role_id": raw_role_id,
        "raw_domain_id": raw_domain_id,
        "manifest_role_id": manifest_role_id,
        "manifest_domain_id": manifest_domain_id,
        "canonical_domain_id": canonical["canonical_domain_id"],
        "domain_alias_detected": canonical["alias_detected"],
        "domain_alias_family": canonical["alias_family"],
        "semantic_identity": canonical,
        "authority": dict(AUTHORITY),
    }


def ids_from_mount_name(name: str) -> tuple[str, str]:
    left, marker, right = str(name or "").partition("__")
    if not marker:
        return "", ""
    return _id_from_mount_part(left, "role_"), _id_from_mount_part(right, "domain_")


def _id_from_mount_part(part: str, prefix: str) -> str:
    if part.startswith(prefix):
        return f"{prefix[:-1]}.{part[len(prefix):]}"
    return ""


def read_manifest(path: str | Path) -> dict[str, Any]:
    import json

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}
