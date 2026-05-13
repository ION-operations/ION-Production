# Chunk 2.4: Implement DAG Workflow Executor

**Phase:** 2 (Core Algorithms)  
**Chunk:** 2.4  
**Duration:** 2 days (16 hours planned)  
**Priority:** P1 (HIGH - Core orchestration feature)  
**Status:** READY TO START ⏳

---

## 🎯 **GOAL**

Implement real DAG (Directed Acyclic Graph) executor for APOE workflows with dependency management and parallel execution.

**Current State:**
- WorkflowExecutor has basic structure
- DAG execution placeholder (sequential fallback)
- No dependency resolution
- No parallel execution

**Success Criteria:**
- Real DAG construction from plan
- Topological sort for execution order
- Dependency resolution
- Parallel execution where possible
- Progress tracking
- Comprehensive tests (90%+ coverage)

---

## 🎭 **APOE WORKFLOW**

### **Role 1: RETRIEVER (Research) - 2 hours**
**Task:** Research DAG execution patterns

**Activities:**
1. Study DAG algorithms
   - Topological sort (Kahn's algorithm)
   - Dependency resolution
   - Cycle detection

2. Review parallel execution
   - Promise.all for parallel tasks
   - Semaphore for concurrency limits
   - Error handling in parallel execution

3. Examine existing APOE implementation
   - Current WorkflowExecutor
   - RoleDispatcher patterns
   - Budget/Quality gate integration

**Outputs:**
- DAG algorithm selection
- Parallel execution strategy
- Integration approach

---

### **Role 2: REASONER (Design) - 2 hours**
**Task:** Design complete DAG executor

**Activities:**
1. Design DAG data structure
   - Node representation
   - Edge representation
   - Metadata storage

2. Design execution algorithm
   - Build DAG from plan
   - Topological sort
   - Parallel execution logic
   - Error handling

3. Design progress tracking
   - Node status tracking
   - Completion percentage
   - Time estimation

**Outputs:**
- Complete algorithm design
- Data structures
- API contracts

---

### **Role 3: BUILDER (Implementation) - 8 hours**
**Task:** Implement DAG executor

**Day 1 (4 hours): Core DAG**
1. Implement DAG data structure
   - DAGNode class
   - DAGGraph class
   - Build from APOE plan

2. Implement topological sort
   - Kahn's algorithm
   - Cycle detection
   - Execution order

3. Write unit tests

**Day 2 (4 hours): Execution + Integration**
4. Implement parallel executor
   - Parallel execution
   - Dependency waiting
   - Error handling

5. Integrate with WorkflowExecutor
   - Replace sequential execution
   - Progress tracking
   - Budget/quality gates

6. Write integration tests

**Outputs:**
- DAG implementation (~300 lines)
- Parallel executor (~200 lines)
- Integration (~100 lines)
- Tests (~400 lines, 20+ cases)

---

### **Role 4: OPERATOR (Execution) - 2 hours**
**Task:** Run tests and verify

**Activities:**
1. Run unit tests
2. Run integration tests
3. Performance benchmarking
4. Fix any failures

**Outputs:**
- All tests passing
- Coverage report (90%+)
- Performance metrics

---

### **Role 5: VERIFIER (Validation) - 2 hours**
**Task:** Validate DAG executor

**Activities:**
1. Test with real workflows
   - Simple linear workflow
   - Parallel branches
   - Complex dependencies

2. Validate correctness
   - Dependency order respected
   - Parallel execution works
   - Error handling correct

3. Performance validation
   - Parallel faster than sequential
   - Overhead acceptable

**Outputs:**
- Validation report
- Performance benchmarks

---

### **Role 6: WITNESS (Documentation) - 1 hour**
**Task:** Document implementation

**Activities:**
1. Update L3 with DAG details
2. Document algorithm
3. Update placeholder registry
4. Create completion report

---

## 📦 **DELIVERABLES**

### **Implementation:**
```
ide_orchestration/prototypes/dac/src/services/lucid-chat/orchestration/
├── DAGExecutor.ts (NEW - 300 lines)
│   ├── DAGNode class
│   ├── DAGGraph class
│   └── Parallel execution
├── WorkflowExecutor.ts (updated - 100 lines)
│   └── Integrate DAG executor

tests/
└── unit/
    └── orchestration/
        ├── test_dag_executor.test.ts (NEW - 15+ cases)
        └── test_workflow_executor.test.ts (updated - 5+ cases)
```

**Total:** ~600 lines implementation + ~400 lines tests

---

## ✅ **VALIDATION CRITERIA**

### **Must Pass:**
1. **DAG Construction:**
   - [ ] Builds DAG from APOE plan
   - [ ] Detects cycles
   - [ ] Validates structure

2. **Execution:**
   - [ ] Topological sort correct
   - [ ] Dependencies respected
   - [ ] Parallel execution works
   - [ ] Error handling robust

3. **Performance:**
   - [ ] Parallel faster than sequential
   - [ ] Overhead <10%
   - [ ] Memory usage acceptable

4. **Integration:**
   - [ ] WorkflowExecutor uses DAG
   - [ ] Budget tracking works
   - [ ] Quality gates enforced
   - [ ] Progress tracking accurate

5. **Quality:**
   - [ ] 90%+ test coverage
   - [ ] All tests passing
   - [ ] Edge cases handled

---

## ⏱️ **TIME ALLOCATION**

| Role | Activity | Hours |
|------|----------|-------|
| Retriever | Research | 2h |
| Reasoner | Design | 2h |
| Builder | Implement + tests | 8h |
| Operator | Run tests | 2h |
| Verifier | Validate | 2h |
| Witness | Document | 1h |
| **TOTAL** | | **17h** |

**Estimated:** 2 working days (8h each)  
**With Efficiency:** Likely 2-3 hours (11x faster trend)

---

## 🎯 **SUCCESS DEFINITION**

**Chunk Complete When:**
- DAG construction works
- Topological sort correct
- Parallel execution functional
- Dependencies respected
- 90%+ test coverage
- All tests passing
- WorkflowExecutor integrated

**This enables true APOE orchestration!** ✅

---

**Status:** ⏳ READY TO START  
**Prerequisites:** Chunks 2.1-2.3 complete ✅  
**Confidence:** 0.87 (DAG algorithms well-known)  
**Impact:** HIGH (enables efficient APOE execution)

Let's implement real orchestration! 🚀


