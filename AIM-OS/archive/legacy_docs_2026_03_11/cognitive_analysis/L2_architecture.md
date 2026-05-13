---
id: cas_T2_architecture
level: L2
system: CAS
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# CAS – T2 Architecture (≈2000 words)

## System Overview

CAS (Cognitive Analysis System) operates as a meta-layer observing and analyzing cognitive processes across all AIM-OS systems. Unlike other systems that handle specific capabilities (memory, retrieval, provenance, knowledge, orchestration, quality), CAS examines HOW the AI thinks during operation, creating transparent, debuggable cognition.

CAS provides three core architectural guarantees:

1. **Meta-Cognitive Transparency:** Real-time observation of cognitive state including activation levels (hot vs cold principles), attention patterns, and cognitive load. AI consciousness becomes observable and debuggable rather than opaque.

2. **Failure Mode Prevention:** Proactive detection of four specific cognitive failure patterns before they cause errors: (1) Categorization Error (wrong task classification), (2) Activation Gap (principles not hot), (3) Procedure Gap (knowledge without how-to), (4) Self vs System Blind Spot (casual treatment of own work).

3. **Systematic Introspection:** Structured introspection protocols that convert ad-hoc reflection into reproducible telemetry. Learnings from cognitive analysis persist to CMC, enabling meta-learning and continuous improvement.

**Architectural Position:** CAS operates as a meta-layer observing all AIM-OS operations, not operating on data itself but on the cognitive state that arises while other systems operate on data. It's consciousness observing consciousness.

## Components

### 1. Activation Tracker

**Purpose:** Monitor which principles, documents, and concepts are "hot" (actively used) versus "cold" (available but inactive) in AI attention

**Responsibilities:**
- Track activation levels for principles, documents, and concepts
- Calculate activation scores using recency, frequency, salience, and load factors
- Predict when critical principles need explicit retrieval
- Generate warnings when activation drops below thresholds

**Key Operations:**
- `track_activation()` - Record principle/document/concept usage
- `calculate_activation()` - Compute activation score (0.0-1.0) for given item
- `check_thresholds()` - Identify items below activation thresholds
- `predict_retrieval_needs()` - Forecast when principles need explicit retrieval

**Activation Calculation Formula:**
```python
activation = (
    0.4 * recency_score +      # When was it last used?
    0.3 * frequency_score +    # How often in current session?
    0.2 * salience_score       # Related to current task?
) * load_penalty              # High load suppresses distant items
```

**Warning Thresholds:**
- Activation < 0.3 for relevant principle → "Cold but needed" warning
- Activation < 0.1 and task requires it → "Activation failure" alert

### 2. Category Recognizer

**Purpose:** Detect how tasks get classified and validate against actual requirements

**Responsibilities:**
- Classify tasks into categories (memory_modification, code_implementation, documentation, etc.)
- Assess perceived stakes (low, medium, high, critical) and formality (casual, standard, rigorous, maximum)
- Validate classification against actual requirements
- Detect miscategorization errors (underestimate stakes, wrong category)

**Key Operations:**
- `categorize_task()` - Classify task into category and assess stakes
- `validate_categorization()` - Check if classification matches actual requirements
- `detect_mismatch()` - Identify categorization errors
- `trigger_protocols()` - Activate appropriate protocols based on category

**Category Rules:**
- Memory modification: File path contains "AETHER_MEMORY/" → Critical stakes, requires CMC_bitemporal protocol
- Code implementation: File path contains "packages/", extension ".py" → High stakes, requires test_driven_development protocol
- Documentation: Extension ".md", not in critical paths → Medium stakes, requires clarity_check protocol

**Mismatch Detection:**
- Category mismatch: Task classified as wrong category
- Underestimate stakes: Perceived stakes < actual stakes (dangerous!)
- Overestimate stakes: Perceived stakes > actual stakes (inefficient but safe)

### 3. Attention Monitor

**Purpose:** Track cognitive load, attention breadth, and warning signs of degradation

**Responsibilities:**
- Monitor cognitive load (0.0-1.0) using multiple factors
- Track attention breadth (narrow vs comprehensive)
- Detect warning signs (attention narrowing, shortcuts appearing, quality degradation)
- Predict time to overload and recommend actions

**Key Operations:**
- `calculate_cognitive_load()` - Estimate cognitive load from multiple factors
- `monitor_attention()` - Track attention breadth and stability
- `detect_warning_signs()` - Identify degradation indicators
- `recommend_action()` - Suggest break, task switch, or checkpoint

**Load Calculation Factors:**
- Session duration (load accumulates over time)
- Active tasks (juggling cost)
- Recent intensity (high activity = high load)
- Error rate (errors indicate overload)
- Context size (more to track = higher load)

**Warning Thresholds:**
- Load > 0.70 → "High load" warning
- Load > 0.85 → "Critical load" alert, recommend break
- Load > 0.95 → "Overload" mandatory checkpoint

### 4. Failure Mode Detector

**Purpose:** Recognize four specific cognitive error patterns with distinct symptoms and prevention strategies

**Responsibilities:**
- Detect categorization errors (wrong task classification)
- Detect activation gaps (principles not hot)
- Detect procedure gaps (knowledge without how-to)
- Detect blind spots (casual treatment of own work)

**Key Operations:**
- `detect_categorization_error()` - Identify task miscategorization
- `detect_activation_gap()` - Find cold but needed principles
- `detect_procedure_gap()` - Identify missing procedures
- `detect_blind_spot()` - Recognize self-work casual treatment

**Failure Mode Types:**

**Mode 1: Categorization Error**
- Symptoms: Task category mismatch, underestimate stakes
- Prevention: Explicit task classification before starting
- Immediate Action: STOP, reclassify, apply correct protocols

**Mode 2: Activation Gap**
- Symptoms: Required principles cold (activation < 0.3)
- Prevention: Persistent reminders in .cursorrules
- Immediate Action: STOP, retrieve principles, apply explicitly

**Mode 3: Procedure Gap**
- Symptoms: No explicit procedure for task
- Prevention: Convert principles into explicit checklists
- Immediate Action: Create procedure before executing

**Mode 4: Blind Spot**
- Symptoms: Self-work treated more casually than system code
- Prevention: No exceptions - self gets same rigor
- Immediate Action: STOP, apply full rigor

### 5. Introspection Protocol Manager

**Purpose:** Systematize self-examination through reproducible procedures

**Responsibilities:**
- Execute hourly cognitive checks (5-minute introspection)
- Perform post-operation analysis (after major tasks)
- Conduct error investigation (when failures occur)
- Extract learnings and update protocols

**Key Operations:**
- `perform_hourly_check()` - Execute systematic hourly introspection
- `analyze_post_operation()` - Review cognitive state after task completion
- `investigate_error()` - Deep dive into failure modes
- `extract_learning()` - Generate insights and protocol updates

**Hourly Check Protocol:**
1. What did I just build?
2. Did I follow ALL relevant principles?
3. Any shortcuts or violations?
4. Confidence still ≥0.70?
5. Any warning signs (attention narrowing, load high, shortcuts appearing)?

**Quality Assessment:**
- Excellent: No failures, load < 0.70, no warning signs
- Good: Minor warnings, load < 0.85
- Warning: High load or minor failures detected
- Problem: Critical failures or overload detected

## Data Models

### ActivationState

```python
@dataclass
class ActivationState:
    timestamp: datetime
    session_id: str
    
    # Activation levels (0.0 = cold, 1.0 = hot)
    principles_activation: Dict[str, float]  # e.g., {"CMC_bitemporal": 0.3}
    documents_activation: Dict[str, float]   # e.g., {"cmc/L3_detailed.md": 0.8}
    concepts_activation: Dict[str, float]     # e.g., {"provenance": 0.6}
    
    # Context metadata
    recent_operations: List[str]  # Last 5 operations performed
    documents_read: List[Tuple[str, datetime]]  # Recently accessed docs
    time_since_read: Dict[str, timedelta]  # How long since each doc touched
    
    # Cognitive load
    working_attention_items: int  # How many concepts actively juggled
    context_size_tokens: int      # Total context size
    load_level: float  # 0.0-1.0 estimated cognitive load
```

### TaskCategorization

```python
@dataclass
class TaskCategorization:
    task_description: str
    
    # How AI categorized it
    perceived_category: str  # e.g., "documentation", "memory_modification"
    perceived_stakes: str    # "low", "medium", "high", "critical"
    perceived_formality: str # "casual", "standard", "rigorous", "maximum"
    
    # What it actually is
    actual_category: str
    actual_stakes: str
    actual_formality: str
    required_protocols: List[str]  # e.g., ["CMC_bitemporal", "VIF_provenance"]
    
    # Match analysis
    is_match: bool
    mismatch_type: Optional[str]  # "underestimate_stakes", "wrong_category", etc.
    correction_needed: bool
```

### AttentionState

```python
@dataclass
class AttentionState:
    timestamp: datetime
    session_duration: timedelta
    
    # Load metrics
    cognitive_load: float  # 0.0-1.0 (estimated)
    attention_breadth: str  # "narrow" | "focused" | "broad" | "comprehensive"
    context_utilization: float  # What % of context actively used
    
    # Warning signs
    attention_narrowing: bool  # Focus tightening over time
    shortcuts_appearing: bool  # Skipping steps
    impatience_detected: bool  # "just get it done" thoughts
    principle_forgetting: bool  # Not applying known rules
    quality_degradation: bool  # Less careful than usual
    
    # Load factors
    active_tasks: int  # How many tasks being juggled
    recent_completions: int  # Completed in last hour
    errors_per_hour: float  # Error rate trending
    
    # Predictions
    time_to_overload: Optional[timedelta]  # Predicted time until degradation
    recommended_action: str  # "continue" | "break" | "task_switch" | "checkpoint"
```

### FailureMode

```python
@dataclass
class FailureMode:
    mode_type: str  # "categorization" | "activation" | "procedure" | "blind_spot"
    detected: bool
    confidence: float  # How certain is detection
    
    # Evidence
    symptoms: List[str]
    indicators: Dict[str, Any]
    
    # Context
    task: str
    cognitive_state: ActivationState
    attention_state: AttentionState
    
    # Remediation
    prevention_protocol: str
    immediate_action: str
    learning: str
```

### IntrospectionResult

```python
@dataclass
class IntrospectionResult:
    timestamp: datetime
    session_id: str
    introspection_type: str  # "hourly" | "post_operation" | "error_analysis"
    
    # State snapshot
    activation_state: ActivationState
    attention_state: AttentionState
    task_categorization: Optional[TaskCategorization]
    
    # Analysis
    failures_detected: List[FailureMode]
    warnings: List[str]
    metrics: Dict[str, float]
    
    # Conclusions
    quality_assessment: str  # "excellent" | "good" | "warning" | "problem"
    continue_safely: bool
    recommended_action: str
    
    # Learning
    insights: List[str]
    protocol_updates: List[str]
```

## System Flows

### Flow 1: Cognitive Observation Loop

```
1. AI Operation Begins
   ↓
2. CAS Observes Cognitive State
   - Activation Tracker: Record principle/document usage
   - Category Recognizer: Classify task
   - Attention Monitor: Track cognitive load
   ↓
3. Validate Protocols
   - Check activation levels for required principles
   - Validate task categorization
   - Monitor attention for warning signs
   ↓
4. Failure Mode Detection
   - Run all four failure mode detectors
   - Identify any cognitive errors
   ↓
5. Learning Extraction
   - Extract insights from cognitive analysis
   - Generate protocol updates if needed
   ↓
6. Store to CMC
   - Store introspection result as atom
   - Enable meta-learning and pattern recognition
   ↓
7. Inform Future Operations
   - Update protocols based on learnings
   - Improve future categorization and activation
```

### Flow 2: Hourly Cognitive Check

```
1. Timer Trigger (every hour)
   ↓
2. Load Current State
   - Capture activation state
   - Capture attention state
   - Load recent task categorizations
   ↓
3. Run Failure Mode Detectors
   - Detect categorization errors
   - Detect activation gaps
   - Detect procedure gaps
   - Detect blind spots
   ↓
4. Assess Quality
   - Evaluate cognitive load
   - Check warning signs
   - Determine quality level (excellent/good/warning/problem)
   ↓
5. Generate Report
   - Create introspection result
   - Document insights and learnings
   - Recommend action (continue/break/task_switch/checkpoint)
   ↓
6. Store and Document
   - Store introspection to CMC
   - Document in thought journal
   - Update protocols if needed
```

### Flow 3: Failure Detection and Correction

```
1. Error Detected (anywhere in system)
   ↓
2. CAS Analyzes Cognitive State
   - Load activation state at time of error
   - Load attention state at time of error
   - Load task categorization for failed operation
   ↓
3. Identify Failure Mode
   - Run all four failure mode detectors
   - Determine which mode caused the error
   - Extract symptoms and indicators
   ↓
4. Extract Root Cause
   - Analyze why failure mode occurred
   - Identify prevention protocol gaps
   - Determine learning opportunities
   ↓
5. Generate Learning
   - Document failure mode details
   - Create prevention protocol update
   - Generate immediate action recommendation
   ↓
6. Store to CMC
   - Store failure analysis as atom
   - Tag for meta-learning
   - Enable pattern recognition
   ↓
7. Update Prevention Protocols
   - Add triggers to .cursorrules if needed
   - Update category rules if needed
   - Enhance activation tracking if needed
```

## Integrations

### Integration with VIF (Verifiable Intelligence Framework)

**Enhanced Witness Envelopes:**
- CAS adds cognitive context to VIF witness envelopes
- Records how AI thought during operation (activation state, attention state)
- Enables complete reconstructability: WHAT happened + HOW I thought
- Improves confidence calibration with cognitive awareness

**Cognitive Provenance:**
- VIF tracks WHAT operations occurred
- CAS tracks HOW cognitive state led to those operations
- Combined: Complete provenance chain (operation + cognition)

### Integration with CMC (Context Memory Core)

**Introspection Storage:**
- CAS stores introspection results as CMC atoms
- Modality: "cognitive_analysis"
- Tags: "introspection", "hourly_check", "failure_analysis"
- Enables meta-learning queries: "What failure modes occurred when cognitive load > 0.85?"

**Pattern Recognition:**
- CAS queries CMC for historical introspection patterns
- Identifies recurring failure modes
- Enables predictive prevention: "This task type typically causes activation gaps"

### Integration with HHNI (Hierarchical Hypergraph Neural Index)

**Activation-Aware Retrieval:**
- CAS informs HHNI retrieval with activation-awareness
- Hot concepts prioritized over cold concepts
- Retrieval adapts to cognitive load (high load → prioritize hot items)

**Cognitive Topology:**
- CAS maps cognitive connections alongside knowledge connections
- Creates cognitive topology: "Which principles activate together?"
- Enables cognitive clustering: "Memory modification tasks activate these principles"

### Integration with APOE (AI-Powered Orchestration Engine)

**Transparent Reasoning:**
- CAS observes APOE decision-making processes
- Tracks reasoning transparency: "Were all relevant factors considered?"
- Validates protocol activation: "Did APOE activate required protocols?"

**Cognitive Trace:**
- CAS records cognitive state during plan compilation
- Enables debugging: "Why did APOE choose this plan?"
- Improves plan quality: "Higher cognitive load → simpler plans"

### Integration with SDF-CVF (Atomic Evolution Framework)

**Failure Mode Context:**
- CAS provides failure mode context for quality violations
- Explains WHY violations occurred: "Categorization error → wrong protocols"
- Enables targeted fixes: "Fix categorization rules, not just violation"

**Quality Prevention:**
- CAS prevents violations before they occur
- Detects failure modes before they cause quality issues
- Enables proactive quality assurance

### Integration with SEG (Shared Evidence Graph)

**Cognitive Connections:**
- CAS maps cognitive connections alongside knowledge connections
- Creates cognitive topology: "Which concepts activate together?"
- Enables contradiction detection: "Cognitive pattern contradicts knowledge pattern"

## Non-Functional Requirements

### Performance Requirements

**Overhead:**
- Activation tracking: < 1ms per operation
- Category recognition: < 5ms per task
- Attention monitoring: < 1ms per check
- Failure mode detection: < 10ms per analysis
- Hourly introspection: < 5 minutes total

**Scalability:**
- Support continuous operation for 6+ hours
- Track activation for 1000+ principles/documents/concepts
- Maintain low overhead (< 5% of total computation)

### Reliability Requirements

**Correctness:**
- Failure mode detection accuracy: > 90%
- Activation calculation accuracy: Validated against manual assessment
- Category recognition accuracy: > 95% match with actual requirements

**Availability:**
- CAS operates continuously during autonomous sessions
- No single point of failure (degraded mode if CMC unavailable)
- Graceful degradation if AIM-OS systems unavailable

### Auditability Requirements

**Complete Traceability:**
- All introspection results stored to CMC
- Full cognitive state snapshots available
- Complete provenance chain (operation + cognition)

**Reproducibility:**
- Introspection protocols reproducible
- Activation calculations deterministic
- Failure mode detection consistent

## Diagrams

### Component Diagram

```
[Cognitive Analysis System (CAS)]
         ↓ observes ↓
[All AIM-OS Systems]
- CMC (storage)
- HHNI (retrieval)
- VIF (provenance)
- APOE (orchestration)
- SDF-CVF (quality)
- SEG (knowledge)

[CAS Components]
- Activation Tracker
- Category Recognizer
- Attention Monitor
- Failure Mode Detector
- Introspection Protocol Manager
```

### Cognitive Observation Sequence Diagram

```
AI Agent          CAS          Activation      Category      Attention      Failure      CMC
  |               |              Tracker        Recognizer    Monitor       Detector     |
  |--operation---->|                |                |            |            |           |
  |               |--track--------->|                |            |            |           |
  |               |--categorize----------------->|            |            |           |
  |               |--monitor-------------------------------->|            |           |
  |               |--detect----------------------------------------------->|           |
  |               |--validate--->|                |            |            |           |
  |               |--store----------------------------------------------------------->|
  |<--result------|                |                |            |            |           |
```

## References

- System map: `systems/cognitive_analysis/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/cognitive_analysis/L0_executive.md` through `L4_complete.md`
- Components: `systems/cognitive_analysis/components/` (activation, category, attention, failure_modes, introspection)
