# ION JOC / UI Canon Intake and Developer Cockpit Evolution Plan

Created: 2026-05-12  
Carrier: ION-through-this-ChatGPT-carrier  
Posture: **CLEAN for sandbox file evidence; CONSERVATIVE for project-state conclusions**  
Authority: **planning / review only**. No accepted-state claim, no production claim, no live connector claim, no repo mutation claim.

---

## 1. Executive diagnosis

The UI problem is not primarily missing components. ION already contains many useful UI surfaces, plans, view models, and candidate panels. The core failure pattern is:

```text
rich panels + weak shell law = vertical dashboard / monolithic board
```

The correct JOC direction is:

```text
governed shell zones
+ one active work surface
+ page-local left drawers
+ universal right inspector
+ bottom temporal proof stream
+ visible context/route/memory/proof
+ DXL matte-black instrument-panel craft
```

The evolved target should be an **ION Developer Cockpit**: a JOC-grade operations surface where a vibe architect can see live work, context routes, queue packets, Codex sessions, branch capsules, receipts, graph domains, carriers, gates, and proof without being forced into raw internal chores.

The best near-term route is **not** another broad UI build. It is a proof-and-settlement pass over the active cockpit route, followed by a graph/cognitive-explorer model layer and then a carefully staged implementation.

---

## 2. Evidence inspected

### UI canon bundle

Inspected `_ui_canon_bundle` files including:

```text
CANON_JOC_UI_ARCHITECTURE.md
JOC_UI_REQUIREMENTS.md
OPUS1_JOC_MASTER_VISION.md
OPUS1_JOC_COMPUTE_AND_IDE_LAYOUT.md
OPUS1_JOC_UI_DESIGN.md
OPUS1_JOC_GOALS_AND_ROADMAP.md
OPUS_VISUAL_EDITOR_ARCHITECTURE.md
OPUS_VISUAL_SETTINGS_CANON.md
ULTIMATE_OPUS_VISUAL_INTERFACE_CANON.md
ui_evolution_plan.md
uishader.txt
```

Key canon result:

```text
JOC is not a browser, not an IDE clone, not an app launcher, and not a monolithic dashboard.
JOC is a maintained operational command surface / central nervous system.
```

Binding shell direction:

```text
TOP_BAR
LEFT_ICON_RAIL
LEFT_DRAWER
MAIN_WORK_SURFACE
RIGHT_INSPECTOR
RIGHT_ICON_RAIL
BOTTOM_TIMELINE
```

Binding visual direction:

```text
DXL matte-black instrument panel
dense but legible
inline SVG icons
no emoji-as-icons
no casual purple/blue/Material defaults
no generic card-board dashboard
no unproved “done” claim without visual proof
```

### ION current UI/JOC evidence

Inspected current ION snapshot paths including:

```text
ION/02_architecture/ION_JOC_COCKPIT_SHELL_COMPONENT_CONTRACT_PROTOCOL.md
ION/02_architecture/ION_JOC_COGNITIVE_EXPLORER_AND_CONTEXT_ROUTE_VIEW_MODEL_PROTOCOL.md
ION/02_architecture/SYSTEM_CARD_AND_DOMAIN_MAP_PROTOCOL.md
ION/00_BOOTSTRAP/V56_ION_JOC_COCKPIT_SHELL_COMPONENT_CONTRACTS_LOCK.md
ION/00_BOOTSTRAP/V58_COGNITIVE_EXPLORER_AND_CONTEXT_ROUTE_VIEW_MODEL_LOCK.md
ION/05_context/current/ai_assistant_work/analysis/UI_FRONTEND_CANON_SYNTHESIS_REPORT_20260509T025441Z.md
ION/05_context/current/ai_assistant_work/protocols/UI_FRONTEND_EXCELLENCE_DOMAIN_PROTOCOL_V0_1.md
ION/05_context/current/ai_assistant_work/next/HELIXION_JOC_WORK_SURFACE_UI_PACKET_20260511.json
ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_REBUILD_CURRENT_PLAN.json
ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_ROUTE_RECOVERY_RECEIPT_20260511.json
ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_RECOVERY_002_EXISTING_COCKPIT_TOP_PAGES_RECEIPT_20260511.json
ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_RECOVERY_003_ANCHORED_PAGES_AND_DRAWER_CANON_RECEIPT_20260511.json
ION/05_context/current/codex_cli/CODEX_CHAT_UI_RECOVERY_ORCHESTRATION_20260507.md
ION/05_context/current/codex_cli/CODEX_CLI_CARRIER_AND_COCKPIT_PASS_20260507.md
ION/05_context/current/codex_cli/CODEX_CHAT_JOC_CONTEXT_VISUALIZATION_ORCHESTRATION_20260508.md
ION/08_ui/joc_cockpit_shell/
ION/04_packages/kernel/ion_codex_chat_*ui.py
ION/04_packages/kernel/ion_codex_chat_memory_visualization*.py
```

### AIM-ION lineage

Inspected selected AIM-ION/JOC lineage:

```text
packages/joc/plans/01-architecture-and-layout.md
packages/joc/plans/09-context-node-graph-visualization.md
packages/joc/plans/10-left-drawer-system.md
packages/joc/plans/12-design-system.md
packages/joc/src/components/layout/LeftDrawerSystem.tsx
packages/joc/src/components/layout/AssistantRail.tsx
packages/joc/src/pages/ContextGraphPage.tsx
packages/joc/src/pages/IntelligenceMapPage.tsx
docs/Aether-OS/design/ui_evolution_plan.md
docs/Aether-OS/design/victus_architecture.md
docs/Aether-OS/design/aether_victus_synthesis.md
```

Important lineage result:

```text
AIM-ION contributes strong interaction architecture:
- page-local drawer registry
- context node graph
- context as git-branch-like provenance
- visible AI cognition/trust/state
- IDE-grade command surface patterns

But AIM-ION visual style is not current ION law where it conflicts with DXL/JOC canon.
For example, older emoji/colorful/glass patterns should be translated, not copied.
```

### dAimon lineage

Inspected selected dAimon evidence:

```text
dAimon/docs/ui_canon_product_plan.md
dAimon/docs/architecture.md
dAimon/orchestration/ui_surface_plan.json
dAimon/capability_graph/capability_graph_seed.json
dAimon/capability_graph/domain_agent_registry_seed.json
dAimon/dashboard/index.html
dAimon/dashboard/styles.css
```

Important dAimon result:

```text
dAimon contributes the governance/product-trust instrument layer:
- settlement matrix
- receipt chain graph
- inheritance filter
- MCP trace pipeline
- capability route graph
- claim audit board
- domain cartography map
```

### Graph/domain-map visual concept

Inspected the graph concept image in current diffs:

```text
diffs/ChatGPT Image May 10, 2026, 12_14_44 PM.png
```

This is a strong product direction: a living domain map with domain districts, process routes, carriers, receipts, risk overlays, selected-node inspector, and bottom timeline. It should be treated as **candidate visual reference**, not accepted UI state.

---

## 3. Current UI state assessment

### Two front-door paths exist

#### 1. Active/current 8765 Python cockpit route

Important files:

```text
ION/04_packages/kernel/ion_codex_chat_shell_ui.py
ION/04_packages/kernel/ion_codex_chat_main_ui.py
ION/04_packages/kernel/ion_codex_chat_left_drawer_ui.py
ION/04_packages/kernel/ion_codex_chat_right_inspector_ui.py
ION/04_packages/kernel/ion_codex_chat_timeline_ui.py
ION/04_packages/kernel/ion_codex_chat_memory_visualization.py
ION/04_packages/kernel/ion_codex_chat_memory_visualization_ui.py
ION/04_packages/kernel/ion_codex_chat_assets_ui.py
ION/04_packages/kernel/ion_dual_codex_chat.py
```

Positive evidence:

```text
- top tabs exist: Chat, JOC, Queue, Codex, Extension, Docs, Projects, WisdomNET, Gates, Receipts, Settings
- left rail/drawer controls exist
- right inspector controls exist
- bottom timeline/filter row exists
- page surfaces exist with anchored page-scroll body and page-anchor bar concepts
- memory/context visualization model exists
```

Risk evidence:

```text
- C-087 / C-088 recovery receipts are candidate and explicitly not visually proved.
- Some main pages are still shallow focused pages/cards rather than full instruments.
- Dual Codex chat tests currently fail in the extracted snapshot.
- The running local service may not reflect latest code without reload.
```

#### 2. React/Vite 8788 JOC shell candidate

Important path:

```text
ION/08_ui/joc_cockpit_shell/
```

Positive evidence:

```text
- React/Vite shell exists.
- It has top nav, left rail, main workspace, right inspector, bottom timeline.
- It has many useful panels:
  QueueGatewayCockpitPanel,
  CodexCapsuleChatWorkbenchPanel,
  ExtensionMicroShellPanel,
  DocsProjectsPackagesPanel,
  Gates/Receipts/runtime panels, etc.
- Its CSS is closer to DXL matte-black than older AIM color language.
```

Risk evidence:

```text
- Current ION corrective docs classify the React route/panels as candidate inventory, not settled app architecture.
- Prior Codex CLI UI work drifted into a large vertical panel board.
- 8788 and 8765 split can confuse operators unless one is explicitly chosen as active front door.
```

### Recommendation on front door

Near term:

```text
8765 / existing cockpit route = active proof surface
8788 React shell = component inventory / future migration candidate
```

Do not promote the React shell as the main app until the seven-zone shell contract, visual proof, and route settlement pass are complete.

---

## 4. Validation performed in sandbox

These commands were run against the extracted snapshot only.

### Python UI model/local cockpit tests

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=ION/04_packages \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q \
  ION/tests/test_kernel_ion_cockpit_view_model.py \
  ION/tests/test_kernel_ion_local_cockpit_app.py
```

Result:

```text
10 passed
```

There was unrelated artifact-tool spreadsheet warmup noise on stderr, but pytest exited successfully.

### Dual Codex chat / active cockpit integration tests

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=ION/04_packages \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q ION/tests/test_kernel_ion_dual_codex_chat.py
```

Result:

```text
10 passed
7 failed
```

Failure themes:

```text
- Codex Solo context was blocked where a test expected ready.
- HTML route expectation still looked for older data-page-target="context".
- Queueing/general turn tests returned false.
- Task-return hydration tests found no hydrated returns.
- Runner-start refusal and HOT_CONTEXT queue-carry tests failed.
```

Interpretation:

```text
The active cockpit route has useful implemented shell pieces, but it is not cleanly settled/proved.
Do not claim the 8765 UI is accepted or fully correct yet.
```

### React/Vite shell build

Initial `npm run build` failed in the extracted zip because `node_modules/.bin/vite` was restored as a plain text shim without executable/symlink semantics.

After adding executable bit in scratch and invoking Vite directly:

```bash
node node_modules/vite/bin/vite.js build
```

Result:

```text
Vite build succeeded.
67 modules transformed.
dist/index.html
dist/assets/index-*.css
dist/assets/index-*.js
```

Interpretation:

```text
The React shell source can build in this sandbox after bypassing an archive/node_modules permission issue.
This does not settle product route or visual quality.
```

---

## 5. Failure map to prevent recurrence

### Failure A — Monolithic vertical dashboard

Bad pattern:

```text
Add panel, add panel, add panel, scroll forever.
```

Correct pattern:

```text
Every new surface must be assigned to:
- top-level page
- page-local left drawer
- universal right inspector lens
- bottom timeline lane/event
- modal/gated command palette
```

### Failure B — Theme mistaken for architecture

Bad pattern:

```text
Dark CSS + cards = JOC.
```

Correct pattern:

```text
JOC = governed operational architecture + DXL visual craft.
```

### Failure C — Split front doors

Bad pattern:

```text
8765 says one thing, 8788 says another, operator cannot tell which is real.
```

Correct pattern:

```text
one active route
one candidate route
explicit proof status on both
```

### Failure D — Internal chores as primary UX

Bad pattern:

```text
User operates lanes, queues, pins, context packages, capsule internals, and raw packet knobs as main workflow.
```

Correct pattern:

```text
User asks/commands.
ION shows route, proof, context, receipts, gates, and next actions.
Internal machinery is translated into visible state and approvals.
```

### Failure E — Chat identity confusion

Bad pattern:

```text
"Chat with Capsule" / Capsule personified as assistant.
```

Correct pattern:

```text
ION Codex Chat:
User talks to Codex/ION carrier.
Capsule/Mini/HOT/context packages are visible behind-the-scenes context strata.
```

### Failure F — Visual graph without proof semantics

Bad pattern:

```text
Beautiful node graph that is decorative and not tied to receipts/routes/status.
```

Correct pattern:

```text
Graph node = typed system/domain/process/context object.
Edge = typed relationship with evidence/proof path.
Timeline = state changes and receipts.
Inspector = selected-node facts, risks, actions, and non-claims.
```

### Failure G — Hidden or overclaimed authority

Bad pattern:

```text
UI shows production/live/browser/service authority without proof.
```

Correct pattern:

```text
Every capability has status:
available / gated / blocked / candidate / accepted / unknown.
No tool visibility becomes permission.
```

---

## 6. Evolved product vision: ION Developer Cockpit

### Product sentence

```text
ION Developer Cockpit is a JOC-grade operating surface for vibe architects: a living graph, chat-command, context-proof, worker-queue, receipt-settlement, and runtime-inspection cockpit for advanced AI-built systems.
```

### Main surfaces

#### A. JOC Home / Living Operational Graph

The home page should become the “see everything” surface.

Graph metaphor:

```text
domain districts
  → systems/buildings
    → modules/rooms
      → packets/tasks/receipts as live objects
```

Overlay layers:

```text
Domains
Templates
Carriers
Agents
Queues
Processes
Receipts
Settlements
Context routes
MCP/tools/connectors
SLA/health
Risk zones
Capacity
Lineage
```

Selected-node inspector:

```text
overview
route/proof
linked files
tests
receipts
risks
workers
timeline
next lawful actions
```

Bottom timeline:

```text
carrier events
queue events
Codex session events
Action/MCP events
patch events
validation events
receipt events
settlement gates
operator corrections
```

#### B. Chat / Command Workbench

The Chat page remains a first-class page, not a side widget.

Rules:

```text
one primary composer
one primary send action
execution posture shown as mode/gate, not competing primary buttons
right inspector shows context/route/proof for selected turn
bottom timeline shows model calls, context loads, queue events, receipts
```

#### C. Cognitive Explorer / Context Route Page

Purpose:

```text
show what the AI read, why it read it, what was selected, what was omitted, and what proof exists before model dispatch.
```

Surfaces:

```text
infinite context command palette
selected context lens
structural blueprint
dependency web
source line citation rail
route reasoning panel
context injection preview
```

Memory strata:

```text
LIVE_INPUT
ACTIVE_CRUCIBLE
ACTIVE_CONTEXT
HOT_CONTEXT
X_RAY_DAG
MINI_LOOKUP
LONG_HORIZON
COLD_EVIDENCE
OMITTED_OR_BLOCKED
```

#### D. Queue / Workers / Agents

Purpose:

```text
make B00-style queue contamination impossible to miss.
```

Surfaces:

```text
active unsuperseded work
historical duplicate groups
canonical packet
superseded duplicates
proof-blocked returns
worker branch capsules
Codex sessions
idempotency ledger
blocked/running/accepted/superseded counts
```

Important improvement:

```text
separate historical duplicate groups from active unsuperseded duplicates.
```

#### E. Receipts / Settlement

Purpose:

```text
show candidate → proved → reviewed → accepted/rejected/deferred inheritance.
```

Surfaces:

```text
receipt chain graph
settlement matrix
candidate work list
proof gaps
non-claims
open blockers
acceptance authority
```

#### F. Docs / Projects / Packages

Purpose:

```text
make source/context packages navigable without becoming a generic file browser.
```

Surfaces:

```text
project cards
latest package status
mounted context package
source freshness
diff/workpacket registry
upload/drop/zip status
favorite roots
```

#### G. Extension / DOM / Page Companion

Purpose:

```text
make browser extension/page-perception work inspectable and gated.
```

Surfaces:

```text
selected DOM evidence
geometry/anchor evidence
target capture preview
drop zones
operator approval gate
connector status
blocked capabilities
```

#### H. WisdomNET / dAimon / ATLAS / Lineage

Purpose:

```text
show external packs and lineage without letting them override ION law.
```

Surfaces:

```text
candidate packs
trusted packs
lineage maps
capability graph
domain-agent registry
integration status
evidence tiers
```

---

## 7. Core data contracts to build before more UI panels

New UI implementation should start with view models, not visuals.

### Cockpit shell

```yaml
CockpitShellViewModel:
  active_page_id:
  top_bar:
    identity:
    route_status:
    model_status:
    service_status:
    proof_status:
  left_rail:
    items: []
  left_drawer:
    active_drawer_id:
    tabs: []
    panels: []
  main_work_surface:
    active_page:
    pages: []
  right_inspector:
    active_lens_id:
    lenses: []
  right_rail:
    items: []
  bottom_timeline:
    lanes: []
    events: []
```

### Living operational graph

```yaml
LivingOperationalGraph:
  graph_id:
  generated_at:
  state_claim:
  nodes:
    - id:
      type: domain | system | agent | carrier | queue_packet | receipt | context_segment | connector | project | package | risk | gate
      label:
      status:
      authority:
      proof_status:
      source_refs: []
      receipt_refs: []
      position:
      metrics:
  edges:
    - id:
      type: depends_on | routes_to | produced | validated_by | superseded_by | blocked_by | inherits_from | reads | writes
      source:
      target:
      evidence_refs: []
      confidence:
      accepted_state: false
  layers:
    - id:
      label:
      enabled:
  selected_node:
    id:
    inspector_lenses: []
```

### Context route visualization

```yaml
ContextRouteViewModel:
  selected_turn_id:
  route_candidates: []
  selected_nodes: []
  selected_files: []
  source_line_citations: []
  dependency_edges: []
  memory_segments: []
  omitted_or_blocked_refs: []
  token_budget:
  route_reasoning_public_summary:
  injection_preview:
  forbidden_claims_preserved:
```

### Queue/worker model

```yaml
QueueCockpitViewModel:
  active_unsuperseded_groups: []
  historical_duplicate_groups: []
  canonical_packets: []
  superseded_packets: []
  proof_blocked_returns: []
  accepted_returns: []
  idempotency_ledger:
  worker_branches: []
  codex_sessions: []
  blocked_actions: []
  receipts: []
```

---

## 8. Implementation route

### Phase 0 — UI route proof and settlement

Packet:

```text
PCKT-ION-JOC-UI-ROUTE-PROOF-001
```

Objective:

```text
Prove what the active cockpit currently renders and decide whether C-087/C-088 recovery should be accepted, patched, or quarantined.
```

Do not add broad new features in this phase.

Required proof:

```text
- identify active local route: 8765, 8788, or both
- confirm service reload state if applicable
- run Python cockpit tests
- run dual Codex chat tests
- run React build if React route is being considered
- capture browser screenshots of:
  - Chat page
  - JOC page
  - Queue page
  - right inspector lens switching
  - left drawer switching
  - bottom timeline
- check no-monolith constraints
- check DXL constraints
- report exact gaps
```

Acceptance result should be one of:

```text
ACCEPT_8765_AS_ACTIVE_CANDIDATE_FRONT_DOOR
PATCH_8765_BEFORE_ACCEPTANCE
QUARANTINE_8765_AND_PROMOTE_REACT_ROUTE_TO_PROOF
DUAL_ROUTE_BLOCKED_UNTIL_FRONT_DOOR_DECISION
```

### Phase 1 — Shell contract hardening

Packet:

```text
PCKT-ION-JOC-SHELL-CONTRACT-HARDEN-001
```

Objective:

```text
Make the shell law testable.
```

Tests should assert:

```text
- exactly one active main page
- top bar fixed
- left rail fixed
- left drawer page-local and functional
- right inspector universal and lens-switched
- bottom timeline anchored
- main page scrolls internally
- no browser-body vertical monolith
- no raw internal chores as primary buttons
- no hidden proof/status claims
```

### Phase 2 — Living Operational Graph view model

Packet:

```text
PCKT-ION-LIVING-OPERATIONAL-GRAPH-MODEL-001
```

Objective:

```text
Create a deterministic graph model from existing ION evidence before building the graph UI.
```

Inputs:

```text
system cards
domain maps
capability graph
queue packets
receipts
diff/workpacket registries
branch capsules
Codex sessions
connector/tool policy
service health
```

Output:

```text
a typed graph fixture + tests
```

No live mutation.

### Phase 3 — Graph UI page

Packet:

```text
PCKT-ION-JOC-LIVING-GRAPH-PAGE-001
```

Objective:

```text
Render the graph/domain map as a JOC page with layers, selected-node inspector, and bottom timeline integration.
```

Design law:

```text
the graph is not decoration;
every node and edge must carry evidence/proof/state.
```

### Phase 4 — Context / Cognitive Explorer

Packet:

```text
PCKT-ION-COGNITIVE-EXPLORER-UI-001
```

Objective:

```text
Make context routing visible before model dispatch.
```

Build:

```text
context command palette
selected route preview
source line rail
dependency web
memory strata
omitted/blocked context lane
injection preview
```

### Phase 5 — Queue / Codex session / branch capsule cockpit

Packet:

```text
PCKT-ION-CODEX-WORKER-COCKPIT-001
```

Objective:

```text
Expose workers, queues, B00-style duplicate states, Codex sessions, branch capsules, and receipts.
```

Must show:

```text
active unsuperseded vs historical duplicate groups
canonical packet
proof-blocked returns
Codex session id
branch capsule sync status
last validation
settlement target
```

### Phase 6 — Visual proof harness

Packet:

```text
PCKT-ION-JOC-VISUAL-PROOF-HARNESS-001
```

Objective:

```text
Stop “looks done” claims by requiring screenshot/browser checks.
```

Harness should produce:

```text
screenshot receipts
shell-zone assertions
DOM structure assertions
no-monolith regression
no-forbidden-color/icon scan
interaction smoke checks
visual proof summary
```

---

## 9. Visual craft direction

### Material language

```text
matte black
subtle bevels
thin recessed borders
micro highlights
compact labels
dense instrumentation
clear state colors
one coherent light source
no large generic shadows
no casual soft SaaS gradients
no cartoon glass
```

### Graph visual language

Use semantic layer colors only where data demands it:

```text
health/status
risk
authority
selected path
blocked/omitted
accepted/proved/candidate
```

Avoid arbitrary purple/blue accenting.

### Controls

```text
SVG currentColor icons
rectilinear/tactile controls
clear focus states
button labels as actions, not slogans
mode chips as status, not decoration
```

### Motion

```text
short, functional transitions
drawer slide
graph focus zoom
timeline scrub
receipt chain reveal
no decorative animation that obscures state
```

---

## 10. Proposed next Codex prompt

Use this after B00 settlement/review is stable, or in a separate read-only UI steward session.

```text
You are codex_ui_joc_opus_canonist.

Active packet:
PCKT-ION-JOC-UI-ROUTE-PROOF-001

Authority:
- local read allowed
- tests allowed
- screenshot/browser validation allowed if local services are available
- no implementation changes unless explicitly approved after audit
- no production deploy
- no git push
- no accepted-state claim
- no queue workers
- no Action/MCP mutation
- no branch-capsule consolidation

Task:
Perform a UI/JOC route proof pass.

Required reads:
- _ui_canon_bundle/CANON_JOC_UI_ARCHITECTURE.md
- _ui_canon_bundle/JOC_UI_REQUIREMENTS.md
- _ui_canon_bundle/OPUS1_JOC_MASTER_VISION.md
- _ui_canon_bundle/OPUS1_JOC_COMPUTE_AND_IDE_LAYOUT.md
- _ui_canon_bundle/ui_evolution_plan.md
- ION/05_context/current/ai_assistant_work/analysis/UI_FRONTEND_CANON_SYNTHESIS_REPORT_20260509T025441Z.md
- ION/05_context/current/ai_assistant_work/next/HELIXION_JOC_WORK_SURFACE_UI_PACKET_20260511.json
- ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_REBUILD_CURRENT_PLAN.json
- ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_RECOVERY_002_EXISTING_COCKPIT_TOP_PAGES_RECEIPT_20260511.json
- ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_RECOVERY_003_ANCHORED_PAGES_AND_DRAWER_CANON_RECEIPT_20260511.json
- ION/04_packages/kernel/ion_codex_chat_shell_ui.py
- ION/04_packages/kernel/ion_codex_chat_assets_ui.py
- ION/08_ui/joc_cockpit_shell/

Report:
1. Which route is active and which route is candidate.
2. Whether C-087/C-088 are visible in the running cockpit.
3. Whether the seven shell zones are present.
4. Whether only one main page is active at a time.
5. Whether top/bottom bars are anchored.
6. Whether left drawers and right inspector lenses work.
7. Whether the UI still behaves like a vertical monolith.
8. Whether visual canon violations remain.
9. Which tests pass/fail.
10. Which screenshots were captured.
11. Exact patch recommendation, if any.

Output:
### UI MOUNT PROOF
### CANON READS
### ACTIVE ROUTE FINDINGS
### 8765 COCKPIT FINDINGS
### 8788 REACT SHELL FINDINGS
### TESTS
### SCREENSHOT PROOF
### MONOLITH / JOC CANON SCORECARD
### RECOMMENDATION
### NON-CLAIMS
```

---

## 11. Bottom-line recommendation

1. **Do not build more panels yet.**  
   First prove and settle the active UI route.

2. **Treat 8765 as active and 8788 as candidate inventory unless proof says otherwise.**

3. **Make the living operational graph the eventual JOC home page**, but build its typed view model before the visual graph.

4. **Use AIM-ION/dAimon as lineage and interaction evidence**, not as direct visual law when they conflict with current DXL/JOC canon.

5. **Make visual proof mandatory.**  
   No future UI “done” claim without browser screenshots, shell-zone assertions, and no-monolith regression.

6. **The true next-age developer cockpit is not a chat app and not a dashboard.**  
   It is a proof-bearing command surface where the operator can see the system think, route, act, validate, block, receipt, and evolve — without confusing candidate output for accepted state.
