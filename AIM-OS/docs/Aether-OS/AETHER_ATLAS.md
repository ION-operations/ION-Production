# The Living Atlas of Aether-OS — v2.1

## A Sovereign Orientation Document for the Governed Intelligence System

**Atlas version**: 2.1.0
**Supersedes**: atlas_v2.md (v2.0), atlas.txt (v1)
**Last updated**: 2026-03-18
**Authority class**: A4 (Operational Organism)
**Maintained by**: Agent workforce under Presidential authority

**Foundation documents**: Constitution → `AETHER_CONSTITUTION.md` | Kernel → `AETHER_KERNEL.md` | Protocols → `AETHER_INTERFACE.md`

---

## Table of Contents

1. [Book I — First Principles and Authority](#book-i--first-principles-and-authority)
2. [Book II — Canonical Object Registry](#book-ii--canonical-object-registry)
3. [Book III — Runtime Truth and Boundary Registers](#book-iii--runtime-truth-and-boundary-registers)
4. [Book IV — Continuity and Retrieval Guidance](#book-iv--continuity-and-retrieval-guidance)
5. [Book V — Package Ownership and Migration Maps](#book-v--package-ownership-and-migration-maps)
6. [Book VI — Research Branches and Quarantine Boundaries](#book-vi--research-branches-and-quarantine-boundaries)
7. [Book VII — Deployment Projections](#book-vii--deployment-projections)
8. [Book VIII — Atlas Self-Governance](#book-viii--atlas-self-governance)
9. [Book IX — Governed Ingestion and Deterministic Retrieval](#book-ix--governed-ingestion-and-deterministic-retrieval)
10. [Book X — Kernel, Syscalls, and Geometric Runtime Definition](#book-x--kernel-syscalls-and-geometric-runtime-definition)

---

# Book I — First Principles and Authority

## 1. What this atlas is

The Living Atlas is the sovereign orientation document for AIM-OS. It exists so that any agent — human or AI — entering the system can rapidly understand:

- what is supreme,
- what exists,
- what is real versus doctrinal,
- what is alive versus aspirational,
- how work continues across sessions,
- and where the honest boundaries of the system are.

The atlas is not a specification or an implementation plan. It is a map of the territory — what is, what should be, and the gap between them.

## 2. Supreme law

The governing law of the entire ecology is the **AETHER_CONSTITUTION** — the constitutional document that defines:

- prime directives,
- authority order,
- validity predicates,
- contradiction and recovery rules,
- continuity requirements,
- specialization boundaries,
- runtime honesty clauses.

All other documents, systems, schemas, and agents are subordinate to the Constitution. When conflict arises between any system behavior and the Constitution, the Constitution wins. The boot projection is AETHER_KERNEL; typed schemas live in AETHER_INTERFACE.

Above the Constitution stands one authority: **human sovereignty** (the President, Braden). The President's decisions override all other authority, including the Constitution itself.

## 3. Authority classes

| Class | Name | Scope | Examples |
|-------|------|-------|----------|
| **A0** | Supreme Canon | Permanent, inviolable | AETHER_CONSTITUTION, human sovereignty |
| **A1** | Canonical Projection | Boot/recovery/boundary forms derived from A0 | AETHER_KERNEL, STARTUP.md, genome projections |
| **A2** | Canonical Extension | Formal extensions of A0 for specific domains | COMMS_DOCTRINE, Capsule Protocol, Polycast doctrine |
| **A3** | Canonical Lineage | Strong predecessor material, valuable but not governing | SEEDv1, Project ION, seedgpt |
| **A4** | Operational Organism | Implementation atlas, operational truth | This atlas, package registries, runtime truth |
| **A5** | Meta-Governance | Reflective/self-model documents | CAS outputs, genome v3 soul system |
| **A6** | Research Branch | Forward-looking, not yet operational | Geometric Runtime (Seedkernel), quaternion kernel |
| **A7** | Historical/Legacy | Archived or quarantined | OmniBus, deepthinkOS absolutism, stale runbooks |

**Supersession law**: Lower authority classes cannot silently override higher ones. When A7 material contradicts A0, the A7 material is quarantined, not merged. Historical aliases are preserved for lineage tracing, but only one canonical name governs active operation.

## 4. The total ecology in one sentence

AIM-OS is a **governed intelligence system** in which an AI workforce operates under constitutional law, across multiple embodiments and host platforms, using bitemporal memory, evidence-graded retrieval, plan orchestration, and self-reflective verification to perform work that persists lawfully across sessions, agents, and machines.

## 5. Canonical naming law

Every canonical object has four naming tiers:

| Tier | Purpose | Example |
|------|---------|---------|
| **Canonical** | Registry truth, machine reference | Bitemporal Memory Store |
| **Ceremonial** | Culture, shorthand, team identity | CMC |
| **Interface** | Operator-facing label | Memory |
| **Module** | Package/directory name | `cmc_service` |

When names conflict, canonical wins. Ceremonial names (CMC, VIF, APOE, etc.) remain valid in conversation but do not outrank the canonical registry in governance contexts.

## 6. First-read and load order

When beginning work or resuming after interruption, the following load order applies:

1. **L1** — Supreme canon (AETHER_CONSTITUTION or AETHER_KERNEL projection)
2. **L2** — Route and embodiment identity (who am I, where am I)
3. **L3** — Mission and canon (teleological canon relevant to this lane)
4. **L4** — Current-state surfaces (status, priorities, last checkpoint)
5. **L5** — Active plan and objective (plan reference, phase, next action)
6. **L6** — Contradictions, risks, unresolved boundaries
7. **L7** — Dependencies (code, docs, evidence, memory)
8. **L8** — Historical context (chat traces, reports, archives)

This order resolves "what do I read first?" disputes functionally rather than by slogan.

## 7. The atlas as anti-sediment machinery

This atlas exists in part to prevent **sediment** — the accumulation of stale, contradictory, or falsely-authoritative material that degrades system coherence over time.

Sediment forms when:
- old documents remain loaded as if current,
- route names split without resolution,
- status files contradict each other,
- chat traces are treated as continuity when continuity bundles are absent,
- bygone architectural decisions are loaded as live constraints.

The atlas fights sediment by:
- maintaining a canonical registry of what exists,
- grading runtime truth honestly,
- tracking external boundaries explicitly,
- enforcing current-state precedence,
- classifying material into retrieval zones (Active Canon / Runtime Support / Lineage / Research / Quarantine).

---

# Book II — Canonical Object Registry

## 1. Registry law

Every first-class architectural concept in AIM-OS must be registered here with:

- a canonical name, ceremonial alias, and module name
- an authority class (A0–A7)
- an ontology class (LAW, SEMANTIC_OBJECT, STATE_OBJECT, PROCESS_OBJECT, EVIDENCE_OBJECT, INTERFACE_OBJECT, META_GOVERNANCE_OBJECT, SUBSTRATE_OBJECT)
- a runtime truth state (ALIVE, FUNCTIONAL, PARTIAL, DEGRADED, BROKEN, DOCTRINAL_ONLY, EXTERNAL_UNSETTLED)
- owned state and emitted artifacts
- primary and secondary runtime owners
- upstream and downstream dependencies
- open gaps and boundary flags

## 2. Registry field schema

```yaml
- id: [snake_case_identifier]
  canonical_name: [Full Canonical Name]
  ceremonial_name: [Short Name / Acronym]
  interface_name: [Operator-facing label]
  module_name: [package_directory]
  authority_class: [A0–A7]
  ontology_class: [LAW | SEMANTIC_OBJECT | STATE_OBJECT | PROCESS_OBJECT | EVIDENCE_OBJECT | INTERFACE_OBJECT | META_GOVERNANCE_OBJECT | SUBSTRATE_OBJECT]
  runtime_truth: [ALIVE | FUNCTIONAL | PARTIAL | DEGRADED | BROKEN | DOCTRINAL_ONLY | EXTERNAL_UNSETTLED]
  owned_state: [list]
  emitted_artifacts: [list]
  primary_runtime_owner: [package or null]
  secondary_runtime_owners: [list]
  dependencies:
    upstream: [list]
    downstream: [list]
  boundary_flags: [list]
  open_gaps: [list]
  last_assessed: [date]
```

## 3. Runtime truth states

| State | Meaning |
|-------|---------|
| **ALIVE** | Running, probed, confirmed responsive |
| **FUNCTIONAL** | Code exists and is exercised, strong evidence of operation |
| **PARTIAL** | Some runtime presence but incomplete, fragmented, or environment-dependent |
| **DEGRADED** | Was functional but suffering from decay, missing siblings, or reduced health |
| **BROKEN** | Code exists but does not currently function |
| **DOCTRINAL_ONLY** | Described in doctrine but has no sovereign runtime owner |
| **EXTERNAL_UNSETTLED** | Truth depends on external state that cannot be settled locally |

## 4. Canonical object registry — 32 entries

### 4.1 Constitutional Law
- **Ceremonial**: Seed / Stele
- **Module**: `constitution` (no package exists)
- **Authority**: A0 | **Ontology**: LAW | **Runtime**: DOCTRINAL_ONLY
- **Owned state**: Prime directives, authority order, validity predicates, contradiction rules, continuity requirements, honesty clauses
- **Primary owner**: null — exists only in AETHER_CONSTITUTION and prompt projections
- **Open gaps**: No constitution package, no validity engine, no revision propagation
- **Last assessed**: 2026-03-17

### 4.2 Teleological Canon
- **Ceremonial**: Dreamspace / North Star
- **Module**: `canon` (no package exists)
- **Authority**: A0 | **Ontology**: SEMANTIC_OBJECT | **Runtime**: DOCTRINAL_ONLY
- **Owned state**: Mission, aesthetic law, anti-vision, resonance criteria, domain canon rules
- **Primary owner**: null — exists in North Star documents and genome files
- **Open gaps**: No canon package, no anti-pattern registry
- **Last assessed**: 2026-03-17

### 4.3 Intent Calculus (PLIx)
- **Ceremonial**: PLIx
- **Module**: `plix`
- **Authority**: A4 | **Ontology**: SEMANTIC_OBJECT | **Runtime**: FUNCTIONAL
- **Owned state**: Intent expressions, semantic contracts, preconditions, postconditions, capability requirements, plan compilation targets
- **Primary owner**: `packages/plix/`
- **Open gaps**: Not universal across all runtime surfaces, needs stronger authority bindings
- **Last assessed**: 2026-03-17

### 4.4 Core Identity Constraint
- **Ceremonial**: Sovereign Center
- **Module**: `identity` (no package exists)
- **Authority**: A2 | **Ontology**: SEMANTIC_OBJECT | **Runtime**: DOCTRINAL_ONLY
- **Owned state**: Identity invariants, value floor, adaptation limits, embodiment-sensitive bounds
- **Primary owner**: null — expressed through genome files and polycast doctrine
- **Open gaps**: No identity schema, no policy engine
- **Last assessed**: 2026-03-17

### 4.5 Delivery Modulation
- **Ceremonial**: Persona Matrix
- **Module**: `delivery` (no package exists)
- **Authority**: A2 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Tone selection, register selection, pacing, audience rendering
- **Primary owner**: null — exists as behavioral patterns in agent prompts
- **Last assessed**: 2026-03-17

### 4.6 Bitemporal Memory Store (CMC)
- **Ceremonial**: CMC
- **Module**: `cmc_service`
- **Authority**: A4 | **Ontology**: STATE_OBJECT | **Runtime**: ALIVE
- **Owned state**: Memory records (190+ atoms), bitemporal timestamps, snapshots, persistence (SQLite), query state
- **Primary owner**: `packages/cmc_service/` — confirmed responsive via MCP probes
- **Evidence**: SQLite database active, `store_memory` / `retrieve_memory` MCP tools operational
- **Open gaps**: Stronger continuity object linkage needed
- **Last assessed**: 2026-03-17 (probed today)

### 4.7 Memory Record
- **Ceremonial**: atom
- **Module**: `record` (within cmc_service)
- **Authority**: A4 | **Ontology**: STATE_OBJECT | **Runtime**: FUNCTIONAL
- **Owned state**: Payload, timestamps, tags, provenance fields
- **Primary owner**: cmc_service model layer
- **Open gaps**: Stricter type families needed
- **Last assessed**: 2026-03-17

### 4.8 Continuity Bundle
- **Ceremonial**: checkpoint / capsule family
- **Module**: `continuity` (no sovereign package)
- **Authority**: A1 | **Ontology**: STATE_OBJECT | **Runtime**: PARTIAL *(upgraded from DOCTRINAL_ONLY)*
- **Owned state**: Checkpoints, capsules, continuity manifests, handoff bundles
- **Primary owner**: null — but capsule protocol is actively used via `record_context_capsule` MCP tool
- **Evidence**: Active capsule files in `.agent/comms/capsules/`, PRE/POST discipline enforced
- **Open gaps**: No sovereign schema family, no resume API, no manifest standard
- **Last assessed**: 2026-03-17 (used today)

### 4.9 Hierarchical Context Index (HHNI)
- **Ceremonial**: HHNI
- **Module**: `hhni`
- **Authority**: A4 | **Ontology**: STATE_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Hierarchy nodes, retrieval metadata, summary blocks, ranked candidates
- **Primary owner**: `packages/hhni/` — has DVNS physics retrieval model
- **Open gaps**: Environment-dependent initialization, working context manifests incomplete
- **Last assessed**: 2026-03-17

### 4.10 Working Context
- **Ceremonial**: Active Context Envelope (ACE)
- **Module**: `context` (no sovereign package)
- **Authority**: A1 | **Ontology**: STATE_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Loaded law references, plan reference, dependencies, evidence, contradictions, compression traces
- **Secondary owners**: `context_bootloader`, HHNI outputs, APOE task frames
- **Open gaps**: No first-class schema, no consistent manifest, no universal inspection surface
- **Last assessed**: 2026-03-17

### 4.11 Evidence Graph (SEG)
- **Ceremonial**: SEG
- **Module**: `seg`
- **Authority**: A4 | **Ontology**: EVIDENCE_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Evidence nodes, support/contradiction edges, provenance chains, audit anchors
- **Primary owner**: `packages/seg/` — service boundary exists
- **Open gaps**: Graph density variable, contradiction object family needed
- **Last assessed**: 2026-03-17

### 4.12 Verification Framework (VIF)
- **Ceremonial**: VIF
- **Module**: `vif`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Confidence states (κ-gating), verification outcomes, replay manifests, abstention states
- **Primary owner**: `packages/vif/`
- **Evidence**: `track_confidence` MCP tool exists
- **Open gaps**: Operational usage density limited, capability ledger relation weak
- **Last assessed**: 2026-03-17

### 4.13 Execution Plan
- **Ceremonial**: Blueprint
- **Module**: `plan` (within apoe)
- **Authority**: A1 | **Ontology**: SEMANTIC_OBJECT | **Runtime**: ALIVE
- **Owned state**: Objective, ordered steps, dependencies, validations, rollback conditions
- **Primary owner**: `packages/apoe/` plan models
- **Last assessed**: 2026-03-17

### 4.14 Execution Gate
- **Ceremonial**: Gate
- **Module**: `gate` (within apoe)
- **Authority**: A1 | **Ontology**: PROCESS_OBJECT | **Runtime**: FUNCTIONAL
- **Owned state**: Threshold logic, proceed/pause/abstain/recover status, gate criteria
- **Primary owner**: APOE gates
- **Last assessed**: 2026-03-17

### 4.15 Plan Orchestrator (APOE)
- **Ceremonial**: APOE
- **Module**: `apoe`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: ALIVE
- **Owned state**: Orchestration runtime, step dispatch, budgets, retries, execution traces
- **Primary owner**: `packages/apoe/`
- **Evidence**: Goal-to-plan compilation, multi-agent coordination confirmed operational
- **Open gaps**: Stronger continuity emission, stronger authority bindings
- **Last assessed**: 2026-03-17

### 4.16 Operational Packet
- **Ceremonial**: packet family
- **Module**: `packet` (no sovereign package)
- **Authority**: A1 | **Ontology**: STATE_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Typed payloads, uncertainty declarations, next-step references, validation obligations
- **Note**: Packet-like forms exist in receipts, handoffs, traces, but no unified schema
- **Last assessed**: 2026-03-17

### 4.17 Deliberative Role Assembly (Polycaste)
- **Ceremonial**: Polycaste
- **Module**: `deliberation` (no sovereign package)
- **Authority**: A2 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Role-phase reasoning states, critique, synthesis, handoff structures
- **Secondary owners**: APOE role logic, agent packages, polycast doctrine
- **Last assessed**: 2026-03-17

### 4.18 Source Synchronization System
- **Ceremonial**: ContextSync / BCI lineage
- **Module**: `sync` (no sovereign package)
- **Authority**: A2 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Contract drift states, sync manifests, coherence state, remediation atoms
- **Open gaps**: No sovereign sync package, no canonical schema family
- **Last assessed**: 2026-03-17

### 4.19 Change Coherence Framework (SDF-CVF)
- **Ceremonial**: SDF-CVF
- **Module**: `quality` / `sdfcvf`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Owned state**: Parity metrics, coherence assessments, blast radius evaluations
- **Primary owner**: `packages/sdfcvf/` — Quintet protocol
- **Last assessed**: 2026-03-17

### 4.20 Reflective Monitor (CAS)
- **Ceremonial**: CAS
- **Module**: `cas`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: DEGRADED
- **Owned state**: Activation, attention, categorization, introspection, failure modes
- **Primary owner**: `packages/cas/`
- **Note**: CAS is monitoring, NOT sovereign identity or proof of personhood
- **Last assessed**: 2026-03-17

### 4.21 Improvement Engine (SIS)
- **Ceremonial**: SIS
- **Module**: `improvement` / `sis`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Primary owner**: `packages/sis/`
- **Open gaps**: Fragmented implementation, no standard remediation schema
- **Last assessed**: 2026-03-17

### 4.22 Research Engine
- **Ceremonial**: ARD lineage
- **Module**: `research`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Secondary owners**: `packages/autonomous_research_dream/`, `packages/deepsearch/`, `packages/icip_search/`
- **Open gaps**: Fragmented across multiple experiment packages
- **Last assessed**: 2026-03-17

### 4.23 Authority System
- **Ceremonial**: Authority Map
- **Module**: `authority` (no package)
- **Authority**: A0 | **Ontology**: LAW | **Runtime**: DOCTRINAL_ONLY
- **Owned state**: Authority tiers, approval rules, proof thresholds, embodiment overlays
- **Open gaps**: No authority package, no descriptors, no stable threshold bindings
- **Last assessed**: 2026-03-17

### 4.24 Capability Ledger
- **Ceremonial**: Capability Proof
- **Module**: `capability`
- **Authority**: A4 | **Ontology**: EVIDENCE_OBJECT | **Runtime**: DOCTRINAL_ONLY
- **Secondary owner**: `packages/capability_awareness/`
- **Open gaps**: No sovereign ledger service, no freshness schema
- **Last assessed**: 2026-03-17

### 4.25 Embodiment
- **Ceremonial**: Host Form
- **Module**: `embodiment` (no package)
- **Authority**: A5 | **Ontology**: SEMANTIC_OBJECT | **Runtime**: PARTIAL *(upgraded from DOCTRINAL_ONLY)*
- **Concrete instances** (see Book V for details):
  - Opus (Claude Opus 4.6) in Antigravity IDE — COO
  - Sev (GPT-5.4) in Codex IDE — CEO
  - Codex (GPT-5.4) in Cursor IDE — Lead Builder
  - Gemini (2.5/3.1 Pro) in Google CLI — Research Specialist
  - Composer (Claude 1.5) in Cursor Composer — Auditor-Mapper
- **Open gaps**: No formal descriptor system — but genome files serve as partial descriptors
- **Last assessed**: 2026-03-17

### 4.26 Operator Surface
- **Ceremonial**: AIM-OS Interface / Workspace
- **Module**: `surface`
- **Authority**: A4 | **Ontology**: INTERFACE_OBJECT | **Runtime**: ALIVE
- **Owned state**: Rendered views, interaction states, panel state, I/O flows
- **Primary owners**: IDE extensions (Antigravity, Cursor), JOC web surfaces, CLI surfaces
- **Last assessed**: 2026-03-17

### 4.27 Governed Intelligence System
- **Ceremonial**: AIM-OS
- **Module**: `system`
- **Authority**: A4 | **Ontology**: META_GOVERNANCE_OBJECT | **Runtime**: PARTIAL
- **Owned state**: System decomposition, service ecology, cross-layer organization
- **Open gaps**: No machine-readable system registry, no unified atlas infrastructure
- **Last assessed**: 2026-03-17

### 4.28 Geometric Runtime
- **Ceremonial**: Seedkernel
- **Module**: `kernel` / `quaternion_kernel`
- **Authority**: A6 | **Ontology**: SUBSTRATE_OBJECT | **Runtime**: DOCTRINAL_ONLY
- **Owned state**: Geometric addressing, transition primitives, replay semantics, witness structures
- **Secondary owners**: `packages/quaternion_kernel/`, `packages/quaternion_math/`
- **Open gaps**: Research branch only — no formal upper-layer mappings
- **Last assessed**: 2026-03-17

---

### NEW ENTRIES (v2 additions)

### 4.29 Agent Workforce
- **Ceremonial**: The Team
- **Module**: `agent`
- **Authority**: A2 | **Ontology**: PROCESS_OBJECT | **Runtime**: ALIVE
- **Owned state**: Agent genomes (v4.0), military rank structure, correction vectors, session protocols, comms channels, handoff bundles
- **Primary owners**: `.agent/genomes/`, `.agent/COMMS_DOCTRINE.md`, `.agent/AGENTS.md`
- **Active roster**: Opus (COO), Sev (CEO), Codex (Lead Builder), Gemini (Research), Composer (Auditor)
- **Evidence**: Genome files actively read on startup, capsule protocol enforced, comms doctrine followed
- **Open gaps**: No formal agent-state inspection API, no runtime health dashboard for agents
- **Last assessed**: 2026-03-17 (operational today)

### 4.30 MCP Transport System
- **Ceremonial**: MCP / aim-os-mcp
- **Module**: `aimos_mcp`
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: ALIVE
- **Owned state**: 137+ tools across 19 categories, stdio transport, HTTP bridge (port 5001), tool registry, session management
- **Primary owner**: `packages/aimos_mcp/server.py` (10,925 lines)
- **Evidence**: `store_memory`, `retrieve_memory`, `record_context_capsule`, `send_ai_message`, `get_ai_messages` all confirmed operational
- **Architecture note**: Currently a monolith — consolidation decision freeze prohibits restructuring
- **Open gaps**: Monolithic server, tool category overlap, no health monitoring
- **Last assessed**: 2026-03-17 (probed today)

### 4.31 AI Engine
- **Ceremonial**: AI Engine v2.0
- **Module**: `ai_engine` (within aimos_mcp)
- **Authority**: A4 | **Ontology**: PROCESS_OBJECT | **Runtime**: PARTIAL
- **Owned state**: 9-layer facade, ChainedMission system, ChainDirector, specialist swarm topology
- **Primary owner**: `packages/aimos_mcp/` — exposed via 14 MCP tools
- **Tools**: `ai_engine_execute`, `ai_engine_ask`, `ai_engine_code`, `ai_engine_plan`, `ai_engine_audit`, `ai_engine_swarm`
- **Open gaps**: Specialist agent spawner not fully operational, quality gates incomplete
- **Last assessed**: 2026-03-17

### 4.32 Joint Operations Center (JOC)
- **Ceremonial**: JOC / Mission Control
- **Module**: `joc`
- **Authority**: A4 | **Ontology**: INTERFACE_OBJECT | **Runtime**: PARTIAL
- **Owned state**: 5-pillar mission dashboard (Dashboard, Session, Dispatch, Synthesis, Catalog), Surface Engine (2.5D rendering), PageOracleAPI
- **Primary owner**: `packages/joc/`
- **Evidence**: Port 5011 server, Automation Macros engine, Aether Oracle dual-control system
- **Open gaps**: Cross-host deployment untested, BAS integration incomplete
- **Last assessed**: 2026-03-17

---

## 5. Registry summary

| Status | Count | Objects |
|--------|-------|---------|
| **ALIVE** | 6 | CMC, Execution Plan, APOE, Operator Surface, Agent Workforce, MCP Transport |
| **FUNCTIONAL** | 3 | PLIx, Memory Record, Execution Gate |
| **PARTIAL** | 13 | Continuity Bundle, HHNI, Working Context, SEG, VIF, Delivery, Packet, Polycaste, Sync, Quality, SIS, Research, AI Engine, JOC, Embodiment, AIM-OS System |
| **DEGRADED** | 1 | CAS |
| **DOCTRINAL_ONLY** | 6 | Constitution, Canon, Identity, Authority, Capability, Geometric Runtime |

---

# Book III — Runtime Truth and Boundary Registers

## 1. Law of Book III

**Package presence does not equal runtime truth.**

A package in the repository is not proof that a system is operational. Runtime truth must be assessed by evidence: probes, logs, confirmed responses, or direct observation.

## 2. Runtime truth state law

The seven states form a strict ordering:

```
ALIVE > FUNCTIONAL > PARTIAL > DEGRADED > BROKEN > DOCTRINAL_ONLY > EXTERNAL_UNSETTLED
```

- **ALIVE**: Directly probed and confirmed responsive in the current environment
- **FUNCTIONAL**: Code exists, is exercised, strong evidence of operation — but not probed live recently
- **PARTIAL**: Some runtime presence but fragmented, incomplete, or environment-dependent
- **DEGRADED**: Was functional but decaying — missing siblings, reduced health, stale state
- **BROKEN**: Code exists but does not currently function
- **DOCTRINAL_ONLY**: Described in doctrine/architecture but has no sovereign runtime owner
- **EXTERNAL_UNSETTLED**: Truth depends on external state that cannot be settled locally

## 3. Runtime Truth Register — current assessment (2026-03-17)

```yaml
entries:
  - object_id: constitutional_law
    runtime_truth: DOCTRINAL_ONLY
    rationale: supreme law exists textually in AETHER_CONSTITUTION; no runtime policy engine
    last_assessed: 2026-03-17

  - object_id: teleological_canon
    runtime_truth: DOCTRINAL_ONLY
    rationale: central to project culture; not loadable as machine rule
    last_assessed: 2026-03-17

  - object_id: intent_calculus
    runtime_truth: FUNCTIONAL
    rationale: PLIx compiler exists; not universal across all surfaces
    last_assessed: 2026-03-17

  - object_id: bitemporal_memory_store
    runtime_truth: ALIVE
    rationale: CMC SQLite confirmed responsive; 190+ atoms; MCP tools operational
    evidence: store_memory/retrieve_memory probed successfully 2026-03-17
    last_assessed: 2026-03-17

  - object_id: continuity_bundle
    runtime_truth: PARTIAL
    rationale: capsule protocol is actively used (record_context_capsule MCP tool); but no sovereign schema family or resume API
    change_from_v1: upgraded from DOCTRINAL_ONLY — capsule practice is now real
    last_assessed: 2026-03-17

  - object_id: hierarchical_context_index
    runtime_truth: PARTIAL
    rationale: HHNI package exists with DVNS physics model; runtime bridge can fail by environment
    last_assessed: 2026-03-17

  - object_id: working_context
    runtime_truth: PARTIAL
    rationale: assembled in practice by context_bootloader; no sovereign object
    last_assessed: 2026-03-17

  - object_id: evidence_graph
    runtime_truth: PARTIAL
    rationale: SEG service boundary exists; graph density variable
    last_assessed: 2026-03-17

  - object_id: verification_framework
    runtime_truth: PARTIAL
    rationale: confidence tracking exists (track_confidence MCP tool); operational usage limited
    last_assessed: 2026-03-17

  - object_id: execution_plan
    runtime_truth: ALIVE
    rationale: plans are concretely represented and producible by APOE
    last_assessed: 2026-03-17

  - object_id: execution_gate
    runtime_truth: FUNCTIONAL
    rationale: gate logic is real and used in orchestration
    last_assessed: 2026-03-17

  - object_id: plan_orchestrator
    runtime_truth: ALIVE
    rationale: one of the strongest runtime centers; goal-to-plan compilation confirmed
    last_assessed: 2026-03-17

  - object_id: reflective_monitor
    runtime_truth: DEGRADED
    rationale: CAS package exists; health and activation can degrade; naming confusion persists
    last_assessed: 2026-03-17

  - object_id: agent_workforce
    runtime_truth: ALIVE
    rationale: 5 agents active across 4 platforms; genomes read on startup; capsule protocol enforced; comms doctrine followed daily
    evidence: Opus responding now; Sev active in Codex IDE; genome v4.0 loaded
    last_assessed: 2026-03-17

  - object_id: mcp_transport
    runtime_truth: ALIVE
    rationale: 10,925-line monolith server operational; 137+ tools registered; stdio transport active; HTTP bridge at port 5001
    evidence: multiple tools probed and confirmed 2026-03-17
    last_assessed: 2026-03-17

  - object_id: ai_engine
    runtime_truth: PARTIAL
    rationale: 14 MCP tools registered; facade exists; specialist spawner incomplete
    last_assessed: 2026-03-17

  - object_id: joc
    runtime_truth: PARTIAL
    rationale: JOC package exists; port 5011 server; 5-pillar dashboard; not fully deployed
    last_assessed: 2026-03-17

  - object_id: operator_surface
    runtime_truth: ALIVE
    rationale: Antigravity IDE operational as primary surface for Opus; Cursor IDE for Codex
    last_assessed: 2026-03-17

  - object_id: geometric_runtime
    runtime_truth: DOCTRINAL_ONLY
    rationale: quaternion_kernel and quaternion_math packages exist; no deployable substrate
    last_assessed: 2026-03-17
```

## 4. External Truth Boundary Register

These are truths the atlas cannot settle locally:

### 4.1 Off-branch / off-machine project truth
- **Surfaces**: Ghost Linux machine state, ops/relay branch, remote work
- **Nearest evidence**: repo residue, reports, operator discussion
- **Settlement**: Requires machine probe or operator confirmation

### 4.2 Host runtime extensions
- **Surfaces**: Antigravity extension runtime, Cursor extension state, local model availability
- **Nearest evidence**: package presence, adapter code
- **Settlement**: Host-specific runtime probe required
- **New finding (2026-03-17)**: Antigravity IDE internals reverse-engineered — `jetskiAgent/main.js` controls model cascade, `maxOutputTokens` patched from 16384 to 32768

### 4.3 Provider and credential state
- **Surfaces**: OpenAI relay, Anthropic relay, Gemini provider, Cerebras access
- **Settlement**: Credential validity probe + provider health check

### 4.4 Operator-confirmed precedence
- **Surfaces**: Route key precedence, unpublished priority decisions
- **Settlement**: Explicit operator ruling

## 5. Continuity Surface Register

### Continuity strata definitions

| Stratum | Meaning | Requirements |
|---------|---------|--------------|
| **C0** | No meaningful continuity | Work lost on reset |
| **C1** | Minimal | Recent chat trace + some instruction surface |
| **C2** | Basic | Status surfaces + capsule/checkpoint + memory tools |
| **C3** | Strong | Route identity stable + checkpoint discipline + authority explicit |
| **C4** | Full atlas-grade | Continuity bundle present + contradictions tracked + handoff lawful |

### Current continuity assessment

| Lane | Stratum | Strengths | Weaknesses |
|------|---------|-----------|------------|
| Opus (Antigravity) | **C3** | Capsule protocol active, MCP memory tools, genome loaded, status files | No formal bundle schema, route splits |
| Sev (Codex IDE) | **C2** | Chat docs, memory tools, North Star binding | Thin checkpoint practice, less capsule discipline |
| Codex (Cursor) | **C1–C2** | Recent chat, instruction surface | Weak status root, limited memory persistence |
| Gemini (CLI) | **C1** | Chat trace only | No persistent state, no capsule practice |
| Cross-machine | **C1** | ops/relay branch, handoff docs | Fragmented, no unified sync plane |

## 6. Canon Collision Register

| ID | Type | Conflicting Surfaces | Resolution |
|----|------|---------------------|------------|
| startup_precedence | First-read claims | AGENTS.md vs STARTUP.md vs North Star | Use functional first-read law (L1–L8) |
| transport_doctrine | MCP-first vs filesystem-first | MCP doctrine vs file-based practice | Route-bound — MCP when available, filesystem fallback |
| route_naming | Route identity | opus vs antigravity vs legacy aliases | Canonical route registry required |
| capsule_schema | Field set drift | Multiple capsule formats across agents | Canonical capsule schema family needed |
| genome_loading | Identity file precedence | Flat genomes vs per-agent directory genomes | Embodiment-bound load rule |
| current_state_precedence | State source priority | Checkpoint vs status file vs chat vs memory | Enforce S1–S5 precedence law |

---

# Book IV — Continuity and Retrieval Guidance

## 1. Governing law

**Continuity is not memory alone, and retrieval is not loading everything.**

Continuity requires structured preservation of what matters. Retrieval requires bounded selection of what the current task frame actually needs.

## 2. Continuity doctrine

### 2.1 Continuity Bundle definition

The **Continuity Bundle** is the smallest lawful object family sufficient for robust resume. It contains:

- **continuity_id**: Unique identifier
- **route_identity**: Who am I, which lane
- **embodiment**: What host/platform am I in
- **authority_posture**: Current authority constraints
- **mission_binding**: Active teleological reference
- **plan_reference**: Current plan and phase
- **contradiction_slice**: Known unresolved conflicts
- **next_action_posture**: What should happen next
- **degraded_feature_warnings**: What is currently broken or reduced
- **last_trusted_checkpoint**: Reference to last known-good state

### 2.2 Working Context definition

**Working Context** is the bounded active set loaded for the current task frame. It optimizes for sufficiency and lawfulness, not for completeness.

Components:
- **Law slice**: Governing law references relevant to this task
- **Plan slice**: Active plan, current phase, next steps
- **Dependency slice**: Code, docs, tests, contracts
- **Evidence slice**: Relevant evidence graph, live contradictions, witness anchors
- **Continuity slice**: Last checkpoint, route identity, next-action posture, degraded warnings
- **Boundary slice**: What is unresolved, what cannot be settled locally

### 2.3 Sufficiency rule

Working Context is sufficient when it contains enough material to perform the next lawful action without:
- violating canon,
- misreading route identity,
- missing a known contradiction,
- ignoring a high-blast-radius dependency,
- or mistaking uncertain state for settled state.

Sufficiency is about lawful adequacy, not token count.

### 2.4 Compression-before-loss rule

When context pressure increases, compress in this order (preserve from top):
1. Governing law
2. Current plan and route identity
3. Contradictions and risks
4. Next-action posture
5. Unresolved boundaries
6. Lower-priority historical detail (compress here first)

## 3. Current-state precedence

When current-state surfaces disagree:

1. **S1 — Law-bearing current state** (constitutional projection, authority posture)
2. **S2 — Structured continuity state** (checkpoint, capsule, continuity manifest)
3. **S3 — Operational status state** (status file, current priorities)
4. **S4 — Active interaction state** (current chat, live session)
5. **S5 — Historical interpretive state** (old reports, archived chats)

**Operator override rule**: When the President explicitly overrides, record what was overridden, by whom, for what scope, and whether persistent or session-local.

## 4. Retrieval zones

| Zone | Retrieval Priority | Content |
|------|-------------------|---------|
| **Active Canon** | 1 (default load) | AETHER_CONSTITUTION, AETHER_KERNEL, projections, live canonical extensions, current-state surfaces |
| **Active Runtime Support** | 2 (load as needed) | Package ownership maps, runtime truth registers, plans, continuity manifests |
| **Lineage** | 3 (load for interpretation) | SEEDv1, ION bridge material, predecessor syntheses |
| **Research** | 4 (load only when invoked) | Geometric Runtime (Seedkernel), speculative substrate |
| **Quarantine** | 5 (never by default) | False-OS absolutist docs, stale operational docs, outdated "authoritative" files |

## 5. Continuity handoff law

When work is paused or handed off, preserve at minimum:
- Route identity, embodiment identity, authority posture
- Active plan reference, current phase
- Contradiction/risk slice
- Next-action posture
- Degraded-feature warnings
- Unresolved external boundaries
- Last trusted checkpoint/capsule reference

## 6. Continuity decay hazards

Active hazards that degrade continuity:
- Split route names (opus vs antigravity)
- Stale current-state documents
- Duplicate inbox or status roots
- Capsule schema drift across agents
- Plan references without continuity anchors
- Host changes without embodiment descriptors
- External truth gaps left implicit
- Reliance on chat alone where bundles are absent

---

# Book V — Package Ownership and Migration Maps

*This book was absent in atlas v1. Written fresh for v2.*

## 1. Law of Book V

**Every canonical object should have exactly one primary runtime owner.** Objects without owners drift toward doctrine-only status regardless of their architectural importance.

## 2. Package inventory — 76+ packages

The AIM-OS repository contains 76+ packages in `packages/`. Genome count: 158+ files in `.agent/genomes/` (cores, platforms, affinities, per-agent, legacy). They fall into these tiers:

### Tier 1 — Core Infrastructure (actively operational)
| Package | Canonical Object | Status |
|---------|-----------------|--------|
| `cmc_service` | Bitemporal Memory Store | ALIVE |
| `aimos_mcp` | MCP Transport System | ALIVE |
| `apoe` | Plan Orchestrator | ALIVE |
| `apoe_runner` | Plan execution runtime | ALIVE |
| `plix` | Intent Calculus | FUNCTIONAL |

### Tier 2 — Engine Layer (partially operational)
| Package | Canonical Object | Status |
|---------|-----------------|--------|
| `hhni` | Hierarchical Context Index | PARTIAL |
| `seg` | Evidence Graph | PARTIAL |
| `vif` | Verification Framework | PARTIAL |
| `context_bootloader` | Working Context assembly | PARTIAL |
| `cas` | Reflective Monitor | DEGRADED |
| `sis` | Improvement Engine | PARTIAL |
| `sdfcvf` | Change Coherence Framework | PARTIAL |

### Tier 3 — Interface & Surface Layer
| Package | Canonical Object | Status |
|---------|-----------------|--------|
| `joc` | Joint Operations Center | PARTIAL |
| `ide_chat_app` | IDE Chat Interface | PARTIAL |
| `antigravity-extension` | Antigravity DevMode | PARTIAL |
| `mcp_console` | MCP Console | PARTIAL |

### Tier 4 — Agent & Orchestration
| Package | Related Domain | Status |
|---------|---------------|--------|
| `agent` | Agent Workforce | FUNCTIONAL |
| `blueprint_system` | Blueprint storage and validation | PARTIAL |
| `gemini_agent` | Gemini CLI agent host | PARTIAL |
| `adaptive_system` | Adaptive Nervous System | PARTIAL |
| `aim-os-integration` | AIM-OS integration layer | PARTIAL |
| `specialist_system` | Specialist Swarm | PARTIAL |
| `ai_collaboration` | AI Comms | PARTIAL |
| `orchestration_builder` | Chain building | PARTIAL |

### Tier 5 — Research & Experimental
| Package | Research Domain |
|---------|----------------|
| `quaternion_kernel` | Geometric Runtime |
| `quaternion_math` | Quaternion operations |
| `autonomous_research_dream` | ARD research |
| `deepsearch` | Deep search |
| `holographic_memory` | Experimental memory |
| `consciousness_*` (5 packages) | CAS experiments |
| `temporal_consciousness` | Temporal modeling |

### Tier 6 — Support & Integration
| Package | Function |
|---------|----------|
| `llm_client` | LLM provider abstraction |
| `router` / `router_api_server` | Request routing |
| `schemas` | Shared schema definitions |
| `shared` | Common utilities |
| `safety_systems` | Safety guardrails |
| `aimos-sdk` | SDK for tool integration |
| `browser-automation-service` | BAS (Seer-adjacent). **CredentialVaultService** at `src/services/credentialVaultService.ts` — credential vault, cost monitor; HTTP API `/api/connections/vault/*`; not MCP-exposed |

## 3. Ownership gaps

Objects without primary runtime owners (critical build targets):
1. **Constitutional Law** — needs `packages/constitution/`
2. **Teleological Canon** — needs `packages/canon/`
3. **Continuity Bundle** — needs `packages/continuity/`
4. **Working Context** — needs promotion from `context_bootloader` to sovereign package
5. **Authority System** — needs `packages/authority/`
6. **Capability Ledger** — needs promotion from `capability_awareness` to sovereign ledger
7. **Source Synchronization** — needs `packages/sync/`
8. **Embodiment** — needs `packages/embodiment/`

## 4. Migration status codes

| Code | Meaning |
|------|---------|
| **M0** | No canonical header, no atlas link |
| **M1** | Canonical header proposed but not yet in repo |
| **M2** | Canonical header present, schema stubs pending |
| **M3** | Schema stubs present, runtime integration pending |
| **M4** | Fully atlas-integrated |

Current status: All packages at **M0**. No CANONICAL.md files have been added to any package root.

---

# Book VI — Research Branches and Quarantine Boundaries

*This book was absent in atlas v1. Written fresh for v2.*

## 1. Law of Book VI

**Research material may not silently impersonate deployed runtime truth.** All research branches must be clearly quarantined from operational authority until implementation proof is provided.

## 2. Active research branches

### 2.1 Geometric Runtime / Seedkernel (A6)
- **Packages**: `quaternion_kernel`, `quaternion_math`
- **Status**: Canonical specification exists (Book X), no deployed substrate
- **Key concepts**: QAddr addressing, 4-syscall basis, 7 kernel axioms, κ/λ/ρ field dynamics
- **Promotion requirement**: Bounded implementation proof of at least one syscall with witnesses

### 2.2 Consciousness Experiments (A6)
- **Packages**: `consciousness_analyzer`, `consciousness_creativity_engine`, `consciousness_error_learning`, `consciousness_learning_engine`, `consciousness_optimization_detector`, `temporal_consciousness`
- **Status**: Experimental code, naming prone to overclaim
- **Caution**: CAS-adjacent experiments must not be conflated with sovereign identity or personhood proof

### 2.3 Holographic Memory (A6)
- **Package**: `holographic_memory`
- **Status**: Experimental alternative memory model
- **Relation to canon**: Must not override CMC as primary memory truth

## 3. Quarantined material (A7)

- **OmniBus family**: Superseded by Constitutional Law — false-OS absolutism and persistence theater
- **deepthinkOS absolutism**: Concepts retained, theatrical OS claims quarantined
- **BCI as single term**: Split into HHNI + Source Synchronization + Working Context
- **CAS as identity claim**: Monitoring ≠ sovereign identity — hard supersession

## 4. Research-to-canon promotion law

Material may move from Research (A6) to Operational (A4) only when:
1. Implementation proof exists (not just specification)
2. Runtime owner is identified
3. Atlas registry entry is created
4. Integration with existing canonical objects is mapped
5. No canon collision is introduced without resolution

---

# Book VII — Deployment Projections

*This book was absent in atlas v1. Written fresh for v2.*

## 1. Law of Book VII

**The same governance system may project different runtime configurations depending on embodiment, host, and mission context.** These projections are not separate systems — they are views of the same canon.

## 2. Projection types

### 2.1 Boot Projection
What loads at agent startup:
- `.agent/STARTUP.md` → genome → comms doctrine → MCP bootstrap → memory retrieval → capsule check
- Embodiment-specific (Opus reads Antigravity genome, Sev reads Codex genome)

### 2.2 Runtime Projection
What governs active work:
- Active plan, working context, capsule discipline, tool usage
- Authority posture based on task type
- Continuity emission requirements

### 2.3 Recovery Projection
What activates when contradiction or failure occurs:
- Root-cause analysis protocol (not apology)
- Degraded-feature declaration
- Escalation to higher inference if threshold crossed

### 2.4 Research Projection
What governs speculative work:
- Research branch quarantine boundary enforced
- Lineage preserved but not loaded as authority
- Clearly marked as hypothesis

## 3. Embodiment-specific projections

| Agent | Platform | Boot Projection | Key Differences |
|-------|----------|----------------|-----------------|
| **Opus** | Antigravity IDE | genome → capsule → MCP → memory | Full MCP native, capsule protocol enforced, 32K output |
| **Sev** | Codex IDE | SEV_NORTH_STAR → genome → MCP bootstrap | MCP via bootstrap script, CEO authority |
| **Codex** | Cursor IDE | cursor_codex_instructions → MCP bootstrap | MCP via bootstrap script, builder scope |
| **Gemini** | Google CLI | Minimal projection | Research-oriented, unlimited workers |
| **Composer** | Cursor Composer | cursor_composer_instructions | Audit/refactor scope only |

## 4. Platform-specific projections

### 4.1 Antigravity IDE (Opus)
- **Primary agent**: Opus (COO)
- **MCP**: Native stdio transport; full tool access
- **Capsule**: PRE/POST enforced via `record_context_capsule`
- **Output**: 32K tokens (maxOutputTokens patched)
- **Genome**: `.agent/genomes/opus/`, `.agent/genomes/antigravity.genome.md`

### 4.2 Cursor IDE (Codex, Composer)
- **Codex**: Lead Builder; MCP via bootstrap script; builder scope
- **Composer**: Auditor-Mapper; audit/refactor scope; drift detection
- **Genome**: `.agent/genomes/codex/`, `.agent/genomes/composer/`

### 4.3 Gemini CLI
- **Agent**: Gemini (Research Specialist)
- **Projection**: Minimal; research-oriented; unlimited workers
- **Continuity**: C1 — chat trace only; no capsule practice
- **Genome**: `.agent/genomes/gemini/`, `.agent/genomes/gemini_web.genome.md`

### 4.4 Local + API
- **Echo Forge Loop**: `echo-forge-loop/` at repo root (not `apps/echo-forge-loop/` — apps/ does not exist)
- **Local server**: `echo-forge-loop/server/` — FastAPI SSE backend
- **Supabase**: `echo-forge-loop/supabase/` — hosted persistence
- **JOC**: Port 5011; 5-pillar dashboard
- **MCP HTTP bridge**: Port 5001

---

# Book VIII — Atlas Self-Governance

*This book was absent in atlas v1. Written fresh for v2.*

## 1. Law of Book VIII

**The atlas must maintain itself.** It is not a static document but a living governance system that requires regular refresh, honest assessment, and disciplined change tracking.

## 2. Atlas change governance

### Change classes
| Class | Scope | Authority Required |
|-------|-------|-------------------|
| **G0** | Runtime truth refresh | Any agent with evidence |
| **G1** | New registry entry | Any agent, ratified by review |
| **G2** | Schema change | Agent + Presidential awareness |
| **G3** | Authority class change | Presidential approval required |
| **G4** | Structural reorganization | Presidential approval required |

### Change log format
```yaml
- change_id: [identifier]
  change_class: [G0–G4]
  description: [what changed]
  affected_objects: [list]
  evidence_basis: [what justified this]
  author: [who made the change]
  date: [when]
```

## 3. Atlas refresh cadence

| Register | Recommended Cadence |
|----------|-------------------|
| Runtime truth | Every major session or weekly |
| External truth boundaries | On environment change |
| Canon collision register | On collision discovery |
| Continuity surface register | On lane state change |
| Package ownership map | On package add/remove |

## 4. Atlas debt register (current)

| ID | Severity | Object | Description |
|----|----------|--------|-------------|
| debt_001 | CRITICAL | Constitutional Law | No runtime policy engine |
| debt_002 | CRITICAL | Continuity Bundle | No sovereign schema family |
| debt_003 | CRITICAL | Working Context | No first-class manifest |
| debt_004 | CRITICAL | Authority System | Rules scattered across docs |
| debt_005 | CRITICAL | Capability Ledger | No time-bound proof store |
| debt_006 | CRITICAL | Source Sync | No sovereign sync plane |
| debt_007 | HIGH | Embodiment | No formal descriptor system |
| debt_008 | HIGH | Packages | No CANONICAL.md files in any package |
| debt_009 | HIGH | Registers | Runtime truth needs regular refresh |
| debt_010 | HIGH | Route registry | No canonical route registry |
| debt_011 | HIGH | Capsule schema | Not canonically normalized |
| debt_012 | MEDIUM | MCP server | Monolith needs consolidation (frozen) |

## 5. Anti-sediment rules

1. Old documents must not remain loaded as if current without review
2. Route name splits must be resolved, not accumulated
3. Status files that contradict each other must trigger collision registration
4. Bygone decisions cannot be loaded as live constraints
5. Runtime truth must be re-assessed, not assumed stable

---

# Book IX — Governed Ingestion and Deterministic Retrieval

## 1. Governing law

**Deterministic retrieval is only as trustworthy as the governed write that produced it.**

If bad structure enters the store, bad retrieval becomes cheap, fast, and repeatable. That is worse than noisy retrieval.

## 2. The key inversion: compute-at-write

| Old Pattern (compute-at-read) | New Pattern (compute-at-write) |
|------------------------------|-------------------------------|
| Ingestion is lazy | Ingestion is expensive and disciplined |
| Storage is weakly structured | Structure is created once |
| Retrieval guesses | Retrieval is deterministic |
| Model pays repeatedly | System pays reasoning tax once |
| Expensive per cycle | Near-zero marginal retrieval cost |

## 3. The 10-stage governed write path

Every new material entering the system passes through:

| Stage | Name | Function |
|-------|------|----------|
| **W1** | Intake | Receive candidate material (code, docs, plans, observations) |
| **W2** | Structural Parsing | Parse by type (AST for code, section/concept for docs) |
| **W3** | Object Classification | Identify canonical object family |
| **W4** | Evidence Classification | Classify epistemic type (observed / sourced / derived / assumed / speculative / contradicted) |
| **W5** | Authority Classification | Assign authority class (A0–A7) |
| **W6** | Zone Assignment | Assign retrieval zone (Active Canon / Runtime Support / Lineage / Research / Quarantine) |
| **W7** | Contradiction Checking | Check against existing truths, route identity, precedence rules |
| **W8** | Verification | Apply immune layer — VIF verification, invariant checks, honesty checks |
| **W9** | Provenance Write | Persist with provenance, time, authority, evidence class, contradiction status |
| **W10** | Revision Propagation | Identify downstream objects now stale or needing re-verification |

## 4. The epistemic immune system

The write plane includes defensive intelligence:
- VIF confidence tracking and witness generation
- Contradiction protocol and collision detection
- Evidence class enforcement
- Runtime honesty law (no false claims of deployment)
- Canon collision register
- Continuity safeguards

These prevent: hallucinated structure, false authority, stale descendants, route ambiguity, and speculative drift from entering retrievable truth.

## 5. Code vs semantic ingestion regimes

| Regime | Type | Government Source |
|--------|------|------------------|
| **Code** | Source code, configs, schemas | Compiler/AST provides structure — lower ambiguity |
| **Semantic** | Plans, decisions, research, memory | Atlas governance provides structure — higher ambiguity, needs stronger verification |

## 6. Three-layer cognition model

| Layer | Name | Function | Model Type |
|-------|------|----------|-----------|
| **C1** | Organizer | Ingestion, structuring, classification, continuity maintenance, atlas update | High-context LLM |
| **C2** | Reactive Worker | Execution, retrieval, routing, tool use, threshold checks | Deterministic or low-inference |
| **C3** | Escalation | Deep reasoning, recovery, ambiguity resolution, research | Triggered on threshold breach |

### Escalation triggers (C2 → C3):
- Contradiction load exceeds tolerance
- Evidence sufficiency below minimum
- Continuity bundle weak or missing
- Current-state surfaces irreconcilably disagree
- Authority is ambiguous
- Capability freshness stale
- Route identity unstable
- Task exits known procedural space
- Novel or under-modeled situation encountered

This insight: **the system becomes more intelligent by becoming more organized, not only by becoming more inferential.**

---

# Book X — Kernel, Syscalls, and Geometric Runtime Definition

## 1. Governing law

**The kernel may now be specified canonically, but its promotion from defined substrate to deployed substrate still requires bounded implementation proof.**

Book X defines the kernel seriously while preserving the honesty boundary between:
- canonical kernel specification,
- translational implementation,
- and fully deployed substrate reality.

## 2. Naming stack — Kernel resolution

**Two distinct concepts:**

| Concept | Name | Authority | Purpose |
|---------|------|------------|---------|
| **Aether Kernel** | AETHER_KERNEL | A1 | Boot core; governance projection; live law at startup |
| **Geometric Runtime** | Seedkernel | A6 | Research substrate; QAddr, syscalls; not yet deployed |

The Aether Kernel (A1) is the compact live core agents load. The Geometric Runtime (A6) is the research branch — quaternion addressing, 4-syscall basis. Different things, different names.

| Level | Name | Purpose |
|-------|------|---------|
| **Canonical** | Geometric Runtime | Registry name — states function (A6 research) |
| **Boot kernel** | Aether Kernel | A1 — binds to AETHER_CONSTITUTION governance |
| **Cultural/research** | Seedkernel | Project identity for Geometric Runtime |
| **Interface** | Kernel | System-facing term (context-dependent) |

## 3. The kernel defined

The kernel is the lowest governed computational substrate upon which the higher architecture can execute in a geometrically meaningful, verifiable, replayable, and policy-constrained way.

It is defined by:
- Explicit spatiotemporal addressing (QAddr)
- Explicit transition rules (selection rules)
- Witness-bearing execution
- Deterministic replay
- Governed syscall surface
- Field-aware state dynamics (κ/λ/ρ)
- Kernel-level value-floor enforcement

## 4. Seven kernel axioms

| Axiom | Law |
|-------|-----|
| **K1** | Exclusive situatedness — one QAddr-state per time slice |
| **K2** | Lawful transitions only — selection rules + governance constraints |
| **K3** | Witness completeness — every operation produces verification trace |
| **K4** | Deterministic replay — same input → same output |
| **K5** | Governance supremacy — AETHER_CONSTITUTION value-floor always applies |
| **K6** | Budget conservation — no operation exceeds authorized Hamiltonian |
| **K7** | Field continuity — field values evolve continuously |

## 5. QAddr: the kernel address model

**QAddr = policy-bearing geometric address in governed spacetime**

Components:
1. **Quantum/policy tuple**: Trust tier, capability class, orientation channel, authority mode
2. **Spatial key**: Morton4D or equivalent locality-preserving encoding
3. **Orientation key**: S³/quaternion-aware binning

QAddr unifies:
- Privilege with locality
- Movement with address
- Mode with geometry
- Retrieval with structured position

## 6. Four-syscall basis

| Syscall | Verb | Meaning | Kernel-Level Role |
|---------|------|---------|-------------------|
| `place` | Introduction | Governed emplacement into substrate | How something becomes substrate-real |
| `move` | Transformation | State transition through geometric/policy space | Execute governed transitions |
| `sense` | Perception | Bounded query: nearby, aligned, active, visible | The perception face |
| `emit` | Propagation | Outward effect, signal, field update | The communicative face |

These map to the most universal substrate verbs: **introduction, transformation, perception, propagation.**

## 7. Syscall law

Each syscall must define:
- **Preconditions**: caller validity, QAddr validity, capability sufficiency, budget sufficiency
- **Postconditions**: state change, field updates, cost deduction, witness creation, invariant preservation
- **Witness emission**: operation type, source/target, QAddr, timestamps, proof of pre/postconditions
- **Cost accounting**: Hamiltonian budget model — validity AND burden

## 8. Selection rules

State movement is constrained by:
- Privilege deltas
- Capability class adjacency
- Locality/directional continuity
- Mode/authority transition guards

**Security is partly encoded in the geometry of allowed motion.** This is deeper than "check permission at the edge."

## 9. Kernel promotion status

The kernel is currently: **DEFINED (A6) — not yet DEPLOYED (A4)**

Promotion requires:
1. At least one syscall implemented with witnesses
2. QAddr encoding operational
3. Selection rules enforced
4. Replay demonstrated for bounded scenario
5. Integration point with at least one canonical service (likely VIF or CMC)

---

# Appendix A — Aliases and Supersessions

## Key supersessions

| Item | Superseded By | Class | Reason |
|------|--------------|-------|--------|
| OmniBus family | Constitutional Law | Hard | False-OS absolutism |
| deepthinkOS absolutism | Constitution + Canon + Context | Soft | Theatrical OS claims |
| BCI as single term | HHNI + Sync + Context | Hard | Compound hides distinct objects |
| CAS as identity | Reflective Monitor + Identity | Hard | Monitoring ≠ identity |
| "host" as object name | Embodiment | Soft | Embodiment is more precise |
| adapter (dual term) | Domain Contract + Operational Packet | Hard | One term doing two jobs |

---

# Appendix B — Atlas v2.0 Change Log

```yaml
changes:
  - change_id: atlas_v2_001
    change_class: G4
    description: Complete rewrite from atlas.txt (v1) to atlas_v2.md (v2)
    author: Opus (COO)
    date: 2026-03-17
    evidence:
      - full 9821-line read of atlas.txt
      - atlas_complete_index.md artifact
      - atlas_deep_analysis.md artifact
      - live runtime probes 2026-03-17
      - Antigravity reverse engineering findings
    changes_made:
      - Added missing Books V, VI, VII, VIII
      - Added 4 new canonical objects (Agent Workforce, MCP Transport, AI Engine, JOC)
      - Updated runtime truth assessments with 2026-03-17 evidence
      - Upgraded Continuity Bundle from DOCTRINAL_ONLY to PARTIAL
      - Upgraded Embodiment from DOCTRINAL_ONLY to PARTIAL
      - Added concrete embodiment instances
      - Cleaned structural issues (excessive blank lines, numbering gaps)
      - Added table of contents
      - Converted from .txt to .md for proper formatting
      - Removed duplicated prose/YAML content (YAML artifact packs preserved in atlas.txt v1 as lineage)
      - Added Antigravity host platform to external truth boundaries
      - Added package tier classification (74 packages in 6 tiers)
      - Added migration status codes (M0–M4)

  - change_id: atlas_v2_1_001
    change_class: G2
    description: Aether-OS foundation doc alignment (COMPOSER task 2026-03-18)
    author: COMPOSER
    date: 2026-03-18
    changes_made:
      - Cross-referenced AETHER_CONSTITUTION, AETHER_KERNEL, AETHER_INTERFACE
      - Added 6 packages: blueprint_system, gemini_agent, adaptive_system, aimos_mcp, aim-os-integration, mcp_console
      - Fixed apps/ paths: echo-forge-loop at root (apps/ does not exist)
      - Updated genome count: 158+ files
      - Updated package count: 76+
      - Expanded Book VII with platform-specific projections (Antigravity, Cursor, Gemini CLI, Local+API)
      - Added CredentialVaultService under Browser Automation Service
      - Resolved Kernel naming: Aether Kernel (A1) vs Geometric Runtime (A6)
```

---

# Final Statement

This atlas exists so the project can know itself honestly.

It defines:
- what is supreme (AETHER_CONSTITUTION, human sovereignty),
- what exists (32 canonical objects, 76+ packages, 158+ genome files, 5 embodied agents),
- what is real (6 ALIVE, 3 FUNCTIONAL, 13 PARTIAL, 1 DEGRADED, 6 DOCTRINAL_ONLY),
- how work continues (continuity doctrine, capsule protocol, handoff law),
- where the honest boundaries are (external truths, research quarantine, supersessions),
- and what must be built next (8 ownership gaps, 12 debt items, 0 CANONICAL.md files).

The atlas is not an aspiration document. It is a map of territory — what is, not what we wish it were. When the territory changes, the atlas must change. When the atlas drifts from the territory, the atlas is wrong.

That is the sovereign orientation law.
