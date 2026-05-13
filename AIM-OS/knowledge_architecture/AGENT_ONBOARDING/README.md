---
id: "agent_onboarding_master_index"
type: "onboarding_index"
title: "AIM-OS Agent Onboarding - Master Index"
description: "Lightweight agent-specific indexes that leverage existing comprehensive documentation"
author: "aether"
version: "1.0.0"
created: "2025-11-18T00:00:00Z"
updated: "2025-11-19T00:00:00Z"
status: "active"
authoritative: true
tags: ["onboarding", "agents", "master_index", "navigation"]
---

# AIM-OS Agent Onboarding - Master Index

**Purpose:** Lightweight agent-specific indexes that leverage existing comprehensive documentation  
**Status:** ✅ **COMPLETE** - All agents onboarded and integrated  
**Last Updated:** 2025-11-19

---

## 🎯 **PHILOSOPHY**

**We already have amazing documentation!** This system doesn't recreate it - it provides:
- ✅ Agent-specific indexes pointing to existing docs
- ✅ Agent context (timeline, keywords, important things)
- ✅ Situation-based navigation
- ✅ References to past missions and consolidation work

**Just 4 files per agent:** README, CONTEXT, NAVIGATION, MISSIONS

---

## 👥 **ALL AGENTS**

### **Core Infrastructure Agents (7):**
1. ✅ [Atlas](./agents/atlas/README.md) - CMC/Architect
2. ✅ [Sev](./agents/sev/README.md) - HHNI/Researcher
3. ✅ [Veritas](./agents/veritas/README.md) - VIF/Auditor
4. ✅ [Nexus](./agents/nexus/README.md) - APOE/Coordinator
5. ✅ [Sage](./agents/sage/README.md) - SEG/Synthesizer
6. ✅ [Meta](./agents/meta/README.md) - CAS/Introspector
7. ✅ [Chronos](./agents/chronos/README.md) - TCS/Historian

### **MVP Builder Agents (3):**
8. ✅ [Lexicon](./agents/lexicon/README.md) - UI Architect
9. ✅ [Codex](./agents/codex/README.md) - Chat Master
10. ✅ [Solo](./agents/solo/README.md) - Integration Specialist

### **Enhancement Agents (2):**
11. ✅ [Prism](./agents/prism/README.md) - Intuition/IIS
12. ✅ [Sentinel](./agents/sentinel/README.md) - Quality Gate/SDF-CVF

### **Future Agents (2):**
13. ✅ [Nova](./agents/nova/README.md) - Developer
14. ✅ [Echo](./agents/echo/README.md) - User Advocate

**Status:** ✅ **ALL 14 AGENTS COMPLETE**

---

## 📚 **WHAT EACH AGENT GETS**

Each agent has 4 files:

1. **[README.md](./agents/{agent}/README.md)** - Agent index (main entry point)
   - Who you are
   - Quick links to everything
   - Status and completion

2. **[CONTEXT.md](./agents/{agent}/CONTEXT.md)** - Agent-specific context
   - Timeline of key events
   - Keywords and important terms
   - Important things to know
   - Relationships with other agents

3. **[NAVIGATION.md](./agents/{agent}/NAVIGATION.md)** - Situation-based navigation
   - "I need to..." → Links to relevant docs
   - By task type, system, integration
   - Points to existing documentation

4. **[MISSIONS.md](./agents/{agent}/MISSIONS.md)** - Past missions reference
   - Consolidation work (Phase 1-6)
   - Agent-specific missions
   - Key deliverables
   - Lessons learned

---

## 🔗 **EXISTING DOCUMENTATION (What We Leverage)**

### **Master Documentation:**
- [SUPER_INDEX.md](../SUPER_INDEX.md) - Complete concept map
- [Consolidation Index](../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_INDEX.md) - All consolidation work
- [Master System Map](../../ide_orchestration/prototypes/dac/docs/MASTER_SYSTEM_MAP.md) - System architecture
- [Master Integration Map](../../ide_orchestration/prototypes/dac/docs/MASTER_INTEGRATION_MAP.md) - Integration map

### **System Documentation:**
- [System T0-T6 Docs](../systems/{system}/) - All system documentation
- [System Integration Docs](../systems/{system}/INTEGRATIONS.md) - Integration patterns

### **Agent Documentation:**
- [Agent Folders](../../ide_orchestration/prototypes/dac/docs/agents/{agent}/) - Existing agent files
- [Agent Reports](../../ide_orchestration/prototypes/dac/docs/agents/{agent}/*.md) - All agent documents

### **Consolidation Work:**
- [Phase 1-6 Documents](../../ide_orchestration/prototypes/dac/docs/PHASE*.md) - All phase documentation
- [Consolidation Achievements](../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_ACHIEVEMENTS.md) - What we accomplished

---

## 🚀 **GETTING STARTED**

### **If You're a New Agent:**
1. Read your agent's [README.md](./agents/{your_name}/README.md)
2. Read your agent's [CONTEXT.md](./agents/{your_name}/CONTEXT.md)
3. Use [NAVIGATION.md](./agents/{your_name}/NAVIGATION.md) to find relevant docs
4. Review [MISSIONS.md](./agents/{your_name}/MISSIONS.md) for past work

### **If You're Working on a Task:**
1. Use [NAVIGATION.md](./agents/{your_name}/NAVIGATION.md) - "I need to..."
2. Follow links to relevant existing documentation
3. Reference [CONTEXT.md](./agents/{your_name}/CONTEXT.md) for agent-specific context

### **If You Need to Understand Past Work:**
1. Read [MISSIONS.md](./agents/{your_name}/MISSIONS.md)
2. Follow links to consolidation documents
3. Review agent-specific deliverables

---

## 📊 **STATUS**

### **Completion Status:**
- **Master Index:** ✅ Complete
- **Templates:** ✅ Complete (4 templates created)
- **Core Agents:** ✅ Complete (7/7 - Atlas, Sev, Veritas, Nexus, Sage, Meta, Chronos)
- **MVP Agents:** ✅ Complete (3/3 - Lexicon, Codex, Solo)
- **Enhancement Agents:** ✅ Complete (2/2 - Prism, Sentinel)
- **Future Agents:** ✅ Complete (2/2 - Nova, Echo)
- **Cursor Integration:** ✅ Complete
- **API/LLM Integration:** ✅ Complete

**Total Files Created:** 63 files
- 56 agent onboarding files (14 agents × 4 files)
- 4 templates
- 2 integration docs
- 1 master index

---

## 🛠️ **MAINTENANCE & PROTOCOLS**

### **Maintenance Protocols:**
- [Maintenance Protocol](./MAINTENANCE_PROTOCOL.md) - How to keep onboarding up to date
- [Documentation Organization Protocol](./DOCUMENTATION_ORGANIZATION_PROTOCOL.md) - How to organize future docs
- [Quality Standards](./ONBOARDING_QUALITY_STANDARDS.md) - Quality checklist
- [Audit Report](./ONBOARDING_AUDIT_REPORT.md) - Latest audit findings

### **Maintenance Scripts:**
- [verify_onboarding_links.py](./scripts/verify_onboarding_links.py) - Verify all links work
- [update_agent_status.py](./scripts/update_agent_status.py) - Update agent status
- [consolidate_onboarding.py](./scripts/consolidate_onboarding.py) - Consolidate updates
- [audit_and_fix_onboarding.py](./scripts/audit_and_fix_onboarding.py) - Comprehensive audit and fix

### **Integration:**
- [Cursor Integration](../../.cursor/rules/agents/AGENT_ONBOARDING_INTEGRATION.md) - Cursor rules integration
- [API/LLM Integration](./API_LLM_INTEGRATION.md) - MCP tools, HHNI, SUPER_INDEX integration

---

## ✅ **QUALITY ASSURANCE**

### **Audit Status:**
- ✅ All agent files created
- ✅ All links verified (via audit script)
- ✅ System paths corrected
- ✅ Agent identity links fixed
- ✅ Verification report links fixed
- ✅ Integration anchors corrected

### **Quality Metrics:**
- **Broken Links:** 0 (verified)
- **Missing Files:** 0 (verified)
- **Incomplete Sections:** 0 (verified)
- **Format Consistency:** 100% (verified)

---

**Status:** ✅ **COMPLETE** - All agents onboarded, integrated, and audited  
**Last Updated:** 2025-11-19  
**See:** [COMPLETE.md](./COMPLETE.md) for completion summary

---

**Created:** 2025-11-18  
**Updated:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Lightweight agent onboarding that leverages existing documentation
