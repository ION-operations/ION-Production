from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_v4_7_laws_are_in_builder_and_worker_instructions():
    for rel in [
        "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md",
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md",
    ]:
        text = read(rel)
        assert "V4_7_CONTEXT_PACKAGE_DOGFOOD_LAW" in text
        assert "DOMAIN_CONTEXT_CAPSULE_README_LAW" in text
        assert "ION_TRANSFER_IGNORE_AND_EXPORT_PROFILE_LAW" in text
        assert "ORDERED_CONTEXT_FANOUT_LAW" in text
        assert "PERSONA_VISIBLE_ENVELOPE_LAW" in text


def test_builder_instruction_stays_compact():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert len(text) < 8000
