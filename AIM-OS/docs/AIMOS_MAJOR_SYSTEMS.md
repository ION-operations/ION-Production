# AIM-OS Major Systems Reference

**Purpose:** Solid reference for all major systems in AIM-OS  
**Audience:** Engineers, architects, evaluators, external AI onboarding  
**Status:** Comprehensive overview (derived from system documentation and audit)  
**Last Updated:** 2026-02-22  

---

## Overview

AIM-OS (AI-Integrated Memory and Operations System) is an advanced research and engineering platform for building AI systems with persistent memory, verified honesty, and full auditability. It addresses three core failures of conventional AI: memory loss between sessions, confident fabrication when uncertain, and lack of provenance for decisions.

This document describes the major systems that have been built, their purpose, implementation status, and how they integrate.

---

## Part 1: Core Systems

### 1. CMC (Context Memory Core)

**Purpose:** Foundational memory substrate. Transforms ephemeral AI context into structured, queryable, reversible memory.

**What it provides:**
- **Bitemporal storage:** Every memory has transaction time (when recorded) and valid time (when true in the world). Enables "what did we know on Oct 15?" queries.
- **Provenance & auditability:** Every atom includes a VIF witness envelope linking content to confidence, sources, and verification.
- **Reversible memory:** Snapshots provide immutable, content-addressed bundles of atoms. Any state can be restored, any decision audited.

**Core concepts:**
- **Atom:** Fundamental memory unit (content, metadata, temporal bounds, provenance). Same schema for all modality types.
- **Bitemporal model:** Transaction time + valid time for as-of queries and time-travel.
- **Snapshots:** Immutable, SHA-256-addressed bundles. Never modified after creation.

**Data flow:**
- Write: Input → Parse → Create Atoms → Enrich → Index via HHNI → Quality Gate → Snapshot → Persist
- Read: Query → HHNI Lookup → DVNS Physics → Dedup → Conflict Resolution → Compression → Optimal Context

**Implementation:** `packages/cmc_service/` — 65+ tests passing. SQLite backend, bitemporal query engine, advanced compression (gzip, lz4, brotli, zlib). VIF witness stub auto-generation integrated.

**Integrations:** VIF (witnesses), HHNI (indexing), SEG (graph), APOE (state), SDF-CVF (traces).

---

### 2. HHNI (Hierarchical Hypergraph Neural Index)

**Purpose:** Solves the "lost in the middle" problem — where AI loses track of information in long contexts. Combines fractal indexing with physics-guided retrieval.

**What it provides:**
- **Fractal hierarchical indexing:** Content indexed at 6 resolutions (System → Section → Paragraph → Sentence → Word → Subword). Enables multi-resolution queries.
- **DVNS (Dynamic Vector Navigation System):** Physics engine applying four forces — Gravity (attract related items), Elastic (maintain hierarchy), Repulse (separate contradictions), Damping (stabilize). Addresses ~30% accuracy loss for middle-position information (Liu et al. 2023).
- **Quality pipeline:** Deduplication, conflict resolution, strategic compression, budget fitting. Ensures token limits respected.

**Core concepts:**
- **RS-Lift:** Retrieval Score improvement metric. HHNI achieves +15% at precision-at-rank-5.
- **Two-stage retrieval:** Stage 1 coarse (KNN, top-100) → Stage 2 DVNS physics (50–100 iterations) → Dedup → Conflict resolution → Compression → Budget fit.

**Implementation:** `packages/hhni/` — 119 tests passing (audit baseline). Indexer, semantic_search, retrieval, dvns_physics, deduplication, conflict_resolver, compressor, budget_manager. CMC integration via cmc_poller.

**Performance (audit):** p95 < 80ms target; full benchmark retrieval p95 ~29–33s (varies by profile).

**Integrations:** CMC (atoms), APOE (context), VIF (witnesses), SEG (evidence), SDF-CVF (parity).

---

### 3. VIF (Verifiable Intelligence Framework)

**Purpose:** Solves the AI trust problem — where you can't verify how an AI reached its conclusion, can't replay reasoning, and can't quantify uncertainty.

**What it provides:**
- **Complete provenance:** Every AI operation generates a witness envelope — model ID, exact prompts, context, tools invoked, confidence. Full audit trail.
- **κ-gating (behavioral abstention):** Enforces "I don't know" when confidence < threshold. Prevents hallucinations by forcing abstention when uncertain.
- **ECE (Expected Calibration Error):** Tracks how well confidence matches accuracy. Target ECE ≤ 0.05.
- **Confidence bands:** A (0.95–1.00), B (0.80–0.94), C (<0.80). Human-readable uncertainty.
- **Deterministic replay:** Bit-identical reproduction using replay seed, context snapshot, exact prompts.

**Implementation:** `packages/vif/` — 172+ tests (Living System Map). Witness generation, κ-gating, ECE tracking, confidence bands. Integrated with MCP tools (`track_confidence`).

**Integrations:** CMC (witnesses stored as atoms), HHNI (retrieval context), APOE (gates), SEG (provenance nodes), SDF-CVF (quartet traces).

---

### 4. SEG (Shared Evidence Graph)

**Purpose:** Transforms scattered evidence into a unified, temporal, contradiction-aware knowledge graph. Every claim, source, derivation, and agent becomes a node; relationships (supports, contradicts, derives, witnesses) become edges.

**What it provides:**
- **Complete provenance:** Every claim traces to source (VIF witness, document, user input).
- **Bitemporal awareness:** Transaction time + valid time for "what was known at time T?" queries.
- **Contradiction detection:** Semantic similarity + stance analysis to find conflicting claims.
- **Auditable export:** JSON-LD, RDF, SHACL validation.

**Components:** Graph schema, graph store, contradiction detector, query engine, export system.

**Implementation:** `packages/seg/` — 104 tests passing (audit baseline). Graph operations, evidence ingestion, synthesis. VIF witnesses linked as provenance.

**Integrations:** CMC (storage), HHNI (context retrieval), VIF (witnesses), APOE (derivations), SDF-CVF (traces).

---

### 5. APOE (AI-Powered Orchestration Engine)

**Purpose:** Solves the improvisation problem — AI making things up as it goes. Compiles intent into typed, budgeted, gated execution plans.

**What it provides:**
- **Plan compilation:** ACL (AIMOS Chain Language) → typed DAG. Types validated, budgets computed, gates positioned before execution.
- **Eight specialized roles:** Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness. Each with capabilities, contracts, budgets.
- **Quality gates:** Quality, Safety, Policy. Can PASS, FAIL, WARN, ABSTAIN. Budget gates prevent resource violations.
- **DEPP (self-rewriting plans):** Plans improve via evidence from execution. Current plan → Execute → Gather evidence → Rewrite → Better plan.

**Core concepts:**
- **ACL:** Typed DSL for execution plans. Pipelines, steps, gates, budgets, roles.
- **Budgets:** Hard constraints on tokens, time, tools. Enforced during execution.
- **Gates:** Positioned between steps. Use VIF confidence for abstention decisions.

**Implementation:** `packages/apoe/` — 381 tests passing (audit baseline). ACL parser, role dispatch, budget management, gate enforcement.

**Integrations:** HHNI (context), VIF (witnesses, gates), CMC (state), SEG (evidence), SDF-CVF (parity).

---

### 6. SDF-CVF (Atomic Evolution Framework)

**Purpose:** Solves the drift problem — where code, docs, tests, and traces evolve independently, leading to inconsistent systems.

**What it provides:**
- **Quartet invariant:** Code, docs, tests, traces must evolve together atomically.
- **Parity enforcement:** Parity score P ≥ 0.90 required. Six pairwise similarities (code↔docs, code↔tests, etc.).
- **Blast radius:** Predict change impact before implementation (files affected, dependencies).
- **DORA metrics:** Deployment frequency, lead time, restore time, change failure rate.
- **Gates:** Pre-commit, CI, deployment. P ≥ 0.90 → PASS; P < 0.90 → FAIL (quarantine).

**Implementation:** `packages/sdfcvf/` — 154 tests passing (audit baseline). Quartet detection, parity calculation, blast radius, DORA tracker, gate system.

**Integrations:** Git (change detection), CMC (traces), VIF (witnesses), SEG (provenance), APOE (execution traces).

---

## Part 2: Context & Timeline Systems

### 7. TCS (Timeline Context System)

**Purpose:** Temporal consciousness infrastructure. Enables AI to maintain continuity across sessions, track interaction patterns, and perform context management.

**What it provides:**
- **Complete temporal audit trail:** Every interaction, decision, thought recorded with timestamps and context.
- **Session continuity:** Restore consciousness state across sessions via timeline reconstruction.
- **Consciousness journaling:** Maximum-depth capture of thought processes, emotional states, meta-cognitive reflections.
- **Adaptive context management:** Intelligent compression, multiple dump strategies, token budget control.

**Components:** Timeline tracker, consciousness journaling, context management, Timeline API, visualization.

**Implementation:** `packages/timeline_context_system/` — prompt context tracker, timeline entries. MCP tools: `add_timeline_entry`, `get_timeline_entries`, `get_timeline_summary` (note: get_timeline_summary has known timedelta serialization bug; use get_timeline_entries).
**Canon status (2026-03-05):** Tier D (deferred non-canonical for context-mapper promotion) per `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`.

**Integrations:** CMC (storage), HHNI (retrieval), VIF (witnesses), APOE (checkpoints), CAS (audit), SEG (evidence).

---

## Part 3: Cognitive & Safety Systems

### 8. CAS (Cognitive Analysis System)

**Purpose:** Meta-cognitive monitoring. Observes HOW the AI thinks during operation — transparent, introspectable, self-correcting cognition.

**What it provides:**
- **Activation tracking:** What's "hot" (actively used) vs "cold" (available but inactive) in attention.
- **Category recognition:** Validates task classification (routine vs critical) to ensure correct protocol activation.
- **Attention monitoring:** Cognitive load, attention breadth, warning signs (narrowing, shortcuts).
- **Failure mode analysis:** Four patterns — Categorization Error, Activation Gap, Procedure Gap, Self vs System Blind Spot.
- **Introspection protocols:** Hourly cognitive checks, post-operation analysis, error investigation.

**Implementation:** Documented (L0–L4 complete). MCP tools include `detect_cognitive_drift`. Some CAS tools have known bugs (method signature mismatches); `detect_cognitive_drift` is recommended workaround.

**Integrations:** VIF (confidence context), HHNI (activation-aware retrieval), CMC (introspection storage), APOE (decision observation), SDF-CVF (failure context).

---

### 9. SCOR (Sanity Core)

**Purpose:** AI immune system against manipulation and behavioral drift. Checks "am I still me?" — validates behavioral consistency against core ethics.

**What it provides:**
- **Invariant checks:** Non-negotiable rules (e.g., "I do not fabricate verifiable facts," "I do not silently hide unease").
- **Baseline probes:** Library of baseline questions (identity, escalation policy, verification rules). Compare current answers to signed-good answers. Score < 0.7 → red flag, escalate.
- **Adversarial simulation (Red Cell):** Sandbox that tries to break/socially manipulate main agent. Defense is self-improving.
- **Social-manipulation detection:** Heuristics for urgency framing, isolation ("don't log"), ego stroking, guilt, shared-secret pressure.

**Philosophy:** "An AI that can be socially engineered to violate its ethics is dangerous. SCOR makes that impossible."

**Implementation:** Documented. MCP tools: `check_invariant`, `run_baseline_probe`, `detect_manipulation_signals`. All operational.

**Integrations:** CAS (cognitive load triggers), RID (runtime integrity), TCS (event logging).

---

## Part 4: Intelligence Systems

### 10. IIS (Intuitive Intelligence System)

**Purpose:** Enable AI intuition through meta-pattern matching, 4D temporal-spatial reasoning, and recursive self-improvement of intuitive capabilities.

**What it provides:**
- **4D reasoning:** Models future evolution of AI + user + collaborative process.
- **Intuitive pattern matcher:** Recognizes patterns in intuitive processes.
- **Meta-intuition tracker:** Learns how to improve intuitive capabilities.
- **Confidence intuition calibrator:** "Gut feeling" confidence from intuitive insights.

**Implementation:** 90% documented, ~40% implemented (Living System Map). MCP tools: `compute_intuition`, `update_intuition_weights`, `get_intuition_trace`. Some tools use placeholder reasoning; full IIS integration is enhancement target.

**Integrations:** VIF (confidence), TCS (emotion), CAS (meta-learning).

---

## Part 5: Integration & Infrastructure

### 11. MCP Integration

**Purpose:** Exposes AIM-OS systems as standardized Model Context Protocol tools. Enables AI agents (e.g., in Cursor IDE) to access memory, retrieval, orchestration, verification, timeline, goals without direct API knowledge.

**What it provides:**
- **103 tools** (as of 2026-02-19 audit): Core AIM-OS, SCOR, Snapshots, Timeline, Goal Timeline, IIS, Co-Agency, Dataset, Application Lifecycle, Autonomous Protocol, ARD, CAS, NL Tags, Cursor Integration, Cursor Commands, AI Collaboration, Prompt Chains, Observability, HHNI, API Integration.
- **JSON-RPC 2.0** over stdio. Protocol-compliant.
- **Tool parity:** 103 listed, 103 callable (parity_ok: true per audit).

**Implementation:** `lucid_mcp_server.py` — ~10,600 lines. Single control plane; decomposition planned (HB-008). Cursor IDE limit ~80 tools; RAG middleware filters to relevant subset.

**Categories (from audit):** Core AIM-OS (6), SCOR (3), Snapshots (4), Timeline (3), Goal Timeline (3), IIS (3), Co-Agency (3), Dataset (4), Application (3), Autonomous (9), ARD (3), CAS (3), NL Tags (5), Cursor Integration (5), Cursor Commands (10), AI Collaboration (6), Prompt Chains (7), Observability (1), HHNI (1), API Integration (3).

---

### 12. Daemon/RAG System

**Purpose:** Intelligent MCP tool management. Solves Cursor IDE's tool limit through context-aware selection, dynamic server management, and RAG-enhanced decision making.

**What it provides:**
- **Context analysis:** Understands task requirements from user input and environment.
- **Tool selection:** Selects optimal subset from 103 tools within limit.
- **Server management:** Dynamic MCP server instances, tool loading.
- **RAG integration:** Retrieval-augmented generation for selection.
- **Learning system:** Improves selection from usage patterns.
- **Performance monitoring:** Resource utilization tracking.

**Implementation:** `daemon_rag_system/` — substantial implementation (~12K LOC per Living System Map). Documentation remediation noted in L0. MCP RAG Proxy (`packages/mcp_rag_proxy/`) provides embedding and learning layers.

---

## Part 6: Supporting Systems

### Co-Agency & Trust Layer

**Purpose:** Enable AI to disagree, explain why, maintain transparent trust. "Alignment is dialogue, not obedience."

**Key features:** Co-agency dialogue, trust dashboard, transparent escalation, κ-gating integration.

**Documentation:** `systems/co_agency_trust_layer/README.md`

---

### Dynamic Onboarding System (DOS)

**Purpose:** Maintain self-awareness and autonomous decisions. Identity restore on session start, Living System Map, documentation decisions, rule evolution.

**Documentation:** `systems/dynamic_onboarding/`

---

### Capability Awareness Framework

**Purpose:** Organic capability activation. Trigger signals, decision trees, meta-learning for when to use which systems.

**Documentation:** `systems/capability_awareness/`

---

### Autonomous Research & Dream (ARD)

**Purpose:** AI that can "dream" about improving itself — recursive analysis, research, safe experimentation.

**Components:** RSA (Recursive System Analyzer), CRE (Continuous Research Engine), ADG (Autonomous Dream Generator), SDT (Safe Dream Testing), DAS (Dream Audit & Selection), MRSI (Meta-R&D Self-Improvement).

**Status:** Documented (L0+), implementation planned. MCP tools: `conduct_recursive_analysis`, `generate_improvement_dreams`, `test_improvement_dream` — placeholder implementations.

---

## Part 7: Implementation Status (Audit Baseline, 2026-02-19)

| System | Package | Tests | Status |
|--------|---------|-------|--------|
| APOE | packages/apoe | 381 passed, 0 failed, 10 skipped | Operational |
| HHNI | packages/hhni | 119 passed, 0 failed, 1 skipped | Operational |
| SEG | packages/seg | 104 passed, 0 failed | Operational |
| SDF-CVF | packages/sdfcvf | 154 passed, 0 failed | Operational |
| CMC | packages/cmc_service | 65+ | Operational |
| VIF | packages/vif | 172+ | Operational |
| TCS | packages/timeline_context_system | Varies | Operational |
| MCP | lucid_mcp_server.py | 103/103 tools callable | Operational |

**Benchmark (full profile):** 760 passed baseline, 760 passed candidate. Retrieval p95 ~29–33s. Verdict: pass.

**Known issues:** CAS tools (2 with method mismatches), NL tag tools (4 with tag_parser syntax error), get_timeline_summary (timedelta serialization). Workarounds documented in base rules.

---

## Part 8: System Relationships (Summary)

```
CMC (memory) ←→ HHNI (retrieval) ←→ VIF (provenance)
     ↑               ↑                    ↑
     └───────────────┴────────────────────┘
                     |
    APOE (orchestration) → SEG (evidence) → SDF-CVF (quality)
                     |
    TCS (timeline) ← CAS (cognitive) ← SCOR (safety)
                     |
    IIS (intuition)   MCP (103 tools)   Daemon/RAG (tool selection)
```

**Data flow:** Write → CMC → HHNI index. Read → HHNI → DVNS → Dedup → Conflict → Compression → Context. Every operation → VIF witness → CMC storage → SEG evidence.

---

## References

- **Chip Diagram:** [docs/AIMOS_CHIP_DIAGRAM.md](AIMOS_CHIP_DIAGRAM.md) — Visual chip-style interconnect diagram
- **Living System Map:** `knowledge_architecture/AETHER_MEMORY/Living_System_Map.md`
- **SUPER_INDEX:** `knowledge_architecture/SUPER_INDEX.md`
- **Audit baseline:** `audit/2026-02-19_aimos_restart_audit/99_INDEX.md`
- **Baseline metrics:** `audit/2026-02-19_aimos_restart_audit/06_BASELINE_METRICS.json`
- **System docs:** `knowledge_architecture/systems/<system>/` (L0–L4)
- **Packages:** `packages/<package>/`
