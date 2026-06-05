from pathlib import Path

from kernel.ion_skill_activation import (
    SKILL_PROTOCOL_PATH,
    SKILL_REGISTRY_PATH,
    build_ion_skill_activation,
    build_ion_skill_surface,
    load_ion_skill_registry,
)


def _seed_skill_root(root: Path) -> None:
    (root / SKILL_PROTOCOL_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / SKILL_PROTOCOL_PATH).write_text("# Skill activation protocol\n", encoding="utf-8")
    path = root / SKILL_REGISTRY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
schema_id: ion.skill_registry.v1
production_authority: false
live_execution_authority: false
secrets_authority: false
principle: Skills activate workflows; templates govern proof.
global_proof_contract:
  context_proof_required: true
skills:
  - skill_id: codex-chat-answer
    display_name: Codex Chat Answer
    class: user_visible
    purpose: Answer normal chat.
    trigger_summary: respond only
    preferred_model: gpt-5.5
    default_reasoning_effort: medium
    activates_templates: [ION/07_templates/context/ION_CONTEXT_LOAD_PROOF.md]
    template_bindings: []
    context_mount: {required_packages: [minimum_working_capsule], route_deeper_packages: [route_depth_package]}
    allowed_authority: {read_context: true, queue_work: false, write_files: false, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: false, receipt_required: false}
    ui: {label: Chat, drawer_visible: true, user_chore: false}
  - skill_id: codex-solo-work
    display_name: Codex Work
    class: user_visible
    purpose: Queue bounded Codex work.
    trigger_summary: run task
    preferred_model: gpt-5.3-codex
    default_reasoning_effort: medium
    activates_templates: [ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md]
    template_bindings: [ION/07_templates/bindings/MASON__CODE.md]
    context_mount: {required_packages: [minimum_working_capsule], route_deeper_packages: [evidence_receipt_package]}
    allowed_authority: {read_context: true, queue_work: true, write_files: bounded_scoped_only, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: Work, drawer_visible: true, user_chore: false}
  - skill_id: codex-recovery
    display_name: Recovery
    class: user_visible
    purpose: Recover drift.
    trigger_summary: recovery
    preferred_model: gpt-5.5
    default_reasoning_effort: high
    activates_templates: [ION/07_templates/reports/AUDIT.md]
    template_bindings: []
    context_mount: {required_packages: [recovery_package], route_deeper_packages: [evidence_receipt_package]}
    allowed_authority: {read_context: true, queue_work: false, write_files: false, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: Recover, drawer_visible: true, user_chore: false}
  - skill_id: ion-full-workflow-handoff
    display_name: ION Handoff
    class: bridge
    purpose: Route through full ION.
    trigger_summary: ion lane
    preferred_model: gpt-5.3-codex-spark
    default_reasoning_effort: low
    activates_templates: [ION/07_templates/bindings/RELAY__HANDOFF.md]
    template_bindings: []
    context_mount: {required_packages: [mission_active_package], route_deeper_packages: [route_depth_package]}
    allowed_authority: {read_context: true, queue_work: bounded_existing_queue_only, write_files: false, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: ION Handoff, drawer_visible: true, user_chore: false}
  - skill_id: template-curation
    display_name: Template Curation
    class: specialist
    purpose: Govern templates and skills.
    trigger_summary: governance
    preferred_model: gpt-5.5
    default_reasoning_effort: high
    activates_templates: [ION/07_templates/actions/TEMPLATE_DEVELOPMENT.md]
    template_bindings: []
    context_mount: {required_packages: [active_authority_package], route_deeper_packages: [route_depth_package]}
    allowed_authority: {read_context: true, queue_work: false, write_files: scoped_governance_surfaces_only, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: Templates, drawer_visible: true, user_chore: false}
  - skill_id: ion-orchestration
    display_name: ION Orchestration
    class: codex_native
    purpose: Route ION handoffs.
    trigger_summary: next packet
    preferred_model: gpt-5.5
    default_reasoning_effort: high
    ion_ops: [context_load, situation_route, receipt_preservation, next_packet_compile]
    activates_templates: [ION/07_templates/actions/TASK.md]
    template_bindings: []
    context_mount: {required_packages: [minimum_working_capsule], route_deeper_packages: [route_depth_package]}
    allowed_authority: {read_context: true, queue_work: bounded_existing_queue_only, write_files: scoped_protocol_packet_receipt_surfaces_only, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: ION Route, drawer_visible: true, user_chore: false}
  - skill_id: ion-context-scout
    display_name: ION Context Scout
    class: codex_native
    purpose: Scout branch context.
    trigger_summary: branch context
    preferred_model: gpt-5.5
    default_reasoning_effort: medium
    ion_ops: [context_load, situation_route, domain_capsule_update, drift_repair]
    activates_templates: [ION/07_templates/context/ION_CONTEXT_LOAD_PROOF.md]
    template_bindings: []
    context_mount: {required_packages: [route_depth_package], route_deeper_packages: [evidence_receipt_package]}
    allowed_authority: {read_context: true, queue_work: false, write_files: candidate_branch_context_only_when_requested, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: Context Scout, drawer_visible: true, user_chore: false}
  - skill_id: ion-memory-curator
    display_name: ION Memory Curator
    class: codex_native
    purpose: Curate Codex memory.
    trigger_summary: memory
    preferred_model: gpt-5.5
    default_reasoning_effort: medium
    ion_ops: [context_load, receipt_preservation, drift_repair, next_packet_compile]
    activates_templates: [ION/07_templates/codex_memory/ION_CODEX_AD_HOC_MEMORY_NOTE.template.md]
    template_bindings: []
    context_mount: {required_packages: [evidence_receipt_package], route_deeper_packages: [recovery_package]}
    allowed_authority: {read_context: true, queue_work: false, write_files: ad_hoc_memory_contribution_lane_only_when_requested, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true, memory_is_recall_not_authority: true}
    ui: {label: Memory, drawer_visible: true, user_chore: false}
  - skill_id: ion-workbench
    display_name: ION Workbench
    class: codex_native
    purpose: Use Project Workbench.
    trigger_summary: workbench
    preferred_model: gpt-5.3-codex
    default_reasoning_effort: medium
    ion_ops: [context_load, bounded_execution, receipt_preservation, drift_repair]
    activates_templates: [ION/07_templates/actions/PATCH_PACKAGE.md]
    template_bindings: []
    context_mount: {required_packages: [mission_active_package], route_deeper_packages: [evidence_receipt_package]}
    allowed_authority: {read_context: true, queue_work: bounded_existing_queue_only, write_files: bounded_patch_or_requested_repo_surfaces_only, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: Workbench, drawer_visible: true, user_chore: false}
  - skill_id: ion-hook-engineer
    display_name: ION Hook Engineer
    class: codex_native
    purpose: Engineer Codex hooks.
    trigger_summary: hooks
    preferred_model: gpt-5.5
    default_reasoning_effort: high
    ion_ops: [context_load, situation_route, receipt_preservation, drift_repair, next_packet_compile]
    activates_templates: [ION/07_templates/actions/FULL_CARRIER_ACTION_RECEIPT.md]
    template_bindings: []
    context_mount: {required_packages: [mission_active_package], route_deeper_packages: [evidence_receipt_package]}
    allowed_authority: {read_context: true, queue_work: false, write_files: scoped_codex_hook_and_config_surfaces_only, production_authority: false, live_execution_authority: false, secrets_authority: false}
    proof_contract: {context_proof_required: true, template_action_proof_required: true, receipt_required: true}
    ui: {label: Hooks, drawer_visible: true, user_chore: false}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_skill_registry_loads_without_authority_grant(tmp_path: Path):
    _seed_skill_root(tmp_path)

    registry = load_ion_skill_registry(tmp_path)

    assert registry["ok"] is True
    assert registry["skill_count"] == 10
    assert registry["production_authority"] is False
    assert registry["live_execution_authority"] is False


def test_skill_activation_selects_queue_and_keeps_templates_as_gate(tmp_path: Path):
    _seed_skill_root(tmp_path)

    activation = build_ion_skill_activation(
        tmp_path,
        lane_id="codex_general",
        objective="Implement the fix.",
        execution_mode="queue_for_codex",
    )

    assert activation["ok"] is True
    assert activation["skill_id"] == "codex-solo-work"
    assert activation["selection_reason"] == "codex_queue_execution_mode"
    assert activation["state_acceptance_granted"] is False
    assert activation["proof_contract"]["template_action_proof_required"] is True
    assert activation["authority"]["production_authority"] is False


def test_skill_activation_selects_recovery_before_template_language(tmp_path: Path):
    _seed_skill_root(tmp_path)

    activation = build_ion_skill_activation(
        tmp_path,
        lane_id="codex_general",
        objective="Recover from UI drift in the skill drawer.",
        execution_mode="respond_only",
    )

    assert activation["skill_id"] == "codex-recovery"
    assert activation["selection_reason"] == "recovery_trigger_detected"


def test_skill_surface_exposes_current_activation(tmp_path: Path):
    _seed_skill_root(tmp_path)

    surface = build_ion_skill_surface(tmp_path, objective="Explain templates and skills.")

    assert surface["ok"] is True
    assert surface["current_activation"]["skill_id"] == "template-curation"
    assert surface["policy"] == "skills_activate_templates_templates_gate_proof"


def test_codex_skills_v0_route_memory_context_workbench_hooks_and_orchestration(tmp_path: Path):
    _seed_skill_root(tmp_path)

    cases = [
        ("please update Codex memory through an ad-hoc note", "ion-memory-curator", "codex_memory_curator_language_detected"),
        ("scout this branch context before editing", "ion-context-scout", "branch_context_scout_language_detected"),
        ("use project workbench file slice and patch preview", "ion-workbench", "project_workbench_language_detected"),
        ("audit the PreCompact hook and carrier sync receipt", "ion-hook-engineer", "codex_hook_engineering_language_detected"),
        ("ION GPT says next packet should route through receipts", "ion-orchestration", "ion_orchestration_language_detected"),
    ]

    for objective, skill_id, reason in cases:
        activation = build_ion_skill_activation(
            tmp_path,
            lane_id="codex_general",
            objective=objective,
            execution_mode="respond_only",
        )
        assert activation["skill_id"] == skill_id
        assert activation["selection_reason"] == reason
        assert activation["authority"]["production_authority"] is False
        assert activation["authority"]["live_execution_authority"] is False
        assert activation["authority"]["secrets_authority"] is False
        assert activation["proof_contract"]["context_proof_required"] is True
