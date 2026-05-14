from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def test_next_chat_prompt_requires_mount_before_substantive_answer():
    prompt = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_NEXT_CHAT_PROMPT.template.txt")
    assert "BOOT-SEQUENCE" in prompt
    assert "Mount the attached ION continuity transfer package first" in prompt
    assert "candidate dynamic domains/agents" in prompt
    assert "persona_gate_blocked" in prompt

def test_sequence_continuation_schema_carries_domain_agent_and_persona():
    import json
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_SEQUENCE_CONTINUATION_V4_3.schema.json"))
    required = schema["properties"]["ion_sequence_continuation"]["required"]
    for field in ["candidate_domains", "candidate_agents", "persona_profile", "authority", "exact_next_sequence"]:
        assert field in required
