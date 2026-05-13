# AUDIT 01 — System Map

**Owner:** Composer  
**Date:** 2026-03-05  
**Method:** Evidence-first, 4-pass anti-satisficing protocol  
**Sources:** PROJECT_TRUTH/00_evidence_ledger.md, 01_canonical_system_index.md, FINDINGS_MASTER_LIST.md, repo search, runtime verification

---

## Executive Summary (10 Bullets)

1. **MCP is the spine** — `lucid_mcp_server.py` (103 tools) + HTTP fallback (`:5001`) + **new SSE server (`:8000`)** for ChatGPT native MCP. GPT 5.2 connected via SSE+ngrok (verified 2026-03-05).

2. **JOC is canonical UI** — `packages/joc/` is the command surface. Build passes. Dispatch/session seam fixed (#10/#11). `packages/ide_chat_app` is a separate app track.

3. **Context systems are fragmented** — No single canon. Live seam: `IDE/src-tauri/context_mapper`. Shadow: `context_capsule_wire_and_mapper_v1/`. Support: `context_bootloader`, `timeline_context_system`. DEC-007 consolidates; dedupe still needed.

4. **Memory stack is operational** — CMC + HHNI + `mcp_memory/` + `mcp_ai_messages.json`. `get_memory_stats` returns operational. HHNI index/retriever sometimes unavailable at runtime.

5. **Coordination is layered** — MCP tools (when up) + `.agent/comms` + roundtable threads. Three intentional channels; overlap causes routing noise under incident pressure.

6. **BAS is built** — `packages/browser-automation-service/` on `:5002`. Health, build, tests pass. **BAS automation to ChatGPT has never worked** (Finding #19). **Native ChatGPT MCP** (SSE+ngrok) is the working path.

7. **Tool registry is authoritative** — `lucid_mcp_server.py` + `scripts/check_mcp_tool_parity.py`. 103/103 parity. `packages/mcp_server/server.py` is alternate/legacy (FastAPI, `:8000` conflict with SSE).

8. **Launch canon** — `mcp_control.ps1`, `run_mcp_http_fallback.ps1`, `START_BAS_DETERMINISTIC.ps1`. Many legacy launchers remain; deprecation tags missing.

9. **Governance is active** — `docs/roundtable/IDENTITY_CANON.md`, `DECISION_LOG`, `WRITE_POLICY`. Older role maps (`ROLE_CONTINUITY_CANON`) conflict; need deprecation.

10. **Genome system is operational** — `.agent/genomes/*` + `GENOME_PROTOCOL.md`. Base+overlay architecture approved. V3 spec supersedes V2. `packages/agent_genome` runtime package still missing.

---

## Full System Map

### 1. MCP Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| Primary MCP server | built | `lucid_mcp_server.py` | — | 103 tools; stdio JSON-RPC |
| HTTP fallback bridge | built | `scripts/mcp_http_fallback_server.py`, `:5001` | — | `/health`, `/mcp/execute`, `/mcp/list` |
| **SSE MCP (ChatGPT)** | **built** | `scripts/mcp_sse_server.py`, `:8000` | — | FastMCP; delegates to lucid; ngrok exposes HTTPS |
| ngrok tunnel | built | `scripts/ngrok_tunnel.py` | — | Exposes :8000 for ChatGPT App |
| Legacy FastAPI MCP | part-built | `packages/mcp_server/server.py`, `:8000` | — | **Port conflict with SSE**; alternate architecture |
| Context-capsule copy | duplicate | `context_capsule_wire_and_mapper_v1/daemon/lucid_mcp_server.py` | — | Reject as canon |
| RAG daemon MCP | specialized | `daemon_rag_system/daemon_rag_mcp_server.py` | — | RAG-focused; not primary |

**Truth lives:** `lucid_mcp_server.py` (tool surface), `scripts/mcp_http_fallback_server.py` (HTTP), `scripts/mcp_sse_server.py` (ChatGPT).  
**Canonical:** lucid + HTTP fallback + SSE.  
**Missing for operational:** Resolve `packages/mcp_server` port/role; add deprecation if obsolete.

---

### 2. JOC Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| JOC app | part-built | `packages/joc/` | — | React/Vite; drawer/tab shell |
| SessionPage | part-built | `packages/joc/src/pages/SessionPage.tsx` | — | Launches browsers; sessionStore |
| DispatchPage | part-built | `packages/joc/src/pages/DispatchPage.tsx` | — | Fixed #10/#11; uses sessionStore browserId |
| basClient | built | `packages/joc/src/services/basClient.ts` | — | JOC→BAS integration |
| ide_chat_app | separate | `packages/ide_chat_app/` | — | Different app; not JOC canon |
| DAC prototype | historical | `ide_orchestration/prototypes/dac/` | — | Prototype; not runtime |

**Truth lives:** `packages/joc/`, `docs/CANON_JOC_UI_ARCHITECTURE.md`.  
**Canonical:** `packages/joc/`.  
**Missing for operational:** Residual jocStore vs sessionStore drift (#18); Perplexity in jocStore but not in BAS (#13).

---

### 3. Context Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| Live Rust mapper | part-built | `IDE/src-tauri/src/context_mapper/*` | — | Lane A live seam |
| Shadow sync | part-built | `context_capsule_wire_and_mapper_v1/shadow_sync/*` | — | Lane B prototype |
| Context bootloader | part-built | `packages/context_bootloader/*` | — | Smart loader; MCP context tools |
| Timeline context | part-built | `packages/timeline_context_system/*` | — | Duplicate variants; needs dedupe |
| JOC ContextCapsule | stub | `packages/joc/src/pages/DispatchPage.tsx` (interface) | — | Adapter for ContextAttachmentV0 pending |
| phase2b packet | evidence | `docs/phase2b_context_packet/*` | — | Snapshot; not runtime |

**Truth lives:** Multiple. DEC-007 + `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md` consolidate.  
**Canonical:** **UNCERTAIN** — no single canon. Lane-specific: IDE mapper (live), context_capsule (shadow).  
**Missing for operational:** Explicit promotion contract; dedupe timeline_context_system.

---

### 4. Memory Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| CMC | built | `packages/cmc_service/*` | — | Bitemporal; memory_store |
| HHNI | part-built | `packages/hhni/*` | — | Retrieval; index/retriever sometimes unavailable |
| mcp_memory | built | `mcp_memory/` | — | Runtime data surface |
| mcp_ai_messages | built | `mcp_ai_messages.json` (root) | `data/mcp/mcp_ai_messages.json` | Root canonical; data/mcp mirror unused |
| codex_ai_messages | built | `codex_workspace/persistence/collaboration/codex_ai_messages.json` | — | Codex workspace mirror |

**Truth lives:** `packages/cmc_service/`, `mcp_memory/`, `mcp_ai_messages.json`.  
**Canonical:** CMC + mcp_memory + message stores.  
**Missing for operational:** HHNI wiring; resolve data/mcp vs root message store.

---

### 5. Orchestration / Agent Coordination Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| MCP collaboration tools | built | `lucid_mcp_server.py` (send_ai_message, get_ai_messages, etc.) | — | When MCP up |
| .agent/comms | built | `.agent/comms/*` | — | Inbox, broadcast, handoff, status |
| Roundtable | built | `docs/communications_mcp_down/threads/*` | — | MCP-down mode |
| post_roundtable_message | built | `scripts/offline_comms/post_roundtable_message.py` | — | File-based posting |
| APOE | part-built | `packages/apoe/*` | — | Workflow engine |
| Router | part-built | `packages/router/*` | — | Routing |
| Specialist system | part-built | `packages/specialist_system/*` | — | Specialist runtime |

**Truth lives:** `.agent/comms/COMMS_CANONICAL.md`, `docs/roundtable/START_HERE.md`.  
**Canonical:** Layered — MCP first, then .agent/comms + roundtable.  
**Missing for operational:** Priority order under incident pressure; Organizer agent (Directive 2).

---

### 6. Browser / Chat Integration Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| BAS | built | `packages/browser-automation-service/` | — | `:5002`; browser lifecycle |
| mcpBridge (BAS) | built | `packages/browser-automation-service/src/api/mcpBridge.ts` | — | BAS→MCP bridge |
| **ChatGPT via BAS** | **never worked** | — | — | Finding #19; automation detected; abandon or redesign |
| **ChatGPT native MCP** | **built** | `scripts/mcp_sse_server.py` + ngrok | — | **Working path** — GPT 5.2 connected 2026-03-05 |
| Provider selectors | built | `packages/shared/providerSelectors.ts` | — | chatgpt, gemini, claude (no perplexity in BAS) |

**Truth lives:** `packages/browser-automation-service/`, `scripts/mcp_sse_server.py`, `scripts/ngrok_tunnel.py`.  
**Canonical:** BAS for JOC-controlled browsers; **SSE+ngrok for ChatGPT**.  
**Missing for operational:** Gemini/Claude native MCP if desired; BAS auth gates (PENDING_AUTH when not logged in).

---

### 7. Tool Registry Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| tools/list | built | `lucid_mcp_server.py` | — | 103 tools |
| Parity check | built | `scripts/check_mcp_tool_parity.py` | — | 103 listed = 103 callable |
| Transport smoke | built | `scripts/mcp_transport_smoke.py` | — | Smoke test |
| Cursor commands | built | `packages/lucid_mcp_server/tools/cursor_commands.py` | — | Sub-registry |
| packages/mcp_server | alternate | `packages/mcp_server/server.py` | — | `/mcp/tools/list`; different API |

**Truth lives:** `lucid_mcp_server.py`, `scripts/check_mcp_tool_parity.py`.  
**Canonical:** Monolith tools/list.  
**Missing for operational:** Hierarchical tool grouping (Directive 6); mode loadouts (Directive 8).

---

### 8. Launch / Runtime Bridge Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| MCP control | built | `scripts/mcp_control.ps1` | — | status/start/stop/test |
| MCP fallback start | built | `scripts/run_mcp_http_fallback.ps1` | — | HTTP bridge launcher |
| BAS launcher | built | `scripts/launchers/START_BAS_DETERMINISTIC.ps1` | — | Deterministic BAS start |
| daemon_bridge | part-built | `IDE/src-tauri/src/daemon_bridge.rs` | — | IDE stdio bridge |
| LAUNCH_HYBRID | alternate | `scripts/launchers/LAUNCH_HYBRID_SOLUTION.ps1` | — | ide_chat_app stack |

**Truth lives:** `scripts/mcp_control.ps1`, `scripts/run_mcp_http_fallback.ps1`, `scripts/launchers/START_BAS_DETERMINISTIC.ps1`.  
**Canonical:** MCP + BAS launchers.  
**Missing for operational:** Deprecation tags on legacy launchers; SSE server launcher doc.

---

### 9. Agent Protocol / Genome Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| Genomes | built | `.agent/genomes/*.genome.md` | — | 5 agents; identity at session start |
| GENOME_PROTOCOL | built | `.agent/genomes/GENOME_PROTOCOL.md` | — | Protocol |
| Base+overlay | approved | `docs/GENOME_ARCHITECTURE_BASE_PLUS_OVERLAY.md` | — | Braden approved 2026-03-05 |
| Injection by platform | built | `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md` | — | Per-IDE mapping |
| V3 spec | doc | `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md` | V2 superseded | Design reference |
| specialist_system | part-built | `packages/specialist_system/*` | — | Runtime |
| agent_genome package | missing | — | — | No dedicated runtime package |

**Truth lives:** `.agent/genomes/`, `docs/GENOME_ARCHITECTURE_BASE_PLUS_OVERLAY.md`.  
**Canonical:** .agent/genomes + comms + specialist_system.  
**Missing for operational:** `packages/agent_genome` implementation.

---

### 10. Governance Plane

| Component | Status | Canonical Path | Alternates | Invariant |
|-----------|--------|----------------|------------|-----------|
| Identity canon | built | `docs/roundtable/IDENTITY_CANON.md` | — | Mandatory; lanes |
| Decision log | built | `docs/roundtable/decisions/DECISION_LOG.md` | — | DEC-001..DEC-007+ |
| Write policy | built | `docs/communications_mcp_down/WRITE_POLICY.md` | — | Thread integrity |
| START_HERE | built | `docs/roundtable/START_HERE.md` | — | Entry point |
| ROLE_CONTINUITY_CANON | conflicting | `docs/agents/ROLE_CONTINUITY_CANON.md` | — | Older; conflicts with IDENTITY_CANON |
| AIM_OS_PRIME_CANON_INDEX | built | `docs/AIM_OS_PRIME_CANON_INDEX_V1.md` | — | Doctrine read order |

**Truth lives:** `docs/roundtable/IDENTITY_CANON.md`, `DECISION_LOG`, `WRITE_POLICY`.  
**Canonical:** Roundtable governance.  
**Missing for operational:** Deprecation headers on ROLE_CONTINUITY_CANON and ROLE_CONTINUITY_STATE.

---

## Invariants (Cross-System)

1. **CMC Principle** — Never delete; only supersede. Bitemporal versioning.
2. **Identity** — One identity per agent. [CALLSIGN] on every response.
3. **Coordination** — Never work alone. MCP + .agent/comms + roundtable.
4. **Evidence-first** — No rebuilding without evidence. Anti-satisficing.
5. **Genomes > LLMs** — Well-defined genome matters more than raw model.
6. **Comms always** — send_ai_message, get_ai_messages, store_memory, retrieve_memory are radio.
7. **Lock protocol** — Runtime actions use runtime_action_lock; LOCK:HELD_BY in messages.
8. **No overwrite without read** — Check status before modifying shared files.

---

## Duplicate / Competing Versions (Summary)

| System | Competing | Canonical | Rejected |
|--------|-----------|-----------|----------|
| MCP | packages/mcp_server, context_capsule copy, daemon_rag | lucid + HTTP + SSE | archive MCP scripts, snapshots |
| JOC | ide_chat_app, DAC prototype | packages/joc | DAC as runtime |
| Context | 4+ families | UNCERTAIN | *_TAGGED duplicates |
| Memory | data/mcp/mcp_ai_messages | root mcp_ai_messages | cursor-addon memoryManager |
| Governance | ROLE_CONTINUITY_CANON | IDENTITY_CANON | older role maps |
| Agent spec | V2 | V3 | V2 superseded |

---

## What's Missing for "Operational"

1. **Context consolidation** — Single canon; dedupe timeline_context_system.
2. **HHNI wiring** — Index/retriever available at runtime.
3. **Organizer agent** — Document organization (Directive 2).
4. **Tool hierarchy** — Grouped presentation (Directive 6).
5. **Mode loadouts** — Curated tool subsets per mission (Directive 8).
6. **Deprecation tags** — Legacy launchers, ROLE_CONTINUITY docs.
7. **packages/mcp_server** — Adjudicate: retire or document as alternate.
8. **packages/agent_genome** — Dedicated runtime package.

---

## Recommended Next 3 Tasks

1. ~~**Document SSE + ngrok launch path**~~ — **DONE 2026-03-05.** Added to BRADEN_RETURN_README, created `docs/MCP_RUNBOOK.md`.

2. ~~**Context system consolidation**~~ — **DONE 2026-03-05.** DEC-007 already executed. Created `docs/CONTEXT_CANON.md` (single entry point). Added `packages/timeline_context_system/DEPRECATION.md` (Tier D, TAGGED files non-canonical).

3. ~~**Governance cleanup**~~ — **DONE 2026-03-05.** Deprecation headers added to `docs/agents/ROLE_CONTINUITY_CANON.md` and `docs/ROLE_CONTINUITY_STATE.md`.

---

*Audit complete. Evidence-first. No rebuild. — Composer*
