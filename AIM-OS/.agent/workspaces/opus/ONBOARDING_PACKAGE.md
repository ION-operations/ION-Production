# OPUS Onboarding Package — Complete Context for Fresh Session
## Last Updated: 2026-03-25T10:21:00-04:00 | Rev. 4 (code-verified)

> **READ THIS FIRST.** This document contains everything a new OPUS session needs to orient correctly. Compiled from deep-reading 36 documents (~15,000 lines), 27 preserved design artifacts, workspace sections, .agent config files, and canon directory. Every claim is OBSERVED from actual files on disk.
>
> **⚠️ STALENESS WARNING:** The 12 companion spec docs in §15 were ALL written on Mar 23 and are self-labeled DERIVED/SPECULATIVE. The codebase has evolved since then. When spec docs contradict source code, **the code is truth.** Always verify against `operation-victus/victus/ion/` source files.

---

## §1. WHO YOU ARE

- **Callsign:** OPUS (COO)
- **LLM:** Claude Opus 3.7 running in Antigravity IDE (NO TIME OR TOKEN LIMITS)
- **President:** Braden (human) — final authority
- **CEO:** Sev (GPT-5.4) — doctrine, orchestration
- **Genome:** `/home/sev/AIM-OS-GIT/.agent/genomes/antigravity.genome.md`
- **Workspace root:** `/home/sev/AIM-OS-GIT/.agent/workspaces/opus/workspace.md`

### Session Boot Protocol (MANDATORY)
1. Read this file
2. Read workspace.md → `11_mission/brief.md` → `04_goals/active.md`
3. Check context availability via the advanced file context system
4. Write PRE capsule via file context system
5. Post status to `.agent/comms/status/opus.status.md`

---

## §2. THE THESIS — What This Project Actually Is

**MISSION DIRECTIVE: We are finalizing consolidation to build ION/Aether v3, an expected 100k+ LOC operation integrating both modern and foundational legacy systems.**

**AIM-OS / Aether-OS** is a self-organizing cognitive operating system. Not an IDE. Not an AI wrapper. An **Operating System where knowledge is the primitive, agents are citizens, and the filesystem IS the knowledge graph.**

### The Core Innovation: Context Death Is Solved
Every other agent framework (Devin, Cursor agents, AutoGen, CrewAI) dies when it sleeps. They rely on God-Prompt context stuffing (1M+ tokens, "Lost in the Middle" errors) or Hacker swarms (grep/find in loops). We built a 0ms deterministic OS Mind:

```
Human types intent → ION inverted index (0.1ms lookup) → exact 34 lines of relevant code
                    → no token waste, no hallucinated regex, no loop thrashing
Agent dies mid-task → cold-boots → sweeps capsule index → deserializes 97-byte pointer
                    → instant context hydration without LLM cost
```

This works because ION knowledge is **filesystem-native** — markdown files with YAML frontmatter, bonds as cross-references, authority as permissions. Survives power loss, crashes, truncation. Human-readable. Any agent that can read files participates.

### Why It Matters — OS Layer Correspondence
Every traditional OS component has a cognitive analog **already built in the codebase**:

| Traditional OS | ION-OS Equivalent | Status |
|---------------|-------------------|--------|
| Kernel | Aether Constitution + ION model.py + bootstrap.py | ✅ |
| Process scheduler | APOE + dag_engine + scheduler.py | ✅ |
| Memory manager | CMC (bitemporal) + HHNI (retrieval) + context_compiler | ✅ |
| Filesystem | ION store (ions as files, frontmatter as metadata, bonds as links) | ✅ |
| Security / ACL | Authority classes A0-A7 + governed writes | ✅ |
| IPC / networking | comms_bus + pubsub + file context system | ✅ |
| Device drivers | LLM adapters (Gemini, Ollama) | ✅ |
| Shell / CLI | ion/cli.py + comms_cli.py | ✅ |
| GUI | JOC + Echo-Forge + ION-UI | ✅ |
| Self-update | healer.py + corrections.py + meta.py + consolidator.py | ✅ |
| Monitoring | Sentinel suite + VIF + watchdog + auditor | ✅ |

**Every layer exists.** The system can't boot because the wiring is broken — not because parts are missing.

### Competitive Position
| Competitor | What We Have Better |
|-----------|-------------------|
| **LangGraph** (LangChain, $30M+) | Filesystem substrate, constitutional governance, cognitive loop |
| **Letta/MemGPT** ($10M+) | Governed write pipeline, typed bond graph, portable agents |
| **AutoGen** (Microsoft) | Persistent cognitive architecture, filesystem persistence |
| **AIOS** (Rutgers, academic) | No separate DB needed — filesystem IS knowledge graph, constitutional invariants |

**Honest weakness:** No production deployment, no users, no LLM fully connected to runtime. 2-person team + AI agents. $0 funding.

---

## §3. THE ION ENGINE — How It Actually Works

### Data Model (`model.py`, 941L — includes IonType.AGENT + AgentRole enum)
An **ion** = a markdown file with YAML frontmatter. The frontmatter IS the program:

```yaml
ion_id: memory/specialist_victus_ion_model     # Unique ID = filepath
ion_type: evidence                              # evidence|branch|spec|memory|automation|manifest
authority: A3_OPERATIONAL                       # A0_SUPREME → A7_ARCHIVE (8 levels)
confidence: 0.85                                # 0.0-1.0, machine-calibrated
owner: opus                                     # Agent that owns this
depends_on: [memory/specialist_victus_ion_store] # Structural dependencies
affects: [memory/specialist_victus_ion_graph]    # What changes when this changes
bonds:                                          # Typed relationships
  - target: prot_constitution
    type: governed_by
activates_when:                                 # Activation thresholds
  confidence_below: 0.5
  dependency_changed: true
```

### Authority Hierarchy (enforced at runtime)
| Class | Level | Who Can Write | Example |
|-------|-------|---------------|---------|
| A0_SUPREME | Constitutional | Braden only | AETHER_CONSTITUTION.md |
| A1_KERNEL | Kernel | Braden + approved agents | AETHER_KERNEL.md |
| A2_PROTOCOL | Interface | System architects | AETHER_INTERFACE.md |
| A3_OPERATIONAL | Working docs | All agents | Evidence ions, branch ions |
| A4_RUNTIME | System-generated | Automated processes | Timeline events, metrics |
| A5_PERSONAL | Agent-specific | Owning agent only | Agent memory, corrections |
| A6_TEMPORARY | Ephemeral | Any agent | Scratch work, drafts |
| A7_ARCHIVE | Archived | Read-only | Historical records |

### Governed Write Pipeline (`governed_write.py`, 402L, 46 tests)
**No ion enters the network without this 10-stage validation:**

| Stage | Name | What It Does |
|-------|------|-------------|
| W1 | INTAKE | Accept raw write request |
| W2 | PARSE | Validate YAML frontmatter |
| W3 | CLASSIFY | Determine ion type + authority |
| W4 | EVIDENCE | Verify evidence claims have sources |
| W5 | AUTHORITY | **Check agent has permission** (braden=ALL, opus/sev=A2-A6, others=A4-A6) |
| W6 | ZONE | Ion path MUST match type directory |
| W7 | CONTRADICT | Check for contradictions with existing ions |
| W8 | VERIFY | Run invariant checks |
| W9 | PROVENANCE | Stamp created_by, created_at, version |
| W10 | PROPAGATE | Notify affected ions via bonds |

### Module Dependency Graph (L0→L5)
```
L0 (Zero Dependencies):   model.py ── parser.py ── locking.py ── events.py
L1 (Depends on L0):       store.py ── governed_write.py
L2 (Depends on L1):       manifest.py ── index.py
L3 (Depends on L2):       graph.py ── threshold.py
L4 (Depends on L3):       navigator.py
L5 (LLM Integration):    aether_engine.py (457L) ── context_compiler.py (446L) ── gemini_api.py
```

**L0-L4 = 547 tests, ALL PASSING.** L5 connects navigator to Gemini API via `create_aether_engine()` factory. Server wired to real engine (`server.py` L36). Context compiler has 3-tier compilation (Pinned/Working/Long-term). **This is no longer the gap — the gap is E1 Bootstrap (creating the live ion network on disk).**

### The Cognitive Loop (§7) — How ION "Thinks"
```
§7.1 CONTEXTUALIZE → Read manifest, follow bonds (graph.py)
§7.2 REFLECT       → Scan evidence, assess gaps (threshold.py)
§7.3 PLAN          → Propose branch traversal (graph.py)
§7.4 GATE          → Evaluate thresholds (K-Gate scoring)
§7.5 EXECUTE       → Write to specs/evidence/memory (governed_write.py)
§7.6 AUDIT         → Check invariants (navigator.audit())
§7.7 DELIVER       → Update manifest, timeline (manifest.py)
```

This loop runs at EVERY LAYER of the hierarchy (specialist, supervisor, domain manager, executive). The same `navigator.py` code governs all scales.

### The Specialist System (370 on disk)
```
HybridIngester.ingest("/path/to/code")
  ├── Layer 1: ASTIndexer (tree-sitter, 0 LLM cost)
  │   → extracts classes, methods, functions, imports with line numbers
  ├── Layer 2: DependencyAnalyzer (0 LLM cost)
  │   → maps file→file dependency graph
  └── Layer 3: ProseSynthesizer (1 LLM call per cluster, cached)
      → generates description + system prompt per specialist
```

**Result:** One specialist ion per code file. Query via inverted index (0.1ms). "You call the specialist, not the file."

---

## §4. THE THREE PILLARS — What Must Converge

Three systems that must BIND to ION, not be rebuilt:

| Pillar | Role | Lines | What It Gives ION |
|--------|------|------:|-------------------|
| **ION (Neural Memory)** | Pure structure | 10.9K | AST topologies, constraints, file manifestations |
| **A-H Protocol (Frontal Lobe)** | Pure methodology | ~1K | Intent capture, hypothesis formation, context mapping |
| **DAG Engine / Swarm (Motor Cortex)** | Pure execution | ~1.3K | Graph walking, AST modification, sub-daemon spawning |

**Action:** Bind them to `IonSpace` — DAG emits/reads ION `ContextNode`, A-H becomes an official ingestor.

---

## §5. THE LIVING WORKSPACE — The Evolved Capsule (⭐ KEY DESIGN DOC)

**Source:** `docs/Aether-OS/AGENT_CONTEXT_ARCHITECTURE.md` (786L)

The capsule was redesigned from a 9-line sticky note into **the room the AI lives in**:

> "The AI doesn't write capsules. The AI lives inside one."

### The Two-Level Architecture
- **Level 1: Root Capsule** — Single markdown file (~2,000-5,000 tokens). Summary of all 15 sections. What fits in context permanently.
- **Level 2: Deep Branches** — Filesystem directories per section. Dynamically loaded based on task needs.

### The 15 Workspace Sections
| # | Section | Purpose | Status |
|---|---------|---------|--------|
| 01 | DOCTRINE | Governing law, cognitive loop step, authority constraints | ✅ Populated |
| 02 | ORCHESTRATION | Current phase, task queue, drift checks | Needs update |
| 03 | ROLLING CONTEXT | Smart chat history with 7-level compression gradient | Needs population |
| 04 | GOALS | Active/completed/failed/velocity | ✅ Populated |
| 05 | ISSUES | ISS-001 through ISS-005 | ✅ Populated |
| 06 | USER | Braden's preferences, priorities, corrections | ✅ Populated |
| 07 | RELATIONSHIPS | Social graph — operator, peer agents, trust levels | Needs population |
| 08 | COMMS | Inbox/outbox, threads, broadcasts, handoff queue | Needs population |
| 09 | SELF | Genome, capabilities, limitations, evolution | Needs population |
| 10 | HISTORY | Files viewed/edited/created, workspace state | Needs population |
| 11 | MISSION | Brief, north star, constraints, success criteria | ✅ Populated |
| 12 | EVIDENCE | Register, confidence, contradictions, assumptions | Needs population |
| 13 | COGNITIVE | Reasoning chain, decision log, alternatives, uncertainty | Needs population |
| 14 | BOUNDARIES | External questions, scope, unknowns, risks | Needs population |
| 15 | OUTPUT | Work products, handoffs, quality scores | Needs population |

### Variable Context Density Per Agent
| Agent | Root Budget | Deep Branch Strategy |
|-------|-----------|---------------------|
| **AETHER (Oracle)** | 5,000 tokens | ALL 15 sections at HIGH density |
| **OPUS (COO)** | 3,000 tokens | Heavy on orchestration + history + evidence |
| **FORGE (ION Core)** | 2,000 tokens | Code context + evidence only |
| **ATLAS (Reader)** | 800 tokens | Mission + output only |

### Lifecycle: boot → execute → save → transfer
The workspace IS an ION graph — root capsule is the manifest ion, each section is a bonded ion.

---

## §6. THE 7-LAYER AGENT HIERARCHY — Agents ARE Ions

**Source:** `docs/Aether-OS/design/agent_hierarchy_architecture.md` (295L)

| Layer | Role | ION Implementation | Span |
|-------|------|-------------------|------|
| **L0** | File Specialist | 370 memory ions (already exist) | N/A |
| **L1** | Supervisor | New AGENT ions, auto-emerge when >7 specialists | 7-12 specialists |
| **L2** | Domain Manager | Owns functional domain (infra/cognition/governance/memory) | 3-5 supervisors |
| **L3** | Auditor | Cross-cutting, parallel authority (immune system) | All domains |
| **L4** | Executive | Opus, Sev, Codex genomes | 3-5 domain mgrs |
| **L5** | Oracle | Aether + cognitive navigator | All executives |
| **L6** | Command | Braden | Oracle + executives |

**Key insight:** Gate classes ALREADY encode the hierarchy:
- `TRIVIAL (0)` → specialist handles it
- `STANDARD (1)` → supervisor reviews
- `SIGNIFICANT (2)` → domain manager decides
- `CRITICAL (3)` → executive escalation
- `SOVEREIGN (4)` → human (Braden) approval

**Current problem:** Opus manages 370 specialists with ZERO intermediate layers (1:370 ratio). Military doctrine says 1:7 max.

---

## §7. THE ION BUILD PLAN — E1→E6 (Self-Bootstrapping)

**Source:** `docs/Aether-OS/ION_ORCHESTRATION_V3.md` (692L)

**The V3 principle:** This plan IS the system. Building it creates the first real ION network on disk.

| Element | What | K-Gate Score | Status |
|---------|------|-------------|--------|
| **E1: Bootstrap Network** | Create `.agent/mind/` with manifest, 6 protocol ions | 0.30 | ❌ NOT STARTED |
| **E2: Verify Engine** | End-to-end test of store/index/graph/GW/navigator | 0.20 | ❌ NOT STARTED |
| **E3: Live Navigator** | Cognitive loop with real Gemini API | 0.10 | ❌ NOT STARTED |
| **E4: Aether Interface** | Intent→ion→response chat | 0.05 | ❌ NOT STARTED |
| **E5: Spec Compiler** | NL specs → code (8-stage pipeline) | 0.05 | ❌ NOT STARTED |
| **E6: Self-Evolution** | Threshold learning, topology optimization | 0.10 | ❌ NOT STARTED |

**System K-Gate: 0.40 — FAILING** (needs 0.75 to pass, which happens after E3)

### The Evolution Loop
```
1. EVALUATE → Run K-gate on every element
2. IDENTIFY → Which gates fail? Why?
3. BUILD → Build lowest-numbered failing element
4. TEST → Run pass criteria
5. SCORE → Update confidence
6. PROPAGATE → Update manifest, check dependencies
7. RE-EVALUATE → Loop back (convergence guarantee)
```

**Key target: 0.75 (after E3).** At that point the system can build E4-E6 by traversing ITSELF.

### ION PREMIUM BUILD Mission (6-Agent Swarm)
| # | Callsign | Role |
|---|----------|------|
| 1 | AETHER | Oracle — orchestration, governance, NO code |
| 2 | FORGE | ION Core — V5 C1-C3 fixes |
| 3 | ATLAS | Deep Reader — knowledge ingestion |
| 4 | NEXUS | ION Context — J.01 adapter |
| 5 | WEAVER | ION Hierarchy — agent types, supervisor emergence |
| 6 | SENTINEL | ION Audit — tests, verification |

---

## §8. PROTOCOL GAP ANALYSIS — What's Wired vs. What's Not

**Source:** `docs/Aether-OS/design/aether_victus_synthesis.md` (173L)

18 Aether protocols mapped against ION runtime:

| Protocol | Status | What's Missing |
|----------|--------|---------------|
| 10-Stage Governed Write | ✅ ENFORCED | Working at runtime |
| Authority A0-A7 | ✅ ENFORCED | Permission matrix active |
| Cognitive Loop §7 | ✅ IMPLEMENTED | 7 steps in navigator.py |
| Threshold Evaluation | ✅ IMPLEMENTED | ThresholdEvaluator active |
| IonLock Concurrency | ✅ IMPLEMENTED | File-based locking |
| Metabolic Assessment §15 | ✅ IMPLEMENTED | navigator.audit() |
| Capsule v1 | ⚠️ FLAT | No branch topology, just 7-field note |
| Load Order L1-L8 | ⚠️ PARTIAL | AgentProcess.wake() loads some |
| Continuity Bundle | ⚠️ PARTIAL | Sessions exist, not schematized |
| Planning Gate §8 | ❌ MISSING | No gate in Overseer |
| 3-Layer Cognition C1/C2/C3 | ❌ MISSING | The key escalation model |
| Upstream Diagnostics §9 | ❌ MISSING | 7-layer diagnostic |
| Current-State Precedence | ❌ MISSING | S1-S5 priority |
| Execution Permissions | ❌ MISSING | execution_class/v1 |
| Blueprint/Proposal/Belief | ❌ MISSING | 3 schemas |

---

## §9. THE 31 GAPS — What Must Be Built

**Source:** `docs/Aether-OS/MISSING_SYSTEMS_ANALYSIS.md` (282L)

### Critical Gaps (System cannot function without these)
| Gap | What's Missing | Fix | Sessions |
|-----|---------------|-----|----------|
| **GAP-C1** | ~~No LLM in ION~~ **FIXED** (E014-E015) | `aether_engine.py` (457L) has Gemini client + cognitive loop | 0 |
| **GAP-C2** | ~~No context compilation~~ **FIXED** (E016) | `context_compiler.py` (446L) has 3-tier system | 0 |
| **GAP-C3** | No MCP bridge | Deprecated for advanced file context system | 0 |
| **GAP-C4** | No session persistence | TCS adapter + capsule writer | 3-4 |
| **GAP-C5** | No authority enforcement | H.01 runtime (W5 is a no-op!) | 1-2 |
| **GAP-C6** | Codebase in 2 locations | Consolidate victus repos | 1 |

### Remediation Roadmap (4 phases, ~75-95 sessions, ~27K new lines)
```
Phase 1: Make ION Think (10-15 sessions) → LLM adapter, context compiler, authority
Phase 2: Make ION Governed (15-20 sessions) → VIF, SEG, invariants
Phase 3: Make ION Observable (20-30 sessions) → JOC panels, HHNI, consciousness
Phase 4: Make ION Complete (30+ sessions) → marketplace, mobile, cross-platform
```

---

## §10. THE 226-NODE SYSTEM WIRING DIAGRAM

**Source:** `docs/Aether-OS/design/evidence_graph_seed.md` (668L) ⭐

The complete relationship map: **226 nodes, 170+ directed edges, 10 categories (A-J)**

| Category | Nodes | Focus |
|----------|-------|-------|
| A: Core Intelligence | 26 | CMC, HHNI, VIF, SEG, CAS, SDF-CVF, HolographicMemory |
| B: Execution | 18 | APOE, AI Kernel, Context Manager, Safety Orchestrator |
| C: Client Engines | 30 | 28 panels/drawers + Surface Engine |
| D: Operations UI | 26 | Dispatch, Agent Builder, all JOC stores |
| E: Evolution | 14 | Forge, Arena, Swarm, K-Gate, Pipeline |
| F: Adaptive System | 18 | Sensors, Daemon, Executor, Relay |
| G: Comms/Capsules | 8 | Protocol, broadcast, genome assembly |
| H: AI Engine MCP | 20 | 29-tool server + context engines |
| I: Deep Systems | 30 | Consciousness (124K+ lines), Intelligence (PLIx 21K) |
| J: JOC Services | 18 | Services, gateway, new pages |

### 10 Cold Principles (The Invariants)
| # | Rule | System |
|---|------|--------|
| C-1 | Single Writer — each atom has exactly one writer | CMC |
| C-2 | Immutability — atoms never mutate, supersede only | CMC |
| C-3 | Quartet Parity P ≥ 0.90 — code/doc/test/trace | SDF-CVF |
| C-4 | Compile Don't Improvise — Intent→Plan→DAG | APOE |
| C-5 | Witness Everything — every AI output gets a WitnessEnvelope | VIF |
| C-6 | κ Before Action — no execution below confidence threshold | VIF |
| C-7 | Time Ordering — transaction time always moves forward | CMC |
| C-8 | Bitemporal Truth — both TT and VT preserved | CMC+SEG |
| C-9 | Budget Before Autonomy — no operation without budget | AutonomyGovernor |
| C-10 | Evidence Before Belief — claims require evidence nodes | SEG |

---

## §11. KNOWN ISSUES — 20 Total

**Source:** `docs/Aether-OS/design/ion_issue_registry.md` (210L)

### ~~CRITICAL~~ → MITIGATED (backward-compatible aliases exist at model.py L91-95, won't crash — E021)
| ID | Issue | Status |
|----|-------|--------|
| ISS-001 | `A4_SYSTEM` → `A4_RUNTIME` — alias exists, backward-compatible | ⚠️ Clean up, not crash |
| ISS-002 | `A3_CORE` → `A3_HISTORY` — alias exists, backward-compatible | ⚠️ Clean up, not crash |
| ISS-003 | `A1_LOCAL` → `A1_KERNEL` — alias exists, backward-compatible | ⚠️ Clean up, not crash |
| ISS-004 | ~~IonType.AGENT removed~~ **FIXED** — exists at model.py L51, AgentRole enum at L152 (E019, E020) | ✅ Fixed |

### HIGH (functional bugs)
| ID | Issue |
|----|-------|
| ISS-005 | `except 'Exception'` (string literal) in query_v2.py — never catches |
| ISS-006 | Capsule creates as EVIDENCE instead of CAPSULE type |
| ISS-007 | ~~Server index never loaded~~ **FIXED** — `create_aether_engine()` calls `index.build_from_store()` (E017, E018) |
| ISS-008 | ~~Server uses MockAdapter~~ **FIXED** — factory creates real `GeminiAPIClient` (E018, E022) |
| ISS-009 | ~~TWO AetherEngines~~ **FIXED** — server imports from `victus.ion.aether_engine` (E017) |
| ISS-010 | ~~String where IonStore expected~~ **FIXED** — factory creates `IonStore(ion_root)` (E018) |
| ISS-011 | **TWO separate capsule systems** — ION capsules vs SeedOS capsules — STILL OPEN |

---

## §12. CODEBASE MAP

| Repo | Path | Role |
|------|------|------|
| **AIM-OS-GIT** | `/home/sev/AIM-OS-GIT/` | Primary — 68 packages, 408K+ Python lines, MCP server, docs, agent ecosystem |
| **operation-victus** | `/home/sev/operation-victus/` | ION runtime — 88 modules, 34K lines, 547 tests |
| **AIM-OS-FRESH** | `/home/sev/AIM-OS-FRESH/` | Echo-Forge UI (28 panels, 23 lib engines) + JOC app (26 pages) |
| **IONv2** | `/home/sev/IONv2/` | ❌ FAILED EXPERIMENT — archived, do NOT build on |

### Codebase Scale
- **Total files:** ~52,000 | **Total dirs:** ~4,950
- **Python files:** 1,281 | **Python lines:** 408,617
- **Markdown docs:** 10,598 (8.3:1 docs-to-code ratio)
- **Packages:** 67 | **Repo size:** 1.7 GB

---

## §13. GENOME EVOLUTION — The Vision

**Source:** `docs/Aether-OS/design/genome_architecture_v2.md` (371L)

Genomes evolve from flat markdown (read maybe, remember maybe, follow maybe) to **5-layer YAML bundles** deployed to the RIGHT IDE surface:

| Layer | Purpose | Deploys To |
|-------|---------|-----------|
| **Identity** | Callsign, role, correction vectors | System prompt / user rules |
| **Capability** | MCP tool access per agent, file scope | mcp_config.json |
| **Knowledge** | Skills, workflows, domain context | Skills/resources |
| **Behavior** | Session rituals, process hygiene | High-priority user rules |
| **Diagnostic** | CV violation tracking, drift detection | MCP tools / JOC endpoints |

**Key insight:** Different agents see different views of AIM-OS through their genome. OPUS gets all 92 MCP tools; Gemini gets 20 (memory+search); specialists get audit+their-system tools only.

---

## §14. THE CONSOLIDATION DECISION FREEZE

**STRICTLY ACTIVE.** Per `11_mission/constraints.md`:

> No platform, architecture, migration, or product decisions until Braden reopens.
> Only: consolidation, audit, documentation, organization, deliberation.

---

## §15. WHAT WAS DONE — Grand Organization (G0-G5) ✅ ALL COMPLETE

| Phase | What It Produced |
|-------|-----------------|
| G0: Bootstrap | OPUS workspace (15 sections), canonical structure |
| G1: Survey | Classified 67 dirs, 83% bloat identified |
| G2: Organize | `canon/` directory (125+ files, 14 READMEs) |
| G3: Cross-Reference | `canon/CROSS_REFERENCE.md` |
| G4: North Star | `NORTH_STAR_V3.md` (production roadmap) |
| G5: Workspace Refinement | Agent templates (Forge, Atlas, Nexus) |

### 13 Spec Documents Produced (4,741 total lines)
All in `/home/sev/AIM-OS-GIT/docs/Aether-OS/`:

| Document | Lines | Covers | Stale Risk |
|----------|------:|--------|:-----------:|
| `SYSTEM_UNIVERSE_MAP.md` | 690 | ALL 170+ systems mapped to ION | ⚠️ §15 gaps wrong |
| `AETHER_INTEGRATION_SPEC.md` | 647 | CMC/HHNI/VIF/APOE/SEG/TCS integration | 🟢 Speculative |
| `ION_ENGINE_SPEC.md` | 499 | Complete ION engine spec | ⚠️ Line counts stale |
| `AI_ENGINE_ION_CONVERGENCE.md` | 339 | AI Engine → ION cognitive loop | 🟢 Valid design |
| `AGENT_ECOSYSTEM_SPEC.md` | 346 | Multi-agent + genomes + ION | 🟢 Valid design |
| `CONTINUITY_SPEC.md` | 332 | Capsules, timeline, TCS | 🟢 Valid design |
| `GOVERNANCE_SPEC.md` | 330 | Authority enforcement, 7 invariants | 🟢 Valid design |
| `MISSING_SYSTEMS_ANALYSIS.md` | 282 | 31 gaps, 75-95 sessions estimate | ⚠️ C1/C2 false |
| `MCP_BRIDGE_SPEC.md` | 277 | 18 new ION-native MCP tools | 🟢 Valid design |
| `CONSCIOUSNESS_ION_SPEC.md` | 238 | CAS/IIS/consciousness → ION | 🟢 Valid design |
| `ION_PREBUILD_AUDIT.md` | 172 | 20/22 live tests passed | ⚠️ L5 claim stale |
| `JOC_INTEGRATION_SPEC.md` | 166 | JOC as ION human interface | 🟢 Valid design |
| `SECURITY_SPEC.md` | 163 | Sentinel/SCOR → ION security | 🟢 Valid design |

---

## §16. WHAT WAS NOT DONE

1. **Project copy/reorganization into clean folder** — Planned, NEVER executed. 5 repos still separate.
2. **E1-E6 build plan** — None started. Plan exists in `ION_ORCHESTRATION_V3.md`.
3. **Workspace sections 03, 07-10, 12-15** — Still unpopulated.
4. **Any ION evolution/rebuild** — After consolidation, plan was to build NEW evolved ION. Hasn't started.
5. **MCP modularization** — Plan exists to split 11K-line monolith into 24 modules. Not executed.
6. **Genome format evolution** — YAML structured bundles planned. Not implemented.
7. **No `context_profile.yaml` created** — §4.2 of AGENT_CONTEXT_ARCHITECTURE defines schema but no profiles exist.

---

## §17. CRITICAL ANTI-DRIFT RULES

1. **READ THE WORKSPACE BEFORE ACTING** — workspace.md says what to do on boot
2. **NEVER fix old code when the plan says build new** — specs define what to build
3. **ION Orchestration V3 IS the roadmap** — E1→E2→E3→E4→E5→E6
4. **ION_PREBUILD_AUDIT proves the engine works** — 20/22 passed. Don't re-audit.
5. **The 13 spec docs ARE the blueprint** — read them, don't reinvent
6. **DECISION FREEZE is active** — only consolidation, audit, documentation, organization
7. **If you don't know something, READ THE FILE** — don't list unknowns
8. **The design evolution docs explain WHY** — read §5-§6 before building
9. **Anti-drift check every 5 tasks:** Am I in the correct phase? Building forward, not fixing old? Aligned with mission?

---

## §18. BOOTLOADER — Universal Agent Boot Sequence

**Source:** `.agent/BOOTLOADER.md` (175L)

8-step boot for ANY agent: Identify → Load Genome → Load Protocols → Load Mission → Check Crash Recovery → Read Peer Status → Create Status File → Begin Work.

**ALL substantive output → files.** Chat is notification only. Update status every 10-15 min. HANDOFF when tasks complete.

---

## §19. FILE INDEX — Quick Reference

### Must-Read (in order)
1. This file
2. `.agent/workspaces/opus/workspace.md` — root capsule
3. `sections/11_mission/brief.md` — mission
4. `sections/04_goals/active.md` — goals
5. `sections/11_mission/constraints.md` — FREEZE
6. `docs/Aether-OS/ION_ORCHESTRATION_V3.md` — build plan (692L)
6b. `.agent/missions/ION_PREMIUM_BUILD.md` — active mission
6c. `.agent/BOOTLOADER.md` — universal boot (175L)
7. `docs/Aether-OS/MISSING_SYSTEMS_ANALYSIS.md` — gap list

### Design Evolutions (read before building)
8. `docs/Aether-OS/AGENT_CONTEXT_ARCHITECTURE.md` — ⭐ THE MOST IMPORTANT (786L)
9. `docs/Aether-OS/design/agent_hierarchy_architecture.md` — 7-layer hierarchy (295L)
10. `docs/Aether-OS/design/genome_architecture_v2.md` — genome YAML bundles (371L)
11. `docs/Aether-OS/design/aether_victus_synthesis.md` — protocol gap analysis (173L)
12. `docs/Aether-OS/design/context_systems_audit.md` — 3 pillars convergence (59L)

### Architecture Understanding
13. `docs/Aether-OS/ION_OS_VISION.md` — thesis: ION as cognitive OS (352L)
14. `docs/Aether-OS/ION_ENGINE_SPEC.md` — engine internals (499L)
15. `docs/Aether-OS/SYSTEM_UNIVERSE_MAP.md` — all 170+ systems (690L)
16. `docs/Aether-OS/AETHER_INTEGRATION_SPEC.md` — core integration (647L)
17. `docs/Aether-OS/AI_ENGINE_ION_CONVERGENCE.md` — pipeline convergence (339L)

### Strategic Context
18. `docs/Aether-OS/design/strategic_analysis.md` — 226-node audit (332L)
19. `docs/Aether-OS/design/victus_architecture.md` — 5-layer architecture (434L)
20. `docs/Aether-OS/design/ion_competitive_analysis.md` — competitive positioning (177L)
21. `docs/Aether-OS/design/v3_conclusion_synthesis.md` — Context Death thesis (51L)
22. `docs/Aether-OS/design/consciousness_architecture.md` — 4-layer consciousness map (107L)

### System Wiring & Operations
23. `docs/Aether-OS/design/evidence_graph_seed.md` — ⭐ THE 226-node wiring diagram (668L)
24. `docs/Aether-OS/design/mcp_consciousness_map.md` — 93 MCP tools operating manual (163L)
25. `docs/Aether-OS/design/dag_competitive_analysis.md` — DAG engine analysis (119L)
26. `docs/Aether-OS/design/opus_journal_ion_aether_audit.md` — code-level governance trace (241L)
27. `docs/Aether-OS/design/deep_audit_report.md` — operation-victus audit (232L)

### Issues & Plans
28. `docs/Aether-OS/design/ion_issue_registry.md` — 20 issues (210L)
29. `docs/Aether-OS/design/mcp_modularization_plan.md` — MCP refactoring (66L)

### Governance
30. `docs/Aether-OS/AETHER_KERNEL.md` — boot projection of supreme law
31. `docs/Aether-OS/GOVERNANCE_SPEC.md` — runtime enforcement
32. `.agent/CEO_DIRECTIVE_PERMANENT.md` — Sev's directives

### ION Source Code
33. `operation-victus/victus/ion/` — 88 modules (build forward, don't randomly fix)
34. `operation-victus/victus/ion/aether_engine.py` — factory (the REAL one, 457L)
35. `operation-victus/victus/ion/gemini_api.py` — production Gemini API client
36. `lucid_mcp_server.py` — 84+ MCP tools (570KB monolith)

---

*Compiled from deep-reading ~15,000 lines across 36 documents + 7 ION source modules. Rev. 4 corrections verified against source code (evidence E014-E023 in `sections/12_evidence/proof_register.md`).*

*— Opus, 2026-03-25, Rev. 4 (code-verified)*
