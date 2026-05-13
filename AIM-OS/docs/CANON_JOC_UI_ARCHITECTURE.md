# JOC UI Canon — Architecture & Display Systems

**Author:** Braden (Architect) + Antigravity (Documenter)  
**Date:** 2026-03-03  
**Status:** 🔴 CANON — Binding architectural decisions for all JOC development  
**Lineage:** DAC Prototype → Max V2 Analysis → Opus JOC Master Vision → This Document  

---

## 1. Purpose

This document defines the **binding canon** for JOC's UI architecture, responsive behavior, multi-form-factor strategy, and the Aether Oracle autopilot control system. All agents and developers building JOC must follow these rules.

---

## 2. Evolutionary Context

JOC is the convergence of multiple prototype generations:

| Prototype | Key Innovation | Carried Forward |
|-----------|---------------|-----------------|
| **DAC** | 5-zone layout, `useAIMOS` hooks, Context Web, 25+ panels, bitemporal timeline | Layout architecture, AIM-OS integration patterns |
| **Max** | Panel-first customization, drag-and-drop layout persistence | Flexible panel management concept |
| **Aether** | Agent orchestration, multi-agent coordination dashboard | Agent fleet control, mission dispatch |
| **Opus JOC Vision** | 5 Pillars (Dashboard, Sessions, Dispatch, Synthesizer, Projects) | Operational mission control paradigm |
| **JOC v1 (Current)** | Unified shell, TopBar nav, calendar/scheduler, macro engine | Live production system |

> [!IMPORTANT]
> JOC is NOT a browser. NOT an IDE. NOT an app launcher. It is the **central nervous system** of AIM-OS — a unified command surface where AI subscriptions become operational assets under orchestrated control.

---

## 3. Display Architecture

### 3.1 Primary Targets

JOC must render optimally across TWO primary desktop form factors:

| Target | Resolution | Aspect | Viewport Width |
|--------|-----------|--------|---------------|
| **Ultrawide** | 3440×1440+ | 21:9 | ≥2560px |
| **Standard** | 1920×1080 | 16:9 | 1280–2559px |

### 3.2 Layout Zones (5-Zone System)

Inherited from DAC and refined for JOC:

```
┌──────────────────────────────────────────────────────────────────┐
│  TOP BAR (40px) — Navigation + Oracle Status + Command Palette   │
├──────┬───────────────────────────────────────────────┬───────────┤
│      │                                               │           │
│ LEFT │            MAIN CONTENT AREA                  │  RIGHT    │
│ RAIL │                                               │  PANEL    │
│(48px │  Primary workspace — page content renders     │ (0-400px) │
│icon) │  here. Full width when right panel closed.    │           │
│      │                                               │  Context  │
│      │  On ultrawide: content + side panel can       │  drawers  │
│      │  display side by side.                        │           │
│      │                                               │           │
├──────┴───────────────────────────────────────────────┴───────────┤
│  BOTTOM BAR (0-400px) — Timeline, Comms, Terminal, Diagnostics   │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 Responsive Behavior

```
ULTRAWIDE (≥2560px):
├── Left Rail: 48px (icon-only, always visible)
├── Main Content: flexible (expands to fill)
├── Right Panel: 350-400px (visible by default)
└── Bottom Bar: collapsible (mid/full states available)
    → Content has enough room for side-by-side layouts
    → Dashboard cards render in 4-5 columns
    → Calendar Week view shows all 7 days comfortably

STANDARD (1280-2559px):
├── Left Rail: 48px (icon-only, always visible)
├── Main Content: flexible (full width when panels closed)
├── Right Panel: 300-350px (overlay mode, toggle on/off)
└── Bottom Bar: collapsible
    → Dashboard cards render in 3-4 columns
    → Calendar Week view may scroll horizontally
    → Right panel overlays content when open
```

### 3.4 CSS Breakpoint Rules

```css
/* Standard desktop */
@media (min-width: 1280px) { /* base layout */ }

/* Ultrawide */
@media (min-width: 2560px) {
  /* Right panel always visible */
  /* Dashboard 5-column grid */
  /* Side-by-side page layouts enabled */
}

/* Below standard — fallback */
@media (max-width: 1279px) {
  /* Simplified single-column layout */
  /* Bottom bar fully collapsed */
  /* Left rail hidden behind hamburger */
}
```

> [!CAUTION]
> JOC is NOT designed for mobile or tablet breakpoints in this application. Those are separate apps (see Section 5). Never compromise the desktop experience for sub-1280px widths.

---

## 4. The Aether Oracle System

### 4.1 Core Concept

The entire JOC application is designed to be **dual-controlled**:

1. **User Mode** — Braden (or any human operator) has full manual control  
2. **Oracle Mode** — Aether Oracle (the CEO/orchestrator AI) can autonomously operate JOC

This is not a "suggestion engine." The Oracle can:
- Dispatch missions to AI providers
- Schedule macro automations
- Respond to events (session health drop → auto-recover)
- Manage agent task assignments
- Monitor cost thresholds and enforce budgets
- Execute timed workflows via the calendar/scheduler system

### 4.2 Control Hierarchy

```
┌─────────────────────────────────────┐
│         BRADEN (User)               │  ← Always has ultimate override
│         Authority: ABSOLUTE         │
├─────────────────────────────────────┤
│     AETHER ORACLE (AI Manager)      │  ← Autonomous operations
│     Authority: DELEGATED            │
│     Scope: Configurable per-system  │
├─────────────────────────────────────┤
│     SPECIALIST AGENTS               │  ← Execute specific tasks
│     Authority: TASK-SCOPED          │
│     (Codex, Opus, Gemini, etc.)     │
└─────────────────────────────────────┘
```

### 4.3 Oracle Status in TopBar

The TopBar must always display the Oracle's current state:

```
┌─────────────────────────────────────────────────────────────────┐
│ ◉ JOC   Operations ▼  Intelligence ▼  ...   │ 🟢 ORACLE: AUTO │
│                                               │ ⌘⇧P Palette     │
└─────────────────────────────────────────────────────────────────┘
```

Oracle states:
- 🟢 **AUTO** — Oracle is actively managing (green pulse animation)
- 🟡 **SUPERVISED** — Oracle suggests, user approves
- 🔴 **MANUAL** — Oracle is passive, user controls everything
- ⚪ **OFFLINE** — Oracle not connected

### 4.4 Oracle Permission Model

Each JOC subsystem has its own autopilot permission level:

| System | Auto | Supervised | Manual | Description |
|--------|------|-----------|--------|-------------|
| Dispatch | ✅ | ✅ | ✅ | Can Oracle send prompts to AI providers? |
| Scheduler | ✅ | ✅ | ✅ | Can Oracle create/modify scheduled events? |
| Macros | ✅ | ✅ | ✅ | Can Oracle trigger automation macros? |
| Sessions | ❌ | ✅ | ✅ | Can Oracle restart/refresh browser sessions? |
| Vault | ❌ | ❌ | ✅ | Can Oracle access/modify credentials? |
| Agent Comms | ✅ | ✅ | ✅ | Can Oracle send messages to agents? |
| Settings | ❌ | ❌ | ✅ | Can Oracle change system settings? |

> [!WARNING]
> The Vault and Settings should NEVER be in full auto mode. These require explicit user action. The Oracle can request escalation via the Co-Agency protocol but cannot unilaterally modify credentials or system configuration.

### 4.5 Oracle Action Log

Every Oracle action must be logged and visible in the Activity Log:

```
[ORACLE] 16:30:00 — Dispatched M-043 to ChatGPT + Gemini (auto)
[ORACLE] 16:28:15 — Triggered "Morning Brief" macro (scheduled)
[ORACLE] 16:25:00 — ⚠️ Requested Vault access → DENIED (requires user)
[ORACLE] 16:22:00 — Refreshed Perplexity session (supervised → approved)
```

---

## 5. Multi-Form-Factor Strategy

### 5.1 Three Applications, One System

JOC is NOT a single responsive web app trying to fit every screen. It is **three purpose-built applications** sharing a common data layer:

```
┌─────────────────────────────────────────────────────────┐
│                    AIM-OS DATA LAYER                     │
│  MCP Server • CMC • HHNI • Zustand (persisted stores)   │
├─────────────┬──────────────────┬────────────────────────┤
│             │                  │                        │
│  JOC DESKTOP│  JOC TABLET      │  JOC MOBILE            │
│  (Electron) │  (PWA / Electron)│  (PWA / React Native)  │
│             │                  │                        │
│  FULL SYSTEM│  OPERATIONS VIEW │  COMMAND & MONITOR     │
│  All 22+    │  Key pages only  │  Essential controls    │
│  pages      │  ~10 pages       │  ~5 screens            │
│             │                  │                        │
│  Ultrawide +│  iPad/Surface    │  iPhone/Android        │
│  Standard   │  landscape       │  portrait              │
└─────────────┴──────────────────┴────────────────────────┘
```

### 5.2 Tablet App — Operations Commander

Designed for iPad Pro / Surface landscape use while away from the main desk:

**Included pages:**
- Dashboard (simplified cards)
- Dispatch Center (send prompts to AIs)
- Agent Comms (message board)
- Calendar (month/week view)
- Activity Log (monitoring feed)
- Session Health (status overview)
- Oracle Control (toggle auto/supervised/manual)
- Settings (essential config only)

**NOT included on tablet:**
- Code Editor, CLI Terminal (no keyboard-heavy interfaces)
- System Atlas, Context Graph (complex visualizations need ultrawide)
- GPU Monitor, Storage Browser (infrastructure tools)

**Design considerations:**
- Touch-optimized hit targets (44px minimum)
- Swipe gestures for navigation between pages
- Simplified TopBar (horizontal page tabs, no dropdowns)
- Bottom sheet pattern for drawers (iOS/Android native feel)

### 5.3 Mobile App — Remote Control

Designed for iPhone/Android — quick monitoring and emergency control:

**Included screens:**
- Dashboard (single-column cards, status only)
- Quick Dispatch (simplified: type prompt → pick AIs → send)
- Agent Comms (chat-style message view)
- Oracle Toggle (one-tap auto/supervised/manual)
- Notifications (push alerts for mission completion, health drops, Oracle requests)

**NOT included on mobile:**
- Everything else. Mobile is a REMOTE CONTROL, not the full system.

**Design considerations:**
- Native navigation (tab bar at bottom)
- Push notifications for critical events
- Biometric auth for sensitive actions
- Minimal UI — status cards and action buttons only

### 5.4 Shared Data Architecture

All three apps read/write from the same sources:

```typescript
// All apps use the same stores
import { useJOCStore } from '@aim-os/joc-core';
import { useCalendarStore } from '@aim-os/joc-core';
import { useCredentialStore } from '@aim-os/joc-core';

// All apps communicate via MCP
import { mcpClient } from '@aim-os/mcp-client';
```

> [!TIP]
> Extract shared stores and types into a `@aim-os/joc-core` package. Desktop, tablet, and mobile apps all import from this package. This ensures data consistency across platforms.

---

## 6. Component Architecture Rules

### 6.1 Every Page Must Support

- Aether Oracle hooks (can be AI-controlled)
- Responsive layout (ultrawide ↔ standard)
- Keyboard shortcuts (desktop)
- Accessibility (ARIA labels, focus management)
- State persistence (Zustand + encrypted persist)

### 6.2 Every Page Must Expose

```typescript
interface PageOracleAPI {
  /** Oracle can programmatically invoke page actions */
  executeAction(action: string, params: Record<string, unknown>): Promise<void>;
  /** Oracle can read current page state */
  getState(): Record<string, unknown>;
  /** Oracle can subscribe to page events */
  onEvent(handler: (event: PageEvent) => void): () => void;
}
```

This is how the Oracle "sees" and "controls" each page.

### 6.3 TopBar Navigation Canon

The TopBar navigation groups are canon:

| Group | Pages | Rationale |
|-------|-------|-----------|
| **Operations** | Dashboard, Dispatch, Mission Builder, Synthesizer, Calendar | Things you DO — active operations |
| **Intelligence** | Sessions, Health, Comms, Context Engine, Context Graph | Things you OBSERVE — AI fleet intelligence |
| **Infrastructure** | System Atlas, Compute, GPU, Vault, Storage | Things that SUPPORT — underlying systems |
| **Tools** | Code Editor, CLI, Projects, Activity, Settings | Things you USE — utility interfaces |

New pages must fit into one of these groups. If a page doesn't fit, question whether it belongs in JOC at all.

---

## 7. Visual Design Canon Compliance

All JOC work follows the Opus Visual Interface Canon:

| Principle | Application |
|-----------|-------------|
| **No Generic Sliders** | Health bars, progress fills, colored indicators. Not numbers. |
| **Direct Manipulation** | Drag to reorder, click to dispatch, swipe to navigate. |
| **ROM Zones** | Green (>80%), amber (50-80%), red (<50%). Everywhere. |
| **Live Preview** | Real-time updates. No refresh buttons. No stale data. |
| **Dark Theme First** | `#0a0a15` background, `#1a1a2e` surfaces, `#4ecdc4` accents. |

---

## 8. Future: JOC + DAC Convergence

The DAC prototype's revolutionary features — **Context Web**, **Evolution Explorer**, **Consciousness Visualization**, **Bitemporal Timeline** — are the roadmap for JOC's next evolution. These features should be integrated as new pages within the existing TopBar navigation structure:

| DAC Feature | JOC Integration | NavGroup |
|-------------|----------------|----------|
| Context Web | New page: `context-web` | Intelligence |
| Evolution Explorer | New page: `evolution` | Intelligence |
| Consciousness Viz | New page: `consciousness` | Infrastructure |
| Bitemporal Timeline | Enhance existing bottom bar timeline | (already exists) |
| `useAIMOS` Hooks | Adopt as standard integration pattern | (architectural) |

---

*This document is canon. All JOC development must comply.*
