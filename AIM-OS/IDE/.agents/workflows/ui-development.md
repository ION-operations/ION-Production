---
description: Protocol for building UI components to AIM-OS quality standards
---

# UI Development Protocol

> Every UI component in AIM-OS must meet instrument-grade quality. This protocol enforces the standards defined in the [UI Canon](file:///c:/Users/bombe/OneDrive/Desktop/AIM-OS/packages/joc/src/docs/binding_ui_canon.md).

## Pre-Flight (before writing any code)

1. **Identify the surface category** from the UI Canon Law 5 Material Hierarchy:
   - Frame chrome → Full `compileMaterialSurface()` treatment
   - Critical instruments → `SkeuButton`, `SkeuLED`, `SkeuHealthBar`
   - Readouts → `SkeuLCD`, `SkeuPanel`
   - Content surfaces → CSS tokens only (flat, dense, calm)
   - Transient overlays → Glow effects only

2. **Classify the component** per Canon Law 2:
   - **Workspace** (A) → Gets TopBar entry, left panels, center canvas
   - **Panel** (B) → Dockable, reusable, registered in Panel Registry
   - **Detail View** (C) → Contextual overlay, no URL routing

3. **Check the design system tokens** exist for your component:
   - Colors: Use CSS custom properties, never hardcode hex
   - Typography: Inter for UI, JetBrains Mono for data/code
   - Spacing: Use the 4px/8px grid system
   - Border radius: Match existing surfaces (8px panels, 4px inputs, 12px modals)

## Build Phase

4. **Create the CSS first.** Define all visual properties before writing component logic:
   - Use the canonical dark theme palette (background: `#08090d` to `#1a1a2e`)
   - Contrast ratios: 4.5:1 text, 3:1 UI elements (WCAG 2.1 AA)
   - Responsive: Use `clamp()` for widths, `repeat(auto-fill, minmax(...))` for grids
   - No fixed pixel widths on content areas

5. **Implement the component** following these rules:
   - Every interactive element gets a unique descriptive `id`
   - Every data display accepts `dataStatus` prop (live/cached/mock/offline/speculative)
   - Use semantic HTML5 elements (`section`, `nav`, `aside`, `article`)
   - ARIA labels on all interactive elements and icon buttons

6. **Add micro-interactions:**
   - Hover: Subtle brightness/scale change (0.2s ease)
   - Focus: 2px outline, `outline-offset: 2px`, always visible
   - Transitions: Use CSS transitions, prefer `transform` and `opacity` (GPU-composited)
   - Respect `prefers-reduced-motion` — no gratuitous animation

## Quality Gates

7. **Before committing**, verify:
   - [ ] Component renders correctly at all 4 breakpoints (Compact/Standard/Wide/Ultrawide)
   - [ ] Keyboard navigation works (Tab/Shift+Tab reaches all interactive elements)
   - [ ] Color contrast meets WCAG 2.1 AA (4.5:1 text, 3:1 UI)
   - [ ] Mock data is visually distinguished from live data
   - [ ] No hardcoded colors — all using CSS custom properties
   - [ ] Surface Engine integration matches the material hierarchy
   - [ ] Component is registered in Panel Registry if it's a Panel (B)
   - [ ] ARIA labels present on all interactive elements

## Typography Standards

| Context | Font | Weight | Size Range |
|---------|------|--------|------------|
| Headers | Inter | 600-700 | 15-20px |
| Body text | Inter | 400-500 | 12-14px |
| Labels/tags | Inter | 500-600 | 9-11px |
| Data/metrics | JetBrains Mono | 400-500 | 10-13px |
| Code/IDs | JetBrains Mono | 400 | 11-13px |

## Color Palette (Dark Theme)

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-base` | `#08090d` | Page background |
| `--bg-surface` | `#0c0d12` | Card/panel backgrounds |
| `--bg-elevated` | `#14151c` | Hover states, modals |
| `--border-subtle` | `rgba(255,255,255,0.06)` | Dividers |
| `--border-focus` | `rgba(255,255,255,0.12)` | Active borders |
| `--text-primary` | `#e2e4e9` | Headings |
| `--text-secondary` | `#8b8fa0` | Body text |
| `--text-muted` | `#555` | Labels, hints |
| `--accent-gold` | `#facc15` | Command, primary actions |
| `--accent-purple` | `#a855f7` | Executive, highlights |
| `--accent-blue` | `#3b82f6` | Links, selections |
| `--accent-green` | `#22c55e` | Success, live indicators |
| `--accent-red` | `#ef4444` | Errors, warnings |
