# Discovery 006: Documentation Conflicts Found
**Timestamp:** 2025-01-27 ~12:50 PM  
**Severity:** HIGH - Multiple sources of truth conflict

---

## 🔴 **CRITICAL: DEADLINE PASSED**

### **North Star Deadline**
- **GOAL_TREE.yaml claims:** Ship by 2025-11-30
- **Current date:** 2025-12-01 (system time)
- **Status:** DEADLINE HAS PASSED ⚠️

The goal tree hasn't been updated to reflect whether the goal was met or needs revision.

---

## 📊 **MCP TOOL COUNT CONFLICTS**

| Source | Count |
|--------|-------|
| `lucid_mcp_server.py` header | 93 |
| `lucid_mcp_server.py` class docstring | 92 |
| `lucid_mcp_server.py` init log | 78 |
| `FACTS.md` ("verified in code") | 84 |
| Actual `# Tool N:` comments | 94 |

**Which is correct?** Unknown without manual verification.

---

## 📈 **SYSTEM COMPLETION PERCENTAGE CONFLICTS**

### **README.md Claims:**
| System | Claimed Status |
|--------|---------------|
| CMC | ~70% |
| HHNI | ~100% |
| VIF | ~95% |
| APOE | ~90% |
| SEG | ~100% |
| SDF-CVF | ~95% |
| CAS | ~60% |

### **FACTS.md Claims:**
| System | Claimed Status |
|--------|---------------|
| CMC | 70% complete, production-ready |
| HHNI | 100% complete ✅ |
| VIF | 95% complete, production-ready |
| APOE | 70% complete, production-ready |
| SEG | Production-ready |
| CAS | Production-ready |

### **Conflict:**
- **APOE:** README says ~90%, FACTS.md says 70%
- **CAS:** README says ~60%, FACTS.md says "Production-ready"
- **SEG:** README says ~100%, FACTS.md says "Production-ready" (no %)

---

## 📅 **DATE INCONSISTENCIES**

### **GOAL_TREE.yaml Dates:**
- last_updated: 2025-11-05 (almost a month old)
- target_date for OBJ-01 (CMC): 2025-11-13 (PASSED)
- target_date for OBJ-02 (HHNI): 2025-11-15 (PASSED)

### **README Claims:**
- "Recent Major Achievements (2025-01-27)" 
- But 2025-01-27 appears to be FUTURE from goal tree perspective

**Confusion:** Are we in January 2027 or December 2025?

---

## 🔍 **IMPORT REALITY vs CLAIMS**

### **My Import Test Results:**
| System | Claim | Reality |
|--------|-------|---------|
| CMC | Working | Works with path fix |
| HHNI | 100% | ✅ Imports cleanly |
| VIF | 95% | ✅ Imports cleanly (class is VIF not VIFWitness) |
| APOE | 70-90% | ❌ Circular import error |
| SEG | Production-ready | ✅ Imports (class is SEGraph) |
| CAS | Production-ready | ✅ Imports (class is FailureModeAnalyzer) |

**Reality Check:** APOE doesn't even import due to circular import!

---

## 📝 **CLASS NAMING CONFLICTS**

Documentation often uses different names than actual code exports:

| Docs Say | Code Actually Exports |
|----------|----------------------|
| VIFWitness | VIF |
| SEG | SEGraph |
| CognitiveAnalyzer | FailureModeAnalyzer, IntrospectionProtocol |

---

## ⚠️ **WHY THIS MATTERS**

1. **Trust erosion:** When docs conflict, which do you trust?
2. **Onboarding friction:** New contributors get confused
3. **Integration errors:** Wrong class names cause failures
4. **Goal tracking failure:** Passed deadlines not acknowledged

---

## ✅ **RECOMMENDED ACTIONS**

### **Immediate:**
1. Update GOAL_TREE.yaml with post-deadline status
2. Fix tool count - pick one number, verify, update all refs
3. Fix APOE circular import (production blocker)

### **Short Term:**
4. Reconcile system completion percentages
5. Update class name references in docs
6. Create automated validation for doc/code sync

### **Long Term:**
7. Implement SOURCE_OF_TRUTH.yaml pattern for all metrics
8. Add CI checks for documentation consistency
9. Create single authoritative status dashboard

---

## 🏷️ **CLASSIFICATION**

- **Type:** Documentation Inconsistency
- **Impact:** High (undermines trust and causes errors)
- **Effort to Fix:** Medium (requires reconciliation)
- **Priority:** High (should fix before more docs diverge)

