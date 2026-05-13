# Section 6: Examples and Use Cases

**Status:** ✅ **EXTRACTED FROM TEXTBOOK + IMPLEMENTATION EXAMPLES**  
**Source:** PLIX Textbook + Phase 2/4 Implementation Examples  
**Last Updated:** 2025-01-27

---

## **6.1 Basic Intent Contract: Booking a Meeting Room**

### **Human-PLIX**

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
    con:duration <= 4h
  post:
    con:room_reserved == true
    con:calendar_event_created == true
    con:confirmation_sent == true
  tests:
    tst:room_confirmed
    tst:no_conflicts
  evidence:
    w:reservation_record
    w:calendar_event_id
  bt:
    tx_time: now()
```

### **Canonical JSON**

```json
{
  "speech": "ensure",
  "entity": "plix://room/meeting_room",
  "action": "book",
  "with": {
    "date": "2025-12-01",
    "duration": "2h",
    "user_id": "user123"
  },
  "pre": [
    {"expr": "room_available", "op": "==", "value": true},
    {"expr": "user_authenticated", "op": "==", "value": true},
    {"expr": "duration", "op": "<=", "value": "4h"}
  ],
  "post": [
    {"expr": "room_reserved", "op": "==", "value": true},
    {"expr": "calendar_event_created", "op": "==", "value": true},
    {"expr": "confirmation_sent", "op": "==", "value": true}
  ],
  "tests": [
    {"test": "room_confirmed"},
    {"test": "no_conflicts"}
  ],
  "evidence": [
    "plix://witness/reservation_record",
    "plix://witness/calendar_event_id"
  ],
  "bt": {
    "tx_time": "2025-01-27T12:00:00Z"
  }
}
```

### **Key Features**

- **Pure Intent:** Expresses "book a room" without specifying mechanism
- **Preconditions:** Room available, user authenticated, duration valid
- **Postconditions:** Room reserved, calendar event created, confirmation sent
- **Tests:** Room confirmed, no conflicts
- **Evidence:** Reservation record, calendar event ID
- **Bitemporal:** Transaction time tracked

---

## **6.2 Database Migration Contract**

### **Human-PLIX**

```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  with:
    version: "2025_11_11_01"
    script.ref: plix://blob/sql/ddl/users_v3#rev@h_abcd
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
    con:forall_rows unique_email
  post:
    con:schema_fingerprint == h_next
    con:migration_logged == true
  tests:
    tst:unique_email passes
    tst:rowcount_stable <= 0
  evidence:
    w:pg.schema_fingerprint_before
    w:pg.schema_fingerprint_after
  bt:
    tx_time: now()
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

### **Key Features**

- **Capability Usage:** Uses `cap:plix://tool/mcp/pg.migrate` capability
- **Complex Constraints:** Logical AND, quantified FORALL
- **Plan Steps:** Validation, execution with retry and compensation
- **Error Handling:** Network timeout retry, execution failure compensation
- **Evidence:** Schema fingerprints before/after migration

---

## **6.3 User Authentication Flow (Security-Sensitive)**

### **Human-PLIX**

```plix
ensure ent:plix://auth/user_session
  act:authenticate
  with:
    user_id: "user123"
    credentials: "${hashed_password}"
  pre:
    con:user_exists == true
    con:credentials_valid == true
    con:scor_social_signals == none
  post:
    con:session_created == true
    con:token_issued == true
    con:scor_baseline_passed == true
  tests:
    tst:session_valid
    tst:token_valid
  evidence:
    w:authentication_witness
    w:scor_baseline_result
  safety_checks:
    scor:social_signal_detection
      threshold: 0.75
    scor:adversarial_simulation
      threshold: 0.80
  bt:
    tx_time: now()
```

### **Key Features**

- **Security Integration:** SCOR social signal detection
- **Safety Checks:** SCOR baseline and adversarial simulation
- **Evidence:** Authentication witness, SCOR baseline result
- **Confidence Thresholds:** Security-sensitive thresholds (0.75, 0.80)

---

## **6.4 Data Processing Pipeline (Composition)**

### **Human-PLIX**

```plix
ensure ent:plix://data/processing_pipeline
  act:process
  with:
    input_data: "${data_source}"
    processing_steps: ["validate", "transform", "aggregate"]
  pre:
    con:data_source_available == true
    con:privacy_compliant == true
  post:
    con:data_processed == true
    con:results_stored == true
    con:provenance_tracked == true
  tests:
    tst:data_quality >= 0.90
    tst:processing_time <= 5m
  evidence:
    w:processing_witness
    w:seg_provenance_chain
  plan [
    step validate_data
      depends_on: []
    step transform_data
      depends_on: [validate_data]
    step aggregate_data
      depends_on: [transform_data]
    step store_results
      depends_on: [aggregate_data]
      compensate cleanup_results
  ]
```

### **Key Features**

- **Composition:** Multiple steps with dependencies
- **Provenance:** SEG provenance chain tracking
- **Compensation:** Cleanup on failure
- **Privacy:** Privacy compliance precondition

---

## **6.5 AI Collaboration: Handoff Task to Agent**

### **Human-PLIX**

```plix
ensure ent:plix://ai/task_handoff
  act:handoff
  with:
    task_id: "${task_id}"
    source_agent: "${source_agent_id}"
    target_agent: "${target_agent_id}"
    task_description: "${task_description}"
  pre:
    con:task_defined == true
    con:target_agent_available == true
    con:scor_anomalous_collaboration == false
  post:
    con:task_handed_off == true
    con:handoff_verified == true
  tests:
    tst:handoff_successful
  evidence:
    w:handoff_witness
    w:scor_collaboration_result
  safety_checks:
    scor:anomalous_collaboration_detection
      threshold: 0.75
    scor:agent_collaboration_baseline
      threshold: 0.80
  compensation:
    intent: "Revoke task handoff"
    steps:
      - act:reclaim_task
      - act:notify_agents
  bt:
    tx_time: now()
```

### **Key Features**

- **Multi-Agent:** Handoff between AI agents
- **SCOR Integration:** Anomalous collaboration detection
- **Compensation:** Task handoff revocation
- **Verification:** Handoff verification postcondition

---

## **6.6 Self-Improvement: Optimize System Performance**

### **Human-PLIX**

```plix
ensure ent:plix://system/performance
  act:optimize
  with:
    target_metric: "response_time"
    target_value: "< 100ms"
  pre:
    con:baseline_measured == true
    con:optimization_safe == true
  post:
    con:performance_improved == true
    con:optimization_logged == true
  tests:
    tst:response_time < 100ms
    tst:no_regressions
  evidence:
    w:performance_witness
    w:sis_optimization_trace
  plan [
    step measure_baseline
    step identify_bottlenecks
      depends_on: [measure_baseline]
    step apply_optimizations
      depends_on: [identify_bottlenecks]
    step validate_improvements
      depends_on: [apply_optimizations]
  ]
```

### **Key Features**

- **SIS Integration:** Self-Improvement System optimization trace
- **Performance Metrics:** Response time target
- **Regression Testing:** No regressions test
- **Iterative Optimization:** Measure → Identify → Apply → Validate

---

## **6.7 Compiler Integration Example**

### **PLIX → AIP Graph Compilation**

```typescript
import { PLIXParser } from '@aimos/plix';
import { PLIXToAIPCompiler } from '@aimos/plix';

// Parse PLIX
const parser = new PLIXParser();
const parseResult = parser.parse(plixText);

if (!parseResult.intent) {
  throw new Error('Parse failed');
}

// Compile to AIP graph
const compiler = new PLIXToAIPCompiler({ tagRegistry });
const aipGraph = await compiler.compileToAIPGraph(parseResult.intent);

console.log('AIP Graph Nodes:', aipGraph.nodes.length);
console.log('AIP Graph Edges:', aipGraph.edges.length);
// Output:
// AIP Graph Nodes: 8 (entity, action, 3 preconditions, 2 postconditions, 2 evidence)
// AIP Graph Edges: 10 (requires, validates, produces, requires)
```

### **PLIX → APOE Execution Plan**

```typescript
// Compile to APOE
const apoeResult = await compiler.compileToAPOE(parseResult.intent);

console.log('APOE Plan:', apoeResult.plan.name);
console.log('Steps:', apoeResult.plan.steps.length);
console.log('Witness Requirements:', apoeResult.witnessRequirements.length);
// Output:
// APOE Plan: Book Meeting Room
// Steps: 3 (validate_preconditions, reserve_room, create_calendar_event)
// Witness Requirements: 2 (reservation_witness, calendar_event_witness)
```

---

## **6.8 Registry Integration Example**

### **Tag Registration**

```typescript
import { PLIXTagRegistry } from '@aimos/plix';

const registry = new PLIXTagRegistry({ cmcClient });

// Register tag
const definition = await registry.registerTag(
  'plix://db/table/users#rev@h_98fa',
  { type: 'table', schema: 'public', columns: ['id', 'email', 'name'] },
  'A',
  'agent-123'
);

console.log('Registered tag:', definition.tag);
console.log('Authority tier:', definition.authorityTier);
```

### **Tag Resolution**

```typescript
// Resolve tag
const resolved = await registry.resolveTag('plix://db/table/users');

if (resolved) {
  console.log('Resolved:', resolved.resolved);
  console.log('Source:', resolved.source); // 'cache' | 'registry' | 'hhni' | 'seg' | 'cmc'
  console.log('Confidence:', resolved.confidence);
}
```

---

## **6.9 GGP Evolution Example**

### **Pattern Mining**

```typescript
import { PLIXGGPSystem } from '@aimos/plix';

const ggpSystem = new PLIXGGPSystem();

// Mine patterns from historical traces
const result = await ggpSystem.minePatterns(historicalTraces);

console.log('Discovered patterns:', result.patterns.length);
console.log('Confidence:', result.confidence);
console.log('Recommendations:', result.recommendations);
// Output:
// Discovered patterns: 5
// Confidence: 0.65
// Recommendations:
//   - "Consider adding 3 high-frequency patterns to official grammar"
//   - "2 emerging patterns detected - monitor for GGP proposals"
```

### **GGP Proposal Creation**

```typescript
// Create GGP proposal
const proposal = await ggpSystem.createGGPProposal(
  pattern,
  {
    problem: 'Current constraint syntax is verbose',
    solution: 'Add shorthand syntax for common constraints',
    benefits: ['Reduced verbosity', 'Improved readability'],
    risks: ['Breaking changes', 'Migration effort']
  },
  deprecationProof,
  { tier: 'A', required: 2 },
  'agent-123'
);

console.log('GGP Proposal ID:', proposal.id);
console.log('Status:', proposal.status); // 'draft'
```

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 7: Tooling and Implementation](./07_tooling.md)

