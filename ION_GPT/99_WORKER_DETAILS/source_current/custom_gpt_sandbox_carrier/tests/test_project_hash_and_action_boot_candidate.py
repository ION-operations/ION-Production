from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"


def read_root(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def read(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8")


def test_instructions_define_project_hash_without_gateway_enforcement():
    for rel in [
        "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md",
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md",
    ]:
        text = read_root(rel)
        assert "PROJECT_CONTINUITY_HASH_LAW" in text
        assert "reuse its `ion_project_hash`" in text
        assert "Do not enforce project hash through Actions/MCP until gateway support is explicitly proven" in text


def test_route_defines_action_boot_as_read_only_and_auth_stop():
    route = yaml.safe_load(read("routes/BOOT_TO_PERSONA_ROUTE.yaml"))
    assert route["project_continuity_hash"]["carried_by"] == "ion_project_hash"
    assert route["project_continuity_hash"]["new_chat_without_package"] == "report_pending_and_create_or_request_candidate_continuity_package"
    assert route["project_continuity_hash"]["action_gateway_enforcement"] == "later_packet_only"
    assert route["action_boot_check"]["normal_boot_requires_live_actions"] is False
    assert "ionGatewayHealth" in route["action_boot_check"]["when_requested_use_read_only_probes"]
    assert "ionMcpHealth" in route["action_boot_check"]["when_requested_use_read_only_probes"]
    assert "AUTH_INVALID" in route["action_boot_check"]["stop_immediately_on"]
    assert "gateway_token_invalid" in route["action_boot_check"]["stop_immediately_on"]


def test_context_package_carries_project_hash_and_action_boot_policy():
    ctx = yaml.safe_load(read("context/ION_CUSTOM_GPT_SANDBOX_CARRIER_CONTEXT_PACKAGE.yaml"))
    assert ctx["project_continuity_hash"]["carried_by"] == "ion_project_hash"
    assert ctx["project_continuity_hash"]["action_gateway_enforcement"] == "later_packet_only"
    assert ctx["action_boot_check"]["normal_boot_requires_live_actions"] is False
    assert ctx["action_boot_check"]["stop_on_auth_invalid"] is True
