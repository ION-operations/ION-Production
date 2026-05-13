# 03 — Project Hub Page (Deep Plan)

> **All projects, organized.** Version branches, relationships, app/doc/hybrid categorization.

---

## What This Page Does

A unified project gallery where every project in the AIM-OS ecosystem is visible:

- **Apps** — running applications (JOC, DAC IDE, Aether Chat, OmniBuilder, etc.)
- **Docs** — documentation-only projects (architecture specs, research reports)
- **Hybrids** — projects that are both code and documentation (prototypes, experiments)
- **Libraries** — shared packages (lucid-mcp, joc components, etc.)

Each project shows version history, relationships to other projects, and deep metadata.

---

## Page Architecture

### Primary View: Project Gallery

Card grid with project cards:

```
┌──────────────────────────────────┐
│ 🖥 JOC - Joint Operations Center │
│ Type: App | Status: Active       │
│ Branch: main (v2.4.1)           │
│ Related: 4 apps, 12 docs        │
│ Agents: Antigravity, DAC, Aether │
│ Last modified: 2 hours ago      │
│ [Open] [Docs] [Branches]        │
└──────────────────────────────────┘
```

Each card shows:
- Project name + icon
- Type badge (App / Doc / Hybrid / Library)
- Active branch and version
- Related project count
- Contributing agents
- Last modified timestamp
- Quick actions

### Secondary View: Relationship Graph

Force-directed graph showing project relationships:

| Edge Type | Visual | Meaning |
|-----------|--------|---------|
| depends_on | Solid arrow | Runtime dependency |
| extends | Dashed arrow | Code extension or fork |
| documents | Dotted line | Documentation relationship |
| competes_with | Red dashed | Alternative implementation |
| supersedes | Strikethrough → solid | Replaced by successor |

### Tertiary View: Branch Viewer

Git-style branch visualization per project:
- Main branch (production)
- Feature branches
- Prototype branches (from the 6 agents' IDE prototypes)
- Merge history

### Quaternary View: Project Detail

Full detail panel for selected project:
- README/description
- File tree
- Contributing agents + their roles
- Related documents (linked)
- Version history with changelog
- Build status and health metrics
- Port assignments (if app)

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 📁 | All Projects | Filterable project list |
| 🔀 | Branches | Branch overview across projects |
| 🔗 | Relations | Relationship type filters |
| 📊 | Stats | Ecosystem analytics |
| 🏷️ | Tags | Project categorization tags |

---

## Implementation Phases

### Phase 1: Project Gallery
- Card grid with basic project metadata
- Type/status filtering
- Search
- Responsive grid layout

### Phase 2: Project Detail Panel
- Slide-over or modal with full project info
- README rendering
- File tree (expandable)
- Related docs links

### Phase 3: Relationship Graph
- Force-directed or hierarchical graph
- Edge type differentiation
- Click to navigate
- Zoom/pan

### Phase 4: Branch Viewer
- Git-style branch visualization
- Branch comparison
- Merge history
