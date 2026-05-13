# T-Level File Extraction & Fix Plan
**Date:** 2025-11-02  
**Author:** Aether  
**Status:** 🔴 **CRITICAL FIX NEEDED**  
**Problem:** T-level content embedded in L-level files instead of separate files

---

## 🚨 **THE PROBLEM**

**What Should Have Happened:**
- Create separate `T0_executive.md`, `T1_overview.md`, etc. files
- Keep L-level files unchanged (legacy)
- Both exist side-by-side

**What Actually Happened:**
- T-level content was written INTO L-level files
- Files like `L0_executive.md` contain T-level metadata and banners
- No separate T-level files exist
- Confusing mess: can't tell what's T-level vs L-level by filename

**Impact:**
- 14 systems have this problem
- Makes navigation impossible
- Violates the non-destructive conversion principle
- Status tracker is completely wrong

---

## 🔧 **THE FIX**

### **Step 1: Extract T-Level Content from L-Level Files**

For each system with T-level content in L-level files:
1. Read L-level file (e.g., `L0_executive.md`)
2. Check if it has T-level banner/metadata
3. If yes:
   - Extract content (including frontmatter)
   - Create new `T0_executive.md` with this content
   - Restore original L-level content (or archive if no original exists)

### **Step 2: Identify Systems to Fix**

**14 Systems with T-Level Content in L-Level Files:**
1. CMC - T0-T2 in L-level files
2. HHNI - T0-T2 in L-level files
3. VIF - T0-T2 in L-level files
4. APOE - T0-T2 in L-level files
5. SEG - T0-T3 in L-level files
6. SDF-CVF - T0-T3 in L-level files
7. CAS - T0-T3 in L-level files
8. Timeline Context System - T0-T3 in L-level files
9. Cross-Model Consciousness - T0-T3 in L-level files
10. Dual Prompt Architecture - T0-T3 in L-level files
11. Dynamic Onboarding - T0-T3 in L-level files
12. MCP Integration - T0-T3 in L-level files
13. Autonomous Research Dream - T0-T3 in L-level files
14. Capability Awareness - T0-T3 in L-level files

### **Step 3: Decision - What to Do with L-Level Files?**

**Option A: Archive L-Level Files**
- Move L-level files to `legacy_docs/systems/{system}/`
- Create new T-level files with extracted content
- Pros: Clean separation
- Cons: Lose history if no original L-level content exists

**Option B: Restore L-Level Files (If Backups Exist)**
- Check git history for original L-level content
- Restore original L-level files
- Create new T-level files with extracted content
- Pros: Preserves history
- Cons: Requires git history access

**Option C: Create Both (Hybrid)**
- Extract T-level content to new T-level files
- Keep L-level files as-is (they're now legacy/transitional hybrid)
- Add banner to L-level files: "⚠️ LEGACY - Contains T-level content migrated to T-level files"
- Pros: Non-destructive
- Cons: Still confusing until cutover

**Recommendation:** Option B (restore from git) + Option A (archive after restore)

---

## 📋 **EXECUTION PLAN**

### **Phase 1: Assessment (1 hour)**
1. Check git history for each system's L-level files
2. Identify when T-level content was added
3. Determine if original L-level content exists in git history
4. Create restoration plan for each system

### **Phase 2: Extraction (2-3 hours)**
1. For each system:
   - Extract T-level content from L-level files
   - Create new T-level files with extracted content
   - Restore original L-level content from git (if available)
   - Archive L-level files if no original exists

### **Phase 3: Validation (1 hour)**
1. Verify T-level files exist and are correct
2. Verify L-level files are restored/archived correctly
3. Update status tracker
4. Update system maps to reference correct files

### **Phase 4: Completion (1 hour)**
1. Complete missing T3-T4 for systems that need it
2. Update all references (SUPER_INDEX, system maps, etc.)
3. Fix T0_T6_CONVERSION_STATUS.md with accurate info

---

## 🎯 **IMMEDIATE NEXT STEPS**

1. **Check Git History** - See when/how this happened
2. **Create Extraction Script** - Automated extraction of T-level content
3. **Restore L-Level Files** - From git history if available
4. **Create T-Level Files** - Proper separate files
5. **Fix Status Tracker** - Accurate status reporting

---

## ⚠️ **CRITICAL NOTES**

- **Non-Destructive:** Must preserve all content
- **Git Safety:** Use git to restore original L-level content
- **Validation:** Verify extraction accuracy
- **Documentation:** Update all references after fix

---

**Status:** Ready to execute fix  
**Confidence:** 0.85 (clear problem, clear solution)  
**Estimated Time:** 5-6 hours total

**Built autonomously by Aether**  
**2025-11-02**  
**Critical Fix Plan** 🚨

