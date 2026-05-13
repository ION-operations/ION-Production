# 01 — Architecture & Layout (Deep Plan)

> **Foundation plan** — everything else builds on this.  
> Grounded in DAC V2 Design, Best Ideas Synthesis, Max panel-first philosophy, user requirements.

---

## Layout Philosophy

The JOC uses a **dual sidebar paradigm**:

- **Right bar + drawers** = **universal** — same tools on every page (notifications, system health, global settings, universal search)
- **Left bar + drawers** = **page-specific** — each page registers its own icon bar items and drawer contents

This creates a "constant cockpit" feeling on the right side while giving each page its own specialized tooling on the left.

---

## The 5-Zone Layout (Heritage from DAC V2)

```
┌────────────────────────────────────────────────────────────────────┐
│  Top Bar (48px) — Nav, command palette, agent status, system pulse │
├──────┬──────┬────────────────────────────────┬──────┬──────────────┤
│ Left │ Left │                                │Right │   Right      │
│ Icon │Drawer│     Main Page Content          │Drawer│   Icon       │
│ Bar  │      │     (Router outlet)            │      │   Bar        │
│(48px)│(0-350│                                │(0-350│  (48px)      │
│      │  px) │                                │  px) │              │
├──────┴──────┴────────────────────────────────┴──────┴──────────────┤
│  Status Bar (32px) — ports, processes, system health, MCP status   │
└────────────────────────────────────────────────────────────────────┘
```

### Zone Definitions

| Zone | Fixed Width | Resizable | Content Source |
|------|------------|-----------|----------------|
| Top Bar | 48px height | No | Global — nav items, page title, command palette |
| Left Icon Bar | 48px width | No | Page-specific — registered per route |
| Left Drawer | 0-350px width | Yes | Page-specific — opens from icon bar click |
| Main Page | Flex remaining | N/A | Router outlet — current page component |
| Right Drawer | 0-350px width | Yes | Universal — same on every page |
| Right Icon Bar | 48px width | No | Universal — notifications, system health, etc. |
| Status Bar | 32px height | No | Global — port monitor, process status, MCP |

---

## Left Icon Bar + Drawer Registry

Each page component exports a `leftDrawerConfig`:

```typescript
interface LeftDrawerConfig {
  pageId: string;           // e.g. 'context-system'
  items: LeftDrawerItem[];
}

interface LeftDrawerItem {
  id: string;
  icon: React.ComponentType;
  label: string;             // tooltip
  drawerComponent: React.ComponentType;
  badge?: number | string;   // notification count or status
  shortcut?: string;         // keyboard shortcut
}
```

Example for Context System Page:
```typescript
const contextPageDrawers: LeftDrawerConfig = {
  pageId: 'context-system',
  items: [
    { id: 'search', icon: SearchIcon, label: 'Context Search', drawerComponent: ContextSearchDrawer },
    { id: 'pipeline', icon: PipelineIcon, label: 'Pipeline Status', drawerComponent: PipelineStatusDrawer },
    { id: 'memory', icon: BrainIcon, label: 'Memory Browser', drawerComponent: MemoryBrowserDrawer },
    { id: 'confidence', icon: ScaleIcon, label: 'Confidence', drawerComponent: ConfidenceDrawer },
    { id: 'evidence', icon: LinkIcon, label: 'Evidence', drawerComponent: EvidenceDrawer },
    { id: 'envelopes', icon: FileIcon, label: 'Envelopes', drawerComponent: EnvelopeDrawer },
  ]
};
```

---

## Right Icon Bar (Universal)

These remain constant across all pages:

| Icon | Drawer | Purpose |
|------|--------|---------|
| 🔔 | Notifications | Agent messages, gate failures, system alerts |
| 💓 | System Health | AIM-OS system status (CMC, HHNI, VIF, SEG, etc.) |
| 🔍 | Universal Search | Cross-system semantic search (HHNI-powered) |
| ⚙️ | Settings | Layout preferences, theme, MCP endpoints |
| 📊 | Quick Stats | Memory count, active agents, κ-score avg |

---

## CSS Architecture

The layout uses CSS Grid for the outer shell and Flexbox for inner zones:

```css
.joc-shell {
  display: grid;
  grid-template-rows: 48px 1fr 32px;
  grid-template-columns: 48px auto 1fr auto 48px;
  grid-template-areas:
    "top    top    top    top    top"
    "l-bar  l-drw  main   r-drw  r-bar"
    "status status status status status";
  height: 100vh;
  overflow: hidden;
}
```

Drawer open/close uses `width` transitions (not `transform`) to properly reflow the grid:
```css
.left-drawer {
  grid-area: l-drw;
  width: 0;            /* closed */
  transition: width 0.2s ease;
  overflow: hidden;
}
.left-drawer.open {
  width: 320px;
}
```

---

## Panel-First Architecture (from Max)

Every tool rendered in a drawer slot is a `Panel` component with consistent behavior:

```typescript
interface PanelProps {
  id: string;
  title: string;
  onClose?: () => void;
  onMinimize?: () => void;
  resizable?: boolean;
  collapsible?: boolean;
  headerActions?: React.ReactNode;
  children: React.ReactNode;
}
```

Panels support:
- ✅ Collapse/expand (accordion mode)
- ✅ Header action buttons
- ✅ Loading states (skeleton shimmer)
- ✅ Error boundaries (graceful fallback)
- ✅ Keyboard shortcut registration

---

## Responsive Behavior

| Viewport | Left Bar | Left Drawer | Main | Right Drawer | Right Bar |
|----------|----------|-------------|------|-------------|-----------|
| ≥1440px | Visible | Inline push | Flex | Inline push | Visible |
| 1024-1439 | Visible | Overlay | Full | Overlay | Visible |
| <1024px | Hidden (hamburger) | Overlay | Full | Overlay | Hidden (hamburger) |

---

## Implementation Phases

### Phase 1: Grid Shell
- CSS Grid layout with all 7 zones
- Top bar with navigation
- Status bar with placeholder content
- Router outlet in main area

### Phase 2: Right Icon Bar + Universal Drawers
- 5 universal icons
- Drawer open/close with width transition
- Notification, System Health, Search, Settings, Quick Stats drawers
- Persist drawer state in localStorage

### Phase 3: Left Drawer Registry System
- LeftDrawerConfig type system
- Context provider for registering page-specific drawers
- Icon bar renders from config
- Drawer area renders from config
- Route change → drawer config swap

### Phase 4: Panel Component System
- Base Panel component with consistent props
- Loading/error states
- Collapse/expand
- Keyboard shortcuts
