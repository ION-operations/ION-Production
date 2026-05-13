# 13 — Production Readiness (Deep Plan)

> **What "production" means for JOC** — no mock data, real connections, robust error handling.

---

## Production Readiness Checklist

### Per-Component Requirements

| Requirement | Description | Source |
|-------------|-------------|--------|
| Real MCP data | No hardcoded mock data in production mode | DAC OBJ-07 |
| Graceful fallback | If MCP disconnects, show [MOCK] badge and fallback data | Data Integration Plan 08 |
| Error boundaries | Every panel wrapped in React Error Boundary | Lex pattern |
| Loading states | Skeleton shimmer during data fetch | Rev pattern |
| WCAG 2.1 AA | Keyboard navigation, ARIA labels, contrast ratios | Rev accessibility-first |
| Lazy loading | Panels load on demand, not at startup | Rev performance |
| Virtual scrolling | Lists >100 items use virtualization | Rev performance |
| Memoization | React.memo, useMemo, useCallback on expensive ops | DAC V2 |

### Per-Page Requirements

| Requirement | Description |
|-------------|-------------|
| Left drawer config | Every page exports `LeftDrawerConfig` |
| Responsive layout | Works at 1024px, 1440px, and 1920px+ |
| Page title | Sets document title on mount |
| Route params | Handles URL params for deep linking |
| Keyboard shortcuts | Page-level shortcuts registered |
| Error state | Full-page error state with retry |
| Empty state | Meaningful empty state when no data |

### System-Level Requirements

| Requirement | Description |
|-------------|-------------|
| MCP health check | Status bar shows all 8 system connection states |
| Theme persistence | Theme choice persists in localStorage |
| Layout persistence | Drawer states, panel sizes persist |
| Performance budget | First paint <2s, interactive <3s |
| Bundle splitting | Route-based code splitting |
| Hot reload | Vite HMR for development |

---

## Quality Gates for Production

| Gate | Method | Threshold |
|------|--------|-----------|
| TypeScript strict | `tsc --noEmit` | Zero errors |
| Lint | ESLint | Zero errors, warnings reviewed |
| Test | Vitest | >80% coverage on hooks and utils |
| Accessibility | axe-core or pa11y | Zero violations |
| Performance | Lighthouse | Score >90 |
| Bundle size | Per-route budget | <500KB per route (gzipped) |

---

## Migration from Prototype to Production

### Step 1: Identify Mock Data
- Search codebase for `mock`, `MOCK`, `fake`, `dummy`, `placeholder`
- List all components using hardcoded data
- Map each to its MCP data source

### Step 2: Wire Real Data
- Implement `useAIMOS` hook (Plan 08)
- Replace mock data sources with hook calls
- Add `[MOCK]` fallback indicators

### Step 3: Add Error Handling
- Wrap every panel in ErrorBoundary
- Add loading skeletons
- Add empty state components
- Add retry buttons on failures

### Step 4: Accessibility Pass
- Keyboard navigation audit
- ARIA label audit
- Focus management verification
- Color contrast verification

### Step 5: Performance Pass
- Lazy loading verification
- Virtual scrolling for long lists
- Memoization audit
- Bundle analysis and splitting
