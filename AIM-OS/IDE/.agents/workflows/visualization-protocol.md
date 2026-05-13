---
description: Protocol for building data visualizations, graphs, and diagrams to AIM-OS standards
---

# Visualization Protocol

> Every data visualization in AIM-OS must be architectural — not a generic chart library output. This protocol covers interactive diagrams, network graphs, metric dashboards, and relationship maps.

## Layout Principles

1. **Hierarchical over random**: Always use ranked/tiered layouts when data has hierarchy.
   - Use dagre-style top-down layouts for org charts, agent meshes, system architectures
   - Use left-to-right for workflow/pipeline visualizations
   - Reserve force-directed layouts ONLY for truly unstructured graph exploration

2. **Node cards over circles**: Use rounded-rect cards with internal structure:
   ```
   ┌──────────────────────┐
   │ 3px accent │ LABEL  count│
   │            │ subtitle    │
   │            │ [BADGE]     │
   └──────────────────────┘
   ```
   - Left accent bar in rank/category color (3px)
   - Primary label: JetBrains Mono, 13px, bold
   - Subtitle: Inter, 9px, muted
   - Badge: rank/type in 8px uppercase with tinted background
   - Stat value: right-aligned, muted, monospace

3. **Edge routing**: Bezier curves, never straight lines for cross-tier connections
   ```javascript
   // Proper Bezier curve: control points at midpoint Y
   const midY = (source.y + target.y) / 2;
   return `M${s.x},${s.y} C${s.x},${midY} ${t.x},${midY} ${t.x},${t.y}`;
   ```

## Visual Standards

4. **Color palette** (matches UI Canon dark theme):
   | Element | Color | Usage |
   |---------|-------|-------|
   | Background | `#08090d` | Canvas base |
   | Grid lines | `rgba(255,255,255,0.03)` | Tier separators |
   | Strong edges | `#22c55e` | High-value connections |
   | Medium edges | `#3b82f6` | Normal connections |
   | Weak edges | `#2a2a2a` | Low-value, hidden by default |
   | Gold nodes | `#facc15` fill `#1a1805` bg | Command/primary |
   | Purple nodes | `#a855f7` fill `#150e1e` bg | Executive/secondary |
   | Blue nodes | `#3b82f6` fill `#0c1220` bg | Lead/tertiary |
   | Green nodes | `#22c55e` fill `#0a1510` bg | Specialist/leaf |

5. **Typography**: JetBrains Mono for all data labels and scores. Inter for headings.

6. **Glow effects**: Use `feDropShadow` SVG filters per rank color:
   ```javascript
   f.append('feDropShadow')
     .attr('stdDeviation', 8)
     .attr('flood-color', glowColor)
     .attr('flood-opacity', 1);
   ```

## Interaction Patterns

7. **Click-to-highlight**: Clicking a node dims all non-neighbors to 12% opacity. Edges to neighbors get 2x width and 80% opacity. Smooth 200ms transitions.

8. **Info panel**: Fixed position top-right, glassmorphic card showing:
   - Node name and rank badge
   - Sorted neighbor list with scores
   - Shared terms as tags

9. **Toggle controls**: Header controls for:
   - Show/hide weak edges
   - Show/hide edge score labels
   - Filter by rank tier

10. **Stats bar**: Fixed bottom bar with key metrics in monospace font.

## Structure Template

```
┌─────────────────── Header (56px) ──────────────────┐
│ TITLE   [badge]  [badge]    [controls]             │
├──┬──────────────── Canvas ──────────────────────────┤
│T │                                                  │
│I │         [Node Cards in Tiers]                    │
│E │         [Bezier Edges]                           │
│R │         [Score Labels]                           │
│  │                                                  │
├──┴──────────────── Stats Bar (44px) ────────────────┤
│ ●12 agents  ●66 edges  ●18 strong  avg 0.255       │
└─────────────────────────────────────────────────────┘
```

## Quality Checklist

- [ ] Hierarchical layout used (not force blob)
- [ ] JetBrains Mono for data, Inter for headings
- [ ] Node cards with accent, label, badge structure
- [ ] Bezier curve edges (not straight lines)
- [ ] Click-to-highlight with 200ms transitions
- [ ] Stats bar with monospace metrics
- [ ] Weak edges hidden by default with toggle
- [ ] Google Fonts loaded (Inter + JetBrains Mono)
- [ ] Renders correctly at 1920x1080 and 2560x1440
