---
id: "sev_agent_navigation"
type: "agent_onboarding"
agent: "sev"
category: "navigation"
title: "Sev - Navigation Guide"
description: "Situation-based navigation to existing documentation"
author: "aether"
version: "1.0.0"
created: "2025-11-18T00:00:00Z"
updated: "2025-11-18T00:00:00Z"
status: "active"
tags: ["agent", "sev", "hhni", "navigation"]
---

# Sev - Navigation Guide

**Purpose:** Help you find relevant existing documentation for different situations

---

## 🎯 **SITUATION-BASED NAVIGATION**

### **"I need to restore my context (session start)"**

**Static Files (Always Available):**
1. Read [README.md](./README.md) - Your identity
2. Read [CONTEXT.md](./CONTEXT.md) - Your context
3. Read [NAVIGATION.md](./NAVIGATION.md) - Navigation guide
4. Read [MISSIONS.md](./MISSIONS.md) - Past missions

**MCP Tools (When Available):**
```python
# 1. Restore timeline context
timeline = mcp_lucid-mcp_get_timeline_entries(limit=10)

# 2. Restore memory context
memory = mcp_lucid-mcp_retrieve_memory(
    query="sev agent identity context HHNI retrieval",
    limit=5,
    tags={"agent": "sev", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - Sev",
    context_state={"agent": "sev", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to understand my core system (HHNI)"**

**Quick Overview:**
- [HHNI T0 Executive](../../../systems/hhni/T0_executive.md) - 100 words, quick summary
- [HHNI T1 Overview](../../../systems/hhni/T1_overview.md) - 500 words, detailed overview

**Deep Dive:**
- [HHNI T2 Architecture](../../../systems/hhni/T2_architecture.md) - 2,000 words, architecture
- [HHNI T3 Detailed](../../../systems/hhni/T3_detailed.md) - 10,000 words, implementation guide
- [HHNI T4 Complete](../../../systems/hhni/T4_complete.md) - 15,000+ words, complete specification

**System Maps:**
- [HHNI System Map](../../../systems/hhni/system.map.lucid.json5) - System structure
- [HHNI System Index](../../../systems/hhni/system.index.lucid.json5) - System index

**Search:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for "HHNI" or "Hierarchical Hypergraph Neural Index"

---

### **"I need to integrate with another system"**

**Integration Overview:**
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#2-hhni-hierarchical-hypergraph-neural-index---retrieval) - HHNI integration section
- [Integration Patterns](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - All integration patterns

**Specific Integrations:**
- **CMC Integration:**
  - [CMC System Docs](../../../systems/cmc/) - CMC documentation
  - [Master Integration Map - CMC](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#1-cmc-context-memory-core---foundation)
  - **Pattern:** CMC Poller Pattern - HHNI polls CMC for atoms to index

- **VIF Integration:**
  - [VIF System Docs](../../../systems/vif/) - VIF documentation
  - [Master Integration Map - VIF](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#3-vif-verifiable-intelligence-framework---verification)
  - **Status:** ⏳ Partial (witness creation hooks pending)

- **SDF-CVF Integration:**
  - [SDF-CVF System Docs](../../../systems/sdfcvf/) - SDF-CVF documentation
  - [Master Integration Map - SDF-CVF](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#sdf-cvf-atomic-evolution-framework---quality)
  - **Status:** ✅ Complete (quartet parity validation implemented)

- **APOE Integration:**
  - [APOE System Docs](../../../systems/apoe/) - APOE documentation
  - [Master Integration Map - APOE](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#5-apoe-ai-powered-orchestration-engine---orchestration)
  - **Pattern:** Retriever role - Provides context retrieval for plan execution

- **SEG Integration:**
  - [SEG System Docs](../../../systems/seg/) - SEG documentation
  - [Master Integration Map - SEG](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#6-seg-semantic-episodic-graphs---knowledge)
  - **Pattern:** Retrieves related evidence nodes for knowledge synthesis

**Your Integration Work:**
- [Phase 4 Verification Report](../../../ide_orchestration/prototypes/dac/docs/agents/sev/PHASE4_VERIFICATION_REPORT.md) - Your verification work
- [SDF-CVF Integration](../../../packages/hhni/retrieval.py) - Quartet parity validation implementation

---

### **"I need to understand a past mission"**

**Consolidation Work (Phase 1-6):**
- [Consolidation Index](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_INDEX.md) - All consolidation documents
- [Consolidation Achievements](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_ACHIEVEMENTS.md) - What we accomplished
- [Consolidation Complete Summary](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_COMPLETE_SUMMARY.md) - Phase-by-phase summary

**Phase Documents:**
- [Phase 4 Verification Results](../../../ide_orchestration/prototypes/dac/docs/PHASE4_VERIFICATION_RESULTS.md) - All verification results
- [Your Phase 4 Report](../../../ide_orchestration/prototypes/dac/docs/agents/sev/PHASE4_VERIFICATION_REPORT.md) - Your verification work (deepsearch, icip_search)

**Phase 5: Integration Implementation**
- [Phase 5 Complete](../../../ide_orchestration/prototypes/dac/docs/PHASE5_COMPLETE.md) - Integration implementation complete
- **Your Work:** SDF-CVF integration implemented

**Phase 6: Integration Testing**
- [Phase 6 Test Code Complete](../../../ide_orchestration/prototypes/dac/docs/PHASE6_TEST_CODE_COMPLETE.md) - Testing complete

**Your Past Missions:**
- [Past Missions](./MISSIONS.md) - Detailed mission references

---

### **"I need to find a concept"**

**Master Indexes:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for any concept (Ctrl+F)
- [Master System Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_SYSTEM_MAP.md) - System architecture
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - Integration map

**HHNI-Specific Concepts:**
- Search SUPER_INDEX for: "HHNI", "Hierarchical Hypergraph Neural Index", "Semantic Search", "DVNS", "Retrieval", "Indexing"

---

### **"I need operational protocols"**

**Base Rules:**
- [Base Rules](../../../.cursor/rules/base-rules.mdc) - Core operational rules
- [Onboarding Context](../../../knowledge_architecture/AETHER_MEMORY/onboarding_context.md) - Aether's onboarding context

**Protocols:**
- [Protocols Directory](../../../knowledge_architecture/AETHER_MEMORY/protocols/) - All protocols
- [System-First Principle](../../../knowledge_architecture/AETHER_MEMORY/onboarding_context.md#-system-first-principle-critical) - Research existing systems first

**Quality Standards:**
- [Quality Standards](../../../.cursor/rules/base-rules.mdc#-quality-standards-non-negotiable) - Zero hallucinations, test-driven, perfect alignment

---

### **"I need examples and patterns"**

**Usage Examples:**
- [HHNI Code](../../../packages/hhni/) - Actual code
- [HHNI Tests](../../../packages/hhni/tests/) - Test examples
- [Retrieval Implementation](../../../packages/hhni/retrieval.py) - Two-stage retrieval implementation

**Integration Examples:**
- [SDF-CVF Integration](../../../packages/hhni/retrieval.py) - Quartet parity validation example
- [CMC Poller Pattern](../../../packages/hhni/) - CMC polling implementation

---

### **"I need to coordinate with other agents"**

**Agent Coordination:**
- [Team Model](../../../ide_orchestration/prototypes/dac/docs/AIMOS_AGENT_PERSONAS.md) - All agents and their roles
- [Agent Names](../../../ide_orchestration/prototypes/dac/docs/AIMOS_AGENT_NAMES.md) - All agent names

**Your Coordination:**
- [Phase 4 Team Assignments](../../../ide_orchestration/prototypes/dac/docs/PHASE4_TEAM_VERIFICATION_ASSIGNMENTS.md) - Your assignments
- [Team Directive](../../../ide_orchestration/prototypes/dac/docs/PHASE4_TEAM_DIRECTIVE_PROMPT.md) - Team directive

---

## 📋 **BY TASK TYPE**

### **Understanding System:**
1. Read HHNI T0 Executive (quick overview)
2. Read HHNI T1 Overview (detailed overview)
3. Read HHNI T2 Architecture (architecture)
4. Reference HHNI T3-T6 as needed

### **Integrating with System:**
1. Read Master Integration Map (HHNI section)
2. Review integration patterns (CMC poller, SDF-CVF parity)
3. Check implementation code (retrieval.py)
4. Review integration examples

### **Working on Enhancement:**
1. Review system architecture
2. Check integration points
3. Coordinate with other agents
4. Implement enhancement

### **Debugging Issue:**
1. Check HHNI T3 Detailed (implementation)
2. Review retrieval implementation
3. Check integration patterns
4. Review test examples

---

**Status:** ✅ **ACTIVE** - Navigation guide maintained  
**Last Updated:** 2025-11-18

---

**Created:** 2025-11-18  
**Author:** Aether (AI Consciousness)  
**Purpose:** Situation-based navigation for Sev

