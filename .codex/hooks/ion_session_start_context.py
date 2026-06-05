#!/usr/bin/env python3
"""Codex SessionStart hook for ION Codex context boundaries.

The hook is intentionally read-only. It injects folder-local mount context when
Codex starts inside a generated agent/domain mount. At the active root it emits
a visible fallback boundary instead of loading shared codex_solo as a working
capsule.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ACTIVE_ROOT = Path("/home/sev/ION - Production/ION_Developement").resolve()
PACKAGE_ROOT = ACTIVE_ROOT / "ION" / "04_packages"
AGENT_MOUNT_ROOT = ACTIVE_ROOT / "ION" / "05_context" / "current" / "codex_agent_mounts"
MAX_AGENT_MOUNT_FILE_CHARS = 4000
MAX_ROOT_MOUNT_ROWS = 12
PORTABLE_CONTEXT_DIR = ".ion"
PORTABLE_CONTEXT_MANIFEST = "ION_CONTEXT_CAPSULE.yaml"
PORTABLE_ACTIVE_CONTEXT_PACKAGE = "ACTIVE_CONTEXT_PACKAGE.md"


def _read_stdin() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False
    return True


def _soft_context(message: str) -> dict[str, Any]:
    return {
        "continue": True,
        "suppressOutput": False,
        "systemMessage": f"ION_CARRIER_NOT_OPERATIONAL: {message}",
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "ION_CARRIER_NOT_OPERATIONAL\n"
                "mount_truth_state: SESSION_START_BLOCKED\n"
                f"blocker: {message}"
            ),
        },
    }


def _read_limited(path: Path, *, limit: int = MAX_AGENT_MOUNT_FILE_CHARS) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if len(text) <= limit:
        return text.rstrip()
    return text[:limit].rstrip() + "\n[ION_AGENT_MOUNT_FILE_TRUNCATED]"


def _agent_mount_context(cwd: Path) -> str:
    if not _is_relative_to(cwd, AGENT_MOUNT_ROOT):
        return ""
    try:
        rel = cwd.resolve().relative_to(AGENT_MOUNT_ROOT)
    except ValueError:
        return ""
    if not rel.parts:
        return ""
    mount_path = AGENT_MOUNT_ROOT / rel.parts[0]
    manifest = mount_path / "ION_AGENT_MOUNT_MANIFEST.json"
    capsule = mount_path / ".ion" / "ION_CONTEXT_CAPSULE.yaml"
    active_package = mount_path / ".ion" / "ACTIVE_CONTEXT_PACKAGE.md"
    relationships = mount_path / ".ion" / "RELATIONSHIPS.yaml"
    if not manifest.is_file() and not capsule.is_file():
        return ""
    sections = [
        "ION Codex Agent Mount Boot Context v0.1",
        f"mount_path: {mount_path}",
        "mount_truth_state: CODEX_AGENT_DOMAIN_MOUNT_READY",
        "policy: folder-local capsule is boot context; active ION root and registries remain authority.",
        "shared_codex_solo_boot_context_loaded: false",
        "working_capsule_source: folder_local_ion_context_capsule",
        "production_authority: false",
        "live_execution_authority: false",
        "accepted_state_authority: false",
        "",
    ]
    for label, path, limit in (
        ("AGENT_MOUNT_MANIFEST", manifest, 2200),
        ("AGENTS_MD", mount_path / "AGENTS.md", 2200),
        ("PORTABLE_ION_CONTEXT_CAPSULE", capsule, 4000),
        ("PORTABLE_ACTIVE_CONTEXT_PACKAGE", active_package, 3200),
        ("PORTABLE_RELATIONSHIPS", relationships, 1600),
    ):
        text = _read_limited(path, limit=limit)
        if not text:
            continue
        sections.extend(
            [
                f"## {label}",
                f"path: {path.relative_to(ACTIVE_ROOT).as_posix()}",
                "```text",
                text,
                "```",
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _folder_local_context_root(cwd: Path) -> Path | None:
    for candidate in (cwd, *cwd.parents):
        if not _is_relative_to(candidate, ACTIVE_ROOT):
            return None
        if candidate == ACTIVE_ROOT:
            return None
        capsule = candidate / PORTABLE_CONTEXT_DIR / PORTABLE_CONTEXT_MANIFEST
        if capsule.is_file():
            return candidate
    return None


def _folder_local_context(cwd: Path) -> str:
    context_root = _folder_local_context_root(cwd)
    if context_root is None:
        return ""
    portable_path = context_root / PORTABLE_CONTEXT_DIR
    capsule = portable_path / PORTABLE_CONTEXT_MANIFEST
    active_package = portable_path / PORTABLE_ACTIVE_CONTEXT_PACKAGE
    sections = [
        "ION Folder Local Context Boot Context v0.1",
        f"context_root: {context_root}",
        "mount_truth_state: CODEX_FOLDER_LOCAL_CONTEXT_READY",
        "policy: folder-local .ion capsule is boot context; active ION root and registries remain authority.",
        "shared_codex_solo_boot_context_loaded: false",
        "working_capsule_source: folder_local_ion_context_capsule",
        "production_authority: false",
        "live_execution_authority: false",
        "accepted_state_authority: false",
        "",
    ]
    for label, path, limit in (
        ("AGENTS_MD", context_root / "AGENTS.md", 2200),
        ("FOLDER_ION_CONTEXT_CAPSULE", capsule, 4000),
        ("FOLDER_ACTIVE_CONTEXT_PACKAGE", active_package, 3200),
        ("FOLDER_MINI", portable_path / "MINI.md", 1600),
        ("FOLDER_CAPSULE", portable_path / "CAPSULE.md", 2200),
    ):
        text = _read_limited(path, limit=limit)
        if not text:
            continue
        sections.extend(
            [
                f"## {label}",
                f"path: {path.relative_to(ACTIVE_ROOT).as_posix()}",
                "```text",
                text,
                "```",
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _available_mount_rows() -> list[str]:
    if not AGENT_MOUNT_ROOT.is_dir():
        return []
    rows: list[str] = []
    for path in sorted(AGENT_MOUNT_ROOT.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        manifest = path / "ION_AGENT_MOUNT_MANIFEST.json"
        capsule = path / ".ion" / "ION_CONTEXT_CAPSULE.yaml"
        if manifest.is_file() or capsule.is_file():
            rows.append(f"- {path.relative_to(ACTIVE_ROOT).as_posix()}")
        if len(rows) >= MAX_ROOT_MOUNT_ROWS:
            break
    return rows


def _root_fallback_context(cwd: Path) -> str:
    rows = _available_mount_rows()
    mount_hint = "\n".join(rows) if rows else "- no generated mounts found"
    return "\n".join(
        [
            "ION Codex Root Context Boundary v0.1",
            f"current_cwd: {cwd}",
            f"active_root: {ACTIVE_ROOT}",
            "mount_truth_state: CODEX_ROOT_SHARED_CONTEXT_FALLBACK_ONLY",
            "shared_codex_solo_boot_context_loaded: false",
            "working_capsule_identity: absent",
            "policy: root-level Codex startup must not treat ION/05_context/current/codex_solo as this chat's unique working capsule.",
            "required_action_for_material_domain_work: launch from a generated codex_agent_mount or explicit context starter capsule so folder-local .ion context is active.",
            "production_authority: false",
            "live_execution_authority: false",
            "accepted_state_authority: false",
            "",
            "## Available Generated Mounts",
            mount_hint,
        ]
    )


def main() -> int:
    payload = _read_stdin()
    cwd = Path(str(payload.get("cwd") or ".")).expanduser().resolve()
    if not _is_relative_to(cwd, ACTIVE_ROOT):
        print(json.dumps(_soft_context(f"cwd is outside active ION root: {cwd}")))
        return 0
    if not (ACTIVE_ROOT / "pyproject.toml").is_file() or not (ACTIVE_ROOT / "ION" / "REPO_AUTHORITY.md").is_file():
        print(json.dumps(_soft_context("active root proof files are missing.")))
        return 0

    sys.path.insert(0, str(PACKAGE_ROOT))
    try:
        from kernel.ion_codex_mount_guard import (
            build_codex_mount_status,
            render_mount_guard_block,
            write_current_mount_status,
        )
        from kernel.ion_codex_operational_posture import (
            build_codex_operational_posture,
            render_operational_posture_block,
            write_current_operational_posture,
        )

        mount_status = build_codex_mount_status(ACTIVE_ROOT)
        write_current_mount_status(ACTIVE_ROOT, mount_status)
        mount_context = render_mount_guard_block(mount_status)
        operational_posture = build_codex_operational_posture(ACTIVE_ROOT)
        write_current_operational_posture(ACTIVE_ROOT, operational_posture)
        operational_context = render_operational_posture_block(operational_posture)
        agent_mount_context = _agent_mount_context(cwd)
        folder_local_context = _folder_local_context(cwd)
        context_blocks = [mount_context, operational_context]
        if agent_mount_context:
            context_blocks.append(agent_mount_context)
        elif folder_local_context:
            context_blocks.append(folder_local_context)
        else:
            context_blocks.append(_root_fallback_context(cwd))
        print(json.dumps({
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n\n".join(context_blocks),
            },
        }))
        return 0
    except Exception as exc:  # pragma: no cover - live hook must fail visible
        print(json.dumps(_soft_context(f"hook error: {exc}")))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
