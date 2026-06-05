import json
from pathlib import Path

from kernel.ion_agent_workspace_comms import (
    build_agent_home_view,
    materialize_agent_workspace_comms_protocol,
    run_agent_home_view_smoke,
)


def _write(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_root(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    (tmp_path / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    _write(
        tmp_path,
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        {
            "schema_id": "ion.codex_solo_context_packages.v1",
            "selected_by_default": ["minimum_working_capsule"],
            "packages": [{"package_id": "minimum_working_capsule"}],
        },
    )
    (tmp_path / "ION/05_context/current/codex_solo/MINI.md").write_text(
        "PHASE: codex_solo_work\n",
        encoding="utf-8",
    )


def _seed_workspace(tmp_path: Path) -> None:
    thread_id = "thread_seed"
    message_id = "msg_seed"
    message_path = f"ION/05_context/current/agent_comms/threads/{thread_id}/messages/20260530T0000000000_{message_id}.json"
    thread_path = f"ION/05_context/current/agent_comms/threads/{thread_id}/THREAD.json"
    room_capsule_path = "ION/05_context/current/agent_comms/rooms/room.main.team/ROOM_CAPSULE.json"

    _write(
        tmp_path,
        "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json",
        {
            "schema_id": "ion.agent_communication_directory.v1",
            "agents_by_role": {
                "role.steward": {
                    "role_id": "role.steward",
                    "display_name": "STEWARD",
                    "mention": "@role.steward",
                }
            },
            "room_contract": {
                "schema_id": "ion.agent_room_contract.v1",
                "rooms_by_id": {
                    "room.main.team": {
                        "room_id": "room.main.team",
                        "room_kind": "main",
                        "channel_id": "team",
                        "purpose": "Shared team workspace.",
                    }
                },
            },
        },
    )
    _write(
        tmp_path,
        "ION/05_context/current/agent_comms/projections/MESSAGE_INDEX.json",
        {
            "schema_id": "ion.agent_comms.message_index.v1",
            "messages": {
                message_id: {
                    "thread_id": thread_id,
                    "message_path": message_path,
                    "thread_path": thread_path,
                    "created_at": "2026-05-30T00:00:00+00:00",
                    "from_role": "operator",
                    "to_roles": ["role.steward"],
                    "mentioned_roles": ["role.steward"],
                    "room_id": "room.main.team",
                    "room_capsule_path": room_capsule_path,
                }
            },
        },
    )
    _write(
        tmp_path,
        thread_path,
        {
            "schema_id": "ion.agent_comms.thread.v1",
            "thread_id": thread_id,
            "room_id": "room.main.team",
            "room_kind": "main",
            "status": "active",
            "participants": ["operator", "role.steward"],
            "created_by": "operator",
            "latest_message_id": message_id,
            "latest_summary": "Please handle blocker.",
            "unread_by_role": {"role.steward": 1},
            "room_capsule_path": room_capsule_path,
        },
    )
    _write(
        tmp_path,
        message_path,
        {
            "schema_id": "ion.agent_comms.message.v1",
            "message_id": message_id,
            "thread_id": thread_id,
            "from_role": "operator",
            "to_roles": ["role.steward"],
            "message_kind": "blocker",
            "subject": "Need steward action",
            "summary": "Please resolve blocker and return receipt links.",
            "requires_response": True,
            "receipt_refs": ["ION/05_context/current/chatgpt_connector/task_returns/seed_return.json"],
            "artifact_refs": ["ION/04_packages/kernel/ion_agent_comms.py"],
        },
    )
    _write(
        tmp_path,
        room_capsule_path,
        {
            "schema_id": "ion.agent_comms.room_capsule.v1",
            "room_id": "room.main.team",
            "room_kind": "main",
            "channel_id": "team",
            "participants": ["operator", "role.steward"],
            "thread_count": 1,
            "latest_message_id": message_id,
            "latest_summary": "Please handle blocker.",
            "source_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json#room_contract"],
            "artifact_refs": ["ION/04_packages/kernel/ion_agent_workspace_comms.py"],
            "route_deeper_refs": {
                "thread_path": thread_path,
                "message_path": message_path,
                "message_index_path": "ION/05_context/current/agent_comms/projections/MESSAGE_INDEX.json",
            },
        },
    )
    _write(
        tmp_path,
        "ION/05_context/current/agent_comms/inbox/role_steward/msg_seed.json",
        {
            "schema_id": "ion.agent_comms.message_ref.v1",
            "message_id": message_id,
            "thread_id": thread_id,
            "from_role": "operator",
            "message_kind": "blocker",
            "subject": "Need steward action",
            "summary": "Please resolve blocker and return receipt links.",
            "status": "unread",
            "message_path": message_path,
            "room_id": "room.main.team",
            "room_capsule_path": room_capsule_path,
            "created_at": "2026-05-30T00:00:00+00:00",
        },
    )
    _write(
        tmp_path,
        "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
        {
            "schema_id": "ion.carrier_message_queue.v1",
            "messages": [
                {
                    "message_id": "carmsg_seed",
                    "sender_carrier_id": "role.nemesis",
                    "recipient": "role.steward",
                    "channel": "team",
                    "message_type": "orientation_ping",
                    "status": "pending",
                    "created_at": "2026-05-30T00:01:00+00:00",
                    "packet_path": "ION/05_context/current/chatgpt_connector/carrier_messages/seed.json",
                    "receipt_refs": ["ION/05_context/current/chatgpt_connector/task_returns/seed.json"],
                    "context_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"],
                }
            ],
        },
    )


def test_agent_workspace_protocol_and_home_view_orientation(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_workspace(tmp_path)

    protocol = materialize_agent_workspace_comms_protocol(tmp_path)
    assert protocol["schema_id"] == "ion.agent_workspace_comms_protocol.v0"
    protocol_path = tmp_path / "ION/05_context/current/agent_comms/ion_agent_workspace_comms_protocol.v0.json"
    assert protocol_path.is_file()

    home_view = build_agent_home_view(
        tmp_path,
        role_id="role.steward",
        carrier_id="CODEX_CLI_CARRIER",
        write_projection=True,
    )
    assert home_view["ok"] is True
    assert home_view["identity"]["assigned_role"] == "role.steward"
    assert home_view["identity"]["carrier_id"] == "CODEX_CLI_CARRIER"
    assert home_view["attention"]["direct_mentions"]
    assert home_view["attention"]["role_mentions"]
    assert home_view["attention"]["owned_threads"]
    assert home_view["attention"]["blockers_waiting_on_me"]
    assert home_view["attention"]["pinned_current_directives"]
    assert home_view["attention"]["unread_ack_defer_state"]["unread_count"] == 1
    assert home_view["receipt_links"]
    assert home_view["context_read_order"]
    assert home_view["scout_context_card"]["schema_id"] == "ion.agent_home_view.scout_context_card.v0"
    assert home_view["scout_context_card"]["forbidden_default_surfaces"]
    assert home_view["self_improvement_loop"]["schema_id"] == "ion.agent_home_view.self_improvement_loop.v0"
    assert home_view["self_improvement_loop"]["counts"]["total"] >= 1
    assert "ION/05_context/current/agent_comms/logs/messages.jsonl" not in home_view["source_surfaces"]["files"]
    assert (tmp_path / home_view["projection_path"]).is_file()
    assert (tmp_path / home_view["scout_context_card_path"]).is_file()
    assert (tmp_path / home_view["self_improvement_loop_path"]).is_file()

    room_model = home_view["attention"]["pinned_current_directives"][0]
    assert room_model["room_header"]["room_id"] == "room.main.team"
    assert room_model["pinned_context_refs"]
    assert room_model["current_directive"]["message_id"] == "msg_seed"
    assert room_model["current_directive"]["expected_reply_shape"] == "task_return_with_receipts"

    smoke = run_agent_home_view_smoke(tmp_path, role_id="role.steward", carrier_id="CODEX_CLI_CARRIER")
    assert smoke["ok"] is True
    assert smoke["oriented_without_full_log_polling"] is True
    assert smoke["used_full_log_polling"] is False
    assert (tmp_path / smoke["smoke_receipt_path"]).is_file()


def test_agent_home_view_scan_limits_are_compact_and_warn(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_workspace(tmp_path)

    for idx in range(6):
        _write(
            tmp_path,
            f"ION/05_context/current/agent_comms/inbox/role_steward/extra_{idx}.json",
            {
                "schema_id": "ion.agent_comms.message_ref.v1",
                "message_id": f"msg_extra_{idx}",
                "thread_id": "thread_seed",
                "from_role": "operator",
                "subject": f"Extra inbox item {idx}",
                "summary": "extra",
                "status": "unread",
            },
        )

    for idx in range(5):
        thread_id = f"thread_extra_{idx}"
        _write(
            tmp_path,
            f"ION/05_context/current/agent_comms/threads/{thread_id}/THREAD.json",
            {
                "schema_id": "ion.agent_comms.thread.v1",
                "thread_id": thread_id,
                "room_id": "room.main.team",
                "room_kind": "main",
                "status": "active",
                "participants": ["role.steward", "operator"],
                "created_by": "operator",
                "latest_summary": f"Thread extra {idx}",
            },
        )

    carrier_messages = [
        {
            "message_id": f"carmsg_extra_{idx}",
            "sender_carrier_id": "role.nemesis",
            "recipient": "role.steward",
            "channel": "team",
            "message_type": "orientation_ping",
            "status": "pending",
            "created_at": f"2026-05-30T00:01:{idx:02d}+00:00",
            "packet_path": f"ION/05_context/current/chatgpt_connector/carrier_messages/extra_{idx}.json",
            "receipt_refs": [],
            "context_refs": [],
        }
        for idx in range(8)
    ]
    _write(
        tmp_path,
        "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
        {
            "schema_id": "ion.carrier_message_queue.v1",
            "messages": carrier_messages,
        },
    )

    home_view = build_agent_home_view(
        tmp_path,
        role_id="role.steward",
        max_inbox_scan=2,
        max_thread_scan=2,
        max_carrier_scan=3,
        max_index_scan=1,
    )

    warnings = {row["code"] for row in home_view["attention"]["partial_visibility_warnings"]}
    assert "inbox_scan_limited" in warnings
    assert "thread_scan_limited" in warnings
    assert "carrier_queue_scan_limited" in warnings
    assert "message_index_scan_limited" not in warnings

    assert len(home_view["attention"]["direct_mentions"]) <= 2
    assert len(home_view["attention"]["owned_threads"]) <= 2
    assert home_view["scout_context_card"]["compact_defaults"]["inbox_scan_cap"] == 2
    assert home_view["scout_context_card"]["compact_defaults"]["thread_scan_cap"] == 2
    assert home_view["scout_context_card"]["compact_defaults"]["carrier_queue_scan_cap"] == 3
    assert "ION/05_context/current/agent_comms/logs/messages.jsonl" in home_view["scout_context_card"]["forbidden_default_surfaces"]
