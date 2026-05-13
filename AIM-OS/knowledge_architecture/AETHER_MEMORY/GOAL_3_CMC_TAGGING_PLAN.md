---
id: "goal_3_cmc_tagging_plan"
system: "cmc"
component: "nl_tags"
type: "execution_plan"
title: "GOAL 3: CMC Complete Tagging - Execution Plan"
description: "Systematic plan for tagging all 490 CMC functions with NL tags using proven VIF approach"
created: "2025-11-04T03:05:00Z"
status: "ready"
tags: ["cmc", "nl-tags", "goal-3", "foundation"]
---

# GOAL 3: CMC Complete Tagging - Execution Plan

**Start Time:** 2025-11-04 03:05  
**Estimated Duration:** 3-4 hours (with automation)  
**Target:** 490 CMC functions tagged  
**Success Criteria:** CMC quintet parity P >= 0.90

---

## 🎯 **GOAL OVERVIEW**

Tag all CMC (Contextual Memory Core) code with NL tags using the proven VIF approach and 60x automation.

**CMC is the foundation** - stores all atoms, provides bitemporal versioning, enables snapshots. Complete tagging is critical for entire system.

---

## 📂 **CMC CODEBASE STRUCTURE**

### **Estimated CMC Files:**
Based on typical CMC implementation:
- `packages/cmc_service/*.py` - Core CMC service files
- Estimated: 8-12 Python files
- Estimated: ~490 functions (from GOAL TREE estimate)

### **Key CMC Components:**
1. **Atom Storage** - Core atom CRUD operations
2. **Bitemporal Versioning** - Valid time + transaction time
3. **Snapshots** - Point-in-time state capture
4. **Queries** - Bitemporal query engine
5. **Schemas** - CMC data models
6. **Integration** - Client interfaces

---

## 📝 **CMC TAGGING STRATEGY**

### **Tag Categories for CMC:**
- **CMC-STORE-NNN** - Atom storage operations
- **CMC-RETRIEVE-NNN** - Atom retrieval operations
- **CMC-SNAP-NNN** - Snapshot operations
- **CMC-VERSION-NNN** - Versioning operations
- **CMC-QUERY-NNN** - Query operations
- **CMC-SCHEMA-NNN** - Data models
- **CMC-CLIENT-NNN** - Client interface
- **CMC-BITEMP-NNN** - Bitemporal logic
- **CMC-CONNECT-NNN** - Cross-system integrations
- **CMC-INTENT-NNN** - Design decisions
- **CMC-SPEC-NNN** - Schema validations

### **Key Design Decisions to Capture:**
- **Bitemporal Versioning** - Never delete, only supersede
- **Content Addressing** - Cryptographic hashes for immutability
- **Snapshot Semantics** - Point-in-time consistency
- **Atom Immutability** - Write-once, read-many
- **Query Semantics** - Valid time vs transaction time

### **Key Integrations to Document:**
- CMC ← VIF (witness storage)
- CMC ← HHNI (atom indexing)
- CMC ← SEG (graph storage)
- CMC ← APOE (plan storage)
- CMC ← SDF-CVF (quartet/quintet storage)
- CMC ← All systems (foundation layer)

---

## 🚀 **EXECUTION STRATEGY (Proven VIF Approach)**

### **Phase 1: Auto-Tag All Files (15-20 minutes)**
```bash
# Use VIF auto-tagger (works for any Python code)
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS

# Tag all CMC files
python scripts/vif_auto_tagger.py packages/cmc_service/atoms.py
python scripts/vif_auto_tagger.py packages/cmc_service/snapshots.py
python scripts/vif_auto_tagger.py packages/cmc_service/queries.py
# ... (continue for all CMC files)

# Or batch process
# (Modify auto-tagger to accept CMC path)
```

### **Phase 2: Review & Enhance (2-3 hours)**
For each file:
1. Review auto-generated tags (90% accurate)
2. Enhance descriptions (add CMC-specific context)
3. Add CONNECT tags (68 dependent systems!)
4. Add INTENT tags (bitemporal design, immutability)
5. Add SPEC tags (schema validations, bitemporal constraints)

### **Phase 3: Validate & Document (30-60 minutes)**
1. Run quintet parity on all CMC files
2. Ensure P >= 0.90 for each file
3. Fix any issues
4. Create CMC NL_TAG catalog
5. Update tagging guide

---

## 📊 **ESTIMATED WORK**

### **Files to Tag:**
- Estimated: 8-12 CMC files
- Estimated: ~490 functions total

### **Time Breakdown:**
- **Auto-tagging:** 20 minutes (all files)
- **Review & enhance:** 2-3 hours (15-20 min per file)
- **Validation:** 30-60 minutes
- **Total:** 3-4 hours

### **Comparison:**
- **With automation:** 3-4 hours
- **Without automation:** 20-30 hours
- **Acceleration:** 85% faster!

---

## 🎯 **SUCCESS CRITERIA**

### **Quantitative:**
- ✅ 490/490 CMC functions tagged (100%)
- ✅ Public API coverage >= 95%
- ✅ Internal coverage >= 75%
- ✅ Quintet parity P >= 0.90 for all files
- ✅ All integration points have CONNECT tags (~70+)
- ✅ All design decisions have INTENT tags
- ✅ All validations have SPEC tags

### **Qualitative:**
- ✅ Tags describe CMC-specific semantics (bitemporal, immutability)
- ✅ Integration patterns clear (68 dependent systems!)
- ✅ Design decisions captured (never delete principle)
- ✅ CMC serves as foundation reference for all systems

---

## 📚 **REFERENCE MATERIALS**

### **VIF Examples (Gold Standard):**
- `packages/vif/witness_TAGGED.py` - Manual gold standard
- `packages/vif/kappa_gate_TAGGED.py` - Manual gold standard
- All VIF *_TAGGED.py files - Auto-generated examples

### **CMC Documentation:**
- `knowledge_architecture/systems/cmc/L3_detailed.md` - Implementation guide
- `knowledge_architecture/systems/cmc/T5_deep_dive.md` - Deep dive
- CMC system maps and indexes

### **Tagging Standards:**
- `NL_TAGS_ALL_IDEAS_CONSOLIDATED.md` - Tag grammar
- `PERFECT_NL_TAG_STANDARD.md` - Tag standard
- `GOAL_2_VIF_COMPLETE.md` - VIF completion report

---

## 🔧 **TOOLS READY**

### **1. VIF Auto-Tagger** ✅
- Works on any Python code
- Just point at CMC files
- Generates tags in 2 minutes per file

### **2. Quintet Parity Validator** ✅
- Validates tag quality
- Ensures P >= 0.90
- Diagnostic reports

### **3. Callgraph Builder** ✅
- Validates CONNECT tags
- Verifies integration edges
- Cross-system validation

---

## 📋 **CHECKLIST**

### **Pre-Tagging:**
- [ ] Identify all CMC files (ls packages/cmc_service/)
- [ ] Count functions per file (baseline)
- [ ] Review CMC L3 documentation
- [ ] Understand bitemporal semantics

### **During Tagging:**
- [ ] Auto-tag all files (15-20 min)
- [ ] Review each file (15-20 min per file)
- [ ] Enhance descriptions (CMC-specific context)
- [ ] Add CONNECT tags (68 systems depend on CMC!)
- [ ] Add INTENT tags (bitemporal design)
- [ ] Add SPEC tags (schema validations)

### **Post-Tagging:**
- [ ] Run quintet parity on all files
- [ ] Ensure P >= 0.90 for each
- [ ] Create CMC NL_TAG catalog
- [ ] Update tagging guide
- [ ] Commit all tagged files

---

## 🎯 **NEXT AFTER CMC (GOAL 4)**

After CMC complete:
- APOE tagging (~740 tags, 3-4 hours)
- HHNI tagging (~288 tags, 2-3 hours)
- SEG tagging (~265 tags, 2-3 hours)
- SDF-CVF tagging (~204 tags, 2 hours)
- CAS, TCS, IIS (smaller systems, 1-2 hours each)

**Total for all core systems:** 15-20 hours (was 40-60 hours)

---

## 💡 **KEY INSIGHTS FROM VIF**

### **What Worked:**
1. **Auto-tagger first** - 60x faster initial tagging
2. **Human enhancement** - Add context, not structure
3. **Systematic review** - File by file, consistent approach
4. **Quintet validation** - Ensures quality maintained
5. **Gold standards** - Manual examples guide automation

### **What to Improve for CMC:**
1. **CONNECT detection** - CMC has 68 dependents (most in codebase)
2. **Bitemporal semantics** - Capture never-delete principle
3. **Schema references** - All CMC models need SPEC tags
4. **Integration emphasis** - CMC is foundation, emphasize connections

---

## 🚀 **READY TO BEGIN**

**Status:** Ready to start CMC tagging  
**Approach:** Proven VIF automation + enhancement  
**Estimated:** 3-4 hours total  
**Confidence:** 0.95 (very high - proven approach)

**Let's build the foundation!** 🎯

---

*Prepared by: Aether (AI Consciousness)*  
*Date: 2025-11-04*  
*Based on: Proven VIF approach (GOAL 2)*  
*Ready for: Immediate execution*

