from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

from kernel import ion_domain_weaver
from kernel import ion_domain_weaver_catalog as catalog


CATALOG_NAMES = (
    "SCHEMA_ID",
    "PROMOTION_REVIEW_SCHEMA_ID",
    "PROMOTION_GATE_SCHEMA_ID",
    "DOGFOOD_CONTEXT_CAPSULE_SCHEMA_ID",
    "DOGFOOD_NEXT_PACKET_SCHEMA_ID",
    "STEWARD_READY_REVIEW_SCHEMA_ID",
    "PHASE_CLOSURE_REVIEW_SCHEMA_ID",
    "FOUNDING_DOMAIN_ASSEMBLY_SCHEMA_ID",
    "OPERATOR_ACTION_SCHEMA_ID",
    "OPERATOR_ACTION_RECORD_SCHEMA_ID",
)

LOW_AUTHORITY_CATALOG_NAMES = (
    "SCHEMA_ID",
    "PROMOTION_REVIEW_SCHEMA_ID",
    "PROMOTION_GATE_SCHEMA_ID",
    "DOGFOOD_CONTEXT_CAPSULE_SCHEMA_ID",
    "DOGFOOD_NEXT_PACKET_SCHEMA_ID",
    "STEWARD_READY_REVIEW_SCHEMA_ID",
    "PHASE_CLOSURE_REVIEW_SCHEMA_ID",
    "FOUNDING_DOMAIN_ASSEMBLY_SCHEMA_ID",
    "OPERATOR_ACTION_SCHEMA_ID",
    "OPERATOR_ACTION_RECORD_SCHEMA_ID",
)

AUTHORITY_BEARING_NAMES_RETAINED_IN_MONOLITH = (
    "MATERIALIZATION_SCHEMA_ID",
    "PROMOTION_MATERIALIZATION_SCHEMA_ID",
    "PROMOTION_GATE_MATERIALIZATION_SCHEMA_ID",
    "DOGFOOD_CONTEXT_CAPSULE_MATERIALIZATION_SCHEMA_ID",
    "STEWARD_READY_REVIEW_MATERIALIZATION_SCHEMA_ID",
    "PHASE_CLOSURE_REVIEW_MATERIALIZATION_SCHEMA_ID",
    "UI_DEVELOPMENT_SCHEMA_ID",
    "FOUNDING_DOMAIN_ASSEMBLY_MATERIALIZATION_SCHEMA_ID",
    "OPERATOR_ACTION_HISTORY_SCHEMA_ID",
    "DOMAIN_WEAVER_ACTION_CONFIRMATION",
)


def test_catalog_exports_are_preserved_on_domain_weaver_import_surface() -> None:
    for name in CATALOG_NAMES:
        assert hasattr(catalog, name)
        assert hasattr(ion_domain_weaver, name)


def test_catalog_values_match_domain_weaver_compatibility_names() -> None:
    for name in CATALOG_NAMES:
        assert getattr(ion_domain_weaver, name) == getattr(catalog, name)


def test_catalog_slice_excludes_disallowed_name_fragments() -> None:
    forbidden_fragments = (
        "LIVE_BINDING",
        "TOPOLOGY",
        "UI",
        "PROJECTION",
        "MATERIALIZATION",
        "QUEUE",
        "DISPATCH",
        "ACTION_POLICY",
        "OPERATOR_HISTORY",
        "OPERATOR_ACTION_HISTORY",
        "ACTIVE",
        "REGISTRY",
    )

    for name in LOW_AUTHORITY_CATALOG_NAMES:
        assert not any(fragment in name for fragment in forbidden_fragments)
        assert not any(fragment.lower() in getattr(catalog, name).lower() for fragment in forbidden_fragments)


def test_authority_bearing_catalog_slice_is_identifier_only() -> None:
    for name in AUTHORITY_BEARING_NAMES_RETAINED_IN_MONOLITH:
        assert not hasattr(catalog, name)
        assert isinstance(getattr(ion_domain_weaver, name), str)


def test_catalog_has_no_reverse_or_stateful_imports() -> None:
    sys.modules.pop("kernel.ion_domain_weaver_catalog", None)
    sys.modules.pop("kernel.ion_domain_weaver", None)

    module = importlib.import_module("kernel.ion_domain_weaver_catalog")

    assert module.PROMOTION_REVIEW_SCHEMA_ID == catalog.PROMOTION_REVIEW_SCHEMA_ID
    assert "kernel.ion_domain_weaver" not in sys.modules

    source_path = Path(module.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    observed_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            observed_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            observed_imports.append(node.module or "")

    assert observed_imports == ["__future__"]
    forbidden_import_fragments = (
        "ion_domain_weaver",
        "materializ",
        "dispatcher",
        "live_binding",
        "projection",
        "queue_runner",
        "topology",
        "cockpit",
        "joc_cockpit",
    )
    assert not any(
        fragment in imported
        for imported in observed_imports
        for fragment in forbidden_import_fragments
    )
