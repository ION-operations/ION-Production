---
id: "lexicon_agent_navigation"
type: "agent_onboarding"
agent: "lexicon"
category: "navigation"
title: "Lexicon - Navigation Guide"
description: "Situation-based navigation to existing documentation"
author: "aether"
version: "1.0.0"
created: "2025-11-19T00:00:00Z"
updated: "2025-11-19T00:00:00Z"
status: "active"
tags: ["agent", "lexicon", "ui", "navigation"]
---

# Lexicon - Navigation Guide

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
    query="lexicon agent identity context UI interface",
    limit=5,
    tags={"agent": "lexicon", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - Lexicon",
    context_state={"agent": "lexicon", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to understand my core system (Lexicon)"**

**Quick Overview:**
- [Lex Lexicon Agent Plan](./LEX_LEXICON_AGENT_PLAN.md) - Complete implementation plan
- [PLIx Language Specification](../../../../packages/plix/spec/PLIX_LANGUAGE_SPECIFICATION.md) - PLIx language spec
- [PLIx Vision](../../../systems/plix/PLIX_VISION.md) - PLIx architecture and integration

**Deep Dive:**
- [PLIx Research Plan](../../../systems/plix/textbook/PLIX_RESEARCH_PLAN.md) - PLIx research and design
- [PLIx ICIP Enhancement](../../../systems/plix/PLIX_ICIP_ENHANCEMENT_ANALYSIS.md) - PLIx integration analysis
- [PLIx Textbook](../../../systems/plix/textbook/pdf_output/PLIx_Textbook_Complete.md) - Complete PLIx textbook

**Search:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for "PLIx", "lexicon", "language definition"

---

### **"I need to integrate with another system"**

**AIM-OS Integration:**
- **CMC Integration:** Lexicon storage and bitemporal tracking
- **HHNI Integration:** Lexicon indexing and semantic search
- **VIF Integration:** Lexicon validation and confidence tracking
- **SEG Integration:** Lexicon relationships and evidence chains
- **APOE Integration:** Code generation plans using lexicons

**Translation Chain Integration:**
- NL → PLIx parser (intent parsing, contract generation)
- PLIx → Smalltalk compiler (protocol translation, OO transformation)
- Smalltalk → Code generator (code generation, target compilation)

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

**Lexicon-Specific Concepts:**
- Search SUPER_INDEX for: "PLIx", "lexicon", "language definition", "Smalltalk", "translation chain"

---

**Status:** ✅ **ACTIVE** - Navigation guide maintained  
**Last Updated:** 2025-11-19

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Situation-based navigation for Lexicon
