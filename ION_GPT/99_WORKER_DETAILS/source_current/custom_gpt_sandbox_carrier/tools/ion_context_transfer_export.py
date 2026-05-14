#!/usr/bin/env python3
"""Candidate transfer ignore/export-profile helper v4.7.

This module implements the bounded part of the transfer system: classification,
manifest generation, and non-exportable boundary enforcement. It does not read
outside the provided root.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Dict, Any
import hashlib
import fnmatch
import yaml

NEVER_EXPORT_MARKERS = [
    "ION_VAULT_LOCAL",
    ".env",
    "secret",
    "token",
    "credential",
    "browser_session",
    "hidden_chain_of_thought",
    "local_cache",
]

DEFAULT_IGNORE_PATTERNS = [
    "*.pyc",
    "__pycache__/**",
    ".pytest_cache/**",
    "*.zip",
    "historical/**",
    "90_HISTORICAL_ZIPS/**",
    "local_cache/**",
    "tmp/**",
]


def is_never_exportable(path: str) -> bool:
    lowered = path.lower()
    return any(marker.lower() in lowered for marker in NEVER_EXPORT_MARKERS)


def ignored_by_patterns(path: str, patterns: Iterable[str]) -> str | None:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(Path(normalized).name, pattern):
            return pattern
    return None


def classify_paths(paths: Iterable[str], ignore_patterns: Iterable[str] | None = None) -> dict:
    ignore_patterns = list(ignore_patterns or DEFAULT_IGNORE_PATTERNS)
    include, omit = [], []
    for path in sorted(paths):
        if is_never_exportable(path):
            omit.append({"path": path, "reason": "non_exportable_boundary"})
            continue
        matched = ignored_by_patterns(path, ignore_patterns)
        if matched:
            omit.append({"path": path, "reason": "ignored_by_pattern", "pattern": matched})
        else:
            include.append(path)
    return {"include": include, "omit": omit}


def load_export_profile(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data


def profile_patterns(profile: Dict[str, Any], profile_name: str) -> List[str]:
    profiles = profile.get("profiles", {})
    selected = profiles.get(profile_name, {})
    return list(DEFAULT_IGNORE_PATTERNS) + list(selected.get("exclude_patterns", []))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_transfer_manifest(root: Path, profile_name: str = "minimal_continuity", paths: Iterable[str] | None = None) -> Dict[str, Any]:
    root = root.resolve()
    profile_path = root / "ION_GPT/ION_EXPORT_PROFILE.yaml"
    profile = load_export_profile(profile_path) if profile_path.exists() else {"profiles": {}}
    patterns = profile_patterns(profile, profile_name)
    if paths is None:
        paths = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    classified = classify_paths(paths, patterns)
    hashes = {}
    for rel in classified["include"]:
        p = root / rel
        if p.exists() and p.is_file():
            hashes[rel] = sha256_file(p)
    return {
        "schema_id": "ion.transfer_manifest.v1",
        "profile": profile_name,
        "include_count": len(classified["include"]),
        "omit_count": len(classified["omit"]),
        "included_files": classified["include"],
        "omitted_files": classified["omit"],
        "hashes": hashes,
        "non_exportable_boundary": NEVER_EXPORT_MARKERS,
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def write_transfer_manifest(root: Path, out_path: Path, profile_name: str = "minimal_continuity") -> Dict[str, Any]:
    manifest = build_transfer_manifest(root, profile_name)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return manifest
