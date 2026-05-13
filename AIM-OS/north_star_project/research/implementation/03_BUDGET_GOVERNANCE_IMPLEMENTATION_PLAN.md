# Implementation Plan: Program-Level Budget Governance

**Phase:** 3 of 8  
**Priority:** HIGH (10-Day "Ship It Harder")  
**Status:** Planning Complete  
**Date:** 2025-11-07  
**Estimated Duration:** 2 days  
**Team Size:** 3 agents

---

## 🎯 **Implementation Objective**

**Goal:** Extend APOE budget system to support program-level aggregation, breach policies, rolling windows, and VIF confidence adjustment.

**Success Criteria:**
- ✅ Program-level budget envelopes created
- ✅ Breach policies enforced (WARN/ABSTAIN/FAIL)
- ✅ Rolling windows tracked (24h/7d/30d)
- ✅ Cost and IO tracking added
- ✅ VIF confidence adjusted based on breaches
- ✅ All tests passing

---

## 👥 **Team Assignment**

### **Primary Owner: Codex (APOE Specialist)**
**Role:** Budget system extension, program-level aggregation  
**Responsibilities:**
- Extend Budget model with cost/IO tracking
- Create ProgramBudgetEnvelope class
- Implement budget aggregation logic
- Create BudgetTracker class
- Write APOE budget tests

### **Secondary Owner: Max (VIF Specialist)**
**Role:** VIF confidence integration, breach history  
**Responsibilities:**
- Enhance VIF witness with budget breach fields
- Implement confidence adjustment logic
- Create breach policy result models
- Write VIF integration tests

### **Tertiary Owner: Aether (CMC/SEG Integration)**
**Role:** CMC storage, SEG evidence linking  
**Responsibilities:**
- Store budget breaches in CMC
- Link breaches to SEG evidence graph
- Create breach history queries
- Write CMC/SEG integration tests

---

## 📋 **Implementation Tasks**

### **Task 3.1: Budget Model Extension** (3 hours)
**Owner:** Codex  
**Dependencies:** None  
**Deliverables:**
- Enhanced `packages/apoe/models.py` Budget class
- Cost tracking fields (cost_limit_dollars, cost_dollars)
- IO tracking fields (io_limit_mb, io_mb)
- Budget consumption tracking

**Acceptance Criteria:**
- Budget model includes cost/IO fields
- Consumption tracking works correctly
- Unit tests passing
- Backward compatible

---

### **Task 3.2: ProgramBudgetEnvelope Class** (4 hours)
**Owner:** Codex  
**Dependencies:** Task 3.1  
**Deliverables:**
- `packages/apoe/budget/program_envelope.py`
- ProgramBudgetEnvelope class
- Budget aggregation methods
- Breach history tracking

**Acceptance Criteria:**
- Envelope aggregates budgets correctly
- Breach history maintained
- Rolling windows initialized
- Unit tests passing

---

### **Task 3.3: RollingWindow Class** (3 hours)
**Owner:** Codex  
**Dependencies:** Task 3.2  
**Deliverables:**
- `packages/apoe/budget/rolling_window.py`
- RollingWindow class
- Window update logic (24h/7d/30d)
- Breach counting per window

**Acceptance Criteria:**
- Windows track consumption correctly
- Breach counts accurate
- Window expiration handled
- Unit tests passing

---

### **Task 3.4: BreachPolicy Class** (3 hours)
**Owner:** Codex  
**Dependencies:** Task 3.2  
**Deliverables:**
- `packages/apoe/budget/breach_policy.py`
- BreachPolicy class
- Policy evaluation logic (WARN/ABSTAIN/FAIL)
- Confidence penalty calculation

**Acceptance Criteria:**
- Policies evaluate correctly
- Penalties calculated accurately
- Policy actions enforced
- Unit tests passing

---

### **Task 3.5: BudgetTracker Enhancement** (4 hours)
**Owner:** Codex  
**Dependencies:** Task 3.2, Task 3.3, Task 3.4  
**Deliverables:**
- Enhanced `packages/apoe/budget_tracker.py`
- Program envelope creation
- Consumption tracking with breaches
- Rolling window updates

**Acceptance Criteria:**
- Tracker creates envelopes correctly
- Consumption tracked accurately
- Breaches detected and recorded
- Integration tests passing

---

### **Task 3.6: VIF Confidence Integration** (4 hours)
**Owner:** Max  
**Dependencies:** Task 3.4  
**Deliverables:**
- Enhanced `packages/vif/witness.py`
- Budget breach history fields
- Confidence adjustment methods
- Breach policy result fields

**Acceptance Criteria:**
- VIF witnesses include breach history
- Confidence adjusted correctly
- Policy results stored
- Unit tests passing

---

### **Task 3.7: CMC Storage Integration** (2 hours)
**Owner:** Aether  
**Dependencies:** Task 3.4  
**Deliverables:**
- Budget breach storage functions
- CMC atom creation for breaches
- Breach history queries
- Storage integration tests

**Acceptance Criteria:**
- Breaches stored in CMC correctly
- History queries work
- Atoms linked properly
- Integration tests passing

---

### **Task 3.8: SEG Evidence Linking** (2 hours)
**Owner:** Aether  
**Dependencies:** Task 3.4, Task 3.6  
**Deliverables:**
- SEG node creation for breaches
- Breach-to-operation linking
- Evidence graph updates
- SEG integration tests

**Acceptance Criteria:**
- Breach nodes created correctly
- Nodes linked to operations
- Graph queries work
- Integration tests passing

---

### **Task 3.9: APOE Execution Integration** (3 hours)
**Owner:** Codex  
**Dependencies:** All previous tasks  
**Deliverables:**
- Enhanced `packages/apoe/executor.py`
- Budget-aware plan execution
- Breach detection during execution
- Confidence adjustment integration

**Acceptance Criteria:**
- Execution tracks budgets correctly
- Breaches detected during execution
- Confidence adjusted appropriately
- End-to-end tests passing

---

### **Task 3.10: Integration Testing** (4 hours)
**Owner:** Codex (with Max and Aether)  
**Dependencies:** All previous tasks  
**Deliverables:**
- End-to-end integration tests
- Budget aggregation test suite
- Breach policy test suite
- VIF/CMC/SEG integration tests

**Acceptance Criteria:**
- All integration tests passing
- Test coverage ≥80%
- Edge cases covered
- Performance acceptable

---

## 🔄 **Dependencies & Sequencing**

```
Task 3.1 (Budget Extension)
  └─> Task 3.2 (Program Envelope)
        ├─> Task 3.3 (Rolling Window)
        ├─> Task 3.4 (Breach Policy)
        │     ├─> Task 3.6 (VIF Integration)
        │     ├─> Task 3.7 (CMC Storage)
        │     └─> Task 3.8 (SEG Linking)
        └─> Task 3.5 (Budget Tracker)
              └─> Task 3.9 (APOE Integration)
                    └─> Task 3.10 (Integration Tests)
```

**Critical Path:** Task 3.1 → Task 3.2 → Task 3.4 → Task 3.5 → Task 3.9 → Task 3.10

---

## ⏱️ **Timeline**

**Day 1 (8 hours):**
- Morning: Task 3.1 (Codex) + Task 3.2 start (Codex)
- Afternoon: Task 3.2 complete (Codex) + Task 3.3 (Codex) + Task 3.4 (Codex)

**Day 2 (8 hours):**
- Morning: Task 3.5 (Codex) + Task 3.6 (Max) + Task 3.7 (Aether)
- Afternoon: Task 3.8 (Aether) + Task 3.9 (Codex) + Task 3.10 (All)

**Total:** 16 hours (2 days)

---

## 🧪 **Testing Strategy**

### **Unit Tests:**
- Budget model extension
- Program envelope aggregation
- Rolling window updates
- Breach policy evaluation
- VIF confidence adjustment

### **Integration Tests:**
- Budget tracker integration
- APOE execution integration
- CMC storage integration
- SEG evidence linking
- End-to-end budget flow

### **Performance Tests:**
- Budget aggregation performance
- Rolling window update performance
- Breach detection performance

---

## 🚨 **Risk Assessment**

### **High Risk:**
- **Budget calculation accuracy:** Complex aggregation logic
  - **Mitigation:** Comprehensive test coverage, code review
  - **Owner:** Codex

### **Medium Risk:**
- **Performance impact:** Rolling windows may slow execution
  - **Mitigation:** Optimize window updates, cache results
  - **Owner:** Codex

### **Low Risk:**
- **VIF/CMC/SEG integration:** Well-understood systems
  - **Mitigation:** Follow existing patterns
  - **Owner:** Max, Aether

---

## ✅ **Quality Gates**

### **Pre-Implementation:**
- [ ] Budget model design reviewed
- [ ] Breach policy logic validated
- [ ] Integration approach documented

### **During Implementation:**
- [ ] All unit tests passing
- [ ] Code coverage ≥80%
- [ ] No performance regressions

### **Post-Implementation:**
- [ ] All integration tests passing
- [ ] Budget calculations verified
- [ ] Documentation updated
- [ ] Team sign-off received

---

## 📚 **Documentation Requirements**

- Budget model API documentation
- Program envelope usage guide
- Breach policy configuration
- Rolling window explanation
- VIF confidence adjustment guide
- Integration examples

---

**Status:** Implementation Plan Complete ✅  
**Ready For:** Team Review & Approval 💙

