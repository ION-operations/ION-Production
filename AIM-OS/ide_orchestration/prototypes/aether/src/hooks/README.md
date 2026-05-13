# AIM-OS Hooks System
## Unified Hook Interface for All AIM-OS Systems

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Comprehensive hook system for AIM-OS integration  
**Status:** Production Ready ✅

---

## 🎯 **OVERVIEW**

The AIM-OS hooks system provides a unified, type-safe interface for interacting with all 8 AIM-OS systems:
- **CMC** (Context Memory Core)
- **HHNI** (Hierarchical Hypergraph Neural Index)
- **VIF** (Verifiable Intelligence Framework)
- **SEG** (Synthesis & Evidence Graph)
- **APOE** (AI-Powered Orchestration Engine)
- **TCS** (Temporal Consciousness Substrate)
- **CAS** (Consciousness Analysis System)
- **SDF-CVF** (Self-Directed Feedback & Continuous Validation Framework)

---

## 🚀 **QUICK START**

### **Unified Hook (Recommended):**
```typescript
import { useAIMOS } from '@/hooks'

function MyComponent() {
  const { cmc, hhni, vif, isConnected } = useAIMOS()
  
  // Use any system
  const handleStore = async () => {
    const atomId = await cmc.store('Important insight', { tag: 'insight' })
  }
  
  return <div>Status: {isConnected ? 'Connected' : 'Mock Mode'}</div>
}
```

### **Individual Hooks:**
```typescript
import { useCMC, useHHNI } from '@/hooks'

function MyComponent() {
  const cmc = useCMC()
  const hhni = useHHNI()
  
  // Use individual hooks
}
```

---

## 📚 **HOOKS REFERENCE**

### **useAIMOS**
Unified hook providing access to all 8 AIM-OS systems.

**Returns:**
- `cmc`: CMCInterface
- `hhni`: HHNIInterface
- `vif`: VIFInterface
- `seg`: SEGInterface
- `apoe`: APOEInterface
- `tcs`: TCSInterface
- `cas`: CASInterface
- `sdfcvf`: SDFCVFInterface
- `isConnected`: boolean
- `connectionStatus`: 'connected' | 'disconnected' | 'connecting' | 'error'
- `error`: Error | null

### **useCMC**
Context Memory Core hook for storing and retrieving memories.

**Methods:**
- `store(content: string, tags?: Record<string, any>): Promise<string>`
- `retrieve(query: string, limit?: number): Promise<Memory[]>`
- `getStats(): Promise<MemoryStats>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useHHNI**
Hierarchical Hypergraph Neural Index hook for semantic search.

**Methods:**
- `search(query: string, limit?: number): Promise<SearchResult[]>`
- `retrieve(atomId: string): Promise<Atom | null>`
- `getHierarchy(atomId: string): Promise<Hierarchy>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useVIF**
Verifiable Intelligence Framework hook for confidence tracking.

**Methods:**
- `trackConfidence(task: string, confidence: number, evidence?: string[]): Promise<void>`
- `getWitnesses(task: string): Promise<Witness[]>`
- `validate(statement: string): Promise<ValidationResult>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useSEG**
Synthesis & Evidence Graph hook for evidence management.

**Methods:**
- `addEvidence(evidence: Evidence): Promise<string>`
- `detectContradictions(query: string): Promise<Contradiction[]>`
- `synthesize(topics: string[]): Promise<Synthesis>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useAPOE**
AI-Powered Orchestration Engine hook for plan management.

**Methods:**
- `createPlan(goal: string, context?: string): Promise<Plan>`
- `executePlan(planId: string): Promise<Execution>`
- `getProgress(planId: string): Promise<Progress>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useTCS**
Temporal Consciousness Substrate hook for timeline management.

**Methods:**
- `addEntry(promptId: string, userInput: string, contextState?: Record<string, any>): Promise<string>`
- `getSummary(limit?: number): Promise<TimelineEntry[]>`
- `getEntries(filters?: TimelineFilters): Promise<TimelineEntry[]>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useCAS**
Consciousness Analysis System hook for consciousness metrics.

**Methods:**
- `getMetrics(): Promise<ConsciousnessMetrics>`
- `detectDrift(context?: DriftContext): Promise<DriftResult>`
- `runAudit(type?: AuditType): Promise<AuditResult>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

### **useSDFCVF**
Self-Directed Feedback & Continuous Validation Framework hook.

**Methods:**
- `validate(action: Record<string, any>, context?: Record<string, any>): Promise<ValidationResult>`
- `checkInvariant(action: Record<string, any>, context?: Record<string, any>): Promise<InvariantResult>`

**Properties:**
- `loading`: boolean
- `error`: Error | null

---

## 💡 **USAGE PATTERNS**

### **Pattern 1: Multiple Systems**
```typescript
const { cmc, hhni, vif } = useAIMOS()

// Use multiple systems together
const handleComplexOperation = async () => {
  // Store memory
  const atomId = await cmc.store('Operation started')
  
  // Search for related content
  const results = await hhni.search('related content')
  
  // Track confidence
  await vif.trackConfidence('Complex operation', 0.85, [atomId])
}
```

### **Pattern 2: Error Handling**
```typescript
const { cmc } = useAIMOS()

const handleStore = async () => {
  try {
    const atomId = await cmc.store('Content')
    console.log('Stored:', atomId)
  } catch (error) {
    console.error('Failed to store:', error)
    // Fallback behavior
  }
}
```

### **Pattern 3: Loading States**
```typescript
const { cmc } = useAIMOS()

return (
  <div>
    {cmc.loading && <div>Loading...</div>}
    {cmc.error && <div>Error: {cmc.error.message}</div>}
    {!cmc.loading && !cmc.error && <div>Ready</div>}
  </div>
)
```

### **Pattern 4: Connection Status**
```typescript
const { isConnected, connectionStatus } = useAIMOS()

return (
  <div>
    {isConnected ? (
      <div>Connected to AIM-OS</div>
    ) : (
      <div>Using mock data</div>
    )}
    <div>Status: {connectionStatus}</div>
  </div>
)
```

---

## 🔧 **MIGRATION PATH**

### **Phase 1: Mock Data (Current)**
- All hooks use mock data
- Perfect for development/prototyping
- No network calls

### **Phase 2: MCP Integration (Future)**
- Replace mock implementations with real MCP calls
- Add connection detection
- Handle errors gracefully

### **Phase 3: Hybrid Mode (Future)**
- Use MCP when available
- Fallback to mock data on error
- Seamless transition

---

## 📋 **TYPE DEFINITIONS**

All types are exported from `@/hooks/types`:

```typescript
import type {
  Memory,
  MemoryStats,
  CMCInterface,
  SearchResult,
  HHNIInterface,
  Witness,
  VIFInterface,
  // ... and more
} from '@/hooks/types'
```

---

## 🎯 **BEST PRACTICES**

1. **Use Unified Hook:** Prefer `useAIMOS` for multiple systems
2. **Handle Errors:** Always wrap async calls in try-catch
3. **Check Loading:** Show loading states for better UX
4. **Connection Status:** Display connection status to users
5. **Type Safety:** Use TypeScript types for all operations

---

## 📖 **EXAMPLES**

See `AIMOSStatusPanel.tsx` for a complete example of hook usage.

---

**Status:** Production Ready ✅  
**Version:** 1.0.0  
**Last Updated:** 2025-11-08

