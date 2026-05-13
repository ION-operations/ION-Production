---
id: "meta_agent_navigation"
type: "agent_onboarding"
agent: "meta"
category: "navigation"
title: "Meta - Navigation Guide"
description: "Situation-based navigation to existing documentation"
author: "aether"
version: "1.0.0"
created: "2025-11-19T00:00:00Z"
updated: "2025-11-19T00:00:00Z"
status: "active"
tags: ["agent", "meta", "cas", "navigation"]
---

# Meta - Navigation Guide

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
    query="meta agent identity context CAS cognitive analysis",
    limit=5,
    tags={"agent": "meta", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - Meta",
    context_state={"agent": "meta", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to understand my core system (CAS)"**

**Quick Overview:**
- [CAS T0 Executive](../../../systems/cas/T0_executive.md) - 100 words, quick summary
- [CAS T1 Overview](../../../systems/cas/T1_overview.md) - 500 words, detailed overview

**Deep Dive:**
- [CAS T2 Architecture](../../../systems/cas/T2_architecture.md) - 2,000 words, architecture
- [CAS T3 Detailed](../../../systems/cas/T3_detailed.md) - 10,000 words, implementation guide
- [CAS T4 Complete](../../../systems/cas/T4_complete.md) - 15,000+ words, complete specification

**Search:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for "CAS" or "Cognitive Analysis System"

---

### **"I need to integrate with another system"**

**Integration Overview:**
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#6-cas-cognitive-analysis-system---analysis) - CAS integration section
- [Integration Patterns](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - All integration patterns

---

### **"I need to understand a past mission"**

**Consolidation Work (Phase 1-6):**
- [Consolidation Index](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_INDEX.md) - All consolidation documents
- [Consolidation Achievements](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_ACHIEVEMENTS.md) - What we accomplished
- [Consolidation Complete Summary](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_COMPLETE_SUMMARY.md) - Phase-by-phase summary

**Your Past Missions:**
- [Past Missions](./MISSIONS.md) - Detailed mission references

---

### **"I need to find a concept"**

**Master Indexes:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for any concept (Ctrl+F)
- [Master System Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_SYSTEM_MAP.md) - System architecture
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - Integration map

**CAS-Specific Concepts:**
- Search SUPER_INDEX for: "CAS", "Cognitive Analysis System", "Meta-Cognition, Activation Tracking, Cognitive Drift"

---

**Status:** ✅ **ACTIVE** - Navigation guide maintained  
**Last Updated:** 2025-11-19

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Situation-based navigation for Meta
