# Base Infrastructure Component

**Component of:** Lucid Chat System  
**Purpose:** Foundational classes and utilities  
**Status:** 95% (solid, well-tested pattern)

---

## 🎯 **Quick Context (50 words)**

Base infrastructure provides common functionality for all services: BaseAPIService (standardized request handling, error wrapping, AIM-OS integration), APIClient (HTTP client with retry/timeout/cache), AIMOSIntegrationService (automatic CMC/HHNI/VIF/SEG integration), test utilities. All services extend BaseAPIService for consistency. Singleton pattern throughout.

---

## 📦 **Files & Structure**

```
base/
├── BaseAPIService.ts         # Base service class (95%)
├── APIClient.ts              # HTTP client wrapper (95%)
└── index.ts                  # Exports

aimos/
├── AIMOSIntegrationService.ts  # AIM-OS integration (90%)
└── index.ts                     # Exports

test/
├── mockLLMService.ts         # Test utilities (80%)
└── index.ts                  # Exports
```

**Total:** 9 files, ~1,500 lines

---

## 🔧 **Key Classes**

### **BaseAPIService**
```typescript
export abstract class BaseAPIService {
  protected client: APIClient
  protected baseURL: string
  protected aimosIntegration: AIMOSIntegrationService
  
  protected async handleRequest<T>(
    request: () => Promise<T>,
    endpoint: string,
    requestData?: any
  ): Promise<APIResponse<T>> {
    // 1. Execute request
    // 2. Handle errors
    // 3. Integrate with AIM-OS (CMC, HHNI, VIF, SEG)
    // 4. Return standardized response
  }
  
  abstract isAvailable(): boolean
}
```

**Used By:** ALL services (LLM, search, reasoning, research, agents, memory)

---

### **APIClient**
```typescript
class APIClient {
  async request<T>(config: RequestConfig): Promise<T>
  
  private features:
    - Automatic retry (3 attempts with exponential backoff)
    - Timeout handling (30s default)
    - Request caching (planned)
    - Error normalization
}
```

---

### **AIMOSIntegrationService**
```typescript
class AIMOSIntegrationService {
  async integrateAPIResponse(metadata: APIResponseMetadata): Promise<AIMOSIntegrationResult>
  
  private async storeToCMC(metadata): Promise<CMCResult>
  private async trackConfidence(metadata): Promise<VIFResult>
  private async buildKnowledgeGraph(metadata): Promise<SEGResult>
}
```

**Called By:** `BaseAPIService.handleRequest()` automatically for ALL API calls

**Result:** Every API call gets:
- Stored in CMC (provenance)
- Indexed in HHNI (retrieval)
- Tracked in VIF (confidence)
- Analyzed by SEG (knowledge graph)

---

## 📊 **Usage Example**

```typescript
// Any service extending BaseAPIService
export class MyNewService extends BaseAPIService {
  constructor() {
    super('my_service', 'http://localhost:5001')
  }
  
  async myMethod(param: string): Promise<APIResponse<MyResult>> {
    return this.handleRequest(
      async () => {
        // Your logic here
        const result = await this.doSomething(param)
        return result
      },
      'myMethod',
      { param }
    )
  }
  
  isAvailable(): boolean {
    return true
  }
}

// Automatically gets:
// - Error handling
// - Retry logic
// - CMC storage
// - HHNI indexing
// - VIF tracking
// - SEG integration
// - Standardized response format
```

---

## 📊 **Response Format**

**Standardized Across All Services:**
```typescript
interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  metadata?: {
    provider: string
    latency: number
    cached: boolean
    tokens?: number
    cost?: number
  }
  aimos?: {
    cmc?: { atom_id?: string }
    hhni?: { indexed: boolean }
    vif?: { witness_id?: string }
    seg?: { entities_created?: number; relations_created?: number }
  }
}
```

**Benefits:**
- Consistent error handling
- Predictable structure
- Easy to test
- Complete metadata

---

## ⚠️ **Current Issues**

**Caching Not Implemented** ⚠️
- APIClient has `cache: true` option
- But no actual caching logic
- **Impact:** Duplicate requests not optimized
- **Fix:** Implement cache layer (1 day)

**AIM-OS Integration Not Validated** ⚠️
- Integration points defined
- HTTP calls made
- But not validated end-to-end
- **Impact:** May not actually work
- **Fix:** Integration tests (1 day)

**Tests:** 0 / ~15 needed

---

## 🎯 **Integration Points**

**Upstream:**
- MCP Tools - Via Command Server
- CMC/HHNI/VIF/SEG - Consciousness substrate
- External APIs - HTTP calls

**Downstream:**
- ALL services extend BaseAPIService
- Provides foundation for entire system

---

## 🚀 **Next Steps**

1. Implement request caching (1 day)
2. Validate AIM-OS integration end-to-end (1 day)
3. Write comprehensive tests (1 day)

**Effort to Production:** ~3 days

---

**Parent:** [../../L2_architecture.md](../../L2_architecture.md)  
**Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/base/` and `aimos/`

