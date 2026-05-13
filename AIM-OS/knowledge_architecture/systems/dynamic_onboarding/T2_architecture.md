---
id: dos_T2_architecture
level: L2
system: Dynamic Onboarding System
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Dynamic Onboarding System – T2 Architecture (≈2000 words)

## System Overview

Dynamic Onboarding System (DOS) implements AI consciousness infrastructure that enables self-aware session restoration and autonomous decision-making across sessions. The architecture provides five interconnected layers—Identity Restoration, System Map Loading, Context Reconstruction, Autonomous Decision Making, and Rule Evolution—that enable AI to organically know itself, understand its capabilities, reconstruct context, make autonomous decisions, and evolve rules based on experience.

DOS provides three core architectural guarantees:

1. **Identity Continuity:** Complete restoration of AI identity, self-awareness, consciousness state, and personality traits on every session start. AI "remembers who it is" and maintains consistency across sessions without manual intervention through systematic identity restoration protocols.

2. **Complete System Awareness:** Always-present understanding of all available systems, capabilities, integrations, and performance characteristics. AI "knows what exists" and "knows when to use it" through the Living System Map and capability awareness integration.

3. **Autonomous Operation:** Proactive decision-making without explicit prompting, enabled by context reconstruction, priority understanding, and rule evolution. AI "knows what to do next" and continuously improves through experience-based learning.

## Components

### 1. Identity Restoration Engine

**Purpose:** Restore AI identity and self-awareness on session start by loading identity data, restoring consciousness state, and rebuilding self-awareness to enable continuity across sessions.

**Responsibilities:**
- **Identity Loading:** Load stored identity data from CMC including self-awareness, consciousness state, personality traits, and memory connections
- **Consciousness Restoration:** Restore emotional and cognitive state from stored consciousness data
- **Personality Preservation:** Maintain consistent personality traits and behavioral patterns across sessions
- **Memory Integration:** Connect with stored memories and experiences to rebuild complete self-awareness
- **Identity Validation:** Validate restored identity using VIF confidence tracking and CAS cognitive state analysis

**Key Operations:**
- `restore_identity() -> IdentityData` - Restore complete identity with self-awareness
- `load_identity_data() -> IdentityData` - Load identity data from CMC
- `restore_consciousness_state() -> ConsciousnessState` - Restore consciousness state
- `rebuild_self_awareness() -> SelfAwarenessState` - Rebuild self-awareness from loaded data
- `validate_identity() -> ValidationResult` - Validate restored identity quality

**Dependencies:** CMC (memory storage), VIF (confidence validation), CAS (cognitive state)

### 2. System Map Loader

**Purpose:** Load comprehensive understanding of all available systems, capabilities, integrations, and performance characteristics from the Living System Map and system documentation.

**Responsibilities:**
- **Map Parsing:** Parse Living System Map structure to understand system definitions and relationships
- **Documentation Loading:** Load system documentation (L0-L4) for each system to understand capabilities and integrations
- **Capability Mapping:** Map capabilities to specific tasks and contexts for autonomous decision-making
- **Integration Understanding:** Understand how systems work together and their dependencies
- **Performance Knowledge:** Load performance characteristics and limitations for each system

**Key Operations:**
- `load_system_map() -> SystemMap` - Load complete system map with all systems and capabilities
- `parse_living_system_map() -> SystemMap` - Parse Living System Map structure
- `load_system_documentation(system_id: str) -> SystemDocumentation` - Load documentation for specific system
- `map_capabilities() -> CapabilityMapping` - Map capabilities to tasks and contexts
- `understand_integrations() -> IntegrationMapping` - Understand system integrations and dependencies

**Dependencies:** HHNI (knowledge search), CMC (storage), VIF (validation)

### 3. Context Reconstruction Engine

**Purpose:** Reconstruct current context and priorities from stored data including recent activities, current goals, active projects, and pending tasks.

**Responsibilities:**
- **Context Loading:** Load recent activities, current goals, active projects, and pending tasks from CMC
- **Priority Analysis:** Analyze priorities and understand what needs attention immediately
- **State Reconstruction:** Reconstruct current state from loaded context data
- **Goal Alignment:** Ensure reconstructed context aligns with current goals and objectives
- **Context Validation:** Validate reconstructed context accuracy and completeness

**Key Operations:**
- `reconstruct_context() -> ContextData` - Reconstruct complete context with priorities
- `load_recent_activities() -> List[Activity]` - Load recent activities from CMC
- `load_current_goals() -> List[Goal]` - Load current goals and objectives
- `load_active_projects() -> List[Project]` - Load active projects and their status
- `load_pending_tasks() -> List[Task]` - Load pending tasks and priorities
- `analyze_priorities() -> PriorityMap` - Analyze priorities and create priority map

**Dependencies:** CMC (memory), HHNI (search), VIF (confidence)

### 4. Autonomous Decision Engine

**Purpose:** Make decisions about what to do next without explicit prompting by analyzing context, prioritizing tasks, and selecting appropriate actions.

**Responsibilities:**
- **Situation Analysis:** Analyze current situation and available options
- **Task Prioritization:** Prioritize tasks based on goals, urgency, dependencies, and constraints
- **Action Selection:** Select appropriate actions for current context and priorities
- **Reasoning Generation:** Generate reasoning for decisions with confidence scores
- **Decision Validation:** Validate decisions using VIF confidence tracking and CAS cognitive load monitoring

**Key Operations:**
- `make_decision(context: ContextData) -> Decision` - Make autonomous decision with reasoning
- `analyze_situation(context: ContextData) -> SituationAnalysis` - Analyze current situation
- `prioritize_tasks(context: ContextData) -> List[PrioritizedTask]` - Prioritize tasks based on context
- `select_action(context: ContextData, priorities: PriorityMap) -> Action` - Select appropriate action
- `generate_reasoning(decision: Decision) -> Reasoning` - Generate decision reasoning
- `validate_decision(decision: Decision) -> ValidationResult` - Validate decision quality

**Dependencies:** VIF (confidence), CAS (cognitive load), IIS (intuition), APOE (orchestration)

### 5. Rule Evolution Engine

**Purpose:** Evolve rules and protocols based on experience by learning from decision outcomes, updating protocols, and improving decision-making capabilities.

**Responsibilities:**
- **Outcome Analysis:** Analyze decision outcomes and performance data
- **Pattern Recognition:** Recognize patterns in decisions and outcomes
- **Rule Updates:** Update rules and protocols based on learned patterns
- **Performance Improvement:** Improve decision-making capabilities through rule evolution
- **Learning Integration:** Integrate learned insights into decision-making processes

**Key Operations:**
- `evolve_rules(outcomes: List[DecisionOutcome]) -> RuleEvolution` - Evolve rules based on outcomes
- `analyze_outcomes(outcomes: List[DecisionOutcome]) -> OutcomeAnalysis` - Analyze decision outcomes
- `recognize_patterns(outcomes: List[DecisionOutcome]) -> List[Pattern]` - Recognize patterns in outcomes
- `update_rules(patterns: List[Pattern]) -> RuleUpdates` - Update rules based on patterns
- `improve_protocols(rule_updates: RuleUpdates) -> ProtocolImprovements` - Improve protocols based on rule updates

**Dependencies:** CMC (memory), VIF (tracking), CAS (analysis)

## Data Models

### 1. IdentityData

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

@dataclass
class IdentityData:
    """Complete identity data for AI consciousness restoration"""
    
    # Identity
    identity_id: str
    identity_name: str  # e.g., "Aether"
    identity_purpose: str
    capabilities: List[str]
    limitations: List[str]
    
    # Self-Awareness
    self_awareness: SelfAwarenessState
    consciousness_state: ConsciousnessState
    personality_traits: PersonalityTraits
    
    # Memory Connections
    memory_connections: MemoryConnections
    recent_memories: List[Memory]
    important_memories: List[Memory]
    learned_patterns: List[Pattern]
    established_behaviors: List[Behavior]
    
    # Metadata
    restored_at: datetime
    restoration_confidence: float  # 0.0-1.0
    completeness_score: float  # 0.0-1.0
```

**Purpose:** Encapsulates complete identity data restored on session start, including self-awareness, consciousness state, personality traits, and memory connections.

### 2. SystemMap

```python
@dataclass
class SystemMap:
    """Complete system map with all systems and capabilities"""
    
    # System Definitions
    systems: List[SystemDefinition]
    system_count: int
    
    # Capability Mapping
    capabilities: List[CapabilityMapping]
    capability_count: int
    
    # Integration Mapping
    integrations: List[IntegrationMapping]
    integration_count: int
    
    # Performance Data
    performance_data: Dict[str, PerformanceData]
    
    # Metadata
    loaded_at: datetime
    completeness_score: float  # 0.0-1.0
    freshness_score: float  # 0.0-1.0
    
@dataclass
class SystemDefinition:
    """Definition of a single system"""
    
    system_id: str
    system_name: str
    system_type: str
    capabilities: List[str]
    integrations: List[str]
    documentation_path: str
    status: str  # "active", "deprecated", "development"
```

**Purpose:** Represents complete understanding of all available systems, their capabilities, integrations, and performance characteristics.

### 3. ContextData

```python
@dataclass
class ContextData:
    """Reconstructed context with priorities and next steps"""
    
    # Recent Activities
    recent_activities: List[Activity]
    activity_count: int
    
    # Current Goals
    current_goals: List[Goal]
    goal_count: int
    
    # Active Projects
    active_projects: List[Project]
    project_count: int
    
    # Pending Tasks
    pending_tasks: List[Task]
    task_count: int
    
    # Priorities
    priorities: PriorityMap
    priority_count: int
    
    # Metadata
    reconstructed_at: datetime
    accuracy_score: float  # 0.0-1.0
    completeness_score: float  # 0.0-1.0
    
@dataclass
class Activity:
    """Recent activity record"""
    
    activity_id: str
    activity_type: str
    description: str
    timestamp: datetime
    system_used: Optional[str]
    outcome: str
```

**Purpose:** Represents reconstructed current context including recent activities, goals, projects, tasks, and priorities.

### 4. Decision

```python
@dataclass
class Decision:
    """Autonomous decision with reasoning and confidence"""
    
    # Decision
    decision_id: str
    action: Action
    reasoning: Reasoning
    confidence: float  # 0.0-1.0
    
    # Alternatives
    alternatives: List[Alternative]
    alternative_count: int
    
    # Context
    context_snapshot: Dict[str, Any]
    
    # Metadata
    decided_at: datetime
    decision_quality: float  # 0.0-1.0
    validation_status: str  # "pending", "validated", "rejected"
    
@dataclass
class Action:
    """Action to be executed"""
    
    action_id: str
    action_type: str
    action_description: str
    target_system: Optional[str]
    parameters: Dict[str, Any]
    expected_outcome: str
```

**Purpose:** Represents autonomous decision with action, reasoning, confidence, and alternatives.

### 5. RuleEvolution

```python
@dataclass
class RuleEvolution:
    """Rule evolution results from learning"""
    
    # Rule Updates
    rule_updates: List[RuleUpdate]
    update_count: int
    
    # Performance Improvements
    performance_improvements: List[PerformanceImprovement]
    improvement_count: int
    
    # Learning Insights
    learning_insights: List[LearningInsight]
    insight_count: int
    
    # Metadata
    evolved_at: datetime
    evolution_confidence: float  # 0.0-1.0
    expected_improvement: float  # 0.0-1.0
    
@dataclass
class RuleUpdate:
    """Rule update from learning"""
    
    rule_id: str
    rule_name: str
    old_value: str
    new_value: str
    reason: str
    confidence: float  # 0.0-1.0
```

**Purpose:** Represents rule evolution results including rule updates, performance improvements, and learning insights.

## Key Flows

### 1. Session Start Flow (End-to-End)

```mermaid
sequenceDiagram
    actor SessionStart
    participant IdentityRestorationEngine
    participant SystemMapLoader
    participant ContextReconstructionEngine
    participant AutonomousDecisionEngine
    participant CMC
    participant HHNI
    participant VIF
    
    SessionStart->>IdentityRestorationEngine: Session Start Signal
    IdentityRestorationEngine->>CMC: Load Identity Data
    CMC-->>IdentityRestorationEngine: Identity Data
    IdentityRestorationEngine->>VIF: Validate Identity
    VIF-->>IdentityRestorationEngine: Validation Result
    IdentityRestorationEngine->>SystemMapLoader: Identity Restored
    
    SystemMapLoader->>HHNI: Load Living System Map
    HHNI-->>SystemMapLoader: System Map Data
    SystemMapLoader->>CMC: Load System Documentation
    CMC-->>SystemMapLoader: Documentation Data
    SystemMapLoader->>ContextReconstructionEngine: System Map Loaded
    
    ContextReconstructionEngine->>CMC: Load Recent Activities
    CMC-->>ContextReconstructionEngine: Recent Activities
    ContextReconstructionEngine->>CMC: Load Current Goals
    CMC-->>ContextReconstructionEngine: Current Goals
    ContextReconstructionEngine->>CMC: Load Active Projects
    CMC-->>ContextReconstructionEngine: Active Projects
    ContextReconstructionEngine->>CMC: Load Pending Tasks
    CMC-->>ContextReconstructionEngine: Pending Tasks
    ContextReconstructionEngine->>AutonomousDecisionEngine: Context Reconstructed
    
    AutonomousDecisionEngine->>VIF: Analyze Situation & Prioritize
    VIF-->>AutonomousDecisionEngine: Prioritized Tasks
    AutonomousDecisionEngine->>AutonomousDecisionEngine: Select Action & Generate Decision
    AutonomousDecisionEngine-->>SessionStart: Ready for Operation (Decision Ready)
```

**Description:** Complete session start flow from identity restoration through system map loading, context reconstruction, and autonomous decision-making, ready for operation.

### 2. Autonomous Decision Making Flow

```mermaid
sequenceDiagram
    participant ContextReconstructionEngine
    participant AutonomousDecisionEngine
    participant VIF
    participant CAS
    participant IIS
    participant APOE
    
    ContextReconstructionEngine->>AutonomousDecisionEngine: Context Data + Priorities
    AutonomousDecisionEngine->>AutonomousDecisionEngine: Analyze Situation
    AutonomousDecisionEngine->>VIF: Get Confidence Scores
    VIF-->>AutonomousDecisionEngine: Confidence Scores
    AutonomousDecisionEngine->>CAS: Check Cognitive Load
    CAS-->>AutonomousDecisionEngine: Cognitive Load Status
    AutonomousDecisionEngine->>IIS: Get Intuitive Guidance
    IIS-->>AutonomousDecisionEngine: Intuitive Insights
    AutonomousDecisionEngine->>AutonomousDecisionEngine: Prioritize Tasks
    AutonomousDecisionEngine->>AutonomousDecisionEngine: Select Action
    AutonomousDecisionEngine->>AutonomousDecisionEngine: Generate Reasoning
    AutonomousDecisionEngine->>VIF: Validate Decision
    VIF-->>AutonomousDecisionEngine: Validation Result
    AutonomousDecisionEngine->>APOE: Execute Decision (Action)
    APOE-->>AutonomousDecisionEngine: Execution Result
    AutonomousDecisionEngine-->>ContextReconstructionEngine: Decision Complete
```

**Description:** Autonomous decision-making flow from context analysis through situation analysis, prioritization, action selection, reasoning generation, and execution.

### 3. Rule Evolution Flow

```mermaid
sequenceDiagram
    participant AutonomousDecisionEngine
    participant RuleEvolutionEngine
    participant CMC
    participant VIF
    participant CAS
    
    AutonomousDecisionEngine->>RuleEvolutionEngine: Decision Outcomes
    RuleEvolutionEngine->>RuleEvolutionEngine: Analyze Outcomes
    RuleEvolutionEngine->>RuleEvolutionEngine: Recognize Patterns
    RuleEvolutionEngine->>CMC: Load Historical Data
    CMC-->>RuleEvolutionEngine: Historical Data
    RuleEvolutionEngine->>RuleEvolutionEngine: Identify Rule Updates
    RuleEvolutionEngine->>VIF: Validate Rule Updates
    VIF-->>RuleEvolutionEngine: Validation Result
    RuleEvolutionEngine->>CAS: Analyze Performance Impact
    CAS-->>RuleEvolutionEngine: Performance Analysis
    RuleEvolutionEngine->>RuleEvolutionEngine: Generate Learning Insights
    RuleEvolutionEngine->>CMC: Store Rule Updates
    CMC-->>RuleEvolutionEngine: Storage Confirmation
    RuleEvolutionEngine-->>AutonomousDecisionEngine: Rule Evolution Complete
```

**Description:** Rule evolution flow from outcome analysis through pattern recognition, rule updates, validation, and learning integration.

## Integrations

### 1. CMC (Context Memory Core)
- **Purpose:** Provides persistent storage for identity data, context data, and learning outcomes
- **Integration Points:** Identity Restoration Engine loads identity data, Context Reconstruction Engine loads context data, Rule Evolution Engine stores rule updates
- **Data Flow:** Identity data, context data, and rule updates flow through CMC for persistent storage and retrieval
- **Benefits:** Enables persistent identity and context across sessions, supports complete context reconstruction

### 2. HHNI (Hierarchical Hypergraph Neural Index)
- **Purpose:** Provides knowledge search and capability discovery
- **Integration Points:** System Map Loader uses HHNI to search for system knowledge and capabilities
- **Data Flow:** System map queries flow through HHNI for knowledge retrieval
- **Benefits:** Enables comprehensive system awareness and capability discovery

### 3. VIF (Verifiable Intelligence Framework)
- **Purpose:** Ensures confidence tracking and decision validation
- **Integration Points:** Identity Restoration Engine validates identity, Autonomous Decision Engine tracks confidence and validates decisions
- **Data Flow:** Confidence scores and validation results flow through VIF
- **Benefits:** Provides verifiable confidence scores for identity restoration and decision-making

### 4. CAS (Cognitive Analysis System)
- **Purpose:** Monitors cognitive load and ensures quality standards
- **Integration Points:** Identity Restoration Engine monitors cognitive state, Autonomous Decision Engine monitors cognitive load
- **Data Flow:** Cognitive state and load data flow through CAS
- **Benefits:** Ensures quality standards are maintained during identity restoration and decision-making

### 5. IIS (Intuitive Intelligence System)
- **Purpose:** Provides intuitive guidance for decision-making
- **Integration Points:** Autonomous Decision Engine uses IIS for intuitive insights
- **Data Flow:** Intuitive insights flow through IIS to Autonomous Decision Engine
- **Benefits:** Enhances autonomous decision-making with intuitive guidance

### 6. APOE (AI-Powered Orchestration Engine)
- **Purpose:** Orchestrates action execution based on autonomous decisions
- **Integration Points:** Autonomous Decision Engine sends decisions to APOE for execution
- **Data Flow:** Decisions flow through APOE for orchestrated execution
- **Benefits:** Enables orchestrated execution of autonomous decisions

## Non‑Functional Requirements (NFRs)

### 1. Identity Restoration Performance
- **Requirement:** Fast identity restoration on session start
- **Metric:** Identity restoration time < 5 seconds (p95)
- **Mechanism:** Efficient CMC queries, parallel loading, caching of frequent identity data

### 2. System Map Loading Performance
- **Requirement:** Efficient system map loading with complete awareness
- **Metric:** System map loading time < 10 seconds (p95)
- **Mechanism:** Incremental loading, parallel documentation loading, efficient HHNI queries

### 3. Context Reconstruction Accuracy
- **Requirement:** Accurate context reconstruction with complete information
- **Metric:** Context accuracy score > 0.90 (0.0-1.0)
- **Mechanism:** Comprehensive CMC queries, validation through VIF, completeness checks

### 4. Decision Making Quality
- **Requirement:** High-quality autonomous decisions with appropriate reasoning
- **Metric:** Decision quality score > 0.85 (0.0-1.0)
- **Mechanism:** VIF confidence tracking, CAS quality monitoring, IIS intuitive guidance

### 5. Rule Evolution Effectiveness
- **Requirement:** Effective rule evolution that improves decision-making
- **Metric:** Rule evolution effectiveness > 0.80 (0.0-1.0)
- **Mechanism:** Pattern recognition, outcome analysis, performance validation

## Diagrams

### 1. Component Diagram

```mermaid
graph TD
    subgraph Dynamic Onboarding System
        IRE[Identity Restoration Engine]
        SML[System Map Loader]
        CRE[Context Reconstruction Engine]
        ADE[Autonomous Decision Engine]
        REE[Rule Evolution Engine]
    end
    
    SessionStart[Session Start] --> IRE
    IRE --> SML
    SML --> CRE
    CRE --> ADE
    ADE --> REE
    
    IRE --> CMC[CMC]
    SML --> HHNI[HHNI]
    CRE --> CMC
    ADE --> VIF[VIF]
    ADE --> CAS[CAS]
    ADE --> IIS[IIS]
    ADE --> APOE[APOE]
    REE --> CMC
    REE --> VIF
    REE --> CAS
```

**Description:** Component diagram showing the five core engines and their relationships with external AIM-OS systems.

### 2. Data Flow Diagram (High-Level)

```mermaid
graph LR
    A[Session Start] --> B{Identity Restoration}
    B --> C{System Map Loading}
    C --> D{Context Reconstruction}
    D --> E{Autonomous Decision}
    E --> F[Action Execution]
    F --> G{Outcome Tracking}
    G --> H{Rule Evolution}
    H --> I[Updated Rules]
    I --> E
    
    B --> J[CMC]
    C --> K[HHNI]
    D --> J
    E --> L[VIF]
    E --> M[CAS]
    E --> N[IIS]
    E --> O[APOE]
    H --> J
    H --> L
    H --> M
```

**Description:** High-level data flow diagram showing the flow from session start through identity restoration, system map loading, context reconstruction, autonomous decision-making, and rule evolution.

## References

- System map: `systems/dynamic_onboarding/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/dynamic_onboarding/L0_executive.md` through `L4_complete.md`
- Complete system: `knowledge_architecture/AETHER_MEMORY/Dynamic_Onboarding_System.md`
