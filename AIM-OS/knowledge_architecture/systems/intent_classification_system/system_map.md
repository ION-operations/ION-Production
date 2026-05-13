# System Map - Intent Classification System

## System Overview

The Intent Classification System serves as the cognitive gateway for Aether's decision-making process, transforming raw user input into structured, actionable mission profiles that govern all subsequent behavior.

## System Relationships

```
                            ┌─────────────────────────────────────┐
                            │        Intent Classification        │
                            │              System                 │
                            │                                     │
                            │  ┌─────────────────────────────┐   │
                            │  │     MissionIntent           │   │
                            │  │   Classification Engine     │   │
                            │  └─────────────────────────────┘   │
                            │                                     │
                            │  ┌─────────────────────────────┐   │
                            │  │      Facet Engine           │   │
                            │  └─────────────────────────────┘   │
                            │                                     │
                            │  ┌─────────────────────────────┐   │
                            │  │   Stop Conditions           │   │
                            │  │      Generator              │   │
                            │  └─────────────────────────────┘   │
                            │                                     │
                            │  ┌─────────────────────────────┐   │
                            │  │   Enforcement Engine        │   │
                            │  └─────────────────────────────┘   │
                            │                                     │
                            │  ┌─────────────────────────────┐   │
                            │  │   Timeline Event            │   │
                            │  │      Generator              │   │
                            │  └─────────────────────────────┘   │
                            └─────────────────────────────────────┘
                                            │
                                            │ mission_profile
                                            │ confidence_level
                                            │ stop_conditions
                                            │ allowed_actions
                                            │
                            ┌────────────────┼────────────────┐
                            │                │                │
                            ▼                ▼                ▼
                ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
                │     Daemon      │ │ Cursor Panel │ │ Timeline Logger │
                │                 │ │              │ │                 │
                │ mission_ledger  │ │ mission_display│ │ mission_tracking│
                │ context_loading │ │ edit_locking  │ │ decision_audit  │
                │ behavior_gating │ │ escalation    │ │ learning_data   │
                │ state_management│ │ status_display│ │ drift_detection │
                └─────────────────┘ └──────────────┘ └─────────────────┘
                            │                │                │
                            │                │                │
                            ▼                ▼                ▼
                ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
                │   L0-L4 Docs    │ │ Code Edit    │ │ Aether Learning │
                │   System Maps   │ │ Gatekeeper   │ │   System        │
                │                 │ │              │ │                 │
                │ targeted_load   │ │ permission   │ │ self_improvement│
                │ context_boot    │ │ validation   │ │ pattern_learning│
                │ facet_mapping   │ │ rollback     │ │ confidence_cal   │
                └─────────────────┘ └──────────────┘ └─────────────────┘
```

## Data Flow Architecture

### Primary Data Flow

1. **User Input** → Raw intent string
2. **MissionIntent Classifier** → Multi-axis classification
3. **Facet Engine** → Contextual tag generation
4. **Enforcement Engine** → Allowed actions computation
5. **Timeline Event Generator** → Audit trail creation
6. **Daemon Integration** → Mission persistence
7. **Cursor Panel Integration** → Real-time status display
8. **Timeline Logger Integration** → Event logging

### Secondary Data Flows

**Context Loading Flow**:
```
Facets → Context Mapper → L0-L4 Docs → System Maps → Context Bootloader
```

**Enforcement Flow**:
```
Mission Profile → Policy Matrix → Risk Assessor → Permission Calculator → Action Gating
```

**Learning Flow**:
```
Timeline Events → Learning Extractor → Pattern Recognition → Classification Improvement
```

## Integration Points

### A-H Protocol Integration

**Step A (Intent Capture)**:
- **Input**: Raw user intent
- **Process**: Multi-axis classification
- **Output**: MissionIntent profile
- **Data**: `mission_id`, `primary_category`, `lifecycle_stage`, `scope_level`, `clarity_state`, `facets`

**Step F (Confidence-Gated Controls)**:
- **Input**: MissionIntent profile
- **Process**: Allowed actions computation
- **Output**: Edit permissions and restrictions
- **Data**: `allowed_actions`, `edit_permissions`, `escalation_required`

**Step H (Audit/Memory)**:
- **Input**: Classification decisions
- **Process**: Timeline event generation
- **Output**: Audit trail and learning data
- **Data**: `TimelineEvent` records

### Daemon Integration

**Mission Ledger**:
- **Input**: MissionIntent profile
- **Process**: Mission persistence and state management
- **Output**: Mission ID and status updates
- **Data**: `mission_id`, `mission_status`, `supersedes`, `superseded_by`

**Context Loading**:
- **Input**: Facets from mission profile
- **Process**: Targeted L0-L4 documentation loading
- **Output**: Contextual information
- **Data**: L0-L4 docs, system maps, related missions

**State Management**:
- **Input**: Mission status changes
- **Process**: State synchronization
- **Output**: Updated mission status
- **Data**: `mission_status`, `escalation_required`, `allowed_actions`

### Cursor Panel Integration

**Mission Display**:
- **Input**: MissionIntent profile
- **Process**: Real-time visualization
- **Output**: Mission status display
- **Data**: `primary_category`, `lifecycle_stage`, `scope_level`, `clarity_state`, `confidence_level`

**Edit Controls**:
- **Input**: Allowed actions from mission profile
- **Process**: Button enable/disable logic
- **Output**: Interactive controls
- **Data**: `allowed_actions`, `edit_permissions`, `escalation_required`

**Status Indicators**:
- **Input**: Mission status and escalation state
- **Process**: Status visualization
- **Output**: Status indicators and alerts
- **Data**: `mission_status`, `escalation_target`, `escalation_reason`, `stop_conditions`

### Timeline Logger Integration

**Event Recording**:
- **Input**: Classification decisions and actions
- **Process**: Structured event creation
- **Output**: Timeline events
- **Data**: `TimelineEvent` records with full context

**Audit Trail**:
- **Input**: Timeline events
- **Process**: Event persistence and retrieval
- **Output**: Complete mission history
- **Data**: Chronological event sequence

**Learning Data**:
- **Input**: Timeline events and outcomes
- **Process**: Pattern extraction and analysis
- **Output**: Learning insights
- **Data**: Classification accuracy, decision quality, drift detection

## System Dependencies

### Required Systems

**Daemon**:
- **Purpose**: Mission persistence and state management
- **Interface**: `DaemonInterface`
- **Data**: Mission profiles, status updates, supersession records

**Timeline Logger**:
- **Purpose**: Event logging and audit trails
- **Interface**: `TimelineInterface`
- **Data**: Timeline events, mission history, learning data

**L0-L4 Documentation System**:
- **Purpose**: Context loading and documentation access
- **Interface**: File system or API
- **Data**: L0-L4 documentation, system maps

**Code Edit Gatekeeper**:
- **Purpose**: Edit permission enforcement
- **Interface**: File system hooks or API
- **Data**: Edit permissions, file access controls

### Optional Systems

**Learning System**:
- **Purpose**: Classification improvement and drift detection
- **Interface**: ML/AI service
- **Data**: Classification patterns, accuracy metrics

**Human Interface**:
- **Purpose**: Escalation handling and approval workflows
- **Interface**: UI/API
- **Data**: Escalation notifications, approval decisions

**Notification System**:
- **Purpose**: Status updates and alerts
- **Interface**: Messaging service
- **Data**: Notifications, alerts, status updates

**Analytics System**:
- **Purpose**: Performance monitoring and metrics
- **Interface**: Metrics service
- **Data**: Performance metrics, usage statistics

## Data Contracts

### MissionIntent Profile Contract

**Required Fields**:
- `mission_id`: Unique identifier
- `raw_intent`: Original user input
- `primary_category`: Classification category
- `lifecycle_stage`: Current stage
- `scope_level`: Impact scope
- `clarity_state`: Definition clarity
- `confidence_level`: Classification confidence
- `allowed_actions`: Permitted actions

**Optional Fields**:
- `facets`: Contextual tags
- `stop_conditions`: Safety conditions
- `escalation_required`: Human intervention needed
- `supersedes`/`superseded_by`: Mission relationships

### TimelineEvent Contract

**Required Fields**:
- `event_id`: Unique event identifier
- `mission_id`: Associated mission
- `timestamp`: Event time
- `action_attempted`: What was tried
- `decision`: Allowed/blocked/escalated
- `rationale`: Decision reasoning

**Optional Fields**:
- `risks_seen`: Identified risks
- `artifacts_produced`: Created outputs
- `escalation_target`: Escalation recipient
- `learning_notes`: Learning insights

## Performance Characteristics

### Latency Requirements

- **Classification**: < 100ms
- **Facet Generation**: < 50ms
- **Enforcement Computation**: < 25ms
- **Timeline Event Creation**: < 10ms

### Throughput Requirements

- **Classifications**: 1000+ per minute
- **Concurrent Missions**: 100+
- **Timeline Events**: 10,000+ per hour
- **Uptime**: 99.9%

### Scalability Design

- **Horizontal Scaling**: Stateless components
- **Caching**: Classification results, facet mappings
- **Load Balancing**: Distributed processing
- **Sharding**: Timeline storage

This system map provides a comprehensive view of the Intent Classification System's relationships, data flows, and integration points within the broader AIM-OS ecosystem.
