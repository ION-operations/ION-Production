#!/usr/bin/env python3
"""
Canonical agent identity routing for filesystem-first comms.
"""

from __future__ import annotations

import re
from typing import Dict, List


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "_", value.strip().lower()).strip("_")


def normalize_key(value: str) -> str:
    compact = re.sub(r"\s+", " ", value.strip().lower())
    return compact


_CANONICAL: Dict[str, Dict[str, str]] = {
    "agent aether": {"canonical_id": "Agent Aether", "route_key": "aether"},
    "codex agent": {"canonical_id": "Codex Agent", "route_key": "codex"},
    "claude opus 4.6": {"canonical_id": "Claude Opus 4.6", "route_key": "antigravity"},
    "sev": {"canonical_id": "Sev", "route_key": "sev"},
    "composer": {"canonical_id": "Composer", "route_key": "composer"},
    "gemini": {"canonical_id": "Gemini", "route_key": "gemini"},
    "codexgit": {"canonical_id": "CodexGit", "route_key": "codexgit"},
}


_ALIASES = {
    "aether": "agent aether",
    "ceo": "agent aether",
    "codex": "codex agent",
    "coo": "claude opus 4.6",
    "opus": "claude opus 4.6",
    "opus 4.6": "claude opus 4.6",
    "claude opus": "claude opus 4.6",
    "opus1": "claude opus 4.6",
    "antigravity": "claude opus 4.6",
    "sev": "sev",
    "gpt-5.4": "sev",
    "gpt 5.4": "sev",
    "gpt-5.2": "sev",
    "gpt 5.2": "sev",
    "composer": "composer",
    "gemini": "gemini",
    "codexgit": "codexgit",
}


def resolve_identity(agent_name: str, strict: bool = False) -> Dict[str, str]:
    raw = (agent_name or "").strip()
    key = normalize_key(raw)

    canonical_key = key
    if key in _ALIASES:
        canonical_key = _ALIASES[key]

    if canonical_key in _CANONICAL:
        resolved = _CANONICAL[canonical_key]
        return {
            "input": raw,
            "canonical_id": resolved["canonical_id"],
            "route_key": resolved["route_key"],
            "canonical_key": canonical_key,
            "matched": "true",
        }

    if strict:
        raise ValueError(
            f"Unknown agent identity '{raw}'. "
            f"Known identities: {', '.join(known_canonical_ids())}"
        )

    route_key = slug(raw) if raw else "unknown"
    return {
        "input": raw,
        "canonical_id": raw or "unknown",
        "route_key": route_key,
        "canonical_key": canonical_key,
        "matched": "false",
    }


def known_canonical_ids() -> List[str]:
    return [entry["canonical_id"] for entry in _CANONICAL.values()]
