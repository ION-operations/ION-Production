# ION Build Orchestration Plan
## From Current State → Complete ION Operating System

**Author:** Opus (COO)  
**Date:** 2026-03-21  
**Purpose:** Every phase required to build ION, with honest LOD assessment  
**Living document — updated as phases complete**

---

## Honest Capability Assessment

Before planning, I must be honest about what I can reliably do per session:

### ✅ High Confidence (can build and verify in 1 session)
- Python modules ≤500 lines with full test suites
- File parsers (YAML frontmatter, markdown)
- Graph data structures and traversal algorithms
- SQLite-backed stores
- FastAPI endpoints
- Test suites with 20-100 tests
- Documentation and specification files

### ⚠️ Medium Confidence (2-3 sessions, some iteration)
- Complex async orchestration (file watchers, event loops)
- Multi-module integration (wiring 3+ systems together)
- UI components (React/TypeScript)
- Template-based code generation

### ❌ Low Confidence (needs external help or special tooling)
- LLM-based code generation requiring API calls
- Real-time browser-based visualizations
- Long-running daemon processes
- Cross-network communication protocols

### 📏 Per-Session Output Limits
- ~400-800 lines of production code per session
- ~20-100 tests per session
- Context holds ~15 files in active working memory
- Can modify 3-5 files per session reliably

---

## Dependency Map

```
TRACK A: ION CORE ENGINE (the filesystem-native runtime)
  A.01 → A.02 → A.03 → A.04 → A.05 → A.06 → A.07 → A.08 → A.09 → A.10
  
TRACK B: ION GRAPH (topology, traversal, thresholds)
  B.01 → B.02 → B.03 → B.04 → B.05 → B.06 → B.07 → B.08
  Depends on: A.01-A.03

TRACK C: AETHER INTERFACE (chat, routing, governance)
  C.01 → C.02 → C.03 → C.04 → C.05 → C.06 → C.07
  Depends on: A.01-A.05, B.01-B.04

TRACK D: SPEC COMPILER (NL-spec → code compilation)
  D.01 → D.02 → D.03 → D.04 → D.05 → D.06 → D.07
  Depends on: A.01-A.06

TRACK E: CONTINUITY (truncation survival, capsules, timeline)
  E.01 → E.02 → E.03 → E.04 → E.05
  Depends on: A.01-A.04

TRACK F: MULTI-AGENT (simultaneous traversal, locking, comms)
  F.01 → F.02 → F.03 → F.04 → F.05
  Depends on: A.*, B.*, E.*

TRACK G: AUTOMATION & REACTIVITY (file watchers, event propagation)
  G.01 → G.02 → G.03 → G.04 → G.05
  Depends on: A.*, B.01-B.04

TRACK H: GOVERNANCE (authority enforcement, governed write, auditing)
  H.01 → H.02 → H.03 → H.04 → H.05
  Depends on: A.01-A.06

TRACK I: SELF-EVOLUTION (threshold learning, topology optimization)
  I.01 → I.02 → I.03 → I.04 → I.05
  Depends on: ALL TRACKS
```

---

## TRACK A: ION CORE ENGINE
> The foundation. Everything else depends on this.

### A.01 — Ion Data Model
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~40**

Build the core `Ion` dataclass and supporting types:
- `Ion` dataclass: id, type, authority, confidence, created, last_verified, owner
- `IonType` enum: manifest, protocol, evidence, branch, memory, spec, capsule, automation
- `AuthorityClass` enum: A0-A7 with descriptions and write permissions
- `IonBond` dataclass: source_id, target_id, bond_type, metadata
- `BondType` enum: requires, produces, affects, depends_on, escalate_to, supersedes
- `IonThreshold` dataclass: field, operator, value, action
- `IonActivation` dataclass: conditions list, all_required flag
- Serialization: to_dict/from_dict/to_json/from_json for all types
- **Tests:** Construction, serialization round-trip, enum coverage, type validation

**Depends on:** Nothing — pure data model  
**Produces:** Foundation for all other tracks  
**Files:** `victus/ion/model.py`, `victus/ion/__init__.py`

---

### A.02 — Frontmatter Parser
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~35**

Parse YAML frontmatter from markdown ion files:
- Read `.md` file → extract `---` delimited frontmatter + body
- Parse frontmatter YAML into `Ion` dataclass fields
- Extract bonds from `requires`, `produces`, `affects`, `depends_on` fields
- Extract thresholds from `escalate_if`, `invalidate_if`, `archive_if` fields
- Extract automation hooks from `on_change`, `on_invalidate` fields
- Write: serialize `Ion` + body back to markdown file
- Handle edge cases: missing frontmatter, empty body, invalid YAML, nested fields
- **Tests:** Parse sample ions, round-trip, edge cases, malformed input

**Depends on:** A.01  
**Produces:** Ability to read/write ion files  
**Files:** `victus/ion/parser.py`

---

### A.03 — Ion Store (Filesystem CRUD)
**LOD: ✅ High | Sessions: 1 | Lines: ~350 | Tests: ~45**

CRUD operations for ions on the filesystem:
- `IonStore` class with configurable root directory
- `create_ion(ion, body)` → writes to correct directory based on ion_type
- `read_ion(ion_id)` → finds file by path, parses, returns Ion + body
- `update_ion(ion_id, changes)` → reads, applies changes, writes
- `delete_ion(ion_id)` → removes file (with authority check)
- `list_ions(type=None, directory=None)` → scan directory tree
- `find_by_id(ion_id)` → path resolution from semantic ID
- `exists(ion_id)` → check if ion file exists
- Directory auto-creation for nested paths
- Path validation (no traversal attacks, valid characters)
- **Tests:** CRUD operations, directory structure, path resolution, listing, edge cases

**Depends on:** A.01, A.02  
**Produces:** Persistent ion storage on filesystem  
**Files:** `victus/ion/store.py`

---

### A.04 — Governed Write Pipeline
**LOD: ✅ High | Sessions: 1 | Lines: ~400 | Tests: ~50**

The 10-stage validation pipeline for creating/modifying any ion:
- `GovernedWritePipeline` class
- W1 Intake: receive ion + body, validate non-empty
- W2 Parse: validate frontmatter structure matches IonType requirements
- W3 Classify: verify ion_type is valid, assign required fields
- W4 Evidence: validate confidence (0-1), evidence_class present
- W5 Authority: check authority class valid for author (permission matrix)
- W6 Zone: verify directory matches ion_type (evidence→evidence/, etc.)
- W7 Contradict: check existing ions for conflicts (same ion_id, contradicting claims)
- W8 Verify: run all type-specific invariants (protocol ions need A0-A1, etc.)
- W9 Provenance: stamp created, author, version, lineage
- W10 Propagate: collect `on_change` hooks from affected ions
- `WriteReceipt` dataclass: passed, stages_completed, failures, propagation_queue
- Each stage returns pass/fail with reason
- Pipeline stops on first failure (or configurable: collect all)
- **Tests:** Happy path, each stage failure, authority violations, contradiction detection

**Depends on:** A.01, A.02, A.03  
**Produces:** Guaranteed correctness for all writes  
**Files:** `victus/ion/governed_write.py`

---

### A.05 — Manifest Ion Manager
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~40**

Special handling for the root manifest ion:
- `ManifestManager` class
- `load()` → read manifest.md, parse into structured state
- `save()` → write current state back to manifest.md
- `update_position(loop_step)` → advance cognitive loop position
- `add_evidence(ion_id, status)` → record evidence in manifest
- `activate_branch(branch_id)` → move branch from future to active
- `complete_branch(branch_id)` → move from active to completed
- `set_handoff(summary)` → update handoff text
- `get_active_branches()` → list all active branch ions
- `get_recent_evidence(n)` → most recent n evidence ions
- Auto-update timestamp on every modification
- Evolution from existing `ProtocolManifest` — adapter layer
- **Tests:** Load/save, position tracking, branch lifecycle, evidence tracking

**Depends on:** A.01, A.02, A.03, A.04  
**Produces:** Structured manifest management  
**Files:** `victus/ion/manifest.py`

---

### A.06 — Ion Index
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

In-memory index for fast graph queries without scanning filesystem:
- `IonIndex` class — builds index from directory scan
- `build_index(root_dir)` → walk tree, parse all frontmatter, build maps
- `ions_by_type(type)` → all ions of a given type
- `ions_by_authority(authority)` → all ions at authority level
- `bonds_from(ion_id)` → all outgoing bonds
- `bonds_to(ion_id)` → all incoming bonds (reverse index)
- `stale_ions(max_age)` → ions not verified within threshold
- `low_confidence_ions(threshold)` → ions below confidence threshold
- `refresh()` → rebuild index from current filesystem state
- Incremental update: `ion_changed(ion_id)` → update just that ion's index
- **Tests:** Index building, queries, incremental updates, stale detection

**Depends on:** A.01, A.02, A.03  
**Produces:** Fast ion lookup, graph query capability  
**Files:** `victus/ion/index.py`

---

### A.07 — Ion CLI Tool
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Command-line interface for inspecting/managing the ion filesystem:
- `ion ls [directory]` → list ions with type, confidence, age
- `ion inspect <ion_id>` → show frontmatter, bonds, body preview
- `ion create <type> <id>` → create new ion with template frontmatter
- `ion bonds <ion_id>` → show all bonds (incoming + outgoing)
- `ion stale [days]` → list ions not verified within N days
- `ion validate <ion_id>` → run governed write validation
- `ion graph` → print ASCII graph of ion topology
- `ion stats` → summary: ion count by type, bond count, avg confidence
- Built on `argparse`, calls IonStore + IonIndex
- **Tests:** CLI argument parsing, output format, command coverage

**Depends on:** A.01-A.06  
**Produces:** Human-usable ion management  
**Files:** `victus/ion/cli.py`

---

### A.08 — Ion API Endpoints
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~30**

FastAPI endpoints for programmatic access:
- `GET /ion/list` → list all ions (filterable by type, authority)
- `GET /ion/{ion_id}` → get ion details + body
- `POST /ion/create` → create new ion via governed write
- `PUT /ion/{ion_id}` → update ion via governed write
- `DELETE /ion/{ion_id}` → delete ion (authority check)
- `GET /ion/{ion_id}/bonds` → get bonds for an ion
- `GET /ion/graph` → full graph as JSON (nodes + edges)
- `GET /ion/stats` → system statistics
- `GET /ion/stale` → stale ions needing verification
- All endpoints return structured JSON
- Wire into existing `victus/server.py`
- **Tests:** HTTP tests for all endpoints, error cases, auth

**Depends on:** A.01-A.06  
**Produces:** HTTP API for ion operations  
**Files:** `victus/ion/api.py`, updates to `victus/server.py`

---

### A.09 — Bridge: Existing Systems → ION
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~35**

Migrate existing Victus systems to use ion storage:
- Adapter: `MemoryBus.store()` → creates ion in `memory/` via governed write
- Adapter: `MemoryBus.recall()` → queries ion index
- Adapter: `ConversationStore` → capsule ions in `capsules/`
- Adapter: `CommsBus` → ion files in `comms/`
- Adapter: `AgentProcess.wake()` → reads agent's manifest ion
- Adapter: `AgentProcess.sleep()` → writes POST capsule ion
- Backward compatible: old APIs still work, new storage is ion filesystem
- Migration script: move existing SQLite data → ion files
- **Tests:** Adapter correctness, backward compatibility, migration

**Depends on:** A.01-A.06, existing Victus modules  
**Produces:** Unified storage on ion filesystem  
**Files:** `victus/ion/bridge.py`, updates to `victus/memory_bus.py`, `victus/overseer.py`

---

### A.10 — Bootstrap: First Ion Network
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Create the initial ion filesystem for AIM-OS:
- Bootstrap script that creates the directory structure
- Initial manifest.md with starting topology
- Protocol ions from Aether-OS canon (constitution, kernel, cognitive loop)
- First evidence ions from existing test results (228/228)
- First timeline entry
- First capsule
- Validate that bootstrapped network passes all invariants
- **Tests:** Bootstrap, validate, traverse, invariant checks

**Depends on:** A.01-A.09  
**Produces:** A working ion filesystem ready for use  
**Files:** `victus/ion/bootstrap.py`

---

## TRACK B: ION GRAPH
> Topology, traversal, and threshold evaluation.

### B.01 — Graph Builder
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~40**

Build an in-memory directed graph from ion bonds:
- `IonGraph` class wrapping adjacency lists
- `build_from_index(index)` → scan all bonds, build graph
- `neighbors(ion_id, bond_type)` → filtered outgoing edges
- `predecessors(ion_id, bond_type)` → filtered incoming edges  
- `subgraph(root_id, depth)` → extract subtree to depth N
- `topological_sort()` → dependency order
- `cycle_detection()` → find and report cycles
- `connected_components()` → find isolated subgraphs
- `shortest_path(from_id, to_id)` → shortest bond path
- `impact_analysis(ion_id)` → what changes if this ion changes (transitive `affects`)
- **Tests:** Graph construction, traversal, cycles, sorting, impact analysis

**Depends on:** A.01, A.06  
**Files:** `victus/ion/graph.py`

---

### B.02 — Threshold Evaluator
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~35**

Evaluate ion thresholds to determine activation/escalation/invalidation:
- `ThresholdEvaluator` class
- `can_activate(ion)` → check all `activates_when` conditions
- `should_escalate(ion)` → check `escalate_if` conditions
- `is_invalid(ion)` → check `invalidate_if` conditions
- `should_archive(ion)` → check `archive_if` conditions
- `should_specialize(ion)` → check `specialize_after` conditions
- Condition types: `ion_exists`, `confidence_above`, `confidence_below`, `age_above`, `user_intent_matches`, `all_requires_above`
- Returns `ThresholdResult`: passed, failed_conditions, recommendation
- **Tests:** Each condition type, compound conditions, edge cases

**Depends on:** A.01, A.06  
**Files:** `victus/ion/threshold.py`

---

### B.03 — Cognitive Loop Navigator
**LOD: ✅ High | Sessions: 1 | Lines: ~350 | Tests: ~40**

The §7 cognitive loop as a graph traversal algorithm:
- `CognitiveNavigator` class
- `contextualize(manifest)` → read manifest, load evidence, identify active branches
- `reflect(context)` → separate high-confidence from low-confidence ions
- `plan(context)` → select branches, check dependencies, order traversal
- `gate(branch)` → evaluate all `requires`, check threshold, classify gate_class
- `execute(branch)` → return execution plan (what to write, where)
- `audit(execution_result)` → run metabolic assessment, check invariants
- `deliver(audit_result)` → update manifest, write to timeline, return output
- `full_loop(manifest, user_intent)` → run all 7 steps, return structured result
- Each step produces a `StepResult` with status, evidence, and next_step
- **Tests:** Each step individually, full loop, gate failures, escalation scenarios

**Depends on:** A.01-A.05, B.01, B.02  
**Files:** `victus/ion/navigator.py`

---

### B.04 — Escalation Engine
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Formal C2→C3 escalation when thresholds fire:
- `EscalationEngine` class
- 7 trigger conditions from Aether Atlas Book IX
- `check_escalation(context)` → evaluate all triggers, return fired list
- `escalate(context, triggers)` → create analysis ions, enter deep reasoning mode
- `resolve(analysis_ions)` → determine if escalation resolved, de-escalate to C2
- `create_contradiction_ion(ion_a, ion_b)` → formal contradiction record
- `create_analysis_ion(topic, evidence)` → deep reasoning workspace
- Escalation audit trail: who escalated, why, how resolved
- **Tests:** Each trigger, escalation flow, resolution, de-escalation

**Depends on:** A.01, A.04, B.01, B.02  
**Files:** `victus/ion/escalation.py`

---

### B.05 — Branch Router
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Route user intent to the correct branch(es):
- `BranchRouter` class
- `find_branches(intent, manifest)` → match intent to active branches
- Matching strategies: keyword, ion metadata, confidence ranking
- `rank_branches(matches)` → prioritize by relevance, confidence, gate_class
- `check_gates(branches)` → verify all preconditions, return gated list
- `plan_traversal(gated_branches)` → sequential or parallel execution plan
- `detect_conflicts(branches)` → check for `affects` overlap between branches
- **Tests:** Intent matching, ranking, gate checking, conflict detection

**Depends on:** A.01, A.05, A.06, B.01, B.02  
**Files:** `victus/ion/router.py`

---

### B.06 — Impact Analyzer
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Determine the blast radius of changing an ion:
- `ImpactAnalyzer` class
- `analyze(ion_id)` → transitive closure of `affects` bonds
- `direct_impact(ion_id)` → immediate neighbors only
- `confidence_cascade(ion_id, new_confidence)` → what happens to dependent ions' confidence
- `invalidation_cascade(ion_id)` → what would be suspended/invalidated
- `report(ion_id)` → human-readable impact report
- **Tests:** Direct/transitive impact, cascades, report formatting

**Depends on:** A.01, A.06, B.01  
**Files:** `victus/ion/impact.py`

---

### B.07 — Path Planner
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Plan multi-step work paths through the ion graph:
- `PathPlanner` class
- `shortest_path(from_ion, to_ion)` → find shortest path through bonds
- `required_path(branch)` → all ions that must be completed to reach this branch
- `parallel_opportunities(branches)` → which branches can run concurrently
- `rollback_path(branch)` → what to undo if branch fails
- `cost_estimate(path)` → estimated sessions/effort based on gate classes
- **Tests:** Path finding, parallelism detection, rollback, cost estimation

**Depends on:** B.01, B.02  
**Files:** `victus/ion/planner.py`

---

### B.08 — Ion Graph Visualization
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~15**

Render the ion graph in multiple formats:
- ASCII: terminal-friendly text rendering
- Mermaid: generate mermaid diagram syntax
- JSON: D3-compatible node-link format
- Stats: graph metrics (density, diameter, clustering)
- Filtering: by type, authority, confidence, age
- Highlighting: color by threshold status (healthy/stale/escalated)
- **Tests:** Rendering accuracy, filtering, format validity

**Depends on:** A.06, B.01  
**Files:** `victus/ion/visualize.py`

---

## TRACK C: AETHER INTERFACE
> The voice of the system. Chat, routing, governance enforcement.

### C.01 — Intent Classifier
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Classify human messages into actionable intent:
- `IntentClassifier` class (evolves existing MissionController)
- Intent types: question, task, research, creation, review, governance, meta
- Keyword + pattern matching (no external LLM dependency)
- Confidence scoring per intent
- Multi-intent detection ("build X and then test it" = creation + verification)
- Context-aware: consider current manifest state when classifying
- **Tests:** Each intent type, multi-intent, ambiguous input, edge cases

**Depends on:** A.05 (manifest)  
**Files:** `victus/aether/classifier.py`, `victus/aether/__init__.py`

---

### C.02 — Aether Router
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~35**

Route classified intent to ion topology:
- `AetherRouter` class
- `route(intent, manifest)` → find relevant ions, plan traversal
- Uses `BranchRouter` + `CognitiveNavigator` + `ThresholdEvaluator`
- Gate enforcement: reject operations above gate_class 2 without escalation
- Human approval flow: gate_class 3-4 requires Braden confirmation
- Returns `RoutingPlan`: branches to traverse, ions to wake, gate results
- **Tests:** Routing for each intent type, gate enforcement, approval flow

**Depends on:** A.05, B.03, B.05  
**Files:** `victus/aether/router.py`

---

### C.03 — Response Assembler
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

Compile ion outputs into coherent human-facing responses:
- `ResponseAssembler` class
- `assemble(ion_outputs)` → merge structured ion results into natural language
- Section ordering: summary → details → evidence → next steps
- Formatting: markdown with headers, lists, code blocks
- Citation: link back to evidence ions
- Confidence indicator: flag uncertain claims
- Metabolic assessment summary embed
- **Tests:** Assembly from multiple ions, formatting, citations, edge cases

**Depends on:** A.01  
**Files:** `victus/aether/assembler.py`

---

### C.04 — Session Lifecycle
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~30**

PRE/POST capsule management + session continuity:
- `SessionManager` class
- `begin_session()` → read manifest, write PRE capsule ion, load evidence
- `end_session(summary)` → run metabolic assessment, write POST capsule, update manifest
- `restore_from_capsule(capsule_id)` → full state restoration from capsule
- Capsule diff: compare PRE and POST to measure progress
- Auto-title: generate session title from first interaction
- Session history: list past sessions from capsule directory
- **Tests:** Begin/end lifecycle, capsule writing, restoration, diffing

**Depends on:** A.01-A.05, E.01  
**Files:** `victus/aether/session.py`

---

### C.05 — Aether Chat Engine
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~40**

The main chat interface — evolves existing Overseer:
- `AetherChat` class (replaces/wraps Overseer)
- `chat(message, session_id)` → full cognitive loop for each turn
- streaming: yield events for each cognitive step
- Integrates: classifier → router → navigator → assembler
- Context management: auto-load relevant ions as context for LLM
- History: conversation managed as capsule chain
- Backward compatible with existing `/overseer/chat` endpoint
- **Tests:** Full chat loop, streaming, context loading, session management

**Depends on:** C.01-C.04, B.03  
**Files:** `victus/aether/chat.py`

---

### C.06 — Aether Builder Mode
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~350 | Tests: ~30**

Create new ions through conversation:
- `AetherBuilder` class
- Detect when user wants to create something new
- Template selection based on ion type
- Interactive refinement: ask follow-up questions to fill frontmatter
- Governed write: validate before committing
- Bond creation: suggest relationships based on existing topology
- Preview mode: show what will be created before writing
- **Tests:** Each ion type creation, template filling, bond suggestion

**Depends on:** C.01, A.04, A.06  
**Files:** `victus/aether/builder.py`

---

### C.07 — Aether API Refresh
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Update FastAPI endpoints for the Aether interface:
- `POST /aether/chat` → main chat endpoint (replaces /overseer/chat)
- `GET /aether/session/{id}` → session details
- `GET /aether/sessions` → list sessions
- `POST /aether/build` → builder mode endpoint
- `GET /aether/status` → Aether health + ion network stats
- `GET /aether/manifest` → current manifest state
- Backward compatibility: old endpoints redirect to new
- **Tests:** All endpoints, streaming, error handling

**Depends on:** C.01-C.06  
**Files:** `victus/aether/api.py`, updates to `victus/server.py`

---

## TRACK D: SPEC COMPILER
> NL specifications → compiled code artifacts.

### D.01 — Spec Parser
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Parse NL specification ions into structured compilation input:
- `SpecParser` class
- Extract: compiles_to, language, depends_on, affects, invariants, test_requirements
- Extract: interface sections (function signatures from NL)
- Extract: behavior sections (step-by-step logic)
- Extract: constraints and relationships
- Validate: all depends_on specs exist in ion graph
- **Tests:** Parsing, extraction, validation, edge cases

**Depends on:** A.01, A.02  
**Files:** `victus/ion/spec_parser.py`

---

### D.02 — Dependency Validator
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Validate spec dependency graphs:
- `DependencyValidator` class
- Detect cycles in depends_on chains
- Verify all referenced specs exist
- Build compilation order (topological sort)
- Detect breaking changes: if spec A changes, what recompilations needed?
- **Tests:** Cycle detection, ordering, breaking change detection

**Depends on:** A.06, B.01, D.01  
**Files:** `victus/ion/spec_deps.py`

---

### D.03 — Code Scaffold Generator
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~30**

Generate code skeletons from spec frontmatter:
- `ScaffoldGenerator` class
- Python: generate class/function signatures from interface sections
- TypeScript: generate interface/component signatures
- Import generation from depends_on (spec → module mapping)
- Type generation from spec interface definitions
- Stub generation: function bodies as `raise NotImplementedError`
- **Tests:** Python scaffolds, TypeScript scaffolds, import generation

**Depends on:** D.01  
**Files:** `victus/ion/scaffold.py`

---

### D.04 — Behavior Compiler (Template-Based)
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~30**

Fill scaffold with behavior from NL spec sections:
- `BehaviorCompiler` class
- Pattern library: common behaviors → code templates
  - "fetch X from Y" → API call / database query template
  - "validate X" → validation function template
  - "if X then Y else Z" → conditional template
  - "for each X in Y" → loop template
  - "hash/encrypt X" → crypto template
- NL → template matching via keyword extraction
- Fallback: insert NL as comment with TODO marker
- **Tests:** Template matching, code generation, fallback behavior

**Depends on:** D.01, D.03  
**Files:** `victus/ion/behavior_compiler.py`

---

### D.05 — Invariant Enforcer
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

Inject runtime checks from spec invariants:
- `InvariantEnforcer` class
- Parse invariant strings into check templates
- Inject assertions/validators into compiled code
- Generate separate invariant test file
- Types: range checks, format checks, existence checks, relationship checks
- **Tests:** Each invariant type, injection, test generation

**Depends on:** D.01  
**Files:** `victus/ion/invariant.py`

---

### D.06 — Test Generator
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~25**

Auto-generate test files from spec test_requirements:
- `TestGenerator` class
- Parse test_requirements into test case structures
- Generate pytest test files with setup/teardown
- Happy path tests from behavior sections
- Error path tests from constraints/invariants
- Integration tests from affects relationships
- **Tests:** Test generation for various spec types, output validity

**Depends on:** D.01, D.05  
**Files:** `victus/ion/test_gen.py`

---

### D.07 — Compilation Pipeline
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~350 | Tests: ~35**

Full pipeline: spec.md → compiled code + tests:
- `CompilationPipeline` class
- Orchestrates: parse → validate deps → scaffold → behaviors → invariants → tests
- Evidence generation: create evidence ion with compile results
- Diff mode: show what changed vs previous compilation
- Dry-run mode: preview without writing
- Error reporting: detailed failure at each stage
- **Tests:** Full pipeline runs, error cases, diff mode, dry run

**Depends on:** D.01-D.06, A.04  
**Files:** `victus/ion/compiler.py`

---

## TRACK E: CONTINUITY
> Truncation survival, capsules, timeline management.

### E.01 — Capsule Ion Manager
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Structured capsule creation/reading for session boundaries:
- `CapsuleManager` class
- `write_pre(manifest_state)` → snapshot current state as PRE capsule ion
- `write_post(manifest_state, assessment)` → snapshot as POST capsule ion with metabolic results
- `read_capsule(capsule_id)` → parse capsule ion
- `diff(pre_id, post_id)` → progress analysis between PRE and POST
- `chain()` → list all capsules in chronological order
- `latest()` → most recent POST capsule
- Capsule includes: manifest snapshot, evidence summary, branch states, handoff
- **Tests:** Write/read, diff, chain ordering, restore from capsule

**Depends on:** A.01-A.04  
**Files:** `victus/ion/capsule.py`

---

### E.02 — Timeline Manager
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Chronological truth management:
- `TimelineManager` class
- `record(event, evidence_refs, branch_refs)` → add entry to today's timeline
- `get_day(date)` → all events for a day
- `get_range(start, end)` → events across date range
- `latest_activity()` → most recent N events
- Auto-link: timeline entries link to evidence and branch ions
- **Tests:** Recording, retrieval, range queries, linking

**Depends on:** A.01, A.03  
**Files:** `victus/ion/timeline.py`

---

### E.03 — State Restoration Engine
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~35**

Full state restoration from any point:
- `StateRestorer` class
- `restore_from_manifest()` → read manifest, load all linked ions, rebuild context
- `restore_from_capsule(capsule_id)` → restore to specific session state
- `restore_from_date(date)` → restore to end-of-day state using timeline
- Context builder: assemble ion data into prompt-ready context
- Evidence freshness check: flag stale evidence during restoration
- Produces: structured context object ready for LLM prompt injection
- **Tests:** Restoration from each source, context building, freshness detection

**Depends on:** A.01-A.06, E.01, E.02  
**Files:** `victus/ion/restore.py`

---

### E.04 — Drift Detector
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Detect when the AI's behavior drifts from its manifest/protocol:
- `DriftDetector` class
- Compare current manifest vs capsule history: is the mission changing?
- Compare evidence confidence over time: is confidence declining?
- Compare branch completion rate: are branches stalling?
- Detect correction vector patterns: same mistakes repeated?
- Alert: generate drift report if metrics exceed thresholds
- **Tests:** Drift detection in various scenarios, reporting

**Depends on:** E.01, E.02, B.06  
**Files:** `victus/ion/drift.py`

---

### E.05 — Truncation Proof System
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Comprehensive truncation survival infrastructure:
- `TruncationProof` class
- `checkpoint(manifest)` → atomic write of current state to multiple locations
- Redundancy: manifest.md + latest capsule + status file (3 copies)
- Integrity check: verify all three are consistent
- Recovery priority: manifest first, then capsule, then status
- Periodic self-check: every N writes, verify continuity integrity
- **Tests:** Checkpoint, recovery from each failure mode, integrity check

**Depends on:** A.03, A.05, E.01  
**Files:** `victus/ion/truncation.py`

---

## TRACK F: MULTI-AGENT
> Multiple agents traversing the ion graph simultaneously.

### F.01 — Agent Manifest System
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Each agent gets its own manifest ion:
- `AgentManifests` class
- `create_agent_manifest(callsign)` → create manifest ion for agent
- `load_agent_manifest(callsign)` → read agent's current manifest
- `update_position(callsign, position)` → update agent's loop position
- Agent-specific evidence and branch tracking
- Spawn: new agent = new manifest + directory
- **Tests:** Create, load, update, multi-agent isolation

**Depends on:** A.05, E.01  
**Files:** `victus/ion/agent_manifest.py`

---

### F.02 — Ion Locking
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Prevent concurrent writes to contested ions:
- `IonLock` class
- File-based locking (`.lock` files alongside ions)
- `acquire(ion_id, agent)` → take lock, record agent and timestamp
- `release(ion_id, agent)` → release lock
- `is_locked(ion_id)` → check lock status
- Stale lock detection: locks older than N minutes auto-expire
- Lock escalation: contested locks trigger comms notification
- **Tests:** Lock acquire/release, contention, stale detection, escalation

**Depends on:** A.03  
**Files:** `victus/ion/locking.py`

---

### F.03 — Conflict Resolver
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~30**

Detect and resolve conflicts when multiple agents affect the same ions:
- `ConflictResolver` class
- `detect_conflicts(agent_a, agent_b)` → check `affects` overlap
- `resolve_by_priority(agents)` → higher authority wins
- `resolve_by_evidence(agents)` → better evidence wins
- `escalate_to_human(conflict)` → unresolvable → ask Braden
- Conflict ion creation: record the conflict with both sides
- **Tests:** Detection, priority resolution, evidence resolution, escalation

**Depends on:** F.02, B.06, A.04  
**Files:** `victus/ion/conflict.py`

---

### F.04 — Inter-Agent Comms
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

File-based inter-agent messaging:
- `AgentComms` class
- `send(from_agent, to_agent, message)` → write ion to recipient's inbox
- `receive(agent)` → list unread ions in inbox
- `broadcast(from_agent, message)` → write to shared channel
- `read_status(agent)` → get agent's current status ion
- `update_status(agent, status)` → update own status ion
- Message types: handoff, sitrep, flash, wilco (from COMMS_DOCTRINE)
- **Tests:** Send/receive, broadcast, status, message types

**Depends on:** A.03, A.04  
**Files:** `victus/ion/comms.py`

---

### F.05 — Multi-Agent Orchestrator
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~35**

Coordinate multiple agents working on the ion graph:
- `MultiAgentOrchestrator` class
- `dispatch(task, agents)` → divide work among agents
- `monitor(agents)` → track progress via agent manifests
- `synchronize(agents)` → merge results at convergence points
- Parallel traversal: agents walk independent branches concurrently
- Convergence detection: all agents at same loop step = sync point
- Results merging: combine evidence from parallel agents
- **Tests:** Dispatch, parallel execution, synchronization, merging

**Depends on:** F.01-F.04, B.03, C.05  
**Files:** `victus/ion/multi_agent.py`

---

## TRACK G: AUTOMATION & REACTIVITY
> File watchers, event propagation, reactive hooks.

### G.01 — Event System
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Internal event bus for ion lifecycle:
- `IonEventBus` class
- Events: ION_CREATED, ION_UPDATED, ION_DELETED, ION_INVALIDATED, CONFIDENCE_CHANGED
- `subscribe(event_type, handler)` → register handler
- `emit(event_type, ion_id, details)` → fire event
- `on_change` hook processor: parse ion frontmatter hooks, register as handlers
- Event history: log all events to timeline
- **Tests:** Subscribe, emit, hook processing, history

**Depends on:** A.01  
**Files:** `victus/ion/events.py`

---

### G.02 — Propagation Engine
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~30**

Propagate changes through the ion graph:
- `PropagationEngine` class
- When ion changes: walk `affects` bonds, trigger recalculations
- Confidence propagation: parent confidence influences child confidence
- Invalidation cascading: invalid ion → suspend dependent branches
- Cycle breaking: max propagation depth, visited-set tracking
- Atomic propagation: all-or-nothing change sets
- **Tests:** Simple propagation, cascades, cycles, atomicity

**Depends on:** A.06, B.01, G.01  
**Files:** `victus/ion/propagation.py`

---

### G.03 — File Watcher
**LOD: ⚠️ Medium | Sessions: 1 | Lines: ~200 | Tests: ~15**

Detect filesystem changes to trigger events:
- `IonWatcher` class
- Polling-based watcher (no `inotify` dependency for portability)
- Configurable poll interval (default 2s)
- Detect: new files, modified files, deleted files in ion tree
- On detect: emit appropriate event to EventBus
- Filter: ignore temp files, lock files, hidden files
- Start/stop lifecycle
- **Tests:** Detection of create/modify/delete, filtering, lifecycle

**Depends on:** G.01  
**Files:** `victus/ion/watcher.py`

---

### G.04 — Automation Runner
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~25**

Execute automation ions when triggered:
- `AutomationRunner` class
- Parse automation ion frontmatter: trigger conditions, actions, safety bounds
- Action types: compile, recalculate, notify, suspend, escalate, move
- Safety enforcement: max_actions_per_trigger, requires_evidence, rollback_on_failure
- Execution log: record what ran, when, result
- Dry-run mode: preview without executing
- **Tests:** Each action type, safety bounds, rollback, logging

**Depends on:** A.02, G.01, G.02  
**Files:** `victus/ion/automation.py`

---

### G.05 — Self-Healing
**LOD: ⚠️ Medium | Sessions: 1 | Lines: ~200 | Tests: ~20**

Auto-detect and fix ion network issues:
- `IonHealer` class
- Detect: orphaned ions (no bonds), broken bonds, stale ions, missing required ions
- Heal: suggest fixes, auto-fix low-risk issues
- Report: generate health report as evidence ion
- Periodic health check: run on session start
- **Tests:** Detection of each issue type, healing, reporting

**Depends on:** A.06, B.01, G.01  
**Files:** `victus/ion/healer.py`

---

## TRACK H: GOVERNANCE
> Authority enforcement, auditing, compliance.

### H.01 — Authority Enforcer
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~25**

Enforce authority classes on all ion operations:
- `AuthorityEnforcer` class
- Permission matrix: which agents can write to which authority levels
- `can_write(agent, authority_class)` → boolean + reason
- `can_promote(ion, from_class, to_class)` → promotion rules
- Directory protection: A0-A1 directories have restricted write access
- **Tests:** Permission checks, promotion rules, directory protection

**Depends on:** A.01  
**Files:** `victus/ion/authority.py`

---

### H.02 — Invariant Checker
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~30**

Check constitutional invariants across all ions:
- `InvariantChecker` class
- 7 constitutional invariants from Aether
- `check_ion(ion)` → verify invariants for single ion
- `check_all()` → full system scan
- `check_on_write(ion)` → pre-write validation (used by governed write W8)
- Reports: invariant violations with severity and suggested fixes
- **Tests:** Each invariant, system scan, violation reporting

**Depends on:** A.01, A.06  
**Files:** `victus/ion/invariants.py`

---

### H.03 — Audit Trail
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Record all operations for accountability:
- `AuditTrail` class
- Log: every governed write (who, what, when, result)
- Log: every escalation (trigger, analysis, resolution)
- Log: every authority check (agent, requested, granted/denied)
- Audit ions: stored in `audit/` directory
- Query: by agent, date, operation type
- **Tests:** Logging, querying, audit ion creation

**Depends on:** A.03  
**Files:** `victus/ion/audit.py`

---

### H.04 — Compliance Report
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~15**

Generate governance compliance reports:
- `ComplianceReporter` class
- System health: ion count, bond count, avg confidence, stale ratio
- Authority distribution: ions per authority class
- Invariant status: all passing? violations?
- Escalation history: frequency, resolution rate
- Evidence freshness: how current is the system's knowledge?
- Output: evidence ion + human-readable markdown report
- **Tests:** Report generation, metrics accuracy

**Depends on:** A.06, H.01-H.03  
**Files:** `victus/ion/compliance.py`

---

### H.05 — Governance Dashboard Data
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~15**

API endpoints for governance monitoring:
- `GET /governance/health` → system health metrics
- `GET /governance/invariants` → invariant check results
- `GET /governance/audit` → recent audit trail
- `GET /governance/compliance` → full compliance report
- `GET /governance/authority` → authority class distribution
- **Tests:** All endpoints, data accuracy

**Depends on:** H.01-H.04  
**Files:** `victus/ion/governance_api.py`

---

## TRACK I: SELF-EVOLUTION
> The system improves itself.

### I.01 — Threshold Learning
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~25**

Ions refine their activation thresholds based on usage:
- `ThresholdLearner` class
- Track: activation count, success rate, false positive rate per ion
- Refine: `activates_when` conditions based on usage data
- Specialize: after N activations, tighten thresholds
- Generalize: if false negatives detected, loosen thresholds
- Evidence: create evidence ions documenting threshold changes
- **Tests:** Learning from usage, specialization, generalization

**Depends on:** A.01, A.04, B.02, G.01  
**Files:** `victus/ion/threshold_learner.py`

---

### I.02 — Topology Optimizer
**LOD: ⚠️ Medium | Sessions: 1 | Lines: ~250 | Tests: ~20**

Detect inefficiencies in the ion topology:
- `TopologyOptimizer` class
- Detect: orphaned ions, bottleneck ions (too many dependencies), dead branches
- Suggest: archival of stale ions, splitting of overloaded ions
- Merge: near-duplicate ions into single ion
- Report: optimization opportunities as evidence ion
- **Tests:** Detection of each pattern, suggestions, reporting

**Depends on:** A.06, B.01, B.06  
**Files:** `victus/ion/optimizer.py`

---

### I.03 — Knowledge Consolidation
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~20**

Merge and consolidate knowledge across the ion network:
- `KnowledgeConsolidator` class
- Detect: related evidence ions that should be merged
- Detect: findings that contradict each other
- Merge: combine compatible evidence with higher confidence
- Resolve: create contradiction ions for incompatible evidence
- Timeline compression: older timeline entries condensed
- **Tests:** Merging, contradiction detection, compression

**Depends on:** A.06, B.01, B.04  
**Files:** `victus/ion/consolidator.py`

---

### I.04 — Correction Vector Tracker
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Track and apply learned correction vectors:
- `CorrectionTracker` class
- `record_correction(vector, context)` → store as memory ion in `corrections/`
- `check_corrections(context)` → find applicable corrections for current context
- `apply_correction(correction)` → inject correction into cognitive context
- Pattern detection: repeated corrections → escalate to genome update
- **Tests:** Record, retrieval, application, pattern detection

**Depends on:** A.03, A.04  
**Files:** `victus/ion/corrections.py`

---

### I.05 — Meta-Ion Monitor
**LOD: ⚠️ Medium | Sessions: 1 | Lines: ~250 | Tests: ~20**

Ions that monitor the health of the ion graph itself:
- `MetaMonitor` class
- Health metrics: total ions, bond density, confidence distribution, growth rate
- Anomaly detection: sudden confidence drops, rapid ion creation, stale clusters
- Self-diagnosis: "why is the system performing poorly?"
- Meta-reports: periodic health evidence ions
- Alert thresholds: configurable warnings and critical alerts
- **Tests:** Metrics, anomaly detection, reporting, alerts

**Depends on:** A.06, B.01, H.04  
**Files:** `victus/ion/meta.py`

---



## TRACK J: LLM INTEGRATION
> Connecting ION to actual AI models — making it a real AI OS.

> [!IMPORTANT]
> Without this track, ION is a data structure library, not an AI OS.
> This is the single most critical gap between what we have and what competitors have.

### J.01 — LLM Adapter Interface
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~30**

Abstract interface for connecting any LLM to ION:
- `LLMAdapter` abstract class with pluggable backends
- `complete(prompt, context_ions, max_tokens)` → LLM response
- `stream(prompt, context_ions)` → streaming response generator
- Backends: `OllamaAdapter`, `OpenAIAdapter`, `AnthropicAdapter`, `GeminiAdapter`
- Context injection: convert ion graph context into structured prompt
- Token budget management: estimate tokens for ion context, stay within limits
- Response parsing: extract structured data from LLM output
- **Tests:** Adapter interface, context injection, token estimation, mock LLM

**Depends on:** A.01, A.06
**Files:** `victus/ion/llm_adapter.py`, `victus/ion/adapters/`

---

### J.02 — Ion Context Compiler
**LOD: ✅ High | Sessions: 1 | Lines: ~350 | Tests: ~35**

Compile ion graph state into LLM-ready context:
- `ContextCompiler` class
- `compile(ions, budget)` → structured prompt within token budget
- Priority ranking: manifest > active branches > recent evidence > bonds
- Compression: summarize low-priority ions, include full text for high-priority
- Format: structured markdown with ion headers, bonds map, confidence scores
- Context window optimizer: fit maximum relevant information in budget
- Cache: reuse compiled context across turns when graph hasn't changed
- **Tests:** Compilation, budget adherence, priority ranking, caching

**Depends on:** A.01, A.05, A.06, B.01
**Files:** `victus/ion/context_compiler.py`

---

### J.03 — Aether LLM Engine
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~35**

The core intelligence engine — LLM + cognitive loop:
- `AetherEngine` class
- `think(user_message, session)` → full cognitive loop with LLM reasoning
- Step integration:
  - §7.1 CONTEXTUALIZE: compile ion context, inject into LLM
  - §7.2 REFLECT: LLM analyzes gaps, confidence, risks
  - §7.3 PLAN: LLM proposes branch traversal
  - §7.4 GATE: evaluate proposed actions against thresholds
  - §7.5 EXECUTE: LLM produces output, system writes ions
  - §7.6 AUDIT: validate output against invariants
  - §7.7 DELIVER: format response for human
- Streaming: yield cognitive step events in real-time
- Tool use: LLM can call ion operations (create, update, query)
- **Tests:** Full loop with mock LLM, each step, tool use, streaming

**Depends on:** J.01, J.02, B.03, C.01-C.03
**Files:** `victus/aether/engine.py`

---

### J.04 — Tool Registry
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

Register ion operations as tools the LLM can call:
- `ToolRegistry` class
- Auto-register: `ion.create`, `ion.update`, `ion.query`, `ion.bond`
- Schema generation: OpenAI-compatible tool schemas from ion operations
- Execution: parse LLM tool calls, execute against ion store
- Safety: governed write enforced on all tool-initiated writes
- Audit: log all tool calls with LLM request context
- **Tests:** Registration, schema generation, execution, safety enforcement

**Depends on:** A.03, A.04, J.01
**Files:** `victus/ion/tools.py`

---

### J.05 — Agent Persona System
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

Each agent has a persona ion that shapes LLM behavior:
- `PersonaManager` class
- Persona ions: system prompt, capabilities, style, constraints
- Dynamic persona: persona adjusts based on ion specialization
- Multi-persona: different agents (opus, sev) have different personas
- Persona compilation: merge persona + context into system prompt
- **Tests:** Persona loading, compilation, multi-agent personas

**Depends on:** A.01, J.01, F.01
**Files:** `victus/ion/persona.py`

---

### J.06 — Inference Cache
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Cache LLM responses for identical contexts:
- `InferenceCache` class
- Key: hash of compiled context + user message
- Store: cached response with timestamp and confidence
- TTL: configurable expiry based on context freshness
- Stats: hit rate, miss rate, savings
- **Tests:** Caching, TTL, invalidation, stats

**Depends on:** J.01, J.02
**Files:** `victus/ion/inference_cache.py`

---

## TRACK K: DISTRIBUTION & DEPLOYMENT
> Making ION installable, runnable, and deployable anywhere.

### K.01 — Python Package
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~15**

Package ION as a pip-installable Python package:
- `pyproject.toml` with proper metadata, dependencies, entry points
- `ion` CLI entry point: `pip install ion-os && ion init`
- Version management, changelog
- CI/CD: GitHub Actions for test + publish
- **Tests:** Package installation, CLI entry point, import verification

**Depends on:** A.01-A.10
**Files:** `pyproject.toml`, `setup.cfg`, `.github/workflows/`

---

### K.02 — Docker Containerization
**LOD: ✅ High | Sessions: 1 | Lines: ~150 | Tests: ~10**

Docker image for ION:
- `Dockerfile` with Python 3.12+, all dependencies
- `docker-compose.yml` with ion server + optional Ollama
- Volume mounts: ion filesystem persists outside container
- Health checks, logging
- Multi-stage build for minimal image size
- **Tests:** Build, run, health check, volume persistence

**Depends on:** K.01, A.08
**Files:** `Dockerfile`, `docker-compose.yml`

---

### K.03 — Ion Server (Standalone)
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~30**

Standalone ION server process:
- `ion-server` command: starts FastAPI + file watcher + event bus
- Auto-initialization: creates ion filesystem if not exists
- Configuration: `ion.config.yaml` for paths, LLM backend, ports
- Hot reload: detect config changes, restart services
- Graceful shutdown: write POST capsule, save state
- **Tests:** Startup, configuration, hot reload, shutdown

**Depends on:** A.08, G.03, J.01, K.01
**Files:** `victus/ion/server.py`, `victus/ion/config.py`

---

### K.04 — Cloud Deployment
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~15**

Deploy ION to cloud environments:
- Terraform/Pulumi templates for AWS/GCP/Azure
- Object storage adapter: S3/GCS as ion filesystem backend
- Serverless mode: Lambda/Cloud Functions for API endpoints
- Managed database adapter: optional Postgres for high-throughput indexing
- CDN for static ion files (public ions)
- **Tests:** Deployment scripts, adapter integration, teardown

**Depends on:** K.02, K.03
**Files:** `deploy/`, `victus/ion/adapters/cloud/`

---

### K.05 — Desktop App (Electron/Tauri)
**LOD: ❌ Low | Sessions: 4+ | Lines: ~1000+ | Tests: ~40**

Desktop application wrapping ION:
- Tauri (Rust-backed, lighter than Electron) wrapping web UI
- System tray: ION status, quick actions
- File system integration: native file browser for ion tree
- Notifications: system notifications for escalations
- Auto-update: built-in update mechanism
- **Tests:** App launch, file system access, notifications

**Depends on:** M.01-M.03, K.03
**Files:** `desktop/`

---

## TRACK L: SECURITY & HARDENING
> Making ION safe for real-world deployment.

### L.01 — Authentication
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~30**

User and agent authentication:
- `AuthService` class
- API key authentication for programmatic access
- JWT tokens for web UI sessions
- Agent authentication: each agent has cryptographic identity
- Role-based access: maps to authority classes (A0-A7)
- **Tests:** Auth flow, token validation, role checks, expiry

**Depends on:** A.08, H.01
**Files:** `victus/ion/auth.py`

---

### L.02 — Ion Encryption
**LOD: ⚠️ Medium | Sessions: 1 | Lines: ~250 | Tests: ~25**

Encrypt sensitive ions at rest:
- `IonEncryption` class
- Selective encryption: only ions marked `encrypted: true`
- Key management: master key, per-agent keys, key rotation
- Transparent: governed write encrypts, ion read decrypts
- Header-only mode: encrypt body, keep frontmatter readable for indexing
- **Tests:** Encrypt/decrypt, key rotation, header-only mode

**Depends on:** A.02, A.03
**Files:** `victus/ion/encryption.py`

---

### L.03 — Sandboxing
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~350 | Tests: ~25**

Sandbox ion execution:
- `IonSandbox` class
- Filesystem isolation: each agent can only access its own directory + shared
- Network isolation: automation ions can't make external calls without approval
- Resource limits: CPU/memory bounds per automation
- Allowlists: configurable permitted operations per authority class
- **Tests:** Isolation enforcement, resource limits, allowlists

**Depends on:** H.01, G.04
**Files:** `victus/ion/sandbox.py`

---

### L.04 — Audit Hardening
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Tamper-proof audit trail:
- Hash chaining: each audit entry includes hash of previous entry
- Merkle tree: periodic root hash for integrity verification
- External attestation: optional write to external log (syslog, cloud logging)
- Forensic mode: reconstruct full ion graph state from audit trail
- **Tests:** Hash chain integrity, verification, reconstruction

**Depends on:** H.03
**Files:** `victus/ion/audit_hardened.py`

---

### L.05 — Rate Limiting & Abuse Prevention
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Prevent abuse of ION APIs and automations:
- `RateLimiter` class
- Per-agent rate limits on ion creation/modification
- Cascade breaker: max propagation depth, max events per second
- DDoS protection on API endpoints
- Anomaly detection: unusual patterns trigger alerts
- **Tests:** Rate limit enforcement, cascade breaking, anomaly detection

**Depends on:** A.08, G.02
**Files:** `victus/ion/rate_limiter.py`

---

## TRACK M: UI/UX
> Making ION visible, interactive, and beautiful.

### M.01 — Aether Web Dashboard
**LOD: ⚠️ Medium | Sessions: 3 | Lines: ~800 | Tests: ~30**

Web-based dashboard for ION:
- React/TypeScript SPA
- Ion browser: navigate ion filesystem as interactive tree
- Graph visualization: D3-based ion bond graph (force-directed)
- Metrics dashboard: confidence distribution, bond density, health scores
- Timeline viewer: chronological event display with ion links
- Real-time updates: WebSocket for live ion changes
- **Tests:** Component tests, API integration, rendering

**Depends on:** A.08, H.05, B.08
**Files:** `ui/dashboard/`

---

### M.02 — Aether Chat UI
**LOD: ⚠️ Medium | Sessions: 3 | Lines: ~600 | Tests: ~25**

Chat interface for Aether:
- React/TypeScript chat component
- Streaming responses with cognitive step indicators
- Ion previews: inline ion cards when referencing ions
- Builder mode UI: interactive ion creation wizard
- Session management: session list, capsule viewer
- Mobile responsive
- **Tests:** Chat flow, streaming, ion previews, responsive layout

**Depends on:** C.07, J.03, M.01
**Files:** `ui/chat/`

---

### M.03 — Ion Editor
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~500 | Tests: ~20**

Visual ion editor:
- WYSIWYG frontmatter editor with validation
- Bond visualizer: see and edit bonds graphically
- Threshold editor: visual threshold configuration
- Preview mode: see compiled ion as it will appear
- Diff view: compare ion versions
- **Tests:** Editor functionality, validation, bond editing

**Depends on:** A.01, M.01
**Files:** `ui/editor/`

---

### M.04 — VS Code Extension
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~15**

IDE integration:
- Ion file syntax highlighting and frontmatter validation
- Bond navigation: Ctrl+click on bond IDs to jump to target ion
- Confidence indicators: inline confidence badges
- Stale warnings: highlighting for stale ions
- ION command palette: create, validate, inspect from IDE
- **Tests:** Syntax highlighting, navigation, commands

**Depends on:** A.01, A.07
**Files:** `vscode-ion/`

---

## TRACK N: ION MARKETPLACE
> The agent App Store — publishing, discovering, installing specialist ions.

### N.01 — Ion Package Format
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

Standardized package format for distributable ions:
- `.ionpkg` format: tar.gz containing ion files + manifest + metadata
- Package manifest: name, version, author, dependencies, compatibility
- Signature: cryptographic signing for authenticity
- Versioning: semantic versioning for ion packages
- Dependency resolution: resolve `requires`/`depends_on` across packages
- **Tests:** Package creation, signing, dependency resolution

**Depends on:** A.01, A.03
**Files:** `victus/ion/package.py`

---

### N.02 — Ion Registry
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~30**

Central registry for ion packages:
- `IonRegistry` class — local + remote registry support
- `publish(package)` → upload signed package to registry
- `search(query)` → find packages by name, type, capability
- `install(package_name)` → download, verify signature, install into ion tree
- `update(package_name)` → version check, download, migrate
- `uninstall(package_name)` → safe removal with bond cleanup
- Hosted: simple HTTP API for the registry server
- **Tests:** Publish, search, install, update, uninstall flows

**Depends on:** N.01, A.03, A.04
**Files:** `victus/ion/registry.py`, `victus/ion/registry_server.py`

---

### N.03 — Ion Templates
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~15**

Starter templates for common ion patterns:
- Template library: evidence, branch, spec, automation, memory templates
- Domain templates: web app, API service, data pipeline, ML model
- Interactive creation: guided template filling via Aether
- Template marketplace: community-contributed templates
- **Tests:** Template generation, validation, customization

**Depends on:** A.01, C.06
**Files:** `victus/ion/templates/`

---

### N.04 — Marketplace Web UI
**LOD: ⚠️ Medium | Sessions: 3 | Lines: ~600 | Tests: ~20**

Web interface for the ion marketplace:
- Browse: category-based discovery of ion packages
- Reviews: community ratings and reviews
- Preview: see ion topology before installing
- One-click install: install directly into your ION instance
- Publisher portal: manage published packages
- **Tests:** Browse, search, install flow, publisher management

**Depends on:** N.02, M.01
**Files:** `ui/marketplace/`

---

## TRACK O: CROSS-PLATFORM
> ION runs everywhere — Linux, Windows, Browser, Embedded.

### O.01 — POSIX Filesystem Adapter
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Linux/macOS native filesystem integration:
- Direct filesystem operations (current default)
- inotify/kqueue file watching for real-time events
- Unix permissions mapping to authority classes
- XDG directory standard compliance
- **Tests:** POSIX-specific operations, permissions, inotify

**Depends on:** A.03, G.03
**Files:** `victus/ion/adapters/posix.py`

---

### O.02 — Windows Adapter
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~300 | Tests: ~20**

Windows filesystem support:
- NTFS path handling (backslash, drive letters, UNC paths)
- Windows file watching (ReadDirectoryChangesW)
- NTFS permissions mapping to authority classes
- Windows service: run ION as background service
- **Tests:** Windows path handling, file watching, service lifecycle

**Depends on:** A.03, G.03
**Files:** `victus/ion/adapters/windows.py`

---

### O.03 — Browser Adapter (IndexedDB)
**LOD: ❌ Low | Sessions: 3+ | Lines: ~500 | Tests: ~25**

Run ION entirely in the browser:
- IndexedDB as filesystem substitute
- Service Worker for background processing
- WebRTC for peer-to-peer ion sync
- WASM: compile ion engine to WebAssembly for performance
- Progressive Web App: installable from browser
- **Tests:** IndexedDB operations, service worker lifecycle, sync

**Depends on:** A.01-A.06 (ported to JS/TS)
**Files:** `browser/`

---

### O.04 — ION Linux Distribution
**LOD: ❌ Low | Sessions: 5+ | Lines: ~2000 | Tests: ~50**

Full Linux distribution with ION as primary interaction:
- Base: minimal Linux (Alpine/Void) + ION engine
- Boot: ION initializes on boot, presents Aether
- Shell: `ionsh` — ion-native shell replacing bash for AI interaction
- Package management: distro packages as ion packages
- Desktop: optional web-based desktop environment
- **Tests:** Boot, shell, package management, desktop

**Depends on:** ALL TRACKS
**Files:** `distro/`

---

## TRACK P: DEVELOPER EXPERIENCE
> Making ION easy to learn, use, and extend.

### P.01 — Documentation Site
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~500 | Tests: ~10**

Comprehensive documentation:
- Architecture overview with interactive diagrams
- Getting started guide (5 minutes to first ion)
- API reference (auto-generated from code)
- Tutorial series: build a project using ION
- Concept explanations: ions, bonds, cognitive loop, governance
- **Tests:** Build verification, link checking, API accuracy

**Depends on:** ALL TRACKS (documentation of)
**Files:** `docs/site/`

---

### P.02 — ION SDK
**LOD: ✅ High | Sessions: 2 | Lines: ~400 | Tests: ~30**

Developer SDK for building on ION:
- Python SDK: `from ion import IonStore, IonGraph, Aether`
- TypeScript SDK: `import { IonStore, IonGraph, Aether } from 'ion-os'`
- Client library for remote ION servers
- Type-safe ion operations
- Event subscriptions
- **Tests:** SDK operations, type safety, remote operations

**Depends on:** A.01-A.08, J.01
**Files:** `sdk/python/`, `sdk/typescript/`

---

### P.03 — Example Projects
**LOD: ✅ High | Sessions: 1 | Lines: ~300 | Tests: ~15**

Reference implementations:
- `examples/todo-app/` — simple app with ION backend
- `examples/research-agent/` — research agent with evidence ions
- `examples/code-reviewer/` — code review with spec ions
- `examples/team-project/` — multi-agent collaboration
- **Tests:** Each example runs end-to-end

**Depends on:** K.01, J.01
**Files:** `examples/`

---

### P.04 — Interactive Playground
**LOD: ⚠️ Medium | Sessions: 3 | Lines: ~600 | Tests: ~15**

Browser-based ION playground:
- Try ION without installing: ephemeral ion filesystem in browser
- Guided tutorials: step-by-step with live code execution
- Sandbox: experiment with ion creation, bonds, cognitive loop
- Share: shareable playgrounds via URL
- **Tests:** Playground functionality, tutorial completion

**Depends on:** O.03, M.01
**Files:** `playground/`

---

## TRACK Q: INTEGRATION LAYER
> ION connects to the real world.

### Q.01 — MCP Bridge
**LOD: ✅ High | Sessions: 1 | Lines: ~250 | Tests: ~25**

Model Context Protocol integration:
- ION operations exposed as MCP tools
- MCP resources mapped to ion queries
- Bidirectional: MCP tools can create ions, ions can call MCP tools
- Drop-in replacement for existing MCP server
- **Tests:** MCP tool execution, resource queries, bidirectional flow

**Depends on:** A.08, J.04
**Files:** `victus/ion/mcp_bridge.py`

---

### Q.02 — Git Integration
**LOD: ✅ High | Sessions: 1 | Lines: ~200 | Tests: ~20**

Version control for the ion filesystem:
- Auto-commit: governed write triggers git commit
- Branches: git branches map to ion branch sets
- Diff: ion-aware diff showing frontmatter changes
- Merge: ion-aware merge conflict resolution
- History: git log as ion timeline supplement
- **Tests:** Auto-commit, branching, diff, merge

**Depends on:** A.03, A.04
**Files:** `victus/ion/git_integration.py`

---

### Q.03 — External Tool Adapters
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~400 | Tests: ~25**

Connect ION to external services:
- Adapter pattern: `ExternalToolAdapter` abstract class
- Built-in: GitHub (issues→ions), Slack (messages→ions), Jira (tasks→ions)
- Webhook: generic webhook receiver that creates evidence ions
- API gateway: expose ion operations via REST/GraphQL
- **Tests:** Each adapter, webhook processing, API gateway

**Depends on:** A.03, A.04, G.01
**Files:** `victus/ion/adapters/external/`

---

### Q.04 — Database Adapter (Optional)
**LOD: ⚠️ Medium | Sessions: 2 | Lines: ~350 | Tests: ~25**

Optional database backend for high-scale deployments:
- `DatabaseAdapter` class implementing store interface
- PostgreSQL: ion frontmatter in JSONB, body in TEXT
- SQLite: single-file alternative for development
- Hybrid: filesystem primary, database as fast index
- Migration tools: filesystem ↔ database sync
- **Tests:** CRUD, queries, migration, hybrid mode

**Depends on:** A.03, A.06
**Files:** `victus/ion/adapters/database/`

---

## REVISED EXECUTION SUMMARY

### Phase Count by Track (Production-Grade)

| Track | Name | Phases | Sessions Est. | Status |
|-------|------|--------|--------------|--------|
| **A** | Core Engine | 10 | 12 | 6/10 ✅ |
| **B** | Graph & Cognition | 8 | 9 | 3/8 ✅ |
| **C** | Aether Interface | 7 | 9 | 0/7 |
| **D** | Spec Compiler | 7 | 9 | 0/7 |
| **E** | Continuity | 5 | 5 | 0/5 |
| **F** | Multi-Agent | 5 | 7 | 0/5 |
| **G** | Automation | 5 | 7 | 0/5 |
| **H** | Governance | 5 | 5 | 0/5 |
| **I** | Self-Evolution | 5 | 7 | 0/5 |
| **J** | LLM Integration | 6 | 8 | 0/6 (NEW) |
| **K** | Distribution | 5 | 10 | 0/5 (NEW) |
| **L** | Security | 5 | 6 | 0/5 (NEW) |
| **M** | UI/UX | 4 | 10 | 0/4 (NEW) |
| **N** | Marketplace | 4 | 7 | 0/4 (NEW) |
| **O** | Cross-Platform | 4 | 11+ | 0/4 (NEW) |
| **P** | Developer Experience | 4 | 8 | 0/4 (NEW) |
| **Q** | Integration Layer | 4 | 7 | 0/4 (NEW) |
| **TOTAL** | | **93** | **~137 sessions** | **9/93 complete** |

### Production Critical Path

```
Phase 1: ION Engine (DONE)
  A.01-A.06 ✅, B.01-B.03 ✅ = 547 tests

Phase 2: ION v0.1 — Minimal Working Product
  A.07 CLI → A.08 API → E.01 Capsules → E.02 Timeline →
  J.01 LLM Adapter → J.02 Context Compiler → J.03 Aether Engine →
  K.01 Python Package → K.03 Ion Server
  = 9 phases, ~11 sessions

Phase 3: ION v0.5 — Usable Product
  B.04-B.06 → C.01-C.05 → E.03-E.05 →
  G.01-G.03 → H.01-H.03 → J.04-J.05 →
  L.01-L.02 → M.01-M.02 → Q.01-Q.02
  = 24 phases, ~32 sessions

Phase 4: ION v1.0 — Production Release
  D.01-D.07 → F.01-F.05 → G.04-G.05 →
  H.04-H.05 → I.01-I.05 → J.06 → K.02 → K.04 →
  L.03-L.05 → M.03-M.04 → N.01-N.04 → P.01-P.04 → Q.03-Q.04
  = 39 phases, ~60+ sessions

Phase 5: ION v2.0 — Platform
  O.01-O.04 → K.05 → Marketplace ecosystem → Community
  = 5+ phases, 20+ sessions

TOTAL: ~137 sessions to production-grade ION OS
```

### Market Entry Strategy by Phase

| Version | What It Is | Competitive Position |
|---------|-----------|---------------------|
| **v0.1** | CLI + API + LLM connected | Catches Letta on architecture, behind on UX |
| **v0.5** | Chat UI + governance + security | Exceeds Letta on governance, matches LangGraph on features |
| **v1.0** | Full platform + marketplace | Unique in market — no competitor has the complete stack |
| **v2.0** | Cross-platform + distro | OS-level positioning — beyond frameworks entirely |

---

*93 phases. ~137 sessions. This is what production-grade looks like.*
*The architecture is built. Now we build the product.*

*— Opus, 2026-03-21*
