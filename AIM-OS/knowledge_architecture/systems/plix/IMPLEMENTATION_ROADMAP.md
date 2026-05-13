# PLIx Implementation Roadmap - Thin-Slice MVP

**Date:** 2025-11-09  
**Status:** 📋 **READY TO START**  
**Timeline:** 4 weeks  
**Based on:** ChatGPT Design Review + Locked Decisions

---

## 🎯 MVP Goal

**"Build a minimal, testable PLIx-0.1 implementation that demonstrates pure intent expression, recoverable execution, conformance gating, and verifiable lineage."**

**Success Criteria:**
- ✅ Parse CNL → PLIx → IR
- ✅ Execute simple intent (room booking)
- ✅ Handle failures with saga compensation
- ✅ Emit provenance events
- ✅ Pass all test matrix tests

---

## 📅 Week-by-Week Plan (Updated with Perplexity Priorities)

### **Week 1-2: PLIx → APOE Compiler** ⭐ **PRIORITY 1**

**Goal:** Compile PLIx contracts to APOE execution plans

**Tasks:**
1. Implement CNL parser (Gherkin-inspired)
   - Lexical analysis: CNL text → tokens
   - Syntax analysis: tokens → AST
   - Semantic analysis: AST → validated AST
   - Contract generation: AST → PLIx contract

2. Define JSON Schema for PLIx-0.1
   - Update `packages/plix/src/models/schema.ts`
   - Add explicit AIM-OS references (SEG, CMC, VIF, SIS)
   - Add type definitions: `datetime`, `duration`, `money`, `uri`, `email`, `uuid`
   - Add unit validation

3. Implement PLIx → IR lowering
   - Create `packages/plix/src/models/ir.ts`
   - Lower PLIx contract to IR structure
   - Handle dependencies, compensations, retries

4. **PLIx → APOE Compiler** (NEW - Priority 1)
   - IR to APOE plan generator
   - Output: JSON-serialized APOE chains
   - Test: Compile booking example → verify chain structure

**Deliverables:**
- `packages/plix/src/parser/cnl-parser.ts`
- `packages/plix/src/models/schema.ts` (updated with AIM-OS references)
- `packages/plix/src/validation/types.ts`
- `packages/plix/src/validation/units.ts`
- `packages/plix/src/compiler/lower.ts`
- `packages/plix/src/models/ir.ts`
- `packages/plix/src/compiler/apoe-generator.ts` ⭐ **NEW**
- `packages/plix/src/integration/apoe-integration.ts` ⭐ **NEW**

**Tests:**
- Parse valid CNL ✅
- Reject unknown keywords/units ✅
- Type validation ✅
- Lower PLIx → IR ✅
- Compile PLIx → APOE plan ✅ ⭐ **NEW**
- Execute APOE plan ✅ ⭐ **NEW**

---

### **Week 2-3: APOE ↔ CMC Integration + Tagging** ⭐ **PRIORITY 2**

**Goal:** Store PLIx intents and outcomes in CMC with advanced tagging

**Tasks:**
1. Plan atoms in CMC with tags (goal, steps, status)
   - Store PLIx intent as CMC atom
   - Tag with intent ID, status, metadata
   - **CMC Tags Integration:** Use CMC tags for intent categorization
     - `plix_intent`, `plix_status`, `plix_category`, `plix_priority`
   - **TPV Integration:** Add TPV for temporal relevance decay
   - Enable retrieval by intent

2. VIF gates determine when to execute vs research
   - Integrate VIF confidence gates
   - Route to SIS.research if confidence < threshold
   - Store confidence scores in CMC

3. Outcome atoms capture postcondition achievement
   - Store postcondition verification results
   - Link to original intent atom
   - Enable outcome queries

4. Idempotency key generation
   - Format: `${intent_hash}.${task_id}.${params_hash}`
   - SHA-256 hashing
   - Store in CMC for deduplication

5. Retry/backoff logic
   - Linear and exponential backoff
   - Max retry limits
   - Store retry attempts in CMC

6. Compensation mapping
   - Map compensate relationships
   - Validate compensation catalog
   - Store compensation history in CMC

**Deliverables:**
- `packages/plix/src/integration/cmc-integration.ts` ⭐ **NEW**
- `packages/plix/src/integration/cmc-tagging.ts` ⭐ **NEW** (CMC tags integration)
- `packages/plix/src/utils/idempotency.ts`
- `packages/plix/src/guards/confidence-gate.ts`
- CMC atom schema for PLIx intents ⭐ **NEW**
- Retrieval queries for intent history ⭐ **NEW**
- Tag-based intent queries ⭐ **NEW**

**Tests:**
- Store intent in CMC ✅ ⭐ **NEW**
- Retrieve intent from CMC ✅ ⭐ **NEW**
- Store outcome in CMC ✅ ⭐ **NEW**
- End-to-end: intent → plan → atom → retrieval ✅ ⭐ **NEW**
- Idempotency key generation ✅
- Confidence gate (low confidence fails) ✅

---

### **Week 3: SEG Contradiction Detector** ⭐ **PRIORITY 3**

**Goal:** Detect when PLIx intents are violated

**Tasks:**
1. PLIx intent vs actual outcome anchored in SEG
   - Store intent as SEG entity
   - Store outcome as SEG entity
   - Create relation: intent → outcome

2. Detect: Intent violated? Postcondition failed?
   - Compare postconditions with actual outcomes
   - Detect contradictions
   - Flag violations

3. Create remediation atoms in SIS
   - Generate improvement hypotheses
   - Store in SIS for future learning
   - Link to original intent

4. PROV event emission
   - Generate PROV-JSON
   - Entities, activities, relations
   - Store in SEG

5. OpenLineage event emission
   - RunEvent (START/COMPLETE/FAIL)
   - JobEvent (task execution)
   - DatasetEvent (data read/write)

6. SEG/CMC integration
   - Store events in SEG
   - Reference CMC atoms
   - Build evidence chains

**Deliverables:**
- `packages/plix/src/integration/seg-contradiction-detector.ts` ⭐ **NEW**
- `packages/plix/src/integration/seg-integration.ts`
- `packages/plix/src/provenance/prov-emitter.ts`
- `packages/plix/src/provenance/openlineage-emitter.ts`
- SEG evidence schema for PLIx intents ⭐ **NEW**
- Contradiction detection logic ⭐ **NEW**

**Tests:**
- Detect intent violation ✅ ⭐ **NEW**
- Detect postcondition failure ✅ ⭐ **NEW**
- Create remediation atoms ✅ ⭐ **NEW**
- Introduce intentional failure, verify detection ✅ ⭐ **NEW**
- PROV events emitted ✅
- OpenLineage events emitted ✅

---

### **Week 4: SIS Dream Generator + NL Tags + Tests** ⭐ **PRIORITY 4**

**Goal:** Learn from failed PLIx intents, integrate NL tags, and complete test matrix

**Tasks:**
1. Observe: Failed PLIx intents → common failure patterns
   - Extract patterns from CMC failure atoms
   - Identify common failure modes
   - Build failure pattern database

2. Generate: Improvement hypotheses (new postconditions, guards, tactics)
   - Propose new postconditions
   - Suggest additional guards
   - Recommend tactics

3. Validate: Run SDF-CVF gates on improvements
   - Validate improvement hypotheses
   - Check for contradictions
   - Verify feasibility

4. Contract tests (compile-time)
   - Parse valid PLIx ✅
   - Reject unknown keywords/units ✅
   - Fail build if missing compensation ✅

5. Constraint property tests
   - `duration <= 4h` → Generate test cases ✅
   - `calendar_conflicts == none` → Simulate conflict ✅

6. Safety tests
   - Force low confidence → Short-circuit ✅
   - SEG stores rationale ✅

7. Execution tests
   - Inject failure → Saga compensation ✅
   - State converges ✅

8. Evidence tests
   - Success: PROV + OpenLineage ✅
   - Failure: START/FAIL + compensation lineage ✅

9. **NL Tags Integration** ⭐ **NEW**
   - Tag PLIx contracts with canonical IDs
   - Link contracts to APOE plans, SEG evidence, VIF gates
   - Implement dependency tracking
   - Cross-system tag propagation

10. AIM-OS integration tests
   - APOE integration (compile IR → ExecutionPlan)
   - Router integration (use existing bandit routing)
   - VIF integration (confidence gates)
   - CMC integration (checkpoints + tags)
   - SEG integration (evidence chains)
   - TCS integration (timeline tracking)
   - SIS integration (dream generation) ⭐ **NEW**
   - NL Tags integration (cross-system linking) ⭐ **NEW**

**Deliverables:**
- `packages/plix/src/integration/sis-dream-generator.ts` ⭐ **NEW**
- `packages/plix/src/integration/nl-tags-integration.ts` ⭐ **NEW** (NL tags integration)
- `packages/plix/src/__tests__/contract.test.ts`
- `packages/plix/src/__tests__/constraints.test.ts`
- `packages/plix/src/__tests__/safety.test.ts`
- `packages/plix/src/__tests__/execution.test.ts`
- `packages/plix/src/__tests__/evidence.test.ts`
- `packages/plix/src/integration/aimos-integration.ts`
- Pattern extraction from intent failures ⭐ **NEW**
- Improvement hypothesis generation ⭐ **NEW**
- NL tag canonical IDs for PLIx contracts ⭐ **NEW**

**Tests:**
- Extract failure patterns ✅ ⭐ **NEW**
- Generate improvement hypotheses ✅ ⭐ **NEW**
- Validate improvements ✅ ⭐ **NEW**
- Propose improvements, verify they prevent past failures ✅ ⭐ **NEW**
- All test matrix tests passing ✅
- AIM-OS integration working ✅

---

## 📊 Success Metrics

**Week 1:**
- ✅ CNL parser parses room booking example
- ✅ Type validation catches errors
- ✅ Schema validates correctly

**Week 2:**
- ✅ PLIx → IR lowering works
- ✅ Confidence gate blocks low confidence
- ✅ OPA policy evaluation works

**Week 3:**
- ✅ Room booking executes successfully
- ✅ Failure triggers compensation
- ✅ Provenance events emitted

**Week 4:**
- ✅ All tests passing
- ✅ Integrated with AIM-OS systems
- ✅ End-to-end demo works

---

## 🔧 Technical Stack

**Parser:**
- Chevrotain (or similar) for CNL parsing
- TypeScript for type safety

**IR:**
- TypeScript interfaces
- JSON Schema validation

**Execution:**
- Node.js/TypeScript runtime
- Mock API for testing

**Integration:**
- Python bindings for AIM-OS (APOE, Router, CMC, SEG, VIF, TCS)
- HTTP/gRPC for cross-language calls

---

---

## 🚀 Future Enhancements (Post-MVP)

### **Phase 5: ICIP Integration** (Weeks 5-8)

**Goal:** Enhance PLIx with ICIP codebase intelligence

**Tasks:**
1. **ICIP CPG → CMC Integration**
   - Convert ICIP Code Property Graph nodes to CMC atoms
   - Tag nodes with `plix_relevant` tags
   - Enable PLIx code context queries

2. **ICIP Patterns → PLIx Intent Learning**
   - Store ICIP patterns in SEG
   - Link patterns to PLIx intents
   - Enable pattern-based intent learning

3. **ICIP Events → PLIx Real-Time Validation**
   - Stream ICIP events to TCS
   - Monitor code changes for PLIx relevance
   - Implement intent re-validation on code changes

4. **ICIP Predictions → PLIx Proactive Planning**
   - Store ICIP predictions in SEG
   - Use predictions for PLIx planning
   - Integrate confidence scores

**Deliverables:**
- `packages/plix/src/integration/icip-cpg-integration.ts`
- `packages/plix/src/integration/icip-pattern-learning.ts`
- `packages/plix/src/integration/icip-realtime-validation.ts`
- `packages/plix/src/integration/icip-predictive-planning.ts`

**Benefits:**
- ✅ Code context understanding for PLIx
- ✅ Pattern-based intent learning
- ✅ Real-time intent validation
- ✅ Proactive intent planning

---

## 📝 Example: Room Booking (Target)

**CNL Input:**
```cnl
Intent: Book a meeting room on 2025-12-01 for 2h

Task check_availability:
  Action: api.check_room_availability
  Params: date=datetime("2025-12-01"), duration=duration("2h")
  Retry: max=3, backoff=exponential, backoff_ms=1000

Task reserve_room:
  Action: api.reserve_room
  Params: room_id=${check_availability.room_id}, duration=duration("2h")
  Depends: check_availability
  Compensate: cancel_reservation

Task cancel_reservation:
  Action: api.cancel_reservation
  Params: reservation_id=${reserve_room.res_id}

Constraints:
  duration <= duration("4h")
  calendar_conflicts == none

Contract:
  Pre:
    - user_authenticated == true
    - room_available == true
  Post:
    - room_reserved == true
    - calendar_event_created == true

Evidence:
  Require: [calendar.open_slots]
  Produce: [reservation.record]
```

**Expected Output:**
- ✅ Parses successfully
- ✅ Lowers to IR
- ✅ Executes via APOE
- ✅ Emits provenance
- ✅ Handles failures with compensation

---

## 🎯 Next Steps

1. **Start Week 1:** Implement CNL parser
2. **Lock Schema:** Update `packages/plix/src/models/schema.ts` with decisions
3. **Create IR Model:** Define `packages/plix/src/models/ir.ts`
4. **Build Incrementally:** One component at a time
5. **Test Continuously:** Write tests as you build

---

**Status:** 📋 **READY TO START**  
**Timeline:** 4 weeks  
**Priority:** High

