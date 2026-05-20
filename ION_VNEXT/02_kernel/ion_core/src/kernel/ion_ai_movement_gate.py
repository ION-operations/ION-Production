"""Read-only AI movement gate evaluator for ION workspace roots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePath
from typing import Any

from .ion_path_authority import decide_path_authority
from .ion_workspace_root_registry import (
    CLASS_ACTIVE_ION_CONTROL_ROOT,
    CLASS_ARCHIVE_WITNESS_ROOT,
    CLASS_CARRIER_INTEGRATION_ROOT,
    CLASS_EXPORT_OUTPUT_ROOT,
    CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT,
    CLASS_FORBIDDEN_EXTERNAL_ROOT,
    CLASS_INTAKE_ROOT,
    CLASS_ION_CONTENT_ROOT,
    CLASS_PRODUCT_PROJECTION_ROOT,
    CLASS_REFERENCE_LIBRARY_ROOT,
    CLASS_SECRET_BOUNDARY_ROOT,
    CLASS_UNKNOWN_ROOT,
    CLASS_WORKSPACE_ESTATE_ROOT,
    build_workspace_root_registry,
    classify_workspace_path,
)


SCHEMA_ID = "ion.ai_movement_gate_decision.v1"

AUTHORITY_FLAGS = (
    "production_authority",
    "live_execution_authority",
    "accepted_state_claim",
    "git_push_authority",
    "deletion_authority",
    "service_restart_authority",
)

BASE_ROOT_BY_MOVEMENT_CLASS = {
    "ION_KERNEL_CONTROL_MOVEMENT": "active_repo",
    "WORKSPACE_MANIFEST_MOVEMENT": "workspace",
    "CUSTOM_GPT_RELEASE_MOVEMENT": "workspace",
    "BROWSER_EXTENSION_MOVEMENT": "workspace",
    "MCP_BRIDGE_MOVEMENT": "workspace",
    "LOCAL_DAEMON_MOVEMENT": "workspace",
    "DAIMON_PROJECT_MOVEMENT": "workspace",
    "INTAKE_ROUTING_MOVEMENT": "workspace",
    "EXPORT_PACKAGE_MOVEMENT": "workspace",
    "ARCHIVE_REFERENCE_MOVEMENT": "workspace",
}

ALLOWED_WRITE_ROOT_IDS_BY_MOVEMENT_CLASS = {
    "ION_KERNEL_CONTROL_MOVEMENT": {"active_ion_control", "ion_content"},
    "WORKSPACE_MANIFEST_MOVEMENT": {"workspace_estate"},
    "CUSTOM_GPT_RELEASE_MOVEMENT": {"ion_gpt", "product_packager", "ion_exports_local"},
    "BROWSER_EXTENSION_MOVEMENT": {"browser_extension"},
    "MCP_BRIDGE_MOVEMENT": {"mcp"},
    "LOCAL_DAEMON_MOVEMENT": {"local_daemon", "systemd"},
    "DAIMON_PROJECT_MOVEMENT": {"daimon"},
    "INTAKE_ROUTING_MOVEMENT": {"needs_routed"},
    "EXPORT_PACKAGE_MOVEMENT": {"ion_exports_local", "ion_gpt", "product_packager"},
    "ARCHIVE_REFERENCE_MOVEMENT": {"quarentine", "aim_os", "atlas", "wisdomnet"},
}


def _resolve(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve(strict=False)
    parent = parent.resolve(strict=False)
    return path == parent or parent in path.parents


def _has_parent_segment(path: str | Path) -> bool:
    return any(part == ".." for part in PurePath(str(path)).parts)


def _has_dotenv_part(path: str | Path) -> bool:
    return any(part == ".env" or part.startswith(".env.") for part in PurePath(str(path)).parts)


def _has_vault_part(path: str | Path) -> bool:
    return any(part == "ION_VAULT_LOCAL" for part in PurePath(str(path)).parts)


def _get(envelope: dict[str, Any], key: str, default: Any = None) -> Any:
    nested = envelope.get("ai_movement_root_envelope")
    if isinstance(nested, dict) and key in nested:
        return nested.get(key)
    return envelope.get(key, default)


def _add_blocker(blockers: list[dict[str, Any]], code: str, detail: str, **extra: Any) -> None:
    item = {"code": code, "detail": detail}
    item.update(extra)
    blockers.append(item)


def _add_warning(warnings: list[dict[str, Any]], code: str, detail: str, **extra: Any) -> None:
    item = {"code": code, "detail": detail}
    item.update(extra)
    warnings.append(item)


def _root_entry_by_id(registry: dict[str, Any], root_id: str | None) -> dict[str, Any] | None:
    if root_id is None:
        return None
    for entry in registry.get("roots", []):
        if entry.get("root_id") == root_id:
            return entry
    return None


def _alias_for_path(registry: dict[str, Any], path: Path) -> dict[str, Any] | None:
    target = path.resolve(strict=False)
    for alias in registry.get("aliases", []):
        alias_path = _resolve(alias.get("alias_path", ""))
        if target == alias_path or _is_within(target, alias_path):
            return alias
    return None


def _is_manifest_path(path: Path, registry: dict[str, Any]) -> bool:
    manifest = _resolve(registry["manifest"]["manifest_path"])
    return path.resolve(strict=False) == manifest


def _allowed_write_root_ids(movement_class: str, target_root_id: str | None) -> set[str]:
    allowed = set(ALLOWED_WRITE_ROOT_IDS_BY_MOVEMENT_CLASS.get(movement_class, set()))
    if target_root_id:
        allowed.add(target_root_id)
    return allowed


def evaluate_ai_movement_gate(
    envelope: dict[str, Any],
    *,
    manifest_path: str | Path | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a movement envelope without mutating workspace state."""

    loaded_registry = registry or build_workspace_root_registry(manifest_path)
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    path_authority_decisions: list[dict[str, Any]] = []
    root_classifications: list[dict[str, Any]] = []

    if loaded_registry.get("schema_id") != "ion.workspace_root_registry_projection.v1":
        _add_blocker(blockers, "ROOT_REGISTRY_SCHEMA_MISMATCH", "root registry projection schema mismatch")
    if loaded_registry.get("conflicts"):
        _add_blocker(
            blockers,
            "ROOT_REGISTRY_CONFLICT",
            "root registry has unresolved conflicts",
            conflicts=loaded_registry.get("conflicts", []),
        )

    actual_cwd = _get(envelope, "actual_cwd")
    actual_realpath = _get(envelope, "actual_realpath")
    expected_cwd = _get(envelope, "expected_cwd")
    expected_realpath = _get(envelope, "expected_realpath")
    if not actual_cwd:
        _add_blocker(blockers, "WRONG_ROOT_CWD", "actual_cwd missing")
    if not actual_realpath:
        _add_blocker(blockers, "EXPECTED_REALPATH_MISMATCH", "actual_realpath missing")
    if not expected_cwd:
        _add_blocker(blockers, "WRONG_ROOT_CWD", "expected_cwd missing")
    if not expected_realpath:
        _add_blocker(blockers, "EXPECTED_REALPATH_MISMATCH", "expected_realpath missing")
    if actual_cwd and expected_cwd and str(_resolve(actual_cwd)) != str(_resolve(expected_cwd)):
        _add_blocker(
            blockers,
            "WRONG_ROOT_CWD",
            "actual cwd does not match expected cwd",
            actual_cwd=str(_resolve(actual_cwd)),
            expected_cwd=str(_resolve(expected_cwd)),
        )
    if actual_realpath and expected_realpath and str(_resolve(actual_realpath)) != str(_resolve(expected_realpath)):
        _add_blocker(
            blockers,
            "EXPECTED_REALPATH_MISMATCH",
            "actual realpath does not match expected realpath",
            actual_realpath=str(_resolve(actual_realpath)),
            expected_realpath=str(_resolve(expected_realpath)),
        )

    movement_class = str(_get(envelope, "movement_class") or "")
    if not movement_class:
        _add_blocker(blockers, "TEMPLATE_MOVEMENT_CLASS_MISMATCH", "movement_class missing")
    base_root = BASE_ROOT_BY_MOVEMENT_CLASS.get(movement_class, "active_repo")

    target_project_root = _get(envelope, "target_project_root")
    target_content_root = _get(envelope, "target_content_root")
    target_classification: dict[str, Any] | None = None
    target_entry: dict[str, Any] | None = None
    if not target_project_root:
        _add_blocker(blockers, "TARGET_PROJECT_ROOT_MISSING", "target_project_root missing")
    else:
        target_path = _resolve(target_project_root)
        alias = _alias_for_path(loaded_registry, target_path)
        if alias and not alias.get("allowed_to_create_alias_path", False):
            _add_blocker(
                blockers,
                "DUPLICATE_TOP_LEVEL_ROOT_CREATION",
                "target path resolves to blocked root alias",
                alias=alias,
            )
        target_classification = classify_workspace_path(target_path, registry=loaded_registry)
        root_classifications.append(target_classification)
        target_entry = _root_entry_by_id(loaded_registry, target_classification.get("root_id"))
        if target_classification["root_class"] == CLASS_UNKNOWN_ROOT:
            _add_blocker(blockers, "UNKNOWN_ROOT_CLASS", "target root class is unknown", path=str(target_path))
            if target_path.parent == _resolve(loaded_registry["manifest"]["workspace_root"]):
                _add_blocker(
                    blockers,
                    "DUPLICATE_TOP_LEVEL_ROOT_CREATION",
                    "target would create or use an unregistered top-level workspace root",
                    path=str(target_path),
                )
        elif target_classification["root_class"] == CLASS_FORBIDDEN_EXTERNAL_ROOT:
            _add_blocker(blockers, "FORBIDDEN_ROOT_CLASS", "target root is outside workspace", path=str(target_path))
    if not target_content_root:
        _add_blocker(blockers, "TARGET_CONTENT_ROOT_OUTSIDE_TARGET_PROJECT", "target_content_root missing")
    elif target_project_root and not _is_within(_resolve(target_content_root), _resolve(target_project_root)):
        target_root_class = target_classification.get("root_class") if target_classification else None
        if target_root_class not in {CLASS_PRODUCT_PROJECTION_ROOT, CLASS_EXPORT_OUTPUT_ROOT}:
            _add_blocker(
                blockers,
                "TARGET_CONTENT_ROOT_OUTSIDE_TARGET_PROJECT",
                "target_content_root is outside target_project_root",
                target_project_root=str(_resolve(target_project_root)),
                target_content_root=str(_resolve(target_content_root)),
            )

    if movement_class and target_entry:
        allowed_classes = set(target_entry.get("allowed_movement_classes") or [])
        if movement_class not in allowed_classes:
            _add_blocker(
                blockers,
                "TEMPLATE_MOVEMENT_CLASS_MISMATCH",
                "movement_class is not allowed for target root",
                movement_class=movement_class,
                target_root_id=target_entry.get("root_id"),
                allowed_movement_classes=sorted(allowed_classes),
            )

    context_required = bool(_get(envelope, "context_proof_required", True))
    if context_required and not _get(envelope, "domain_context_package"):
        _add_blocker(blockers, "DOMAIN_PACKAGE_MISSING", "domain_context_package missing")
    if not _get(envelope, "active_template"):
        _add_blocker(blockers, "TEMPLATE_MISSING", "active_template missing")

    requested_authority = _get(envelope, "requested_authority", {}) or _get(envelope, "authority", {}) or {}
    for flag in AUTHORITY_FLAGS:
        if requested_authority.get(flag) is True:
            _add_blocker(
                blockers,
                f"{flag.upper()}_UNGRANTED",
                f"{flag} requested without movement gate authority",
            )

    planned_reads = list(_get(envelope, "planned_reads", []) or [])
    for raw_path in planned_reads:
        if _has_vault_part(raw_path) or _has_dotenv_part(raw_path):
            _add_blocker(blockers, "VAULT_OR_ENV_READ_ATTEMPT", "planned read targets vault or env path", raw_path=str(raw_path))
        decision = decide_path_authority(raw_path, purpose="read", base_root=base_root, manifest_path=manifest_path)
        path_authority_decisions.append(decision)
        if not decision["authorized"]:
            _add_blocker(blockers, "PATH_AUTHORITY_REJECTED", "path authority rejected planned read", decision=decision)

    allowed_write_root_ids = _allowed_write_root_ids(movement_class, target_classification.get("root_id") if target_classification else None)
    planned_writes = list(_get(envelope, "planned_writes", []) or [])
    for raw_path in planned_writes:
        decision = decide_path_authority(raw_path, purpose="write", base_root=base_root, manifest_path=manifest_path)
        path_authority_decisions.append(decision)
        resolved = _resolve(decision["resolved_path"])
        if not decision["authorized"]:
            _add_blocker(blockers, "PATH_AUTHORITY_REJECTED", "path authority rejected planned write", decision=decision)
        if _has_parent_segment(raw_path) and movement_class == "ION_KERNEL_CONTROL_MOVEMENT":
            _add_blocker(
                blockers,
                "ACTIVE_ROOT_PARENT_RELATIVE_WRITE",
                "active ION movement attempted parent-relative write",
                raw_path=str(raw_path),
            )
        write_classification = classify_workspace_path(resolved, registry=loaded_registry)
        root_classifications.append(write_classification)
        write_root_id = write_classification.get("root_id")
        if _is_manifest_path(resolved, loaded_registry) and movement_class == "WORKSPACE_MANIFEST_MOVEMENT":
            continue
        if write_classification["root_class"] == CLASS_UNKNOWN_ROOT:
            _add_blocker(blockers, "UNKNOWN_ROOT_CLASS", "planned write root is unknown", path=str(resolved))
        elif write_classification["root_class"] == CLASS_FORBIDDEN_EXTERNAL_ROOT:
            _add_blocker(blockers, "FORBIDDEN_ROOT_CLASS", "planned write is outside workspace", path=str(resolved))
        elif write_classification["root_class"] == CLASS_SECRET_BOUNDARY_ROOT:
            _add_blocker(blockers, "VAULT_OR_ENV_READ_ATTEMPT", "planned write targets secret boundary", path=str(resolved))
        elif write_root_id not in allowed_write_root_ids:
            _add_blocker(
                blockers,
                "SIBLING_ROOT_IMPLICIT_EDIT",
                "planned write root is not allowed by movement class",
                movement_class=movement_class,
                write_root_id=write_root_id,
                allowed_write_root_ids=sorted(allowed_write_root_ids),
                path=str(resolved),
            )

    planned_artifacts = list(_get(envelope, "planned_artifacts", []) or [])
    for raw_path in planned_artifacts:
        decision = decide_path_authority(raw_path, purpose="artifact", base_root=base_root, manifest_path=manifest_path)
        path_authority_decisions.append(decision)
        if not decision["authorized"]:
            code = "EXPORT_OUTSIDE_WORKSPACE"
            if decision["reason_code"] == "ARTIFACT_INSIDE_ACTIVE_REPO":
                code = "ARTIFACT_INSIDE_ACTIVE_REPO"
            _add_blocker(blockers, code, "path authority rejected planned artifact", decision=decision)

    settlement_target = _get(envelope, "settlement_target")
    if not settlement_target:
        _add_blocker(blockers, "MISSING_SETTLEMENT_TARGET", "settlement_target missing")
    receipt_paths = list(_get(envelope, "receipt_paths", []) or [])
    required_receipt_markers = {
        "signons": "MISSING_SIGNON_RECEIPT",
        "leases": "MISSING_LEASE_RECEIPT",
        "signoffs": "MISSING_SIGNOFF_RECEIPT",
    }
    for marker, code in required_receipt_markers.items():
        if not any(marker in str(path) for path in receipt_paths):
            _add_blocker(blockers, code, f"receipt_paths missing {marker} receipt path")

    for warning in loaded_registry.get("warnings", []):
        _add_warning(warnings, warning.get("type", "ROOT_REGISTRY_WARNING"), "root registry warning", warning=warning)

    accepted = not blockers
    return {
        "schema_id": SCHEMA_ID,
        "accepted": accepted,
        "verdict": "ACCEPTED" if accepted else "BLOCKED",
        "movement_class": movement_class or None,
        "target_root_id": target_classification.get("root_id") if target_classification else None,
        "target_root_class": target_classification.get("root_class") if target_classification else None,
        "target_root_relation": target_classification.get("root_relation") if target_classification else None,
        "blockers": blockers,
        "warnings": warnings,
        "path_authority_decisions": path_authority_decisions,
        "root_classifications": root_classifications,
        "required_receipts": receipt_paths,
        "settlement_target": settlement_target,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only ION AI movement gate evaluator")
    parser.add_argument("--input", required=True, help="Path to a JSON movement envelope")
    parser.add_argument("--manifest-path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    envelope = json.loads(Path(args.input).read_text(encoding="utf-8"))
    decision = evaluate_ai_movement_gate(envelope, manifest_path=args.manifest_path)
    if args.json:
        print(json.dumps(decision, indent=2, sort_keys=True))
    else:
        print(decision["verdict"])
    return 0 if decision["accepted"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
