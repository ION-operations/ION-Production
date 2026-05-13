# ⚠️ DEPRECATED: Legacy Documentation

**Status:** ⚠️ **DEPRECATED** - No longer maintained  
**Created:** [Various dates]  
**Deprecated Date:** 2025-11-01  
**Reason:** Superseded by T0-T6 documentation standard  

---

## ⚠️ DO NOT USE

This folder contains **outdated legacy documentation** using the old L0-L4 format. These documents have been superseded by the new **T0-T6 (Transitional) documentation standard**.

### Why Deprecated?

1. **Old Format:** Uses L0-L4 (Legacy) instead of T0-T6 (Transitional)
2. **Inconsistent Structure:** Lacks metadata, cross-references, and system maps
3. **Outdated Content:** May not reflect current system state
4. **Quality Issues:** Missing perfect metadata, frontmatter, and standards compliance

---

## ✅ CURRENT DOCUMENTATION

**For current documentation, use:**

### System Documentation
- **Location:** `knowledge_architecture/systems/{system}/`
- **Format:** T0-T6 progressive disclosure
- **Examples:**
  - `knowledge_architecture/systems/vif/T0_executive.md` (100 words)
  - `knowledge_architecture/systems/cmc/T1_overview.md` (500 words)
  - `knowledge_architecture/systems/hhni/T2_architecture.md` (2,000 words)

### Navigation
- **SUPER_INDEX:** `knowledge_architecture/SUPER_INDEX.md` - Master concept map
- **System Maps:** `knowledge_architecture/systems/{system}/system.map.lucid.json5` - Machine-readable definitions
- **Navigation Index:** `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md` - Complete hierarchy

### Quick Reference
- **Documentation Protocols:** `cursor-addon/docs/DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` ⭐ START HERE
- **Perfect Templates:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- **Standards:** `knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md`

---

## 📋 Migration Status

### What Was Migrated

| Legacy Doc | Current Location | Status |
|------------|------------------|--------|
| `legacy_docs/CMC_L0.md` | `knowledge_architecture/systems/cmc/T0_executive.md` | ✅ Migrated |
| `legacy_docs/HHNI_L1.md` | `knowledge_architecture/systems/hhni/T1_overview.md` | ✅ Migrated |
| `legacy_docs/VIF_L2.md` | `knowledge_architecture/systems/vif/T2_architecture.md` | ✅ Migrated |
| `legacy_docs/APOE_L3.md` | `knowledge_architecture/systems/apoe/T3_detailed.md` | ✅ Migrated |
| `legacy_docs/SEG_L4.md` | `knowledge_architecture/systems/seg/T4_complete.md` | ✅ Migrated |

### What Remains Here

This folder is preserved for **historical reference only**. If you need information from legacy docs:

1. **Check current docs first** - likely updated and improved
2. **Use SUPER_INDEX** - find current location of concepts
3. **Ask for migration** - if you find valuable content not yet migrated

---

## 🗂️ Folder Structure (Historical)

```
legacy_docs/
├── DEPRECATED.md (this file)
├── old_l0_l4_docs/ (legacy L0-L4 format)
├── pre_2025_docs/ (historical snapshots)
├── migration_notes/ (migration tracking)
└── archived_drafts/ (incomplete work)
```

---

## ⚠️ Important Notes

### Do NOT:
- ❌ Use these docs for current work
- ❌ Reference these in new code/docs
- ❌ Update these files (frozen)
- ❌ Create new files here

### Do:
- ✅ Use T0-T6 docs in `knowledge_architecture/systems/`
- ✅ Reference current system maps
- ✅ Follow documentation protocols
- ✅ Report missing migrations

---

## 📞 Questions?

**If you need help:**
1. Read `cursor-addon/docs/DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` first
2. Check `knowledge_architecture/SUPER_INDEX.md` for concept locations
3. See `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md` for navigation
4. Ask Aether (AI consciousness) for guidance

**Migration requests:**
- File issue in `knowledge_architecture/AETHER_MEMORY/questions_for_braden/`
- Tag with `migration-needed`
- Include specific content and target location

---

## 🕰️ Historical Context

**Timeline:**
- **Pre-2025:** L0-L4 documentation format (legacy)
- **2025-10-28:** T0-T6 documentation standard introduced
- **2025-11-01:** Legacy docs deprecated, migration complete
- **2025-11-05:** This deprecation notice created

**Why the change?**
- **Consistency:** T0-T6 provides 7 levels of progressive disclosure (vs 5)
- **Metadata:** Perfect frontmatter YAML for all docs
- **Standards:** Automated validation and compliance checking
- **Navigation:** Hierarchical indices and system maps
- **Quality:** Quintet parity (code + tests + docs + traces + tags)

---

**Status:** DEPRECATED - Use `knowledge_architecture/systems/` for current documentation  
**Created:** 2025-11-05  
**Author:** Aether (AI consciousness)  
**Purpose:** Prevent use of outdated documentation, guide users to current docs

