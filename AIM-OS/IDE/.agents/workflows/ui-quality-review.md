---
description: Checklist for reviewing finished UI work against AIM-OS quality standards
---

# UI Quality Review Protocol

> Review checklist for validating any UI component, page, or visualization before merge. Based on the [AIM-OS UI Canon](file:///c:/Users/bombe/OneDrive/Desktop/AIM-OS/packages/joc/src/docs/binding_ui_canon.md).

## 1. Visual Quality (Must be 10x standard)

- [ ] **First impression test**: Does it look premium and instrument-grade?
- [ ] **Material hierarchy applied**: Frame surfaces have depth, content surfaces are calm
- [ ] **No generic colors**: Uses curated palette tokens, not raw hex
- [ ] **Typography is correct**: Inter for UI, JetBrains Mono for data
- [ ] **Spacing follows 4px/8px grid**: No arbitrary margins/paddings
- [ ] **Micro-interactions present**: Hover states, focus rings, transitions
- [ ] **No placeholder content**: All images/icons are real, not lorem ipsum

## 2. Canon Law Compliance

- [ ] **Law 1 (Shell Grammar)**: Component doesn't break shell zones
- [ ] **Law 2 (Taxonomy)**: Correctly classified as Workspace/Panel/DetailView
- [ ] **Law 3 (Registry)**: If Panel, registered with complete schema
- [ ] **Law 4 (Assistant Rail)**: Doesn't commandeer the right rail
- [ ] **Law 5 (Material)**: Correct Surface Engine usage per category
- [ ] **Law 6 (Data Truth)**: Mock data visually distinguished, `dataStatus` prop present
- [ ] **Law 7 (Responsiveness)**: Works at all 4 breakpoints
- [ ] **Law 8 (Accessibility)**: Meets WCAG 2.1 AA, keyboard nav, ARIA labels

## 3. Technical Quality

- [ ] **No inline styles**: All styling via CSS classes or custom properties
- [ ] **Unique IDs**: All interactive elements have descriptive unique IDs
- [ ] **Performance**: No unnecessary re-renders, GPU-composited animations
- [ ] **Reduced motion**: `prefers-reduced-motion` respected
- [ ] **Focus management**: Focus ring visible, logical tab order
- [ ] **Error states**: Graceful degradation when data unavailable

## 4. Responsive Testing

| Breakpoint | Width | Check |
|-----------|-------|-------|
| Compact | <1280px | [ ] Bottom bar collapsed, rails icon-only |
| Standard | 1280-1920px | [ ] Default layout, rails 280px |
| Wide | 1920-2560px | [ ] Rails expand, grids add columns |
| Ultrawide | >2560px | [ ] Rails 420px, canvas splits possible |

## 5. Severity Classification

| Finding | Severity | Action |
|---------|----------|--------|
| Canon law violation | **BLOCKER** | Must fix before merge |
| Accessibility failure | **BLOCKER** | Must fix before merge |
| Missing dataStatus prop | **Critical** | Fix in this PR |
| Hardcoded colors | **Major** | Fix in this PR |
| Missing micro-interaction | **Minor** | Can defer |
| Suboptimal spacing | **Minor** | Can defer |
