from __future__ import annotations

import importlib.util
import io
import json
import sys
import tomllib
from pathlib import Path

from kernel.ion_mcp_local_bridge import IonMcpLocalBridge


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _hook_command(config: dict, event: str) -> str:
    return config["hooks"][event][0]["hooks"][0]["command"]


def test_project_codex_config_is_project_scoped_and_hook_enabled():
    root = _repo_root()
    config_path = root / ".codex" / "config.toml"

    config = tomllib.loads(config_path.read_text(encoding="utf-8"))

    assert (root / "AGENTS.md").is_file()
    assert config["sandbox_mode"] == "workspace-write"
    assert config["approval_policy"] == "on-request"
    assert config["features"]["hooks"] is True
    assert config["sandbox_workspace_write"]["network_access"] is False
    assert "ION/05_context/current/codex_agent_mounts" in config["sandbox_workspace_write"]["writable_roots"]
    assert config["mcp_servers"]["ion_local"]["enabled"] is True
    assert config["mcp_servers"]["ion_local"]["required"] is False
    assert "--stdio" in config["mcp_servers"]["ion_local"]["args"]
    assert "codex_solo as a unique working capsule" in config["developer_instructions"]
    assert "ION/05_context/current/codex_agent_mounts/<mount_id>" in config["developer_instructions"]
    assert set(config["hooks"]) >= {"SessionStart", "UserPromptSubmit", "PreCompact", "PostCompact", "Stop"}
    assert "ion_session_start_context.py" in _hook_command(config, "SessionStart")
    assert "ion_user_prompt_submit.py" in _hook_command(config, "UserPromptSubmit")
    assert "ion_precompact.py" in _hook_command(config, "PreCompact")
    assert "ion_postcompact.py" in _hook_command(config, "PostCompact")
    assert "ion_stop.py" in _hook_command(config, "Stop")
    bridge_tools = {tool["name"] for tool in IonMcpLocalBridge(root).tool_descriptors()}
    assert set(config["mcp_servers"]["ion_local"]["enabled_tools"]).issubset(bridge_tools)


def test_codex_native_agent_config_is_enabled_without_unsupported_spawn_depth():
    root = _repo_root()
    parent = root.parent

    for config_path in (root / ".codex" / "config.toml", parent / ".codex" / "config.toml"):
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))

        assert config["features"]["multi_agent"] is True
        assert config["agents"]["max_threads"] == 10
        assert config["agents"]["max_depth"] == 2
        assert "max_spawn_depth" not in config["agents"]


def test_session_start_hook_outputs_additional_context(monkeypatch, capsys):
    root = _repo_root()
    hook_path = root / ".codex" / "hooks" / "ion_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_session_start_context", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ion_session_start_context"] = module
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(root), "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert payload["continue"] is True
    assert "ION Codex Mount Guard v0.1" in context
    assert "mount_truth_state: CODEX_CARRIER_LOCAL_MOUNT_READY" in context
    assert "ION Codex Operational Posture v0.1" in context
    assert "ion_operational_state: ION_CODEX_OPERATIONAL_READY" in context
    assert "ION Codex Root Context Boundary v0.1" in context
    assert "CODEX_ROOT_SHARED_CONTEXT_FALLBACK_ONLY" in context
    assert "shared_codex_solo_boot_context_loaded: false" in context
    assert "ION Codex Solo Boot Context" not in context
    assert str(root) in context


def test_session_start_hook_outputs_folder_local_agent_mount_context(monkeypatch, capsys):
    root = _repo_root()
    mount = root / "ION/05_context/current/codex_agent_mounts/role_codex_carrier_steward__domain_codex_carrier_sync"
    hook_path = root / ".codex" / "hooks" / "ion_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_session_start_context_mount", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(mount), "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "ION Codex Agent Mount Boot Context v0.1" in context
    assert "CODEX_AGENT_DOMAIN_MOUNT_READY" in context
    assert "PORTABLE_ION_CONTEXT_CAPSULE" in context
    assert "shared_codex_solo_boot_context_loaded: false" in context
    assert "ION Codex Solo Boot Context" not in context


def test_session_start_hook_outputs_generic_folder_local_context(monkeypatch, capsys):
    root = _repo_root()
    context_root = root / "ION/05_context/current/domain_weaver"
    hook_path = root / ".codex" / "hooks" / "ion_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_session_start_context_folder", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(context_root), "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "ION Folder Local Context Boot Context v0.1" in context
    assert "CODEX_FOLDER_LOCAL_CONTEXT_READY" in context
    assert "FOLDER_ION_CONTEXT_CAPSULE" in context
    assert "FOLDER_ACTIVE_CONTEXT_PACKAGE" in context
    assert "shared_codex_solo_boot_context_loaded: false" in context
    assert "ION Codex Solo Boot Context" not in context


def test_session_start_hook_fails_soft_outside_active_root(monkeypatch, capsys):
    root = _repo_root()
    hook_path = root / ".codex" / "hooks" / "ion_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_session_start_context_outside", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": "/tmp", "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["continue"] is True
    assert "outside active ION root" in payload["systemMessage"]


def test_parent_codex_config_bridges_to_active_root():
    root = _repo_root()
    parent = root.parent
    config_path = parent / ".codex" / "config.toml"

    config = tomllib.loads(config_path.read_text(encoding="utf-8"))

    assert not (parent / "AGENTS.md").exists()
    assert config["features"]["hooks"] is True
    assert str(root) in config["developer_instructions"]
    assert "codex_solo as a unique working capsule" in config["developer_instructions"]
    assert "ION/05_context/current/codex_agent_mounts/<mount_id>" in config["developer_instructions"]
    assert config["mcp_servers"]["ion_local"]["enabled"] is True
    assert config["mcp_servers"]["ion_local"]["cwd"] == str(root)
    assert set(config["hooks"]) >= {"SessionStart", "UserPromptSubmit", "PreCompact", "PostCompact", "Stop"}
    assert "ion_parent_session_start_context.py" in _hook_command(config, "SessionStart")
    assert "ion_user_prompt_submit.py" in _hook_command(config, "UserPromptSubmit")
    assert "ion_precompact.py" in _hook_command(config, "PreCompact")
    assert "ion_postcompact.py" in _hook_command(config, "PostCompact")
    assert "ion_stop.py" in _hook_command(config, "Stop")


def test_parent_session_start_hook_loads_active_root_context(monkeypatch, capsys):
    root = _repo_root()
    parent = root.parent
    hook_path = parent / ".codex" / "hooks" / "ion_parent_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_parent_session_start_context", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ion_parent_session_start_context"] = module
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(parent), "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert payload["continue"] is True
    assert "ION Codex Mount Guard v0.1" in context
    assert "mount_truth_state: CODEX_CARRIER_LOCAL_MOUNT_READY" in context
    assert "ION Codex Operational Posture v0.1" in context
    assert "ion_operational_state: ION_CODEX_OPERATIONAL_READY" in context
    assert "ION Parent Workspace Context Boundary" in context
    assert "CODEX_PARENT_SHARED_CONTEXT_FALLBACK_ONLY" in context
    assert "shared_codex_solo_boot_context_loaded: false" in context
    assert "ION Codex Solo Boot Context" not in context
    assert str(root) in context


def test_parent_session_start_hook_outputs_generic_folder_local_context(monkeypatch, capsys):
    root = _repo_root()
    parent = root.parent
    context_root = root / "ION/05_context/current/domain_weaver"
    hook_path = parent / ".codex" / "hooks" / "ion_parent_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_parent_session_start_context_folder", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(context_root), "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "ION Folder Local Context Boot Context v0.1" in context
    assert "CODEX_FOLDER_LOCAL_CONTEXT_READY" in context
    assert "FOLDER_ION_CONTEXT_CAPSULE" in context
    assert "shared_codex_solo_boot_context_loaded: false" in context
    assert "ION Codex Solo Boot Context" not in context


def test_parent_session_start_hook_fails_soft_outside_parent(monkeypatch, capsys):
    root = _repo_root()
    parent = root.parent
    hook_path = parent / ".codex" / "hooks" / "ion_parent_session_start_context.py"
    spec = importlib.util.spec_from_file_location("ion_parent_session_start_context_outside", hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": "/tmp", "hook_event_name": "SessionStart"})))

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["continue"] is True
    assert "outside ION production parent" in payload["systemMessage"]
