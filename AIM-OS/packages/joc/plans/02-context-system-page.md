# 02 — Context System Page (Deep Plan)

> **The most architecturally complex page in JOC.**  
> This plan is grounded in 6 major documents spanning 5,000+ lines.

---

## What This Page Actually Represents

The Aether/Codex context system is NOT a simple "context graph." It is a multi-layered context management architecture with:

1. **An 8-stage orchestration pipeline (S0-S8)** that processes every AI interaction
2. **A 5-layer recursive meta-cognition system (LUCID Empire)** for reasoning about reasoning
3. **A deterministic Rust-based context mapper** (Sovereign Context Mapper) for token-efficient envelopes
4. **A bitemporal memory system** with consciousness state persistence
5. **Context Mesh Maps** — executable contracts governing cross-dependencies
6. **A Context Web visualization** — force-directed graph of conversation knowledge

---

## Source Documents

| Document | Lines | Key Content |
|----------|-------|-------------|
| AETHER_CHAT_COMPLETE_SYSTEM_MAP.md | 1,741 | S0-S8 pipeline, multi-LLM routing, Context Web spec |
| AETHER_CHAT_DEEP_TECHNICAL_ANALYSIS.md | 1,076 | LUCID Empire, κ-gating, multi-agent orchestration |
| AETHER_CHAT_UNIFIED_IMPLEMENTATION_PLAN.md | 766 | 24-week 6-phase roadmap |
| SOVEREIGN_CONTEXT_MAPPER_BUILD_PLAN.md | 529 | Rust deterministic parsing, Active Context Envelopes |
| Aether Memory System L2 | 536 | Bitemporal atoms, consciousness state, indexes |
| context_mesh_maps.py | 657 | NetworkX dependency graphs, constraint contracts |

---

## Page Architecture

### Primary View: Pipeline Monitor

A real-time view of the S0-S8 pipeline showing context flow for the most recent or selected query:

```
┌─────────────────────────────────────────────────────────────┐
│  S0: Ingest → S1: Pre-Process → S2: Context Web Build →    │
│  S3: Thinking (LUCID) → S4: κ-Gate → S5: Post-Process →    │
│  S6: UX Polish → S7: Memory → S8: Follow-ups               │
└─────────────────────────────────────────────────────────────┘
```

Each stage shows:
- **Status** (idle / active / complete / error)
- **AIM-OS systems engaged** (e.g., S1 uses HHNI, CMC, VIF, CAS, SCOR, APOE)
- **Processing metrics** (tokens processed, context atoms retrieved, confidence κ-score)
- **Expandable detail** — click any stage to see the actual data flowing through it

### Secondary View: Context Web (Force-Directed Graph)

The actual Context Web visualization spec from Aether Chat S2/S6:

**Nodes** = `ContextNode` objects built from HHNI + CMC results:
- Properties: `id`, `label`, `type`, `relevance` (0-1), `recency`, `size`, `color`, `glow`
- Types: `topic`, `entity`, `concept`, `decision`, `evidence`, `contradiction`
- Visual: size = relevance, glow = recency, color = type category

**Edges** = SEG-discovered relationships:
- Types: `builds_on`, `contradicts`, `complements`, `evolves_from`, `references`
- Properties: `strength` (0-1), `evidence_count`, `confidence`
- Visual: thickness = strength, color = type, dashed = low confidence

**Interactions**:
- **Semantic search** — type a query, highlight matching nodes
- **Timeline view** — slider to see graph evolution over time
- **Causation chain** — select a node, see what led to it (via SEG provenance)
- **Find commonality** — select 2+ nodes, highlight shared ancestors

**Physics**: Force-directed layout (not static SVG positions):
- Attractive force between connected nodes (proportional to edge strength)
- Repulsive force between all nodes (prevent overlap)
- Gravity toward center (prevent drift)
- User can drag nodes, pin nodes, zoom/pan

### Tertiary View: LUCID Empire Reasoning Traces

Visualization of the 5-layer recursive meta-cognition:

1. **Layer 1: Thought Articulation** — the explicit reasoning chain
2. **Layer 2: Reasoning Reflection** — reflecting on the reasoning
3. **Layer 3: Pattern Identification** — recurring assumptions, blind spots
4. **Layer 4: Temporal Lucidity** — reasoning evolution over time (via TCS)
5. **Layer 5: Infinite Lucidity** — CAS introspection depth (≤5)

Display as nested collapsible layers, each showing:
- The reasoning text (from CMC atoms)
- Confidence κ-score (from VIF)
- Evidence chain (from SEG)
- Whether it triggered a gate action (PROCEED / SPECULATE_WITH_WARNING / ABSTAIN_AND_CLARIFY)

### Quaternary View: Active Context Envelopes

Display of Sovereign Context Mapper output:
- **Target file** — full implementation (highlighted)
- **Dependency contracts** — public API surface only (read-only badge)
- **Parse confidence** — High / Degraded / Fallback with reasoning
- **Symbol usage** — which imported symbols are actually referenced
- **Truncation tier** — what was kept vs. dropped and why

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 🔍 | Context Search | Semantic search across all context atoms (HHNI) |
| 📊 | Pipeline Status | Compact S0-S8 stage indicators |
| 🧠 | Memory Browser | Browse bitemporal memory atoms (CMC) |
| ⚖️ | Confidence | VIF κ-score dashboard, confidence calibration |
| 🔗 | Evidence | SEG evidence chain browser |
| 📐 | Envelopes | Active Context Envelope inspector |

---

## Data Sources (MCP Integration)

| Feature | MCP Tool | Fallback |
|---------|----------|----------|
| Memory atoms | `retrieve_memory` | Mock bitemporal atoms |
| Timeline | `get_timeline_summary` | Mock timeline entries |
| Confidence | `track_confidence` | Static κ-scores |
| Evidence | `synthesize_knowledge` | Mock SEG graph |
| Context search | `deepsearch` | Client-side filter |
| HHNI status | `get_hhni_status` | "Disconnected" state |

---

## Implementation Phases

### Phase 1: Pipeline Monitor (Visual Only)
- Render S0-S8 stages as interactive horizontalflow
- Each stage shows name, status indicator, engaged AIM-OS systems
- Click stage → expandable detail panel
- Data: hardcoded pipeline structure, real status via MCP if available

### Phase 2: Context Web (Force-Directed Graph)
- Replace static SVG with physics-based force-directed layout
- Use `d3-force` or `@antv/g6` for graph rendering
- Node types with distinct colors and sizes
- Edge types with distinct styles
- Zoom, pan, drag, pin interactions
- Data: MCP `retrieve_memory` + `synthesize_knowledge` → node/edge construction

### Phase 3: LUCID Empire Traces
- Nested collapsible layer visualization
- CMC atom display per layer
- VIF κ-score badges
- SEG evidence chain links
- Gate action indicators

### Phase 4: Active Context Envelopes
- Envelope inspector panel
- Target file vs. contract differentiation
- Parse confidence indicators
- Symbol usage highlighting

---

## What NOT to Do

- ❌ Do NOT use static SVG with hardcoded positions
- ❌ Do NOT show fake nodes that don't correspond to real CMC atoms
- ❌ Do NOT label things "HHNI" or "VIF" without actually connecting to those systems
- ❌ Do NOT simplify the pipeline to fewer than 8 stages (S0-S8 is the canonical architecture)
- ❌ Do NOT skip the evidence chain — every node must be traceable to its CMC source
