import json
from pathlib import Path

from kernel.ion_codex_conversation_archive import attach_codex_conversation_to_chat, build_codex_conversation_archive
from kernel.ion_dual_codex_chat import WRITE_CONFIRMATION_TOKEN, load_dual_chat_state


SESSION_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def seed_codex_home(root: Path) -> Path:
    codex_home = root / "codex-home"
    write_jsonl(
        codex_home / "history.jsonl",
        [
            {
                "session_id": SESSION_ID,
                "ts": "2026-05-23T12:03:00+00:00",
                "text": "archive smoke token=super-secret-value",
            }
        ],
    )
    write_jsonl(
        codex_home / "session_index.jsonl",
        [
            {
                "id": SESSION_ID,
                "thread_name": "Archive smoke thread",
                "updated_at": "2026-05-23T12:04:00+00:00",
            }
        ],
    )
    write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{SESSION_ID}.jsonl",
        [
            {
                "type": "session_meta",
                "timestamp": "2026-05-23T12:00:00+00:00",
                "payload": {"id": SESSION_ID, "cwd": "/workspace/ion"},
            },
            {
                "type": "turn_context",
                "timestamp": "2026-05-23T12:00:02+00:00",
                "payload": {"model": "gpt-5-codex", "cwd": "/workspace/ion"},
            },
            {
                "type": "event_msg",
                "timestamp": "2026-05-23T12:01:00+00:00",
                "payload": {"type": "user_message", "message": "show archive token=super-secret-value"},
            },
            {
                "type": "response_item",
                "timestamp": "2026-05-23T12:01:03+00:00",
                "payload": {"type": "function_call", "name": "ion_status"},
            },
            {
                "type": "response_item",
                "timestamp": "2026-05-23T12:01:04+00:00",
                "payload": {"type": "reasoning", "content": [{"type": "output_text", "text": "private hidden reasoning"}]},
            },
            {
                "type": "response_item",
                "timestamp": "2026-05-23T12:02:00+00:00",
                "payload": {"role": "assistant", "content": [{"type": "output_text", "text": "archive summary ready"}]},
            },
        ],
    )
    return codex_home


def test_codex_conversation_archive_indexes_safe_redacted_sessions(monkeypatch, tmp_path):
    codex_home = seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path)

    assert archive["schema_id"] == "ion.codex_conversation_archive.v1"
    assert archive["source_counts"]["session_files_total"] == 1
    assert archive["raw_content_exported"] is False
    assert archive["raw_transcript_exported"] is False
    assert archive["hidden_reasoning_exposed"] is False
    session = archive["sessions"][0]
    assert session["session_id"] == SESSION_ID
    assert archive["current_session_id"] == SESSION_ID
    assert session["is_current_session"] is True
    assert session["session_flags"]["current_session"] is True
    assert session["thread_name"] == "Archive smoke thread"
    assert session["display_title"] == "show archive token=[REDACTED]"
    assert session["cwd"] == "/workspace/ion"
    assert session["project_label"] == "workspace/ion"
    assert session["model"] == "gpt-5-codex"
    assert session["tool_counts"]["ion_status"] == 1
    assert session["activity_score"] > 0
    assert session["tool_summary"] == [{"name": "ion_status", "count": 1}]
    assert session["raw_transcript_exported"] is False
    assert "[REDACTED]" in session["latest_user_snippet"]
    assert "super-secret-value" not in json.dumps(archive)


def test_codex_conversation_archive_selected_excerpt_and_query_are_guarded(monkeypatch, tmp_path):
    codex_home = seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, selected_session_id=SESSION_ID, query="archive smoke")

    assert archive["source_counts"]["session_files_returned"] == 1
    assert archive["sessions"][0]["session_id"] == SESSION_ID
    excerpt = archive["selected_session_excerpt"]
    assert excerpt["found"] is True
    assert excerpt["raw_transcript_exported"] is False
    assert [item["role"] for item in excerpt["items"]] == ["user", "tool_call", "assistant"]
    assert "[REDACTED]" in excerpt["items"][0]["snippet"]
    assert excerpt["safe_transcript_exported"] is True
    assert excerpt["display_mode"] == "safe_redacted_full_transcript"
    assert excerpt["item_count"] == 3
    assert "show archive token=[REDACTED]" in excerpt["items"][0]["text"]
    assert "super-secret-value" not in json.dumps(excerpt)
    assert "private hidden reasoning" not in json.dumps(excerpt)


def test_codex_conversation_archive_keeps_direct_chat_lanes_before_content_heuristics(monkeypatch, tmp_path):
    session_id = "abababab-bbbb-cccc-dddd-eeeeeeeeeeee"
    codex_home = tmp_path / "codex-home"
    write_jsonl(codex_home / "history.jsonl", [{"session_id": session_id, "ts": "2026-05-23T12:03:00+00:00", "text": "context question"}])
    write_jsonl(codex_home / "session_index.jsonl", [{"id": session_id, "thread_name": "Direct lane thread"}])
    write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{session_id}.jsonl",
        [
            {
                "type": "session_meta",
                "timestamp": "2026-05-23T12:00:00+00:00",
                "payload": {"id": session_id, "cwd": "/workspace/ion"},
            },
            {
                "type": "response_item",
                "timestamp": "2026-05-23T12:01:00+00:00",
                "payload": {"role": "user", "content": [{"type": "input_text", "text": "show capsule context and compaction state"}]},
            },
            {
                "type": "response_item",
                "timestamp": "2026-05-23T12:02:00+00:00",
                "payload": {
                    "role": "assistant",
                    "content": [{
                        "type": "output_text",
                        "text": "Files changed: ION/example.py. Context refreshed notes stay in the reply bubble.",
                    }],
                },
            },
        ],
    )
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, selected_session_id=session_id)

    items = archive["selected_session_excerpt"]["items"]
    assert items[0]["message_kind"] == "user_message"
    assert items[0]["visual_lane"] == "user"
    assert items[1]["message_kind"] == "assistant_reply"
    assert items[1]["visual_lane"] == "ai"


def test_codex_conversation_archive_selected_transcript_is_not_tiny_excerpt(monkeypatch, tmp_path):
    session_id = "bbbbbbbb-cccc-dddd-eeee-ffffffffffff"
    codex_home = tmp_path / "codex-home"
    write_jsonl(codex_home / "history.jsonl", [{"session_id": session_id, "ts": "2026-05-23T14:03:00+00:00", "text": "long chat"}])
    write_jsonl(codex_home / "session_index.jsonl", [{"id": session_id, "thread_name": "Long chat", "updated_at": "2026-05-23T14:04:00+00:00"}])
    rows = [
        {
            "type": "session_meta",
            "timestamp": "2026-05-23T14:00:00+00:00",
            "payload": {"id": session_id, "cwd": "/workspace/ion"},
        },
        {
            "type": "turn_context",
            "timestamp": "2026-05-23T14:00:01+00:00",
            "payload": {"model": "gpt-5-codex", "cwd": "/workspace/ion"},
        },
    ]
    for index in range(35):
        rows.append({
            "type": "response_item",
            "timestamp": f"2026-05-23T14:{index % 60:02d}:02+00:00",
            "payload": {"role": "user" if index % 2 == 0 else "assistant", "content": [{"type": "output_text", "text": f"message {index} full body"}]},
        })
    write_jsonl(codex_home / f"sessions/2026/05/23/rollout-{session_id}.jsonl", rows)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, selected_session_id=session_id)

    excerpt = archive["selected_session_excerpt"]
    assert excerpt["safe_transcript_exported"] is True
    assert excerpt["raw_transcript_exported"] is False
    assert excerpt["item_count"] == 35
    assert len(excerpt["items"]) == 35
    assert len(excerpt["items"]) > 24
    assert excerpt["items"][-1]["text"] == "message 34 full body"


def test_codex_conversation_archive_selected_transcript_prefers_latest_tail(monkeypatch, tmp_path):
    session_id = "cccccccc-dddd-eeee-ffff-000000000000"
    codex_home = tmp_path / "codex-home"
    write_jsonl(codex_home / "history.jsonl", [{"session_id": session_id, "ts": "2026-05-23T15:03:00+00:00", "text": "latest visible prompt"}])
    write_jsonl(codex_home / "session_index.jsonl", [])
    rows = [
        {
            "type": "session_meta",
            "timestamp": "2026-05-23T15:00:00+00:00",
            "payload": {"id": session_id, "cwd": "/workspace/ion"},
        }
    ]
    for index in range(1005):
        rows.append({
            "type": "response_item",
            "timestamp": f"2026-05-23T15:{index % 60:02d}:02+00:00",
            "payload": {"role": "assistant", "content": [{"type": "output_text", "text": f"display item {index}"}]},
        })
    rows.append({
        "type": "event_msg",
        "timestamp": "2026-05-23T15:59:00+00:00",
        "payload": {"type": "user_message", "message": "latest visible prompt"},
    })
    write_jsonl(codex_home / f"sessions/2026/05/23/rollout-{session_id}.jsonl", rows)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, selected_session_id=session_id)

    excerpt = archive["selected_session_excerpt"]
    assert archive["current_session_id"] == session_id
    assert excerpt["is_current_session"] is True
    assert excerpt["display_mode"] == "safe_redacted_latest_transcript_window"
    assert excerpt["window_mode"] == "latest_tail"
    assert excerpt["item_count"] == 1000
    assert excerpt["total_displayable_items"] == 1006
    assert excerpt["omitted_older_items"] == 6
    assert excerpt["items"][0]["index"] == 7
    assert excerpt["items"][-1]["text"] == "latest visible prompt"


def test_codex_conversation_archive_selected_transcript_supports_range_windows(monkeypatch, tmp_path):
    session_id = "dddddddd-eeee-ffff-0000-111111111111"
    codex_home = tmp_path / "codex-home"
    write_jsonl(codex_home / "history.jsonl", [{"session_id": session_id, "ts": "2026-05-23T16:03:00+00:00", "text": "range window"}])
    write_jsonl(codex_home / "session_index.jsonl", [])
    rows = [
        {
            "type": "session_meta",
            "timestamp": "2026-05-23T16:00:00+00:00",
            "payload": {"id": session_id, "cwd": "/workspace/ion"},
        }
    ]
    for index in range(1200):
        text = f"display item {index}"
        if index == 500:
            text = "*** Begin Patch\n*** Update File: ION/example.py\n+changed\n*** End Patch"
        rows.append({
            "type": "response_item",
            "timestamp": f"2026-05-23T16:{index % 60:02d}:02+00:00",
            "payload": {"role": "assistant", "content": [{"type": "output_text", "text": text}]},
        })
    write_jsonl(codex_home / f"sessions/2026/05/23/rollout-{session_id}.jsonl", rows)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(
        tmp_path,
        selected_session_id=session_id,
        selected_window_start=501,
        selected_window_count=500,
    )

    excerpt = archive["selected_session_excerpt"]
    assert excerpt["display_mode"] == "safe_redacted_transcript_window"
    assert excerpt["window_mode"] == "bounded_window"
    assert excerpt["window_count"] == 500
    assert excerpt["item_count"] == 500
    assert excerpt["total_displayable_items"] == 1200
    assert excerpt["oldest_item_index"] == 501
    assert excerpt["newest_item_index"] == 1000
    assert excerpt["omitted_older_items"] == 500
    assert excerpt["omitted_newer_items"] == 200
    assert excerpt["has_older_items"] is True
    assert excerpt["has_newer_items"] is True
    assert excerpt["items"][0]["message_kind"] == "diff"
    assert excerpt["items"][0]["visual_lane"] == "diff"
    assert excerpt["items"][0]["diff_stats"]["files"] == ["ION/example.py"]
    assert excerpt["items"][0]["diff_stats"]["added_lines"] == 1


def test_codex_conversation_archive_includes_safe_compaction_hook_receipts(monkeypatch, tmp_path):
    session_id = "eeeeeeee-ffff-0000-1111-222222222222"
    codex_home = tmp_path / "codex-home"
    write_jsonl(codex_home / "history.jsonl", [{"session_id": session_id, "ts": "2026-05-23T17:03:00+00:00", "text": "compact hook"}])
    write_jsonl(codex_home / "session_index.jsonl", [])
    write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{session_id}.jsonl",
        [
            {
                "type": "session_meta",
                "timestamp": "2026-05-23T17:00:00+00:00",
                "payload": {"id": session_id, "cwd": "/workspace/ion"},
            },
            {
                "type": "event_msg",
                "timestamp": "2026-05-23T17:01:00+00:00",
                "payload": {"type": "user_message", "message": "before compact"},
            },
        ],
    )
    receipt_path = tmp_path / f"ION/05_context/current/codex_cli/hooks/runtime/precompact/20260523T170200+0000_PreCompact_{session_id}_turn.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps({
        "event_name": "PreCompact",
        "created_at": "2026-05-23T17:02:00+00:00",
        "ion_operation_targets": ["receipt_preservation", "next_packet_compile"],
        "operation_payload": {
            "checkpoint_kind": "precompact_context_baton",
            "active_objective": {
                "mission": "Maintain Codex chat",
                "phase": "codex_solo_work",
                "last_receipt": "Windowed transcript ready",
                "next_action": "Render compaction cards",
            },
        },
    }), encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, selected_session_id=session_id, selected_window_count=20)

    excerpt = archive["selected_session_excerpt"]
    hook_items = [item for item in excerpt["items"] if item["source_type"] == "hook_receipt"]
    assert len(hook_items) == 1
    assert hook_items[0]["message_kind"] == "compaction"
    assert hook_items[0]["compaction_markers"] == ["PRECOMPACT"]
    assert hook_items[0]["path_refs"][0].startswith("ION/05_context/current/codex_cli/hooks/runtime/precompact/")
    assert "Render compaction cards" in hook_items[0]["text"]


def test_codex_conversation_archive_query_filters_sessions(monkeypatch, tmp_path):
    codex_home = seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, query="does-not-exist")

    assert archive["source_counts"]["session_files_total"] == 1
    assert archive["source_counts"]["session_files_returned"] == 0
    assert archive["sessions"] == []


def test_codex_conversation_archive_derives_project_mission_agent_labels(monkeypatch, tmp_path):
    session_id = "11111111-2222-3333-4444-555555555555"
    codex_home = tmp_path / "codex-home"
    write_jsonl(codex_home / "history.jsonl", [{"session_id": session_id, "ts": "2026-05-23T13:03:00+00:00", "text": "drawer sessions"}])
    write_jsonl(
        codex_home / "session_index.jsonl",
        [{
            "id": session_id,
            "thread_name": "# AGENTS.md instructions for /home/sev/ION - Production <INSTRUCTIONS> Continuity Recovery Rule",
            "updated_at": "2026-05-23T13:04:00+00:00",
        }],
    )
    write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{session_id}.jsonl",
        [
            {
                "type": "session_meta",
                "timestamp": "2026-05-23T13:00:00+00:00",
                "payload": {"id": session_id, "cwd": "/home/sev/ION - Production/ION_Developement"},
            },
            {
                "type": "turn_context",
                "timestamp": "2026-05-23T13:00:01+00:00",
                "payload": {"model": "gpt-5.5", "cwd": "/home/sev/ION - Production/ION_Developement"},
            },
            {
                "type": "event_msg",
                "timestamp": "2026-05-23T13:01:00+00:00",
                "payload": {"type": "user_message", "message": "Build project mission drawer"},
            },
            {
                "type": "event_msg",
                "timestamp": "2026-05-23T13:01:02+00:00",
                "payload": {
                    "type": "developer_context",
                    "message": "\n".join([
                        "active_mission: Maintain the primary Codex Capsule chat profile with bounded full-ION comms.",
                        "suggested_domain: codex_carrier_sync",
                        "suggested_skill: ion-orchestration",
                        "role_phase_sequence: PERSONA_INTERFACE_INGRESS -> RELAY -> STEWARD -> MASON -> SCRIBE",
                    ]),
                },
            },
            {
                "type": "response_item",
                "timestamp": "2026-05-23T13:02:00+00:00",
                "payload": {"type": "function_call", "name": "exec_command"},
            },
        ],
    )
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    archive = build_codex_conversation_archive(tmp_path, query="conversation navigator")

    assert archive["source_counts"]["session_files_returned"] == 1
    session = archive["sessions"][0]
    assert session["display_title"] == "Build project mission drawer"
    assert session["project_label"] == "ION - Production/ION_Developement"
    assert any(label["label"].startswith("Maintain the primary Codex Capsule") and label["confidence"] == "explicit" for label in session["mission_labels"])
    assert any(label["label"] == "Conversation Navigator" and label["confidence"] == "weak" for label in session["mission_labels"])
    assert any(label["label"] == "STEWARD" and label["confidence"] == "explicit" for label in session["agent_labels"])
    assert any(label["label"] == "ion-orchestration" and label["source"] == "suggested_skill" for label in session["agent_labels"])
    assert session["session_flags"]["has_explicit_mission"] is True
    assert session["tool_summary"] == [{"name": "exec_command", "count": 1}]


def test_attach_codex_conversation_to_chat_adds_active_redacted_context(monkeypatch, tmp_path):
    codex_home = seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    result = attach_codex_conversation_to_chat(
        tmp_path,
        session_id=SESSION_ID,
        confirmation=WRITE_CONFIRMATION_TOKEN,
    )

    assert result["ok"] is True
    packet = result["packet"]
    assert packet["schema_id"] == "ion.codex_conversation_archive_attachment.v1"
    assert packet["raw_transcript_exported"] is False
    assert packet["codex_resume"]["command"] == ["codex", "resume", SESSION_ID]
    assert "[REDACTED]" in packet["attachment_text"]
    assert "super-secret-value" not in json.dumps(packet)
    assert (tmp_path / packet["packet_path"]).exists()
    state = load_dual_chat_state(tmp_path)
    attachments = state["memory"]["archive_attachments"]
    assert attachments[0]["session_id"] == SESSION_ID
    assert attachments[0]["status"] == "active"
    assert any(turn.get("kind") == "archive_attachment" and turn.get("session_id") == SESSION_ID for turn in state["lanes"]["codex_general"]["turns"])
