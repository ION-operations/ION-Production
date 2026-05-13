# JOC UI Requirements Specification
> **Owner:** Braden  
> **Last Updated:** 2026-03-04  
> **Priority:** CRITICAL — Every AI agent working on JOC MUST read this file first.

---

## 1. Visual Aesthetic: DXL Matte-Black Instrument Panel

**Reference:** `packages/joc/src/styles/joc.css` CSS variables  
**Style Reference Image:** See DSLR camera panel aesthetic — small, precise, instrument-grade detailing.

### Color Palette
| Token | Value | Usage |
|-------|-------|-------|
| Background deep | `#0a0a0a` | Page backgrounds |
| Background surface | `#0e0e0e` | Cards, panels |
| Background panel | `#111111` | Sub-bars, secondary panels |
| Border | `#1e1e1e` | All borders |
| Border hover | `#2a2a2a` | Hover states |
| Border active | `#444444` | Active/focus states |
| Text primary | `#cccccc` | Primary text |
| Text secondary | `#aaaaaa` | Secondary labels |
| Text hint | `#555555` | Hints, inactive |
| Text muted | `#333333` | Very subtle |

### Typography
- **Font family:** `var(--font-mono)` for ALL UI labels, values, badges
- **Sizes:** 7-11px range. Section titles 9px, labels 8-9px, values 11-14px
- **Weight:** 600-700 for labels, 400 for body
- **Letter-spacing:** 0.5-1.5px on uppercase labels
- **Transform:** `uppercase` for all section headers and labels

### Absolute Rules
> [!CAUTION]
> - **NO EMOJI** anywhere in the UI. All icons MUST be custom inline SVGs.
> - **NO Material Design colors** (no `#4CAF50`, `#2196F3`, etc.)
> - **NO purple or blue accent colors** (no `#7c4dff`, `#00d4ff` except as data viz)
> - **NO `var(--accent)`** in navigation or structural elements
> - **NO rounded corners > 2px** on instrument panels
> - **NO large font sizes** (nothing above 14px except page-level stat values)

### Desired Feel
- DSLR camera top panel: small, precise, densely informational
- Aircraft instrument cluster: matte black, minimal chrome
- Professional recording console: tight grids, no wasted space
- Every pixel intentional. No placeholder content.

---

## 2. Navigation Architecture

### TopBar
- **Flat group buttons** — NO dropdown menus ever
- Groups: `OPERATIONS` | `INTELLIGENCE` | `INFRASTRUCTURE` | `TOOLS`
- Left: JOC logo (monospace, 11px, #888)
- Right: Oracle status badge (DXL styled)
- Background: `#0e0e0e`, border-bottom: `1px solid #1e1e1e`

### PageSubBar (replaces old PageTabs)
- Contextual sub-tabs for the active TopBar group
- Background: `#111111`, monospace 9px, uppercase
- Active tab: `#ccc` text + 2px bottom border

### Group → Sub-Page Mapping
| Group | Sub-Pages |
|-------|-----------|
| OPERATIONS | Dashboard, Dispatch, Mission Builder, Synthesizer, Calendar, Context Engine |
| INTELLIGENCE | Sessions, Session Health, Agent Comms, Context Graph, Oracle, Agent Builder |
| INFRASTRUCTURE | Compute, System Atlas, Credential Vault |
| TOOLS | Code Editor, Terminal, Settings |

---

## 3. Page Consolidation Rules

### Principle
> If a page has sparse content that looks ridiculous on a full screen, it should NOT be a standalone page. It should be a **side drawer** on its parent page, or a **section** within a related page.

### Completed Merges
- `GpuMonitorPage` → Inference queue merged into `ComputePage` local section
- `StorageBrowserPage` → Storage quotas + file browser added as `SettingsPage` section
- `MCPDiagnosticsPage` → Health status + tool list added as `SettingsPage` section
- `ActivityLogPage` → Route removed (content exists as `activity-feed` left drawer)
- `ProjectCatalogPage` → Route removed (content exists as left drawer)

### Dead Routes Removed from PageRouter
`gpu`, `activity`, `projects`, `storage`, `diagnostics`

---

## 4. Pages DXL Overhaul Status

### ✅ Completed (Tier 1)
- `DashboardPage` — Full DXL rebuild with custom SVGs
- `DispatchPage` — Full DXL rebuild + 5 custom strategy SVG icons
- `OraclePage` — Full DXL rebuild
- `SessionPage` — Full DXL rebuild + 7 custom inline SVGs

### ❌ Still Needs DXL Overhaul
- `ComputePage` — Has emoji, old colors, doesn't fill screen width
- `SettingsPage` — Has emoji, old styling
- `SessionHealthPage` — Needs DXL
- `AgentCommsPage` — Needs DXL
- `AutoContextPage` — Needs DXL
- `CredentialVaultPage` — Needs DXL
- `CliTerminalPage` — Needs DXL
- `MissionBuilderPage` — Needs DXL
- `CalendarPage` — Needs DXL
- `ContextGraphPage` — Needs DXL
- `AgentBuilderPage` — Needs DXL
- `WelcomePage` — Needs DXL
- `SurfaceEngineDemo` — Needs DXL
- `Left drawer panels` — Need DXL styling
- `Right icon bar` — Needs DXL styling

---

## 5. Custom SVG Icon Library

All icons must be inline SVGs with `currentColor`, no emoji, no Material Design icons.

### Created Icons (in `components/icons.tsx` or inline)
- RadarIcon, ConstellationIcon, LaunchVectorIcon, SignalPulseIcon
- HexLatticeIcon, ChipDieIcon, TuningForkIcon, CloseIcon, ChevronLeftIcon
- 5 Dispatch strategy icons (sequential, parallel, ring, cascade, swarm)
- 7 Session page icons (browser, model, inject, dom, screenshot, extract, refresh)

### Icon Rules
- Stroke-based, 1.5-2px stroke width
- `currentColor` for all fill/stroke
- Default size: 14-16px
- Viewbox: `0 0 24 24` standard

---

## 6. Component Patterns

### Panel/Card
```css
background: #0e0e0e;
border: 1px solid #1e1e1e;
padding: 8-12px;
border-radius: 0-2px;
```

### Section Headers
```css
font-family: var(--font-mono);
font-size: 9px;
font-weight: 700;
letter-spacing: 1px;
text-transform: uppercase;
color: #555;
margin-bottom: 6px;
```

### Status Dots
```css
width: 6px;
height: 6px;
border-radius: 50%;
/* Green: #33cc66, Yellow: #cc9900, Red: #cc3333, Off: #333 */
```

### Progress Bars
```css
height: 3-4px;
background: #1a1a1a;
border-radius: 0;
/* Fill uses contextual color */
```

---

## 7. Critical Protocols

1. **ALWAYS read this file** before making JOC UI changes
2. **Use MCP tools** (`store_memory`, `retrieve_memory`) to persist decisions
3. **No placeholders** — every element must have real mock data
4. **Full-width layouts** — pages must use available screen width
5. **Document all changes** in conversation artifacts
6. **Validate visually** with browser screenshots after changes
7. **Check against this spec** before calling work "done"
