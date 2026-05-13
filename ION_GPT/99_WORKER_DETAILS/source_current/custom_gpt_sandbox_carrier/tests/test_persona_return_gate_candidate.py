from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[5]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

def test_instruction_contains_persona_return_gate_law():
    for rel in [
        "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md",
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md",
    ]:
        text = read(rel)
        assert "PERSONA_RETURN_GATE_LAW" in text
        assert "FRONT_DOOR_BOUNDARY_ARTIFACT_LAW" in text
        assert "Persona Interface is front-door ingress and final user-facing renderer" in text

def test_context_package_does_not_make_persona_manager():
    data = yaml.safe_load(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/context/ION_CUSTOM_GPT_SANDBOX_CARRIER_CONTEXT_PACKAGE.yaml"))
    assert data["front_door_agent"] == "PERSONA_INTERFACE"
    assert data["manager_agent"] == "STEWARD"
    assert data["orchestration_agent"] == "STEWARD"
    assert data["presentation_agent"] == "PERSONA_INTERFACE"
    assert data["persona_return_gate"]["required"] is True

def test_boot_route_has_return_path_and_gate():
    data = yaml.safe_load(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/routes/BOOT_TO_PERSONA_ROUTE.yaml"))
    phases = [phase["phase"] for phase in data["internal_cycle"]]
    assert phases.index("RELAY_RETURN_PACKAGE") < phases.index("PERSONA_RETURN_GATE") < phases.index("PERSONA_INTERFACE_RESPONSE")
    assert data["persona_return_gate"]["required_for_substantive_final_answer"] is True
    assert data["front_door_boundary_model"]["logical_return"] == [
        "RELAY_RETURN_PACKAGE",
        "PERSONA_RETURN_GATE",
        "PERSONA_INTERFACE_RESPONSE",
    ]

def test_templates_bind_ion_to_persona_gate():
    persona = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_PERSONA_INTERFACE_RESPONSE.template.md")
    boot = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md")
    assert "`ION ::` content must be based on a Relay return package" in persona
    assert "Persona Return Gate rule" in boot
