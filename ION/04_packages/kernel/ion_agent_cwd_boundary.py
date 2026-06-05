"""Agent working-directory boundary projection for ION movements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .ion_path_authority import DEFAULT_WORKSPACE_MANIFEST
from .ion_workspace_root_registry import (
    CLASS_ACTIVE_ION_CONTROL_ROOT,
    CLASS_EXPORT_OUTPUT_ROOT,
    CLASS_FORBIDDEN_EXTERNAL_ROOT,
    CLASS_ION_CONTENT_ROOT,
    CLASS_UNKNOWN_ROOT,
    build_workspace_root_registry,
    classify_workspace_path,
)


SCHEMA_ID = "ion.agent_cwd_boundary.v1"
CODEX_AGENT_MOUNT_MANIFEST = "ION_AGENT_MOUNT_MANIFEST.json"


def _resolve(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve(strict=False)
    parent = parent.resolve(strict=False)
    return path == parent or parent in path.parents


def _add(items: list[dict[str, Any]], code: str, detail: str, **extra: Any) -> None:
    item = {"code": code, "detail": detail}
    item.update(extra)
    items.append(item)


def _blocked_alias_for_path(registry: Mapping[str, Any], path: Path) -> dict[str, Any] | None:
    target = path.resolve(strict=False)
    for alias in registry.get("aliases", []):
        if not isinstance(alias, Mapping):
            continue
        alias_path = _resolve(str(alias.get("alias_path") or ""))
        if target == alias_path or _is_within(target, alias_path):
            if alias.get("allowed_to_create_alias_path") is False:
                return dict(alias)
    return None


def _default_worker_cwd(
    *,
    active_ion_root: Path,
    target_project_root: Path,
    target_root_class: str,
) -> Path:
    if target_root_class in {CLASS_ACTIVE_ION_CONTROL_ROOT, CLASS_ION_CONTENT_ROOT}:
        return active_ion_root
    if target_root_class == CLASS_EXPORT_OUTPUT_ROOT:
        return active_ion_root
    return target_project_root


def _codex_agent_mount_allowance(
    *,
    envelope: Mapping[str, Any],
    active_ion_root: Path,
    worker_launch_cwd: Path,
    target_command_cwd: Path,
) -> dict[str, Any]:
    """Validate the one allowed active-root subdir launch case.

    Codex agent/domain mounts intentionally launch from a generated folder under
    the active repo so Codex can see folder-local AGENTS.md and .codex config.
    That is not a sibling-root movement, but it still needs proof.
    """

    blockers: list[dict[str, Any]] = []
    if not _is_within(worker_launch_cwd, active_ion_root):
        _add(blockers, "CODEX_AGENT_MOUNT_OUTSIDE_ACTIVE_ROOT", "Codex agent mount cwd must stay under active_ion_root")
    if target_command_cwd != worker_launch_cwd:
        _add(
            blockers,
            "CODEX_AGENT_MOUNT_COMMAND_CWD_MISMATCH",
            "target_command_cwd must equal worker_launch_cwd for a generated Codex agent mount",
        )
    declared_manifest = str(
        envelope.get("codex_agent_mount_manifest")
        or envelope.get("ion_codex_agent_mount_manifest")
        or ""
    ).strip()
    manifest_path = _resolve(declared_manifest) if declared_manifest else worker_launch_cwd / CODEX_AGENT_MOUNT_MANIFEST
    if not _is_within(manifest_path, worker_launch_cwd):
        _add(
            blockers,
            "CODEX_AGENT_MOUNT_MANIFEST_OUTSIDE_CWD",
            "Codex agent mount manifest must be inside worker_launch_cwd",
            manifest_path=str(manifest_path),
        )
    required = {
        "manifest": manifest_path,
        "agents_md": worker_launch_cwd / "AGENTS.md",
        "codex_config": worker_launch_cwd / ".codex" / "config.toml",
    }
    for label, path in required.items():
        if not path.is_file():
            _add(
                blockers,
                f"CODEX_AGENT_MOUNT_{label.upper()}_MISSING",
                f"Codex agent mount requires {label}",
                path=str(path),
            )
    return {
        "accepted": not blockers,
        "mount_path": str(worker_launch_cwd),
        "manifest_path": str(manifest_path),
        "blocker_count": len(blockers),
        "blocker_codes": [item["code"] for item in blockers],
        "blockers": blockers,
    }


def build_agent_cwd_boundary(
    envelope: Mapping[str, Any],
    *,
    active_root: str | Path | None = None,
    manifest_path: str | Path | None = None,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Project control-plane, worker-launch, and target-command cwd facts."""

    loaded_registry = dict(registry or build_workspace_root_registry(manifest_path or DEFAULT_WORKSPACE_MANIFEST))
    manifest = loaded_registry.get("manifest") if isinstance(loaded_registry.get("manifest"), Mapping) else {}
    active_ion_root = _resolve(
        envelope.get("active_ion_root")
        or active_root
        or manifest.get("active_repo_root")
        or Path.cwd()
    )
    workspace_root = _resolve(envelope.get("workspace_root") or manifest.get("workspace_root") or active_ion_root.parent)
    control_plane_cwd = _resolve(envelope.get("control_plane_cwd") or envelope.get("actual_cwd") or active_ion_root)
    control_plane_realpath = _resolve(envelope.get("control_plane_realpath") or envelope.get("actual_realpath") or control_plane_cwd)
    target_project_raw = envelope.get("target_project_root")
    target_content_raw = envelope.get("target_content_root") or target_project_raw
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not target_project_raw:
        _add(blockers, "AGENT_CWD_TARGET_PROJECT_ROOT_MISSING", "target_project_root is required to bind worker cwd")
        target_project_root = active_ion_root
    else:
        target_project_root = _resolve(str(target_project_raw))

    target_content_root = _resolve(str(target_content_raw or target_project_root))
    target_classification = classify_workspace_path(target_project_root, registry=loaded_registry)
    target_root_class = str(target_classification.get("root_class") or CLASS_UNKNOWN_ROOT)
    target_root_id = target_classification.get("root_id")
    alias = _blocked_alias_for_path(loaded_registry, target_project_root)
    if alias:
        _add(
            blockers,
            "AGENT_CWD_BLOCKED_ALIAS_ROOT",
            "target_project_root resolves under a blocked root alias",
            alias=alias,
        )
    if target_root_class == CLASS_UNKNOWN_ROOT:
        _add(
            blockers,
            "AGENT_CWD_UNKNOWN_TARGET_ROOT",
            "target_project_root is inside the workspace but not registered",
            target_project_root=str(target_project_root),
        )
    if target_root_class == CLASS_FORBIDDEN_EXTERNAL_ROOT:
        _add(
            blockers,
            "AGENT_CWD_FORBIDDEN_TARGET_ROOT",
            "target_project_root is outside the governed workspace",
            target_project_root=str(target_project_root),
        )
    if target_root_class not in {CLASS_UNKNOWN_ROOT, CLASS_FORBIDDEN_EXTERNAL_ROOT} and not target_project_root.exists():
        _add(
            blockers,
            "AGENT_CWD_TARGET_PROJECT_ROOT_MISSING_ON_DISK",
            "target_project_root must exist before an agent can launch there",
            target_project_root=str(target_project_root),
        )
    if not _is_within(target_content_root, target_project_root) and target_root_class != CLASS_EXPORT_OUTPUT_ROOT:
        _add(
            blockers,
            "AGENT_CWD_TARGET_CONTENT_OUTSIDE_PROJECT",
            "target_content_root must stay within target_project_root",
            target_project_root=str(target_project_root),
            target_content_root=str(target_content_root),
        )

    requested_worker_cwd = str(envelope.get("worker_launch_cwd") or "").strip()
    worker_launch_cwd = _resolve(requested_worker_cwd) if requested_worker_cwd else _default_worker_cwd(
        active_ion_root=active_ion_root,
        target_project_root=target_project_root,
        target_root_class=target_root_class,
    )
    requested_command_cwd = str(envelope.get("target_command_cwd") or "").strip()
    target_command_cwd = _resolve(requested_command_cwd) if requested_command_cwd else worker_launch_cwd

    if not _is_within(control_plane_cwd, active_ion_root):
        _add(
            warnings,
            "CONTROL_PLANE_CWD_OUTSIDE_ACTIVE_ION_ROOT",
            "control-plane cwd is not inside the active ION root",
            control_plane_cwd=str(control_plane_cwd),
            active_ion_root=str(active_ion_root),
        )
    if not _is_within(worker_launch_cwd, workspace_root):
        _add(
            blockers,
            "WORKER_LAUNCH_CWD_OUTSIDE_WORKSPACE",
            "worker launch cwd must stay inside workspace_root",
            worker_launch_cwd=str(worker_launch_cwd),
            workspace_root=str(workspace_root),
        )
    if target_root_class not in {CLASS_ACTIVE_ION_CONTROL_ROOT, CLASS_ION_CONTENT_ROOT, CLASS_EXPORT_OUTPUT_ROOT}:
        if worker_launch_cwd != target_project_root:
            _add(
                blockers,
                "WORKER_LAUNCH_CWD_TARGET_MISMATCH",
                "sibling or external project movement must launch the worker from target_project_root",
                worker_launch_cwd=str(worker_launch_cwd),
                target_project_root=str(target_project_root),
            )
        if target_command_cwd != target_project_root:
            _add(
                blockers,
                "TARGET_COMMAND_CWD_TARGET_MISMATCH",
                "project-local commands must run from target_project_root",
                target_command_cwd=str(target_command_cwd),
                target_project_root=str(target_project_root),
            )
    codex_agent_mount = None
    if target_root_class in {CLASS_ACTIVE_ION_CONTROL_ROOT, CLASS_ION_CONTENT_ROOT} and worker_launch_cwd != active_ion_root:
        codex_agent_mount = _codex_agent_mount_allowance(
            envelope=envelope,
            active_ion_root=active_ion_root,
            worker_launch_cwd=worker_launch_cwd,
            target_command_cwd=target_command_cwd,
        )
        if not codex_agent_mount["accepted"]:
            blockers.extend(codex_agent_mount["blockers"])

    accepted = not blockers
    return {
        "schema_id": SCHEMA_ID,
        "accepted": accepted,
        "status": "AGENT_CWD_BOUND" if accepted else "AGENT_CWD_BLOCKED",
        "workspace_root": str(workspace_root),
        "active_ion_root": str(active_ion_root),
        "control_plane_cwd": str(control_plane_cwd),
        "control_plane_realpath": str(control_plane_realpath),
        "worker_launch_cwd": str(worker_launch_cwd),
        "worker_launch_realpath": str(worker_launch_cwd),
        "target_command_cwd": str(target_command_cwd),
        "target_command_realpath": str(target_command_cwd),
        "target_project_root": str(target_project_root),
        "target_content_root": str(target_content_root),
        "target_root_id": target_root_id,
        "target_root_class": target_root_class,
        "target_root_relation": target_classification.get("root_relation"),
        "cwd_layers": {
            "control_plane_cwd": "where ION queue, receipts, reports, and context packages are prepared",
            "worker_launch_cwd": "where the Codex worker process is launched",
            "target_command_cwd": "where project-local commands must run",
        },
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blocker_codes": [item["code"] for item in blockers],
        "warning_codes": [item["code"] for item in warnings],
        "blockers": blockers,
        "warnings": warnings,
        "codex_agent_mount": codex_agent_mount,
        "active_root_subdir_worker_launch_allowed": bool(codex_agent_mount and codex_agent_mount["accepted"]),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Project ION agent working-directory boundaries")
    parser.add_argument("--input", required=True)
    parser.add_argument("--active-root")
    parser.add_argument("--manifest-path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    envelope = json.loads(Path(args.input).read_text(encoding="utf-8"))
    boundary = build_agent_cwd_boundary(
        envelope,
        active_root=args.active_root,
        manifest_path=args.manifest_path,
    )
    if args.json:
        print(json.dumps(boundary, indent=2, sort_keys=True))
    else:
        print(boundary["status"])
    return 0 if boundary["accepted"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
