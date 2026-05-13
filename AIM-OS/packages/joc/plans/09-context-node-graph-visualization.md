# 09 — Context Node Graph Visualization (Deep Plan)

> **The "git branch for context" dream.**
> A visual timeline + node graph showing how AI context was constructed, routed, and evolved.

---

## What This Is

The user described this as:

> "A context visual system that essentially is like a git branch for context showing the entire node graph and timeline of the context the AI has utilized from our advanced context systems."

This is distinct from the Context Web (plan 02). The Context Web shows knowledge relationships. The **Context Node Graph** shows the *process* — how context was assembled, which sources contributed, where branches diverged, and how context evolved across conversations.

Think: **git log --graph** but for AI context provenance.

---

## Source Architecture

This visualization sits at the intersection of:

1. **TCS (Timeline Context System)** — sequential prompt history, `prompt_id` tracking
2. **CMC (Consciousness Memory Capsules)** — bitemporal memory atoms with validity ranges
3. **HHNI (Hierarchical Holistic Node Indexing)** — multi-level context retrieval
4. **Aether Chat S2** — Context Web construction phase
5. **Aether Chat S3** — LUCID Empire reasoning fork/merge patterns

---

## Visual Design

### Primary View: Context Flow Graph

Horizontal left-to-right timeline with branching:

```
  Conversation 1                    Conversation 2
  ┌─────┐                          ┌─────┐
  │ P-1 │──→ [CMC-a, CMC-b] ──→ │ P-5 │
  │     │      ↓                   │     │
  │ P-2 │──→ [CMC-c] ──────────→ │ P-6 │──→ [CMC-g] (new insight)
  │     │      ↓        ↘         │     │       ↓
  │ P-3 │──→ [CMC-d]    [KI-1] → │ P-7 │──→ [CMC-h] (merged)
  │     │      ↓                   │     │
  │ P-4 │──→ [CMC-e, CMC-f]      │ P-8 │
  └─────┘                          └─────┘
```

**Node Types:**
| Type | Shape | Color | Meaning |
|------|-------|-------|---------|
| Prompt | Square | Blue | User prompt in conversation |
| CMC Atom | Circle | Cyan | Memory atom retrieved or created |
| KI (Knowledge Item) | Diamond | Gold | Distilled knowledge item |
| HHNI Retrieval | Hexagon | Green | Context chunk from hierarchical index |
| SEG Entity | Triangle | Purple | Entity from Shared Evidence Graph |
| Branch Point | Star | Red | Context divergence (fork) |
| Merge Point | Star (filled) | Orange | Context convergence (merge) |

**Edge Types:**
| Type | Style | Color | Meaning |
|------|-------|-------|---------|
| Retrieved | Solid | Blue | Atom was retrieved into context |
| Created | Dashed | Green | Atom was created as result |
| Evolved | Gradient | Cyan→Green | Atom was updated/refined |
| Branched | Fork line | Red | Context split into parallel paths |
| Merged | Converging lines | Orange | Multiple contexts combined |
| Invalidated | Strikethrough | Gray | Context superseded or contradicted |

### Secondary View: Timeline Ruler

Horizontal timeline at the bottom showing:
- Conversation boundaries (labeled segments)
- Prompt sequence numbers
- Time axis (relative or absolute)
- Scrubber control — drag to see graph state at any point in time

### Tertiary View: Impact Heatmap

Overlay showing which context atoms had the highest influence on final outputs:
- Color intensity = influence score (0-1)
- Hover → shows which prompts used this atom
- Click → navigates to the source conversation

---

## Interactions

| Interaction | Behavior |
|------------|----------|
| Click node | Shows detail panel: atom content, creation time, validity range, confidence, source |
| Click edge | Shows relationship type, strength, evidence chain |
| Drag timeline | Animates graph evolution over time |
| Select 2 nodes | Shows path between them (provenance chain) |
| Right-click node | Options: inspect, trace origin, find descendants, find contradictions |
| Search box | Highlights nodes matching semantic query (HHNI search) |
| Filter sidebar | Toggle node/edge types, filter by conversation, by confidence threshold |

---

## Data Sources

| Feature | MCP Tool | Data Shape |
|---------|----------|-----------|
| Prompt history | `get_timeline_entries` | `{prompt_id, user_input, context_state, timestamp}` |
| Memory atoms | `retrieve_memory` | `{content, tags, created_at, confidence}` |
| Timeline graph | `get_timeline_summary` | Sequential entries with prompt IDs |
| HHNI context | `get_hhni_status` | Index node information |
| Knowledge synthesis | `synthesize_knowledge` | Synthesized knowledge from topics |
| Evidence chain | `track_confidence` | VIF records with provenance |

---

## Implementation Phases

### Phase 1: Linear Timeline
- Horizontal timeline of prompts from TCS
- Each prompt shows as a node with expandable detail
- Connected by sequential edges
- Conversation boundaries as labeled segments

### Phase 2: Context Atoms Layer
- Add CMC atom nodes retrieved per prompt
- Edges from prompts to their retrieved atoms
- Edges from prompts to newly created atoms
- Color-coding by atom type

### Phase 3: Branching & Merging
- Detect when the same atom appears in multiple conversations (branch)
- Detect when multiple atoms converge into a synthesis (merge)
- Render branch/merge visual as git-style fork lines

### Phase 4: Interactive Graph
- Full zoom/pan/drag interaction
- Node selection and detail panel
- Path highlighting between selected nodes
- Timeline scrubber for temporal navigation
- Search and filter controls

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 🕐 | Timeline | Conversation list with date ranges |
| 🔍 | Search | Semantic search across context atoms |
| 🎯 | Impact | Impact heatmap controls and legend |
| 🔀 | Branches | List of detected branch/merge points |
| 📊 | Stats | Context graph statistics (total nodes, edges, avg depth) |
