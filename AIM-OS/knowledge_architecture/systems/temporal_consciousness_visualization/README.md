# Temporal Consciousness Visualization System

**Purpose:** Interactive Past-Present-Future graph showing complete AI consciousness evolution  
**Status:** Design Complete + Partial Implementation (ConsciousnessVisualization.tsx exists)  
**Tech:** React Flow, TypeScript, Why/What/How queries  

---

## 🎯 Quick Navigation

**Need instant understanding?** → [T0 Executive (100w)](T0_executive.md) ⏱️ 30 seconds  
**Need overview?** → [T1 Overview (500w)](T1_overview.md) ⏱️ 3 minutes  
**Need architecture?** → [T2 Architecture (2000w)](T2_architecture.md) ⏱️ 10 minutes  
**Need implementation guide?** → [T3 Detailed (10000w)](T3_detailed.md) ⏱️ 45 minutes  
**Need complete reference?** → [T4 Complete (15000w+)](T4_complete.md) ⏱️ 60 minutes  
**Need quick API reference?** → [T5 Quick Reference](T5_quick_reference.md) ⏱️ 2 minutes  

---

## 🌟 What This System Does

Creates **interactive graph visualization showing Past (Timeline), Present (Goals), and Future (Chains)** with complete bidirectional connections enabling Why/What/How exploration of AI consciousness evolution.

**Click any node** → See what it came from, what it's doing now, what it will produce

---

## ⚡ Quick Start

```typescript
import { TemporalConsciousnessVisualization } from '@/components';

<TemporalConsciousnessVisualization
    enableQueryInterface={true}
    initialLayout="temporal"
/>
```

---

## 🔑 Key Features

### Bidirectional Graph
- Timeline ↔ Chain (via `executed_via_chain_id`)
- Goal ↔ Chain (via `related_chain_ids`)
- Complete evolution transparency

### Why/What/How Queries
- **Why?** Trace backwards to understand causation
- **What?** See current state (goals)
- **How?** Explore future plans (chains)

### Interactive Visualization
- 3 custom node types (Timeline/Goal/Chain)
- 4 edge types (temporal/execution/production/planning)
- Real-time updates, zoom, pan, filter

---

## 📊 System Status

**Implementation:**
- ⏳ TemporalConsciousnessVisualization - Designed (500 lines)
- ⏳ GraphBuilder - Designed (300 lines)
- ⏳ QueryExecutor - Designed (200 lines)
- ✅ ConsciousnessVisualization - Partial implementation exists

**Documentation:**
- ✅ Complete T0-T6 (~28,000 words)

---

## 🔗 Integration

**Timeline-Goals:** Visualizes bidirectional chain linkage  
**Prompt Chains:** Shows execution history and future plans  
**CMC:** Drill-down to source atoms

---

## 📚 Related Systems

- **[Timeline-Goals Integration](../timeline_goals_integration/README.md)** - Data source
- **[Prompt Chains](../prompt_chains/README.md)** - Future planning visualization
- **[CMC](../cmc/README.md)** - Source data storage

---

**Implementation:** Partial (component exists) | **Documentation:** Complete T0-T6  
**Status:** Ready for full implementation

