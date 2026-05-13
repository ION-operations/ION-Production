# PLIx Grammar Specification (ChatGPT-Informed)

**Date:** 2025-11-09  
**Status:** 📋 **GRAMMAR SPECIFICATION**  
**Source:** ChatGPT Research + Gemini Framework

---

## Grammar Overview

PLIx uses a **controlled natural-language style** (like Gherkin) that is **human-legible yet machine-strict**. The grammar balances readability with formality, enabling bidirectional translation between NL and code.

---

## YAML/JSON Schema Structure

### Complete Example

```yaml
# Intent Section (ChatGPT: IntentSection)
intent: "Book a meeting room"

# Context (Gemini: Context)
context:
  entities: ["MeetingRoom", "Calendar", "User"]
  scope: "office_booking"
  risk: 0.3

# Contract Section (Gemini: Contract Layer)
contract:
  pre:
    - "room_available == true"
    - "user_authenticated == true"
  post:
    - "room_reserved == true"
    - "calendar_event_created == true"
  capabilities:
    - "calendar_api"
    - "room_management_api"
  policies:
    - "duration <= 4h"
    - "calendar_conflicts == none"
  invariants:
    - "user_permissions_valid == true"
  
  # DSL Structure (Gemini: SmaCoNat methodology)
  dsl_structure:
    rules:
      - type: "Heading"
        content: "Meeting Room Booking"
      - type: "Event"
        content: "BookRoom"
    ontology: ["BOOK", "CHECK", "RESERVE"]
  
  # Formal Validation (Gemini: Alloy/TLA+)
  formal_validation:
    alloy_model: |
      sig Room { available: Bool }
      pred bookRoom[r: Room] { r.available = True }
    validation_status: "pending"
  
  # Layer-1 Guards (Gemini: Fast constraints)
  layer1_guards:
    json_schema:
      type: "object"
      properties:
        duration:
          type: "number"
          maximum: 4
    regex_constraints:
      - "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"  # Date format
  
  # Layer-2 Validators (Gemini: Rigorous semantic)
  layer2_validators:
    shacl_shapes: []
    smt_solvers: []

# Task List (ChatGPT: TaskList)
tasks:
  - step: "Check availability"
    id: "check_availability"
    action: api.check_room_availability
    params:
      date: "2025-12-01"
      duration: 2h
    agent: "booking_agent"
    target: "meeting_rooms"
    retry:
      max_attempts: 3
      backoff: "exponential"
      backoff_ms: 1000
  
  - step: "Reserve room"
    id: "reserve_room"
    action: api.reserve_room
    params:
      room_id: "<from_previous_step>"
      user_id: "<context.user_id>"
    agent: "booking_agent"
    target: "meeting_rooms"
    depends_on: ["check_availability"]
    compensate:
      action: api.cancel_reservation
      tool: "room_api"
      args:
        room_id: "<from_previous_step>"

# Constraints (ChatGPT: ConstraintList)
constraints:
  - "duration <= 4h"
  - "calendar_conflicts == none"
  - "user_age >= 18"

# Evidence (ChatGPT: EvidenceList)
evidence:
  required:
    - type: "code"
      description: "Room availability API response"
      optional: false
    - type: "doc"
      description: "Booking confirmation email"
      optional: false
  
  produce:
    - type: "code"
      description: "Reservation record"
      format: "json"
    - type: "lineage"
      description: "Booking workflow trace"
  
  # OpenLineage Integration (Gemini)
  openlineage:
    job_event:
      source_code_location: "plix/contracts/booking.yaml"
      declared_inputs: ["calendar", "room_db"]
      declared_outputs: ["reservation_record"]
    
    run_events: []
    
    dataset_events: []
  
  # W3C PROV Trace (Gemini)
  prov_trace:
    entities: []
    activities: []
  
  # Intent Lineage (Gemini)
  intent_lineage:
    original_nl_intent: "Book a meeting room"
    compiled_dsl_contract: "plix/contracts/booking.yaml"
    execution_plan_id: "plan_123"
    evidence_chain: []

# Conditions (Gemini: Recoverable Conditions)
conditions:
  onTestFail: "retry"
  onLowConfidence: "escalate"
  onPolicyBreach: "fail"
  onTimeout: "compensate"
  onError: "compensate"
  
  # Saga Pattern (Gemini)
  saga_pattern:
    compensations:
      - step_id: "reserve_room"
        compensation_action: "cancel_reservation"
        compensation_tool: "room_api"
        compensation_args:
          room_id: "<from_previous_step>"
    
    recovery_verification:
      tla_spec: |
        VARIABLES room_state
        Init == room_state = "available"
        Book == room_state = "available" /\ room_state' = "reserved"
        Cancel == room_state = "reserved" /\ room_state' = "available"
      verification_status: "pending"

# Telemetry (Gemini: Safety Gates)
telemetry:
  confidenceThresholds:
    minimum: 0.70
    warning: 0.80
    critical: 0.90
  
  timeouts:
    step: 30000
    plan: 300000
    retry: 5000
  
  costBudgets:
    tokens: 10000
    api_calls: 10
    compute_time_ms: 60000
  
  # Safety Gates (Gemini)
  safety_gates:
    linguistic_confidence:
      method: "self-ref"
      confidence_score: 0.85
      threshold: 0.70
      confidence_tokens: ["high", "certain"]
    
    economic_router:
      method: "barp"
      preference_vector: [0.6, 0.4]  # [accuracy, cost]
      estimated_reward: 0.82
      cost_estimate: 0.15
    
    compliance_gate:
      engine: "opa"
      policy_queries:
        - "allow if user.role == 'employee'"
        - "deny if duration > 4h"
      decision: "permit"
      policy_results:
        - query: "allow if user.role == 'employee'"
          result: true
        - query: "deny if duration > 4h"
          result: false

# Provenance (Gemini)
provenance:
  who: "system"
  when: "2025-11-09T12:00:00Z"
  lineage: []
  version: "1.0.0"

# Metadata
metadata:
  tags: ["booking", "meeting", "calendar"]
  priority: "medium"
  status: "draft"
```

---

## EBNF Grammar (ChatGPT-Informed)

```
Specification ::= IntentSection ContextSection ContractSection TaskList 
                  [ConstraintList] [EvidenceSection] ConditionsSection 
                  TelemetrySection ProvenanceSection [MetadataSection]

IntentSection  ::= "intent:" <string>

ContextSection ::= "context:" ContextFields
ContextFields  ::= "entities:" <string_list>
                   "scope:" <string>
                   "risk:" <float>
                   ["metadata:" <object>]

ContractSection ::= "contract:" ContractFields
ContractFields  ::= "pre:" <condition_list>
                    "post:" <condition_list>
                    "capabilities:" <string_list>
                    "policies:" <string_list>
                    ["invariants:" <condition_list>]
                    ["dsl_structure:" DSLStructure]
                    ["formal_validation:" FormalValidation]
                    ["layer1_guards:" Layer1Guards]
                    ["layer2_validators:" Layer2Validators]

DSLStructure   ::= "rules:" RuleEntry+ "ontology:" <string_list>
RuleEntry      ::= "- type:" <string> "content:" <string>

FormalValidation ::= ["alloy_model:" <string>]
                     ["tla_spec:" <string>]
                     "validation_status:" ("pending" | "valid" | "invalid")
                     ["validation_errors:" <string_list>]

Layer1Guards   ::= ["json_schema:" <object>]
                   ["regex_constraints:" <string_list>]
                   ["gbnf_controllers:" <string_list>]

Layer2Validators ::= ["shacl_shapes:" <string_list>]
                    ["smt_solvers:" <string_list>]

TaskList       ::= "tasks:" TaskEntry+
TaskEntry      ::= "- step:" <string>
                   "id:" <identifier>
                   "action:" <identifier>
                   "params:" ParamMap
                   "agent:" <string>
                   "target:" <string>
                   ["depends_on:" <identifier_list>]
                   ["retry:" RetryConfig]
                   ["compensate:" CompensationConfig]

ParamMap       ::= <key>:<value> ("," <key>:<value>)*
RetryConfig    ::= "max_attempts:" <integer>
                   "backoff:" ("linear" | "exponential" | "fixed")
                   "backoff_ms:" <integer>
                   ["conditions:" <string_list>]

CompensationConfig ::= "action:" <string>
                      ["tool:" <string>]
                      ["args:" ParamMap]

ConstraintList ::= "constraints:" Condition+
Condition      ::= <expression>  // Logical expression

EvidenceSection ::= "evidence:" EvidenceFields
EvidenceFields  ::= "required:" EvidenceEntry+
                    "produce:" EvidenceEntry+
                    ["openlineage:" OpenLineageConfig]
                    ["prov_trace:" PROVConfig]
                    ["intent_lineage:" IntentLineageConfig]

EvidenceEntry  ::= "- type:" ("code" | "doc" | "decision" | "test" | "diff" | "lineage")
                  "description:" <string>
                  ["optional:" <boolean>]
                  ["format:" <string>]

OpenLineageConfig ::= ["job_event:" JobEvent]
                     ["run_events:" RunEvent*]
                     ["dataset_events:" DatasetEvent*]

JobEvent       ::= "source_code_location:" <string>
                   "declared_inputs:" <string_list>
                   "declared_outputs:" <string_list>

RunEvent       ::= "state:" ("START" | "COMPLETE" | "FAIL")
                   "timestamp:" <datetime>
                   "input_datasets:" <string_list>
                   "output_datasets:" <string_list>
                   ["error_message:" <string>]
                   ["execution_time_ms:" <integer>]

DatasetEvent   ::= "dataset_id:" <string>
                   ["schema:" <object>]
                   ["ownership:" <string>]
                   ["data_source_location:" <string>]

PROVConfig     ::= "entities:" PROVEntity* "activities:" PROVActivity*

PROVEntity     ::= "id:" <string> "type:" <string> "attributes:" <object>
PROVActivity   ::= "id:" <string> "type:" <string>
                   "started_at:" <datetime>
                   ["ended_at:" <datetime>]
                   "used:" <string_list>
                   "generated:" <string_list>

IntentLineageConfig ::= "original_nl_intent:" <string>
                       "compiled_dsl_contract:" <string>
                       "execution_plan_id:" <string>
                       "evidence_chain:" <string_list>

ConditionsSection ::= "conditions:" ConditionFields
ConditionFields ::= "onTestFail:" Action
                    "onLowConfidence:" Action
                    "onPolicyBreach:" Action
                    ["onTimeout:" Action]
                    ["onError:" Action]
                    ["custom:" CustomCondition*]
                    ["saga_pattern:" SagaPattern]

Action          ::= "retry" | "compensate" | "fail" | "escalate"
CustomCondition ::= "condition:" <string> "action:" Action

SagaPattern     ::= "compensations:" CompensationEntry+
                   ["recovery_verification:" RecoveryVerification]

CompensationEntry ::= "step_id:" <string>
                     "compensation_action:" <string>
                     ["compensation_tool:" <string>]
                     ["compensation_args:" ParamMap]

RecoveryVerification ::= ["tla_spec:" <string>]
                        "verification_status:" ("pending" | "verified" | "failed")
                        ["verification_errors:" <string_list>]

TelemetrySection ::= "telemetry:" TelemetryFields
TelemetryFields ::= "confidenceThresholds:" ConfidenceThresholds
                   "timeouts:" Timeouts
                   ["costBudgets:" CostBudgets]
                   ["safety_gates:" SafetyGates]

ConfidenceThresholds ::= "minimum:" <float>
                         "warning:" <float>
                         "critical:" <float>

Timeouts        ::= "step:" <integer>
                   "plan:" <integer>
                   ["retry:" <integer>]

CostBudgets     ::= ["tokens:" <integer>]
                   ["api_calls:" <integer>]
                   ["compute_time_ms:" <integer>]

SafetyGates     ::= ["linguistic_confidence:" LinguisticConfidence]
                   ["economic_router:" EconomicRouter]
                   ["compliance_gate:" ComplianceGate]

LinguisticConfidence ::= "method:" "self-ref"
                        "confidence_score:" <float>
                        "threshold:" <float>
                        ["confidence_tokens:" <string_list>]

EconomicRouter  ::= "method:" "barp"
                   "preference_vector:" <float_list>
                   "estimated_reward:" <float>
                   "cost_estimate:" <float>

ComplianceGate  ::= "engine:" ("opa" | "cedar")
                   "policy_queries:" <string_list>
                   "decision:" ("permit" | "forbid")
                   "policy_results:" PolicyResult+

PolicyResult    ::= "query:" <string>
                   "result:" <boolean>
                   ["explanation:" <string>]

ProvenanceSection ::= "provenance:" ProvenanceFields
ProvenanceFields ::= "who:" <string>
                    "when:" <datetime>
                    "lineage:" <string_list>
                    ["version:" <string>]

MetadataSection ::= "metadata:" <object>
```

---

## Key Design Principles (ChatGPT)

### 1. Balanced Readability and Formality
- **Human-legible:** Controlled natural language (Gherkin-style keywords)
- **Machine-strict:** Unambiguous semantics, typed parameters
- **Example:** "Task: Approve loan if X and Y; Constraint: UserAge >= 18; Evidence: creditReportScore"

### 2. Bidirectional Translatability
- **NL → PLIx:** Parse natural language into structured PLIx
- **PLIx → Code:** Compile PLIx to executable code/workflows
- **PLIx → NL:** Generate human-readable descriptions from PLIx

### 3. Typed Contracts
- **Input/Output Types:** Each task specifies types and side effects
- **Static Checking:** Type-checkers/SMT solvers validate contracts
- **Formal Integration:** Works with TLA+, OPA, etc.

### 4. Evidence Binding
- **Provenance References:** PROV-style metadata
- **Quality Scores:** Confidence scores for evidence
- **Evidence Chains:** Links between claims and supporting artifacts

### 5. Versioned and Temporal Persistence
- **Bitemporal Tracking:** Valid time + system time
- **Append-Only Store:** Event log for full history
- **Compliance Support:** Audit trails for regulatory requirements

### 6. Interoperability
- **Workflows:** Temporal, Step Functions
- **Policies:** Rego (OPA), Cedar
- **Provenance:** PROV-JSON, OpenLineage events
- **Specs:** Gherkin scenarios

---

## LLM Toolchain Integration

### LangChain
```yaml
# PLIx → LangChain
tasks:
  - step: "Fetch sales data"
    action: langchain.tool.fetch_sales_data
    params:
      date: "2025-12-01"
```

### AutoGen
```yaml
# PLIx → AutoGen
tasks:
  - step: "Draft email"
    action: autogen.agent.draft_email
    agent: "assistant_agent"
    params:
      recipient: "alice"
      content: "<from_previous_step>"
```

### DSPy
```yaml
# PLIx → DSPy Module
contract:
  dsl_structure:
    rules:
      - type: "Module"
        content: "Summarize sales report"
    ontology: ["SUMMARIZE", "FETCH", "FORMAT"]
```

### LangGraph
```yaml
# PLIx → LangGraph State
plan:
  steps:
    - step: "Check availability"
      id: "node_1"
      depends_on: []
    - step: "Reserve room"
      id: "node_2"
      depends_on: ["node_1"]
```

---

**Status:** Grammar specification complete, ready for compiler implementation

