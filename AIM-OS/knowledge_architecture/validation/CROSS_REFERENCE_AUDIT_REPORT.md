# Cross-Reference Audit Report

**Date:** 2025-11-03T22:58:40.346568  
**Systems Validated:** 9  
**Status:** ✅ ALL PASS

---

## Summary

**Overall Pass Rate:** 9 / 9 (100%)

**Total Issues:**
- Broken References: 0
- Missing References: 3
- Bidirectional Issues: 3

---

## System-by-System Results


### ✅ cmc

**Status:** PASS

**Issues:**
- ⚠️ Cross-system connections YAML shows connection 'SDF-CVF', but T2 doc does not reference it


### ✅ seg

**Status:** PASS


### ✅ hhni

**Status:** PASS


### ✅ vif

**Status:** PASS

**Issues:**
- ⚠️ Cross-system connections YAML shows connection 'SDF-CVF', but T2 doc does not reference it


### ✅ sdfcvf

**Status:** PASS


### ✅ apoe

**Status:** PASS

**Issues:**
- ⚠️ Cross-system connections YAML shows connection 'All systems', but T2 doc does not reference it


### ✅ cognitive_analysis

**Status:** PASS


### ✅ timeline_context_system

**Status:** PASS

**Issues:**
- ⚠️ Bidirectional reference missing: timeline_context_system→cognitive_analysis exists, but cognitive_analysis→timeline_context_system missing


### ✅ intuitive_intelligence_system

**Status:** PASS

**Issues:**
- ⚠️ Bidirectional reference missing: intuitive_intelligence_system→cognitive_analysis exists, but cognitive_analysis→intuitive_intelligence_system missing
- ⚠️ Bidirectional reference missing: intuitive_intelligence_system→timeline_context_system exists, but timeline_context_system→intuitive_intelligence_system missing


---

**Next Steps:** Run `python scripts/generate_cross_references.py --all` to generate missing cross-references.
