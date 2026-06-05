from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from kernel.ion_codex_carrier_sync import (
    build_response_contract,
    build_carrier_sync_status,
    checkpoint_precompact,
    classify_prompt_submit,
    main,
    record_stop_receipt,
    resolve_context_scope,
    suggest_skill_or_domain,
    verify_postcompact,
)


def _minimal_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-shell"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    solo = root / "ION/05_context/current/codex_solo"
    solo.mkdir(parents=True)
    (solo / "MINI.md").write_text(
        "\n".join(
            [
                "MISSION: Maintain the primary Codex Capsule chat profile with bounded full-ION comms.",
                "PHASE: carrier_sync_tests",
                "LAST_RECEIPT: seeded unit receipt",
                "BLOCKER: None",
                "NEXT: Continue carrier sync validation.",
                "ACTIVE_TEMPLATE: CODEX_SOLO_WORK_UNIT",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (solo / "STATUS.json").write_text(
        json.dumps(
            {
                "capsule": {
                    "recent_rows": [
                        {
                            "id": "C-001",
                            "date": "2026-05-15",
                            "summary": "seeded",
                            "status": "TEST",
                        }
                    ]
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def _base_payload(root: Path, event: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "cwd": str(root),
        "hook_event_name": event,
        "session_id": "00000000-0000-4000-8000-000000000001",
        "turn_id": "turn-1",
        "transcript_path": None,
        "model": "gpt-test",
        "permission_mode": "default",
    }
    if event in {"PreCompact", "PostCompact"}:
        payload["trigger"] = "manual"
    if event == "UserPromptSubmit":
        payload["prompt"] = "Proceed with the Codex carrier hook setup."
    if event == "Stop":
        payload["last_assistant_message"] = "Implemented carrier sync adapter."
        payload["stop_hook_active"] = True
    return payload


def test_prompt_submit_classifies_continue_and_writes_candidate_receipt(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)

    output = classify_prompt_submit(_base_payload(root, "UserPromptSubmit"), root=root)

    assert output["continue"] is True
    assert output["suppressOutput"] is True
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "CARRIER_FEATURES_MUST_MAP_TO_ION_OPS" in context
    assert "ION Codex Mount Guard v0.1" in context
    assert "mount_truth_state: CODEX_CARRIER_LOCAL_MOUNT_PARTIAL" in context
    assert "ION Codex Operational Posture v0.1" in context
    assert "ion_operational_state: ION_CODEX_OPERATIONAL_BLOCKED" in context
    assert "ION Codex Response Contract v0.1" in context
    assert "must_not_stop_at_mount_explanation" in context
    assert "proceed_continue_detected: True" in context
    assert "ION Codex Context Scope v0.1" in context
    assert "classification: root_shared_fallback_only" in context
    assert "shared_codex_solo_is_working_capsule: False" in context
    assert "PCKT-ION-CODEX-CARRIER-SYNC-LAYER-V0_1" in context
    receipt_path = context.split("candidate_receipt: ", 1)[1].splitlines()[0]
    receipt = json.loads((root / receipt_path).read_text(encoding="utf-8"))
    assert receipt["schema_id"] == "ion.codex_carrier_sync_hook_receipt.v0_1"
    assert receipt["event_name"] == "UserPromptSubmit"
    assert receipt["candidate_state_only"] is True
    assert receipt["production_authority"] is False
    assert "situation_route" in receipt["ion_operation_targets"]
    assert receipt["operation_payload"]["mount_guard"]["mount_truth_state"] == "CODEX_CARRIER_LOCAL_MOUNT_PARTIAL"
    assert receipt["operation_payload"]["mount_guard_write"]["path"].endswith("CURRENT_CODEX_CARRIER_MOUNT.json")
    assert receipt["operation_payload"]["operational_posture"]["ion_operational_state"] == "ION_CODEX_OPERATIONAL_BLOCKED"
    assert receipt["operation_payload"]["operational_posture_write"]["path"].endswith("CURRENT_ION_CODEX_OPERATIONAL_POSTURE.json")
    assert receipt["operation_payload"]["response_contract"]["status"] == "BLOCK_OR_RECEIPT_ONLY_UNTIL_MOUNT_READY"
    assert receipt["operation_payload"]["context_scope"]["classification"] == "root_shared_fallback_only"
    assert receipt["operation_payload"]["active_objective"]["shared_codex_solo_objective_loaded"] is False


def test_context_scope_detects_folder_local_agent_mount(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)
    mount = root / "ION/05_context/current/codex_agent_mounts/role_mason__domain_construction"
    (mount / ".ion").mkdir(parents=True)
    (mount / "ION_AGENT_MOUNT_MANIFEST.json").write_text("{}", encoding="utf-8")
    (mount / ".ion/ION_CONTEXT_CAPSULE.yaml").write_text("schema_id: test\n", encoding="utf-8")

    scope = resolve_context_scope({"cwd": str(mount)}, root)

    assert scope["classification"] == "codex_agent_mount"
    assert scope["working_capsule_source"] == "folder_local_ion_context_capsule"
    assert scope["shared_codex_solo_boot_context_loaded"] is False
    assert scope["shared_codex_solo_is_working_capsule"] is False
    assert scope["mount_path"] == "ION/05_context/current/codex_agent_mounts/role_mason__domain_construction"


def test_prompt_submit_mount_objective_does_not_read_shared_solo_mini(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)
    mount = root / "ION/05_context/current/codex_agent_mounts/role_mason__domain_construction"
    (mount / ".ion").mkdir(parents=True)
    (mount / "ION_AGENT_MOUNT_MANIFEST.json").write_text(
        json.dumps(
            {
                "agent_role_id": "role.mason",
                "agent_display_name": "MASON",
                "domain_id": "domain.construction_routing_integration",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (mount / ".ion/ION_CONTEXT_CAPSULE.yaml").write_text("schema_id: test\n", encoding="utf-8")
    (mount / ".ion/ACTIVE_CONTEXT_PACKAGE.md").write_text("# local package\n", encoding="utf-8")
    payload = _base_payload(root, "UserPromptSubmit")
    payload["cwd"] = str(mount)

    output = classify_prompt_submit(payload, root=root)

    context = output["hookSpecificOutput"]["additionalContext"]
    assert "classification: codex_agent_mount" in context
    assert "active_shared_codex_solo_objective_loaded: False" in context
    assert "active_agent_role_id: role.mason" in context
    assert "active_domain_id: domain.construction_routing_integration" in context
    assert "active_mission: Maintain the primary Codex Capsule chat profile" not in context
    receipt_path = context.split("candidate_receipt: ", 1)[1].splitlines()[0]
    receipt = json.loads((root / receipt_path).read_text(encoding="utf-8"))
    objective = receipt["operation_payload"]["active_objective"]
    assert objective["classification"] == "codex_agent_mount"
    assert objective["shared_codex_solo_objective_loaded"] is False
    assert "mission" not in objective
    assert objective["agent_role_id"] == "role.mason"
    assert objective["domain_id"] == "domain.construction_routing_integration"


def test_context_scope_detects_folder_local_context_capsule(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)
    context_root = root / "ION/05_context/current/domain_weaver"
    nested = context_root / "validation"
    (context_root / ".ion").mkdir(parents=True)
    nested.mkdir(parents=True)
    (context_root / ".ion/ION_CONTEXT_CAPSULE.yaml").write_text("schema_id: test\n", encoding="utf-8")
    (context_root / ".ion/ACTIVE_CONTEXT_PACKAGE.md").write_text("# local package\n", encoding="utf-8")

    scope = resolve_context_scope({"cwd": str(nested)}, root)

    assert scope["classification"] == "folder_local_context_capsule"
    assert scope["working_capsule_source"] == "folder_local_ion_context_capsule"
    assert scope["shared_codex_solo_boot_context_loaded"] is False
    assert scope["shared_codex_solo_is_working_capsule"] is False
    assert scope["context_root_path"] == "ION/05_context/current/domain_weaver"


def test_prompt_submit_folder_local_objective_does_not_read_shared_solo_mini(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)
    context_root = root / "ION/05_context/current/domain_weaver"
    (context_root / ".ion").mkdir(parents=True)
    (context_root / ".ion/ION_CONTEXT_CAPSULE.yaml").write_text("schema_id: test\n", encoding="utf-8")
    (context_root / ".ion/ACTIVE_CONTEXT_PACKAGE.md").write_text("# local package\n", encoding="utf-8")
    (context_root / ".ion/CONTEXT_IDENTITY.json").write_text(
        json.dumps(
            {
                "context_id": "domain_weaver_current_context",
                "domain_id": "domain.current_phase_orchestration_management",
                "focus": "domain_weaver_context_identity",
                "active_template": "DOMAIN_WEAVER_FOLDER_LOCAL_CONTEXT",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    payload = _base_payload(root, "UserPromptSubmit")
    payload["cwd"] = str(context_root)

    output = classify_prompt_submit(payload, root=root)

    context = output["hookSpecificOutput"]["additionalContext"]
    assert "classification: folder_local_context_capsule" in context
    assert "active_shared_codex_solo_objective_loaded: False" in context
    assert "active_context_id: domain_weaver_current_context" in context
    assert "active_domain_id: domain.current_phase_orchestration_management" in context
    assert "active_focus: domain_weaver_context_identity" in context
    assert "active_mission: Maintain the primary Codex Capsule chat profile" not in context
    receipt_path = context.split("candidate_receipt: ", 1)[1].splitlines()[0]
    receipt = json.loads((root / receipt_path).read_text(encoding="utf-8"))
    objective = receipt["operation_payload"]["active_objective"]
    assert objective["classification"] == "folder_local_context_capsule"
    assert objective["shared_codex_solo_objective_loaded"] is False
    assert "mission" not in objective
    assert objective["context_id"] == "domain_weaver_current_context"


def test_compact_hooks_create_and_verify_baton(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)

    pre_output = checkpoint_precompact(_base_payload(root, "PreCompact"), root=root)
    post_output = verify_postcompact(_base_payload(root, "PostCompact"), root=root)

    assert pre_output == {"continue": True, "suppressOutput": True}
    assert post_output == {"continue": True, "suppressOutput": True}
    pre_receipts = list((root / "ION/05_context/current/codex_cli/hooks/runtime/precompact").glob("*.json"))
    post_receipts = list((root / "ION/05_context/current/codex_cli/hooks/runtime/postcompact").glob("*.json"))
    assert len(pre_receipts) == 1
    assert len(post_receipts) == 1
    post_receipt = json.loads(post_receipts[0].read_text(encoding="utf-8"))
    assert post_receipt["operation_payload"]["precompact_checkpoint_found"] is True
    assert post_receipt["operation_payload"]["precompact_checkpoint_ref"]["receipt_path"].endswith(".json")
    assert post_receipt["operation_payload"]["mount_guard"]["mount_truth_state"] == "CODEX_CARRIER_LOCAL_MOUNT_PARTIAL"
    assert post_receipt["operation_payload"]["mount_guard_write"]["path"].endswith("CURRENT_CODEX_CARRIER_MOUNT.json")
    assert post_receipt["operation_payload"]["operational_posture"]["ion_operational_state"] == "ION_CODEX_OPERATIONAL_BLOCKED"


def test_postcompact_warns_when_baton_missing_but_does_not_block(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)

    output = verify_postcompact(_base_payload(root, "PostCompact"), root=root)

    assert output["continue"] is True
    assert output["suppressOutput"] is True
    assert "systemMessage" in output
    receipt = next((root / "ION/05_context/current/codex_cli/hooks/runtime/postcompact").glob("*.json"))
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["operation_payload"]["precompact_checkpoint_found"] is False


def test_stop_hook_writes_turn_handoff_receipt(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)

    output = record_stop_receipt(_base_payload(root, "Stop"), root=root)

    assert output == {"continue": True, "suppressOutput": True}
    receipt = next((root / "ION/05_context/current/codex_cli/hooks/runtime/stop").glob("*.json"))
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["event_name"] == "Stop"
    assert payload["operation_payload"]["receipt_kind"] == "turn_stop_handoff"
    assert payload["operation_payload"]["mount_guard"]["mount_truth_state"] == "CODEX_CARRIER_LOCAL_MOUNT_PARTIAL"
    assert payload["operation_payload"]["operational_posture"]["ion_operational_state"] == "ION_CODEX_OPERATIONAL_BLOCKED"
    assert payload["operation_payload"]["next_baton"]["candidate_state_only"] is True
    assert payload["live_execution_authority"] is False


def test_prompt_domain_suggestions_map_carrier_features_to_ion_ops() -> None:
    hook_route = suggest_skill_or_domain("Fix the PreCompact hook and MCP carrier setup")
    joc_route = suggest_skill_or_domain("Continue the Helixion JOC WisdomNET packet")
    action_route = suggest_skill_or_domain("Validate the GPT Builder Action schema gateway")
    drift_route = suggest_skill_or_domain("Why aren't you operating as ION if I have to constantly tell you to mount it?")

    assert hook_route["suggested_domain"] == "codex_carrier_sync"
    assert hook_route["confidence"] == "high"
    assert joc_route["suggested_domain"] == "helixion_joc_rebuild"
    assert joc_route["proceed_continue_detected"] is True
    assert action_route["suggested_domain"] == "ion_gpt_action_gateway"
    assert drift_route["intent_class"] == "carrier_operation_failure_repair"
    assert drift_route["candidate_packet"] == "PCKT-ION-CODEX-OPERATE-NOT-EXPLAIN-GUARD-V0_1"


def test_response_contract_requires_operating_without_operator_remount_when_ready() -> None:
    route = suggest_skill_or_domain("Why aren't you operating as ION?")

    contract = build_response_contract(
        route,
        {"mount_truth_state": "CODEX_CARRIER_LOCAL_MOUNT_READY"},
        {"ion_operational_state": "ION_CODEX_OPERATIONAL_READY"},
    )

    assert contract["status"] == "OPERATE_AS_ION_NOW"
    assert contract["operator_remount_required"] is False
    assert contract["must_not_ask_operator_to_remount_when_ready"] is True
    assert contract["must_not_stop_at_mount_explanation"] is True
    assert contract["must_take_bounded_next_step"] is True
    assert contract["persona_fronted_response_required"] is True
    assert contract["visible_role_surface_required"] is False
    assert contract["internal_role_trace_visible_by_default"] is False
    assert contract["audit_trace_available_on_request"] is True
    assert contract["visible_role_markers"] == ["PERSONA_INTERFACE_RESPONSE", "RELAY", "STEWARD", "MASON", "SCRIBE"]
    assert "return only the Persona Interface response" in contract["visible_role_rule"]
    assert "carrier drift" in contract["failure_condition"]
    assert "leaking internal role machinery" in contract["failure_condition"]


def test_carrier_sync_status_is_observation_only(tmp_path: Path) -> None:
    root = _minimal_root(tmp_path)

    status = build_carrier_sync_status(root)

    assert status["schema_id"] == "ion.codex_carrier_sync.v0_1"
    assert status["verdict"] == "ION_CODEX_CARRIER_SYNC_READY"
    assert status["policy"]["capsule_hot_context_auto_mutation"] is False
    assert status["policy"]["broad_pretooluse_governance"] is False
    assert status["production_authority"] is False
    assert status["mount_guard"]["mount_truth_state"] == "CODEX_CARRIER_LOCAL_MOUNT_PARTIAL"
    assert status["operational_posture"]["ion_operational_state"] == "ION_CODEX_OPERATIONAL_BLOCKED"


def test_cli_hook_reads_stdin_and_outputs_valid_json(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _minimal_root(tmp_path)
    payload = _base_payload(root, "UserPromptSubmit")
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))

    assert main(["--ion-root", str(root), "hook", "--event", "UserPromptSubmit", "--json"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["continue"] is True
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
