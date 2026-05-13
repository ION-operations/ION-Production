# Daemon, Stdio, MCP Tools & Context Bus — AIM-OS Findings

**Purpose:** Document all AIM-OS information related to daemons, stdio, MCP tools, and patterns similar to the "Localized LSP for LLMs" / persistent stdio daemon (Context Bus / Orchestration Bus) discussion.  
**Scope:** AIM-OS project folder only.  
**Date:** 2026-02-28  

---

## 1. Summary of the Discussion You Referenced

The discussion describes:

- **Idea:** A **Localized Language Server Protocol (LSP) for LLMs** — offloading "hunting and gathering" of codebase context to a **background CLI agent** so the "Cerebral Cortex" (ChatGPT/Gemini Web UIs) stays focused on reasoning and the "Brain Stem" (e.g. Gemini CLI) does routing, parsing, and context shaping. This avoids **context window exhaustion** by giving the Web Agent only exact, formatted answers from a **Context Bus**.
- **Rejection of:** (1) Ephemeral `tokio::process::Command` spawns per request (cold start, amnesiac CLI), (2) Local TCP socket server (firewall, port collisions).
- **Proposed solution:** **Persistent Stdio Daemon** — same pattern as VS Code ↔ rust-analyzer and official MCP: spawn the CLI **once** at Tauri boot, hold **stdin/stdout** open, full-duplex **JSON-RPC over newline-delimited lines** (NDJSON). The Rust backend has an `OrchestrationBus` that keeps the child process alive and pipes requests in / reads envelope responses out.
- **Benefits:** Semantic cache (CLI holds AST in RAM, ~3s → &lt;20ms), native MCP server, speculative pre-fetching while the Web UI streams.
- **Three tiers:** (1) Web UIs = Cerebral Cortex, (2) CLI Daemon = Brain Stem / Context Bus, (3) Rust/Tauri Kernel = Motor Cortex (actuation).

**Critical question from the discussion:** *How do we pipe the CLI into the Tauri backend?* Answer given: persistent stdio daemon, not ephemeral spawns, not TCP.

---

## 2. What Exists in AIM-OS (Mapped)

### 2.1 MCP Over Stdio — Production

| Component | Location | Role |
|-----------|----------|------|
| **MCP Server (stdio loop)** | `lucid_mcp_server.py` | Single Python process. **Stdio:** reads line-by-line from `sys.stdin`, parses JSON, dispatches to `handle_request`, writes JSON response to `sys.stdout` and flushes. All logging goes to **stderr** so stdout stays JSON-only for MCP. |
| **Server loop (exact)** | `lucid_mcp_server.py` ~384–413 | `run()`: `while True` → `line = sys.stdin.readline()` → `request = json.loads(line.strip())` → `response = self.handle_request(request)` → `sys.stdout.write(json.dumps(response) + '\n')`; `sys.stdout.flush()`. |
| **MCP Client (spawns server)** | `cursor-addon/src/mcp/mcpClient.ts` | **Spawn:** `spawn('python', ['-u', mcpServerPath], { cwd: workspaceRoot, stdio: ['pipe', 'pipe', 'pipe'] })`. Holds process and pipes; writes JSON-RPC messages to `process.stdin.write(JSON.stringify(message) + '\n')`; reads from `process.stdout.on('data', ...)`, splits by newline, parses JSON, routes to `handleMessage` / pending requests. |
| **Protocol** | Same everywhere | **JSON-RPC 2.0**; newline-delimited JSON (one request/response per line). Methods: `initialize`, `tools/list`, `tools/call`; notifications: `notifications/cancelled`, `notifications/initialized`. |

**References:**

- `knowledge_architecture/SUPER_INDEX.md` — "MCP Client (Cursor Addon): Connects Extension to Python MCP server (lucid_mcp_server.py) via **JSON-RPC 2.0 over stdio**".
- `docs/AIMOS_MAJOR_SYSTEMS.md` — MCP Integration: "**JSON-RPC 2.0** over stdio. Protocol-compliant."
- `ide_orchestration/prototypes/dac/docs/AIMOS_DESIGN_SYSTEM_PROTOCOL.md` — "App → MCP Client → **lucid_mcp_server.py (stdio)** → Core AIM-OS Systems".
- `ide_orchestration/prototypes/dac/docs/PHASE4_VERIFICATION_RESULTS.md` — "MCP Client spawns Python process and communicates via **JSON-RPC 2.0**"; "Integration: Extension Webview → Command Server HTTP API → **MCP Client → MCP Server (Python stdio)** → AIM-OS Backend".
- `ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md` — "IDE System → MCP Client → **lucid_mcp_server.py (stdio)** → Core Systems".
- `knowledge_architecture/SAM/sources/MASTER_MCP_INTEGRATION_SYSTEM_MAP.md` — "Server Lifecycle: Start → Load tools → Register → **Serve JSON-RPC 2.0 over stdio** → Monitor → Shutdown".

So in AIM-OS, **the canonical MCP transport is already persistent stdio**: the Cursor addon (or Command Server) spawns `lucid_mcp_server.py` once and keeps the process alive; all tool calls go over stdin/stdout. That is the same *transport* idea as the discussion’s persistent daemon (one process, long-lived pipes).

---

### 2.2 Daemon/RAG System

| Component | Location | Role |
|-----------|----------|------|
| **Docs (L0–L4, T0–T6)** | `knowledge_architecture/systems/daemon_rag_system/` | Executive, overview, architecture, detailed, complete, quick ref, source ref. |
| **Main implementation** | `daemon_rag_system/daemon_rag_system.py` | Core daemon logic: tool registry, context analysis, tool selection, RAG, server manager, learning, etc. |
| **HTTP API** | `daemon_rag_system/http_api_server.py` | Uvicorn app on port 5000 for Lexicon/IDE (e.g. health, telemetry). **Not stdio** — HTTP. |
| **Daemon MCP server (stdio)** | `daemon_rag_system/daemon_rag_mcp_server.py` | **MCP over stdio:** `main()` reads `sys.stdin` line-by-line, JSON parse, `handler.handle_request(request)`, writes JSON to `sys.stdout` and **flush**. Can be run as a standalone MCP server process (e.g. for tool-selection / RAG-aware MCP). |
| **SUPER_INDEX** | `knowledge_architecture/SUPER_INDEX.md` | Daemon/RAG: "Intelligent MCP tool management … context-aware selection … **http_api_server.py** (HTTP API for Lexicon)". |
| **Daemon spec** | `cursor-addon/docs/DAEMON_SYSTEM_SPECIFICATION.md` | Solves Cursor 40-tool limit; context analysis → tool selection → server management → execution → learning. Tool Registry, Context Analysis Engine, Tool Selection Engine, RAG, Server Manager, Performance Monitor, Learning System, Resource Manager. |
| **System Atlas** | `apps/system-atlas/public/data/graph.json` | Nodes for Daemon/RAG: toolRegistry, contextAnalysisEngine, toolSelectionEngine, ragSystem, serverManager, performanceMonitor, learningSystem, resourceManager, httpApiServer. |

So AIM-OS has **two** daemon-related surfaces:

1. **lucid_mcp_server.py** — The main MCP tool server; **stdio**; used by Cursor addon and Command Server.
2. **daemon_rag_system** — Context-aware tool selection and RAG; exposes both an **HTTP API** (http_api_server.py) and an **MCP-over-stdio** entry point (daemon_rag_mcp_server.py).

Neither is a "Gemini CLI" or "context envelope" daemon; they are MCP tool servers and RAG/tool-selection daemons.

---

### 2.3 Lucid Orchestrator Daemon (HTTP, Not Stdio)

| Component | Location | Role |
|-----------|----------|------|
| **HTTP daemon** | `packages/lucid_orchestrator/daemon/http_daemon.py` | Flask app on port 5000: health, nodes, spec, blueprint, timeline, propose-change, focus, telemetry (progress, confidence-routing). Serves IDE/Vite app. |
| **README** | `packages/lucid_orchestrator/daemon/README.md` | "Flask-based daemon … exposes a small JSON API on port 5000". Telemetry snapshots, IDE integration via `VITE_LUCID_DAEMON_URL`. |
| **Lucid daemon (logic)** | `packages/lucid_orchestrator/daemon/lucid_daemon.py` | Dataclasses and logic for SpecBlock, Blueprint, Timeline, etc.; used by HTTP daemon. WebSockets mentioned; primary interface is HTTP. |

This daemon is **HTTP-only** for the IDE prototype, not an MCP or stdio process.

---

### 2.4 Cursor Addon — Command Server and MCP Client

| Component | Location | Role |
|-----------|----------|------|
| **MCPClient** | `cursor-addon/src/mcp/mcpClient.ts` | Spawns `python -u lucid_mcp_server.py` with **stdio: ['pipe', 'pipe', 'pipe']**. Sends JSON-RPC on stdin; reads stdout by line; `initialize()`, `sendRequest()`, `listTools()`, `callTool()`, `disconnect()`. |
| **Command Server** | `cursor-addon/src/commandServer.ts` | HTTP server (e.g. port 5001); `/mcp/execute`, `/mcp/list`, `/mcp/restart`. Uses **MCPClient** internally; initializes once, holds client. So: HTTP → Command Server → **MCP Client (single long-lived process)** → **stdio** → lucid_mcp_server.py. |
| **Extension / Webview** | `extension.ts`, `webviewProvider.ts`, `lucidDashboardProvider.ts` | Create MCPClient, call `initialize()` then `callTool` / `listTools`. Same pattern: one spawned process, stdio. |

So the **persistent process + stdio** pattern is already how Cursor talks to the MCP server; the only thing not present is doing this from **Tauri** (Rust) and with a **CLI that produces context envelopes** (e.g. AST/XML) instead of MCP tools.

---

### 2.5 Archive — Stdio MCP Tests

| File | Location | Role |
|------|----------|------|
| **test_mcp_stdio.py** | `archive/test_mcp_stdio.py` | Starts `run_mcp_stdio.py` with `subprocess.Popen(..., stdin=PIPE, stdout=PIPE, stderr=PIPE)`; sends JSON-RPC `tools/list` and `tools/call` on stdin; reads response from stdout by line. |
| **run_mcp_stdio.py** | `archive/run_mcp_stdio.py` | (Referenced by test; may wrap lucid_mcp_server or similar.) |
| **cursor_mcp_config_working_stdio.json** | `archive/cursor_mcp_config_working_stdio.json` | Cursor MCP config for stdio. |
| **test_stdio_*.py, run_mcp_stdio_*.py** | `archive/` | Other stdio/MCP test and run scripts. |

These show **stdio MCP** was validated via subprocess + stdin/stdout pipes.

---

### 2.6 "Context Bus" and "Orchestration Bus" in AIM-OS

- **HHNI as context bus:**  
  `north_star_project/THE_NORTH_STAR_DOCUMENT.md` and `north_star_project/chapters/06_hhni/chapter.md`: "**HHNI becomes the shared context bus**, eliminating ad-hoc re-orientation for every agent." So "context bus" in AIM-OS docs means **HHNI as the shared retrieval/context layer**, not a persistent CLI process.

- **Emotional AI / context bus:**  
  `ide_orchestration/prototypes/dac/docs/agents/codex/CODEX_CHAT_IDE_DEEP_BRIEF.md`: "Node F: Emotional AI overlay (runs in parallel, **subscribes to context bus**)." Conceptual only; no Tauri/CLI implementation.

- **Orchestration bus (your discussion):**  
  The **OrchestrationBus** in the discussion is a **Rust struct** in a hypothetical `context_bus.rs` that holds a **persistent child process** (e.g. Gemini CLI) and its stdin handle. **No such file or Tauri-side "orchestration bus" exists in the AIM-OS repo.** The SAIOS/IDE app (Tauri) in `Application_Dev/IDE` has no context_bus or CLI daemon yet.

---

### 2.7 Design / Integration Docs (MCP + Stdio)

| Doc | Key point |
|-----|------------|
| **AIMOS_DESIGN_SYSTEM_PROTOCOL.md** | "App → MCP Client → **lucid_mcp_server.py (stdio)** → Core AIM-OS Systems"; recommends MCP for app integration. |
| **COMPLETE_SYSTEM_MAP_AND_INTEGRATION_STATUS.md** | "Lucid MCP server (**stdio**)". |
| **UNIFIED_TEXTBOOK.md** (code-reflex-orchestra) | Example: call MCP server via stdio — `subprocess.Popen(..., stdin=PIPE, stdout=PIPE)`, write `json.dumps(message) + "\n"` to `proc.stdin`, read `proc.stdout.readline()`. |

---

## 3. File Index — Daemon, Stdio, MCP (Concise)

### 3.1 MCP server and stdio loop

- **lucid_mcp_server.py** — Main MCP server; `run()` is the stdio loop (stdin → JSON → handle_request → stdout + flush); stderr for logs; ~10.6k LOC.

### 3.2 Daemon/RAG

- **daemon_rag_system/daemon_rag_system.py** — Core daemon implementation.
- **daemon_rag_system/daemon_rag_mcp_server.py** — MCP over stdio entry point; `main()` reads stdin, writes stdout.
- **daemon_rag_system/http_api_server.py** — HTTP API (e.g. port 5000).
- **knowledge_architecture/systems/daemon_rag_system/** — L0–L4, T0–T6 docs.
- **cursor-addon/docs/DAEMON_SYSTEM_SPECIFICATION.md** — Daemon architecture and tool limit solution.

### 3.3 Cursor addon (MCP client, Command Server)

- **cursor-addon/src/mcp/mcpClient.ts** — Spawns Python MCP server, stdio pipes, JSON-RPC send/receive.
- **cursor-addon/src/commandServer.ts** — HTTP server; uses MCPClient; `/mcp/execute`, `/mcp/list`, `/mcp/restart`.

### 3.4 Lucid orchestrator daemon (HTTP)

- **packages/lucid_orchestrator/daemon/http_daemon.py** — Flask daemon, port 5000.
- **packages/lucid_orchestrator/daemon/README.md** — API surface, telemetry, IDE integration.
- **packages/lucid_orchestrator/daemon/lucid_daemon.py** — Daemon logic (SpecBlock, Blueprint, etc.).

### 3.5 System maps and indexes

- **knowledge_architecture/SAM/sources/MASTER_MCP_INTEGRATION_SYSTEM_MAP.md** — MCP + Daemon/RAG; "Serve JSON-RPC 2.0 over stdio".
- **knowledge_architecture/SUPER_INDEX.md** — Entries for Daemon/RAG, MCP Client (stdio).
- **docs/AIMOS_MAJOR_SYSTEMS.md** — Sections 11 (MCP Integration), 12 (Daemon/RAG).
- **apps/system-atlas/public/data/graph.json** — Daemon/RAG and MCP-related nodes; "JSON-RPC 2.0 client over stdio (stdin/stdout)".

### 3.6 Archive (stdio tests)

- **archive/test_mcp_stdio.py** — Stdio MCP test (spawn, stdin write, stdout read).
- **archive/run_mcp_stdio.py**, **archive/run_mcp_stdio_*.py**, **archive/test_stdio_*.py**, **archive/cursor_mcp_config_working_stdio.json** — Supporting scripts/config.

### 3.7 Other references

- **ide_orchestration/prototypes/dac/docs/PHASE4_VERIFICATION_RESULTS.md** — Verification of MCP Client + Python stdio.
- **ide_orchestration/prototypes/dac/docs/AIMOS_DESIGN_SYSTEM_PROTOCOL.md** — MCP (stdio) integration pattern.
- **knowledge_architecture/FLOATING_FILES_ORGANIZED/ARCHITECTURE_DOCS/DAEMON_RAG_MCP_SYSTEM.md** — Daemon/RAG + MCP.
- **knowledge_architecture/FLOATING_FILES_ORGANIZED/PLANS_AND_IMPLEMENTATION/DAEMON_RAG_IMPLEMENTATION_PROTOCOL.md** — Implementation protocol.

---

## 4. Relationship to the Discussion

| Discussion concept | In AIM-OS |
|--------------------|-----------|
| **Persistent stdio daemon** | ✅ **lucid_mcp_server.py** is a long-lived process talking JSON-RPC over stdio. Cursor addon spawns it once and keeps pipes open. |
| **JSON-RPC over stdio (NDJSON)** | ✅ Same: one JSON object per line on stdin/stdout; flush after each response. |
| **Avoid ephemeral spawns** | ✅ Cursor uses one MCP process per extension/session, not one per request. |
| **Avoid TCP for this channel** | ✅ MCP in AIM-OS uses stdio for the Cursor ↔ MCP server link; HTTP is used only for Command Server ↔ clients (Electron, etc.). |
| **"Context Bus" as CLI that returns context envelopes** | ❌ Not in AIM-OS. HHNI is described as "context bus" in a retrieval sense. No Tauri-side OrchestrationBus or CLI that returns AST/XML envelopes. |
| **Tauri backend holding stdin/stdout of a CLI** | ❌ Tauri app (SAIOS) lives in `Application_Dev/IDE`; AIM-OS has no Tauri code. No `context_bus.rs` or equivalent. |
| **Gemini CLI (or similar) in daemon mode** | ❌ No Gemini CLI daemon or "Librarian" process in AIM-OS. |
| **Speculative pre-fetch / pipeline stalling** | ❌ Not implemented; discussion only. |

So: **AIM-OS already uses the same *transport* pattern (persistent process + stdio + JSON-RPC)** for MCP. What it does *not* have is the *role* of that process as a "Context Bus" that turns codebase requests into AST/XML envelopes for a Web UI, or any of that logic in a Tauri backend.

---

## 5. Where to Strike First (If Implementing the Discussion in SAIOS/Tauri)

As in the discussion:

1. **Rust daemon controller (e.g. `context_bus.rs`)** — In the Tauri app (e.g. SAIOS in `Application_Dev/IDE`): spawn the CLI **once** at startup, hold `ChildStdin`/`ChildStdout`, run a Tokio task that reads lines from stdout and routes envelope payloads (e.g. to the webview or state machine). Expose a method to send JSON-RPC requests to the CLI.
2. **CLI daemon mode** — In the Gemini (or other) CLI codebase: add a `--daemon-mode` (or similar) that enters a loop reading stdin for JSON-RPC, building context envelopes (e.g. AST/XML), writing JSON (or NDJSON) to stdout. That CLI then *is* the persistent "Librarian" process.
3. **System prompts / envelope format** — Define the exact `<system_envelope>` (or equivalent) format and the Librarian’s system prompt so it returns deterministic, parseable context for the Web Agent.

AIM-OS can be used as reference for: (a) **stdio protocol** — see `lucid_mcp_server.run()` and `cursor-addon/src/mcp/mcpClient.ts`; (b) **keeping one process alive** — see MCPClient lifecycle; (c) **logging only to stderr** so stdout stays clean for JSON.

---

## 6. Deliverable Summary

- **What:** A single doc that (1) summarizes the "LSP for LLMs" / persistent stdio daemon discussion, (2) maps all AIM-OS daemon, stdio, and MCP implementations and docs, (3) distinguishes what exists (MCP over stdio, Daemon/RAG, HTTP daemons) from what does not (Tauri Context Bus, CLI envelope daemon, speculative pre-fetch), and (4) points to where to implement the discussion (Tauri + CLI).
- **Where:** `docs/DAEMON_STDIO_MCP_AND_CONTEXT_BUS_FINDINGS.md`
- **How to verify:** Open the file; use it as the index for "daemon," "stdio," "MCP," and "context bus" in AIM-OS; cross-check paths (lucid_mcp_server.py, mcpClient.ts, daemon_rag_system, etc.) and quotes against the repo.
