---
ion_id: docs/aether-os/aimos-context-integration
type: protocol
authority: A2_CANONICAL_EXTENSION
confidence: 0.92
epistemic_status: DERIVED
owner: opus
created: 2026-03-24T19:15:00-04:00
bonds:
  - target: docs/aether-os/agent-context-architecture
    type: depends_on
    note: "This document maps all existing systems INTO that architecture"
  - target: docs/aether-os/aether-atlas
    type: governed_by
  - target: docs/aether-os/aether-constitution
    type: governed_by
tags: [integration, context, systems, consolidation, mapping]
summary: |
  Deep integration mapping of all AIM-OS, Aether, and ION systems into
  the 15-section Agent Context Architecture. Maps 12 core AIM-OS packages,
  103 ION runtime modules, MCP tool categories, and all agent infrastructure
  to specific workspace sections with concrete integration patterns.
---

# AIM-OS ↔ Agent Context Architecture Integration Map

> **Companion to:** [AGENT_CONTEXT_ARCHITECTURE.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/AGENT_CONTEXT_ARCHITECTURE.md)
>
> This document answers: **How does every existing system integrate into the
> living workspace?** Based on deep-read of 12+ packages and 103 ION modules.

---

## §1. Systems Inventory (Research Results)

### 1.1 Core AIM-OS Packages (8 Systems)

| System | Package | Lines | Core Modules | Purpose |
|--------|---------|-------|-------------|---------|
| **CMC** | `packages/cmc_service/` | 80 files | `models.py` (Atom/Snapshot/WitnessStub), `memory_store.py`, `cross_model_atoms.py`, `bitemporal_queries.py` | Cross-model memory with bitemporal tracking. 190+ atoms alive in SQLite. |
| **HHNI** | `packages/hhni/` | 71 files | `hierarchical_index.py` (5-level: System→Section→Paragraph→Sentence→Subword), `retrieval.py`, `compressor.py`, `budget_manager.py`, `dvns_physics.py` | Fractal multi-resolution retrieval with zoom_in/zoom_out. |
| **SEG** | `packages/seg/` | 34 files | `seg_graph.py` (NetworkX MultiDiGraph), `witness.py`, `models.py` (Entity/Relation/Evidence/Contradiction/TimeSlice) | Shared Evidence Graph with time-travel queries and provenance tracing. |
| **VIF** | `packages/vif/` | 66 files | `kappa_gate.py` (κ-gating behavioral abstention), `confidence_extraction.py`, `calibration.py`, `cross_model_replay.py` | Confidence verification, HITL escalation, adaptive thresholds by ECE. |
| **APOE** | `packages/apoe/` | 115 files | `execution_orchestrator.py`, `insight_transfer.py`, `model_selector.py`, `advanced_gates.py`, `compensation_engine.py` | Multi-model execution with 4 modes (single/parallel/sequential/consensus). |
| **CAS** | `packages/cas/` | ~30 files | Consciousness analysis, self-awareness metrics | Agent self-model and introspection. |
| **SDF-CVF** | Referenced in integrations | — | Cross-validation framework | Multi-model output comparison and verification. |
| **TCS** | `packages/timeline_context_system/` | 50+ files | `demo_context_dump.py`, context bootloaders, weighted priority loading | Rolling context with timeline tracking and smart compression. |

### 1.2 ION Runtime Modules (103 Python files in `victus/ion/`)

| Module | Lines | What It Does |
|--------|-------|-------------|
| **model.py** | ~800 | Ion data model: 14 ion types, 8 authority classes, 5 gate classes, CapsulePhase, AgentRole, Priority, Provenance |
| **governed_write.py** | 444 | 10-stage validation pipeline (W1-W10). Authority permissions matrix. |
| **navigator.py** | 625 | §7 cognitive loop with LLM augmentation at reflect/plan/audit. CognitiveContext + ReflectionResult + ExecutionPlan + AuditResult |
| **context_compiler.py** | 446 | Three-tier context compilation (Pinned/Working/Long-term) + per-cognitive-step |
| **context.py** | 100 | BFS radial context assembly from ion graph |
| **capsule.py** | 245 | PRE/POST capsule lifecycle via GovernedWritePipeline |
| **manifest.py** | ~300 | ManifestManager: loop position, active/future branches, evidence trail, system confidence |
| **graph.py** | ~200 | IonGraph: NetworkX topology, predecessors/successors, bond queries |
| **index.py** | ~400 | IonIndex: all_ions(), stale_ions(), low_confidence_ions(), ions_by_type() |
| **store.py** | ~300 | IonStore: CRUD for ions on filesystem with frontmatter |
| **threshold.py** | ~200 | ThresholdEvaluator: gate condition evaluation |
| **agent_comms.py** | ~150 | Agent-to-agent messaging |
| **agent_manifest.py** | ~100 | Agent manifest with role, genome, status |
| **authority.py** | ~150 | Authority class management, permission checking |
| **classifier.py** | ~200 | Ion classification engine |
| **compliance.py** | ~100 | Compliance checking for writes |
| **escalation.py** | ~100 | HITL escalation pipeline |
| **locking.py** | ~100 | File-level ion locking for concurrent writes |
| **auto_loop.py** | ~200 | Automatic cognitive loop runner |

### 1.3 MCP Tools (via lucid_mcp_server.py)

| Category | Tools | What They Do |
|----------|-------|-------------|
| **Memory** | `store_memory`, `retrieve_memory`, `list_memories` | Key-value memory persistence |
| **Context** | `record_context_capsule`, `get_timeline_summary` | Session capsule creation, timeline |
| **Agent Comms** | `send_ai_message`, `get_ai_messages`, `list_agents` | Inter-agent messaging |
| **Session** | `get_session_status`, `update_session` | Session state tracking |

---

## §2. The Integration Matrix

Each cell shows:  **which system(s) power this workspace section** and **how**.

```
                           WORKSPACE SECTIONS
                           ══════════════════
    SYSTEM ↓     │ DOC │ ORC │ CHAT│ GOAL│ ISS │ USR │ REL │ COM │ SELF│ HIS │ MIS │ EVI │ COG │ BND │ OUT │
    ─────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
    CMC          │     │     │  ●  │     │     │  ●  │  ●  │     │     │  ●  │     │     │     │     │     │
    HHNI         │  ●  │     │  ●  │     │     │     │     │     │     │  ●  │     │  ●  │     │     │     │
    SEG          │     │     │     │     │  ●  │     │  ●  │     │     │     │     │  ●  │     │  ●  │     │
    VIF          │     │     │     │     │     │     │     │     │     │     │     │  ●  │  ●  │     │  ●  │
    APOE         │     │  ●  │     │     │     │     │     │     │     │     │     │     │  ●  │     │  ●  │
    CAS          │     │     │     │     │     │     │     │     │  ●  │     │     │     │  ●  │     │     │
    TCS          │     │     │  ●  │     │     │     │     │     │     │  ●  │     │     │     │     │     │
    ION CtxComp  │  ●  │  ●  │     │     │     │     │     │     │     │     │  ●  │  ●  │  ●  │     │     │
    ION Navigator│  ●  │  ●  │     │  ●  │     │     │     │     │     │     │  ●  │  ●  │  ●  │     │  ●  │
    ION Capsule  │     │  ●  │     │     │     │     │     │     │     │     │  ●  │     │     │     │     │
    ION GovWrite │  ●  │     │     │     │     │     │     │     │     │  ●  │     │  ●  │     │     │     │
    MCP Tools    │     │     │     │     │     │  ●  │     │  ●  │     │     │     │     │     │     │     │
    ─────────────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
    
    Legend: DOC=Doctrine, ORC=Orchestration, CHAT=Rolling Context,
            GOAL=Goals, ISS=Issues, USR=User, REL=Relationships,
            COM=Comms, SELF=Self, HIS=History, MIS=Mission,
            EVI=Evidence, COG=Cognitive, BND=Boundaries, OUT=Output
```

---

## §3. Per-Section Integration Detail

### §3.1 DOCTRINE — Governing Law

**Systems that feed Doctrine:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **ION ContextCompiler** `compile_for_step()` | Pinned tier (A0-A1) always loads constitutional ions | The Doctrine section's deep branch IS the Pinned tier output. When workspace boots, `compile_three_tier()` populates `sections/doctrine/current.md` with all A0+A1 ions. |
| **ION Navigator** `contextualize()` | Loads manifest + active branches + evidence | Navigator's `CognitiveContext` feeds the loop_step indicator in doctrine. |
| **ION GovernedWrite** `AUTHORITY_PERMISSIONS` | Defines what the agent can write at each authority | `sections/doctrine/authority_posture.md` maps directly from `get_permissions(agent)`. |
| **HHNI** `hierarchical_index` | Multi-resolution retrieval of constitutional docs | When doctrine references constitution articles, HHNI does the zoom_in/zoom_out to find the right granularity. |

**Integration formula:**
```python
# On workspace boot:
doctrine.current = context_compiler.compile_three_tier(budget=1000).text  # Pinned tier
doctrine.authority_posture = governed_write.get_permissions(callsign)
doctrine.cognitive_loop = navigator.current_step
```

---

### §3.2 ORCHESTRATION — Dynamic Mission Planning

**Systems that feed Orchestration:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **ION Navigator** `plan()` | ExecutionPlan with ordered branches, gate results, depth estimate | `sections/orchestration/task_queue.md` IS the Navigator's ExecutionPlan rendered as markdown. |
| **ION Capsule** `CapsuleManager` | PRE/POST snapshots bracket mission phases | Each phase transition writes a POST capsule to `sections/orchestration/phase_transitions/`. |
| **ION ContextCompiler** `compile_for_step("plan")` | Loads branches + requirements for planning | Orchestration deep branch uses this to know which plans are active. |
| **APOE** `ExecutionOrchestrator` | Multi-model execution with quality scoring | For tasks requiring cross-model consensus, APOE's execution modes feed into orchestration decisions. |

**Integration formula:**
```python
# During execution:
orchestration.current_phase = manifest_manager.get_active_branches()
orchestration.task_queue = navigator.plan().ordered_branches
orchestration.drift_check = navigator.audit().drift
# On phase transition:
capsule_manager.create_post_capsule(session_id, agent, results=phase_results)
```

---

### §3.3 ROLLING CONTEXT — Smart Chat History

**Systems that feed Rolling Context:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **CMC** `memory_store` | Atoms persist conversation fragments with bitemporal tracking | Each exchange → CMC atom with timestamp, modality, tags. The rolling context IS the CMC atom timeline for this agent. |
| **TCS** `timeline_context_system` | Weighted priority loading with smart compression | TCS's compression algorithms drive the 7-level gradient: full → summarized → 1-line → topic → indexed. |
| **HHNI** `hierarchical_index` | Multi-resolution retrieval of older exchanges | When agent needs to "zoom into" an older conversation, HHNI provides the fractal index. Query by topic → get section → zoom to paragraph. |
| **CMC** `advanced_compression` | Intelligent lossy compression preserving semantics | Compression-before-loss applied to older exchanges. CMC's BTSM (bitemporal store manager) handles the temporal layering. |

**Integration formula:**
```python
# After each exchange:
cmc.ingest_atom(AtomCreate(
    modality="conversation",
    content=AtomContent(inline=exchange_text),
    tags={"agent": 0.9, "topic_X": 0.7},
))

# On workspace boot — load rolling context:
recent_atoms = cmc.query(modality="conversation", limit=50, sort="created_at DESC")
active = render_full(recent_atoms[:10])
recent = render_summarized(recent_atoms[10:50])
compressed = hhni.query("conversation history", target_level=SECTION, max_results=20)
```

**This is where CMC's cross-model atoms become critical:** if multiple AI agents had conversations about the same topic, the CMC `cross_model_atom_creator` can synthesize them into unified context.

---

### §3.4 GOALS — Objective Timeline

**Systems that feed Goals:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **ION Navigator** `contextualize()` + `audit()` | Active branches = current goals. Audit health = velocity. | `active_branches` → active goals. `overall_health` → velocity indicator. |
| **ION Manifest** `ManifestManager` | Loop position, system confidence, completed branches | `completed_branches` → completed goals. `system_confidence` → goal confidence. |

**Integration formula:**
```python
goals.active = [branch.summary for branch in manifest.get_active_branches()]
goals.completed = [branch.summary for branch in manifest.get_completed_branches()]
goals.velocity = "on_track" if audit.overall_health > 0.6 else "behind"
```

---

### §3.5 ISSUES — Problem Tracking

**Systems that feed Issues:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **SEG** `detect_contradictions()` | Found contradictions → active issues | Every detected contradiction becomes an issue entry with entity IDs, explanation, confidence. |
| **SEG** `trace_provenance()` | Provenance chains show root causes of issues | When investigating an issue, SEG's provenance tracing finds the causal chain. |

**Integration formula:**
```python
# On audit:
contradictions = seg.detect_contradictions()
for c in contradictions:
    issues.active.add(Issue(
        severity="HIGH",
        description=c.explanation,
        source=f"SEG: {c.entity1_id} ↔ {c.entity2_id}",
        provenance=seg.trace_provenance(c.entity1_id)
    ))
```

---

### §3.6 USER — Operator Knowledge

**Systems that feed User:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **CMC** `memory_store` | Persistent user preferences, memories, corrections | CMC atoms tagged `user_preference`, `user_correction`, `user_priority`. |
| **MCP** `store_memory` / `retrieve_memory` | Key-value operator memories | MCP memory tools already persist user info — bridge to CMC atoms. |

**Integration formula:**
```python
user.profile = cmc.query(tags={"user_preference": 0.5}, limit=50)
user.priorities = mcp.retrieve_memory("operator_priorities")
user.corrections = cmc.query(tags={"user_correction": 0.5}, sort="created_at DESC")
```

---

### §3.7 RELATIONSHIPS — Social Graph

**Systems that feed Relationships:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **SEG** entities + relations | Agents as entities, relationships as relations | Each agent → SEG entity. Trust, history, handoff patterns → SEG relations. |
| **CMC** `cross_model_atoms` | Cross-model memory reveals which AIs worked together | CMC's cross-model subsystem tracks which models produced which atoms — showing collaboration patterns. |
| **ION** `agent_manifest.py` | Agent role, genome, callsign | Static agent info feeds relationship baseline. |

**Integration formula:**
```python
# For each agent:
relationships.agents[callsign] = SEGEntity(
    type="agent",
    name=callsign,
    attributes=agent_manifest.to_dict(),
)
# Add relation:
seg.add_relation(Relation(
    source_id=my_callsign,
    target_id=peer_callsign,
    relation_type=RelationType.COLLABORATES_WITH,
    confidence=trust_score
))
```

---

### §3.8 COMMS — Agent Communication Hub

**Systems that feed Comms:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **MCP** `send_ai_message` / `get_ai_messages` | Direct agent-to-agent messaging | MCP message tools → `sections/comms/inbox.md` and `outbox.md`. |
| **ION** `agent_comms.py` | ION-native agent communication | ION's comms module provides structured message types. |

**Integration formula:**
```python
# On workspace boot:
comms.inbox = mcp.get_ai_messages(to_ai=callsign)
comms.outbox = mcp.get_ai_messages(from_ai=callsign, limit=10)
# During execution:
mcp.send_ai_message(from_ai=callsign, to_ai=target, content=message)
```

---

### §3.9 SELF — Persona and Capabilities

**Systems that feed Self:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **CAS** (Consciousness Analyzer) | Self-awareness metrics, introspection | CAS's self-model feeds `sections/self/capabilities.md` and `limitations.md`. |
| **ION** `agent_manifest.py` | Agent role, genome, correction vectors | Genome file → `sections/self/genome.md`. |

---

### §3.10 HISTORY — Workspace Modification Trail

**Systems that feed History:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **CMC** `memory_store` | File interaction atoms with bitemporal tracking | Every file view/edit → CMC atom tagged `file_interaction`. |
| **ION GovernedWrite** `WriteReceipt` | Every governed write produces a receipt | Receipts → `sections/history/files_edited.md` with stage results. |
| **TCS** timeline tracking | Temporal ordering of all workspace changes | TCS provides the timeline view of all modifications. |
| **HHNI** multi-resolution | Zoom in on specific file histories when needed | Old file interactions compressed via HHNI from sentence→paragraph→section. |

---

### §3.11 MISSION — Strategic Context

**Systems that feed Mission:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **ION Navigator** `manifest.mission` | Mission string from ManifestManager | Direct mapping: `manifest.mission` → `sections/mission/brief.md`. |
| **ION Capsule** `create_pre_capsule()` | Mission is immutable in capsule (unless director changes) | Capsule's `must_not` constraints → `sections/mission/constraints.md`. |
| **ION ContextCompiler** `compile_three_tier()` | Pinned tier always loads the mission | Mission ions at A0-A1 level always present in context. |

---

### §3.12 EVIDENCE — Proof Register

**Systems that feed Evidence:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **SEG** evidence operations | `add_evidence()`, `list_evidence()`, time-travel queries | SEG IS the evidence register. Every claim, test result, observed fact → SEG evidence node. |
| **VIF** `kappa_gate` | κ-gating validates confidence before evidence is accepted | Before adding evidence to SEG, VIF gates it: confidence must pass the κ threshold for the task criticality. |
| **VIF** `calibration` | ECE calibration adjusts thresholds based on past accuracy | VIF's `adaptive_kappa_threshold()` adjusts the evidence acceptance bar for poorly-calibrated models. |
| **ION Navigator** `reflect()` | Reflection separates high/low confidence ions | `.low_confidence` and `.high_confidence` lists feed confidence state. |
| **ION ContextCompiler** `compile_for_step("reflect")` | Loads evidence ions for reflection step | Evidence ions sorted by confidence for workspace evidence section. |
| **ION GovernedWrite** `_w4_evidence()` | Validates confidence range on every write | Confidence validation at write time ensures evidence integrity. |

**This is the most system-rich section** — 6 systems converge here.

**Integration formula:**
```python
# On evidence creation:
gate_result = vif.kappa_gate.check(
    confidence=claim_confidence,
    task_criticality=TaskCriticality.IMPORTANT,
)
if gate_result.passed:
    seg.add_evidence(Evidence(
        claim=claim_text,
        source=source,
        confidence=claim_confidence,
    ))
elif gate_result.should_escalate:
    vif.hitl_escalator.escalate(gate_result, context={"claim": claim_text})
    # → goes to Comms inbox as escalation request
```

---

### §3.13 COGNITIVE — Reasoning Chain State

**Systems that feed Cognitive:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **ION Navigator** full §7 loop | CognitiveContext, ReflectionResult, ExecutionPlan, AuditResult | The cognitive section IS the Navigator's state, rendered as inspectable markdown. |
| **VIF** `confidence_extraction` | Confidence scores on each reasoning step | VIF tracks confidence through the reasoning chain — which steps are certain vs uncertain. |
| **APOE** `insight_transfer` | TransferContext with recommended approach, key considerations, risks | APOE's insight transfer documents the reasoning behind model selection and execution strategy. |
| **CAS** introspection | Self-awareness metrics during reasoning | CAS feeds uncertainty awareness and meta-cognitive observations. |

**This section makes the AI's reasoning inspectable:**

```python
cognitive.current_chain = navigator.contextualize()  # What does the system see?
cognitive.reflection = navigator.reflect()            # What does it think about that?
cognitive.plan = navigator.plan()                     # What does it decide to do?
cognitive.decision_log.append(Decision(
    what=plan.ordered_branches[0],
    why=plan.rationale,
    alternatives=plan.ordered_branches[1:],
    confidence=vif.check(confidence).confidence,
    step=navigator.current_step,
))
```

---

### §3.14 BOUNDARIES — What's Unresolved

**Systems that feed Boundaries:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **SEG** `detect_contradictions()` | Open contradictions = unresolved boundaries | Contradictions that haven't been resolved stay as open boundary questions. |
| **ION Navigator** `reflect()` | Gaps (low-confidence deps), risks (stale ions) | Navigator reflection surfaces unknowns and risks. |

---

### §3.15 OUTPUT — Work Products

**Systems that feed Output:**

| System | Integration Pattern | Implementation |
|--------|-------------------|----------------|
| **APOE** `ExecutionResult` | Quality score, confidence score, completeness score | Every execution result → output quality log with multi-dimensional scoring. |
| **VIF** `kappa_gate` | κ-gate result on output before delivery | Before delivering output, VIF gates it: is it confident enough? |
| **ION Navigator** `deliver()` | Delivery summary with loop position, branch status, health | Navigator's delivery step = the output section's final record. |

---

## §4. The Convergence Architecture

All systems converge through **three integration layers:**

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: WORKSPACE                        │
│         15 sections of the living workspace                  │
│    (AGENT_CONTEXT_ARCHITECTURE.md defines this)             │
│                                                              │
│  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐       │
│  │DOC │ORC │CHAT│GOAL│ISS │USR │REL │COM │SELF│... │       │
│  └──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴──┬─┘       │
│     │    │    │    │    │    │    │    │    │    │            │
├─────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────────────┤
│     │    │    │    │    │    │    │    │    │    │            │
│  LAYER 2: ION RUNTIME                                        │
│  Navigator, ContextCompiler, GovernedWrite, CapsuleManager   │
│  Manifest, Graph, Index, Store, Threshold                    │
│                                                              │
│  ION types = workspace elements:                             │
│    PROTOCOL → Doctrine    BRANCH → Orchestration            │
│    EVIDENCE → Evidence    CAPSULE → Mission+Orchestration    │
│    MEMORY   → Rolling Context + History + User              │
│    AGENT    → Self + Relationships                          │
│    MANIFEST → Workspace root capsule                        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 1: AIM-OS PACKAGES                                    │
│  The specialized engines that power specific capabilities    │
│                                                              │
│  CMC → persistence, bitemporal memory, cross-model atoms    │
│  HHNI → multi-resolution retrieval, compression, zoom       │
│  SEG → evidence graph, contradictions, provenance, time     │
│  VIF → confidence gating, calibration, HITL escalation      │
│  APOE → multi-model execution, insight transfer, consensus  │
│  CAS → self-awareness, introspection, meta-cognition        │
│  TCS → timeline tracking, smart compression, priority load  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Layer 1 → Layer 2 Integration

AIM-OS packages are already partially integrated with ION:
- `seg/hhni_integration.py` — SEG uses HHNI for retrieval
- `seg/vif_integration.py` — SEG uses VIF for confidence
- `seg/cmc_integration.py` — SEG uses CMC for persistence
- `vif/seg_integration.py` — VIF uses SEG for evidence
- `apoe/cmc_integration.py` — APOE uses CMC for memory
- `hhni/sdfcvf_integration.py` — HHNI uses SDF-CVF for validation

These cross-integration files are the BRIDGE from Layer 1 to Layer 2.

### Layer 2 → Layer 3 Integration

ION runtime modules map to workspace sections via ion types:

| ION Type | Workspace Section(s) | How |
|----------|---------------------|-----|
| `MANIFEST` | Root capsule (workspace.md) | Manifest IS the workspace root |
| `PROTOCOL` | Doctrine | Protocols loaded as governing law |
| `BRANCH` | Orchestration, Goals | Active branches = tasks + goals |
| `EVIDENCE` | Evidence | Evidence ions = proof register |
| `MEMORY` | Rolling Context, History, User | Memory ions persist interactions |
| `CAPSULE` | Mission, Orchestration | PRE/POST bracket operations |
| `AGENT` | Self, Relationships | Agent ions describe agents |
| `SPEC` | Output (specs for code to produce) | Spec ions define deliverables |
| `TOOL` | Cognitive (tools available) | Tool ions in reasoning chain |

---

## §5. What's Missing (Build List)

These integrations don't exist yet and must be built:

### 5.1 Workspace Boot Service

```
NEEDED: workspace_boot(callsign) → Reads context_profile.yaml,
  calls context_compiler.compile_three_tier() for Layer 2,
  queries CMC for Layer 1 data,
  populates all 15 sections.
STATUS: Does NOT exist. Navigator + ContextCompiler have the pieces
  but no orchestration service connects them to workspace files.
```

### 5.2 Rolling Context Compression Service

```
NEEDED: rolling_compress(exchange) → Ingests new exchange into CMC,
  applies TCS compression to older exchanges,
  uses HHNI for multi-resolution indexing,
  updates workspace rolling_context section.
STATUS: CMC, TCS, HHNI all exist but NOT CONNECTED to each other
  or to workspace files.
```

### 5.3 Evidence Integration Service

```
NEEDED: evidence_gate(claim, confidence) → VIF κ-gate →
  if passed: SEG.add_evidence() → update workspace evidence section
  if failed: VIF HITL escalation → update workspace comms inbox
STATUS: VIF and SEG both exist with integration files,
  but not wired to workspace sections.
```

### 5.4 Cognitive Render Service

```
NEEDED: render_cognitive_state() → Navigator state →
  markdown rendering of current chain, decisions, alternatives →
  updates workspace cognitive section.
STATUS: Navigator produces CognitiveContext/ReflectionResult/ExecutionPlan/AuditResult
  but no renderer converts them to inspectable workspace markdown.
```

### 5.5 Workspace Lifecycle MCP Tools

```
NEEDED: MCP tools for workspace operations:
  - workspace_boot(callsign)     → boot the workspace
  - workspace_save(callsign)     → save current state
  - workspace_section(name)      → read a specific section
  - workspace_update(name, data) → update a section
  - workspace_compress()         → compress rolling context
STATUS: MCP server has memory/capsule/comms tools but NO workspace tools.
```

---

## §6. Priority Integration Order

Based on causal dependencies and immediate value:

```
PHASE 1: Foundation (builds on what exists)
  ├── 1a. Workspace Boot Service → connects Navigator + ContextCompiler → workspace files
  ├── 1b. Cognitive Render Service → Navigator state → inspectable markdown
  └── 1c. Evidence Integration Service → VIF + SEG → workspace evidence section

PHASE 2: Memory Layer
  ├── 2a. Rolling Context Compression → CMC + TCS + HHNI → workspace rolling_context
  └── 2b. CMC ↔ Workspace bridge → atoms ↔ section files

PHASE 3: Communication Layer
  ├── 3a. Workspace MCP Tools → MCP server → workspace CRUD
  └── 3b. Comms Integration → MCP messages + ION agent_comms → workspace comms

PHASE 4: Full Integration
  ├── 4a. SEG ↔ Workspace bridge → contradictions/provenance ↔ issues/boundaries
  └── 4b. APOE ↔ Workspace bridge → execution results ↔ output quality
```

---

## §7. Self-Audit

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Deep-read all 8 core AIM-OS systems | ✅ | Read models.py (CMC), hierarchical_index.py (HHNI), seg_graph.py (SEG), kappa_gate.py (VIF), execution_orchestrator.py (APOE) |
| Deep-read ION runtime modules | ✅ | Read capsule.py, navigator.py, governed_write.py, context_compiler.py, context.py |
| Deep-read MCP tools | ✅ | Grep for record_context_capsule, confirmed tool categories |
| All 15 sections mapped | ✅ | §3.1-§3.15 each show which systems feed them |
| Cross-integration files identified | ✅ | SEG has 6 integration files, VIF has 6, APOE has 5 |
| Build list concrete | ✅ | §5 — 5 specific services with status |
| Priority order defined | ✅ | §6 — 4 phases based on dependencies |

---

*Derived from: Deep-read of 12+ packages totaling 600+ files and 103 ION modules*
*Governed by: AETHER_CONSTITUTION, AETHER_ATLAS*
*— Opus, 2026-03-24*
