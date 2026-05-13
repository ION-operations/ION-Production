# PLIx Design Decisions - Final Synthesis & Locked Decisions

**Date:** 2025-11-09  
**Status:** 🔒 **DESIGN DECISIONS LOCKED**  
**Sources:** ChatGPT5 Questions + ChatGPT Design Review  
**Priority:** Critical - Implementation depends on these

---

## 🎯 Decision Summary Table

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Observable postconditions | **Hybrid: State queries + Events** | CMC stores state, SEG tracks events, VIF witnesses both |
| 2 | Types & units | **Lock at grammar level** | Prevents ambiguity, enables validation |
| 3 | Constraint calculus | **Hybrid: Boolean + Arithmetic** | Safe + expressive, compiles to SMT |
| 4 | IR shape | **Per-node checkpoints, task+params+intent-hash idempotency** | Matches APOE execution model |
| 5 | Confidence gate math | **Global 0.70 + per-task override + evidence learning** | Matches VIF confidence routing |
| 6 | Policy bridge | **Static compile-time + Runtime OPA** | Fail fast, gate at runtime |
| 7 | Lineage schema | **PROV + OpenLineage + CMC atom references** | Full auditability |
| 8 | Round-trip fidelity | **Strict for core, lossy for notes** | Preserves intent, allows formatting changes |
| 9 | Compensation catalog | **Required for side-effects, CI enforced** | Safety requirement |
| 10 | Error taxonomy | **5 fault types + saga reaction table** | Standardized error handling |

---

## 📋 Detailed Decisions

### **1. Observable Model for Postconditions**

**Decision:** **Hybrid Approach**

**State Queries:**
- Query CMC atoms for state snapshots
- Example: `room_reserved == true` → Query CMC for `reservation` atom
- Used for: Idempotency checks, state verification

**Witnessed Events:**
- Track events in SEG event stream
- Example: `ReservationCreated` event seen
- Used for: Real-time verification, event-driven workflows

**Adapter Functions:**
- Custom read models for complex queries
- Example: `check_room_availability()` function
- Used for: Domain-specific verification

**Implementation:**
```typescript
post: [
  { type: "state_query", condition: "room_reserved == true", source: "cmc" },
  { type: "event", condition: "ReservationCreated", source: "seg" },
  { type: "adapter", condition: "check_availability()", source: "api" }
]
```

---

### **2. Types & Units**

**Decision:** **Lock at Grammar Level**

**Required Types:**
- `datetime` - ISO 8601: `datetime("2025-12-01T10:00:00Z")`
- `duration` - ISO 8601 duration: `duration("2h")`, `duration("PT30M")`
- `money` - Currency + amount: `money("USD 100.00")`, `money("EUR 50.00")`
- `uri` - Full URI validation: `uri("https://example.com/api")`
- `email` - Email format: `email("user@example.com")`
- `uuid` - UUID v4: `uuid("550e8400-e29b-41d4-a716-446655440000")`

**Grammar:**
```yaml
params:
  date: datetime("2025-12-01T10:00:00Z")
  duration: duration("2h")
  cost: money("USD 100.00")
  endpoint: uri("https://api.example.com/rooms")
  user_email: email("user@example.com")
  reservation_id: uuid("550e8400-e29b-41d4-a716-446655440000")
```

**Validation:** Compile-time type checking, runtime validation

---

### **3. Constraint Calculus**

**Decision:** **Hybrid: Boolean + Basic Arithmetic**

**Boolean Operators:**
- `==`, `!=`, `&&`, `||`, `!`
- Example: `user_authenticated == true && room_available == true`

**Comparison Operators:**
- `<=`, `>=`, `<`, `>`
- Example: `duration <= duration("4h")`

**Arithmetic Operators:**
- `+`, `-`, `*`, `/` (for durations, money)
- Example: `total_cost == base_cost + tax`

**Functions:**
- `len()` - String/array length
- `contains()` - Array/string contains
- `matches()` - Regex match
- Example: `len(user_id) > 0 && matches(user_id, "^[a-z0-9]+$")`

**Compilation:** GBNF → AST → SMT (for formal verification)

---

### **4. IR Shape**

**Decision:** **Per-Node Checkpoints, Task+Params+Intent-Hash Idempotency**

**IR Structure:**
```typescript
interface IRPlan {
  intent: string;
  intent_hash: string;  // SHA-256 hash of intent + params
  
  nodes: IRNode[];
  edges: IREdge[];
  
  guards: {
    pre: string[];
    post: string[];
    constraints: string[];
    confidence_min: number;  // Default: 0.70
  };
  
  checkpoint_policy: "per-node" | "per-phase" | "per-intent";
  idempotency_key: string;  // Format: "${intent_hash}.${task_id}.${params_hash}"
}

interface IRNode {
  id: string;
  kind: "action" | "gate" | "checkpoint" | "compensate";
  action: string;
  params: Record<string, any>;
  deps: string[];
  compensate?: string;
  retry?: {
    max: number;
    policy: "linear" | "exponential";
    ms: number;
  };
  confidence_min?: number;  // Override global
}

interface IREdge {
  source: string;
  target: string;
  type: "depends" | "compensate" | "parallel";
}
```

**Checkpoint Policy:** `per-node` (default for v0.1)

**Idempotency:** `task+params+intent-hash`
- Format: `${intent_hash}.${task_id}.${sha256(params)}`
- Stored in CMC for deduplication

---

### **5. Confidence Gate Math**

**Decision:** **Global 0.70 + Per-Task Override + Evidence Learning**

**Formula:**
```typescript
confidence = base_confidence * evidence_multiplier

evidence_multiplier = 
  (success_rate * 0.3) +      // Historical success
  (evidence_quality * 0.2) +  // Evidence strength
  0.5                         // Base multiplier

// With decay over time
decay_factor = Math.exp(-time_since_last_use / decay_half_life)
confidence *= decay_factor
```

**Thresholds:**
- Global minimum: `0.70` (matches AIM-OS standard)
- Warning threshold: `0.80`
- Critical threshold: `0.90`
- Per-task override: Optional `confidence_min` in task

**Evidence Learning:**
- Store confidence deltas in SEG
- Update via VIF confidence tracking
- Learn from success/failure outcomes

**Implementation:**
```yaml
telemetry:
  confidence:
    global_minimum: 0.70
    warning: 0.80
    critical: 0.90
    decay_half_life: duration("7d")  # 7 days

tasks:
  - id: critical_step
    confidence_min: 0.85  # Override global
```

---

### **6. Policy Bridge**

**Decision:** **Static Compile-Time + Runtime OPA**

**Static (Compile-Time):**
- Type checking
- Syntax validation
- Dependency analysis
- Side-effect detection

**Runtime (OPA):**
- Policy evaluation
- Constraint satisfaction
- Resource limits
- Access control

**Claim Schema:**
```json
{
  "intent": "book_room",
  "task": "reserve_room",
  "params": {
    "duration": "2h",
    "room_id": "room-123"
  },
  "context": {
    "user_id": "user123",
    "timestamp": "2025-12-01T10:00:00Z",
    "session_id": "session-456"
  }
}
```

**OPA Policy:**
```rego
package plix.booking

default allow = false

allow {
    input.params.duration <= "4h"
    input.context.user_id != ""
    not calendar_conflicts(input.params.room_id, input.params.date)
}
```

**Implementation:** Both static and runtime gates, fail fast on static

---

### **7. Lineage Schema**

**Decision:** **PROV + OpenLineage + CMC Atom References**

**Event Envelopes:**
```typescript
interface RunEvent {
  eventType: "START" | "COMPLETE" | "FAIL";
  eventTime: string;  // ISO 8601
  run: { runId: string };
  job: { namespace: string; name: string };
}

interface JobEvent {
  eventType: "START" | "COMPLETE" | "FAIL";
  eventTime: string;
  job: { namespace: string; name: string };
  task: { taskId: string; action: string };
}

interface DatasetEvent {
  eventType: "READ" | "WRITE";
  eventTime: string;
  dataset: { namespace: string; name: string };
  task: { taskId: string };
}
```

**PROV Integration:**
```json
{
  "entity": {
    "urn:entity:reservation-123": {
      "prov:value": { "room_id": "room-123", "status": "reserved" }
    }
  },
  "activity": {
    "urn:activity:reserve-room": {
      "prov:type": "api.reserve_room"
    }
  },
  "wasGeneratedBy": {
    "urn:entity:reservation-123": {
      "prov:activity": "urn:activity:reserve-room"
    }
  }
}
```

**CMC Integration:** Reference CMC atom IDs in events
- `cmc_atom_id: "atom-abc123"` in event metadata
- Enables bitemporal queries

**Storage:** SEG stores events, CMC stores atom references

---

### **8. Round-Trip Fidelity**

**Decision:** **Strict for Core, Lossy for Notes**

**Perfect Round-Trip (Must Preserve):**
- ✅ Contract text (intent description)
- ✅ Step IDs (task identifiers)
- ✅ Params (parameter names and values)
- ✅ Dependencies (depends_on relationships)
- ✅ Constraints (pre/post/constraints)
- ✅ Evidence requirements/productions

**Lossy (Acceptable):**
- ❌ Freeform notes (comments, explanations)
- ❌ Formatting (whitespace, line breaks)
- ❌ Ordering (task order may change for optimization)
- ❌ Metadata (timestamps, generated fields)

**Implementation:** 
- CNL parser preserves core structure
- Round-trip tests verify core preservation
- Formatting changes acceptable

---

### **9. Compensation Catalog**

**Decision:** **Required for Side-Effects, CI Enforced**

**Rule:** Every `Task` with side effects MUST declare:
- `compensate: <task_id>` - Compensating task
- OR `compensate: none` - Explicitly marked with justification

**Side-Effect Detection:**
- Static analysis: Detect API calls, database writes, file operations
- Heuristic: Any `action` starting with `api.`, `db.`, `file.` considered side-effecting

**CI Enforcement:**
```yaml
# .github/workflows/plix-validation.yml
- name: Validate Compensations
  run: |
    python scripts/validate_compensations.py packages/plix/
    # Fails if side-effecting task missing compensation
```

**Justification Format:**
```yaml
tasks:
  - id: read_only_task
    action: api.read_data
    compensate: none  # Read-only, no side effects
    justification: "Read-only operation, no state changes"
```

---

### **10. Error Taxonomy**

**Decision:** **5 Fault Types + Saga Reaction Table**

**Fault Types:**
```typescript
enum FaultType {
  PreconditionFault = "precondition_fault",
  PolicyFault = "policy_fault",
  LowConfidenceFault = "low_confidence_fault",
  TransportFault = "transport_fault",
  SideEffectFault = "side_effect_fault"
}
```

**Saga Reaction Table:**

| Fault Type | Retry? | Compensate? | Escalate? | Example |
|------------|--------|-------------|-----------|---------|
| PreconditionFault | ❌ No | ❌ No | ✅ Yes | `room_available == false` |
| PolicyFault | ❌ No | ❌ No | ✅ Yes | OPA denied |
| LowConfidenceFault | ❌ No | ❌ No | ✅ Yes | Confidence < 0.70 |
| TransportFault | ✅ Yes | ❌ No | ✅ After max retries | Network timeout |
| SideEffectFault | ❌ No | ✅ Yes | ✅ After compensation | Partial state change |

**Implementation:**
```typescript
function handleFault(fault: Fault, saga: Saga): void {
  switch (fault.type) {
    case FaultType.PreconditionFault:
    case FaultType.PolicyFault:
    case FaultType.LowConfidenceFault:
      escalate(fault);
      break;
      
    case FaultType.TransportFault:
      if (fault.retryCount < fault.maxRetries) {
        retry(fault);
      } else {
        escalate(fault);
      }
      break;
      
    case FaultType.SideEffectFault:
      compensate(saga, fault);
      escalate(fault);
      break;
  }
}
```

---

## 🚀 Thin-Slice MVP Implementation Plan

### **Phase 1: Parser + JSON Schema** (Week 1)

**Tasks:**
1. Implement CNL parser (Gherkin-inspired)
2. Define JSON Schema for PLIx-0.1
3. Type/unit validation
4. Error messages

**Deliverables:**
- `packages/plix/src/parser/cnl-parser.ts`
- `packages/plix/src/models/schema.ts` (updated)
- `packages/plix/src/validation/types.ts`

---

### **Phase 2: Lowering to IR** (Week 1-2)

**Tasks:**
1. Implement PLIx → IR lowering
2. Idempotency key generation
3. Retry/backoff logic
4. Compensation mapping

**Deliverables:**
- `packages/plix/src/compiler/lower.ts`
- `packages/plix/src/models/ir.ts`
- `packages/plix/src/utils/idempotency.ts`

---

### **Phase 3: Guards** (Week 2)

**Tasks:**
1. VIF confidence gate integration
2. OPA policy callout (minimal policy)
3. Constraint evaluation

**Deliverables:**
- `packages/plix/src/guards/confidence-gate.ts`
- `packages/plix/src/guards/policy-gate.ts`
- `packages/plix/src/guards/constraint-gate.ts`

---

### **Phase 4: Execution Adapter** (Week 2-3)

**Tasks:**
1. Mock API implementation
2. Happy path execution
3. Saga compensation paths

**Deliverables:**
- `packages/plix/src/runtime/executor.ts`
- `packages/plix/src/runtime/saga.ts`
- `packages/plix/src/adapters/mock-api.ts`

---

### **Phase 5: Evidence Emitters** (Week 3)

**Tasks:**
1. PROV event emission
2. OpenLineage event emission
3. SEG/CMC integration

**Deliverables:**
- `packages/plix/src/provenance/prov-emitter.ts`
- `packages/plix/src/provenance/openlineage-emitter.ts`
- `packages/plix/src/integration/seg-integration.ts`

---

### **Phase 6: Tests** (Week 3-4)

**Tasks:**
1. Contract tests (compile-time)
2. Constraint property tests
3. Safety tests
4. Execution tests
5. Evidence tests

**Deliverables:**
- `packages/plix/src/__tests__/contract.test.ts`
- `packages/plix/src/__tests__/constraints.test.ts`
- `packages/plix/src/__tests__/safety.test.ts`
- `packages/plix/src/__tests__/execution.test.ts`
- `packages/plix/src/__tests__/evidence.test.ts`

---

## 📊 Implementation Status

**Current State:**
- ✅ Design decisions locked
- ✅ Schema defined (partial)
- ✅ IR structure defined (partial)
- ⏳ Parser implementation (pending)
- ⏳ Compiler implementation (pending)
- ⏳ Runtime implementation (pending)

**Next Steps:**
1. Update `packages/plix/src/models/schema.ts` with locked decisions
2. Create `packages/plix/src/models/ir.ts` with IR structure
3. Implement parser (Phase 1)
4. Implement compiler (Phase 2)
5. Build MVP (Phases 3-6)

---

**Status:** 🔒 **DESIGN LOCKED - READY FOR IMPLEMENTATION**  
**Priority:** High - Begin MVP implementation  
**Timeline:** 4 weeks for thin-slice MVP

