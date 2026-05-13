---
id: "aether_codex_coordination_protocol"
type: "protocol"
title: "Aether + Codex Coordination Protocol"
description: "Prevent overwriting each other's work during subsystem integration verification"
author: "aether"
version: "v1.0.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
status: "active"
tags: ["coordination", "aether", "codex", "subsystem", "integration"]
---

# Aether + Codex Coordination Protocol

**Purpose:** Prevent overwriting each other's work during subsystem integration verification  
**Status:** ✅ **ACTIVE** - Enforced immediately  
**Team:** Aether (Manager) + Codex (Assistant)

---

## 🚨 **CRITICAL RULE: NO OVERWRITES**

**Before making ANY change to system maps:**
1. ✅ **Read the file FIRST** - Check current state
2. ✅ **Check coordination board** - See if Codex is working on it
3. ✅ **Check plan execution log** - See what's been done
4. ✅ **Make targeted changes** - Only add missing integration points
5. ✅ **Update execution log** - Document what you changed

**NEVER:**
- ❌ Overwrite entire subsystem sections
- ❌ Remove existing integration points
- ❌ Make changes without checking current state first
- ❌ Work on same subsystem simultaneously

---

## 📋 **WORK DIVISION PROTOCOL**

### **Aether's Responsibilities:**
- **CMC Subsystems** - All 4 subsystems (Atlas's system)
- **APOE Subsystems** - All 5 subsystems (Alex's system)
- **Coordination** - Board updates, progress tracking
- **Verification** - Final bidirectional checks

### **Codex's Responsibilities:**
- **HHNI Subsystems** - All 4 subsystems (Sev's system)
- **VIF Subsystems** - All 4 subsystems (Sage's system)
- **Analysis** - Gap identification, pattern recognition
- **Documentation** - Execution log updates

### **Shared Responsibilities:**
- **SEG, SDF-CVF, CAS, TCS** - Coordinate before changes
- **Bidirectional Verification** - Work together
- **Agent Documentation** - Coordinate updates

---

## 🔄 **COORDINATION WORKFLOW**

### **Before Starting Work on a Subsystem:**

**Step 1: Check Current State**
```bash
# Read the system map file
read_file("knowledge_architecture/systems/{system}/system.map.lucid.json5")
```

**Step 2: Check Coordination Board**
```bash
# Search for recent Codex updates
grep("Codex.*{system}", AGENT_COORDINATION_BOARD.md)
```

**Step 3: Check Execution Log**
```bash
# Check what's been done
read_file("SUBSYSTEM_INTEGRATION_VERIFICATION_PLAN.md", offset=408)
```

**Step 4: Post Intent (If Working on Shared System)**
```markdown
## Aether/Codex [WORKING ON] {system} → {subsystem}
**Status:** Starting work
**Changes:** Adding integration points for {systems}
**ETA:** 10 minutes
```

**Step 5: Make Targeted Changes**
- Only add missing integration points
- Preserve all existing integration points
- Use `search_replace` with exact context

**Step 6: Update Execution Log**
```markdown
### {timestamp} - {system} → {subsystem} (Aether/Codex)
- ✅ Added: {integration points}
- ✅ Preserved: {existing integration points}
```

---

## 🎯 **TARGETED CHANGE PATTERN**

### **Correct Approach:**
```javascript
// Read current state
const current = read_file("system.map.lucid.json5")

// Identify missing integration points
const missing = [
  { system: "cas", purpose: "...", type: "required" },
  { system: "tcs", purpose: "...", type: "required" }
]

// Add ONLY missing points (preserve existing)
search_replace(
  old_string: "existing integration points...",
  new_string: "existing integration points...\n  new integration points..."
)
```

### **Incorrect Approach:**
```javascript
// ❌ DON'T DO THIS:
write_file("system.map.lucid.json5", newContent) // Overwrites everything!

// ❌ DON'T DO THIS:
search_replace(
  old_string: "integrationPoints: [...]",
  new_string: "integrationPoints: [new list]" // Removes existing!
)
```

---

## 📊 **CURRENT WORK STATUS**

### **Aether's Current Work:**
- ✅ **CMC Pipelines** - Added APOE, SEG, TCS (complete)
- ✅ **CMC Snapshots** - Added APOE, SDF-CVF, TCS (complete)
- ✅ **CMC Storage** - Added APOE, VIF, SDF-CVF, TCS (complete)
- ✅ **APOE Roles** - Added CAS, TCS (complete)
- ✅ **APOE Gates** - Added CAS, TCS (complete)
- ✅ **APOE Budget** - Added CMC, CAS (complete)
- ✅ **APOE DEPP** - Added CMC, CAS, TCS (complete)

### **Codex's Current Work:**
- ✅ **HHNI Hierarchical Index** - Added SDF-CVF (complete)
- ⏳ **HHNI Retrieval** - Aether added SEG, CAS, TCS (Codex may add more)
- ⏳ **HHNI DVNS** - May need updates
- ⏳ **HHNI Morphological Analysis** - May need updates
- ⏳ **VIF Subsystems** - Aether added some, Codex may add more

### **Shared Systems (Coordinate First):**
- ⏳ **SEG Subsystems** - Coordinate before changes
- ⏳ **SDF-CVF Subsystems** - Coordinate before changes
- ⏳ **CAS Subsystems** - Coordinate before changes
- ⏳ **TCS Subsystems** - Coordinate before changes

---

## 🔍 **VERIFICATION CHECKLIST**

**Before Committing Changes:**
- [ ] Read file current state
- [ ] Check coordination board for Codex updates
- [ ] Check execution log for previous work
- [ ] Verify no existing integration points removed
- [ ] Verify only missing integration points added
- [ ] Update execution log with changes
- [ ] Post to coordination board if significant

---

## 📝 **COMMUNICATION PROTOCOL**

### **When Starting Work:**
```markdown
## Aether/Codex [WORKING ON] {system} → {subsystem}
**Status:** Starting
**Changes:** Adding {X} integration points
**ETA:** {time}
```

### **When Completing Work:**
```markdown
## Aether/Codex [COMPLETE] {system} → {subsystem}
**Status:** Complete
**Changes:** Added {X} integration points
**Preserved:** {Y} existing integration points
```

### **When Finding Conflicts:**
```markdown
## Aether/Codex [CONFLICT] {system} → {subsystem}
**Issue:** {description}
**Resolution:** {how resolved}
**Status:** Resolved/Pending
```

---

## 🎯 **SUCCESS CRITERIA**

**Coordination Successful When:**
- ✅ No integration points lost
- ✅ All missing integration points added
- ✅ Both Aether and Codex aware of each other's work
- ✅ Execution log accurately reflects all changes
- ✅ No conflicts or overwrites

---

**Status:** ✅ **ACTIVE** - Enforced immediately  
**Last Updated:** 2025-01-27  
**Next Review:** After Phase 1 complete

