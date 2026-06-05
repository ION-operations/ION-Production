from pathlib import Path

from kernel.ion_codex_carrier_domain import REQUIRED_SURFACES
from kernel.ion_codex_cli_workbench import (
    SCHEMA_ID,
    build_codex_cli_workbench_model,
)


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")
    for rel in REQUIRED_SURFACES.values():
        _write(root, rel, f"# seeded\n{rel}\n")
    _write(
        root,
        ".codex/config.toml",
        """
sandbox_mode = "danger-full-access"
approval_policy = "never"
model = "gpt-5"

[profiles.default]
model = "gpt-5"

[mcp_servers.ion_local]
command = "python"
args = ["-m", "kernel.ion_mcp_local_bridge"]
""",
    )
    _write(root, "ION/02_architecture/CODEX_CARRIER_OS_RUNTIME_PROTOCOL.md", "# carrier os\n")
    _write(root, "ION/05_context/current/codex_solo/CAPSULE.md", "# Minimum working context\n| C-001 | 2026-05-23 | Seeded workbench | `ION/example.json` | COMPLETE |\n")
    _write(root, "ION/05_context/current/codex_solo/MINI.md", "CODEX SOLO MINI INDEX\nROLE: lookup/receipt index\nLAST_RECEIPT: Seeded workbench\n")
    _write(root, "ION/05_context/current/codex_solo/HOT_CONTEXT.md", "# Codex Solo HOT_CONTEXT\n\n## MINIMUM WORKING CAPSULE\nSeeded\n")
    _write(root, "ION/05_context/current/codex_solo/LONG_HORIZON.json", "{\"epoch_count\":1,\"capsule_entry_count\":1}\n")
    _write(root, "ION/05_context/current/codex_solo/ROUTE.json", "{\"entries\":[]}\n")
    _write(root, "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json", "{\"package_count\":1,\"selected_by_default\":[\"minimum_working_capsule\"]}\n")
    _write(
        root,
        "ION/05_context/current/ACTIVE_CODEX_CAPSULE_CHAT_MODEL.json",
        "{\"schema_id\":\"ion.codex_capsule_chat_model.v1\",\"verdict\":\"READY\",\"ui\":{\"conversation\":{\"summary\":{\"turn_count\":2}}},\"response_runs\":{\"record_count\":1,\"records\":[{\"run_id\":\"run1\",\"status\":\"done\"}]},\"turn_traces\":{\"trace_count\":1},\"lanes\":{\"codex_general\":{\"turns\":[{\"turn_id\":\"t1\"},{\"turn_id\":\"t2\"}]}}}\n",
    )
    _write(root, "ION/05_context/current/codex_cli/hooks/runtime/userpromptsubmit/receipt.json", "{\"ok\":true}\n")


def test_codex_cli_workbench_projects_context_settings_tools_and_visibility(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    (tmp_path / ".codex" / "sessions").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    model = build_codex_cli_workbench_model(tmp_path)

    assert model["schema_id"] == SCHEMA_ID
    assert model["visibility_contract"]["hidden_reasoning_exposed"] is False
    assert model["visibility_contract"]["secrets_authority"] is False
    assert model["settings"]["project_config"]["mcp_server_names"] == ["ion_local"]
    assert model["tools"]["slash_command_count"] >= 1
    assert model["chat"]["turn_count"] == 2
    surface_ids = {surface["surface_id"] for surface in model["context"]["surfaces"]}
    assert {"capsule", "mini", "hot_context", "long_horizon"}.issubset(surface_ids)
    assert model["context"]["timeline"]["schema_id"] == "ion.codex_context_timeline.v1"
    assert model["context"]["timeline"]["summary"]["surface_count"] >= 6
    assert model["hooks"]["runtime_receipts"]["hook_group_count"] == 1
    assert model["accepted_state_authority"] is False
    assert model["production_authority"] is False
    assert model["live_execution_authority"] is False
