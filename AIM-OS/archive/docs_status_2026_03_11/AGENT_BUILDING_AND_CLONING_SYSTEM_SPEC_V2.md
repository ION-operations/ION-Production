# Agent Building and Cloning System Spec v2

Status: Draft (team review)  
Date: 2026-03-04  
Audience: Braden, Agent Aether, Codex agents, Opus, Composer, Gemini  
Purpose: Unified, implementation-ready definition of agents, cloning, specialization, and handoff in AIM-OS.

---

## 1) Problem Statement

AIM-OS already has strong pieces:
- Specialist activation with thresholds and work detection
- APOE role dispatch and orchestration
- Identity continuity protocol for MCP operations
- Extensive Agent Genome architecture documentation

But these are still partially separated in runtime. This spec unifies them into one operating model.

---

## 2) Canonical Definitions

1. Role  
Temporary execution function for a step (planner, retriever, reasoner, verifier, builder, critic, operator, witness). Roles are not persistent identities.

2. Agent  
Persistent operational identity with:
- Behavioral DNA: goals, policies, guardrails, tool permissions, skills, playbooks
- Knowledge DNA: isolated context banks, indexed memory, episode history
- Measured performance: confidence, cost, latency, quality outcomes

3. Specialist Agent  
Agent with bounded domain ownership and activation thresholds.

4. Clone  
New persistent agent identity derived from a parent agent genome plus explicit mutation delta.

5. Genome  
Versioned, bitemporal snapshot of an agent (identity, policies, competence, context, metrics, experience, lineage).

6. Handoff  
Explicit transfer of ownership between agents based on relevance, confidence, and scope gates.

7. Fission  
Splitting one over-broad agent into two or more specialists when breadth causes performance decay.

---

## 3) Why Agents, Not Role-Switching One Agent

Single-agent role switching is useful inside a task, but insufficient as the core architecture:
- Context contamination increases across unrelated domains.
- Cross-domain prompt/rule interference reduces reliability.
- Specialized learning is hard to preserve and measure over time.
- Provenance and accountability become ambiguous.

Persistent specialist agents solve this:
- Stable behavioral policy per domain
- Warm, domain-specific context banks
- Measurable evolution with lineage
- Clean handoff and ownership contracts

Decision rule:
- Use role switching inside an agent for step execution.
- Use separate agents/clones for persistent specialization.

---

## 4) Existing Foundations in AIM-OS (Ground Truth)

1. Specialist runtime exists now:
- `packages/specialist_system/specialist_registry.py`
- `packages/specialist_system/activation_system.py`
- `packages/specialist_system/work_detector.py`

Key thresholds already implemented:
- Ownership: `>= 0.90`
- Activation: `>= 0.70`
- Consultation: `>= 0.60`

2. Role runtime exists now:
- `packages/apoe/role_dispatcher.py`

3. Identity continuity protocol exists (required direction):
- `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`

4. Agent Genome architecture is well-documented:
- `knowledge_architecture/systems/agent_genome/*`
- `knowledge_architecture/AETHER_MEMORY/RA_AGENT_GENOME_IMPLEMENTATION_PLAN.md`

5. Governance model exists:
- `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`
- `docs/CODEX_AGENT_EXECUTION_CHARTER_V1.md`

Runtime gap to close:
- `packages/agent_genome/` implementation is not present as a production runtime package yet.

---

## 5) Unified Architecture (Target)

### 5.1 Control Plane
- Agent Registry: identity, ownership, status
- Genome Registry: snapshot, resolve, clone, diff, promote
- Policy Engine: autonomy mode, safety, budget, quality gates

### 5.2 Execution Plane
- Work Detector -> Specialist Activation -> Owning Agent
- Owning Agent executes via APOE role chain
- Handoff when thresholds fail

### 5.3 Data Plane
- CMC: memory channels + genome snapshots (bitemporal)
- HHNI: index agent skills/tools/playbooks/episodes
- SEG: shared knowledge links and contradiction traces
- VIF: confidence + witness trail for agent decisions

### 5.4 Interface Plane
- JOC Agent Builder page:
  - create/clone/promote agents
  - inspect lineage and context health
  - view handoff chain and confidence/cost signals

---

## 6) Agent Genome Minimum Runtime Contract

Each active agent version must include:
- `id`, `version`, `parent`, `lineage`
- `purpose`, `goals`, `budgets`, `autonomy`
- `tools_manifest`, `skills`, `playbooks`
- `memory_channels`, `rag_collections`, `shared_knowledge_refs`
- `metrics` (confidence, cost, latency, quality)
- `episodes` references
- `valid_from`, `tx_time`, `valid_to`

Runtime requirements:
- Immutable version directories
- `alias.current` pointer for active version
- Clone mutation file (explicit delta)
- Diff-able profile/policy/context/skills/tools changes

---

## 7) Lifecycle Protocol

1. Onboard
- Register agent identity.
- Create baseline genome.
- Create isolated channels.
- Require `agent_name` attribution for operations.

2. Activate
- Detect work -> score relevance.
- Assign ownership/activation/consultation.

3. Execute
- Build role chain via APOE inside owning agent.
- Log witnesses + traces.

4. Learn
- Store episodes and summary deltas.
- Update metrics.

5. Snapshot
- Write immutable genome version.
- Update `alias.current` only after gates pass.

6. Clone
- `clone(parent_ref, new_agent_id, mutation_delta)`.
- New writable channels; shared knowledge remains read-only.

7. Promote
- Run eval/tournament.
- Enforce VIF confidence, parity, and budget gates.

8. Retire/Archive
- Freeze alias.
- Keep lineage searchable.

---

## 8) Handoff and Fission Policy

### 8.1 Handoff (task-time)
- Keep current specialist thresholds as primary gate:
  - ownership >= 0.90
  - activation >= 0.70
  - consultation >= 0.60
- Force handoff when:
  - confidence drops under agent policy floor
  - budget violation risk exceeds policy
  - scope boundary violated by mission packet

### 8.2 Fission (evolution-time)
Compute a `FissionScore` over rolling episodes:
- Domain entropy (breadth spread)
- Context-switch frequency
- Confidence decay by domain
- Token waste due to irrelevant context
- Latency/cost drift

Recommendation:
- Trigger clone recommendation when `FissionScore >= 0.65` for sustained window (for example 20+ episodes) and specialist candidate consistently outperforms baseline.

---

## 9) Context Bank Model

Each agent gets isolated writable channels:
- `short` (episode/task)
- `scratch` (session)
- `long` (agent memory)
- `ops` (mission/execution metadata)

Shared read-only knowledge:
- SEG pointers
- curated HHNI collections

Rules:
- No direct cross-clone writes.
- Share via explicit publish/subscribe artifacts with provenance.
- Apply TTL + compaction to avoid unbounded context growth.

---

## 10) Governance and Quality Gates

Required for production:
1. Mission packet before specialist delegation.
2. Agent identity attribution in MCP operations.
3. Evidence trail for ownership/handoff decisions.
4. VIF confidence gate + budget gate enforcement.
5. SDF-CVF parity enforcement for code/docs/tests/traces.

---

## 11) Delivery Plan (Pragmatic)

Phase 0: Contract Alignment
- Finalize this spec and schemas.
- Decide canonical runtime package location (`packages/agent_genome`).

Phase 1: Runtime Core
- Implement registry + snapshot + resolve + diff + clone APIs.
- Integrate `alias.current` workflow.

Phase 2: Specialist + APOE Integration
- Wire specialist ownership result to APOE chain execution.
- Persist handoff metadata and witnesses.

Phase 3: Context Evolution
- Implement channel isolation manager and compaction policy.
- Add episode capture + metrics updater.

Phase 4: Promotion Engine
- Add tournament runner + gate evaluator.
- Implement promotion/rollback workflow.

Phase 5: JOC Surface
- Add Agent Builder/Clone dashboard and lineage inspector.

---

## 12) Team Assignment Shape

1. Codex agents
- Spec authority, runtime implementation, gate wiring, integration spine.

2. Opus
- JOC UI for Agent Builder and operational views, bound to stable contracts.

3. Composer
- Indexing, documentation harmonization, schema docs, audit trails.

4. Gemini
- Independent audit: policy correctness, risk review, gate integrity.

---

## 13) Immediate Next Deliverables

1. Create `packages/agent_genome/` scaffold with:
- registry
- genome manager
- clone API
- promotion gate API

2. Add `agent_name` + `agent_genome_ref` fields to orchestration/messaging metadata.

3. Add first fission telemetry collector:
- context switching
- confidence decay
- cost/latency drift

4. Add test set:
- clone isolation
- lineage integrity
- promotion gate pass/fail
- handoff correctness

---

## 14) Acceptance Criteria

System is production-usable when:
1. Agents can be snapshotted, cloned, and resolved deterministically.
2. Clone memory isolation is enforced with tests.
3. Ownership/handoff is logged with reproducible rationale.
4. Promotion cannot bypass quality gates.
5. JOC can display agent lineage, status, and gate state.

---

## 15) Notes on Opus Proposal Integration

Adopted directly:
- Two-pillar agent definition (rules/skills + context banks)
- Specialization-threshold rationale
- Need for fission detection and JOC management UI

Adjusted for implementation realism:
- Runtime genome package is currently a gap, not a completed implementation.
- Specialist runtime and APOE runtime are available now and should be bridged first.
- Governance contracts (COO scope, mission packets, identity protocol) are mandatory from day one.

