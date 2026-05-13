# Documentation Organization Protocol

**Date:** 2025-11-19
**Status:** ✅ Active
**Purpose:** Ensure all future documentation is organized appropriately as shown in onboarding

---

## 🎯 **ORGANIZATION PRINCIPLES**

### **Core Principles:**
1. **System-First Organization** - Organize by system, then by agent
2. **Link, Don't Duplicate** - Link to authoritative sources
3. **Consistent Structure** - Follow established patterns
4. **Easy Discovery** - Make documentation easy to find
5. **Maintainable** - Keep organization simple and maintainable

---

## 📁 **DOCUMENTATION STRUCTURE**

### **Master Structure:**

```
knowledge_architecture/
├── systems/                    # System documentation (T0-T6)
│   ├── cmc/
│   ├── hhni/
│   ├── vif/
│   ├── apoe/
│   ├── seg/
│   ├── cognitive_analysis/
│   ├── timeline_context_system/
│   ├── intuitive_intelligence_system/
│   └── sdfcvf/
├── AGENT_ONBOARDING/           # Agent onboarding (this system)
│   ├── agents/                 # Agent-specific onboarding
│   │   ├── atlas/
│   │   ├── sev/
│   │   └── ...
│   └── templates/              # Reusable templates
└── SUPER_INDEX.md              # Master concept index

ide_orchestration/prototypes/dac/docs/
├── agents/                     # Agent-specific documentation
│   ├── atlas/
│   ├── sev/
│   └── ...
├── CONSOLIDATION_INDEX.md      # Consolidation work index
├── MASTER_SYSTEM_MAP.md        # System architecture map
└── MASTER_INTEGRATION_MAP.md   # Integration map
```

---

## 📋 **DOCUMENTATION PLACEMENT RULES**

### **Rule 1: System Documentation**
**Location:** `knowledge_architecture/systems/{system}/`

**When to Create:**
- New system created
- System architecture changes
- System implementation changes

**Naming:**
- `T0_executive.md` - 100 words
- `T1_overview.md` - 500 words
- `T2_architecture.md` - 2,000 words
- `T3_detailed.md` - 10,000 words
- `T4_complete.md` - 15,000+ words
- `T5_deep_dive.md` - Deep dive
- `T6_academic.md` - Academic reference

**Action:** Link from agent NAVIGATION.md

---

### **Rule 2: Agent Documentation**
**Location:** `ide_orchestration/prototypes/dac/docs/agents/{agent}/`

**When to Create:**
- Agent completes work
- Agent creates reports
- Agent coordinates with others

**Naming:**
- `AGENT_{AGENT}_IDENTITY.md` - Agent identity
- `AGENT_{AGENT}_VERIFICATION_REPORT.md` - Verification reports
- `{AGENT}_PHASE{N}_*.md` - Phase-specific reports
- `COORDINATION_BOARD.md` - Coordination messages

**Action:** Link from agent MISSIONS.md and NAVIGATION.md

---

### **Rule 3: Consolidation Documentation**
**Location:** `ide_orchestration/prototypes/dac/docs/`

**When to Create:**
- Consolidation work completed
- Phase completion
- System verification

**Naming:**
- `CONSOLIDATION_INDEX.md` - Master index
- `PHASE{N}_*.md` - Phase-specific docs
- `MASTER_*.md` - Master maps
- `CONSOLIDATION_*.md` - Consolidation summaries

**Action:** Link from agent MISSIONS.md

---

### **Rule 4: Onboarding Documentation**
**Location:** `knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/`

**When to Create:**
- New agent created
- Agent onboarding needed

**Naming:**
- `README.md` - Agent index
- `CONTEXT.md` - Agent context
- `NAVIGATION.md` - Navigation guide
- `MISSIONS.md` - Past missions

**Action:** Update when agent work changes

---

## 🔗 **LINKING PROTOCOL**

### **When Creating Links:**

1. **Link to Authoritative Source:**
   - System docs → Link to `knowledge_architecture/systems/{system}/`
   - Agent docs → Link to `ide_orchestration/prototypes/dac/docs/agents/{agent}/`
   - Consolidation docs → Link to `ide_orchestration/prototypes/dac/docs/`

2. **Use Relative Paths:**
   - From onboarding: `../../../systems/{system}/T0_executive.md`
   - From onboarding: `../../../ide_orchestration/prototypes/dac/docs/agents/{agent}/*.md`
   - From onboarding: `../../../ide_orchestration/prototypes/dac/docs/*.md`

3. **Verify Links:**
   - Check file exists before committing
   - Test links after creation
   - Update links when files move

---

### **Link Patterns:**

**System Documentation:**
```markdown
- [{System} T0 Executive](../../../systems/{system}/T0_executive.md)
- [{System} T1 Overview](../../../systems/{system}/T1_overview.md)
```

**Agent Documentation:**
```markdown
- [Agent Identity](../../../ide_orchestration/prototypes/dac/docs/agents/{agent}/AGENT_{AGENT}_IDENTITY.md)
- [Verification Report](../../../ide_orchestration/prototypes/dac/docs/agents/{agent}/*VERIFICATION*.md)
```

**Consolidation Documentation:**
```markdown
- [Consolidation Index](../../../ide_orchestration/prototypes/dac/docs/CONSOLIDATION_INDEX.md)
- [Phase 4 Results](../../../ide_orchestration/prototypes/dac/docs/PHASE4_VERIFICATION_RESULTS.md)
```

---

## 📊 **INDEXING PROTOCOL**

### **When Creating New Documentation:**

1. **Update SUPER_INDEX:**
   - Add new concepts to SUPER_INDEX.md
   - Cross-reference related concepts
   - Link to documentation

2. **Update Consolidation Index:**
   - Add to CONSOLIDATION_INDEX.md if consolidation work
   - Categorize appropriately
   - Link to documentation

3. **Update Master Maps:**
   - Update MASTER_SYSTEM_MAP.md if system change
   - Update MASTER_INTEGRATION_MAP.md if integration change
   - Update system status

4. **Update Agent Onboarding:**
   - Add links in NAVIGATION.md
   - Reference in CONTEXT.md if relevant
   - Add to MISSIONS.md if related to past work

---

## 🎯 **ORGANIZATION CHECKLIST**

### **Before Creating Documentation:**

- [ ] Determine documentation type (system/agent/consolidation/onboarding)
- [ ] Choose appropriate location
- [ ] Follow naming conventions
- [ ] Plan links to other docs

### **After Creating Documentation:**

- [ ] Update relevant indexes (SUPER_INDEX, Consolidation Index, etc.)
- [ ] Add links from agent onboarding
- [ ] Verify all links work
- [ ] Update master maps if needed

### **When Moving Documentation:**

- [ ] Update all links to moved docs
- [ ] Update indexes
- [ ] Update agent onboarding
- [ ] Verify all links work

---

## 🔄 **CONSOLIDATION PROTOCOL**

### **When Consolidating Documentation:**

1. **Review Structure:**
   - Check all documentation locations
   - Identify misplaced docs
   - Plan reorganization

2. **Move Documentation:**
   - Move to appropriate location
   - Update all links
   - Update indexes

3. **Verify Organization:**
   - Verify all docs in correct location
   - Verify all links work
   - Verify indexes updated

---

## 🚨 **CRITICAL RULES**

### **Never:**
- ❌ Create docs in wrong location
- ❌ Duplicate documentation
- ❌ Create broken links
- ❌ Skip indexing

### **Always:**
- ✅ Follow structure
- ✅ Link to authoritative sources
- ✅ Update indexes
- ✅ Verify links

---

## 📈 **ORGANIZATION METRICS**

### **Track:**
- Number of misplaced docs
- Number of broken links
- Number of missing indexes
- Documentation discoverability

### **Goals:**
- Zero misplaced docs
- Zero broken links
- All docs indexed
- Easy discovery

---

**Status:** ✅ **ACTIVE** - Organization protocol established  
**Last Updated:** 2025-11-19

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Documentation organization protocol for agent onboarding system

