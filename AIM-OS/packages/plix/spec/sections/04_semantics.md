# Section 4: Semantics (Meaning and Execution)

**Status:** ✅ **FORMALIZED WITH HOARE LOGIC**  
**Source:** PLIX Textbook Part II: Architecture (Chapters 5-8) + Phase 2 Compiler  
**Last Updated:** 2025-01-27

---

## **4.1 Operational Pipeline**

### **Execution Flow**

**8-Step Pipeline:**
1. **Resolve:** Resolve tags via registry (HHNI/SEG/CMC)
2. **Authorize:** Validate authority tier and permissions
3. **Check Pre:** Evaluate preconditions
4. **Execute:** Execute plan steps via APOE
5. **Tests:** Run test specifications
6. **Evidence:** Collect evidence/witnesses via VIF
7. **Post:** Verify postconditions
8. **Emit:** Emit provenance events to SEG

### **Pipeline Diagram**

```
PLIX Intent
    ↓
[1] Resolve Tags (Registry/HHNI/SEG/CMC)
    ↓
[2] Authorize (Authority Tier Check)
    ↓
[3] Check Preconditions (Constraint Evaluation)
    ↓
[4] Execute Plan (APOE Execution)
    ↓
[5] Run Tests (Test Specification Execution)
    ↓
[6] Collect Evidence (VIF Witness Generation)
    ↓
[7] Verify Postconditions (Constraint Evaluation)
    ↓
[8] Emit Provenance (SEG Event Emission)
    ↓
Result + Witnesses
```

### **Pipeline Details**

**Step 1: Resolve Tags**
- Resolve entity tags via registry/HHNI
- Resolve capability tags via registry/SEG
- Cache resolved tags for performance
- Handle unresolved tags (error or fallback)

**Step 2: Authorize**
- Validate authority tier for operation
- Check permissions for capability access
- Escalate if insufficient authority
- Record authorization decision

**Step 3: Check Preconditions**
- Evaluate all preconditions
- Check constraint satisfaction
- Fail if any precondition fails
- Record precondition checks

**Step 4: Execute Plan**
- Compile plan to APOE execution plan
- Execute steps in dependency order
- Handle retries and fallbacks
- Track execution progress

**Step 5: Run Tests**
- Execute test specifications
- Verify test results
- Fail if tests fail (based on `onTestFail` policy)
- Record test results

**Step 6: Collect Evidence**
- Generate VIF witnesses for operations
- Collect evidence requirements
- Verify evidence quality
- Store evidence in SEG

**Step 7: Verify Postconditions**
- Evaluate all postconditions
- Check constraint satisfaction
- Fail if any postcondition fails
- Record postcondition checks

**Step 8: Emit Provenance**
- Emit SEG events for intent execution
- Track intent lineage
- Record intent-outcome mapping
- Update evidence graph

---

## **4.2 Contract Semantics (Hoare Logic)**

### **Hoare Triple Format**

**Standard Format:**
```
{pre} plan.execute() {post}
```

**Where:**
- `pre`: Set of preconditions (must hold before execution)
- `post`: Set of postconditions (must hold after execution)
- `plan.execute()`: Execution of the plan steps

### **Formal Semantics**

**Precondition Semantics:**
```
∀c ∈ pre: eval(c, state_before) = true
```

**Postcondition Semantics:**
```
∀c ∈ post: eval(c, state_after) = true
```

**Plan Execution Semantics:**
```
state_after = execute(plan, state_before)
```

**Complete Hoare Triple:**
```
{∀c ∈ pre: eval(c, state_before) = true}
  execute(plan, state_before)
{∀c ∈ post: eval(c, state_after) = true}
```

### **Hoare Triple Examples**

**Example 1: Database Migration**
```
{schema_intact == h_prev ∧ rowcount_stable <= 0}
  migrate(version: "v2.0")
{schema_fingerprint == h_next ∧ migration_logged == true}
```

**Example 2: Room Reservation**
```
{room_available == true ∧ user_authenticated == true}
  reserve_room(date: "2025-12-01", duration: "2h")
{room_reserved == true ∧ calendar_event_created == true}
```

**Example 3: User Authentication**
```
{user_exists == true ∧ credentials_valid == true}
  authenticate(user_id: "user123")
{session_created == true ∧ token_issued == true}
```

### **Hoare Logic Rules**

**Rule 1: Precondition Enforcement**
- Preconditions must hold before execution
- Execution fails if any precondition fails
- Precondition failure → compensation or escalation

**Rule 2: Postcondition Guarantee**
- Postconditions must hold after execution
- Execution fails if any postcondition fails
- Postcondition failure → rollback or compensation

**Rule 3: Invariant Preservation**
- Invariants must hold throughout execution
- Invariant violation → immediate failure
- Invariant checks at each step

**Rule 4: Compensation Logic**
- If execution fails, compensation must restore pre-state
- Compensation must satisfy: `{post} compensate() {pre}`
- Compensation failure → escalation

---

## **4.3 Type System**

### **Type Hierarchy**

**Core Types:**
- `Entity`: Tagged entity references
- `Action`: Action identifiers
- `Capability<In, Out>`: Typed capabilities with input/output types
- `Constraint`: Constraint expressions (evaluable to boolean)
- `Test`: Test specifications (executable)
- `Evidence`: Evidence references (resolve to witnesses)

### **Type Inference**

**Tag Resolution:**
- Tags resolve to entity types via registry
- Entity type determined by namespace (e.g., `db` → `Entity`)
- Type information stored in registry

**Action Inference:**
- Actions infer types from capability signatures
- Capability signature: `Capability<In, Out>`
- Action type: `Action<In, Out>`

**Constraint Inference:**
- Constraints infer types from expression evaluation
- Constraint type: `Constraint → Boolean`
- Type checking: ensure constraint evaluates to boolean

### **Type Rules**

**Rule 1: Tag Type Consistency**
- Tags must resolve to consistent types
- Type mismatch → error
- Type checking via registry

**Rule 2: Action-Capability Compatibility**
- Actions must match capability signatures
- Input/output types must match
- Type checking via capability resolution

**Rule 3: Constraint Type Safety**
- Constraints must evaluate to boolean
- Type checking via constraint evaluation
- Type errors → compilation error

---

## **4.4 Effect System**

### **Effect Types**

**Read Effect:**
- Read-only access (no side effects)
- Safe for parallel execution
- No state modification

**Write Effect:**
- Write access (modifies state)
- Requires authority tier ≥ B
- State modification tracked

**Execute Effect:**
- Execution capability (runs actions)
- Requires capability resolution
- Action execution tracked

**Witness Effect:**
- Evidence generation (creates witnesses)
- Requires VIF integration
- Witness generation tracked

### **Effect Inference**

**Action Effects:**
- Actions with `Write` effect require authority tier ≥ B
- Actions with `Execute` effect require capability resolution
- Actions with `Witness` effect require VIF integration

**Effect Rules:**
- If action has `Write` effect → must have auth tier ≥ B
- If action has `Execute` effect → must resolve capability tag
- If action has `Witness` effect → must produce VIF witness

### **Effect Examples**

**Read Effect:**
```plix
ask ent:plix://db/table/users
  act:query
  with: filter: "active == true"
```
Effect: `Read` (no state modification)

**Write Effect:**
```plix
ensure ent:plix://db/table/users
  act:update
  with: user_id: "user123", status: "active"
```
Effect: `Write` (requires auth tier ≥ B)

**Execute Effect:**
```plix
ensure ent:plix://db/schema/public
  using cap:plix://tool/mcp/pg.migrate
  with: version: "v2.0"
```
Effect: `Execute` (requires capability resolution)

**Witness Effect:**
```plix
ensure ent:plix://db/schema/public
  act:migrate
  evidence:
    ev:plix://witness/schema_before
    ev:plix://witness/schema_after
```
Effect: `Witness` (requires VIF integration)

---

## **4.5 Bitemporal Rules**

### **Transaction Time Rules**

**Rule 1: Immutability**
- `tx_time` is set at intent creation and never changes
- Enables append-only audit trail
- Prevents retroactive modifications

**Rule 2: Monotonicity**
- `tx_time` increases monotonically
- Later intents have later `tx_time`
- Enables timeline reconstruction

**Rule 3: Completeness**
- Every intent must have `tx_time`
- `tx_time` defaults to creation time if not specified
- Enables temporal queries

### **Valid Time Rules**

**Rule 1: Mutability**
- `valid_time` can be updated (bitemporal versioning)
- Old versions preserved (bitemporal history)
- Enables "what was valid when" queries

**Rule 2: Consistency**
- `valid_time` must be consistent with `tx_time`
- Cannot have `valid_time` before `tx_time`
- Temporal queries respect both times

**Rule 3: Completeness**
- `valid_time` is optional (defaults to `tx_time`)
- If specified, must be valid time range
- Enables temporal queries

### **Bitemporal Query Semantics**

**Query at Transaction Time:**
```
query(tx_time = T) → {intents where tx_time <= T}
```
"What did we know at time T?"

**Query at Valid Time:**
```
query(valid_time = T) → {intents where valid_time contains T}
```
"What was valid at time T?"

**Query Both:**
```
query(tx_time = T1, valid_time = T2) → {intents where tx_time <= T1 AND valid_time contains T2}
```
"What did we know was valid at time T2 when we recorded it at time T1?"

---

## **4.6 Contradiction Handling**

### **Contradiction Detection**

**SEG Integration:**
- SEG detects contradictions via evidence graph
- Contradictions identified via `contradicts` edges
- Contradiction detection triggers resolution

**Detection Process:**
1. SEG analyzes evidence graph
2. Identifies contradictory claims
3. Reports contradictions with authority tiers
4. Triggers resolution process

### **Resolution Rules**

**Rule 1: Authority-Weighted Resolution**
- Higher authority tier wins
- Tier comparison: S > A > B > C
- Authority-weighted resolution

**Rule 2: Recency-Weighted Resolution**
- More recent evidence wins (if same tier)
- Timestamp comparison
- Recency-weighted resolution

**Rule 3: Escalation**
- Escalation if contradiction persists
- Human operator intervention
- Escalation recorded in timeline

### **Resolution Examples**

**Example 1: Authority-Weighted**
- Claim A: Tier A, "room available"
- Claim B: Tier B, "room unavailable"
- Resolution: Claim A wins (A > B)

**Example 2: Recency-Weighted**
- Claim A: Tier A, timestamp T1, "room available"
- Claim B: Tier A, timestamp T2 (T2 > T1), "room unavailable"
- Resolution: Claim B wins (same tier, more recent)

**Example 3: Escalation**
- Contradiction persists after resolution attempts
- Escalation to human operator
- Operator decision recorded

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 5: Layer Model and Extensions](./05_evolution.md)

