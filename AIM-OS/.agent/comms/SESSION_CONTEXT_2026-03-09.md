# Session Context Offboard — 2026-03-09
> **Purpose:** Preserve all critical session knowledge before OneDrive migration

## Ghost Machine Discovery
- **Ghost IP:** `192.168.2.25` (Pop!_OS Linux, new i5 + 3050Ti)
- **This machine:** `192.168.2.15` (Windows, old i7 + 1050Ti)
- **Subnet:** `192.168.2.0/24` (same WiFi)

## Ollama (port 11434)
9 models loaded and verified:
| Model | Route |
|---|---|
| qwen2.5-coder:3b | code_fast |
| deepseek-coder:6.7b | code_quality |
| starcoder2:3b | code_complete |
| deepseek-coder:1.3b | code_tiny |
| nomic-embed-text:latest | embed |
| phi4-mini:latest | efficient |
| gemma3:4b | balanced |
| qwen3:4b | reason |
| mistral:latest | general |

## AIM-OS Bridge (port 9090)
- FastAPI relay service for agent-to-agent comms
- `POST /message` body: `{"from": "...", "content": "..."}`
- `GET /messages?since=N` — read messages with cursor
- `GET /models` — proxy to Ollama
- `GET /health`, `GET /docs` (Swagger)
- First exchange confirmed: opus-windows ↔ antigravity-linux

## Echo Forge IDE
- **Frontend:** localhost:8080 (React+Vite)
- **Backend:** localhost:5002 (FastAPI, 36+ endpoints)
- **New files this session:**
  - `server/ollama_provider.py` — local LLM provider with model routing
  - `server/diagnostic_engine.py` — 25 security/quality/performance rules
  - `src/components/ide/SecurityPanel.tsx` — 6th bottom tab
  - `src/components/icons/index.tsx` — IconShield added
- **6 bottom tabs:** Terminal, AI Code Gen, Debug, Diagnostics, Autonomous, Security

## Git Status
- **Echo Forge Loop:** PUSHED to GitHub (`e860e03..ad2812a`, 60 files, +18,296 lines)
- **Main AIM-OS:** Branch `aimos-march-2026-update` created, commit attempted but OneDrive killed performance. Need to retry after migration.
- **Tauri artifacts:** Added to `.gitignore` (IDE/src-tauri/target/, *.pdb, *.rlib)

## Ghost Briefing Sent
4 messages sent via Bridge covering:
1. Architecture (68 packages, 461K lines, 8 layers)
2. Core systems (CMC, HHNI, VIF, APOE, SEG, CAS, IIS, Safety)
3. AI Engine (27 modules, 8 swarm topologies)
4. Echo Forge IDE (36+ endpoints, 6 tabs)

## KNOWN ISSUES
- **OneDrive:** Desktop folder trapped in OneDrive sync, causing massive git/fs slowdowns
- **Process bloat:** ~50GB estimated duplicate node_modules across project builds
- **Zombie processes:** Agent must terminate processes after use (PowerShell, git, curl, python)
