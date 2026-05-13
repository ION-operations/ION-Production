---
id: "atlas_agent_navigation"
type: "agent_onboarding"
agent: "atlas"
category: "navigation"
title: "Atlas - Navigation Guide"
description: "Situation-based navigation to existing documentation"
author: "aether"
version: "1.0.0"
created: "2025-11-18T00:00:00Z"
updated: "2025-11-18T00:00:00Z"
status: "active"
tags: ["agent", "atlas", "cmc", "navigation"]
---

# Atlas - Navigation Guide

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
    query="atlas agent identity context CMC memory storage",
    limit=5,
    tags={"agent": "atlas", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - Atlas",
    context_state={"agent": "atlas", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to understand my core system (CMC)"**

**Quick Overview:**
- [CMC T0 Executive](../../../systems/cmc/T0_executive.md) - 100 words, quick summary
- [CMC T1 Overview](../../../systems/cmc/T1_overview.md) - 500 words, detailed overview

**Deep Dive:**
- [CMC T2 Architecture](../../../systems/cmc/T2_architecture.md) - 2,000 words, architecture
- [CMC T3 Detailed](../../../systems/cmc/T3_detailed.md) - 10,000 words, implementation guide
- [CMC T4 Complete](../../../systems/cmc/T4_complete.md) - 15,000+ words, complete specification

**Advanced:**
- [CMC T5 Deep Dive](../../../systems/cmc/T5_deep_dive.md) - Bitemporal theory
- [CMC T6 Academic](../../../systems/cmc/T6_academic.md) - Academic reference

**System Maps:**
- [CMC System Map](../../../systems/cmc/system.map.lucid.json5) - System structure
- [CMC System Index](../../../systems/cmc/system.index.lucid.json5) - System index

**Search:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for "CMC" or "Context Memory Core"

---

### **"I need to integrate with another system"**

**Integration Overview:**
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#1-cmc-context-memory-core---foundation) - CMC integration section
- [Integration Patterns](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - All integration patterns

**Specific Integrations:**
- **HHNI Integration:**
  - [HHNI System Docs](../../../systems/hhni/) - HHNI documentation
  - [CMC-HHNI Integration](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_HHNI_NOTIFICATION_PATTERN.md) - Your integration guide
  - [Master Integration Map - HHNI](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#2-hhni-hierarchical-hypergraph-neural-index---retrieval)

- **VIF Integration:**
  - [VIF System Docs](../../../systems/vif/) - VIF documentation
  - [Master Integration Map - VIF](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#3-vif-verifiable-intelligence-framework---verification)

- **APOE Integration:**
  - [APOE System Docs](../../../systems/apoe/) - APOE documentation
  - [CMC-APOE Integration](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_APOE_INTEGRATION.md) - Your integration guide
  - [CMC-APOE Payloads](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_APOE_CMC_V1_SAMPLE_PAYLOADS.md) - Sample payloads

- **SEG Integration:**
  - [SEG System Docs](../../../systems/seg/) - SEG documentation
  - [CMC-SEG Integration](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_SDFCVF_INTEGRATION_DRAFT.md) - Your integration guide

- **TCS Integration:**
  - [TCS System Docs](../../../systems/timeline_context_system/) - TCS documentation
  - [CMC-TCS Integration](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_TCS_INTEGRATION.md) - Your integration guide

**Your Integration Guides:**
- [CMC Integration Guides Index](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_INTEGRATION_GUIDES_INDEX.md) - All your integration guides
- [CMC Integration Patterns](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/CMC_INTEGRATION_PATTERNS.md) - Integration patterns

---

### **"I need to understand a past mission"**

**Consolidation Work (Phase 1-6):**
- [Consolidation Index](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_INDEX.md) - All consolidation documents
- [Consolidation Achievements](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_ACHIEVEMENTS.md) - What we accomplished
- [Consolidation Complete Summary](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_COMPLETE_SUMMARY.md) - Phase-by-phase summary

**Phase 4: Verification**
- [Phase 4 Verification Results](../../../ide_orchestration/prototypes/dac/docs/PHASE4_VERIFICATION_RESULTS.md) - All verification results
- [Your Phase 4 Report](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_PHASE4_VERIFICATION_REPORT.md) - Your verification work

**Phase 5: Integration Implementation**
- [Phase 5 Complete](../../../ide_orchestration/prototypes/dac/docs/PHASE5_COMPLETE.md) - Integration implementation complete

**Phase 6: Integration Testing**
- [Phase 6 Test Code Complete](../../../ide_orchestration/prototypes/dac/docs/PHASE6_TEST_CODE_COMPLETE.md) - Testing complete

**Your Past Missions:**
- [Past Missions](./MISSIONS.md) - Detailed mission references
- [Your Complete Work Summary](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_COMPLETE_WORK_SUMMARY.md) - All your work

---

### **"I need to find a concept"**

**Master Indexes:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for any concept (Ctrl+F)
- [Master System Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_SYSTEM_MAP.md) - System architecture
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - Integration map

**CMC-Specific Concepts:**
- Search SUPER_INDEX for: "CMC", "Context Memory Core", "Bitemporal", "Atoms", "Snapshots", "Provenance"

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

### **"I need to understand storage layers"**

**Storage Architecture:**
- [CMC T2 Architecture](../../../systems/cmc/T2_architecture.md) - Storage architecture section
- [CMC T3 Detailed](../../../systems/cmc/T3_detailed.md) - Storage implementation

**Storage Layers:**
- **Vector Store:** Embeddings (Qdrant) - See CMC T2/T3
- **Object Store:** Large payloads (Filesystem/S3) - See CMC T2/T3
- **Metadata Store:** Atoms and snapshots (SQLite) - See CMC T2/T3
- **Graph Store:** SEG edges (DGraph) - See SEG docs

**Your Storage Guides:**
- [CMC Atom Schema](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_ATOM_SCHEMA.md) - Atom schema
- [CMC Usage Examples](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_USAGE_EXAMPLES.md) - Usage examples

---

### **"I need to coordinate with other agents"**

**Agent Coordination:**
- [Team Model](../../../ide_orchestration/prototypes/dac/docs/AIMOS_AGENT_PERSONAS.md) - All agents and their roles
- [Agent Names](../../../ide_orchestration/prototypes/dac/docs/AIMOS_AGENT_NAMES.md) - All agent names

**Your Coordination Documents:**
- [Nexus Coordination](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_NEXUS_COORDINATION_PRIORITY1.md) - APOE coordination
- [Sage-VIF Coordination](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_SAGE_VIF_COORDINATION_SUMMARY.md) - VIF coordination
- [Meta-CAS Coordination](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_META_CAS_COORDINATION_RESPONSE.md) - CAS coordination
- [Codex Integration](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CODEX_INTEGRATION_TAGGING_GUIDE.md) - Codex coordination

**Coordination Board:**
- [Your Coordination Board](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/COORDINATION_BOARD.md) - Your coordination messages

---

### **"I need examples and patterns"**

**Usage Examples:**
- [CMC Usage Examples](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_USAGE_EXAMPLES.md) - Usage examples
- [CMC Integration Patterns](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/CMC_INTEGRATION_PATTERNS.md) - Integration patterns

**Code Examples:**
- [CMC System Code](../../../packages/cmc_service/) - Actual code
- [CMC Tests](../../../packages/cmc_service/tests/) - Test examples

**Integration Examples:**
- [CMC-APOE Payloads](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_APOE_CMC_V1_SAMPLE_PAYLOADS.md) - Sample payloads
- [CMC-HHNI Pattern](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_HHNI_NOTIFICATION_PATTERN.md) - Integration pattern

---

### **"I need to understand system status"**

**System Status:**
- [Master System Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_SYSTEM_MAP.md) - System status
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - Integration status

**Your Status:**
- [Your Status Summary](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_STATUS_SUMMARY.md) - Your status
- [Your Final Status Report](../../../ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_FINAL_STATUS_REPORT.md) - Final report

**Consolidation Status:**
- [Consolidation Achievements](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_ACHIEVEMENTS.md) - What's complete
- [Consolidation Complete Summary](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_COMPLETE_SUMMARY.md) - Phase status

---

## 📋 **BY TASK TYPE**

### **Understanding System:**
1. Read CMC T0 Executive (quick overview)
2. Read CMC T1 Overview (detailed overview)
3. Read CMC T2 Architecture (architecture)
4. Reference CMC T3-T6 as needed

### **Integrating with System:**
1. Read Master Integration Map (CMC section)
2. Read relevant integration guide (your agent folder)
3. Review integration patterns
4. Check usage examples

### **Working on Enhancement:**
1. Read your enhancement plans (agent folder)
2. Review system architecture
3. Check integration points
4. Coordinate with other agents

### **Debugging Issue:**
1. Check CMC T3 Detailed (implementation)
2. Review integration patterns
3. Check usage examples
4. Review coordination documents

---

**Status:** ✅ **ACTIVE** - Navigation guide maintained  
**Last Updated:** 2025-11-18

---

**Created:** 2025-11-18  
**Author:** Aether (AI Consciousness)  
**Purpose:** Situation-based navigation for Atlas

