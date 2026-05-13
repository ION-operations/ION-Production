# Lucid Chat Testing Guide

**System:** Lucid Chat  
**Framework:** Vitest  
**Coverage Target:** 90%+  
**Status:** Framework Complete, Tests Growing

---

## 🎯 **QUICK START**

### **Run All Tests:**
```bash
cd ide_orchestration/prototypes/dac
npm test
```

### **Run with Coverage:**
```bash
npm run test:coverage
```

### **Watch Mode:**
```bash
npm run test:watch
```

### **UI Mode:**
```bash
npm run test:ui
```

---

## 📊 **Test Structure**

```
tests/
├── setup.ts                  # Global test setup
├── __mocks__/                # Mock utilities
│   ├── mockCommandServer.ts  # MCP tool mocking
│   └── mockLLMService.ts     # LLM response mocking
├── unit/                     # Unit tests
│   ├── base/
│   │   └── test_base_service.test.ts
│   ├── llm/
│   │   └── test_llm_service.test.ts
│   ├── orchestration/
│   ├── search/
│   ├── reasoning/
│   │   └── test_branch_reasoning.test.ts
│   ├── research/
│   ├── agents/
│   └── memory/
├── integration/              # Integration tests
│   ├── test_apoe_workflow.test.ts
│   ├── test_search_integration.test.ts
│   └── test_multi_agent.test.ts
└── e2e/                      # End-to-end tests
    ├── test_full_chat_flow.test.ts
    └── test_research_flow.test.ts
```

**Current:** 3 unit tests passing  
**Target:** 185 total tests (130 unit, 40 integration, 15 e2e)

---

## 🧪 **Writing Tests**

### **Basic Test Pattern:**
```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { MyService } from '@services/lucid-chat'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('MyService', () => {
  let service: MyService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    service = new MyService()
  })

  describe('myMethod', () => {
    it('should do what it claims', async () => {
      // Arrange: Set up test data
      const input = 'test'

      // Act: Execute the method
      const result = await service.myMethod(input)

      // Assert: Validate the result
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
    })

    it('should handle errors', async () => {
      // Test error handling
    })

    it('should integrate with AIM-OS', async () => {
      // Test CMC/HHNI/VIF/SEG integration
    })
  })
})
```

---

## 🎭 **Mocking Strategy**

### **Mock Command Server (MCP Tools):**
```typescript
import { createMockCommandServer, mockMCPResponses } from '../../__mocks__/mockCommandServer'

const mockServer = createMockCommandServer()
global.fetch = mockServer.mockFetch as any

// Set specific response
mockServer.setResponse('store_memory', {
  success: true,
  data: { atom_id: 'test_123' }
})

// Or use prebuilt responses
mockServer.setResponse('store_memory', mockMCPResponses.store_memory)
```

### **Mock LLM Service:**
```typescript
import { createMockLLMService, mockLLMResponses } from '../../__mocks__/mockLLMService'

const mockLLM = createMockLLMService()

// Simple response
mockLLM.complete.mockResolvedValue(mockLLMResponses.simple)

// Reasoning response
mockLLM.complete.mockResolvedValue(mockLLMResponses.reasoning)

// Error response
mockLLM.complete.mockResolvedValue(mockLLMResponses.error)

// Multiple responses in sequence
mockLLM.complete
  .mockResolvedValueOnce(mockLLMResponses.hypotheses)
  .mockResolvedValueOnce(mockLLMResponses.reasoning)
  .mockResolvedValueOnce(mockLLMResponses.simple)
```

---

## 📊 **Coverage Requirements**

### **Target Coverage:**
- Lines: 90%+
- Functions: 90%+
- Branches: 90%+
- Statements: 90%+

### **View Coverage:**
```bash
npm run test:coverage
open coverage/index.html  # Opens HTML report
```

### **Current Coverage:**
```
Tests:    3 passing
Coverage: ~5% (just started)
Target:   90%
Gap:      -85%
```

---

## ✅ **Testing Checklist**

### **For New Feature:**
- [ ] Write unit tests for all public methods
- [ ] Write unit tests for error cases
- [ ] Write integration test for feature flow
- [ ] Test AIM-OS integration (CMC, HHNI, VIF, SEG)
- [ ] Achieve 90%+ coverage for new code
- [ ] All tests passing before commit

### **For Bug Fix:**
- [ ] Write failing test that reproduces bug
- [ ] Fix code to make test pass
- [ ] Add edge case tests
- [ ] Verify coverage maintained

---

## 🎯 **Test Types**

### **Unit Tests:**
- Test individual functions/classes in isolation
- Mock all external dependencies
- Fast (<1s per test file)
- **Target:** 130 unit tests

### **Integration Tests:**
- Test component interactions
- Mock external APIs only
- May be slower (1-5s per test)
- **Target:** 40 integration tests

### **E2E Tests:**
- Test complete user workflows
- Minimal mocking
- Slower (5-30s per test)
- **Target:** 15 E2E tests

---

## 💡 **Testing Best Practices**

1. **Arrange-Act-Assert pattern** - Clear test structure
2. **Descriptive test names** - `it('should do X when Y')`
3. **One assertion per test** - (or closely related assertions)
4. **Independent tests** - No test depends on another
5. **Fast tests** - Mock expensive operations
6. **Clear error messages** - Help debug failures

---

## 🚀 **Next Steps**

**Phase 1:** Basic Framework ✅ (Complete)
- Vitest configured
- Mock utilities created
- 3 tests passing
- Can run tests

**Phase 2:** Core Component Tests (Week 2-3)
- APOE orchestration tests (~50 tests)
- Search services tests (~35 tests)
- Reasoning/Research tests (~20 tests)
- Agent tests (~15 tests)
- Memory tests (~10 tests)

**Phase 3:** Integration & E2E (Week 4)
- Integration tests (~40 tests)
- E2E tests (~15 tests)

**Target:** 185 total tests, 90%+ coverage

---

**Status:** ✅ Framework Complete  
**Tests:** 3 passing  
**Coverage:** ~5%  
**Next:** Write more tests in Phase 2


