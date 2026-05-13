# MCP Runbook — Launch Options

**Purpose:** How to start MCP for different clients (Cursor, JOC, ChatGPT, Codex).  
**Updated:** 2026-03-07

---

## CANON: Codex Requires HTTP Fallback

**Codex has no stdio path.** Only Cursor spawns `lucid_mcp_server.py` directly. **For Codex sessions: start HTTP fallback BEFORE using Codex.**

```powershell
powershell -File scripts/mcp_control.ps1 -Action ensure
```

This is now the preferred recovery/start command because it verifies:
- `/health`
- `/mcp/list`
- a real `get_memory_stats` tool call

If the bridge is half-dead, `ensure` restarts it and re-tests the full tool surface. Without a healthy `:5001` bridge, Codex cannot reach MCP tools. (DEC-008 plus 2026-03-07 recovery hardening)

---

## Quick Reference

| Client | Transport | Port | Script | Notes |
|--------|-----------|------|--------|-------|
| Cursor | stdio | — | Extension spawns `lucid_mcp_server.py` | Automatic |
| **Codex** | **HTTP** | **5001** | `scripts/mcp_http_fallback_server.py` | **REQUIRED — Codex has no stdio** |
| JOC / agents | HTTP | 5001 | `scripts/mcp_http_fallback_server.py` | `/mcp/execute` |
| **ChatGPT** | **SSE** | **8000** | `scripts/mcp_sse_server.py` + ngrok | Native ChatGPT MCP |

---

## 1. HTTP Fallback (Cursor, JOC, Codex)

For Cursor (when extension uses HTTP), JOC, or any client hitting `:5001`:

```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS
powershell -File scripts/mcp_control.ps1 -Action ensure
# Or, if you specifically need a raw manual launch:
python scripts/mcp_http_fallback_server.py
```

- **Health:** `GET http://localhost:5001/health`
- **Execute:** `POST http://localhost:5001/mcp/execute` with `{"tool": "...", "arguments": {...}}`
- **List tools:** `GET http://localhost:5001/mcp/list`
- **Full readiness check:** `powershell -File scripts/mcp_control.ps1 -Action test`

---

## 2. ChatGPT Native MCP (GPT 5.2)

ChatGPT Developer Mode connects via SSE. Requires two terminals:

**Terminal 1 — SSE server:**
```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS
python scripts/mcp_sse_server.py
```
Listens on `http://localhost:8000`. Exposes 15 core tools (comms, memory, planning, quality, timeline).

**Terminal 2 — ngrok tunnel:**
```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS
python scripts/ngrok_tunnel.py
```
Exposes `:8000` via HTTPS. Output shows:
```
>>> PASTE THIS INTO CHATGPT APP <<<
MCP Server URL: https://xxxx.ngrok.io/sse
```

Paste that URL into ChatGPT App creation screen. GPT 5.2 can then call `get_memory_stats`, `store_memory`, `send_ai_message`, etc.

**Dependencies:** `pip install fastmcp pyngrok` (if not already installed)

---

## 3. Stdio (Cursor Extension)

When Cursor extension runs MCP, it spawns:
```bash
python -u lucid_mcp_server.py
```
With `PYTHONPATH` set to repo root. No manual start needed.

---

## 4. Troubleshooting

| Symptom | Fix |
|---------|-----|
| **Codex can't connect to MCP** | Run `powershell -File scripts/mcp_control.ps1 -Action ensure` |
| `:5001` connection refused | Run `powershell -File scripts/mcp_control.ps1 -Action ensure` |
| `:5001` is listening but requests fail or close unexpectedly | Run `powershell -File scripts/mcp_control.ps1 -Action ensure` |
| `:8000` connection refused | Start `mcp_sse_server.py` |
| ChatGPT "connection failed" | Ensure ngrok is running; URL may have changed (restart ngrok) |
| `store_memory` fails | Check `docs/MCP_FAILURE_LOG.md` |
| Tool parity | `python scripts/check_mcp_tool_parity.py` → expect 103/103 |

---

## 5. Related

- `docs/CODEX_IDE_MCP_ONBOARDING_V1.md` — Codex setup
- `docs/communications_mcp_down/README.md` — When MCP is down
- `docs/MCP_FAILURE_LOG.md` — Failure log and diagnosis
