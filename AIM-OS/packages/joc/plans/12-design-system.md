# 12 — Design System (Deep Plan)

> **Unified visual language** — glassmorphism, confidence indicators, evidence badges.

---

## Design Principles

1. **High information density** — monitoring-grade aesthetics, not consumer-app whitespace
2. **Glassmorphism dark theme** — `backdrop-filter: blur()`, semi-transparent panels, subtle borders
3. **AIM-OS system colors** — every system (CMC, HHNI, VIF, SEG, etc.) has a consistent color
4. **Confidence is always visible** — κ-scores shown as badges, bars, or glow effects
5. **Evidence is traceable** — every data point has a "source" link

---

## Color System

### AIM-OS System Colors

| System | Color | Hex | Usage |
|--------|-------|-----|-------|
| CMC | Cyan | `#00BCD4` | Memory atoms, storage |
| HHNI | Green | `#4CAF50` | Search, indexing, navigation |
| VIF | Gold | `#FFC107` | Confidence scores, κ-gates |
| SEG | Purple | `#9C27B0` | Evidence, relationships |
| TCS | Blue | `#2196F3` | Timeline, temporal |
| CAS | Red-Orange | `#FF5722` | Consciousness, attention |
| APOE | Teal | `#009688` | Plans, orchestration |
| SCOR | Indigo | `#3F51B5` | Safety, scoring |

### Status Colors

| Status | Color | Usage |
|--------|-------|-------|
| Active/OK | `#4CAF50` | Connected systems, running processes |
| Warning | `#FFC107` | High CPU, stale data, degraded confidence |
| Error | `#F44336` | Disconnected, failed gates, contradictions |
| Info | `#2196F3` | Informational indicators |
| Muted | `#616161` | Disabled, unavailable, mock data |

### Confidence Display

| κ-Score Range | Visual | Color |
|--------------|--------|-------|
| 0.90 - 1.00 | Solid green badge | `#4CAF50` |
| 0.75 - 0.89 | Solid cyan badge | `#00BCD4` |
| 0.50 - 0.74 | Amber outline badge | `#FFC107` |
| 0.25 - 0.49 | Red outline badge | `#FF5722` |
| 0.00 - 0.24 | Pulsing red badge | `#F44336` |

---

## Glassmorphism Tokens

```css
:root {
  /* Surfaces */
  --surface-primary: rgba(18, 18, 24, 0.92);
  --surface-secondary: rgba(25, 25, 35, 0.88);
  --surface-elevated: rgba(30, 30, 45, 0.85);
  --surface-glass: rgba(255, 255, 255, 0.04);

  /* Blur */
  --blur-light: blur(8px);
  --blur-medium: blur(16px);
  --blur-heavy: blur(24px);

  /* Borders */
  --border-subtle: 1px solid rgba(255, 255, 255, 0.06);
  --border-active: 1px solid rgba(255, 255, 255, 0.12);
  --border-glow: 1px solid rgba(0, 188, 212, 0.3);

  /* Shadows */
  --shadow-float: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-raised: 0 4px 16px rgba(0, 0, 0, 0.3);

  /* Text */
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.65);
  --text-muted: rgba(255, 255, 255, 0.38);

  /* Typography */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-sans: 'Inter', -apple-system, sans-serif;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.25s ease;
  --transition-drawer: 0.2s ease;
}
```

---

## Component Patterns

### Badge Components

- `<ConfidenceBadge score={0.92} />` — κ-score with color-coded display
- `<SystemBadge system="CMC" connected={true} />` — AIM-OS system indicator
- `<StatusBadge status="active" />` — generic status indicator
- `<MockBadge />` — "[MOCK]" label when using fallback data

### Panel Components

- Glass surface background with blur
- Subtle top border for depth
- Collapsible header with title, icon, and actions
- Loading skeleton with shimmer animation
- Error boundary with retry button

### Graph Components

- Consistent node shapes per type (square=prompt, circle=atom, diamond=KI, etc.)
- Edge styles per relationship type
- Hover tooltip with detail preview
- Click → detail panel

---

## Implementation Phases

### Phase 1: CSS Token System
- All CSS custom properties defined in `design-tokens.css`
- System color variables
- Glassmorphism surface classes

### Phase 2: Badge Component Library
- ConfidenceBadge, SystemBadge, StatusBadge, MockBadge
- Consistent sizing and spacing
- Responsive text scaling

### Phase 3: Panel Base Component
- Glass surface styling
- Loading/error states
- Collapse/expand behavior
- Consistent header layout

### Phase 4: Graph Style Standards
- Node shape definitions
- Edge style definitions
- Color palette application
- Interaction patterns
