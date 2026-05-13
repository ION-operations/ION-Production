# Chunk 3.1: Expand Unit Tests

**Phase:** 3 (Testing & Validation)  
**Chunk:** 3.1  
**Duration:** 1 day (8 hours planned)  
**Priority:** P0-7 (CRITICAL - Test coverage)  
**Status:** READY TO START ⏳

---

## 🎯 **GOAL**

Expand unit test coverage from 100+ to 160+ test cases, focusing on Phase 2 components.

**Current State:**
- ICIP: 45 tests ✅
- DEEPSEARCH: 55 tests ✅
- BaseAPIService: 3 tests ✅
- LLMService: 3 tests ✅
- BranchReasoning: 3 tests ✅
- **Total:** 109 tests

**Target State:**
- All Phase 2 components tested
- 90%+ coverage
- 160+ total tests

**Success Criteria:**
- TokenCounter: 10+ tests
- CostCalculator: 10+ tests
- BudgetTracker: 15+ tests
- QualityGates: 15+ tests
- DAGExecutor: 20+ tests
- WorkflowExecutor: 10+ tests
- **Total:** 80+ new tests

---

## 🎭 **APOE WORKFLOW**

### **Role 1: RETRIEVER (Research) - 0.5 hours**
**Task:** Review existing tests and identify gaps

**Activities:**
1. List all Phase 2 components
2. Check which have tests
3. Identify missing test coverage
4. Review test patterns

**Outputs:**
- Component test matrix
- Gap analysis
- Test priorities

---

### **Role 2: REASONER (Design) - 0.5 hours**
**Task:** Design test suites

**Activities:**
1. Design TokenCounter tests
2. Design CostCalculator tests
3. Design BudgetTracker tests
4. Design QualityGates tests
5. Design DAGExecutor tests

**Outputs:**
- Test plan for each component
- Test case list

---

### **Role 3: BUILDER (Implementation) - 6 hours**
**Task:** Write comprehensive tests

**Activities:**
1. TokenCounter tests (~100 lines)
2. CostCalculator tests (~150 lines)
3. BudgetTracker tests (~200 lines)
4. QualityGates tests (~200 lines)
5. DAGExecutor tests (~300 lines)
6. WorkflowExecutor tests (~150 lines)

**Outputs:**
- 80+ new test cases
- ~1,100 lines of test code

---

### **Role 4: VERIFIER (Validation) - 0.5 hours**
**Task:** Run tests and verify coverage

---

### **Role 5: WITNESS (Documentation) - 0.5 hours**
**Task:** Document test coverage

---

## 📦 **DELIVERABLES**

### **Test Files:**
```
tests/unit/orchestration/
├── test_token_counter.test.ts (NEW - 100 lines)
├── test_cost_calculator.test.ts (NEW - 150 lines)
├── test_budget_tracker.test.ts (NEW - 200 lines)
├── test_quality_gates.test.ts (NEW - 200 lines)
├── test_dag_executor.test.ts (NEW - 300 lines)
└── test_workflow_executor.test.ts (NEW - 150 lines)
```

**Total:** ~1,100 lines of tests

---

## ✅ **VALIDATION CRITERIA**

### **Must Pass:**
1. **All tests passing** ✅
2. **90%+ coverage** ✅
3. **160+ total tests** ✅
4. **Edge cases covered** ✅

---

## ⏱️ **TIME ALLOCATION**

| Role | Hours |
|------|-------|
| Retriever | 0.5h |
| Reasoner | 0.5h |
| Builder | 6h |
| Verifier | 0.5h |
| Witness | 0.5h |
| **TOTAL** | **8h** |

**With Efficiency:** Likely 1-2 hours (8x faster trend)

---

**Status:** ⏳ READY  
**Confidence:** 0.90  
**Impact:** HIGH (test coverage critical)

Let's test everything! 🚀


