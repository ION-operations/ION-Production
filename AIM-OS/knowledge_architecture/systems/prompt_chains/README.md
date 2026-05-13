# Prompt Chains System

**Purpose:** Executable workflows for AI operations through meta-orchestration  
**Status:** Design Complete (Nov 2, 2025), Implementation Planned  
**Foundation Chains:** 4 designed (Autonomous Operation, A-H Protocol, T0-T6 Documentation, Code Implementation)  

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

Prompt Chains transforms implicit AI workflows into **explicit, executable orchestration graphs**. Every operation in AIM-OS follows a pattern (Intent → Planning → Memory → Retrieval → Validation → Synthesis → Quality → Result) - this system makes that pattern explicit, executable, and composable.

**The Meta-Realization:** AIM-OS itself IS a complex prompt chain. We're building chains to orchestrate our orchestration system - recursive meta-orchestration.

---

## ⚡ Quick Start

```python
from packages.prompt_chains.executor.chain_executor import ChainExecutor
from packages.prompt_chains.models.prompt_chain import PromptChain
import yaml

# Load Foundation Chain (Autonomous Operation)
with open('chains/autonomous_operation.yaml') as f:
    chain_data = yaml.safe_load(f)

chain = PromptChain.from_dict(chain_data)

# Execute chain
executor = ChainExecutor()
result = executor.execute_chain(
    chain=chain,
    context={'session_type': 'autonomous', 'max_duration_hours': 6}
)

# Result: Complete autonomous session with task execution, quality gates, confidence routing
```

---

## 🔑 Key Features

### Meta-Orchestration
Chains orchestrate other chains, creating hierarchical workflows:
- **Meta-Chains:** Orchestrate atomic chains
- **Composite Chains:** Combine multiple chains
- **Adaptive Chains:** Self-modify based on results

### Complete AIM-OS Integration
Every chain node explicitly declares which system it uses:
- **CMC:** Memory operations (store, retrieve)
- **HHNI:** Semantic search and retrieval
- **VIF:** Confidence tracking and gating
- **APOE:** Planning and orchestration
- **SEG:** Knowledge synthesis
- **SDF-CVF:** Quality enforcement

### Temporal Consciousness Integration
Bidirectional linkage with goals:
- Goals track `related_chain_ids` (chains working toward them)
- Chains track `goal_id` (goal they serve)
- Timeline records chain executions as timeline entries
- Complete Past (Timeline) ↔ Present (Goals) ↔ Future (Chains) graph

### Dynamic Routing
Chains route based on runtime conditions:
- **Confidence gates:** Proceed only if confidence ≥ threshold
- **Quality gates:** Proceed only if quartet parity ≥ 0.90
- **Result-based:** Route based on operation results
- **Custom conditions:** Any Python expression

---

## 📊 System Status

**Design Status:**
- ✅ Complete meta-architecture (Nov 2, 2025)
- ✅ All 4 Foundation Chains designed
- ✅ Data models complete (PromptChain, ChainNode, ChainEdge)
- ✅ ChainExecutor architecture designed
- ✅ Complete T0-T6 documentation

**Implementation Status:**
- ⏳ Data models - Planned
- ⏳ ChainExecutor - Planned
- ⏳ Foundation Chains - Planned (implementation ready)
- ⏳ System integration - Planned (patterns defined)

**Documentation Status:**
- ✅ T0 Executive (100 words)
- ✅ T1 Overview (500 words)
- ✅ T2 Architecture (2,000 words)
- ✅ T3 Detailed (10,000 words)
- ✅ T4 Complete (15,000+ words)
- ✅ T5 Quick Reference (500 words)
- ✅ README (this file)

**Files:**
- `models/prompt_chain.py` (Designed - 400+ lines)
- `executor/chain_executor.py` (Designed - 300+ lines)
- `chains/*.yaml` (4 Foundation Chains designed)

---

## 🚀 Foundation Chains (Tier 1)

### Chain 1: Autonomous Operation ⭐ CRITICAL
**Purpose:** Orchestrates complete autonomous sessions  
**Flow:** Session Init → Task Generation → Selection → Alignment Check → Execution → Cognitive Check → Loop  
**Systems:** CMC, APOE, VIF, SDF-CVF, CAS  
**Why Critical:** This IS the autonomous operation system itself  

### Chain 2: A-H Protocol ⭐ CRITICAL
**Purpose:** Executes A-H development protocol  
**Flow:** A: Intent → B: Hypothesis → C: Context → D: Expansion → E: Mesh → F: Gates → G: Implementation → H: Audit  
**Systems:** All (complete AIM-OS integration)  
**Why Critical:** This IS the development protocol implementation  

### Chain 3: T0-T6 Documentation ⭐ CRITICAL
**Purpose:** Generates complete documentation hierarchies  
**Flow:** System Analysis → T0 (100w) → T1 (500w) → T2 (2000w) → T3 (10000w) → T4 (15000w) → T5 → README  
**Why Critical:** This IS the documentation generation system  

### Chain 4: Code Implementation ⭐ CRITICAL
**Purpose:** Implements code with all AIM-OS protocols  
**Flow:** L0-L4 Docs First → Implement+Tags → Tests → Quartet Parity → Run Tests → Commit  
**Why Critical:** This IS the code implementation workflow  

---

## 🔗 Integration Points

**Timeline Context System:**
- Chain executions stored as timeline entries
- Temporal tracking of all chain operations

**Goal Timeline Integration:**
- Bidirectional chain-goal linkage
- Automatic goal progress updates
- `related_chain_ids` / `goal_id` connections

**APOE (Planning):**
- Meta-chains use APOE for task generation
- Dynamic sub-chain selection
- Plan compilation from intent

**VIF (Confidence):**
- All decisions check confidence thresholds
- Automatic abstention when confidence low
- Confidence tracking throughout execution

**SDF-CVF (Quality):**
- Quality gates at critical points
- Quartet parity enforcement
- Quality-based routing

---

## 📚 Related Systems

- **[APOE](../apoe/README.md)** - Planning and orchestration (chains use APOE)
- **[Timeline-Goals Integration](../timeline_goals_integration/README.md)** - Bidirectional chain-goal linkage
- **[CMC](../cmc/README.md)** - Chain execution storage
- **[VIF](../vif/README.md)** - Confidence gating
- **[SDF-CVF](../sdfcvf/README.md)** - Quality enforcement

---

## 🎯 Next Steps

**For New Users:**
1. Read [T0 Executive](T0_executive.md) for instant understanding
2. Read [T5 Quick Reference](T5_quick_reference.md) for API overview
3. Try the Quick Start code example above
4. Read [T3 Detailed](T3_detailed.md) when ready to implement

**For Implementation:**
1. Review [T3 Detailed](T3_detailed.md) - Complete implementation guide
2. Review existing design documents in `knowledge_architecture/applications/ide_chat_app/`
3. Implement data models (PromptChain, ChainNode, ChainEdge)
4. Implement ChainExecutor engine
5. Create 4 Foundation Chains
6. Test with real autonomous session

**For Enhancement:**
1. Read [T4 Complete](T4_complete.md) - Future enhancements
2. Consider Tier 2 chains (extended functionality)
3. Consider visualization layer
4. Consider chain library/marketplace

---

**Implementation:** Design Complete (Nov 2, 2025)  
**Documentation:** Complete T0-T6  
**Status:** Ready for implementation

