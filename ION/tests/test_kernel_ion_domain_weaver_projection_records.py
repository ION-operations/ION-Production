from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Any

from kernel import ion_domain_weaver
from kernel import ion_domain_weaver_projection_records as records


def _ready_mount(**extra: Any) -> dict[str, Any]:
    mount = {
        "mount_id": "mount.role.mason",
        "domain_id": "kernel",
        "mount_path": "ION/agents/mason",
        "materialized": True,
        "agents_md_exists": True,
        "config_exists": True,
        "portable_context_manifest_exists": True,
        "portable_communications_exists": True,
        "portable_address_book_exists": True,
        "portable_active_context_package_md_exists": True,
        "portable_context_manifest_path": "context.json",
        "portable_active_context_package_md_path": "ACTIVE.md",
        "portable_agent_path": "AGENTS.md",
        "portable_domain_path": "domain.yaml",
        "portable_relationships_path": "relationships.json",
        "portable_communications_path": "communications.json",
        "portable_address_book_path": "address_book.json",
    }
    mount.update(extra)
    return mount


def test_agent_domain_ids_are_deduplicated_and_ordered() -> None:
    agent = {
        "role_id": "role.mason",
        "registry_primary_domain": "kernel",
        "registry_secondary_domains": [" runtime ", "kernel", "runtime"],
        "domain_ids": ["kernel", "context"],
        "native_codex_mount": {"domain_id": "mount_domain"},
    }

    assert records._agent_domain_ids(agent) == [
        ("kernel", "primary"),
        ("runtime", "secondary"),
        ("context", "member"),
        ("mount_domain", "mount"),
    ]


def test_agent_record_uses_supplied_portable_package_without_filesystem_dependency() -> None:
    package = {"exists": True, "latest_path": "pkg/LATEST.json", "drop_in_ready": True}
    agent = {
        "role_id": "role.mason",
        "display_name": "Mason",
        "registry_primary_domain": "kernel",
        "template_bindings": [" build ", "build", "review"],
    }
    comms = {"available_for_comms": True, "aliases": ["mason"], "can_receive_workpacks": True}

    record = records._agent_record(agent, _ready_mount(), comms, portable_package=package)

    assert record["role_id"] == "role.mason"
    assert record["domain_ids"] == ["kernel"]
    assert record["codex_mount"]["ready"] is True
    assert record["capsule"]["ready"] is True
    assert record["portable_package"] == package
    assert record["template_bindings"] == ["build", "review"]
    assert record["gaps"] == []
    assert record["ready_for_domain_weave"] is True


def test_candidate_domain_record_is_coverage_only_and_does_not_accept_candidate_state() -> None:
    coverage_agent = records._agent_record(
        {
            "role_id": "role.mason",
            "display_name": "Mason",
            "registry_primary_domain": "kernel",
        },
        _ready_mount(),
        {"available_for_comms": True},
        portable_package={"exists": False, "drop_in_ready": False, "latest_path": ""},
    )
    domain = {
        "domain_id": "ion_vnext_kernel",
        "display_name": "Kernel Candidate",
        "fact_posture": "candidate",
        "accepted_ion_state": True,
        "paths": ["ION/04_packages/kernel"],
        "local_read_first_files": ["ION/03_registry/domains/kernel.domain.yaml"],
    }

    coverage_rows = records._candidate_coverage_rows(domain, {"role.mason": coverage_agent})
    record = records._domain_record(domain, [], coverage_rows)

    assert [row["role_id"] for row in coverage_rows] == ["role.mason"]
    assert record["candidate_domain"] is True
    assert record["accepted_ion_state"] is False
    assert record["status"] == "candidate_covered"
    assert record["candidate_coverage_count"] == 1
    assert record["gaps"] == []


def test_domain_weaver_private_projection_record_surface_remains_compatible() -> None:
    assert ion_domain_weaver.CANDIDATE_DOMAIN_ROLE_COVERAGE is records.CANDIDATE_DOMAIN_ROLE_COVERAGE
    assert ion_domain_weaver._role_id is records._role_id
    assert ion_domain_weaver._domain_id is records._domain_id
    assert ion_domain_weaver._agent_domain_ids is records._agent_domain_ids
    assert ion_domain_weaver._agent_mount is records._agent_mount
    assert ion_domain_weaver._domain_record is records._domain_record


def test_projection_records_helper_has_no_reverse_or_stateful_imports() -> None:
    sys.modules.pop("kernel.ion_domain_weaver_projection_records", None)
    sys.modules.pop("kernel.ion_domain_weaver", None)

    module = importlib.import_module("kernel.ion_domain_weaver_projection_records")

    assert module._role_id({"role_id": "role.mason"}) == "role.mason"
    assert "kernel.ion_domain_weaver" not in sys.modules

    source_path = Path(module.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    observed_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            observed_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            observed_imports.append(node.module or "")

    assert observed_imports == ["__future__", "typing"]
    forbidden_import_fragments = (
        "ion_domain_weaver",
        "materializ",
        "dispatcher",
        "operator_action",
        "projection_refresh",
        "queue",
        "registry",
        "live",
        "topology",
        "cockpit",
        "secret",
    )
    assert not any(
        fragment in imported
        for imported in observed_imports
        for fragment in forbidden_import_fragments
    )
