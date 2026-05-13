# Complete Reorganization Plan

**Date:** 2026-01-10  
**Status:** PLAN - AWAITING APPROVAL  
**Mission:** Reorganize entire project from chaos to manageable structure

---

## 🎯 **PLAN OVERVIEW**

This plan addresses all issues identified in the diagnostic report:
1. Fix git configuration
2. Consolidate duplicate folders
3. Archive/remove backup folders
4. Consolidate documentation (150+ indexes → 1 master index)
5. Organize root directory structure
6. Remove empty folders
7. Standardize naming conventions

**⚠️ CRITICAL: This plan requires approval before execution. NO CHANGES will be made until approved.**

---

## 📋 **PHASE 1: GIT CONFIGURATION FIX**

### **Problem:**
- `.gitignore` line 51: `Documentation/**` ignores entire Documentation folder
- `.gitignore` line 57: `Documentation/appexamples/` explicitly ignores appexamples
- Result: Nothing in `Documentation/appexamples/standalonewaves/` is tracked

### **Solution:**
1. **Remove or modify `.gitignore` lines 51 and 57:**
   - Option A: Remove `Documentation/**` and `Documentation/appexamples/` entirely
   - Option B: Make exceptions for active projects (e.g., `standalonewaves`)
   - Option C: Move active projects out of `Documentation/` folder

2. **Recommended Approach (Option C):**
   - Move `Documentation/appexamples/standalonewaves/` → `apps/standalonewaves/`
   - Keep `Documentation/` for legacy/archived docs only
   - Update `.gitignore` to only ignore archived docs

### **Files to Modify:**
- `.gitignore` (lines 51, 57, 114-116)

---

## 📋 **PHASE 2: ROOT DIRECTORY REORGANIZATION**

### **Current Problem:**
- 60+ root-level directories with no clear structure
- Apps, docs, backups, examples all mixed together

### **Proposed Structure:**
```
AIM-OS/
├── apps/                    # Active applications
│   ├── standalonewaves/
│   ├── lucidimage/
│   ├── gptwaves/
│   └── ...
├── examples/                # Example projects (read-only)
│   ├── canvas-chronicle/
│   ├── water-showcase-unified/
│   └── ...
├── archives/               # Archived/backup projects
│   ├── backups/
│   ├── legacy/
│   └── ...
├── docs/                    # Documentation (organized)
│   ├── knowledge_architecture/
│   ├── systems/
│   └── ...
├── packages/                # Reusable packages
├── tools/                   # Development tools
├── research/                # Research projects
└── root files...            # README, LICENSE, etc.
```

### **Migration Plan:**
1. **Create new structure:**
   - Create `apps/` folder
   - Create `examples/` folder
   - Create `archives/` folder
   - Create `docs/` folder (if needed)

2. **Move active apps to `apps/`:**
   - `standalonewaves/` → `apps/standalonewaves/`
   - `lucidimage/` → `apps/lucidimage/`
   - `gptwaves/` → `apps/gptwaves/`
   - Other active apps...

3. **Move examples to `examples/`:**
   - `canvas-chronicle/` → `examples/canvas-chronicle/`
   - `water-showcase-unified/` → `examples/water-showcase-unified/`
   - Other example projects...

4. **Move backups to `archives/backups/`:**
   - `standalonewaves_backup_*` → `archives/backups/standalonewaves_backup_*`
   - `LUCID-IDE-backup/` → `archives/backups/LUCID-IDE-backup/`
   - `FlowStateApp-Backup-*` → `archives/backups/FlowStateApp-Backup-*`
   - `Flag2_Complete_Package-*` → `archives/backups/Flag2_Complete_Package-*`
   - `apps\splash_backup_*` → `archives/backups/splash_backup_*`

5. **Move `00_Organized/` to `archives/organized/`:**
   - `00_Organized/` → `archives/organized/` (or analyze and split)

6. **Keep core folders in root:**
   - `packages/`
   - `knowledge_architecture/`
   - `cursor-addon/`
   - `ide_orchestration/`
   - `coordination/`
   - `goals/`
   - `audits/`
   - Root files (README.md, .gitignore, etc.)

---

## 📋 **PHASE 3: DUPLICATE FOLDER CONSOLIDATION**

### **Problem:**
- `water-showcase-unified` and `water-showcase-unified - Copy` (duplicate)
- Multiple canvas-related folders (6+ similar folders)

### **Solution:**
1. **Identify which is "current":**
   - Compare file modification dates
   - Check git history
   - Ask user if unclear

2. **Keep current, archive old:**
   - Keep `water-showcase-unified/` (if current)
   - Move `water-showcase-unified - Copy/` → `archives/backups/water-showcase-unified-copy/`

3. **Consolidate canvas folders:**
   - Analyze differences between canvas-* folders
   - Keep most current/complete version
   - Archive others to `archives/examples/canvas-*/`

---

## 📋 **PHASE 4: DOCUMENTATION CONSOLIDATION**

### **Problem:**
- 150+ index files with inconsistent naming
- 124 MAP files scattered throughout
- 6 SUPER_INDEX files
- 292 duplicate README.md files
- No central index

### **Solution:**
1. **Create single master index:**
   - Create `docs/MASTER_INDEX.md` at root
   - Consolidate all indexes into this single file
   - Organize by category:
     - Systems
     - Applications
     - Examples
     - Documentation
     - Tools
     - Research

2. **Archive old indexes:**
   - Move all old index files to `archives/docs/indexes/`
   - Keep only the master index active

3. **Consolidate MAP files:**
   - Create `docs/SYSTEM_MAPS/` folder
   - Move all MAP files here
   - Create `docs/SYSTEM_MAPS/MASTER_MAP_INDEX.md` to index all maps

4. **Consolidate SUPER_INDEX files:**
   - Keep only `knowledge_architecture/SUPER_INDEX.md` (most current)
   - Archive others to `archives/docs/super_indexes/`

5. **Handle duplicate README files:**
   - Keep README.md in each project folder (one per project)
   - Archive duplicate README.md files to `archives/docs/readmes/`
   - Update master index to point to active README files

---

## 📋 **PHASE 5: EMPTY FOLDER REMOVAL**

### **Problem:**
- `src/` - 0 files
- `standalonewaves_backup_2026-01-09_183140/` - 0 files
- `GPT-rigging-system/` - 0 files
- `image-editor-reviews/` - 0 files

### **Solution:**
1. **Verify empty:**
   - Double-check each folder is truly empty
   - Check for hidden files

2. **Remove empty folders:**
   - Delete `src/` (if truly empty)
   - Delete `standalonewaves_backup_2026-01-09_183140/` (empty backup)
   - Delete `GPT-rigging-system/` (if truly empty)
   - Delete `image-editor-reviews/` (if truly empty)

---

## 📋 **PHASE 6: NAMING STANDARDIZATION**

### **Problem:**
- Multiple naming conventions for same file types
- Case sensitivity issues

### **Solution:**
1. **Standardize index files:**
   - Use `INDEX.md` for all indexes (lowercase)
   - Or use `MASTER_INDEX.md` for master indexes
   - Remove variations like `_index.md`, `00-master-index.md`, etc.

2. **Standardize MAP files:**
   - Use `SYSTEM_MAP.md` for system maps
   - Use `INTEGRATION_MAP.md` for integration maps
   - Use `DEPENDENCY_MAP.md` for dependency maps

3. **Standardize documentation:**
   - Use consistent naming for T-level docs: `T0_executive.md`, `T1_overview.md`, etc.
   - Use consistent naming for phase reports: `PHASE1_COMPLETION_REPORT.md`, etc.

---

## 📋 **PHASE 7: 00_ORGANIZED FOLDER ANALYSIS**

### **Problem:**
- `00_Organized/` has 537,098 files
- Impossible to navigate or understand

### **Solution:**
1. **Analyze structure:**
   - Map all subdirectories
   - Identify what's actually organized vs. what's just dumped there
   - Identify duplicates and redundancies

2. **Reorganize:**
   - Move organized content to appropriate folders (apps/, examples/, docs/, etc.)
   - Archive truly legacy content to `archives/organized/`
   - Remove duplicates

3. **If too large to reorganize:**
   - Move entire folder to `archives/organized/`
   - Create index of what's inside
   - Access only when needed

---

## 🚨 **EXECUTION ORDER**

1. **Phase 1:** Fix git configuration (CRITICAL - enables tracking)
2. **Phase 2:** Root directory reorganization (FOUNDATION)
3. **Phase 3:** Duplicate folder consolidation (CLEANUP)
4. **Phase 4:** Documentation consolidation (ORGANIZATION)
5. **Phase 5:** Empty folder removal (CLEANUP)
6. **Phase 6:** Naming standardization (POLISH)
7. **Phase 7:** 00_Organized analysis (LONG-TERM)

---

## ⚠️ **RISKS AND MITIGATION**

### **Risk 1: Breaking References**
- **Risk:** Moving files breaks references in code/docs
- **Mitigation:** Use git to track moves, update references systematically

### **Risk 2: Losing Files**
- **Risk:** Accidentally deleting important files
- **Mitigation:** Create full backup before starting, use git for safety

### **Risk 3: Breaking Builds**
- **Risk:** Moving folders breaks build scripts/paths
- **Mitigation:** Update all build scripts, test after each phase

### **Risk 4: Git History Loss**
- **Risk:** Moving files loses git history
- **Mitigation:** Use `git mv` to preserve history

---

## 📊 **ESTIMATED EFFORT**

- **Phase 1:** 1-2 hours (git fix)
- **Phase 2:** 4-8 hours (root reorganization)
- **Phase 3:** 2-4 hours (duplicate consolidation)
- **Phase 4:** 8-16 hours (documentation consolidation)
- **Phase 5:** 1 hour (empty folder removal)
- **Phase 6:** 4-8 hours (naming standardization)
- **Phase 7:** 16-32 hours (00_Organized analysis)

**Total:** 36-71 hours (1-2 weeks of focused work)

---

## ✅ **SUCCESS CRITERIA**

1. ✅ Git tracks all active projects
2. ✅ Root directory has < 20 folders
3. ✅ No duplicate folders in root
4. ✅ All backups in `archives/backups/`
5. ✅ Single master index for documentation
6. ✅ All MAP files in `docs/SYSTEM_MAPS/`
7. ✅ No empty folders
8. ✅ Consistent naming conventions
9. ✅ `00_Organized/` analyzed and reorganized

---

## 🎯 **APPROVAL REQUIRED**

**⚠️ THIS PLAN REQUIRES USER APPROVAL BEFORE EXECUTION**

**Questions for User:**
1. Approve this reorganization plan?
2. Any folders that should NOT be moved?
3. Any specific naming conventions preferred?
4. Should we create full backup before starting?
5. Execute all phases or phase-by-phase?

---

**Status:** PLAN COMPLETE - AWAITING APPROVAL  
**No changes will be made until approved.**
