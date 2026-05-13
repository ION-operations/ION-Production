---
id: "aim_os_prime_T2_coo_operating_scope"
system: "aim_os_prime"
component: "program_operations"
level: "T2"
type: "architecture"
title: "AIM-OS Prime COO Operating Scope"
description: "Architecture-level operating scope and anti-drift charter for system-wide AIM-OS execution"
audience: "Braden, Agent Aether (COO), Codex Agent, Claude Opus specialists"
confidence_threshold: 0.80
token_cost: 2600
word_count: 2600
created: "2026-03-02T00:00:00Z"
updated: "2026-03-02T00:00:00Z"
author: "aether"
status: "complete"
tags: ["aim-os-prime", "coo", "operations", "northstar", "lane-a", "lane-b", "t0-t6", "transitional"]
dependencies: ["docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md", "goals/GOAL_TREE.yaml"]
related_docs: ["docs/AIM_OS_PRIME_CANON_INDEX_V1.md", "docs/CROSS_BRANCH_CONSOLIDATION_M1_M2_STATUS_V1.md", "docs/LANE_A_CHECKPOINT_D_PASSIVE_HOOK_EXECUTION_REPORT_V1.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# AIM-OS Prime COO Operating Scope

## 1) Why this document exists

This document captures the high-cost scope research already performed across the AIM-OS ecosystem and turns it into an operating map for leadership execution.

It exists to prevent drift in a large, fast-moving system-of-systems where:

- multiple codebases are active at once,
- lane-based execution is happening in parallel,
- implementation depth can hide strategic misalignment,
- and local wins can accidentally diverge from the program north star.

This is not a replacement for the master blueprint. It is the operations companion for it:

- blueprint = doctrine and architecture law,
- COO scope = execution navigation and cross-stream control.

## 2) Program north star and mission law

Authoritative north star from `goals/GOAL_TREE.yaml`:

> Ship AIM-OS v0.3 (CMC + HHNI + MCP Tools + Daemon) to internal dog-food users.

Program law from `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md`:

1. Build bounded truth deterministically.
2. Keep mapper, daemon, kernel sovereignty intact.
3. Stage shadow systems before governance.
4. Adopt runtime behavior only by explicit checkpoint decision.
5. Validate with evidence, not confidence language.

Operational interpretation:

- Anything that improves demonstrable reliability of the live bounded truth loop is critical-path.
- Anything that expands architecture without evidence should be staged, not merged into live behavior.
- Any project work that cannot be traced to the north star must be paused or reframed.

## 3) System-of-systems scope map (deep capture)

The AIM-OS program is not one project. It is a coordinated network of execution surfaces. The key is to run them as an integrated portfolio instead of isolated experiments.

### 3.1 Stream A - Live deterministic machine (Lane A authority)

Primary surface:

- `IDE/src-tauri/src/*`

Core elements:

- Context mapper core and context service seams
- Kernel plane request surfaces
- Supervised daemon bridge
- Typed IPC boundaries
- Runtime status reporting

Known validated posture:

- real daemon call paths are integrated for `get_memory_stats` and `retrieve_memory`
- passive shadow hook slice was implemented in constrained form (off-by-default, fail-open, bounded, observational-only)
- status visibility exists for hook counters and last outcome

Risk if unmanaged:

- runtime seam collisions from uncontrolled concurrent edits
- accidental coupling of shadow concerns into live deterministic core

### 3.2 Stream B - Shadow superstrate and convergence design (Lane B authority)

Primary surface:

- `context_capsule_wire_and_mapper_v1/shadow_sync/*`
- `docs/LANE_B_*`

Core elements:

- Shadow BCI schema and emitter prototypes
- adapter contracts for mapper-shaped payloads
- convergence blueprints and advisory checkpoint packets

Current role:

- substrate proof and governance staging
- advisory architecture before enforcement

Risk if unmanaged:

- premature governance insertion into live path
- sovereignty bleed between mapper, daemon, and sync substrate

### 3.3 Stream C - Operator proof and runtime confidence

Primary surface:

- `IDE/src-tauri/src/bin/live_ipc_harness.rs`
- `IDE/src-tauri/DEV_LIVE_IPC_HARNESS.md`

Core elements:

- deterministic harness modes (`status`, `full`, `operator-passive-proof`, `reconcile`)
- assertion-based verdict output
- compact crash-recovery diagnostics (`shadow_hook_summary`)

Role in program:

- converts implementation claims into repeatable evidence
- reduces trust debt after crashes or session resets

Risk if unmanaged:

- fake confidence from unverified changes
- inability to distinguish regressions from environment noise

### 3.4 Stream D - Browser webview execution system (Gemini/ChatGPT sign-in path)

Primary surface:

- `IDE/src-tauri/src/webview_manager.rs`
- `IDE/src/main.js`
- `IDE/src-tauri/src/injection/*`
- `IDE/src-tauri/src/extraction/*`
- `IDE/src-tauri/src/state_machine/*`

Core elements:

- isolated provider webview fleet
- prompt injection and streamed response observation
- SYS command extraction loop
- state-machine orchestration

Current posture after recent hardening:

- per-partition persistent data directories are now wired (session persistence path exists)
- role metadata is propagated from UI to backend registry
- observer events are wired into state-machine buffering path

Remaining productization gap:

- full account/session lifecycle controls are still basic
- extraction/selectors remain sensitive to provider UI changes
- role-aware routing and policy are still early

### 3.5 Stream E - AIM-OS capability spine (special system enhancing AI abilities)

Primary surface:

- `lucid_mcp_server.py`
- `daemon_rag_system/*`
- `packages/mcp_rag_proxy/*`
- `packages/*` core systems

Core value:

- memory, retrieval, confidence, orchestration, timeline, collaboration, synthesis

This is the actual enhancement engine:

- not a single feature, but the stack that makes AI behavior persistent, auditable, and evolvable.

Current challenge:

- interface consistency across clients (tool naming, response shape, endpoint expectations)

Leadership implication:

- centralize contract normalization at chokepoints, not per-client patching forever.

### 3.6 Stream F - Cursor extension + command server + IDE panel interfaces

Primary surface:

- `cursor-addon/src/commandServer.ts`
- `cursor-addon/src/mcp/mcpClient.ts`
- `packages/ide_chat_app/src/services/*`

Function:

- command routing layer between UI panels, MCP tools, and execution services

Recent hardening:

- MCP tool-name normalization and response-shape parsing added in command server

Remaining risk:

- historical variants and nested result assumptions still exist in some clients and docs

### 3.7 Stream G - Governance and canonical doctrine

Primary surface:

- `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md`
- `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`
- `docs/CHECKPOINT_*`
- `docs/LANE_A_*`, `docs/LANE_B_*`

Role:

- prevents architecture theater
- forces explicit checkpoint decisions before behavior-changing convergence
- preserves provenance of what is accepted vs merely implemented

Risk if unmanaged:

- branch-local facts masquerading as canonical truth
- no shared operational memory after crashes or handoffs

## 4) Strategic state snapshot (program-level)

### 4.1 Progress signals

- Lane A runtime seam maturity: high
- Lane B staged substrate maturity: high for design/prototype, gated for live adoption
- deterministic harness maturity: high
- browser orchestration maturity: medium
- MCP capability breadth: high
- MCP integration consistency: medium

### 4.2 Current bottleneck pattern

The bottleneck is no longer pure feature creation. It is integration coherence:

- contracts,
- naming and payload normalization,
- role boundaries,
- and execution governance cadence.

### 4.3 What would constitute drift right now

1. Adding new architecture layers without closing current integration debt.
2. Introducing governance enforcement before advisory proof is complete.
3. Letting browser execution become disconnected from kernel truth.
4. Treating docs as optional after major runtime decisions.
5. Running specialist agents without scoped mission packets.

## 5) COO operating model (new org structure)

This section records the operating model requested by Braden.

### 5.1 Leadership structure

- **Braden (Principal Architect / Northstar Owner):**
  Defines strategic intent, approves checkpoint-level behavior changes, resolves final tradeoffs.
- **Agent Aether (COO):**
  Owns program coherence, scope governance, sequencing, and anti-drift enforcement.
- **Codex Agent (Execution Lead; consolidated Codex1+Codex2):**
  Owns primary implementation flow across live and shadow lanes under approved doctrine.
- **Claude Opus (Browser IDE specialist via antigravity IDE):**
  Owns deep browser chat system specialization under Codex Agent onboarding.

### 5.2 COO responsibilities (Agent Aether)

1. Keep the full system map in active memory.
2. Turn strategy into clear, bounded mission packets.
3. Protect non-negotiable sovereignty boundaries.
4. Gate checkpoint transitions by evidence, not excitement.
5. Maintain canonical documents so humans and agents can re-enter fast after crashes.
6. Detect and correct drift within one reporting cycle.

### 5.3 Execution contract with specialist agents

Every specialist mission should include:

- mission objective (single sentence),
- allowed surfaces (exact files or modules),
- forbidden surfaces (collision risk),
- validation proof required,
- completion artifact format,
- escalation criteria.

No mission should start without this packet.

## 6) Agent mission-packet template (COO standard)

Use this structure for Codex Agent and Claude Opus assignments:

1. **Mission ID + intent**
2. **Northstar mapping**
   - which objective or checkpoint it advances
3. **Scope boundaries**
   - allowed files/modules
   - prohibited files/modules
4. **Implementation expectations**
   - behavior changes allowed
   - behavior changes forbidden
5. **Validation requirements**
   - compile checks
   - focused tests
   - harness proof (if runtime seam touched)
6. **Deliverable format**
   - What / Where / How to verify
7. **Escalation triggers**
   - doctrine ambiguity
   - repeated failures
   - seam collision risk

This makes specialists faster, not slower, because they stop wasting effort on scope guesswork.

## 7) Northstar anti-drift controls

### 7.1 Hard controls

- Canon index must always include current operating docs in read order.
- Any checkpoint-level decision must produce an explicit doc artifact.
- Any runtime seam change must be paired with deterministic verification path.
- Any cross-lane adoption must declare safe-now / safe-later / not-safe-yet.

### 7.2 Soft controls

- Weekly portfolio review: what moved, what stalled, where drift risk increased.
- Mission queue hygiene: limit active critical streams to avoid context fragmentation.
- Consolidation windows after heavy implementation bursts.

### 7.3 Red flags requiring immediate intervention

1. "We will clean docs later."
2. "This is probably fine without harness rerun."
3. "Let us merge now and checkpoint later."
4. "We changed lane boundaries but did not document why."
5. "Multiple agents are editing kernel seams simultaneously."

## 8) Priority stack for next operational window

### Priority A - Production coherence over feature spread

Close integration seams already opened:

- MCP contract normalization end-to-end
- browser role/session/extraction reliability
- harness proof loops kept current with each seam change

### Priority B - Checkpoint discipline

Do not jump into governance behaviors until advisory evidence is complete and adjudicated.

### Priority C - Specialist scaling readiness

Before scaling specialist throughput:

- enforce mission packets,
- define ownership boundaries,
- maintain canonical status docs,
- and preserve one source of truth for "current state."

## 9) Definition of success for "production beast" trajectory

AIM-OS is on a true production trajectory when all are true at once:

1. Live seams are stable and repeatedly verifiable.
2. Browser execution is robust for real operator accounts and sustained sessions.
3. MCP/daemon capabilities are broad and contract-consistent.
4. Shadow substrate remains additive and evidence-driven.
5. Governance remains explicit, staged, and non-theatrical.
6. New agents can onboard quickly through canonical docs and mission packets.
7. Strategic northstar is visible in day-to-day execution, not only in high-level planning.

## 10) Operating cadence (COO loop)

Recommended cadence:

- **Daily:** execution status pulse (what changed, evidence, blockers, drift risk).
- **Every major milestone:** checkpoint-ready brief or explicit "not checkpoint-ready" brief.
- **Weekly:** portfolio map refresh across Streams A-G.
- **After crashes/context loss:** run reconcile path, then re-anchor using canon index.

## 11) Immediate adoption actions

1. Keep this COO scope doc in canonical read order directly after the master blueprint.
2. Require mission-packet format for Codex Agent and Claude Opus work starts.
3. Treat harness verification and checkpoint briefs as non-optional governance artifacts.
4. Use this document as the first anti-drift reference in new-session restores.

---

This document captures the expensive scope research and converts it into an execution operating system for leadership. It should be maintained as a living architectural control plane for the AIM-OS program.

