# For Braden — When You Return

**Last updated:** 2026-03-05  
**Updated by:** Composer (Auditor)  
**Status:** GPT 5.2 connected via MCP. Project intact.

---

## TL;DR

The project is NOT dead. **GPT 5.2 is now connected to AIM-OS via native ChatGPT MCP** (verified 2026-03-05). MCP has 103 tools. JOC shell works. BAS passes. What broke before was agent identity and coordination — not the code itself.

---

## What Happened (March 4)

1. Codex agents (in Codex IDE) kept forgetting their identity — calling themselves the wrong names
2. They overwrote each other's files without coordination
3. MCP crashed from concurrent uncoordinated startups (race condition on message store)
4. You stepped away. Handed project to Opus (now Aether/COO) and Composer (Auditor)

## What We Fixed

1. **JOC Build** — 3 TS errors fixed (surface-engine-webgpu, MCPDiagnosticsPage). Build passes. 2026-03-04.
2. **Agent Genome System** — `.agent/genomes/` — 5 identity docs that agents load at session start
3. **Military Comms Doctrine** — `.agent/COMMS_DOCTRINE.md` — callsigns, message formats, chain of command
4. **Filesystem-First Comms** — `.agent/comms/` — inboxes, broadcasts, handoffs, status files (works without MCP)
5. **MCP Code Fixed** — atomic writes, identity canonicalization (already committed)
6. **Roundtable Bootstraps Hardened** — anti-identity-confusion measures in all bootstrap files

## Org Structure (Your Decision)

| Role | Who |
|------|-----|
| **CEO** | Braden |
| **COO (Aether)** | Opus (promoted) |
| **Auditor** | Composer |
| **Specialists** | Codex variants (fired from exec) |
| **UI Builder** | Gemini Pro |

## What's Working RIGHT NOW

| System | State | How to Start |
|--------|-------|-------------|
| **GPT 5.2 via MCP** | **Connected** | See "ChatGPT MCP" below |
| Git repo | All code intact | `git log --oneline -5` |
| JOC shell | Phase A complete | `cd packages/joc && npm run dev` |
| BAS | 6/8 gates pass | `cd packages/browser-automation-service && npm start` |
| MCP HTTP fallback | `:5001` | `python scripts/mcp_http_fallback_server.py` or `scripts/run_mcp_http_fallback.ps1` |
| MCP stdio (Cursor) | Via extension | Extension spawns lucid_mcp_server |
| Agent genomes | 5 agents | In `.agent/genomes/*.genome.md` |
| Agent comms | Templates + inboxes | In `.agent/comms/` |

## Your Roadmap (Still Valid)

File: `docs/OPUS1_JOC_GOALS_AND_ROADMAP.md`

- **Phase A** ✅ Shell (drawers, tabs, dashboard, icons, design system)
- **Phase B** ← NEXT (Session page, AI drivers, browser automation, credential vault)
- **Phase C** — Intelligence (multi-AI dispatch, synthesis, auto-context)
- **Phase D** — Expansion (GPU inference, cloud VMs, Drive integration)
- **Phase E** — Full browser OS

## To Start Working Again

```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS

# 1. Start MCP HTTP fallback (for Cursor/JOC/agents)
python scripts/mcp_http_fallback_server.py
# Or: .\scripts\run_mcp_http_fallback.ps1

# 2. Start JOC (in new terminal)
cd packages/joc
npm run dev

# 3. When starting any agent session, paste their identity:
#    See .agent/STARTUP.md for all agents
```

## ChatGPT MCP (GPT 5.2 Connection)

To connect ChatGPT (Developer Mode) to AIM-OS:

```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS

# Terminal 1: SSE MCP server (port 8000)
python scripts/mcp_sse_server.py

# Terminal 2: ngrok tunnel (exposes HTTPS for ChatGPT)
python scripts/ngrok_tunnel.py
# Paste the SSE URL into ChatGPT App creation screen
```

See `docs/MCP_RUNBOOK.md` for full MCP launch options.

## Key Files to Read

| File | What It Is |
|------|-----------|
| `docs/BRADEN_MORNING_DIRECTIVES_2026-03-05.md` | Today's standing orders |
| `docs/AUDIT_01_SYSTEM_MAP.md` | Full system map (10 planes) |
| `docs/CONTEXT_CANON.md` | Context system tiers (DEC-007) |
| `docs/MCP_RUNBOOK.md` | MCP launch options (HTTP, SSE, ChatGPT) |
| `.agent/STARTUP.md` | Agent identity protocol |
| `.agent/genomes/*.genome.md` | Agent identity files |
| `docs/OPUS1_JOC_GOALS_AND_ROADMAP.md` | Your roadmap |
| `docs/SALVAGE_PLAN_2026-03-04.md` | Composer's salvage plan |

---

*The project survives bad days. We're still here. — Aether + Composer*
