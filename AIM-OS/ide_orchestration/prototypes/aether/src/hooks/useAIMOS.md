# useAIMOS Hook System
## Unified AIM-OS Hook Implementation

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Implement unified useAIMOS hook system for V2  
**Status:** Implementation Started  
**Source:** Dac's Prototype Best Idea

---

## 🎯 **VISION**

**Single Hook Interface:** `const { cmc, hhni, vif, seg, apoe, tcs, cas, sdfcvf } = useAIMOS()`

**Benefits:**
- Simple, consistent API across all 8 AIM-OS systems
- Easy migration from mock data to real MCP calls
- TypeScript support throughout
- Error handling and loading states built-in
- Real-time updates when connected

---

## 🏗️ **ARCHITECTURE**

### **Hook Structure:**
```typescript
interface AIMOSHook {
  cmc: CMCInterface
  hhni: HHNIInterface
  vif: VIFInterface
  seg: SEGInterface
  apoe: APOEInterface
  tcs: TCSInterface
  cas: CASInterface
  sdfcvf: SDFCVFInterface
  isConnected: boolean
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'error'
  error: Error | null
}
```

### **System Interfaces:**

#### **CMC Interface:**
```typescript
interface CMCInterface {
  store: (content: string, tags?: object) => Promise<string>
  retrieve: (query: string, limit?: number) => Promise<Memory[]>
  getStats: () => Promise<MemoryStats>
  loading: boolean
  error: Error | null
}
```

#### **HHNI Interface:**
```typescript
interface HHNIInterface {
  search: (query: string, limit?: number) => Promise<SearchResult[]>
  retrieve: (atomId: string) => Promise<Atom | null>
  getHierarchy: (atomId: string) => Promise<Hierarchy>
  loading: boolean
  error: Error | null
}
```

#### **VIF Interface:**
```typescript
interface VIFInterface {
  trackConfidence: (task: string, confidence: number, evidence?: string[]) => Promise<void>
  getWitnesses: (task: string) => Promise<Witness[]>
  validate: (statement: string) => Promise<ValidationResult>
  loading: boolean
  error: Error | null
}
```

#### **SEG Interface:**
```typescript
interface SEGInterface {
  addEvidence: (evidence: Evidence) => Promise<string>
  detectContradictions: (query: string) => Promise<Contradiction[]>
  synthesize: (topics: string[]) => Promise<Synthesis>
  loading: boolean
  error: Error | null
}
```

#### **APOE Interface:**
```typescript
interface APOEInterface {
  createPlan: (goal: string, context?: string) => Promise<Plan>
  executePlan: (planId: string) => Promise<Execution>
  getProgress: (planId: string) => Promise<Progress>
  loading: boolean
  error: Error | null
}
```

#### **TCS Interface:**
```typescript
interface TCSInterface {
  addEntry: (promptId: string, userInput: string, contextState?: object) => Promise<string>
  getSummary: (limit?: number) => Promise<TimelineEntry[]>
  getEntries: (filters?: TimelineFilters) => Promise<TimelineEntry[]>
  loading: boolean
  error: Error | null
}
```

#### **CAS Interface:**
```typescript
interface CASInterface {
  getMetrics: () => Promise<ConsciousnessMetrics>
  detectDrift: (context?: DriftContext) => Promise<DriftResult>
  runAudit: (type?: AuditType) => Promise<AuditResult>
  loading: boolean
  error: Error | null
}
```

#### **SDF-CVF Interface:**
```typescript
interface SDFCVFInterface {
  validate: (action: object, context?: object) => Promise<ValidationResult>
  checkInvariant: (action: object, context?: object) => Promise<InvariantResult>
  loading: boolean
  error: Error | null
}
```

---

## ⚙️ **IMPLEMENTATION**

### **Mode Support:**
1. **Mock Data Mode (Default):**
   - Returns mock data immediately
   - No network calls
   - Perfect for development/prototyping

2. **MCP Mode (When Connected):**
   - Makes real MCP tool calls
   - Handles errors gracefully
   - Shows loading states

3. **Hybrid Mode:**
   - Uses MCP when available
   - Falls back to mock data on error
   - Seamless transition

### **Error Handling:**
- Network errors → Fallback to mock data
- Invalid responses → Show error, use mock data
- Timeout errors → Retry once, then fallback
- User-friendly error messages

### **Loading States:**
- Per-system loading states
- Global connection status
- Optimistic updates where possible

---

## 📋 **USAGE EXAMPLES**

### **Basic Usage:**
```typescript
import { useAIMOS } from '@/hooks/useAIMOS'

function MyComponent() {
  const { cmc, hhni, vif } = useAIMOS()
  
  // Store memory
  const handleStore = async () => {
    const atomId = await cmc.store('Important insight', { tag: 'insight' })
    console.log('Stored:', atomId)
  }
  
  // Search HHNI
  const handleSearch = async () => {
    const results = await hhni.search('refactoring patterns')
    console.log('Found:', results)
  }
  
  // Track confidence
  const handleConfidence = async () => {
    await vif.trackConfidence('Task completion', 0.95, ['evidence_1'])
  }
  
  return (
    <div>
      {cmc.loading && <div>Loading...</div>}
      {cmc.error && <div>Error: {cmc.error.message}</div>}
      <button onClick={handleStore}>Store Memory</button>
    </div>
  )
}
```

### **With Error Handling:**
```typescript
function MyComponent() {
  const { cmc, isConnected, connectionStatus } = useAIMOS()
  
  const handleStore = async () => {
    try {
      const atomId = await cmc.store('Important insight')
      console.log('Stored:', atomId)
    } catch (error) {
      console.error('Failed to store:', error)
      // Fallback behavior
    }
  }
  
  return (
    <div>
      <div>Status: {connectionStatus}</div>
      {isConnected ? (
        <div>Connected to AIM-OS</div>
      ) : (
        <div>Using mock data</div>
      )}
      <button onClick={handleStore}>Store Memory</button>
    </div>
  )
}
```

---

## 🔧 **TECHNICAL REQUIREMENTS**

### **Dependencies:**
- React hooks
- TypeScript
- MCP tool integration (when connected)
- Mock data (default)

### **File Structure:**
```
src/hooks/
  useAIMOS.ts          # Main hook
  useCMC.ts            # CMC hook
  useHHNI.ts           # HHNI hook
  useVIF.ts            # VIF hook
  useSEG.ts            # SEG hook
  useAPOE.ts           # APOE hook
  useTCS.ts            # TCS hook
  useCAS.ts            # CAS hook
  useSDFCVF.ts         # SDF-CVF hook
  types.ts             # TypeScript types
  mockData.ts          # Mock implementations
  mcpClient.ts         # MCP client wrapper
```

---

## 📈 **MIGRATION PATH**

### **Phase 1: Mock Implementation**
- Implement all hooks with mock data
- Test with existing components
- Ensure API consistency

### **Phase 2: MCP Integration**
- Add MCP client wrapper
- Implement real MCP calls
- Add error handling

### **Phase 3: Hybrid Mode**
- Add connection detection
- Implement fallback logic
- Test seamless transitions

### **Phase 4: Optimization**
- Add caching
- Optimize re-renders
- Add performance monitoring

---

**Status:** Design Complete, Implementation Started  
**Next:** Implement useCMC hook first 💙

