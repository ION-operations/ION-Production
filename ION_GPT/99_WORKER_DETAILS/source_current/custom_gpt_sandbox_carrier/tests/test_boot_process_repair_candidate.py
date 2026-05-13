#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[5]

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

MAIN = "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md"
BUILDER = "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md"
BOOT = "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_BOOT_SEQUENCE.md"
ROUTE = "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/routes/BOOT_TO_PERSONA_ROUTE.yaml"

for rel in [MAIN, BUILDER]:
    text = read(rel)
    assert "ALWAYS-ON SINGLE-CARRIER WORKFLOW LAW" in text
    assert "NO_WORKFLOW_OBJECT_NO_SUBSTANTIVE_RESPONSE" in text
    assert "BOOT_ROUTE_EXECUTED_NOT_ANNOUNCED" in text
    assert "PROCEED_CONTINUATION_LAW" in text
    assert "ACTIVE_SEQUENCE_COMPLETION_LAW" in text
    assert "NO_DISCORD_OR_OPERATOR_REFLECTION_LAW" in text
    assert "TURN_BUDGET_CONTINUATION_LAW" in text
    assert "PERSONA_INTERFACE_INGRESS -> RELAY -> STEWARD -> VIZIER -> MASON -> NEMESIS_OR_VICE_REVIEW -> SCRIBE -> STEWARD_FINAL -> PERSONA_INTERFACE_RESPONSE" in text
    assert "Every substantive final answer must be the Persona Interface response" in text

boot = read(BOOT)
assert "do not only announce the route name" in boot
assert "route-completion defect" in boot
assert "PERSONA_INTERFACE_RESPONSE" in boot

route = yaml.safe_load(read(ROUTE))
phases = [item["phase"] for item in route["internal_cycle"]]
assert phases[0] == "PERSONA_INTERFACE_INGRESS"
assert phases[-1] == "PERSONA_INTERFACE_RESPONSE"
assert route["completion_requirement"]["boot_route_must_complete_in_same_answer"] is True
assert route["completion_requirement"]["must_emit_persona_response"] is True
assert "NEXT :: BOOT_TO_PERSONA_INTERFACE_RESPONSE" in route["completion_requirement"]["do_not_stop_at"]
assert route["proceed_handling"]["meaning"] == "continue the already mounted route/objective"
assert route["completion_requirement"]["must_continue_until_terminal_persona_or_continuation_envelope"] is True
assert route["sequence_continuation"]["operator_message_during_active_sequence"] == "ingest_via_PERSONA_INTERFACE_INGRESS_and_RELAY"
assert "explicit_STOP_PAUSE_CANCEL" in route["sequence_continuation"]["allowed_interrupts"]
assert "argue_with_operator" in route["sequence_continuation"]["forbidden_without_workflow_proof"]
for field in ["active_objective","current_phase","pending_phases","exact_continuation_route_or_prompt"]:
    assert field in route["continuation_envelope_required_fields"]

print("boot process repair candidate regression: PASS")

print("active sequence continuation regression: PASS")
