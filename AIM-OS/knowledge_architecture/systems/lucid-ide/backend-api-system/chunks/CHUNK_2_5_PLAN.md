# Chunk 2.5: Implement Real Budget Tracking

**Phase:** 2 (Core Algorithms)  
**Chunk:** 2.5  
**Duration:** 1 day (8 hours planned)  
**Priority:** P0-5 (CRITICAL - Budget enforcement)  
**Status:** READY TO START ⏳

---

## 🎯 **GOAL**

Implement real token counting, cost calculation, and budget enforcement in BudgetTracker.

**Current State:**
- BudgetTracker has structure
- Token counting placeholder (returns 0)
- Cost calculation placeholder
- Budget checking functional but with wrong data

**Success Criteria:**
- Real token counting (tiktoken or estimate)
- Accurate cost calculation per model
- Budget warnings at thresholds
- Budget enforcement (stop at limit)
- Comprehensive tests (90%+ coverage)

---

## 🎭 **APOE WORKFLOW**

### **Role 1: RETRIEVER (Research) - 1 hour**
**Task:** Research token counting approaches

**Activities:**
1. Study tiktoken library
2. Review model pricing
3. Examine token estimation methods
4. Research budget tracking patterns

**Outputs:**
- Token counting approach
- Pricing data per model
- Budget tracking strategy

---

### **Role 2: REASONER (Design) - 1 hour**
**Task:** Design budget system

**Activities:**
1. Design token counter
   - Use tiktoken if available
   - Fallback: Character-based estimation

2. Design cost calculator
   - Pricing table per model
   - Input + output token costs

3. Design budget enforcer
   - Warning thresholds (50%, 75%, 90%)
   - Hard limits
   - Graceful degradation

**Outputs:**
- Complete design
- Pricing table
- Threshold logic

---

### **Role 3: BUILDER (Implementation) - 4 hours**
**Task:** Implement budget tracking

**Activities:**
1. Implement token counter (~100 lines)
2. Implement cost calculator (~80 lines)
3. Update BudgetTracker (~100 lines)
4. Write tests (~200 lines)

**Outputs:**
- Real token counting
- Accurate cost calculation
- Budget enforcement
- Comprehensive tests

---

### **Role 4: VERIFIER (Validation) - 1 hour**
**Task:** Validate accuracy

**Activities:**
1. Test token counting accuracy
2. Verify cost calculations
3. Test budget enforcement
4. Edge case testing

**Outputs:**
- Validation report
- Accuracy assessment

---

### **Role 5: WITNESS (Documentation) - 1 hour**
**Task:** Document implementation

---

## 📦 **DELIVERABLES**

### **Implementation:**
```
ide_orchestration/prototypes/dac/src/services/lucid-chat/orchestration/
├── TokenCounter.ts (NEW - 100 lines)
├── CostCalculator.ts (NEW - 80 lines)
├── BudgetTracker.ts (updated - 100 lines)

tests/unit/orchestration/
└── test_budget_tracker.test.ts (NEW - 200 lines)
```

**Total:** ~280 lines implementation + ~200 lines tests

---

## ✅ **VALIDATION CRITERIA**

### **Must Pass:**
1. **Token Counting:**
   - [ ] Accurate within 5% of actual
   - [ ] Fast (<10ms per count)
   - [ ] Handles all text types

2. **Cost Calculation:**
   - [ ] Correct pricing per model
   - [ ] Input + output tokens separated
   - [ ] Batch costs correct

3. **Budget Enforcement:**
   - [ ] Warnings at thresholds
   - [ ] Stops at hard limit
   - [ ] Status tracking accurate

4. **Quality:**
   - [ ] 90%+ test coverage
   - [ ] All tests passing

---

## ⏱️ **TIME ALLOCATION**

| Role | Hours |
|------|-------|
| Retriever | 1h |
| Reasoner | 1h |
| Builder | 4h |
| Verifier | 1h |
| Witness | 1h |
| **TOTAL** | **8h** |

**With Efficiency:** Likely 1-2 hours (11x faster trend)

---

**Status:** ⏳ READY  
**Confidence:** 0.85  
**Impact:** HIGH (budget control)

Let's track costs properly! 🚀


