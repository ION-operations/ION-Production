# dAimon UI Canon Product Plan

Status: planning canon for the dAimon product surface
Source authority: `/home/sev/ION - Production/_ui_canon_bundle`

## Canon Sources Read

- `CANON_JOC_UI_ARCHITECTURE.md`
- `JOC_UI_REQUIREMENTS.md`
- `ULTIMATE_OPUS_VISUAL_INTERFACE_CANON.md`
- `OPUS_VISUAL_SETTINGS_CANON.md`
- `OPUS_VISUAL_EDITOR_CANON.md`
- `OPUS_VISUAL_CANON_CONTEXT_PROMPT.md`
- `OPUS1_JOC_UI_DESIGN.md`
- `ui_evolution_plan.md`
- `uishader.txt`

## Product Translation

dAimon is not a memory dashboard and not a generic analytics app. Its UI should
feel like a trust operations console: a dense, matte-black command surface where
the operator can see what AI work entered, what was classified, what was settled,
what receipts exist, what future agents may inherit, and which proof gates remain
blocked.

The core UI principle:

```text
AI output is candidate motion. dAimon UI shows whether that motion becomes
trusted inheritance.
```

## Binding Visual Direction

Use the JOC DXL matte-black instrument-panel standard:

- Deep background: `#0a0a0a`
- Surface: `#0e0e0e`
- Panel: `#111111`
- Border: `#1e1e1e`
- Hover border: `#2a2a2a`
- Active border: `#444444`
- Primary text: `#cccccc`
- Secondary text: `#aaaaaa`
- Hint text: `#555555`
- Labels and badges: monospace, uppercase, compact
- Panel radius: `0-2px`
- SVG icons only; no emoji
- No purple/blue navigation accents
- No generic slider/input settings panels for core trust interactions

The current `dashboard/` can remain the hackathon proof viewer. The next UI
should be a proper desktop console with a denser shell, visible panels, and
graph/instrument interactions.

## Shell Architecture

Adopt a dAimon variant of the JOC five-zone system:

```text
TOP BAR
  product identity, active project lane, carrier status, command palette

LEFT RAIL
  primary mode icons and project/domain switching

MAIN WORKSPACE
  current trust surface: cockpit, settlement, graph, evidence, demo package

RIGHT INSPECTOR / DRAWER
  selected object, receipt, claim, trace, route, carrier, or domain detail

BOTTOM PROOF STREAM
  live event feed, worker telemetry, queue state, proof-gate returns
```

Desktop is primary. Ultrawide should show main workspace and right inspector
side by side. Standard desktop should allow the right inspector to overlay or
collapse. Mobile should become a separate command/monitor surface, not a
compressed version of the full desktop console.

## Top-Level Navigation

Top bar groups:

```text
OPERATIONS
GOVERNANCE
INTELLIGENCE
INFRASTRUCTURE
DEMO
```

Sub-page map:

| Group | Pages |
| --- | --- |
| OPERATIONS | Cockpit, Live Run, Worker Telemetry, Queue |
| GOVERNANCE | Settlement, Receipts, Inheritance, Claims |
| INTELLIGENCE | Domain Graph, Capability Routes, Carrier Handoffs, Context Packages |
| INFRASTRUCTURE | MongoDB, Agent Builder MCP, Google/Gemini, GitHub |
| DEMO | Evidence Package, Video Agent, Submission Checklist, Non-Claims |

## Right Drawer System

The right icon rail should expose inspectable trust objects instead of plain
settings. Each icon opens a full, top, or bottom drawer following the Lucid/JOC
split-position pattern.

Drawer types:

- Object Inspector
- Receipt Inspector
- Settlement Inspector
- MCP Trace Inspector
- Claim Auditor
- Carrier Handoff Inspector
- Domain/Route Inspector
- Artifact Inspector

Each drawer uses sub-tabs when dense:

```text
Receipt Inspector
  [Summary] [Objects] [Proof] [Inheritance] [Non-Claims]

MCP Trace Inspector
  [Query] [Returned] [Excluded] [Citations] [Live Gate]
```

## Bottom Proof Stream

The bottom bar is not decoration. It is the continuity heartbeat:

```text
[worker] run accepted
[receipt] receipt_daimon_live_vertical_slice_20260509_live_seed_001 issued
[mongo] 5 inheritable objects returned
[gemini] candidate response captured; not inheritable
[agent-builder] live MCP trace pending
```

Collapsed state should show counts and status dots. Expanded state should show
time-ordered events, active workers, proof gate returns, and clickable artifact
links.

## Visual Instruments

The UI canon forbids treating complex state as only forms and tables. dAimon's
core objects need visual instruments.

### 1. Settlement Matrix

Purpose: decide candidate state transitions.

Visual model:

```text
candidate objects enter from left
operator drags or clicks objects into:
ACCEPT | REJECT | DEFER | REQUEST PROOF | HUMAN REVIEW
```

Required feedback:

- Authority score meter
- Proof debt indicator
- Receipt impact preview
- Inheritance consequence preview
- Non-inheritable warning if proof is missing

### 2. Receipt Chain Graph

Purpose: show how accepted context becomes inheritable.

Visual model:

```text
source object -> settlement decision -> receipt -> inheritance bundle -> carrier handoff
```

Interaction:

- Select any node to open the right inspector
- Hover edges to show `relies_on`, `settled_by`, `inherits_from`, `validates`
- Color only by trust status, not decorative theme

### 3. Inheritance Filter Instrument

Purpose: show accepted-only retrieval as a visual gate.

Visual model:

```text
all objects -> status gates -> returned bundle
```

The user should see rejected, deferred, proof-debt, and witness-only objects
physically excluded from the returned bundle. This is a dAimon-specific visual
instrument and should replace generic filter dropdowns for demo-critical flows.

### 4. MCP Trace Pipeline

Purpose: prove MongoDB MCP retrieval boundaries.

Visual model:

```text
$match -> $project -> $limit -> returned ids -> receipt citations
```

The pipeline should render the query shape as stages, with object IDs flowing
through. Excluded IDs remain visible as witness but cannot enter the returned
lane.

### 5. Capability Route Graph

Purpose: show generative governance.

Visual model:

```text
objective -> domain -> role -> carrier -> proof obligations -> settlement target
```

Route nodes should expose:

- authority ceiling
- proof obligation set
- side-effect boundary
- human approval requirement
- receipt target

### 6. Claim Audit Board

Purpose: govern the demo and product narrative.

Visual model:

```text
claim -> status -> evidence artifact -> receipt/non-claim boundary
```

Statuses:

- `proven_local`
- `proven_live_mongodb`
- `proven_live_google`
- `pending_live_trace`
- `roadmap`
- `non_claim`

### 7. Domain Cartography Map

Purpose: show governed graph regions and future fission.

Visual model:

```text
domains as bounded graph regions
edges show routes_to, blocks, validates, supersedes, conflicts_with
```

Fission signals should be visual:

- high template density
- noisy context package
- repeated ownership confusion
- heavy neighboring-domain traffic

## Page Plan

### Phase 1: Hackathon Evidence Console

Upgrade the current static dashboard into a denser DXL proof console.

Pages:

- Evidence Cockpit
- Live Vertical Slice
- Claim Audit
- MCP Trace Gate
- Video Package

Deliverables:

- DXL token rewrite
- compact top bar and status strip
- claim matrix and proof stream visible on first viewport
- no oversized hero styling
- no card-inside-card composition

### Phase 2: Governance Console

Build the operator-facing trust workflow.

Pages:

- Settlement Matrix
- Receipt Chain Graph
- Inheritance Filter Instrument
- Object Inspector

Deliverables:

- visual settlement lanes
- receipt graph
- accepted-only gate instrument
- bottom proof stream

### Phase 3: Generative Governance Console

Build the planning and route layer.

Pages:

- Domain Cartography
- Capability Route Graph
- Context Package Builder
- Carrier Handoff Inspector

Deliverables:

- objective-to-domain route graph
- proof obligation editor as visual relationship graph
- carrier capability matrix
- domain fission indicators

### Phase 4: Enterprise Trust Console

Build the audit and collaboration layer.

Pages:

- Audit Ledger
- Project Lanes
- Collaborator Authority
- Adapter Registry
- Deployment Evidence

Deliverables:

- project-bound identity panel
- role/capability sharing
- adapter proof dashboard
- enterprise audit export

## Component System

Suggested structure for the next app shell:

```text
ui/
  shell/
    DaimonTopBar
    DaimonLeftRail
    DaimonRightDrawerRail
    DaimonBottomProofStream
    DaimonWorkspace
  instruments/
    SettlementMatrix
    ReceiptChainGraph
    InheritanceGate
    McpTracePipeline
    CapabilityRouteGraph
    ClaimAuditBoard
    DomainCartographyMap
  inspectors/
    ObjectInspector
    ReceiptInspector
    TraceInspector
    ClaimInspector
    CarrierInspector
  tokens/
    daimon-dxl.css
```

## Design Acceptance Criteria

Before calling the dAimon UI canon-compliant:

- Uses DXL matte-black tokens and compact monospace labels.
- Avoids emoji and uses inline SVG icons.
- Avoids large marketing hero composition for the actual app.
- Shows proof state on the first viewport.
- Makes accepted-only inheritance visible, not merely textual.
- Makes excluded objects visible as non-inheritable witness.
- Shows Gemini output as candidate unless settled.
- Shows Agent Builder MCP trace as pending until a live trace artifact exists.
- Provides right-inspector and bottom-proof-stream patterns.
- Replaces generic controls with visual instruments for trust workflows.
- Passes desktop and mobile/monitor screenshot checks for text overlap.

## Immediate Next Build Slice

The next implementation should not attempt the full product console at once.
Build this narrow slice:

```text
DXL Evidence Cockpit
  -> top bar
  -> compact metrics strip
  -> claim audit board
  -> live vertical-slice phase strip
  -> inheritance gate preview
  -> right receipt inspector
  -> bottom proof stream
```

This turns the current dashboard from a proof page into the first real dAimon
trust-console surface while preserving the honest live proof boundaries.
