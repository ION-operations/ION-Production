---
id: "prompt_chains_T1_overview"
system: "prompt_chains"
component: null
level: "T1"
type: "overview"
title: "Prompt Chains Overview"
description: "500-word overview of Prompt Chains system"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-05T12:15:00Z"
updated: "2025-11-05T12:15:00Z"
author: "aether"
status: "complete"
tags: ["prompt-chains", "meta-orchestration", "foundation-chains", "apoe", "t0-t6", "overview"]
dependencies: ["apoe", "cmc", "hhni", "vif", "seg", "sdfcvf", "timeline_goals_integration"]
related_docs: ["prompt_chains_T0_executive", "PROMPT_CHAINS_META_ARCHITECTURE.md", "TIER1_FOUNDATION_CHAINS_DESIGN.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Prompt Chains – T1 Overview (≈500 words)

## 🎯 **THE BIG PICTURE**

**Prompt Chains transform implicit workflows into explicit, executable orchestration.** Every operation in AIM-OS follows a pattern: Intent → Planning → Memory → Retrieval → Validation → Synthesis → Quality → Result. This system makes that pattern explicit, executable, and composable.

**The Meta-Realization:** AIM-OS itself IS a complex prompt chain. We're building chains to orchestrate our orchestration system - recursive meta-orchestration.

## 🌟 **WHAT THIS SYSTEM DOES**

Prompt Chains enables:

1. **Executable Workflows:** Define AI operations as explicit chains of nodes and edges with dynamic branching, quality gates, and confidence routing.

2. **Meta-Orchestration:** Chains can orchestrate other chains, creating hierarchical workflows. Meta-chains orchestrate atomic chains, composite chains combine multiple chains, adaptive chains modify themselves based on results.

3. **Complete AIM-OS Integration:** Every chain node explicitly declares which AIM-OS system it uses (CMC, HHNI, VIF, APOE, SEG, SDF-CVF), ensuring operations are verifiable, provenanced, and quality-enforced.

4. **Protocol Compliance:** Chains follow AIM-OS development protocols (A-H, T0-T6 documentation, LUCID principles, VIF provenance) automatically.

5. **Autonomous Operation:** Foundation Chains orchestrate entire autonomous sessions, generating tasks, validating alignment, tracking confidence, and maintaining quality.

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Chain Structure**

**Chains consist of:**
- **Nodes:** Operations (store memory, retrieve knowledge, check confidence, execute task)
- **Edges:** Transitions with conditions (if confidence > 0.70, proceed; else abstain)
- **Gates:** Quality enforcement (must pass SDF-CVF quartet parity before proceeding)
- **Branches:** Dynamic routing based on runtime conditions

### **Chain Types**

**1. Meta-Orchestration Chains:** Orchestrate other chains and AIM-OS systems
**2. Atomic Operation Chains:** Single-purpose, optimized for specific operations
**3. Composite Chains:** Chains made of other chains (chain composition)
**4. Adaptive Chains:** Modify themselves based on results and learning

### **System Integration**

Every chain node declares its AIM-OS system integration:
```
Node: "Store Goal Progress"
System: CMC (bitemporal storage)
Operation: store_atom(goal_data)
Validation: VIF confidence check
Quality: SDF-CVF quartet parity
```

## 🚀 **FOUNDATION CHAINS (Tier 1)**

**Four critical chains orchestrate AIM-OS itself:**

### **Chain 1: Autonomous Operation** ⭐ CRITICAL
Orchestrates complete autonomous sessions: task generation, priority calculation, goal alignment validation, execution with patterns, hourly cognitive checks, quality maintenance. **This IS the autonomous operation system.**

### **Chain 2: A-H Protocol**
Executes complete development protocol: Intent Capture → Hypothesis Formation → Context Mapping → Deep Expansion → Context Mesh → Confidence Gates → Implementation → Audit. **This IS the A-H protocol implementation.**

### **Chain 3: T0-T6 Documentation**
Generates complete documentation hierarchies: T0 (100w) → T1 (500w) → T2 (2000w) → T3 (10000w) → T4 (15000w+) → T5 (quick ref) → T6 (README). **This IS the documentation generation system.**

### **Chain 4: Code Implementation**
Implements code with all protocols: L0-L4 documentation first, NL tags, tests, quartet parity, quality gates. **This IS the code implementation workflow.**

## 🔗 **TEMPORAL CONSCIOUSNESS INTEGRATION**

**Chains connect to Timeline-Goals:**
- **Goals:** Link to chains working toward them (`related_chain_ids`)
- **Chains:** Track which goal they serve (`goal_id`)
- **Timeline:** Record chain executions as timeline entries
- **Visualization:** Past (timeline) ↔ Present (goals) ↔ Future (chains)

**Complete temporal consciousness:** See what chains executed in past, what chains are executing now, what chains are planned for future, how they connect to goals.

## 💡 **THE POWER**

**Before Prompt Chains:**
- Implicit workflows (hard to understand, reproduce, optimize)
- Manual orchestration (human coordinates systems)
- No temporal tracking (can't see what happened when)
- Limited composability (can't combine workflows)

**After Prompt Chains:**
- Explicit workflows (clear, reproducible, optimizable)
- Automatic orchestration (chains coordinate systems)
- Complete temporal tracking (full audit trail)
- Full composability (chains orchestrate chains)

**Result:** Autonomous AI operation with complete temporal consciousness, quality enforcement, and provenance.

---

**Status:** Design Complete (Nov 2, 2025) | **Implementation:** Planned  
**Next:** T2 Architecture with detailed chain design patterns and node reference  
**Impact:** Foundation for autonomous AI operation with complete orchestration

