# Chapter 20: PLIX-to-AIP Compiler: Complete Integration

**Part:** IV - Compilation  
**Chapter:** 20  
**Target Word Count:** 3,000-3,500 words  
**Status:** ✅ **COMPLETE**  
**Priority:** ⚠️ **CRITICAL** - Essential for AIM-OS integration

---

## Introduction

In previous chapters, we explored PLIx syntax, constraints, error handling, and tag systems. We saw how PLIx contracts express intent declaratively, but we haven't yet explored how these contracts are **compiled** into executable systems.

The **PLIX-to-AIP Compiler** is the bridge between PLIx contracts and AIM-OS execution. It transforms PLIx contracts into:

1. **AIP Graph:** Graph representation of intent (entities, actions, constraints, evidence)
2. **APOE Execution Plans:** Executable plans with dependencies, retries, compensation
3. **VIF Witness Requirements:** Verification requirements for intent achievement

This chapter explores the complete compilation process—from PLIx contracts to AIM-OS execution. By the end, you'll understand how PLIx integrates with AIM-OS systems and how to write contracts that compile effectively.

---

## Section 20.1: PLIX → AIP Graph Compilation

### The AIP Graph Model

The AIP (AIM-OS Integration Protocol) graph represents intent as a **graph structure**:

- **Nodes:** Entities, actions, capabilities, constraints, tests, evidence
- **Edges:** Dependencies, compensations, requirements, productions, validations

### Mapping PLIX to AIP Nodes

**Entity Nodes:**
```typescript
// PLIX: ent:plix://db/table/users#rev@h_98fa
// AIP Node:
{
  id: 'entity',
  type: 'entity',
  tag: 'plix://db/table/users#rev@h_98fa',
  resolved: { type: 'database_table', schema: 'public', name: 'users' },
  metadata: { source: 'registry', confidence: 0.95 }
}
```

**Action/Capability Nodes:**
```typescript
// PLIX: act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
// AIP Node:
{
  id: 'action',
  type: 'capability',
  tag: 'plix://tool/mcp/pg.migrate#rev@h_2a10',
  resolved: { type: 'mcp_tool', tool: 'pg.migrate', ... },
  metadata: { source: 'registry', confidence: 0.90 }
}
```

**Constraint Nodes:**
```typescript
// PLIX: pre: con:schema_intact == h_prev
// AIP Node:
{
  id: 'pre_0',
  type: 'constraint',
  metadata: {
    constraint: { type: 'basic', expr: 'schema_intact', op: '==', value: 'h_prev' },
    type: 'precondition'
  }
}
```

**Test Nodes:**
```typescript
// PLIX: tests: tst:unique_email passes
// AIP Node:
{
  id: 'test_0',
  type: 'test',
  metadata: {
    test: 'unique_email',
    bound: { op: '==', value: true }
  }
}
```

**Evidence Nodes:**
```typescript
// PLIX: evidence: w:plix://witness/schema_before
// AIP Node:
{
  id: 'evidence_0',
  type: 'evidence',
  tag: 'plix://witness/schema_before',
  resolved: { type: 'vif_witness', witness_type: 'schema_fingerprint', ... },
  metadata: { source: 'seg', confidence: 0.85 }
}
```

### Mapping PLIX to AIP Edges

**Dependency Edges:**
```typescript
// PLIX: plan [ step step2 depends_on: [step1] ]
// AIP Edge:
{
  source: 'step1',
  target: 'step2',
  type: 'depends_on'
}
```

**Compensation Edges:**
```typescript
// PLIX: step reserve_room compensate release_room
// AIP Edge:
{
  source: 'reserve_room',
  target: 'release_room',
  type: 'compensates'
}
```

**Requirement Edges:**
```typescript
// PLIX: Entity requires action
// AIP Edge:
{
  source: 'entity',
  target: 'action',
  type: 'requires'
}
```

**Validation Edges:**
```typescript
// PLIX: Constraint validates action
// AIP Edge:
{
  source: 'pre_0',
  target: 'action',
  type: 'validates'
}
```

**Production Edges:**
```typescript
// PLIX: Action produces postcondition
// AIP Edge:
{
  source: 'action',
  target: 'post_0',
  type: 'produces'
}
```

### Complete AIP Graph Example

**PLIX Contract:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:schema_intact == h_prev
    con:rowcount_stable <= 0
  post:
    con:schema_fingerprint == h_next
  tests:
    tst:unique_email passes
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
```

**AIP Graph:**
```typescript
{
  nodes: [
    { id: 'entity', type: 'entity', tag: 'plix://db/table/users#rev@h_98fa', ... },
    { id: 'action', type: 'capability', tag: 'plix://tool/mcp/pg.migrate#rev@h_2a10', ... },
    { id: 'pre_0', type: 'constraint', metadata: { constraint: {...}, type: 'precondition' } },
    { id: 'pre_1', type: 'constraint', metadata: { constraint: {...}, type: 'precondition' } },
    { id: 'post_0', type: 'constraint', metadata: { constraint: {...}, type: 'postcondition' } },
    { id: 'test_0', type: 'test', metadata: { test: 'unique_email' } },
    { id: 'evidence_0', type: 'evidence', tag: 'plix://witness/schema_before', ... },
    { id: 'evidence_1', type: 'evidence', tag: 'plix://witness/schema_after', ... }
  ],
  edges: [
    { source: 'entity', target: 'action', type: 'requires' },
    { source: 'pre_0', target: 'action', type: 'validates' },
    { source: 'pre_1', target: 'action', type: 'validates' },
    { source: 'action', target: 'post_0', type: 'produces' },
    { source: 'action', target: 'test_0', type: 'validates' },
    { source: 'action', target: 'evidence_0', type: 'produces' },
    { source: 'action', target: 'evidence_1', type: 'produces' }
  ]
}
```

---

## Section 20.2: Tag Resolution via HHNI/SEG/CMC

### Multi-Source Tag Resolution

The compiler resolves tags using a **multi-source strategy**:

**Resolution Priority:**
1. **Tag Registry** (authoritative) - Primary source, cached
2. **HHNI** (semantic search) - Entity/action lookups
3. **SEG** (evidence/lineage) - Evidence resolution
4. **CMC** (general lookup) - General storage

### Resolution Process

**Step 1: Check Tag Registry**
```typescript
if (tagRegistry) {
  const resolved = await tagRegistry.resolveTag(tag);
  if (resolved) {
    return { resolved: resolved.resolved, source: 'registry', confidence: 0.95 };
  }
}
```

**Step 2: Query HHNI (Semantic Search)**
```typescript
if (hhniClient) {
  const hhniResult = await hhniClient.semanticSearch(tag);
  if (hhniResult && hhniResult.similarity > 0.80) {
    return { resolved: hhniResult.entity, source: 'hhni', confidence: hhniResult.similarity };
  }
}
```

**Step 3: Query SEG (Evidence/Lineage)**
```typescript
if (segClient) {
  const segResult = await segClient.queryEvidence(tag);
  if (segResult) {
    return { resolved: segResult.evidence, source: 'seg', confidence: 0.85 };
  }
}
```

**Step 4: Query CMC (General Lookup)**
```typescript
if (cmcClient) {
  const cmcResult = await cmcClient.retrieve_memory({ query: tag, limit: 1 });
  if (cmcResult && cmcResult.results.length > 0) {
    return { resolved: JSON.parse(cmcResult.results[0].content), source: 'cmc', confidence: 0.70 };
  }
}
```

### Resolution Caching

**Cache Strategy:**
```typescript
// Check cache first
if (tagCache.has(tag)) {
  const cached = tagCache.get(tag);
  if (cached.confidence >= 0.80) {
    return cached;  // Use cached result
  }
}

// Resolve tag
const resolved = await resolveTag(tag);

// Cache result
tagCache.set(tag, resolved);
```

### Resolution Examples

**Example 1: Registry Resolution**
```typescript
const tag = 'plix://db/table/users#rev@h_98fa';
const resolved = await compiler.resolveTag(tag);
// Returns: { resolved: {...}, source: 'registry', confidence: 0.95 }
```

**Example 2: HHNI Semantic Search**
```typescript
const tag = 'plix://db/table/users';  // No revision
const resolved = await compiler.resolveTag(tag);
// Returns: { resolved: {...}, source: 'hhni', confidence: 0.88 }
// HHNI found similar entity with 88% similarity
```

**Example 3: SEG Evidence Resolution**
```typescript
const tag = 'plix://witness/schema_before';
const resolved = await compiler.resolveTag(tag);
// Returns: { resolved: {...}, source: 'seg', confidence: 0.85 }
// SEG found evidence witness
```

---

## Section 20.3: PLIX → APOE Execution Plan

### APOE Execution Plan Structure

APOE (Atomic Provenance Orchestration Engine) execution plans include:

- **Plan Name:** Intent name
- **Steps:** Execution steps with dependencies
- **Dependencies:** Step dependency graph
- **Gates:** Error handling gates
- **Budgets:** Retry/timeout budgets

### Plan Step Mapping

**PLIX Step:**
```plix
step execute_migration
  retry 3 backoff exponential(100ms, 2s) jitter
  on_error: net.timeout -> retry with retry(3, 100ms, 2s)
  on_error: execution.failed -> compensate rollback_migration
  compensate rollback_migration
```

**APOE Step:**
```typescript
{
  id: 'execute_migration',
  step: 'execute_migration',
  agent: 'aether',
  tool: 'pg.migrate',
  target: 'plix://db/table/users#rev@h_98fa',
  args: { version: '2025_11_11_01', script: 'plix://blob/sql/ddl/users_v3#rev@h_abcd' },
  depends_on: ['validate_preconditions'],
  retry: {
    max: 3,
    backoff: 'exponential',
    min_delay: '100ms',
    max_delay: '2s',
    jitter: true
  },
  errors: [
    { on: 'net.timeout', action: 'retry', config: { retry: { max: 3, min_delay: '100ms', max_delay: '2s' } } },
    { on: 'execution.failed', action: 'compensate', config: { compensate: 'rollback_migration' } }
  ],
  compensate: 'rollback_migration'
}
```

### Dependency Graph Mapping

**PLIX Plan:**
```plix
plan [
  step validate_preconditions
  step execute_migration
    depends_on: [validate_preconditions]
  step validate_postconditions
    depends_on: [execute_migration]
]
```

**APOE Dependency Graph:**
```typescript
{
  steps: [
    { id: 'validate_preconditions', depends_on: [] },
    { id: 'execute_migration', depends_on: ['validate_preconditions'] },
    { id: 'validate_postconditions', depends_on: ['execute_migration'] }
  ],
  deps: [
    { from: 'validate_preconditions', to: 'execute_migration' },
    { from: 'execute_migration', to: 'validate_postconditions' }
  ]
}
```

### Error Clause → APOE Gate Mapping

**PLIX Error Clause:**
```plix
on_error: net.timeout -> retry with retry(3, 100ms, 2s)
```

**APOE Gate:**
```typescript
{
  type: 'error_gate',
  condition: { error_type: 'net.timeout' },
  action: 'retry',
  config: {
    retry: {
      max: 3,
      min_delay: '100ms',
      max_delay: '2s'
    }
  }
}
```

### Retry Specification → APOE Budget Mapping

**PLIX Retry:**
```plix
retry 3 backoff exponential(100ms, 2s) jitter
```

**APOE Budget:**
```typescript
{
  retry: {
    max: 3,
    backoff: 'exponential',
    min_delay: '100ms',
    max_delay: '2s',
    jitter: true
  },
  timeout: {
    step: '30s',
    plan: '5m'
  }
}
```

### Complete APOE Compilation Example

**PLIX Contract:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  plan [
    step validate_preconditions
      on_error: constraint.violated -> fail
    step execute_migration
      retry 3 backoff exponential(100ms, 2s) jitter
      on_error: net.timeout -> retry with retry(3, 100ms, 2s)
      on_error: execution.failed -> compensate rollback_migration
      compensate rollback_migration
  ]
```

**APOE Execution Plan:**
```typescript
{
  name: 'migrate_users_table',
  steps: [
    {
      id: 'validate_preconditions',
      step: 'validate_preconditions',
      agent: 'aether',
      tool: 'validate',
      target: 'plix://db/table/users#rev@h_98fa',
      args: {},
      depends_on: [],
      errors: [
        { on: 'constraint.violated', action: 'fail' }
      ]
    },
    {
      id: 'execute_migration',
      step: 'execute_migration',
      agent: 'aether',
      tool: 'pg.migrate',
      target: 'plix://db/table/users#rev@h_98fa',
      args: { version: '2025_11_11_01' },
      depends_on: ['validate_preconditions'],
      retry: {
        max: 3,
        backoff: 'exponential',
        min_delay: '100ms',
        max_delay: '2s',
        jitter: true
      },
      errors: [
        { on: 'net.timeout', action: 'retry', config: { retry: { max: 3, min_delay: '100ms', max_delay: '2s' } } },
        { on: 'execution.failed', action: 'compensate', config: { compensate: 'rollback_migration' } }
      ],
      compensate: 'rollback_migration'
    }
  ],
  deps: [
    { from: 'validate_preconditions', to: 'execute_migration' }
  ]
}
```

---

## Section 20.4: VIF Witness Requirement Generation

### Witness Requirements

VIF (Verifiable Intelligence Framework) witness requirements specify:

- **Operation:** Which operation requires witness
- **Step ID:** Which step requires witness (if step-level)
- **Required Confidence:** Minimum confidence threshold
- **Evidence Types:** Types of evidence required
- **Metadata:** Additional witness metadata

### Plan-Level Witness Requirements

**PLIX Contract:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
  telemetry:
    confidenceThresholds:
      minimum: 0.70
      warning: 0.80
      critical: 0.90
```

**VIF Witness Requirements:**
```typescript
[
  {
    operation: 'migrate_users_table',
    requiredConfidence: 0.70,
    evidenceTypes: ['schema_fingerprint_before', 'schema_fingerprint_after'],
    metadata: {
      warning_threshold: 0.80,
      critical_threshold: 0.90
    }
  }
]
```

### Step-Level Witness Requirements

**PLIX Contract:**
```plix
plan [
  step execute_migration
    evidence:
      w:plix://witness/migration_log
    telemetry:
      confidenceThresholds:
        minimum: 0.75
]
```

**VIF Witness Requirements:**
```typescript
[
  {
    operation: 'migrate_users_table',
    stepId: 'execute_migration',
    requiredConfidence: 0.75,
    evidenceTypes: ['migration_log'],
    metadata: {}
  }
]
```

### Confidence Threshold Mapping

**PLIX Telemetry:**
```plix
telemetry:
  confidenceThresholds:
    minimum: 0.70
    warning: 0.80
    critical: 0.90
```

**VIF Witness Requirements:**
```typescript
{
  requiredConfidence: 0.70,  // minimum threshold
  metadata: {
    warning_threshold: 0.80,
    critical_threshold: 0.90
  }
}
```

### Evidence Type Mapping

**PLIX Evidence:**
```plix
evidence:
  w:plix://witness/schema_before
  w:plix://witness/schema_after
```

**VIF Evidence Types:**
```typescript
{
  evidenceTypes: [
    'schema_fingerprint_before',  // Resolved from tag
    'schema_fingerprint_after'    // Resolved from tag
  ]
}
```

### Complete Witness Generation Example

**PLIX Contract:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
  telemetry:
    confidenceThresholds:
      minimum: 0.70
      warning: 0.80
      critical: 0.90
  plan [
    step execute_migration
      evidence:
        w:plix://witness/migration_log
      telemetry:
        confidenceThresholds:
          minimum: 0.75
  ]
```

**VIF Witness Requirements:**
```typescript
[
  {
    operation: 'migrate_users_table',
    requiredConfidence: 0.70,
    evidenceTypes: ['schema_fingerprint_before', 'schema_fingerprint_after'],
    metadata: {
      warning_threshold: 0.80,
      critical_threshold: 0.90
    }
  },
  {
    operation: 'migrate_users_table',
    stepId: 'execute_migration',
    requiredConfidence: 0.75,
    evidenceTypes: ['migration_log'],
    metadata: {}
  }
]
```

---

## Section 20.5: Complete Integration Examples

### Example 1: Database Migration (Full Flow)

**PLIX Contract:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  with:
    version: "2025_11_11_01"
    script.ref: plix://blob/sql/ddl/users_v3#rev@h_abcd
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
  post:
    con:schema_fingerprint == h_next
    con:migration_logged == true
  tests:
    tst:unique_email passes
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
  telemetry:
    confidenceThresholds:
      minimum: 0.70
  plan [
    step validate_preconditions
      on_error: constraint.violated -> fail
    step execute_migration
      retry 3 backoff exponential(100ms, 2s) jitter
      on_error: net.timeout -> retry with retry(3, 100ms, 2s)
      on_error: execution.failed -> compensate rollback_migration
      compensate rollback_migration
  ]
```

**Compilation Flow:**
1. **Parse PLIX** → PLIxIntent object
2. **Resolve Tags** → Entity, capability, evidence tags resolved
3. **Compile AIP Graph** → Graph with nodes and edges
4. **Compile APOE Plan** → Execution plan with steps, dependencies, errors
5. **Generate VIF Witnesses** → Witness requirements for verification

**Result:**
- **AIP Graph:** 8 nodes (entity, action, 2 preconditions, 1 postcondition, 1 test, 2 evidence), 7 edges
- **APOE Plan:** 2 steps with dependencies, retry, error handling, compensation
- **VIF Witnesses:** 1 plan-level witness requirement (confidence 0.70)

### Example 2: Room Booking (Full Flow)

**PLIX Contract:**
```plix
ensure ent:plix://room/meeting_room
  act:book
  with:
    date: "2025-12-01"
    duration: "2h"
    user_id: "user123"
  pre:
    con:room_available == true
    con:user_authenticated == true
  post:
    con:room_reserved == true
    con:calendar_event_created == true
  evidence:
    w:plix://witness/reservation_record
    w:plix://witness/calendar_event_id
  plan [
    step check_availability
    step reserve_room
      depends_on: [check_availability]
      compensate release_room
      on_error: execution.failed -> compensate release_room
  ]
```

**Compilation Flow:**
1. **Parse PLIX** → PLIxIntent object
2. **Resolve Tags** → Room entity, reservation capability, evidence tags
3. **Compile AIP Graph** → Graph with booking flow
4. **Compile APOE Plan** → Execution plan with availability check → reservation
5. **Generate VIF Witnesses** → Witness requirements for reservation proof

**Result:**
- **AIP Graph:** 6 nodes (entity, action, 2 preconditions, 2 postconditions, 2 evidence), 6 edges
- **APOE Plan:** 2 steps with dependency, compensation
- **VIF Witnesses:** 1 plan-level witness requirement

### Example 3: User Authentication (Full Flow)

**PLIX Contract:**
```plix
ensure ent:plix://auth/user_session
  act:authenticate
  with:
    user_id: "user123"
    credentials: "${hashed_password}"
  pre:
    con:user_exists == true
    con:credentials_valid == true
  post:
    con:session_created == true
    con:token_issued == true
  evidence:
    w:plix://witness/authentication_witness
  telemetry:
    confidenceThresholds:
      minimum: 0.80
      warning: 0.85
      critical: 0.90
  plan [
    step validate_credentials
      on_error: auth.invalid -> fail
    step create_session
      depends_on: [validate_credentials]
      on_error: execution.failed -> fail
  ]
```

**Compilation Flow:**
1. **Parse PLIX** → PLIxIntent object
2. **Resolve Tags** → Auth entity, authentication capability, witness tag
3. **Compile AIP Graph** → Graph with authentication flow
4. **Compile APOE Plan** → Execution plan with validation → session creation
5. **Generate VIF Witnesses** → Witness requirements with high confidence thresholds

**Result:**
- **AIP Graph:** 5 nodes (entity, action, 2 preconditions, 2 postconditions, 1 evidence), 5 edges
- **APOE Plan:** 2 steps with dependency, error handling
- **VIF Witnesses:** 1 plan-level witness requirement (confidence 0.80, warning 0.85, critical 0.90)

---

## Section 20.6: Integration Best Practices

### Tag Usage Best Practices

**1. Use Specific Tags**
```plix
# Good: Specific tag with revision
ent:plix://db/table/users#rev@h_98fa

# Bad: Ambiguous tag
ent:plix://db/table/users
```

**2. Register Tags Before Use**
```typescript
// Good: Register tag before using in contract
await registry.registerTag('plix://db/table/users', {...}, 'A', ...);

// Then use in PLIX contract
ensure ent:plix://db/table/users
  ...
```

**3. Use Appropriate Authority Tiers**
```plix
# Good: Production tag with tier A
ent:plix://db/table/users#rev@h_98fa  # Tier A

# Good: Development tag with tier B
ent:plix://db/table/users_dev#rev@h_abcd  # Tier B
```

### Constraint Best Practices

**1. Use Logical Constraints for Complex Conditions**
```plix
# Good: Logical AND
pre:
  con:(schema_intact == h_prev) AND (rowcount_stable <= 0)

# Bad: Multiple separate constraints (less clear)
pre:
  con:schema_intact == h_prev
  con:rowcount_stable <= 0
```

**2. Use Quantified Constraints for Collections**
```plix
# Good: Quantified constraint
pre:
  con:forall_rows unique_email

# Bad: Manual iteration (not expressible in PLIX)
# (Would require plan steps, not constraints)
```

**3. Use Temporal Constraints for Time-Based Conditions**
```plix
# Good: Temporal constraint
pre:
  con:eventually_true(payment_received, within_ms=5000)

# Bad: Plan step timeout (less declarative)
# (Would require plan step with timeout, not constraint)
```

### Error Handling Best Practices

**1. Retry Transient Errors**
```plix
# Good: Retry network timeout
on_error: net.timeout -> retry with retry(3, 100ms, 2s)

# Bad: Fail on transient error
on_error: net.timeout -> fail
```

**2. Compensate Reversible Operations**
```plix
# Good: Compensate reversible operation
step reserve_room
  compensate release_room
  on_error: execution.failed -> compensate release_room

# Bad: No compensation for reversible operation
step reserve_room
  on_error: execution.failed -> fail
```

**3. Escalate Policy Violations**
```plix
# Good: Escalate policy violation
on_error: policy.denied -> escalate admin

# Bad: Fail on policy violation (should be escalated)
on_error: policy.denied -> fail
```

### Performance Optimization

**1. Cache Tag Resolutions**
```typescript
// Good: Cache tag resolutions
const resolved = await compiler.resolveTag(tag);
// Cache hit rate: >80%

// Bad: Resolve tags repeatedly
// (Compiler handles caching automatically)
```

**2. Use Specific Queries**
```typescript
// Good: Specific namespace query
await registry.queryTags({ namespace: 'db', limit: 100 });

// Bad: Query all tags (inefficient)
await registry.queryTags({ limit: 10000 });
```

**3. Optimize Constraint Evaluation**
```plix
# Good: Simple constraints evaluated first (short-circuit)
pre:
  con:(simple_check == true) AND (complex_check == true)

# Bad: Complex constraints evaluated first
pre:
  con:(complex_check == true) AND (simple_check == true)
```

---

## Chapter 20 Summary

The PLIX-to-AIP Compiler bridges PLIx contracts and AIM-OS execution:

1. **PLIX → AIP Graph:** Graph representation of intent (entities, actions, constraints, evidence)
2. **Tag Resolution:** Multi-source lookup via Registry → HHNI → SEG → CMC
3. **PLIX → APOE Plan:** Executable plans with dependencies, retries, compensation
4. **VIF Witness Generation:** Verification requirements for intent achievement
5. **Complete Integration:** Full flow from PLIX contracts to AIM-OS execution

**Key Takeaways:**
1. **AIP Graph:** Graph structure represents intent as nodes and edges
2. **Tag Resolution:** Multi-source strategy ensures tags can always be resolved
3. **APOE Compilation:** PLIX plans compile to executable APOE plans
4. **VIF Witnesses:** Witness requirements enable verification of intent achievement
5. **Best Practices:** Tag usage, constraints, error handling, performance optimization

**Next:** Chapter 21 explores PLIX runtime implementation—how PLIX contracts are executed with durable execution, recovery, and error handling.

---

**Word Count:** ~3,400 words  
**Status:** ✅ **COMPLETE**  
**Cross-References:**
- Chapter 5: Tag System (tag resolution)
- Chapter 15: Tag Registry (registry integration)
- Chapter 11-14: AIM-OS Integration (all systems)
- Spec Section 4: Semantics (compilation semantics)
- Spec Section 7.2: Compiler API

