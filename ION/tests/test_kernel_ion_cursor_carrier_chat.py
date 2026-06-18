import json
from pathlib import Path

from kernel.ion_cursor_carrier_chat import (
    build_cursor_carrier_chat_model,
    record_cursor_chat_turn,
    run_cursor_carrier_chat_turn,
)

_HASH_A = "a" * 64


def _write_minimal_ion_tree(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


def _write_turn_packet(root: Path) -> None:
    turn = {
        "schema_id": "ion.carrier_turn_packet.v1",
        "spawn_queue": [
            {
                "index": 1,
                "role": "steward",
                "context_package_path": "ION/05_context/current/pkg.md",
                "context_load_receipt_path": "ION/05_context/current/receipt.json",
            }
        ],
    }
    path = root / "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(turn, indent=2) + "\n", encoding="utf-8")


def _write_receipt(root: Path) -> None:
    receipt = {
        "required_context_reads": [
            {"path": "ION/REPO_AUTHORITY.md", "kind": "file", "required": True},
        ]
    }
    path = root / "ION/05_context/current/receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def _passing_output() -> str:
    return (
        "### CONTEXT PROOF\n"
        "- path: ION/REPO_AUTHORITY.md\n"
        f"  sha256: {_HASH_A}\n"
        "  line: L1\n"
        "  excerpt: authority\n\n"
        "### TEMPLATE ACTION PROOF\n"
        "template_id: ion.template.patch_proposal.v1\n"
        "action_id: cursor_carrier_chat_turn\n"
        "result: bounded proof run\n"
        "touched_paths:\n"
        "  - ION/05_context/current/example.json\n\n"
        "### RESULT\n"
        "bounded cursor carrier chat turn\n"
    )


def _write_recent_run(root: Path, *, run_name: str = "cursor_run_test_steward") -> Path:
    run_dir = root / "ION/05_context/current/cursor_connector/cursor_queue_runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / "output.md"
    output_path.write_text("# prior run\n", encoding="utf-8")
    return output_path


def test_build_cursor_carrier_chat_model_returns_spawn_queue_and_runs(tmp_path: Path) -> None:
    _write_minimal_ion_tree(tmp_path)
    _write_turn_packet(tmp_path)
    _write_recent_run(tmp_path)

    model = build_cursor_carrier_chat_model(tmp_path)

    assert model["schema_id"] == "ion.cursor_carrier_chat_model.v1"
    assert len(model["spawn_queue"]) == 1
    assert model["spawn_queue"][0]["role"] == "steward"
    assert model["spawn_queue"][0]["index"] == 1
    assert model["spawn_queue"][0]["context_package_path"] == "ION/05_context/current/pkg.md"
    assert len(model["recent_runs"]) == 1
    assert model["recent_runs"][0]["run_dir"] == "cursor_run_test_steward"
    assert model["recent_runs"][0]["output_present"] is True
    assert model["production_authority"] is False


def test_build_cursor_carrier_chat_model_includes_carrier_control_proof_summary(tmp_path: Path) -> None:
    _write_minimal_ion_tree(tmp_path)
    _write_turn_packet(tmp_path)
    receipt_path = tmp_path / "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_RECEIPT.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(
            {
                "accepted": True,
                "integration_decision": "ALLOW_CARRIER_CONTINUE",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    model = build_cursor_carrier_chat_model(tmp_path)

    assert model["carrier_control_proof"] == {
        "accepted": True,
        "integration_decision": "ALLOW_CARRIER_CONTINUE",
        "receipt_path": "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_RECEIPT.json",
    }


def test_run_cursor_carrier_chat_turn_with_injected_runner(tmp_path: Path) -> None:
    _write_minimal_ion_tree(tmp_path)
    _write_turn_packet(tmp_path)
    _write_receipt(tmp_path)

    run_dir = tmp_path / "ION/05_context/current/cursor_connector/cursor_queue_runs/cursor_run_fake"
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / "output.md"
    output_path.write_text(_passing_output(), encoding="utf-8")
    output_rel = "ION/05_context/current/cursor_connector/cursor_queue_runs/cursor_run_fake/output.md"

    runner_payload = {
        "ok": True,
        "output_path": output_rel,
        "returncode": 0,
    }

    class FakeCompleted:
        returncode = 0
        stdout = json.dumps(runner_payload)
        stderr = ""

    def fake_runner(command, **kwargs):  # noqa: ANN001
        assert "--no-record-return" in command
        assert Path(kwargs["cwd"]).resolve() == tmp_path.resolve()
        assert kwargs["env"]["PYTHONPATH"] == "ION/04_packages"
        return FakeCompleted()

    result = run_cursor_carrier_chat_turn(
        tmp_path,
        operator_message="continue",
        role="steward",
        index=1,
        _runner=fake_runner,
    )

    assert result["both_accepted"] is True
    assert result["context_proof_accepted"] is True
    assert result["template_action_accepted"] is True
    assert result["output_path"] == output_rel
    assert result["runner_returncode"] == 0
    assert result["findings"] == []


def test_record_cursor_chat_turn_appends_turns(tmp_path: Path) -> None:
    _write_minimal_ion_tree(tmp_path)

    first = record_cursor_chat_turn(
        tmp_path,
        operator_message="hello",
        assistant_text="world",
        turn_result={"both_accepted": True},
    )
    second = record_cursor_chat_turn(
        tmp_path,
        operator_message="again",
        assistant_text="done",
        turn_result={"both_accepted": False},
    )

    assert first["ok"] is True
    assert second["turn_count"] == 2
    state = json.loads(
        (tmp_path / "ION/05_context/current/cursor_carrier_chat/state.json").read_text(encoding="utf-8")
    )
    assert state["schema_id"] == "ion.cursor_carrier_chat_state.v1"
    assert len(state["turns"]) == 2
    assert state["turns"][0]["operator_message"] == "hello"
    assert state["turns"][1]["assistant_text"] == "done"
