# ION Orchestration Plan v2
## Execution Plan for the ION Master Plan

**Author:** Opus (COO)  
**Date:** 2026-03-21  
**Governing document:** [ION_MASTER_PLAN.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/ION_MASTER_PLAN.md)  
**Living document — updated every session**

---

> This is the session-by-session BUILD ORDER for the ION Master Plan.
> The Master Plan defines WHAT ION is. This document defines HOW and WHEN to build it.
> Every item here traces back to a specific section in the Master Plan.

---

## Phase-to-Code Map: What Exists vs What's Needed

### Master Plan Phase 1: Ion Engine (§VIII — "Build the core runtime")

**STATUS: ✅ CORE COMPLETE — 547 tests passing. Needs end-to-end verification.**

| Master Plan Requirement | Existing Implementation | Lines | Tests | Status |
|------------------------|------------------------|-------|-------|--------|
| Ion parser — read frontmatter + body | `ion/parser.py` | 376 | 63 | ✅ Done |
| Ion writer — governed write (10 stages) | `ion/governed_write.py` | 402 | 46 | ✅ Done |
| Graph builder — traverse bonds, build adjacency | `ion/graph.py` | 384 | 45 | ✅ Done |
| Threshold evaluator — activation/escalation/invalidation | `ion/threshold.py` | 319 | 41 | ✅ Done |
| Manifest manager — auto-update manifest | `ion/manifest.py` | 429 | 55 | ✅ Done |
| File watcher — detect changes, trigger hooks | `ion/watcher.py` | 105 | — | ⚠️ Not exercised |
| Ion data model | `ion/model.py` | 801 | 135 | ✅ Done |
| In-memory index | `ion/index.py` | 318 | 55 | ✅ Done |
| Ion store (filesystem CRUD) | `ion/store.py` | 380 | 57 | ✅ Done |
| Bridge to Victus infrastructure | `ion/bridge.py` | 45 | — | ✅ Done |
| Navigator (cognitive loop traversal) | `ion/navigator.py` | 404 | 50 | ✅ Done |
| Bootstrap (create initial ion network) | `ion/bootstrap.py` | 108 | — | ⚠️ Not tested e2e |
| CLI interface | `ion/cli.py` | 320 | — | ⚠️ Not tested e2e |
| API endpoints | `ion/api.py` | 246 | — | ⚠️ Not wired into server |

**Remaining Phase 1 work:**
1. Run bootstrap end-to-end, create a real ion network on disk
2. Verify CLI against bootstrapped network
3. Wire API into server.py
4. Run navigator through a full 7-step loop on real ions

---

### Master Plan Phase 2: Aether Interface (§VIII — "Build the chat/builder interface")

**STATUS: ⚠️ PARTIALLY EXISTS — Pieces are scattered across Victus infrastructure**

| Master Plan Requirement | Existing Piece | Where | Gap |
|------------------------|---------------|-------|-----|
| Intent classifier | `mission_controller.py` | Victus (315 lines) | Classifies to Victus engines (pipeline/DAG/mesh/crucible), not ION topology |
| Ion router — find relevant ions, check gates | `ion/router.py` + `ion/navigator.py` | ION (88 + 404 lines) | Router is thin. Navigator has the loop but doesn't call LLMs |
| Response assembler | — | Doesn't exist | Need: compile ion traversal results into chat response |
| Session manager (capsules) | `overseer.py` | Victus (557 lines) | Already uses ION store for conversations ✅ |
| Builder mode — create ions through conversation | — | Doesn't exist | Need: Aether detects gaps, creates new ions via governed write |

**The core gap (Master Plan §3.1-3.3):** Aether needs to:
1. LISTEN — parse human intent → HAVE: `mission_controller.py`
2. ROUTE — find relevant ions → PARTIAL: `ion/router.py` thin, needs to query index
3. GOVERN — enforce constitutional law → HAVE: `ion/governed_write.py`, `ion/invariants.py`
4. SPEAK — assemble ion outputs → MISSING: response assembler

**The integration gap:** The navigator (`ion/navigator.py`) runs the 7-step cognitive loop but does it **mechanically** — it traverses the graph data structure but never calls an LLM to reason about what it finds. The K-Gate (`k_gate.py`) routes LLM calls but doesn't know about the ion graph. These two systems need to meet.

---

### Master Plan Phase 3: Spec Compiler (§IV — "The NL-Spec Compilation Model")

**STATUS: ❌ BARELY STARTED — Master Plan §4.4 describes an 8-stage pipeline; only stage 1 is sketched**

| Master Plan Stage (§4.4) | Existing | Status |
|--------------------------|----------|--------|
| 1. PARSE — extract frontmatter, NL sections | `ion/spec_parser.py` (114 lines) | ⚠️ Basic, needs to match §4.2 anatomy |
| 2. VALIDATE — all depends_on exist? No cycles? | `ion/spec_deps.py` (85 lines) | ⚠️ Exists but untested |
| 3. SCAFFOLD — generate types, imports, signatures | — | ❌ Missing |
| 4. FILL — NL behavior → code (LLM or template) | `ion/compiler.py` (70 lines) | ❌ Regex toy, needs full rewrite with LLM |
| 5. ENFORCE — inject invariant checks, assertions | — | ❌ Missing |
| 6. TEST_GEN — generate tests from test_requirements | — | ❌ Missing |
| 7. INTEGRATION — verify against affects specs | — | ❌ Missing |
| 8. EVIDENCE — create evidence ion with results | — | ❌ Missing |

**Key principle from Master Plan §4.3:**
> "The AI never edits the compiled output directly. If it needs to change behavior, it edits the spec. The pipeline recompiles."

This is the transformative part. The compiler replaces traditional code editing with spec editing.

---

### Master Plan Phase 4: Multi-Agent (§VIII)

**STATUS: ❌ STUBS ONLY — Not actionable until Phases 1-2 work end-to-end**

| Requirement | Stub | Lines | Notes |
|-------------|------|-------|-------|
| Agent manifests | `ion/agent_manifest.py` | 79 | Position tracking per agent |
| Ion locking | `ion/locking.py` | 80 | Prevent concurrent writes |
| Conflict resolution | `ion/conflict.py` | 60 | Detect affects overlap |
| Comms | `ion/agent_comms.py` | 57 | Directory-based messaging |

---

### Master Plan Phase 5: Self-Evolution (§VIII)

**STATUS: ❌ CODE EXISTS BUT PREMATURE — No running system to evolve**

| Requirement | File | Lines | Notes |
|-------------|------|-------|-------|
| Threshold learning | `ion/threshold_learner.py` | 242 | Learns from activation patterns |
| Topology optimization | `ion/topology_optimizer.py` | 182 | Detects orphans, bottlenecks |
| Consolidation | `ion/consolidator.py` | 171 | Merge compatible evidence |
| Corrections | `ion/corrections.py` | 146 | Track correction vectors |
| Meta-monitoring | `ion/meta.py` | 218 | Graph health metrics |

---

## Existing Victus Infrastructure → ION Mapping

The Master Plan §IX (Appendix B) defines how current AIM-OS maps to ION. Here's the implementation status of each mapping:

| Current Component | ION Mapping (per Master Plan) | Status |
|------------------|------------------------------|--------|
| `protocol_manifest.py` | Ion engine core (Phase 1) | ✅ ION engine exists and replaces this |
| `overseer.py` | Aether + manifest manager | ⚠️ Overseer already uses ION store; needs Aether routing |
| Genome files | Root ion specs for each agent | ❌ Not migrated |
| MCP memory tools | `memory/` directory | ❌ Not migrated |
| Capsule protocol | `capsules/` directory | ⚠️ Overseer writes capsules to ION store |
| `dag_engine.py` | Multi-branch traversal (C1) | ❌ DAG engine doesn't talk to ION graph |
| `mesh_orchestrator.py` | Multi-agent simultaneous traversal | ❌ Not integrated |
| `mission_controller.py` | Aether's intent classifier | ⚠️ Exists, not routing to ION |
| `memory_bus.py` | `evidence/` + `memory/` directories | ❌ Not migrated |
| `comms_bus.py` | `comms/` directory | ❌ Comms bus uses flat files, not ION bonds |
| Test suites | Evidence ions from spec test_requirements | ❌ Spec compiler not built |

---

## Build Order: Session-by-Session

### ═══════════════════════════════════════════
### BLOCK 1: VERIFY PHASE 1 (1-2 sessions)
### ═══════════════════════════════════════════

> Master Plan Phase 1 code exists. Verify it works end-to-end before building on top of it.

#### Session 1.1 — Bootstrap and Verify

**Goal:** Create a real ion network on disk and verify the entire Phase 1 stack works.

1. Run `ion/bootstrap.py` → creates directory structure per Master Plan §2.3
2. Verify the bootstrapped network matches the Master Plan filesystem layout:
   - `manifest.md` at root
   - `protocol/` with governance ions
   - `evidence/`, `branches/`, `memory/`, `specs/`, `automations/`, `timeline/`, `comms/`, `capsules/`
3. Verify `ion/store.py` reads/writes every bootstrapped ion correctly
4. Verify `ion/index.py` builds from bootstrapped network
5. Verify `ion/graph.py` builds traversable graph from bonds
6. Verify `ion/navigator.py` runs a full 7-step loop on the bootstrapped network (mechanically, no LLM yet)
7. Run `ion/cli.py` commands: `ion ls`, `ion inspect manifest`, `ion bonds manifest`, `ion graph`, `ion stats`
8. Fix any failures

**Exit criteria:** CLI works, navigator completes a full loop, all 547 existing tests still pass.

#### Session 1.2 — Wire API and Populate

**Goal:** Wire ION API into the Victus server and populate the network with real content.

1. Add `ion/api.py` router to `server.py` at `/ion/` prefix
2. Test all API endpoints against bootstrapped network
3. Populate the ion network with real content:
   - Protocol ions from `AETHER_CONSTITUTION.md`, `AETHER_KERNEL.md`
   - Evidence ions from actual test results
   - Branch ions for current active work
   - Memory ions from key decisions (e.g., "filesystem over MCP")
4. Verify governed write pipeline on real content (not just test fixtures)

**Exit criteria:** `/ion/ls`, `/ion/inspect/{id}`, `/ion/create` all work via HTTP. Real content in the ion network.

---

### ═══════════════════════════════════════════
### BLOCK 2: BUILD AETHER (3-5 sessions)
### ═══════════════════════════════════════════

> Master Plan Phase 2. This is the main build. Aether is the interface that makes ION a usable OS.
> Ref: Master Plan §3.1-3.4

#### Session 2.1 — Ion Context Compiler

**Goal:** Build the component that takes ion IDs → compiles their content into an LLM prompt.

Master Plan ref: §3.3 step 4 ("Activates ions — wake relevant specialist ions, load their context")

**What to build:** Rewrite `ion/context_compiler.py` (currently a 42-line Gemini hallucination)

- Input: list of ion IDs + token budget
- Read each ion via store → get frontmatter + body + bonds
- Priority ordering: by authority class (A0 first), then by confidence
- Token budget management: high-priority ions get full text, low-priority get summaries
- Output: formatted context string for LLM injection
- Uses existing `IonStore` and `IonIndex` from `bridge.py`

**Lines: ~200 | Depends on: Session 1.1**

#### Session 2.2 — Navigator + K-Gate Integration

**Goal:** Make the navigator's cognitive loop call real LLMs via K-Gate.

Master Plan ref: §5.1 ("The Cognitive Loop as Graph Traversal")

**What to change in `ion/navigator.py`:**

Each step of the 7-step loop needs to use the context compiler + K-Gate:

1. **CONTEXTUALIZE** — read manifest → compile active branch context → send to K-Gate: "Given this state, what's the goal?"
2. **REFLECT** — compile high/low confidence evidence → send to K-Gate: "What do I know vs don't know?"
3. **PLAN** — compile available branches → send to K-Gate: "Which branch should I traverse? What's the execution order?"
4. **GATE** — pure threshold evaluation (NO LLM — this is mechanical)
5. **EXECUTE** — send the execution plan + relevant ion context → K-Gate for actual work
6. **AUDIT** — send output back → K-Gate for metabolic assessment (§15)
7. **DELIVER** — format output, update manifest, write evidence

**Lines: ~200 modifications to existing 404 lines | Depends on: 2.1**

#### Session 2.3 — Intent Classifier → ION Topology

**Goal:** Make Aether classify human intent and map it to ions in the graph.

Master Plan ref: §3.3 steps 1-3 ("Classifies intent, Maps to ion topology, Checks gates")

**What to build/modify:**

- Extend `mission_controller.py` (or create new `ion/intent.py`):
  - Classify human message → ion type needed (question → evidence, task → branch, creation → spec)
  - Query ion index → find relevant ions by tags, type, bonds
  - Check gates → are required ions valid? Evidence sufficient?
  - If gap detected → flag for builder mode (Session 2.4)
- Return: list of ion IDs to activate, gate status, gap analysis

**Lines: ~250 | Depends on: Session 1.1**

#### Session 2.4 — Response Assembler + Builder Mode

**Goal:** Aether assembles ion traversal results into coherent response. Aether creates new ions when gaps detected.

Master Plan ref: §3.3 step 6 ("Assembles output") + §3.4 ("Aether as Builder")

**Response assembler:**
- Takes: navigator traversal results (a list of ion outputs from each cognitive step)
- Assembles into: coherent natural language response
- Includes: confidence levels, evidence citations, caveats per `seedos_compact_core.md`
- Runs: metabolic assessment (§15) — did this change goals? Worth recording?

**Builder mode (§3.4):**
- When intent classifier finds no relevant ions → trigger builder
- Classify need → what type of ion?
- Authority check → can this agent create this ion type?
- Governed write → run 10-stage validation
- Bond → connect new ion to graph
- This is how the OS grows organically

**Lines: ~300 | Depends on: Sessions 2.2, 2.3**

#### Session 2.5 — Overseer ION Dispatch Mode

**Goal:** Wire Aether into the overseer as a new dispatch mode alongside pipeline/DAG/mesh/crucible.

**What to change in `overseer.py`:**
- New dispatch path: when mission controller classifies request as ION-suitable → dispatch to navigator
- Navigator uses K-Gate for LLM calls (same as pipeline, but traverses ion graph instead of running 9-phase pipeline)
- Results go through response assembler → back to user via SSE

This means the overseer now has 5 dispatch modes:
1. `direct` — simple K-Gate call (existing)
2. `pipeline` — 9-phase cognition pipeline (existing)
3. `dag` — DAG execution engine (existing)
4. `mesh` — multi-agent mesh (existing)
5. `ion` — ION graph traversal via navigator + Aether (NEW)

**Lines: ~150 additions | Depends on: Sessions 2.1-2.4**

---

### ═══════════════════════════════════════════
### BLOCK 3: BUILD SPEC COMPILER (3-4 sessions)
### ═══════════════════════════════════════════

> Master Plan Phase 3, §IV. The NL-Spec compilation model.
> This is the transformative piece: AI writes specs, not code.

#### Session 3.1 — Spec Parser + Validator

**Goal:** Full spec parser matching Master Plan §4.2 anatomy.

**Rewrite `ion/spec_parser.py` to handle:**
- Spec frontmatter: `spec_id`, `compiles_to`, `language`, `spec_version`, `depends_on`, `affects`, `invariants`, `test_requirements`
- Body sections: Purpose, Dependencies, Interface (with function signatures), Constraints
- Validation: all `depends_on` specs exist, no cycles, `compiles_to` path valid

**Verify `ion/spec_deps.py`:**
- Dependency resolution across spec graph
- Cycle detection
- Topological sort for compilation order

**Lines: ~300 | Depends on: Block 1**

#### Session 3.2 — Scaffold + Fill (LLM-Assisted Code Generation)

**Goal:** Implement Master Plan §4.4 stages 3-4.

**Rewrite `ion/compiler.py`:**
- **Stage 3 — SCAFFOLD:** From spec frontmatter + interface section → generate: imports (from `depends_on`), class/function signatures, type stubs
- **Stage 4 — FILL:** Send scaffold + NL behavior descriptions → K-Gate LLM → generate implementation code
- Each function's NL description (e.g., "Retrieve user by email from Database") → code

The LLM sees:
- The scaffold (types + signatures)
- The NL behavior for this function
- The `depends_on` specs (so it knows what APIs are available)
- The `invariants` (so it knows what constraints to enforce)

**Lines: ~400 | Depends on: 3.1, Block 2 (needs K-Gate integration)**

#### Session 3.3 — Enforce + Test Gen

**Goal:** Implement Master Plan §4.4 stages 5-6.

**Stage 5 — ENFORCE:**
- Parse `invariants` from spec frontmatter
- Inject assertion checks into compiled code
- E.g., invariant "Passwords must be hashed with bcrypt (min 12 rounds)" → assertion in the compiled `login()` function

**Stage 6 — TEST_GEN:**
- Parse `test_requirements` from spec frontmatter
- Generate pytest test file with test cases for each requirement
- E.g., "Must test: valid login, invalid password, expired token" → three test functions

**Lines: ~300 | Depends on: 3.2**

#### Session 3.4 — Integration + Evidence

**Goal:** Implement Master Plan §4.4 stages 7-8.

**Stage 7 — INTEGRATION:**
- For each spec in `affects` list: verify compiled output is compatible
- Check: do function signatures match what `affects` specs expect?
- Check: do types align?

**Stage 8 — EVIDENCE:**
- Create evidence ion recording: what was compiled, when, test results, integration status
- Bond evidence to spec and compiled output
- Update manifest with compilation results

**Lines: ~200 | Depends on: 3.3**

---

### ═══════════════════════════════════════════
### BLOCK 4: MULTI-AGENT (future, blocked on Blocks 1-3)
### ═══════════════════════════════════════════

> Master Plan Phase 4. Multiple agents traversing the ion graph simultaneously.
> Not detailed here because it depends on a single-agent system working first.
> The stubs exist: `agent_manifest.py`, `locking.py`, `conflict.py`, `agent_comms.py`.

---

### ═══════════════════════════════════════════
### BLOCK 5: SELF-EVOLUTION (future, blocked on Blocks 1-3)
### ═══════════════════════════════════════════

> Master Plan Phase 5. The system improves itself.
> Code already exists: `threshold_learner.py`, `topology_optimizer.py`, `consolidator.py`, `corrections.py`, `meta.py`.
> Wire these in when there's a real system producing usage data.

---

## What About the Gemini-Hallucinated Files?

These files contain word-salad docstrings from a different model. Action per file:

| File | Lines | Action | Reason |
|------|-------|--------|--------|
| `ion/llm_adapter.py` | 49 | **DELETE** | Victus has `ollama_runner.py` (408) + `k_gate.py` (864). This is a useless abstract stub with nonsense docs. |
| `ion/context_compiler.py` | 42 | **REWRITE** in Session 2.1 | Needs to be a real context compiler per Master Plan §3.3 |
| `ion/tools.py` | 45 | **REVIEW** | May contain valid tool definitions |
| `aether/engine.py` | 56 | **DELETE** | "Physical cognitive execution mapped recursively across 7 formal OS steps natively" — word salad. The navigator IS the engine. |
| `ion/pubsub.py` | 33 | **DELETE** | `ion/events.py` (96 lines) already does this properly |

---

## What About Governance, Automation, Self-Healing?

The following tracks were coded during this conversation and are functional but not yet exercised:

| Track | Files | Total Lines | Status |
|-------|-------|-------------|--------|
| **G: Automation** | `events.py`, `propagation.py`, `watcher.py`, `automation.py`, `healer.py` | 614 | Ready to wire after Block 2 |
| **H: Governance** | `authority.py`, `invariants.py`, `audit.py`, `compliance.py`, `governance_api.py` | 605 | Ready to wire after Block 2 |
| **I: Self-Evolution** | `threshold_learner.py`, `topology_optimizer.py`, `consolidator.py`, `corrections.py`, `meta.py` | 959 | Ready to wire after Block 3 |

These don't need sessions of their own. They're already written. They just need a running system to plug into. Wire them incrementally as Blocks 2-3 progress.

---

## Relay/Orchestration Alignment

The [Relay Orchestration Journal](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/RELAY_ORCHESTRATION_JOURNAL.md) defines the operator experience. ION is the substrate that the relay sits on.

| Relay Need (§Journal) | ION Equivalent |
|----------------------|----------------|
| Re-entry boot | Read `manifest.md` → follow branches → recover state |
| Status visibility | Query `ion/index.py` → active agents, active branches, evidence freshness |
| Delegation/routing | Aether intent → ion router → activate relevant ions |
| Approval/intervention | Gate class checks (gate_class > 2 → human approval) |
| Continuity writeback | POST capsule ion → manifest update → timeline entry |

The relay doesn't need its own implementation. It needs ION's Phase 1-2 to work, then it gets relay for free by querying the ion graph through the API.

---

## Session Estimates

| Block | Sessions | What |
|-------|----------|------|
| **1** | 1-2 | Verify Phase 1: bootstrap, CLI, API wiring |
| **2** | 3-5 | Build Aether: context compiler, navigator+LLM, intent classifier, response assembler, overseer dispatch |
| **3** | 3-4 | Build Spec Compiler: parser, scaffold+fill, enforce+test, integration+evidence |
| **4** | 2-3 | Multi-Agent (blocked on 1-3) |
| **5** | 1-2 | Wire Self-Evolution (code exists, just connect it) |
| **Total** | **10-16** | |

---

## How This Plan Should Be Used

1. **This traces to the Master Plan.** Every item cites a section number.
2. **Update this document every session.** Mark what's done, correct estimates, add learnings.
3. **Don't skip ahead.** Block 2 requires Block 1 verification. Block 3 requires Block 2.
4. **Open questions go to Braden.** Don't assume answers.
5. **If something doesn't match the Master Plan, update THIS document, not the Master Plan.** The Master Plan is the vision. This is the execution.
6. **Per `seedos_compact_core.md` line 66:** If scope expands beyond the original ask, NAME the expansion and ask.

---

*This is iteration 1 of the execution plan. It will be refined as work progresses.*

*— Opus, 2026-03-21*
