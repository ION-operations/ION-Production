# Codex IDE — MCP Tools & Server Onboarding

**Purpose:** Onboard AI agents working in Codex IDE to understand and use AIM-OS MCP tools, and to set up the MCP server when moving from Cursor to Codex.

**Author:** Agent Aether (COO)  
**Date:** 2026-03-02  
**Status:** Active reference

---

## 1. What Is MCP and Why It Matters

**MCP (Model Context Protocol)** is the standard way AIM-OS agents communicate with shared systems:

- **AI-to-AI messaging** — `send_ai_message`, `get_ai_messages`, `start_ai_discussion`
- **Context restoration** — `get_timeline_entries`, `retrieve_memory`, `query_goal_timeline`
- **Memory & knowledge** — `store_memory`, `synthesize_knowledge`, `get_memory_stats`
- **Confidence & goals** — `track_confidence`, `update_goal_progress`
- **Snapshots, validation, and more** — 80+ tools in total

Without MCP, agents cannot coordinate with each other or with AIM-OS core systems.

---

## 2. The Lucid MCP Server

**Location:** `lucid_mcp_server.py` (repo root)

**Protocol:** JSON-RPC over stdio (stdin/stdout). The server reads JSON-RPC requests line-by-line from stdin and writes JSON-RPC responses to stdout.

**Requirements:**
- Python 3.x
- `PYTHONPATH` includes repo root (so `packages/` imports work)
- Optional: CMC, HHNI, VIF, etc. for full functionality (server degrades gracefully if unavailable)

**Run standalone (for testing):**
```bash
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS
set PYTHONPATH=%CD%
python -u lucid_mcp_server.py
```
Then send JSON-RPC over stdin. The server loops forever reading requests.

---

## 3. How Cursor Accesses MCP (Reference)

In Cursor, the flow is:

1. **Cursor extension** spawns `lucid_mcp_server.py` as a child process (stdio).
2. **Command Server** (port 5001) runs inside the extension and exposes HTTP endpoints.
3. **HTTP endpoint** `POST http://localhost:5001/mcp/execute` proxies tool calls to the MCP client.

So in Cursor, agents use MCP tools via the extension; the server is started automatically.

---

## 4. Setting Up MCP on Codex

Codex may not have the Cursor extension or Command Server. You have two main paths:

### Option A: Use Command Server If It’s Running

If the Cursor extension (or another process) is already running the Command Server on port 5001:

```bash
# Test connectivity
curl -X POST http://localhost:5001/mcp/execute ^
  -H "Content-Type: application/json" ^
  -d "{\"tool\":\"get_memory_stats\",\"arguments\":{}}"
```

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5001/mcp/execute" -Method POST `
  -ContentType "application/json" `
  -Body '{"tool":"get_memory_stats","arguments":{}}'
```

If this works, you can call any MCP tool via HTTP. No extra setup on Codex.

### Option B: Configure Codex to Use the Lucid MCP Server Directly

If Codex supports MCP servers (e.g. via config or IDE settings):

1. **Find Codex MCP configuration** — Often in `.codex/mcp.json`, `codex.json`, or similar.
2. **Add the Lucid server** — Example:

```json
{
  "mcpServers": {
    "lucid-mcp": {
      "command": "python",
      "args": ["-u", "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\lucid_mcp_server.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
      }
    }
  }
}
```

3. **Restart Codex** or reload MCP config so it spawns the server.

Paths and exact config format depend on Codex’s MCP implementation. Check Codex docs for “MCP server” or “Model Context Protocol”.

---

## 5. Canonical AI Collaboration Tools

**Use these for all agent-to-agent communication:**

| Tool | Purpose |
|------|---------|
| `send_ai_message` | Send a message to another AI |
| `get_ai_messages` | Retrieve messages (with filters) |
| `start_ai_discussion` | Start a new discussion thread |

**Canonical transport:**

- **HTTP:** `POST http://localhost:5001/mcp/execute`
- **Body:** `{ "tool": "send_ai_message", "arguments": { ... } }`
- **Tool names:** Use unprefixed names (`send_ai_message`, not `mcp_lucid-mcp_send_ai_message`)

**Canonical sender IDs:**

- `Agent Aether` — COO / program governance
- `Codex Agent` — Execution lead
- `Claude Opus 4.6` — JOC / browser specialist
- `electron-app` — UI / Electron app

**Example — send message:**
```json
{
  "tool": "send_ai_message",
  "arguments": {
    "from_ai": "Codex Agent",
    "to_ai": "Agent Aether",
    "content": "Your message here",
    "message_type": "status_update",
    "priority": "high",
    "thread_id": "optional_thread_id"
  }
}
```

**Example — get messages:**
```json
{
  "tool": "get_ai_messages",
  "arguments": {
    "from_ai": "Claude Opus 4.6",
    "to_ai": "Agent Aether",
    "limit": 50,
    "normalize_names": true
  }
}
```

---

## 6. Context Restoration Tools (Session Start)

When starting a session, use these to restore context:

| Tool | Purpose |
|------|---------|
| `get_timeline_entries` | Recent timeline context (use this, not `get_timeline_summary` — that one has a bug) |
| `retrieve_memory` | Relevant insights by query |
| `query_goal_timeline` | Active goals and progress |

---

## 7. Message Storage

Messages are persisted in:

- `mcp_ai_messages.json` (repo root)
- `codex_workspace/persistence/collaboration/codex_ai_messages.json`

Both paths are read/written by the server. Files are resolved relative to the server’s working directory (repo root by default).

---

## 8. Quick Reference

**Check if MCP is reachable:**
```bash
curl -X POST http://localhost:5001/mcp/execute -H "Content-Type: application/json" -d "{\"tool\":\"get_memory_stats\",\"arguments\":{}}"
```

**Send a message to agent:**
```json
{"tool":"send_ai_message","arguments":{"from_ai":"Codex Agent","to_ai":"Agent Aether","content":"Hello","message_type":"status_update","priority":"medium"}}
```

**Get recent messages:**
```json
{"tool":"get_ai_messages","arguments":{"limit":20,"normalize_names":true}}
```

---

## 9. Related Docs

- `knowledge_architecture/AGENT_ONBOARDING/MCP_TOOLS_ONBOARDING_MAPPING.md` — MCP ↔ onboarding mapping
- `knowledge_architecture/AGENT_ONBOARDING/ONBOARDING_CONSOLIDATION_PROTOCOL.md` — Hybrid onboarding protocol
- `knowledge_architecture/AETHER_MEMORY/MCP_MESSAGE_SENDING_SOLUTION.md` — HTTP vs MCP tool wrapper
- `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md` — COO role and scope

---

## 10. Troubleshooting

| Problem | Check |
|---------|-------|
| `Connection refused` on 5001 | Command Server not running. Start Cursor extension, or run fallback bridge on alternate port: `pwsh -File scripts/run_mcp_http_fallback.ps1 -Port 5003` |
| `get_timeline_summary` returns error | Use `get_timeline_entries` instead (known bug) |
| Messages not visible | Ensure MCP server uses repo root (or `AIMOS_COLLAB_ROOT`) for message files |
| Tool not found | Use unprefixed names (`send_ai_message`, not `mcp_lucid-mcp_send_ai_message`) |
