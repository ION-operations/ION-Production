from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path

from kernel import ion_domain_weaver_packet_templates as templates
from kernel.ion_domain_weaver_catalog import DOGFOOD_NEXT_PACKET_SCHEMA_ID


def test_work_request_template_builds_stable_low_authority_codex_request() -> None:
    payload = {"source": {"items": ["one"]}}
    result = templates.build_domain_weaver_codex_work_request_template(
        request_id="codex_req_domain_weaver_packet_template_factory_20260603_attempt_001",
        objective="Build a deterministic helper seam only.",
        requested_by="domain_weaver_packet_template_factory",
        work_class="packet_template_factory_seam",
        lane_id="source_seam_lane",
        route_family="domain_weaver_packet_template_factories",
        request_kind="domain_weaver_packet_template_factory_candidate",
        agent_role="role.mason",
        supporting_roles=["role.nemesis", "", "role.scribe", "role.nemesis"],
        required_context_reads=[
            "ION/04_packages/kernel/ion_domain_weaver.py",
            "",
            "ION/04_packages/kernel/ion_domain_weaver.py",
            "ION/tests/test_kernel_ion_agent_control_plane.py",
        ],
        payload_key="domain_weaver_packet_template_factory",
        payload=payload,
    )

    assert result["schema_id"] == templates.WORK_REQUEST_SCHEMA_ID
    assert result["objective_sha256"] == hashlib.sha256(result["objective"].encode("utf-8")).hexdigest()
    assert result["status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert result["requested_authority"] == templates.denied_domain_weaver_authority()
    assert result["ai_movement_root_envelope"] == templates.domain_weaver_root_envelope()
    assert result["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert result["required_context_reads"] == [
        "ION/04_packages/kernel/ion_domain_weaver.py",
        "ION/tests/test_kernel_ion_agent_control_plane.py",
    ]
    assert result["return_contract_sections"] == list(templates.DEFAULT_RETURN_CONTRACT_SECTIONS)
    assert result["domain_weaver_packet_template_factory"] == payload

    payload["source"]["items"].append("mutated")
    assert result["domain_weaver_packet_template_factory"]["source"]["items"] == ["one"]


def test_next_packet_candidate_template_uses_catalog_schema_and_no_authority_escalation() -> None:
    result = templates.build_domain_weaver_next_packet_candidate_template(
        packet_id="PCKT-DOMAIN-WEAVER-PACKET-TEMPLATE-FACTORY-SEAM-20260603",
        selected_domain="packet_template_factories",
        objective="Fan in packet template factory candidates.",
        why_this_next="The candidate helper seam is ready for review.",
        required_context_reads=["a.json", "a.json", "", "b.md"],
        expected_changed_paths=["ION/04_packages/kernel/ion_domain_weaver_packet_templates.py"],
    )

    assert result == {
        "schema_id": DOGFOOD_NEXT_PACKET_SCHEMA_ID,
        "packet_id": "PCKT-DOMAIN-WEAVER-PACKET-TEMPLATE-FACTORY-SEAM-20260603",
        "selected_domain": "packet_template_factories",
        "objective": "Fan in packet template factory candidates.",
        "why_this_next": "The candidate helper seam is ready for review.",
        "recommended_role": "role.steward",
        "required_context_reads": ["a.json", "b.md"],
        "expected_changed_paths": ["ION/04_packages/kernel/ion_domain_weaver_packet_templates.py"],
        "authority_boundary": templates.denied_domain_weaver_authority(),
    }


def test_source_seam_packet_template_matches_packet_factory_boundaries() -> None:
    result = templates.build_domain_weaver_source_seam_packet_template(
        packet_id="PCKT-DOMAIN-WEAVER-PACKET-TEMPLATE-FACTORY-SEAM-AUTONOMOUS-FANOUT-20260603-ATTEMPT-001",
        created_at="2026-06-03T18:29:00Z",
        active_root="/home/sev/ION - Production/ION_Developement",
        operator_lane="domain_weaver_stewarded_autonomy",
        selected_domain="packet_template_factories",
        objective="Extract pure deterministic helpers.",
        why_this_next="The next source-architecture seam is bounded.",
        candidate_worker_paths=[
            "ION/04_packages/kernel/ion_domain_weaver_packet_templates.py",
            "ION/tests/test_kernel_ion_domain_weaver_packet_templates.py",
        ],
        lead_integrator_paths=["ION/04_packages/kernel/ion_domain_weaver.py"],
        nemesis_paths=["ION/05_context/current/domain_weaver/stewarded_autonomy/*PACKET_TEMPLATE*NEMESIS*"],
        allowed_actions=["pure deterministic dict/list/string template construction", ""],
        required_proof_before_settlement=[
            "helper module import-cycle proof requirement recorded",
            "compatibility import/wrapper proof",
        ],
    )

    assert result["schema_id"] == templates.SOURCE_SEAM_PACKET_SCHEMA_ID
    assert result["write_ownership"] == {
        "candidate_worker": [
            "ION/04_packages/kernel/ion_domain_weaver_packet_templates.py",
            "ION/tests/test_kernel_ion_domain_weaver_packet_templates.py",
        ],
        "lead_integrator_after_fanin": ["ION/04_packages/kernel/ion_domain_weaver.py"],
        "nemesis": ["ION/05_context/current/domain_weaver/stewarded_autonomy/*PACKET_TEMPLATE*NEMESIS*"],
    }
    assert result["allowed"] == ["pure deterministic dict/list/string template construction"]
    assert "queue dispatch/start execution" in result["forbidden"]
    assert "accepted-state claim" in result["forbidden"]
    assert result["required_proof_before_settlement"] == [
        "helper module import-cycle proof requirement recorded",
        "compatibility import/wrapper proof",
    ]


def test_identity_metadata_uses_role_tier_without_rank_overclaim() -> None:
    result = templates.domain_weaver_metadata_envelope(
        packet_id="PCKT-DOMAIN-WEAVER-TRUE-NAME-FORMATION-20260603",
        lane_id="domain_formation_lane",
        domain_id="domain.domain_weaver_true_name_system",
        agent_role="role.true_name_steward",
        callsign="Franklin",
        domain_weaver_role_tier="R7_STEWARD",
    )

    identity = result["worker_identity"]
    assert identity["callsign"] == "Franklin"
    assert identity["domain_weaver_role_tier"] == "R7_STEWARD"
    assert identity["role_phase_tier"] == "R7_STEWARD"
    assert identity["ion_settlement_rank"] is None
    assert "rank" not in identity
    assert "self_repair_routing" not in result

    legacy = templates.domain_weaver_metadata_envelope(
        packet_id="PCKT-DOMAIN-WEAVER-LEGACY-RANK-ALIAS-20260603",
        lane_id="domain_formation_lane",
        domain_id="domain.domain_weaver_packet_templates",
        agent_role="role.mason",
        rank="R5_MASON",
    )
    assert legacy["worker_identity"]["domain_weaver_role_tier"] == "R5_MASON"
    assert legacy["worker_identity"]["ion_settlement_rank"] is None
    assert "rank" not in legacy["worker_identity"]


def test_specialist_domain_formation_packet_is_candidate_only_and_proof_bound() -> None:
    result = templates.build_specialist_domain_formation_packet_template(
        packet_id="PCKT-DOMAIN-WEAVER-SPECIALIST-DOMAIN-FORMATION-20260603-ATTEMPT-001",
        created_at="2026-06-03T23:21:00Z",
        domain_id="domain.domain_weaver_context_active_resolver",
        display_name="Domain Weaver Context Active Resolver",
        purpose="Resolve fresh active context packages before worker start.",
        steward_role_id="role.context_active_resolver_steward",
        lane_ids=["context_lane", "", "context_lane", "settlement_lane"],
        required_context_reads=[
            "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
            "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
            "ION/04_packages/kernel/ion_codex_queue_runner.py",
        ],
        owned_paths=[
            "ION/04_packages/kernel/ion_codex_queue_runner.py",
            "ION/04_packages/kernel/ion_domain_weaver_worker_start_readiness.py",
        ],
        candidate_worker_roles=["role.context_cartographer", "role.nemesis", "role.nemesis"],
        callsign="Franklin",
        proof_requirements=["resolver freshness receipt before any materialization-ready claim"],
        blockers=["active_context_packages_stale"],
    )

    assert result["schema_id"] == templates.SPECIALIST_DOMAIN_FORMATION_PACKET_SCHEMA_ID
    assert result["packet_posture"] == "candidate_only_not_registry_materialization"
    assert result["formation_ready"] is False
    assert result["binding_ready"] is False
    assert result["dispatch_ready"] is False
    assert result["materialization_ready"] is False
    assert result["registry_materialization_allowed"] is False
    assert result["topology_or_ui_resume_allowed"] is False
    assert result["authority_boundary"] == templates.denied_domain_weaver_authority()
    assert result["lane_ids"] == ["context_lane", "settlement_lane"]
    assert result["required_context_reads"] == [
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "ION/04_packages/kernel/ion_codex_queue_runner.py",
    ]
    assert result["candidate_worker_roles"] == ["role.context_cartographer", "role.nemesis"]
    assert result["steward_identity"]["callsign"] == "Franklin"
    assert result["steward_identity"]["domain_weaver_role_tier"] == "R7_STEWARD"
    assert result["steward_identity"]["ion_settlement_rank"] is None
    assert "rank" not in result["steward_identity"]
    assert "active_root_proof_before_worker_start" in result["required_proof_before_settlement"]
    assert "resolver freshness receipt before any materialization-ready claim" in result["required_proof_before_settlement"]
    assert "accepted-state claim" in result["forbidden"]
    assert "self_repair_routing" not in result
    assert result["worker_return_posture"] == "carrier_intake_not_product_state"
    assert result["role_tier_policy"]["role_tier_is_not_rank"] is True

    routed = templates.build_specialist_domain_formation_packet_template(
        packet_id="PCKT-DOMAIN-WEAVER-SPECIALIST-DOMAIN-FORMATION-ROUTING-20260603-ATTEMPT-001",
        created_at="2026-06-03T23:22:00Z",
        domain_id="domain.domain_weaver_context_active_resolver",
        display_name="Domain Weaver Context Active Resolver",
        purpose="Resolve fresh active context packages before worker start.",
        steward_role_id="role.context_active_resolver_steward",
        lane_ids=["context_lane"],
        required_context_reads=["ION/05_context/current/codex_solo/HOT_CONTEXT.md"],
        owned_paths=["ION/04_packages/kernel/ion_codex_queue_runner.py"],
        include_self_repair_routing=True,
        self_repair_return_gates={"context_freshness": True},
    )
    assert routed["self_repair_routing"]["included_only_by_explicit_request"] is True
    assert routed["self_repair_routing"]["return_to_domain_owned_repair_ready"] is False


def test_monolith_packet_template_compatibility_wrappers_match_helper_payloads() -> None:
    monolith = importlib.import_module("kernel.ion_domain_weaver")
    objective = "Adopt packet template helpers through compatibility wrappers."

    for symbol_name in (
        "DEFAULT_FORBIDDEN_ACTIONS",
        "DEFAULT_REQUESTED_AUTHORITY",
        "DEFAULT_RETURN_CONTRACT_SECTIONS",
        "DOMAIN_WEAVER_MOVEMENT_CLASS",
        "DOMAIN_WEAVER_TARGET_ROOT_ID",
        "SOURCE_SEAM_PACKET_SCHEMA_ID",
        "WORK_REQUEST_SCHEMA_ID",
    ):
        assert getattr(monolith, symbol_name) == getattr(templates, symbol_name)

    assert monolith.domain_weaver_objective_sha256(objective) == templates.domain_weaver_objective_sha256(
        objective
    )
    assert monolith.denied_domain_weaver_authority() == templates.denied_domain_weaver_authority()
    assert monolith.domain_weaver_root_envelope() == templates.domain_weaver_root_envelope()

    work_request_kwargs = {
        "request_id": "codex_req_domain_weaver_wrapper_adoption_20260603_attempt_001",
        "objective": objective,
        "requested_by": "domain_weaver_packet_template_factory",
        "work_class": "packet_template_factory_wrapper_adoption",
        "lane_id": "source_seam_lane",
        "route_family": "domain_weaver_packet_template_factories",
        "request_kind": "domain_weaver_packet_template_wrapper_candidate",
        "agent_role": "role.mason",
        "supporting_roles": ["role.nemesis", "role.scribe", "role.nemesis", ""],
        "required_context_reads": [
            "ION/04_packages/kernel/ion_domain_weaver.py",
            "ION/04_packages/kernel/ion_domain_weaver.py",
            "ION/04_packages/kernel/ion_domain_weaver_packet_templates.py",
        ],
        "payload_key": "compatibility_payload",
        "payload": {"source": {"items": ("one", "two")}},
    }
    assert monolith.build_domain_weaver_codex_work_request_template(
        **work_request_kwargs
    ) == templates.build_domain_weaver_codex_work_request_template(**work_request_kwargs)

    next_packet_kwargs = {
        "packet_id": "PCKT-DOMAIN-WEAVER-PACKET-TEMPLATE-MONOLITH-ADOPTION-20260603",
        "selected_domain": "packet_template_factories",
        "objective": objective,
        "why_this_next": "The monolith compatibility wrapper seam is ready for review.",
        "required_context_reads": ["a.json", "a.json", "", "b.md"],
        "expected_changed_paths": ["ION/04_packages/kernel/ion_domain_weaver.py"],
        "authority_boundary": {"production_authority": False, "accepted_state_claim": False},
    }
    assert monolith.build_domain_weaver_next_packet_candidate_template(
        **next_packet_kwargs
    ) == templates.build_domain_weaver_next_packet_candidate_template(**next_packet_kwargs)

    source_seam_kwargs = {
        "packet_id": "PCKT-DOMAIN-WEAVER-PACKET-TEMPLATE-MONOLITH-ADOPTION-20260603-ATTEMPT-001",
        "created_at": "2026-06-03T18:41:00Z",
        "active_root": "/home/sev/ION - Production/ION_Developement",
        "operator_lane": "domain_weaver_stewarded_autonomy",
        "selected_domain": "packet_template_factories",
        "objective": objective,
        "why_this_next": "Serialize helper adoption into the Domain Weaver monolith.",
        "candidate_worker_paths": [
            "ION/04_packages/kernel/ion_domain_weaver.py",
            "ION/tests/test_kernel_ion_domain_weaver_packet_templates.py",
        ],
        "allowed_actions": ["import selected helper symbols into ion_domain_weaver.py", ""],
        "required_proof_before_settlement": [
            "representative payload equality",
            "import-cycle/static import proof",
        ],
        "lead_integrator_paths": ["ION/05_context/current/domain_weaver/operator_actions"],
        "nemesis_paths": ["ION/05_context/current/domain_weaver/stewarded_autonomy/*PACKET_TEMPLATE*ADOPTION*NEMESIS*"],
    }
    assert monolith.build_domain_weaver_source_seam_packet_template(
        **source_seam_kwargs
    ) == templates.build_domain_weaver_source_seam_packet_template(**source_seam_kwargs)


def test_packet_templates_module_has_no_monolith_or_stateful_imports() -> None:
    sys.modules.pop("kernel.ion_domain_weaver_packet_templates", None)
    sys.modules.pop("kernel.ion_domain_weaver", None)

    module = importlib.import_module("kernel.ion_domain_weaver_packet_templates")

    assert module.WORK_REQUEST_SCHEMA_ID == templates.WORK_REQUEST_SCHEMA_ID
    assert "kernel.ion_domain_weaver" not in sys.modules

    source_path = Path(module.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    observed_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            observed_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            observed_imports.append(node.module or "")

    assert observed_imports == [
        "__future__",
        "hashlib",
        "typing",
        "ion_domain_weaver_catalog",
        "ion_domain_weaver_true_names",
    ]
    forbidden_imports = (
        "ion_domain_weaver",
        "kernel.ion_domain_weaver",
    )
    forbidden_import_fragments = (
        "materializ",
        "dispatcher",
        "live_binding",
        "projection",
        "queue_runner",
        "topology",
        "cockpit",
        "joc_cockpit",
        "operator_action",
        "registry",
    )
    assert not any(imported in forbidden_imports for imported in observed_imports)
    assert not any(
        fragment in imported
        for imported in observed_imports
        for fragment in forbidden_import_fragments
    )
