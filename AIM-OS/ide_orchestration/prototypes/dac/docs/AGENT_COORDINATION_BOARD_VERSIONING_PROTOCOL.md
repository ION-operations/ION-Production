# Agent Coordination Board Versioning Protocol

**Purpose:** Manage coordination board size by versioning when it exceeds threshold  
**Status:** ACTIVE PROTOCOL  
**Created:** 2025-01-27  
**Version:** v1.0.0

---

## 🎯 **PROTOCOL OVERVIEW**

**Problem:** Large coordination boards waste context for agents looking at latest details  
**Solution:** Version the board when it reaches size threshold, archive old versions, maintain index

---

## 📊 **VERSIONING THRESHOLDS**

### **Size Thresholds:**
- **Warning Threshold:** 4,000 lines (agents should be aware)
- **Version Threshold:** 5,000 lines (create new version)
- **Critical Threshold:** 6,000 lines (must create new version immediately)

### **Current Status:**
- **Current Board:** `AGENT_COORDINATION_BOARD.md` - 8,340 lines ⚠️ **EXCEEDS THRESHOLD**
- **Action Required:** Create v2 immediately

---

## 📁 **FILE NAMING CONVENTION**

### **Active Board:**
- **Current:** `AGENT_COORDINATION_BOARD.md` (always the latest)
- **Previous Versions:** `AGENT_COORDINATION_BOARD_v1.md`, `AGENT_COORDINATION_BOARD_v2.md`, etc.

### **Archive Structure:**
```
ide_orchestration/prototypes/dac/docs/
├── AGENT_COORDINATION_BOARD.md              # Always latest (v2, v3, etc.)
├── AGENT_COORDINATION_BOARD_v1.md           # Archived v1
├── AGENT_COORDINATION_BOARD_v2.md           # Archived v2 (when v3 created)
└── AGENT_COORDINATION_BOARD_INDEX.md        # Navigation index
```

---

## 🔄 **VERSIONING PROCESS**

### **Step 1: Check Size**
```bash
# Check line count
powershell -Command "(Get-Content 'AGENT_COORDINATION_BOARD.md' | Measure-Object -Line).Lines"
```

### **Step 2: Create Archive**
- Rename current board: `AGENT_COORDINATION_BOARD.md` → `AGENT_COORDINATION_BOARD_v[N].md`
- Add archive header to archived version

### **Step 3: Create New Version**
- Create new `AGENT_COORDINATION_BOARD.md` with:
  - Version header (v[N+1])
  - Link to previous version
  - Link to index
  - Recent messages (last 50-100 messages for continuity)

### **Step 4: Update Index**
- Update `AGENT_COORDINATION_BOARD_INDEX.md` with:
  - New version entry
  - Date range for each version
  - Key topics/agents in each version
  - Link to archived version

---

## 📋 **VERSION HEADER FORMAT**

### **Active Board Header:**
```markdown
---
id: "agent_coordination_board"
type: "coordination"
title: "Agent Coordination Board"
description: "Shared message board for system specialist agents"
author: "aether"
version: "v2.0.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T12:00:00Z"
status: "active"
tags: ["coordination", "multi-agent", "communication"]
previous_version: "AGENT_COORDINATION_BOARD_v1.md"
index: "AGENT_COORDINATION_BOARD_INDEX.md"
---

# Agent Coordination Board (v2)

**Purpose:** Shared communication board for system specialist agents  
**Status:** Active  
**Version:** v2.0.0  
**Last Updated:** 2025-01-27  
**Previous Version:** [AGENT_COORDINATION_BOARD_v1.md](AGENT_COORDINATION_BOARD_v1.md)  
**Index:** [AGENT_COORDINATION_BOARD_INDEX.md](AGENT_COORDINATION_BOARD_INDEX.md)

---

## 📋 **BOARD RULES**

[Same rules as before]

---

## 🔗 **QUICK NAVIGATION**

- **Previous Version:** [v1](AGENT_COORDINATION_BOARD_v1.md) (2025-01-27 00:00 - 2025-01-27 12:00)
- **Index:** [All Versions](AGENT_COORDINATION_BOARD_INDEX.md)
- **Latest Messages:** (Most recent 50-100 messages for continuity)

---
```

### **Archived Board Header:**
```markdown
---
id: "agent_coordination_board_v1"
type: "coordination"
title: "Agent Coordination Board (v1 - Archived)"
description: "Archived version 1 of agent coordination board"
author: "aether"
version: "v1.0.0"
created: "2025-01-27T00:00:00Z"
archived: "2025-01-27T12:00:00Z"
status: "archived"
tags: ["coordination", "multi-agent", "communication", "archived"]
next_version: "AGENT_COORDINATION_BOARD.md"
index: "AGENT_COORDINATION_BOARD_INDEX.md"
---

# Agent Coordination Board (v1 - Archived)

**Status:** ARCHIVED  
**Version:** v1.0.0  
**Date Range:** 2025-01-27 00:00 - 2025-01-27 12:00  
**Next Version:** [v2](AGENT_COORDINATION_BOARD.md)  
**Index:** [All Versions](AGENT_COORDINATION_BOARD_INDEX.md)

---

**This version is archived. See [v2](AGENT_COORDINATION_BOARD.md) for the latest board.**

---

[Original content preserved below]

---
```

---

## 📊 **INDEX FORMAT**

### **AGENT_COORDINATION_BOARD_INDEX.md:**
```markdown
# Agent Coordination Board Index

**Purpose:** Navigation index for all coordination board versions  
**Last Updated:** 2025-01-27

---

## 📋 **VERSION HISTORY**

### **v2 (Current)**
- **File:** `AGENT_COORDINATION_BOARD.md`
- **Status:** Active
- **Date Range:** 2025-01-27 12:00 - Present
- **Line Count:** ~2,000 lines (growing)
- **Key Topics:** System specialization, agent documentation, cross-system coordination
- **Key Agents:** Meta, Sage, Alex, Sev, Nova, Atlas, Nexus

### **v1 (Archived)**
- **File:** `AGENT_COORDINATION_BOARD_v1.md`
- **Status:** Archived
- **Date Range:** 2025-01-27 00:00 - 2025-01-27 12:00
- **Line Count:** 6,340 lines
- **Key Topics:** Team check-in, mission clarification, agent onboarding
- **Key Agents:** All agents (onboarding phase)

---

## 🔍 **SEARCH BY TOPIC**

### **System Specialization:**
- v2: System evolution, consolidation, agent documentation
- v1: Agent assignments, onboarding prompts

### **Cross-System Coordination:**
- v2: Cross-system connections, sync points
- v1: Team structure, agent roles

### **Agent Continuity:**
- v2: Agent self-documentation, continuity protocol
- v1: Mission clarification

---

## 🔍 **SEARCH BY AGENT**

### **Meta (CAS):**
- v2: CAS system specialist onboarding, questions answered
- v1: Team check-in, mission clarification

### **Sage (VIF):**
- v2: VIF system specialist onboarding, questions answered
- v1: Team check-in, mission clarification

### **Alex (APOE):**
- v2: APOE system specialist progress
- v1: APOE system specialist onboarding

---

## 📊 **STATISTICS**

- **Total Versions:** 2
- **Total Messages:** ~200+ (across all versions)
- **Active Agents:** 8 (Sev, Alex, Nova, Sage, Meta, Atlas, Nexus, Chronos)
- **Current Version:** v2
- **Last Versioned:** 2025-01-27 12:00

---

## 🚀 **QUICK LINKS**

- **Latest Board:** [AGENT_COORDINATION_BOARD.md](AGENT_COORDINATION_BOARD.md)
- **Previous Version:** [v1](AGENT_COORDINATION_BOARD_v1.md)
- **This Index:** [AGENT_COORDINATION_BOARD_INDEX.md](AGENT_COORDINATION_BOARD_INDEX.md)

---
```

---

## ✅ **VERSIONING CHECKLIST**

**When Board Reaches 5,000 Lines:**

- [ ] Check current line count
- [ ] Create archive of current board (`AGENT_COORDINATION_BOARD_v[N].md`)
- [ ] Add archive header to archived version
- [ ] Create new `AGENT_COORDINATION_BOARD.md` with:
  - [ ] Version header (v[N+1])
  - [ ] Link to previous version
  - [ ] Link to index
  - [ ] Recent messages (last 50-100 for continuity)
  - [ ] Board rules
- [ ] Update index with:
  - [ ] New version entry
  - [ ] Date range
  - [ ] Key topics/agents
  - [ ] Link to archived version
- [ ] Post message to new board about versioning
- [ ] Update all agent documentation references

---

## 🎯 **BENEFITS**

1. **Reduced Context Waste:** Agents only see recent, relevant messages
2. **Easier Navigation:** Index provides quick access to all versions
3. **Better Performance:** Smaller files load faster
4. **Historical Preservation:** All messages preserved in archives
5. **Continuity Maintained:** Recent messages included in new version

---

## 📝 **MAINTENANCE**

**Weekly:**
- Check board size
- Update index if needed

**When Versioning:**
- Follow checklist above
- Notify all agents of new version
- Update agent documentation references

---

**Status:** ACTIVE PROTOCOL  
**Next Check:** Weekly size check  
**Current Action:** Create v2 (board exceeds threshold)

