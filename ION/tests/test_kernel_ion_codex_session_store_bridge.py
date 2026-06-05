import json
from pathlib import Path

from kernel import ion_codex_session_store_bridge as bridge
from kernel.ion_codex_session_store_bridge import (
    CONFIRMATION_TOKEN,
    invoke_codex_session_store_route,
)


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# authority\n", encoding="utf-8")


def _seed_codex_session(codex_home: Path, cwd: Path) -> str:
    session_id = "019eabcd-1111-2222-3333-444444444444"
    session_dir = codex_home / "sessions/2026/06/03"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_path = session_dir / f"rollout-2026-06-03T18-00-00-{session_id}.jsonl"
    session_path.write_text(
        json.dumps(
            {
                "type": "session_meta",
                "timestamp": "2026-06-03T18:00:00Z",
                "payload": {
                    "id": session_id,
                    "timestamp": "2026-06-03T18:00:00Z",
                    "cwd": cwd.as_posix(),
                    "originator": "codex-tui",
                    "cli_version": "test",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return session_id


def test_resume_send_preview_refuses_active_root_patch_under_read_only_sandbox(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    codex_home = tmp_path / ".codex"
    session_id = _seed_codex_session(codex_home, tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    result = invoke_codex_session_store_route(
        tmp_path,
        route_id="session_resume_send_preview",
        args={"session_id": session_id, "prompt": "Please implement an active-root patch for this source/test patch."},
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "SANDBOX_MISMATCH"
    assert result["finding"] == "active_root_patch_requires_workspace_write_sandbox"
    assert result["required_sandbox"] == "workspace-write"
    assert result["requested_sandbox"] == "read-only"


def test_resume_send_preview_allows_explicit_workspace_write_for_patch_prompt(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    codex_home = tmp_path / ".codex"
    session_id = _seed_codex_session(codex_home, tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    result = invoke_codex_session_store_route(
        tmp_path,
        route_id="session_resume_send_preview",
        args={
            "session_id": session_id,
            "prompt": "Please implement an active-root patch for this source/test patch.",
            "sandbox_mode": "workspace-write",
        },
    )

    assert result["ok"] is True
    assert result["resume_possible"] is True
    assert result["bounded_execution"]["sandbox"] == "workspace-write"
    assert "--sandbox" in result["command_argv"]
    assert "workspace-write" in result["command_argv"]


def test_resume_send_preview_preserves_workspace_write_from_either_sandbox_alias(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    codex_home = tmp_path / ".codex"
    session_id = _seed_codex_session(codex_home, tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    for sandbox_args in (
        {"sandbox_mode": "read-only", "sandbox": "workspace-write"},
        {"sandbox_mode": "workspace-write", "sandbox": "read-only"},
    ):
        result = invoke_codex_session_store_route(
            tmp_path,
            route_id="session_resume_send_preview",
            args={
                "session_id": session_id,
                "prompt": "Please implement an active-root patch for this source/test patch.",
                **sandbox_args,
            },
        )

        assert result["ok"] is True
        sandbox_index = result["command_argv"].index("--sandbox")
        assert result["command_argv"][sandbox_index + 1] == "workspace-write"
        assert result["bounded_execution"]["sandbox"] == "workspace-write"


def test_resume_send_refuses_active_root_patch_under_read_only_before_execution(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    codex_home = tmp_path / ".codex"
    session_id = _seed_codex_session(codex_home, tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    result = invoke_codex_session_store_route(
        tmp_path,
        route_id="session_resume_send",
        args={
            "session_id": session_id,
            "prompt": "ACTIVE-ROOT WRITE REPAIR: source/test patch needed.",
            "idempotency_key": "sandbox-mismatch",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "SANDBOX_MISMATCH"
    assert result["mutates_active_state"] is False


def test_resume_send_preserves_workspace_write_from_sandbox_alias_before_execution(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    codex_home = tmp_path / ".codex"
    session_id = _seed_codex_session(codex_home, tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())
    captured: dict[str, object] = {}

    class FakeCompleted:
        returncode = 0
        stdout = "workspace write preserved\n"
        stderr = ""

    def fake_run(argv, cwd, text, capture_output, timeout, env):
        captured["argv"] = list(argv)
        captured["cwd"] = cwd
        captured["timeout"] = timeout
        captured["env_term"] = env["TERM"]
        assert text is True
        assert capture_output is True
        return FakeCompleted()

    monkeypatch.setattr(bridge.subprocess, "run", fake_run)

    result = invoke_codex_session_store_route(
        tmp_path,
        route_id="session_resume_send",
        args={
            "session_id": session_id,
            "prompt": "ACTIVE-ROOT WRITE REPAIR: source/test patch needed.",
            "sandbox_mode": "read-only",
            "sandbox": "workspace-write",
            "idempotency_key": "workspace-write-alias-preserved",
            "confirmation": CONFIRMATION_TOKEN,
            "timeout_seconds": 10,
        },
    )

    assert result["ok"] is True
    argv = captured["argv"]
    assert isinstance(argv, list)
    sandbox_index = argv.index("--sandbox")
    assert argv[sandbox_index + 1] == "workspace-write"
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    receipt_sandbox_index = receipt["command_argv_redacted"].index("--sandbox")
    assert receipt["command_argv_redacted"][receipt_sandbox_index + 1] == "workspace-write"


def test_resume_send_tui_inline_driver_uses_codex_resume_no_alt_screen(tmp_path: Path, monkeypatch) -> None:
    _seed_root(tmp_path)
    codex_home = tmp_path / ".codex"
    session_id = _seed_codex_session(codex_home, tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())
    captured: dict[str, object] = {}

    def fake_pty(argv, cwd, timeout_seconds, env):
        captured["argv"] = list(argv)
        assert argv[1:5] == ["resume", "--no-alt-screen", "--sandbox", "workspace-write"]
        assert argv[-2] == session_id
        assert argv[-1] == "continue"
        assert timeout_seconds == 10
        assert env["TERM"] == "xterm-256color"
        return 0, False, "SESSION_RESUME_BRIDGE_SMOKE_OK\n", ""

    monkeypatch.setattr(bridge, "_run_tui_inline_pty", fake_pty)

    preview = invoke_codex_session_store_route(
        tmp_path,
        route_id="session_resume_send_preview",
        args={
            "session_id": session_id,
            "prompt": "continue",
            "sandbox_mode": "workspace-write",
            "driver_mode": "tui_inline",
        },
    )

    assert preview["ok"] is True
    assert preview["bounded_execution"]["driver_mode"] == "tui_inline"
    assert preview["bounded_execution"]["mode"] == "codex_resume_tui_inline_no_alt_screen"
    assert preview["command_argv"][1:5] == ["resume", "--no-alt-screen", "--sandbox", "workspace-write"]

    result = invoke_codex_session_store_route(
        tmp_path,
        route_id="session_resume_send",
        args={
            "session_id": session_id,
            "prompt": "continue",
            "sandbox_mode": "workspace-write",
            "driver_mode": "tui_inline",
            "idempotency_key": "tui-inline-continue",
            "confirmation": CONFIRMATION_TOKEN,
            "timeout_seconds": 10,
        },
    )

    assert result["ok"] is True
    assert result["driver_mode"] == "tui_inline"
    assert captured["argv"][1:5] == ["resume", "--no-alt-screen", "--sandbox", "workspace-write"]
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    assert receipt["driver_mode"] == "tui_inline"
    assert receipt["driver_label"] == "codex_resume_tui_inline_no_alt_screen"
