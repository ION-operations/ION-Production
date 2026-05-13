# Chunk 1.2: Set Up Testing Framework

**Phase:** 1 (Foundation)  
**Chunk:** 1.2  
**Duration:** 1 day (8 hours)  
**Priority:** P0 (CRITICAL - No tests currently)  
**Status:** READY TO START ⏳

---

## 🎯 **GOAL**

Establish operational testing infrastructure for Lucid Chat system with first passing test.

**Why This Matters:**
- Currently 0% test coverage (can't validate anything)
- Need testing to validate all future work
- Test-driven development prevents technical debt
- Immediate feedback on what works vs doesn't

---

## 🎭 **APOE WORKFLOW**

### **Role 1: RETRIEVER** (Research) - 1 hour
**Task:** Research testing best practices and frameworks

**Activities:**
1. Review existing AIM-OS testing (packages/integration_tests/)
2. Research Jest vs Vitest for TypeScript
3. Find testing patterns for async services
4. Review mocking strategies
5. Understand coverage reporting

**Outputs:**
- Framework recommendation (Jest or Vitest)
- Testing patterns identified
- Mock strategy clear

---

### **Role 2: BUILDER** (Implementation) - 4 hours
**Task:** Set up testing infrastructure

**Activities:**
1. Install testing dependencies (2h)
   - Install Jest or Vitest
   - Install @testing-library if needed
   - Install coverage tools
   - Configure TypeScript support

2. Create test structure (1h)
   - Create `tests/` directory
   - Set up `unit/`, `integration/`, `e2e/` folders
   - Create test utilities
   - Create mock factories

3. Write first tests (1h)
   - Smoke test (system loads)
   - BaseAPIService test
   - Simple service test

**Outputs:**
- Testing framework configured
- Test directory structure
- 3-5 passing tests

---

### **Role 3: OPERATOR** (Execution) - 1 hour
**Task:** Run tests and verify setup

**Activities:**
1. Run tests via CLI
2. Generate coverage report
3. Verify CI integration (if applicable)
4. Test watch mode
5. Validate error reporting

**Outputs:**
- Tests run successfully
- Coverage report generated
- Test commands documented

---

### **Role 4: VERIFIER** (Validation) - 1 hour
**Task:** Validate testing framework works

**Activities:**
1. Write failing test
2. Fix code to make it pass
3. Verify coverage updates
4. Test error messages clear
5. Validate mock system works

**Outputs:**
- TDD workflow validated
- Coverage tracking verified
- Mock system working

---

### **Role 5: WITNESS** (Documentation) - 30 min
**Task:** Document testing setup

**Activities:**
1. Create TESTING_GUIDE.md
2. Document test commands
3. Create chunk completion report
4. Update master tracker

**Outputs:**
- `TESTING_GUIDE.md`
- `CHUNK_1_2_COMPLETE.md`
- Updated tracker

---

## 📦 **DELIVERABLES**

### **Primary:**
```
ide_orchestration/prototypes/dac/
├── vitest.config.ts (or jest.config.js)
├── tests/
│   ├── setup.ts
│   ├── unit/
│   │   ├── base/
│   │   │   └── test_base_service.test.ts
│   │   └── llm/
│   │       └── test_llm_service.test.ts
│   ├── integration/
│   │   └── test_basic_flow.test.ts
│   └── __mocks__/
│       ├── mockLLMService.ts
│       └── mockCommandServer.ts
└── package.json (updated with test scripts)
```

### **Documentation:**
```
knowledge_architecture/systems/lucid-chat/
└── TESTING_GUIDE.md
```

**Total:** Testing framework + 3-5 passing tests + documentation

---

## ✅ **VALIDATION CRITERIA**

### **Must Pass:**
1. **Framework Operational:**
   - [ ] Can run `npm test` successfully
   - [ ] Tests execute and report results
   - [ ] Coverage reporting works
   - [ ] Watch mode functional

2. **Tests Passing:**
   - [ ] At least 3 tests passing
   - [ ] Tests cover basic functionality
   - [ ] Mock system working
   - [ ] Error messages clear

3. **Documentation:**
   - [ ] Test commands documented
   - [ ] Test structure explained
   - [ ] Mock usage explained
   - [ ] Coverage interpretation guide

4. **Process:**
   - [ ] Chunk journal maintained
   - [ ] Completion report created
   - [ ] Master tracker updated
   - [ ] Lessons documented

---

## ⏱️ **TIME ALLOCATION**

| Role | Activity | Hours |
|------|----------|-------|
| Retriever | Research frameworks | 1h |
| Builder | Set up + write tests | 4h |
| Operator | Run tests | 1h |
| Verifier | Validate TDD workflow | 1h |
| Witness | Document | 0.5h |
| **TOTAL** | | **7.5h** |

**Estimated:** 1 working day (8h)  
**Buffer:** +0.5h  
**Total:** 8h ≈ 1 day

---

## 🎯 **SUCCESS CRITERIA**

**Chunk Complete When:**
- Testing framework installed and configured
- Can run tests via CLI
- At least 3 tests passing
- Coverage reporting works
- Testing guide documented
- Next chunk ready (1.3: Label Placeholders)

---

## 📝 **NOTES**

**Framework Decision:**
- Jest: Mature, well-documented, industry standard
- Vitest: Faster, better Vite integration, modern
- **Recommendation:** Vitest (already using Vite)

**Testing Priorities:**
- Smoke tests first (does it load?)
- Base infrastructure tests (BaseAPIService)
- Simple service tests (one full test per major service)
- Integration tests (Phase 3)

---

**Status:** ⏳ READY TO START  
**Prerequisites:** Chunk 1.1 complete ✅  
**Confidence:** 0.90 (Clear scope, familiar territory)


