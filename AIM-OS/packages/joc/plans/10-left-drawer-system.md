# 10 — Left Drawer System (Deep Plan)

> **Per-page left icon bar + drawer system.** Each page gets unique left-side tools.

---

## Core Requirement

The user specified:
> "The left side will be unique to the page you are on so it provides extra space for tools and drawers per page as needed."

---

## Implementation Architecture

### 1. LeftDrawerContext

React context that manages current page's drawer configuration:

```typescript
interface LeftDrawerContextValue {
  config: LeftDrawerConfig | null;
  activeDrawerId: string | null;
  openDrawer: (id: string) => void;
  closeDrawer: () => void;
  toggleDrawer: (id: string) => void;
  registerConfig: (config: LeftDrawerConfig) => void;
}
```

### 2. Registration Pattern

Each page uses a hook to register its drawers on mount:

```typescript
function ContextSystemPage() {
  useLeftDrawerRegistration({
    pageId: 'context-system',
    items: [
      { id: 'search', icon: SearchIcon, label: 'Context Search', component: ContextSearchDrawer },
      { id: 'pipeline', icon: PipelineIcon, label: 'Pipeline Status', component: PipelineStatusDrawer },
      // ...
    ]
  });

  return <div>...</div>;
}
```

### 3. Icon Bar Component

Renders from registered config. On route change, config swaps automatically.

### 4. Drawer Component

- Slides in from left edge (width transition, not transform)
- Overlays or pushes main content depending on viewport size
- Close on: icon re-click, Escape key, click-outside
- Remembers last open drawer per page (localStorage)

---

## Pages and Their Left Drawers

| Page | Drawers |
|------|---------|
| Context System | Search, Pipeline, Memory, Confidence, Evidence, Envelopes |
| Task Manager | Tasks, Blockers, Gates, Agents, Burn Chart, Alerts |
| Log Whisperer | Sources, Search, AI Whisper, Sentinels, Stats, Config |
| Project Hub | All Projects, Branches, Relations, Stats, Tags |
| Doc Builder | Library, Search, NL Tags, Generate, Validate, Coverage |
| Aether Oracle | Agents, Consciousness, Messages, Tasks, Performance, Registry |
| System Atlas | Modules, Search, Dependencies, Contracts, Health |
| Mission Control | Fleet, Sessions, Health, Timeline, Alerts |
| AI Cockpit | Files, Symbols, Context, Git, Templates |

---

## Implementation Phases

### Phase 1: Context + Registration Hook
- `LeftDrawerContext` provider
- `useLeftDrawerRegistration` hook
- Route-change cleanup

### Phase 2: Icon Bar Component
- Icon rendering from config
- Active state highlighting
- Badge rendering
- Tooltip labels

### Phase 3: Drawer Component
- Width transition animation
- Push vs. overlay based on viewport
- Click-outside close
- Keyboard (Escape) close

### Phase 4: State Persistence
- localStorage for last-open-drawer per page
- Keyboard shortcut registration per drawer
