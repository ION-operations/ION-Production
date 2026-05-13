# PLIx Design Decisions & Open Questions (ChatGPT Feedback Synthesis)

**Date:** 2025-11-09  
**Source:** ChatGPT Design Review  
**Status:** 🔴 **CRITICAL - NEED DECISIONS**  
**Priority:** High - Lock these before implementation

---

## 🎯 What We've Nailed (ChatGPT Validation)

ChatGPT confirms our core design is solid:

✅ **Pure intent layer** - Cleanly separated from mechanism  
✅ **Contract → Execution → Safety → Evidence stack** - Coherent architecture  
✅ **CNL (Gherkin-inspired) + DbC** - Human-legible with formal contracts  
✅ **Runtime guardrails** - Confidence gates, adaptive routing, policy-as-code  
✅ **Provenance as primitive** - W3C PROV + OpenLineage + bitemporal CMC

---

## 🔴 10 Critical Design Decisions (Lock Now)

### **1. Observable Model for Postconditions**

**Question:** How do `post:` predicates bind to concrete state/read models?

**Options:**
- **A)** State queries: `room_reserved == true` (query state store)
- **B)** Witnessed events: `ReservationCreated` seen (event stream)
- **C)** Hybrid: Both state queries and events

**Recommendation:** **C) Hybrid** - Support both:
- State queries for idempotency checks
- Events for real-time verification
- Adapter functions for custom read models

**AIM-OS Integration:**
- CMC atoms store state snapshots
- SEG tracks event lineage
- VIF witnesses capture both

---

### **2. Types & Units**

**Question:** Lock scalar types and unit semantics at grammar level?

**Required Types:**
- `datetime` - ISO 8601 format
- `duration` - `2h`, `30m`, `1d`
- `money` - `USD 100.00`, `EUR 50.00`
- `uri` - Full URI validation
- `email` - Email format validation
- `uuid` - UUID format validation

**Grammar Level:**
```yaml
params:
  date: datetime("2025-12-01T10:00:00Z")
  duration: duration("2h")
  cost: money("USD 100.00")
```

**Recommendation:** **YES** - Lock types at grammar level to prevent ambiguity

---

### **3. Constraint Calculus**

**Question:** Minimal expression language for `pre/post/constraints`?

**Options:**
- **A)** Pure boolean (safe, simple)
- **B)** Arithmetic predicates (expressive, complex)
- **C)** Hybrid: Boolean + basic arithmetic

**Recommendation:** **C) Hybrid** - Boolean + basic arithmetic:
- Boolean: `==`, `!=`, `&&`, `||`, `!`
- Comparison: `<=`, `>=`, `<`, `>`
- Arithmetic: `+`, `-`, `*`, `/` (for durations, money)
- Functions: `len()`, `contains()`, `matches()`

**Compilation:** GBNF → AST → SMT (for formal verification)

---

### **4. IR Shape**

**Question:** Specify PLIx → IR lowering structure?

**Required IR Elements:**
- Node kinds: `action`, `gate`, `checkpoint`, `compensate`
- Edges: `depends`, `compensate`, `parallel`
- Checkpoint policy: `per-node`, `per-phase`, `per-intent`
- Idempotency keys: `task+params+intent-hash`
- Retry/backoff: `max`, `policy` (linear/exponential), `ms`

**IR Structure:**
```json
{
  "nodes": [
    {
      "id": "check_availability",
      "kind": "action",
      "retry": {"max": 3, "policy": "exponential", "ms": 1000}
    }
  ],
  "edges": [
    {"source": "check_availability", "target": "reserve_room", "type": "depends"}
  ],
  "checkpoints": "per-node",
  "idempotency": "task+params+intent-hash"
}
```

**Recommendation:** Lock IR structure in `packages/plix/src/models/ir.ts`

---

### **5. Confidence Gate Math**

**Question:** Exact formula & thresholds?

**Components:**
- Global minimum: `0.70` (default)
- Per-action prior: Override per task
- Decay/boost from evidence: Historical success rate
- Persist confidence deltas: Store in SEG for learning

**Formula:**
```
confidence = base_confidence * evidence_multiplier
evidence_multiplier = (success_rate * 0.3) + (evidence_quality * 0.2) + 0.5
```

**Recommendation:** 
- Global min: `0.70`
- Per-action override: Optional `confidence_min` in task
- Evidence learning: Store in SEG, update via VIF

---

### **6. Policy Bridge**

**Question:** Map `constraints:` → static checks + runtime OPA?

**Mapping:**
- **Static (compile-time):** Type checking, syntax validation, dependency analysis
- **Runtime (OPA):** Policy evaluation, constraint satisfaction, resource limits

**Claim Schema:**
```json
{
  "intent": "book_room",
  "task": "reserve_room",
  "params": {"duration": "2h"},
  "context": {"user_id": "user123", "timestamp": "2025-12-01T10:00:00Z"}
}
```

**Recommendation:** 
- Static: Compile-time validation
- Runtime: OPA evaluation with claim schema
- Both: Fail fast on static, gate on runtime

---

### **7. Lineage Schema**

**Question:** Minimal event envelopes?

**Required Events:**
- `RunEvent` - Intent execution start/complete/fail
- `JobEvent` - Task execution start/complete/fail
- `DatasetEvent` - Data read/write events
- `PROV` - Entities, activities, relations
- `OpenLineage` - Job/Dataset lineage

**Event Schema:**
```json
{
  "eventType": "START|COMPLETE|FAIL",
  "eventTime": "2025-12-01T10:00:00Z",
  "run": {"runId": "run-123"},
  "job": {"namespace": "aimos/plix", "name": "reserve_room"},
  "provenance": {
    "entity": "urn:entity:reservation-123",
    "activity": "urn:activity:reserve-room",
    "wasGeneratedBy": "urn:activity:reserve-room"
  }
}
```

**CMC Integration:** Reference CMC atom IDs in events

**Recommendation:** Lock schema in `packages/plix/src/models/provenance.ts`

---

### **8. Round-Trip Fidelity**

**Question:** What must be perfectly reversible NL ↔ PLIx?

**Perfect Round-Trip:**
- ✅ Contract text (intent description)
- ✅ Step IDs (task identifiers)
- ✅ Params (parameter names and values)
- ✅ Dependencies (depends_on relationships)
- ✅ Constraints (pre/post/constraints)

**Lossy (Acceptable):**
- ❌ Freeform notes (comments, explanations)
- ❌ Formatting (whitespace, line breaks)
- ❌ Ordering (task order may change)

**Recommendation:** Document round-trip guarantees in PLIx spec

---

### **9. Compensation Catalog**

**Question:** Require compensator for every side-effecting task?

**Rule:** Every `Task` with side effects MUST declare:
- `compensate: <task_id>` - Compensating task
- OR `compensate: none` - Explicitly marked with justification

**CI Enforcement:**
- Static analysis: Detect side effects
- Require compensation declaration
- Fail build if missing

**Recommendation:** **YES** - Enforce compensation catalog in CI

---

### **10. Error Taxonomy**

**Question:** Standardize fault types and saga reaction table?

**Fault Types:**
- `PreconditionFault` - Pre-condition failed
- `PolicyFault` - Policy denied
- `LowConfidenceFault` - Confidence below threshold
- `TransportFault` - Network/API error
- `SideEffectFault` - Side effect divergence

**Saga Reaction Table:**
| Fault Type | Retry? | Compensate? | Escalate? |
|------------|--------|-------------|-----------|
| PreconditionFault | No | No | Yes |
| PolicyFault | No | No | Yes |
| LowConfidenceFault | No | No | Yes |
| TransportFault | Yes | No | After max retries |
| SideEffectFault | No | Yes | After compensation |

**Recommendation:** Lock error taxonomy in `packages/plix/src/models/errors.ts`

---

## 📋 Minimal PLIx-0.1 Grammar (ChatGPT Proposal)

**Stable Core:**
```yaml
intent: "Book a meeting room"

context:
  purpose: "Enable collaboration"

tasks:
  - id: check_availability
    action: api.check_room_availability
    params: { date: datetime("2025-12-01"), duration: duration("2h") }
    retry: { max: 3, backoff: exponential, backoff_ms: 1000 }

  - id: reserve_room
    action: api.reserve_room
    params: { room_id: ${check_availability.room_id}, duration: duration("2h") }
    depends_on: [check_availability]
    compensate: cancel_reservation

  - id: cancel_reservation
    action: api.cancel_reservation
    params: { reservation_id: ${reserve_room.res_id} }

constraints:
  - duration <= duration("4h")
  - calendar_conflicts == none

contract:
  pre:
    - user_authenticated == true
    - room_available == true
  post:
    - room_reserved == true
    - calendar_event_created == true

evidence:
  require: [calendar.open_slots]
  produce: [reservation.record]
```

**IR (Lowered):**
```json
{
  "nodes": [
    {
      "id": "check_availability",
      "kind": "action",
      "retry": {"max": 3, "policy": "exponential", "ms": 1000}
    },
    {
      "id": "reserve_room",
      "kind": "action",
      "deps": ["check_availability"],
      "compensate": "cancel_reservation"
    },
    {
      "id": "cancel_reservation",
      "kind": "action",
      "compensates": "reserve_room"
    }
  ],
  "guards": {
    "pre": ["user_authenticated", "room_available"],
    "post": ["room_reserved", "calendar_event_created"],
    "constraints": ["duration <= 4h", "calendar_conflicts == none"],
    "confidence_min": 0.72
  },
  "checkpoints": "per-node",
  "idempotency": "task+params+intent-hash"
}
```

---

## 🧪 Test Matrix (ChatGPT Proposal)

### **Contract Tests (Compile-Time)**
- ✅ Parses valid PLIx
- ✅ Rejects unknown keywords/units
- ✅ Fails build if `Task` missing `compensate` and side-effects declared

### **Constraint Property Tests**
- ✅ `duration <= 4h` → Generate cases: `1h`✅, `4h`✅, `4h1m`❌
- ✅ `calendar_conflicts == none` → Simulate conflict, ensure gate stops plan

### **Safety Tests**
- ✅ Force low confidence (< threshold) → Execution short-circuits with `LowConfidence` fault
- ✅ SEG stores rationale

### **Execution Tests**
- ✅ Inject failure after `reserve_room` → Saga triggers `cancel_reservation`
- ✅ State converges

### **Evidence Tests**
- ✅ On success: PROV entity/activity + OpenLineage START/COMPLETE emitted
- ✅ On failure: START/FAIL + compensation lineage present

---

## 🚀 Thin-Slice MVP (ChatGPT Recommendation)

**6 Components:**

1. **Parser + JSON Schema** - PLIx-0.1 (units/types + error messages)
2. **Lowering to IR** - Idempotency keys, retries, compensations
3. **Guards** - VIF confidence gate + OPA policy callout (minimal policy)
4. **Execution Adapter** - Mock API + happy/saga paths
5. **Evidence Emitters** - PROV + OpenLineage minimal events to SEG/CMC
6. **Tests** - From matrix above wired into CI

---

## 📝 10 Quick Questions to Lock Scope

1. **Postconditions:** State queries or witnessed events? → **Hybrid**
2. **Round-trip:** Strict NL ↔ PLIx or normalized? → **Strict for core, normalized for notes**
3. **Confidence:** Global floor or per-action priors? → **Global floor + per-action override**
4. **Constraints:** Hard policies or soft hints? → **Hard policies (OPA)**
5. **Checkpoint cadence:** Per node vs per intent phase? → **Per node**
6. **Compensations:** Best-effort or terminal state? → **Terminal state with retries**
7. **Evidence retention:** Full lineage forever or roll-up? → **Full lineage (CMC bitemporal)**
8. **Required types:** Dates, durations, decimals, enums? → **All + URI, email, UUID**
9. **Parallel tasks:** Fan-out/fan-in now or sequential? → **Sequential for v0.1**
10. **PLIx location:** Own package or embedded in APOE? → **Own package with adapters**

---

## 🎯 Next Steps

1. **Lock Design Decisions** - Answer all 10 questions definitively
2. **Update PLIx Schema** - Incorporate decisions into `packages/plix/src/models/schema.ts`
3. **Create IR Model** - Define IR structure in `packages/plix/src/models/ir.ts`
4. **Implement Parser** - CNL → PLIx → IR lowering
5. **Build MVP** - Thin-slice implementation with tests

---

**Status:** 🔴 **AWAITING DECISIONS**  
**Priority:** High - Lock before implementation  
**Owner:** PLIx Design Team

