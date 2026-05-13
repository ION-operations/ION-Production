# MCP Server — System Summary

> **Source:** `lucid_mcp_server.py` (571KB — monolith)
> **Status:** Functional, needs modularization
> **Config:** `/home/sev/.gemini/settings.json` + `/home/sev/.gemini/antigravity/mcp_config.json`

## What MCP Does
Model Context Protocol server that bridges AI agents to persistent tools. Runs via stdio or HTTP fallback (port 5001).

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Memory** | `store_memory`, `retrieve_memory`, `list_memories` | Key-value memory persistence |
| **Context** | `record_context_capsule`, `get_timeline_summary` | Session capsule creation, timeline |
| **Agent Comms** | `send_ai_message`, `get_ai_messages`, `list_agents` | Inter-agent messaging |
| **Session** | `get_session_status`, `update_session` | Session state tracking |

## Runtime Files
- `mcp_ai_messages.json` — Agent message store
- `mcp_timeline_entries.json` — Timeline entries
- `mcp_memory/` — 175 memory files

## Known Issues
- **ISS-004:** Monolith at 571KB — needs modularization
- `.bak` file is 567KB of dead weight
- Logs (mcp_err.log, mcp_out.log) should be gitignored

## Integration with Workspace
→ Comms (§8) via send/get_ai_messages
→ User (§6) via store/retrieve_memory
→ Mission (§11) via record_context_capsule
