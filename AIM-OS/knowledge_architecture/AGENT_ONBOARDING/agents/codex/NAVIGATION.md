---
id: "codex_agent_navigation"
type: "agent_onboarding"
agent: "codex"
category: "navigation"
title: "Codex - Navigation Guide"
description: "Situation-based navigation to existing documentation"
author: "aether"
version: "1.0.0"
created: "2025-11-19T00:00:00Z"
updated: "2025-11-19T00:00:00Z"
status: "active"
tags: ["agent", "codex", "chat", "navigation"]
---

# Codex - Navigation Guide

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
    query="codex agent identity context chat conversation",
    limit=5,
    tags={"agent": "codex", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - Codex",
    context_state={"agent": "codex", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to understand my core system (Chat)"**

**Quick Overview:**
- [Chat T0 Executive](../../../systems/chat/T0_executive.md) - 100 words, quick summary
- [Chat T1 Overview](../../../systems/chat/T1_overview.md) - 500 words, detailed overview

**Deep Dive:**
- [Chat T2 Architecture](../../../systems/chat/T2_architecture.md) - 2,000 words, architecture
- [Chat T3 Detailed](../../../systems/chat/T3_detailed.md) - 10,000 words, implementation guide
- [Chat T4 Complete](../../../systems/chat/T4_complete.md) - 15,000+ words, complete specification

**Search:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for "Chat" or "Chat/IDE"

---

### **"I need to integrate with another system"**

**Integration Overview:**
- [Master Integration Map](../../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md#ide-ui-integration-systems) - Chat integration section
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

**Chat-Specific Concepts:**
- Search SUPER_INDEX for: "Chat", "Chat/IDE", "Chat Architecture, Message Handling, Context Management"

---

**Status:** ✅ **ACTIVE** - Navigation guide maintained  
**Last Updated:** 2025-11-19

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Situation-based navigation for Codex
