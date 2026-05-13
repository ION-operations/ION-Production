---
ion_id: docs/aether-os/master-orchestration
type: protocol
authority: A2_CANONICAL_EXTENSION
confidence: 0.92
epistemic_status: DERIVED
owner: opus
created: 2026-03-24T18:20:00-04:00
updated: 2026-03-24T18:20:00-04:00
supersedes:
  - brain/686bae59/implementation_plan
  - brain/686bae59/task
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: docs/aether-os/doc-architecture
    type: depends_on
  - target: docs/aether-os/state-of-the-union
    type: depends_on
tags: [orchestration, mission, living-document, anti-drift]
summary: |
  The single source-of-truth mission document for making ION/Aether operational.
  Living document — updated by the executing agent after every significant action.
  Covers 6 phases from current broken state to quaternion OS, with concrete
  verification gates, anti-drift checkpoints, and dynamic progress tracking.
---

# MASTER ORCHESTRATION — ION/Aether Consolidation
## The Living Mission Document

> **This document IS the mission.** It is read at session start, worked from during execution,
> and updated after every significant action. If this document drifts from reality,
> the mission has failed.
>
> **Anti-drift rule:** After every 5 tasks completed, re-read §0 and verify the current
> prompt's work aligns with the current phase objective. If it doesn't, stop and re-orient.

---

## §0. MISSION IDENTITY

**MISSION:** Take ION/Aether from fragmented, partially-working subsystems to a fully operational AI operating system, moving through 6 product phases from MVP AI builder to quaternion-kernel OS.

**MUST-NOT:**
1. Must not fabricate capability claims (Constitution Art. 1)
2. Must not widen scope without explicit Braden approval (Art. 18)
3. Must not start code work before completing the current phase's organize tasks

**CURRENT PHASE:** Phase 0 — ORGANIZE
**CURRENT PROMPT NUMBER:** ~15 (estimated from session history)
**LAST UPDATED:** 2026-03-24T18:20:00-04:00

---

## §0A. PLANNING DENSITY LAW

> **Governing law:** Constitution Art. 16 — Blueprint Depth Classes.
> Not all phases deserve the same planning granularity. Density follows proximity,
> criticality, and readiness — not uniformity.

### The Principle

Planning density fluctuates. Near-term work needs file paths, shell commands, and
dependency chains. Far-future work needs strategic anchors and gate conditions.
Some far-future elements get elevated density when they're architecturally critical
or pre-planned in advance.

```
                    PLANNING DENSITY MAP
                    ═══════════════════

  HIGH ██████████████████████████████████████████████████████
  DENSITY                                              
       ███ Phase 0  ███ Phase 1  ██ Phase 2  █ Phase A  
       ███ ORGANIZE ███ STABILIZE██ VS CODE  █ MVP WEB  
       ███ Class 3  ███ Class 3  ██ Class 2  █ Class 2  
       ███ (now)    ███ (next)   ██ (weeks)  █ (parallel)
       ███          ███          ██          █              
  LOW  ·                                                   
       · Phase 3   · Phase 4   · Phase 5                   
       · ION IDE   · Linux     · Quaternion                
       · Class 1   · Class 0   · Class 0                   
       · (months)  · (months+) · (years)                   

  ▲ DENSITY RISES when a phase approaches execution
  ▲ DENSITY RISES for architecturally critical decisions regardless of timeline
  ▼ DENSITY STAYS LOW for phases that depend on undetermined upstream choices
```

### Depth Class Definitions (from Constitution Art. 16)

| Class | Phase Mapping | What's Documented |
|-------|--------------|--------------------|
| **3** | Phase 0, Phase 1 | Every file path, every shell command, every dependency chain, root causes, approach options, rollback plans |
| **2** | Phase 2, Phase A | Task descriptions with verification, key architectural decisions pre-surfaced, effort ranges, dependency links |
| **1** | Phase 3 | Objective + task list + gate conditions. Implementation detail added when Phase 2 nears completion |
| **0** | Phase 4, Phase 5 | Objective + gate conditions only. Detail added when predecessor phase approaches gate |

### Dynamic Elevation Rules

1. **Approaching execution:** When a phase is ≤2 phases from current, elevate its depth class by 1
2. **Architectural decision required NOW:** If a far-future phase requires a decision that affects near-term work, elevate the SPECIFIC TASK to Class 2-3 regardless of phase depth
3. **Strategic pre-planning:** If Braden or research surfaces important detail about a future phase, record it at whatever depth it arrives — don't artificially compress
4. **Never backfill uniformly:** Don't expand all tasks in a phase just because one task got elevated. Keep the density differential.

---

## §1. GROUND TRUTH — Where We Actually Are

### 1.1 What Exists (OBSERVED — verified via file read or test output)

| System | Location | Lines | Runtime Truth | Evidence |
|--------|----------|------:|--------------|----------|
| ION Model (types, bonds, authority) | `victus/ion/model.py` | 940 | FUNCTIONAL | 20/22 prebuild tests |
| IonStore (filesystem CRUD) | `victus/ion/store.py` | 380 | FUNCTIONAL | Creates/reads .md ions |
| IonIndex (query engine) | `victus/ion/index.py` | 290 | FUNCTIONAL | Pattern + tag + type queries |
| IonGraph (bond traversal) | `victus/ion/graph.py` | 340 | FUNCTIONAL | 5/5 tests — topology, impact |
| Governed Write (10-stage) | `victus/ion/governed_write.py` | 420 | FUNCTIONAL | Authority + zone + duplicate rejection |
| Navigator (7-step cognitive loop) | `victus/ion/navigator.py` | 624 | FUNCTIONAL | health=0.80, mechanical completion |
| Context Compiler (three-tier) | `victus/ion/context_compiler.py` | 304 | FUNCTIONAL | Pinned/Working/LongTerm + budget |
| Threshold System | `victus/ion/threshold.py` | 280 | FUNCTIONAL | Confidence validation |
| K-Gate (confidence gating) | `victus/ion/kgate.py` | 190 | FUNCTIONAL | κ-threshold enforcement |
| LLM Adapter | `victus/ion/llm_adapter.py` | ~300 | FUNCTIONAL | Gemini+Ollama+Mock, 17/17 tests |
| Agent Types (IonType.AGENT) | `victus/ion/agent_types.py` | est. | FUNCTIONAL | Supervisor + hierarchy restored |
| Server (FastAPI) | `victus/aether/server.py` | est. | FUNCTIONAL | Wired to real AetherEngine |
| CLI | `victus/ion/cli/` | est. | FUNCTIONAL | ls, stats, inspect, bonds, graph |
| Constitutional Stack | `docs/Aether-OS/*.md` | 3,448 | ALIVE | 4 docs, 39 articles, 21 schemas |
| Agent Infrastructure | `.agent/` | est. | ALIVE | Bootloader, 11 genomes, protocols |
| CMC (Memory Store) | `packages/cmc_service/` | est. | ALIVE | SQLite, 190+ atoms, MCP tools |
| MCP Transport | `lucid_mcp_server.py` | 10,925 | ALIVE | 137+ tools, stdio transport |
| APOE (Orchestrator) | `packages/apoe/` | est. | ALIVE | Goal-to-plan compilation |
| Quaternion Kernel (Rust) | `packages/quaternion_kernel/` | 641 | DOCTRINAL_ONLY | 4 syscalls, no deployable substrate |

### 1.2 What's Broken (OBSERVED)

| Issue | Severity | Location | Root Cause (if known) | Blocking |
|-------|----------|----------|-----------------------|----------|
| Bootstrap hangs | 🔴 CRITICAL | `victus/ion/bootstrap.py` → `bridge.py` | Singleton import chain deadlock | Phase 1 |
| No live LLM e2e | 🔴 CRITICAL | `victus/ion/llm_adapter.py` → engine | Architecture exists, never run live | Phase 1 |
| `data/ions/` missing | 🟡 HIGH | `operation-victus/data/` | Never created on disk | Phase 1 |
| 20 legacy enum refs | 🟡 HIGH | Scattered across victus/ | FORGE C1 got most, ~20 leaked | Phase 1 |
| 0 pytest tests collected | 🟡 HIGH | `victus/ion/` | scaffold naming/config issue | Phase 1 |
| No VS Code integration | 🔴 CRITICAL | — | Nothing built | Phase 2 |
| MCP monolith (10K lines) | 🟠 MEDIUM | `lucid_mcp_server.py` | Single file, 137+ tools | Phase 2-3 |
| 68 packages unwired | 🟠 MEDIUM | `AIM-OS-GIT/packages/` | Exist but not connected to ION | Phase 2-3 |

### 1.3 The 4 Repositories

| Repo | Path | Decision | Rationale |
|------|------|----------|-----------|
| `operation-victus` | `/home/sev/operation-victus/` | **CANONICAL runtime** | 63 core modules after cut list |
| `AIM-OS-GIT` | `/home/sev/AIM-OS-GIT/` | **Infrastructure + docs** | .agent/, packages/, docs/ |
| `AIM-OS-FRESH` | `/home/sev/AIM-OS-FRESH/` | **READ-ONLY archive** | Echo-Forge ideas, knowledge corpus |
| `AIM-OS` | `/home/sev/AIM-OS/` | **Historical reference** | Pre-Git era, A7 authority |

### 1.4 Existing Audit Corpus (Don't Redo These)

| Document | Lines | What It Covers |
|----------|------:|----------------|
| [STATE_OF_THE_UNION](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/STATE_OF_THE_UNION.md) | 170 | Synthesis of all 8 audits + decision matrix |
| [DOC_ARCHITECTURE](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/DOC_ARCHITECTURE.md) | 320 | How docs are organized for AI (canon-aligned) |
| [SYSTEM_UNIVERSE_MAP](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/SYSTEM_UNIVERSE_MAP.md) | 690 | ALL 170+ systems mapped to ION |
| [ION_RUNTIME_AUDIT](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/ION_RUNTIME_AUDIT.md) | 150 | victus/ion/ file-by-file (63 keep, 36 cut) |
| [AETHER_ATLAS](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/AETHER_ATLAS.md) | 1327 | 32 canonical objects, runtime truth, 76+ packages |
| [01_COMPREHENSIVE_TECHNICAL_AUDIT](file:///home/sev/AIM-OS-GIT/audit/2026-02-19_aimos_restart_audit/01_COMPREHENSIVE_TECHNICAL_AUDIT.md) | 339 | Codex/GPT-5 engineering audit, 2.8/5 maturity |
| [DEEP_CONSOLIDATION_ANALYSIS](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/DEEP_CONSOLIDATION_ANALYSIS.md) | 350 | 5 duplicate system groups identified |

---

## §2. PHASE 0 — ORGANIZE
**Status: 🔵 IN PROGRESS**
**Goal: Perfect knowledge of what we have before touching code**
**Estimated prompts: 5-10**

### 2.1 Completed Tasks

- [x] **T0.01** Full file audit of `victus/ion/` — 105 files audited, 63 keep, 36 cut
  - Output: [ION_RUNTIME_AUDIT.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/ION_RUNTIME_AUDIT.md)
  - Completed: 2026-03-24

- [x] **T0.02** Cross-repo audit synthesis — Read 8+ existing audit docs, produced STATE_OF_THE_UNION
  - Output: [STATE_OF_THE_UNION.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/STATE_OF_THE_UNION.md)
  - Completed: 2026-03-24

- [x] **T0.03** Documentation architecture — aligned to Constitution + Atlas canon
  - Output: [DOC_ARCHITECTURE.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/DOC_ARCHITECTURE.md)
  - Completed: 2026-03-24 (v2 — rewritten after deep canon read)

- [x] **T0.04** Deep canon read — all 4 governing documents (3,448 lines total)
  - Constitution: 39 articles, 8 Parts, 583 lines
  - Kernel: 19 sections, 422 lines
  - Interface: 21 schemas, 1116 lines
  - Atlas: 10 Books, 32 objects, 1327 lines
  - Completed: 2026-03-24

### 2.2 Remaining Phase 0 Tasks

- [ ] **T0.05** Create GENESIS.md (L3, 100 words)
  - Source: DOC_ARCHITECTURE §4
  - Verification: File exists at `docs/Aether-OS/GENESIS.md`, contains ≤100 words
  - Effort: 1 prompt

- [ ] **T0.06** Create NORTH_STAR.md v2 (L3, updated 6-phase roadmap)
  - Source: DOC_ARCHITECTURE §5, original AIM_OS_NORTH_STAR.md
  - Verification: File exists, 6 phases described, current position marked
  - Effort: 1 prompt

- [ ] **T0.07** Create STATE_REGISTER.md (L4, single-file runtime truth)
  - Source: Atlas Book III + STATE_OF_THE_UNION + runtime probes
  - Verification: Every system has a runtime_truth state, probed where possible
  - Effort: 2-3 prompts (includes live probing of systems)

- [ ] **T0.08** Create 12 domain summaries (L7, ~500 words each)
  - Source: SYSTEM_UNIVERSE_MAP, cross-referenced with actual code
  - Verification: 12 files in `docs/Aether-OS/domains/`, each ≤600 words
  - Effort: 3-5 prompts (can be parallelized with swarm)

- [ ] **T0.09** Explicit cut list — every file/system getting deleted
  - Source: ION_RUNTIME_AUDIT (36 files), STATE_OF_THE_UNION §5 (cut decisions)
  - Verification: Cut list is concrete paths, not categories. Braden approved.
  - Effort: 1 prompt

- [ ] **T0.10** Explicit build list — every system that doesn't exist but must
  - Source: STATE_OF_THE_UNION §6, DOC_ARCHITECTURE §9
  - Verification: Build list has effort estimates, priority, and blocking dependencies
  - Effort: 1 prompt

- [ ] **T0.11** Clean IDE instructions
  - Action: Replace Antigravity user rules with single bootloader line
  - Verification: `cat /home/sev/.gemini/settings.json` shows only bootloader reference
  - Effort: 1 prompt (but needs Braden approval)

- [ ] **T0.12** Mark superseded docs
  - Action: Add `status: SUPERSEDED` headers to stale docs per DOC_ARCHITECTURE §11
  - Verification: Old docs have headers, no confusion about which is canonical
  - Effort: 1-2 prompts

### 2.3 Phase 0 Gate (ALL must be true to proceed)

```
□ GENESIS.md exists and is ≤100 words
□ NORTH_STAR.md v2 exists with 6 phases
□ STATE_REGISTER.md exists with runtime truth for all systems
□ 12 domain summaries exist
□ Cut list exists and is approved by Braden
□ Build list exists with priorities
□ IDE instructions cleaned (Braden approved)
□ This orchestration document is still accurate (anti-drift check)
```

---

## §3. PHASE 1 — STABILIZE
**Status: ⬜ NOT STARTED**
**Goal: Every test passes, bootstrap works, first live LLM call succeeds**
**Estimated prompts: 15-25**
**Depends on: Phase 0 gate**

### 3.1 Task Breakdown

- [ ] **T1.01** Fix bootstrap hang
  - Root cause: `bootstrap.py` imports `bridge.py` which triggers singleton initialization
  - Approach: Read `bootstrap.py` and `bridge.py`, identify the circular import, break it
  - Verification: `python -c "from victus.ion.bootstrap import bootstrap_network; bootstrap_network()"` completes in <5s
  - Files: `victus/ion/bootstrap.py`, `victus/ion/bridge.py`
  - Effort: 1-3 prompts
  - Blocker for: T1.02, T1.05

- [ ] **T1.02** Create `data/ions/` with initial 16 ions
  - Depends on: T1.01 (bootstrap must work)
  - Action: Either run bootstrap_network() or manually create seed ions
  - Verification: `ls /home/sev/operation-victus/data/.ion/` shows 16+ `.md` files
  - Effort: 1-2 prompts

- [ ] **T1.03** Fix remaining legacy enum refs
  - What: ~20 references to old enum values (A4_SYSTEM, A3_CORE, A1_LOCAL, etc.)
  - Approach: `grep -rn "A4_SYSTEM\|A3_CORE\|A1_LOCAL" victus/` → fix each
  - Verification: `grep -rn "A4_SYSTEM\|A3_CORE\|A1_LOCAL" victus/` returns 0 results
  - Effort: 1-2 prompts

- [ ] **T1.04** Get pytest suite running
  - What: 0 tests currently collected from `victus/ion/`
  - Approach: Check conftest.py, check test file naming, check __init__.py chain
  - Verification: `pytest victus/ion/ -v` collects 50+ tests, all pass
  - Files to check: `victus/ion/conftest.py`, `victus/ion/tests/`, pytest.ini or setup.cfg
  - Effort: 2-4 prompts

- [ ] **T1.05** Wire AetherEngine → LLM Adapter
  - Depends on: T1.01 (bootstrap), T1.02 (seed ions for context)
  - What: engine.process() should flow through: context_compiler → llm_adapter → response
  - Approach: Read engine.py, verify adapter wiring, trace call path
  - Verification: Unit test showing engine.process("hello") returns coherent response via mock adapter
  - Effort: 2-3 prompts

- [ ] **T1.06** First live LLM call
  - Depends on: T1.05 (engine wiring), T1.02 (seed data for context)
  - What: Call through real Gemini or Ollama, not mock
  - Approach: Configure API keys/endpoints, run engine.process() with real adapter
  - Verification: `python -c "..."` returns an LLM response that includes ion context
  - Evidence: Response shows awareness of ion graph (not vanilla LLM response)
  - Effort: 2-3 prompts
  - **This is the most important task in Phase 1**

- [ ] **T1.07** A/B comparison: ION context vs no context
  - Depends on: T1.06 (live LLM working)
  - What: Same prompt, once with ION context pipeline, once without → compare
  - Verification: Document showing measurable improvement in response quality/relevance
  - Effort: 1 prompt

- [ ] **T1.08** Governed write e2e test
  - What: Create an ion via the governed write pipeline, verify all 10 stages execute
  - Verification: Ion created on disk, audit trail in output, authority enforced
  - Effort: 1 prompt

- [ ] **T1.09** Navigator e2e test
  - What: Submit a task to the navigator, verify 7-step cognitive loop completes
  - Verification: All 7 steps logged: contextualize→reflect→plan→gate→execute→audit→deliver
  - Effort: 1 prompt

### 3.2 Phase 1 Gate (ALL must be true to proceed)

```
□ bootstrap_network() completes without hanging
□ data/ions/ exists with 16+ seed ions
□ 0 legacy enum references remain
□ pytest collects 50+ tests, all pass
□ engine.process() returns LLM response with ion context
□ Live LLM call succeeds (Gemini or Ollama, not mock)
□ Governed write creates ion on disk with full audit trail
□ Navigator completes 7-step loop for a test task
□ This orchestration document is updated with Phase 1 results
```

---

## §4. PHASE 2 — VS CODE EXTENSION
**Status: ⬜ NOT STARTED**
**Goal: ION powers a VS Code extension that actually improves coding**
**Estimated prompts: 30-50**
**Depends on: Phase 1 gate**

> [!IMPORTANT]
> This is the first PRODUCT. Not a demo. An extension that makes VS Code measurably better
> because ION understands your codebase.

### 4.1 Extension Foundation (10-15 prompts)

- [ ] **T2.01** VS Code extension scaffold
  - Create TypeScript project with extension API
  - Register commands: `ion.ingest`, `ion.query`, `ion.inspect`, `ion.agents`
  - Register views: sidebar panel, graph visualization
  - Verification: Extension loads in VS Code, shows in sidebar
  - Effort: 3-5 prompts

- [ ] **T2.02** ION Server API (REST/WebSocket)
  - Expose ION engine operations as HTTP endpoints
  - Endpoints: /ingest, /query, /process, /ions, /graph, /status
  - WebSocket for real-time events (ion created, bond formed, agent message)
  - Verification: `curl localhost:PORT/status` returns ION engine health
  - Effort: 3-4 prompts

- [ ] **T2.03** Extension ↔ Server bridge
  - Extension connects to ION server on activation
  - Bidirectional: extension sends workspace context, server sends ion events
  - Reconnection handling, status indicator in VS Code status bar
  - Verification: Extension connects, icon in status bar shows green
  - Effort: 2-3 prompts

### 4.2 Code Intelligence (10-15 prompts)

- [ ] **T2.04** Workspace ingest (code → ions)
  - Use tree-sitter to parse workspace files into ions
  - Each function/class/module becomes an ion with bonds
  - File save triggers re-ingest of changed file
  - Verification: Open a Python project → ions appear in ION sidebar panel
  - Effort: 5-7 prompts

- [ ] **T2.05** Context-aware chat
  - Chat panel in VS Code that uses ION context pipeline
  - Three-tier context: current file (pinned), open tabs (working), workspace (long-term)
  - LLM responses grounded in actual codebase understanding
  - Verification: Ask "what does function X do?" → response references actual code
  - Effort: 3-5 prompts

- [ ] **T2.06** Governed code writes
  - When AI suggests code changes, they go through governed write pipeline
  - 10-stage validation before applying change to workspace
  - Audit trail: who requested, what changed, what was validated
  - Verification: AI-generated code change shows governance receipt
  - Effort: 2-3 prompts

### 4.3 Visualization & UX (5-10 prompts)

- [ ] **T2.07** Ion graph panel
  - Sidebar panel showing ion graph for current workspace
  - Clickable nodes → navigate to source code
  - Bond visualization (imports, calls, inherits)
  - Verification: Visual graph appears when workspace is ingested
  - Effort: 3-5 prompts

- [ ] **T2.08** Confidence overlay
  - Show K-Gate confidence scores on AI responses
  - Color coding: green (high confidence), yellow (moderate), red (low/abstaining)
  - Verification: AI response shows confidence badge
  - Effort: 1-2 prompts

- [ ] **T2.09** Status bar integration
  - ION status: connected/disconnected, active ions, last operation
  - Click → show ION dashboard panel
  - Verification: Status bar shows ION icon with live data
  - Effort: 1-2 prompts

### 4.4 Phase 2 Gate

```
□ Extension installs and activates in VS Code
□ Workspace files are ingested as ions
□ Chat panel returns contextually-aware responses
□ Five real coding tasks improved by ION context (documented)
□ Governed write pipeline enforced on AI code suggestions
□ Ion graph displays and is navigable
□ Confidence overlay working on responses
□ Extension published to VS Code Marketplace (or local VSIX)
□ Braden has used it for a full coding session and confirms value
```

---

## §5. PHASE 3 — ION IDE (VS CODE FORK)
**Status: ⬜ NOT STARTED** | **Depth Class: 1** *(objectives + tasks + gate — detail added when Phase 2 nears gate)*
**Goal: Fork VS Code into a purpose-built ION IDE**
**Depends on: Phase 2 gate + Braden architecture approval**

### 5.1 Strategic Objectives

1. Fork VS Code (or Theia) into a standalone branded product: ION IDE
2. Replace the command palette with the 7-step cognitive loop as primary interaction
3. Replace the file tree with the ion graph browser (semantic, not hierarchical)
4. Integrate JOC as a native IDE panel
5. Make constitutional governance visible (authority badges, governed write receipts, claim tags)
6. Built-in agent swarm management

### 5.2 Decisions Required Before Phase 3 (can be surfaced earlier)

> [!IMPORTANT]
> These decisions affect Phase 2 architecture and should be evaluated during Phase 2.

| Decision | Options | Deadline | Why It Matters Now |
|----------|---------|----------|--------------------|
| Fork base | VS Code vs Theia vs OpenVSX | Phase 2 midpoint | Extension architecture differs per base |
| Graph browser tech | D3.js vs Cytoscape vs custom WebGL | Phase 2 T2.07 | Graph panel in Phase 2 should use same tech |
| Agent protocol | LSP extension vs custom WebSocket | Phase 2 T2.03 | Bridge architecture carries forward |

### 5.3 Phase 3 Gate

```
□ ION IDE builds and runs as standalone application
□ File tree replaced by ion graph browser
□ Command palette replaced by cognitive loop UI
□ Agent swarm spawnable and monitorable from IDE
□ Braden uses ION IDE for a full day and confirms superiority to VS Code
```

---

## §6. PHASE 4 — AETHER LINUX
**Status: ⬜ NOT STARTED** | **Depth Class: 0** *(objective + gate only — elevates when Phase 3 nears gate)*
**Goal: A bootable Linux distro with ION as native intelligence layer**
**Depends on: Phase 3 gate**

### 6.1 Strategic Anchors

- ION filesystem daemon: file system events → ion creation (inotify/fanotify)
- systemd services: ION server + MCP bridge + agent mesh as system services
- ION-aware package manager (dependency reasoning via ion graph)
- Capsule-based session management (login → resume capsule)

### 6.2 Early Decision (may surface during Phase 2-3)

| Decision | Why It Matters Early |
|----------|---------------------|
| Base distro (Arch vs NixOS vs custom) | Nix's declarative model maps well to ions; Arch is simpler |
| Filesystem approach (overlay vs native) | Determines Phase 5 compatibility |

### 6.3 Phase 4 Gate

```
□ ISO boots on bare metal or VM
□ ION filesystem daemon running — file events create ions
□ Braden daily-drives it for 1 week without reverting
```

---

## §7. PHASE 5 — ION-OS (QUATERNION KERNEL)
**Status: ⬜ NOT STARTED** | **Depth Class: 0** *(vision + gate only — A6 Research Branch)*
**Goal: Full unique operating system with physics-based kernel**
**Depends on: Phase 4 gate + significant research**

### 7.1 Vision

Ion graph IS the filesystem. Quaternion kernel provides 4 syscalls (place, move, sense, emit).
S³ binning for geometric process scheduling. Self-modifying governance within constitutional bounds.
Witness structures for every state transition.

### 7.2 Existing Foundation

- `packages/quaternion_kernel/` (641 lines Rust) — 4 syscalls prototyped, morton4D indexing
- `packages/quaternion_math/` — S³ geometry library
- Atlas §4.28: classified as A6 Research Branch, DOCTRINAL_ONLY runtime truth

### 7.3 Phase 5 Gate

```
□ Kernel boots on at least one hardware platform
□ 4 syscalls operational
□ Ion filesystem stores and retrieves ions natively
□ Self-modifying governance demonstrated within bounds
```

---

## §8. PHASE A — MVP AI BUILDER (Parallel Track)
**Status: ⬜ NOT STARTED** | **Depth Class: 2** *(elevated — potential FIRST revenue product)*
**Goal: First revenue product — Lovable-style web AI builder powered by ION**
**Estimated prompts: 40-60**
**Can run in parallel with Phase 2-3**

> [!IMPORTANT]
> This may be the FIRST product shipped. It can start as soon as Phase 1 gate passes.
> It's a web app, not an IDE — simpler to ship, easier to monetize.

### 8.1 Task Breakdown

- [ ] **TA.01** Web app scaffold (Next.js or Vite)
- [ ] **TA.02** Chat interface with ION context pipeline
- [ ] **TA.03** Code generation with governed writes
- [ ] **TA.04** Project preview (live rendering of generated code)
- [ ] **TA.05** Authentication + user accounts
- [ ] **TA.06** Subscription/payment (Stripe)
- [ ] **TA.07** Deployment pipeline (user projects → hosted URLs)
- [ ] **TA.08** K-Gate confidence UI (user sees AI confidence)
- [ ] **TA.09** Ion graph visualization for generated projects
- [ ] **TA.10** Landing page + marketing
- [ ] **TA.11** Beta launch with 10 testers
- [ ] **TA.12** Public launch

### 8.2 Phase A Gate

```
□ Web app accessible at public URL
□ User can sign up, describe a project, and get working code
□ Generated code passes basic quality checks via governed write
□ 10 beta testers confirm value
□ Payment processing works
□ Braden approves public launch
```

---

## §9. ANTI-DRIFT PROTOCOL

### 9.1 Every 5 Tasks

After completing every 5 tasks (regardless of phase):
1. Re-read §0 (MISSION IDENTITY) — am I still on mission?
2. Check: is my current work advancing the CURRENT PHASE goal?
3. If not: STOP. Document the drift reason. Re-orient.
4. Update this document with completed tasks and any new discoveries.

### 9.2 Every Session Start

1. Read this document (§0 for mission, current phase for tasks)
2. Check what was last completed (look for most recent `[x]` task)
3. Verify the next unchecked task still makes sense
4. If reality has changed: update §1 (GROUND TRUTH) first
5. Post SITREP capsule via MCP

### 9.3 Phase Transition Protocol

Before declaring a phase complete:
1. Check EVERY gate condition (§X.Y Phase Gate)
2. Run ALL verification commands listed
3. Document results in this file under the gate
4. Get Braden approval for phase transition
5. Update §0 CURRENT PHASE

### 9.4 Discovery Protocol

When discovering something unexpected during execution:
1. If it changes ground truth → update §1 immediately
2. If it adds a new task → add it to the current phase with T{phase}.{next_number}
3. If it blocks another task → update the blocked task's "Depends on" field
4. If it contradicts this plan → surface the contradiction (Constitution Art. 10)

---

## §10. RESOURCE MAP

### Key Files to Read First

| When | Read This | Why |
|------|-----------|-----|
| Any session start | This document (§0 + current phase) | Mission orientation |
| Need system architecture | [DOC_ARCHITECTURE.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/DOC_ARCHITECTURE.md) | Organization spec |
| Need to find a system | [SYSTEM_UNIVERSE_MAP.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/SYSTEM_UNIVERSE_MAP.md) | 170+ systems indexed |
| Need governing law | [AETHER_KERNEL.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/AETHER_KERNEL.md) | Boot projection of constitution |
| Need runtime truth | [AETHER_ATLAS.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/AETHER_ATLAS.md) Book III | 32 objects assessed |
| Need to boot an agent | [BOOTLOADER.md](file:///home/sev/AIM-OS-GIT/.agent/BOOTLOADER.md) | 8-step boot sequence |
| Need the original vision | [AIM_OS_NORTH_STAR.md](file:///home/sev/AIM-OS-GIT/AIM_OS_NORTH_STAR.md) | Nov 2025, 838 lines |
| Need honest build state | [ION_STATE_OF_BUILD.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/ION_STATE_OF_BUILD.md) | Evidence register |
| Need file-level audit | [ION_RUNTIME_AUDIT.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/ION_RUNTIME_AUDIT.md) | 63 keep, 36 cut |

### Key Commands

| Command | Purpose |
|---------|---------|
| `cd /home/sev/operation-victus && python -m pytest victus/ion/ -v` | Run ION test suite |
| `grep -rn "A4_SYSTEM\|A3_CORE\|A1_LOCAL" victus/` | Find legacy enum refs |
| `find victus/ion/ -name "*.py" \| wc -l` | Count ION modules |
| `ls /home/sev/operation-victus/data/.ion/ 2>/dev/null \| wc -l` | Check seed ions |
| `python -c "from victus.ion.bootstrap import bootstrap_network; bootstrap_network()"` | Test bootstrap |
| `curl -s http://127.0.0.1:5001/health` | Check MCP HTTP bridge |
| `ps aux \| grep lucid_mcp` | Check MCP process |

---

## §11. PROGRESS LOG

> Updated after each significant action. Most recent entry at top.

### 2026-03-24T18:20 — Session 2 (Prompt ~15)
- **Completed:** T0.01-T0.04 (audit, canon read, doc architecture v2)
- **Created:** STATE_OF_THE_UNION.md, DOC_ARCHITECTURE.md (v2), MASTER_ORCHESTRATION.md
- **Key discovery:** Atlas already defines L1-L8 load order, registry schema, and runtime truth states. My original doc architecture was misaligned — rewrote for full canon compliance.
- **Next:** T0.05-T0.12 (remaining Phase 0 organize tasks)

### 2026-03-24T14:00 — Session 2 (Prompt ~8)
- **Completed:** System map visualization (isometric city view)
- **Created:** system_map_design.md, walkthrough.md
- **Note:** Braden wanted deeper than visualization — wanted real audit maps

### 2026-03-24T01:50 — Session 1 (Prompts 1-7)
- **Completed:** Swarm deployment (FORGE/NEXUS/WEAVER/SENTINEL/ATLAS)
- **Key results:** FORGE fixed enums + wired server. NEXUS rewrote LLM adapter. WEAVER restored agent types. SENTINEL exposed 0-test-collected + missing data/ions.
- **Created:** implementation_plan.md (v1 — now superseded by this document)

---

*This document is the mission. Work from it. Update it. If it drifts from reality, fix it immediately.*
*— Opus, 2026-03-24*
