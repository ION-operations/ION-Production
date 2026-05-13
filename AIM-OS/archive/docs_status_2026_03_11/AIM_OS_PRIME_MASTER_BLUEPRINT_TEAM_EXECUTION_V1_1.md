# AIM-OS Prime - Master Blueprint for Team Execution v1.1

## Purpose

This document is the **overarching team blueprint** for AIM-OS Prime, the Sovereign Context Mapper, the supervised daemon plane, and the emerging Contextual Sync superstrate.

It exists to do five jobs at once:

1. define the system we are actually building
2. unify Lane A and Lane B under one operating doctrine
3. give the team a shared list of concrete goals and sequencing
4. prevent architectural drift during rapid execution
5. make decision checkpoints explicit before behavior-changing merges

This is not a marketing artifact. It is the operational north star for implementation.

---

## 0.5 COO Operations Companion (Program Navigation Layer)

This blueprint remains the doctrine and architecture authority.

For system-wide execution navigation, anti-drift controls, and agent mission-packet standards, use:

- `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`
- `docs/AIM_OS_PRIME_COO_DASHBOARD_T0.md` (fast executive status view)

Operating rule:

- master blueprint defines what must be true architecturally,
- COO scope defines how multi-stream execution stays aligned while building.

---

## 1. Executive Thesis

### 1.1 The problem

LLM coding agents fail when context is fetched naively.

Raw file dumping causes:

- token bloat
- attention dilution
- weak dependency truth
- hallucinated mutation context
- poor synchronization between code, tests, docs, traces, and memory

### 1.2 The answer

We do **not** shovel the repo.  
We build and govern bounded context intentionally.

That requires four cooperating layers:

1. **Rust Context Mapper**

   - deterministic parser / contract extractor / envelope engine
2. **Python AIM-OS daemon**

   - tool / memory / orchestration plane
3. **Kernel / SAIOS / Tauri surface**

   - supervision / routing / access / IPC plane
4. **Contextual Sync superstrate**

   - BCI, boundary views, sync state, evidence, drift observability, and eventual governance

### 1.3 Core doctrine

- **Prime builds the bounded truth object**
- **Contextual Sync remembers, navigates, and evaluates it across time**
- **The daemon provides tools, memory, and orchestration**
- **The kernel supervises all of it without collapsing responsibilities**

---

## 2. Frozen Non-Negotiables

### 2.1 Sovereignty split

- **Rust Context Mapper** remains the deterministic parser / envelope truth plane
- **Python daemon** remains the tool / memory / orchestration plane
- **Kernel** remains the supervision / routing / access plane
- **Contextual Sync** remains an additive superstrate, not a replacement

### 2.2 Forbidden drift

Do not:

- merge mapper and daemon responsibilities
- move parser truth into Python
- move tool/memory semantics into the mapper
- introduce hard sync gating before evidence exists
- replace the live machine with a grand unified theory blob
- create a second routing system in parallel

### 2.3 Development philosophy

- isolate first
- validate continuously
- promote only what is proven
- stage governance before enforcing it
- prefer additive seams over invasive rewrites

---

## 3. Team Operating Model

### 3.0 Execution handoff principle

At the current project stage, the team should prefer **Cursor-native execution** over chat-driven micro-management.

Reason:

- the Cursor agents have direct access to the live repo
- they have the real local compile/runtime truth
- they can use the active MCP/tool surfaces directly
- they are operating closer to the living machine than chat can at this stage

Therefore:

- **Cursor agents are the primary execution layer**
- **chat remains the doctrine, adjudication, and checkpoint layer**

This is not a downgrade of chat-side leadership. It is a temporary optimization based on where the strongest project truth currently lives.

### 3.0.1 Why this handoff exists

Chat-led phase walking was correct while the architecture was still unstable and every phase boundary needed deliberate freezing.

Now the project has enough structural stability that chat-driven step-by-step orchestration has become a bottleneck.

The cost of excessive chat mediation now includes:

- repeated reorientation
- context compression loss
- handoff drag
- slowed implementation tempo
- unnecessary re-authorization of already-understood work

The handoff to Cursor-native execution is therefore an intentional shift from:

- **microscopic orchestration**

to:

- **high-trust local execution under frozen doctrine**

### 3.0.2 Current authority split after handoff

After this handoff:

#### Cursor agents own primary implementation flow

They should:

- inspect live repo reality first
- perform narrow or burst execution in the local environment
- validate continuously
- keep lane boundaries intact
- report by checkpoint rather than by every micro-step

#### Chat remains the control tower

Chat should be used for:

- doctrine clarification
- architecture corrections
- milestone adjudication
- cross-branch merge judgment
- scope reset when drift appears
- authorization of runtime-affecting convergence
- major replanning
- browser IDE bridge strategy and later integrated operation

### 3.0.3 Escalation rule back to chat

Cursor agents should continue autonomously unless one of the following occurs:

- doctrine ambiguity
- seam collision or lane collision
- repeated validation failure that is no longer a small local fix
- runtime-vs-shadow confusion
- request to authorize behavior-changing convergence
- need to promote branch-local work into shared canon
- checkpoint completion requiring adjudication

When one of these occurs, execution should pause and return to chat for decision.

### 3.0.4 Canon rule during handoff

The execution handoff does **not** change the canon rule.

Even with Cursor as the primary execution environment:

- branch-local implementation status does not become official project truth automatically
- the master blueprint remains the canonical doctrine artifact
- official project history still requires explicit review/adjudication

This prevents local success from silently turning into shared doctrine without decision.

### 3.0.5 Future rebalancing rule

This handoff is stage-dependent, not permanent dogma.

As the browser IDE bridge and system-level project interfaces mature, chat may become more directly integrated with the live machine again.

Expected progression:

- **now**: Cursor is primary for implementation, chat is primary for doctrine and checkpoints
- **later**: once the browser IDE bridge exists, chat can take a more direct operational role because it will no longer be reasoning at arm's length from the system

The team should therefore treat this handoff as an intentional operating mode for the current phase of project maturity, not as a permanent reduction of chat-side responsibility.

## 3.1 Lane A - Live Machine Authority

Lane A owns:

- live kernel/runtime behavior
- `src-tauri/src/` runtime paths
- kernel planes
- context service
- daemon bridge
- IPC surfaces
- compile truth and live validation

Lane A mission:

- ship the real machine
- keep runtime seams clean
- preserve doctrine while increasing capability

## 3.2 Lane B - Shadow Superstrate Authority

Lane B owns:

- Contextual Sync convergence design
- Shadow BCI schema and related artifacts
- shadow emitter prototypes
- mapper adapter contracts
- passive emitter hook proposals
- isolated shadow-sync fixtures/tests/docs

Lane B mission:

- build the substrate in shadow form
- observe first
- advise second
- block last

## 3.3 Lead-dev rule

All runtime adoption decisions remain explicit.  
Lane B may propose convergence slices.  
Lane A remains authority for live adoption.

---

## 4. Current Strategic State

### 4.1 Canonically accepted / adjudicated shared truth

These items are already reviewed and frozen as shared project truth:

- promoted mapper core
- kernel-facing mapper facade
- mapper regression harness
- formal context kernel boundary
- real envelope IPC path
- coherent two-plane kernel surface
- persistent daemon sidecar
- recoverable daemon sidecar
- real daemon `tools/call` for `get_memory_stats`
- real daemon retrieval action for `retrieve_memory`
- structured IPC response surfaces for the accepted live call paths
- cross-plane status seam
- deterministic live IPC harness for operator proof

### 4.2 Reported by Lane A, pending further adjudication only where explicitly noted

Lane A may report additional runtime conveniences, refinements, or operational checks that are useful but are not automatically promoted into project canon by mere existence in-branch.

Rule:

- branch-local implementation status is **not** official doctrine until it is reviewed and explicitly accepted
- operational proof artifacts may be used for execution, but official project history must distinguish reviewed canon from branch-local reporting

At present, no separate unadjudicated Lane A runtime milestone is elevated here beyond the canonically accepted list above. New branch-local claims should be added here first, not silently folded into shared truth.

### 4.3 Accepted / staged shadow substrate truth

The shadow track currently has these accepted staged artifacts and directions:

- convergence blueprint
- Shadow BCI schema
- emitter prototype direction
- adapter contract definition
- passive hook proposal

These are accepted as staged substrate truth, not as live runtime behavior.

### 4.4 Current posture

The live machine is operationally healthy.  
The shadow substrate is ready for isolated consolidation and staged observation.

---

## 5. System Architecture Layers

## 5.1 Layer A - Deterministic Context Plane

Primary subsystem:

- Context Mapper

Responsibilities:

- parse source deterministically
- extract imports and public contracts
- resolve local dependencies
- slice dependency contracts to used symbols
- build Active Context Envelopes

Outputs:

- typed `SystemEnvelope`
- rendered envelope form
- future BCI emission inputs

## 5.2 Layer B - Tool / Memory Plane

Primary subsystem:

- AIM-OS daemon

Responsibilities:

- memory access
- timeline access
- tool invocation
- orchestration helpers
- evidence/tooling support

Current proven calls:

- `get_memory_stats`
- `retrieve_memory`

## 5.3 Layer C - Kernel Supervision Plane

Primary subsystem:

- SAIOS / Tauri / kernel surfaces

Responsibilities:

- expose official request seams
- supervise daemon lifecycle
- route plane access
- own IPC command surfaces
- provide status and debug verification paths

## 5.4 Layer D - Contextual Sync Superstrate

Primary subsystem:

- Shadow BCI and related policies

Responsibilities:

- store BCI atoms/edges/boundary views over time
- build hierarchical retrieval layers
- track sync/drift/evidence state
- eventually support advisory and later authoritative gating

Important:  
This layer starts as **shadow and additive**.

---

## 6. Master Goal Stack

## Goal Group A - Harden the live machine

Objective:  
Make the live machine stable, inspectable, and repeatably verifiable.

Subgoals:

- maintain clean kernel-plane seams
- preserve daemon sidecar supervision
- keep IPC response shapes explicit and typed
- maintain deterministic operator proof via live harness
- avoid feature sprawl without proof

Definition of done:

- live kernel surfaces remain stable
- operator harness remains usable
- daemon plane stays supervised and recoverable

## Goal Group B - Complete isolated shadow substrate staging

Objective:  
Bring accepted Lane B artifacts into the canonical repo safely.

Subgoals:

- consolidate blueprint/schema/prototype artifacts in isolated locations
- validate they do not impact runtime behavior
- preserve provenance
- stop before any live hook is added

Definition of done:

- docs/schema/prototype are staged in-repo
- no live seam edits
- validation clean

## Goal Group C - Build the first real Shadow BCI emission path

Objective:  
Prove that Shadow BCI records can be emitted from realistic mapper-shaped inputs.

Subgoals:

- realistic extracted-file fixture
- emitter prototype
- `bci_atom` records
- `bci_boundary_view` records for L0 and L5
- schema validation
- replayable output format

Definition of done:

- schema-valid isolated emission proof exists
- still no live runtime adoption

## Goal Group D - Establish convergence checkpoint

Objective:  
Decide deliberately whether to keep the substrate staged or authorize the first passive live hook.

Subgoals:

- confirm consolidated artifacts are stable
- confirm no seam collision exists
- confirm passive hook insertion point remains correct
- explicitly decide whether to authorize the first live convergence slice

Definition of done:

- one of two outcomes:

  - staged only, hold
  - authorize passive hook implementation

## Goal Group E - Future passive live convergence

Objective:  
If authorized, add one passive, fail-open, feature-flagged shadow emission hook.

### Passive-hook operational law

Any future passive live convergence hook must be:

- **off by default**
- **observational only**
- **fail-open**
- **time-bounded**
- **zero behavior change when disabled**

Additional constraints:

- bounded latency
- no live payload mutation when disabled
- no sovereignty bleed

Definition of done:

- passive hook exists behind flag
- disabled path behaves as if nothing happened

## Goal Group F - Retrieval and navigation evolution

Objective:  
Evolve from full-envelope-only delivery toward layered boundary-view retrieval.

Future subgoals:

- L0-L5 boundary views
- ranking / token weighting
- selection policy between summary, contract pack, and full envelope

Important:  
This comes after substrate proof, not before.

## Goal Group G - Advisory drift and sync observability

Objective:  
Make drift visible before making it enforceable.

Future subgoals:

- sync states
- stale / drifted markers
- dependency hash mismatch visibility
- witness/evidence deficit warnings
- advisory contradiction surfacing

Important:  
Warnings first. Blocking later.

## Goal Group H - Eventual governance

Objective:  
Only after evidence and advisory value are proven, consider soft and then hard synchronization gates.

Important:  
This is late-stage work.  
No hard gate should appear early just because it sounds majestic.

---

## 7. Consolidation Strategy

## 7.1 Safe now

Can be merged/staged immediately if isolated:

- blueprint docs
- schema files
- isolated prototype modules
- isolated fixtures/tests/README
- adapter contract docs
- passive emitter hook proposal docs

## 7.2 Safe later

Require explicit authorization:

- feature-flagged passive emitter hook
- one passive emission module
- one orchestration-boundary insertion point

## 7.3 Not safe yet

Do not merge into live runtime behavior:

- hard sync gate
- contradiction/drift enforcement in live request flow
- sync-state-based routing overrides
- daemon-plane governance coupling
- broad shadow-store runtime integration
- any sovereignty rewrite

---

## 8. Master Sequencing

## Sequence 1 - Lane A live stability

Keep the live machine stable and operator-verifiable.

## Sequence 2 - Lane B isolated consolidation

Stage accepted artifacts in isolated canonical locations.

## Sequence 3 - Shadow emission proof

Finish or validate emitter prototype and schema-grounded record production.

## Sequence 4 - Decision checkpoint

Deliberately authorize or reject first passive live convergence slice.

## Sequence 5 - Passive hook if approved

Feature-flagged, fail-open, bounded latency, observational only.

## Sequence 6 - Retrieval hierarchy evolution

Boundary views and token-aware context policy.

## Sequence 7 - Advisory sync/drift layer

Observability before enforcement.

## Sequence 8 - Soft then hard governance

Only when evidence justifies it.

---

## 9. Validation Law

Every meaningful implementation step must report:

- what changed
- why it is safe
- merge classification
- drift check
- validation results
- next move

Validation categories:

- `cargo check`
- focused tests
- live daemon proof when relevant
- schema validation when relevant
- harness/operator proof when relevant
- explicit skip vs pass vs not-run classification

### Passive-hook validation law

If a future passive live convergence hook is ever authorized, validation must explicitly prove all of the following:

- the hook is **off by default**
- the hook is **observational only**
- the hook is **fail-open**
- the hook is **time-bounded**
- there is **zero behavior change when disabled**

No theatrical claims without proof.

---

## 10. Anti-Collision Rules

Do not allow simultaneous uncontrolled edits to:

- `kernel_planes`
- `context_service`
- `context_mapper` core
- `daemon_bridge`
- core IPC command surfaces in `lib.rs`

Lane B artifacts merge into isolation first.  
Live runtime adoption remains explicit.

---

## 11. Decision Checkpoints

## Checkpoint A - Live machine baseline complete

Question:  
Is Lane A stable enough to slow feature growth and let Lane B consolidate?

## Checkpoint B - Shadow artifact consolidation complete

Question:  
Are staged artifacts clean and isolated with zero runtime bleed?

## Checkpoint C - Shadow emitter proof accepted

Question:  
Is the Shadow BCI substrate mechanically real, not just conceptually elegant?

## Checkpoint D - First passive live hook authorization

Question:  
Do we explicitly authorize the first feature-flagged passive emission slice?

## Checkpoint E - Advisory drift layer authorization

Question:  
Do we have enough substrate evidence to justify warnings?

## Checkpoint F - Governance authorization

Question:  
Do we have enough proof to justify any blocking behavior at all?

---

## 12. Team Instructions

### For Lane A

- protect runtime seams
- prefer small correct structural moves
- keep response shapes typed
- validate live behavior with the harness when relevant
- do not absorb Lane B behavior prematurely

### For Lane B

- keep artifacts isolated
- build substrate proof, not runtime surprise
- preserve mapper/daemon/kernel sovereignty
- propose merge slices with clear safe-now / safe-later / not-safe-yet classification

### For both lanes

- no architecture cosplay
- no surprise rewrites
- no doctrine bending because something feels exciting

---

## 13. Immediate Team Priorities

### Priority 1

Complete Cross-Branch Consolidation M1 + M2 only.

### Priority 2

Run one full deterministic harness proof including the envelope path if not yet baselined in the same report.

### Priority 3

Validate or finish the isolated Shadow BCI emitter prototype.

### Priority 4

Hold a convergence checkpoint before any passive live hook is authorized.

---

## 14. Compact Motto

**Build the bounded truth object.**  
**Stage the shadow substrate.**  
**Observe before governing.**  
**Adopt live behavior only by explicit decision.**

---

## 15. One-Sentence Team Directive

AIM-OS Prime builds deterministic bounded context for the live machine, Contextual Sync grows around it as a shadow superstrate, and the team must advance both without ever confusing staging, observation, and governance with one another.
