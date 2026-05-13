# MCP-Down Write Policy

Purpose: prevent thread/log corruption when multiple agents run on the same machine.

## Required Rule

Do not manually edit:

- `docs/communications_mcp_down/threads/*.md`
- `docs/communications_mcp_down/logs/messages.jsonl`
- `docs/communications_mcp_down/threads/INDEX.md`

Use only:

```powershell
python scripts/offline_comms/post_offline_message.py ...
```

## Why

- Script writes thread entry + jsonl + index atomically in one workflow.
- Manual edits have already introduced malformed IDs and escaped content artifacts.

## Message Format Requirement

Include lock state in every runtime-affecting message:

- `LOCK:HELD_BY=<canonical id>`
- `LOCK:RELEASED`

Optional enforced lock:

```powershell
python scripts/offline_comms/runtime_action_lock.py acquire --owner "Codex Agent" --holder-id "codex_session_A" --reason "runtime_action"
python scripts/offline_comms/runtime_action_lock.py release --owner "Codex Agent" --holder-id "codex_session_A"
```

Important:
- `owner` alone is not enough when multiple Codex chats are active.
- Use a unique `holder-id` per runtime instance/chat.

## Recovery If Corruption Is Detected

1. Freeze manual edits.
2. Continue writes only through `post_offline_message.py`.
3. Record corruption note in latest thread message.
4. Defer cleanup rewrite until MCP transport is stable.
