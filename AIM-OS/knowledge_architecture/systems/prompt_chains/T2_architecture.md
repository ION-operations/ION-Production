---
id: "prompt_chains_T2_architecture"
system: "prompt_chains"
component: null
level: "T2"
type: "architecture"
title: "Prompt Chains Architecture"
description: "2000-word architecture document for Prompt Chains system"
audience: "developers, architects"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-05T12:30:00Z"
updated: "2025-11-05T12:30:00Z"
author: "aether"
status: "complete"
tags: ["prompt-chains", "architecture", "meta-orchestration", "foundation-chains", "t0-t6"]
dependencies: ["apoe", "cmc", "hhni", "vif", "seg", "sdfcvf", "timeline_goals_integration"]
related_docs: ["prompt_chains_T0_executive", "prompt_chains_T1_overview", "PROMPT_CHAINS_META_ARCHITECTURE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Prompt Chains – T2 Architecture (≈2,000 words)

## 🏗️ **COMPLETE SYSTEM ARCHITECTURE**

### **The Meta-Architectural Insight**

**AIM-OS itself IS a complex prompt chain.** Every operation follows an implicit pattern:

```
Intent → Planning (APOE) → Memory (CMC) → Retrieval (HHNI) → 
Validation (VIF) → Synthesis (SEG) → Quality (SDF-CVF) → Result
```

**Prompt Chains makes this explicit** through executable workflow graphs with nodes, edges, conditions, and system integration.

### **System Overview Diagram**

```
┌────────────────────────────────────────────────────────────────────┐
│                  PROMPT CHAINS ARCHITECTURE                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               LAYER 1: CHAIN DEFINITIONS                      │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Chain Specification (YAML/JSON)                       │  │  │
│  │  │  - Nodes (operations)                                  │  │  │
│  │  │  - Edges (transitions)                                 │  │  │
│  │  │  - Conditions (if/else logic)                          │  │  │
│  │  │  - Gates (quality enforcement)                         │  │  │
│  │  │  - System Integration (CMC/HHNI/VIF/APOE/SEG/SDF-CVF) │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Compilation                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          LAYER 2: EXECUTION ENGINE (Python)                  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  ChainExecutor                                          │  │  │
│  │  │  - Parses chain definitions                            │  │  │
│  │  │  - Executes nodes sequentially                         │  │  │
│  │  │  - Evaluates edge conditions                           │  │  │
│  │  │  - Enforces quality gates                              │  │  │
│  │  │  - Routes based on confidence                          │  │  │
│  │  │  - Integrates with all AIM-OS systems                  │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Orchestration                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         LAYER 3: SYSTEM INTEGRATION                          │  │
│  │  ┌───────────┐  ┌───────┐  ┌──────┐  ┌──────┐  ┌──────┐   │  │
│  │  │    CMC    │  │  HHNI │  │  VIF │  │ APOE │  │  SEG │   │  │
│  │  │  Memory   │  │ Index │  │ Valid│  │ Plan │  │ Synth│   │  │
│  │  └───────────┘  └───────┘  └──────┘  └──────┘  └──────┘   │  │
│  │  ┌─────────────┐  ┌────────────────────────────────────┐   │  │
│  │  │  SDF-CVF    │  │  Timeline-Goals Integration        │   │  │
│  │  │  Quality    │  │  Bidirectional chain-goal linkage  │   │  │
│  │  └─────────────┘  └────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Storage & Tracking                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │            LAYER 4: STORAGE & PROVENANCE                     │  │
│  │  - Chain definitions in CMC (bitemporal)                     │  │
│  │  - Execution records in Timeline (temporal tracking)         │  │
│  │  - Goal linkage in Goals system (bidirectional)              │  │
│  │  - Confidence scores in VIF (validation)                     │  │
│  │  - Quality metrics in SDF-CVF (enforcement)                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📦 **CORE COMPONENTS**

### **1. Chain Definition Model**

**Data Structure:**

```python
@dataclass
class PromptChain:
    """
    Executable workflow graph for AI operations
    
    Represents a chain of operations with dynamic branching,
    quality gates, and complete AIM-OS system integration.
    """
    
    # === IDENTITY ===
    chain_id: str              # Unique chain identifier (e.g., "chain-autonomous-001")
    name: str                  # Human-readable name
    description: str           # Complete chain purpose
    version: str               # Semantic version (e.g., "1.2.0")
    
    # === CLASSIFICATION ===
    chain_type: ChainType      # META | ATOMIC | COMPOSITE | ADAPTIVE
    tier: int                  # Tier 1 (foundation) or Tier 2+ (extended)
    priority: ChainPriority    # CRITICAL | HIGH | MEDIUM | LOW
    
    # === STRUCTURE ===
    nodes: List[ChainNode]     # Operations (see Node structure below)
    edges: List[ChainEdge]     # Transitions between nodes
    start_node_id: str         # Entry point node ID
    end_node_ids: List[str]    # Valid exit points
    
    # === INTEGRATION ===
    goal_id: Optional[str]     # Goal this chain serves (bidirectional link)
    parent_chain_id: Optional[str]  # If this is a sub-chain
    sub_chain_ids: List[str]   # If this orchestrates other chains
    
    # === METADATA ===
    created_at: datetime
    updated_at: datetime
    created_by: str            # "aether" | "human"
    
    # === PROVENANCE ===
    execution_count: int = 0   # How many times executed
    success_count: int = 0     # How many successful executions
    failure_count: int = 0     # How many failed executions
    average_duration: float = 0.0  # Average execution time (seconds)
```

### **2. Node Structure**

**ChainNode Model:**

```python
@dataclass
class ChainNode:
    """
    Single operation in a chain
    
    Every node explicitly declares which AIM-OS system it uses,
    enabling complete traceability and system integration.
    """
    
    # === IDENTITY ===
    node_id: str               # Unique node ID within chain
    name: str                  # Human-readable operation name
    description: str           # What this node does
    
    # === OPERATION ===
    operation_type: NodeType   # SYSTEM_CALL | DECISION | GATE | BRANCH | MERGE
    
    # === SYSTEM INTEGRATION (Explicit!) ===
    system: Optional[str]      # Which AIM-OS system: "CMC" | "HHNI" | "VIF" | etc.
    operation: Optional[str]   # System operation: "store_atom" | "retrieve" | etc.
    parameters: Dict[str, Any] # Operation parameters
    
    # === QUALITY ===
    confidence_threshold: float = 0.70  # Minimum confidence to proceed
    quality_gate: Optional[QualityGate] = None  # SDF-CVF validation
    
    # === PROVENANCE ===
    execution_required: bool = True  # Can this be skipped?
    timeout_seconds: Optional[float] = None  # Max execution time
```

**Node Types:**

| Type | Purpose | Example |
|------|---------|---------|
| **SYSTEM_CALL** | Call AIM-OS system | Store in CMC, retrieve from HHNI |
| **DECISION** | Conditional branching | If confidence > 0.70, proceed; else abstain |
| **GATE** | Quality enforcement | SDF-CVF quartet parity check |
| **BRANCH** | Parallel execution | Execute multiple paths simultaneously |
| **MERGE** | Combine results | Aggregate outputs from parallel branches |

### **3. Edge Structure**

**ChainEdge Model:**

```python
@dataclass
class ChainEdge:
    """
    Transition between nodes with conditional logic
    
    Edges enable dynamic routing based on runtime conditions,
    confidence scores, quality results, and system state.
    """
    
    # === IDENTITY ===
    edge_id: str               # Unique edge ID
    from_node_id: str          # Source node
    to_node_id: str            # Target node
    
    # === CONDITION (Optional - always taken if None) ===
    condition_type: Optional[ConditionType] = None  # CONFIDENCE | QUALITY | RESULT | CUSTOM
    condition_expression: Optional[str] = None  # Python expression: "confidence > 0.70"
    
    # === METADATA ===
    label: str = ""            # Human-readable label for visualization
    weight: float = 1.0        # Routing weight (for optimization)
```

**Condition Types:**

| Type | Expression Example | Meaning |
|------|-------------------|---------|
| **CONFIDENCE** | `confidence > 0.70` | Route based on VIF confidence score |
| **QUALITY** | `quartet_parity >= 0.90` | Route based on SDF-CVF quality |
| **RESULT** | `status == "success"` | Route based on operation result |
| **CUSTOM** | `context["x"] > 100` | Custom Python expression |

---

## 🎯 **CHAIN TYPES & PATTERNS**

### **1. Meta-Orchestration Chains**

**Purpose:** Orchestrate other chains and AIM-OS systems

**Pattern:**
```
[Start] → [APOE: Generate Plan] → [Chain Selection] → [Execute Sub-Chains] → [Aggregate Results] → [End]
           │                         │                      │
           ├─→ [CMC Storage]         ├─→ [VIF Confidence]  └─→ [SDF-CVF Quality]
```

**Example: Autonomous Operation Chain**
- Orchestrates entire autonomous session
- Calls sub-chains for task execution
- Aggregates results, tracks confidence, maintains quality

**Key Features:**
- **Recursive orchestration** - chains orchestrating chains
- **Dynamic sub-chain selection** - chooses chains based on runtime conditions
- **Result aggregation** - combines outputs from multiple chains

### **2. Atomic Operation Chains**

**Purpose:** Single-purpose, optimized chains for specific operations

**Pattern:**
```
[Start] → [VIF: Check Confidence] → [System Operation] → [VIF: Track Result] → [End]
```

**Example: Memory Storage Chain**
- Check confidence ≥ 0.70
- Store atom in CMC
- Track confidence in VIF
- Return atom_id

**Key Features:**
- **Simple, linear flow** - no complex branching
- **Single system focus** - optimized for one operation
- **Fast execution** - minimal overhead

### **3. Composite Chains**

**Purpose:** Chains made of other chains (composition)

**Pattern:**
```
[Start] → [Chain 1] → [Chain 2] → [Chain 3] → [Merge Results] → [End]
           │            │            │
           └──── Parallel execution ──┘
```

**Example: Code Review Chain**
- Composition of Analysis Chain + Optimization Chain + Testing Chain
- All execute in parallel
- Results merged for final review

**Key Features:**
- **Chain composition** - building blocks approach
- **Parallel execution** - multiple chains simultaneously
- **Result merging** - combining outputs intelligently

### **4. Adaptive Chains**

**Purpose:** Chains that modify themselves based on results

**Pattern:**
```
[Start] → [Operation] → [Result Analysis] → [Self-Modification] → [Retry with New Strategy] → [End]
                         │                      │
                         └─→ [Learn from Failure] ──┘
```

**Example: Self-Optimizing Chain**
- Executes operation
- Analyzes result quality
- If quality low, modifies chain strategy
- Retries with improved approach

**Key Features:**
- **Self-modification** - chains evolve themselves
- **Learning** - improve from successes/failures
- **Adaptive routing** - dynamic strategy changes

---

## 🔗 **SYSTEM INTEGRATION ARCHITECTURE**

### **CMC Integration (Memory)**

**Every chain operation stores provenance in CMC:**

```python
# Node: Store Chain Execution
system: "CMC"
operation: "store_atom"
parameters:
  mpd_id: chain_execution_id
  data:
    chain_id: "chain-autonomous-001"
    node_id: "task-execution"
    result: execution_result
    confidence: 0.85
    quality: 0.92
  atom_type: "chain_execution"
  valid_from: execution_start
  valid_to: null  # Current version
```

**Enables:**
- Complete audit trail of all chain executions
- Time-travel queries ("what happened at sequence 15?")
- Bitemporal version tracking

### **HHNI Integration (Retrieval)**

**Chains retrieve relevant context from semantic index:**

```python
# Node: Retrieve Related Chains
system: "HHNI"
operation: "semantic_search"
parameters:
  query: "autonomous operation patterns"
  top_k: 5
  filters:
    type: "chain"
    tier: 1
```

**Enables:**
- "Find similar chains" queries
- Related chain discovery
- Knowledge reuse across chains

### **VIF Integration (Confidence)**

**Every decision node checks confidence:**

```python
# Node: Confidence Gate
system: "VIF"
operation: "check_confidence"
parameters:
  operation_id: node_id
  threshold: 0.70
  
# Edge: Route based on confidence
condition: "confidence >= 0.70"
  true_path: proceed_node
  false_path: abstain_node
```

**Enables:**
- Confidence-gated execution
- Automatic abstention when uncertain
- Confidence tracking throughout chain

### **APOE Integration (Planning)**

**Meta-chains use APOE for planning:**

```python
# Node: Generate Task Plan
system: "APOE"
operation: "compile_plan"
parameters:
  intent: "autonomous operation"
  context: current_state
  constraints: ["confidence >= 0.70", "goal_aligned"]
```

**Enables:**
- Dynamic task generation
- Plan compilation from intent
- Orchestration of sub-chains

### **SEG Integration (Synthesis)**

**Chains synthesize knowledge from results:**

```python
# Node: Synthesize Learning
system: "SEG"
operation: "synthesize_knowledge"
parameters:
  inputs: [chain_result_1, chain_result_2, chain_result_3]
  synthesis_type: "composite"
```

**Enables:**
- Knowledge synthesis across chain executions
- Learning from multiple executions
- Evidence graph construction

### **SDF-CVF Integration (Quality)**

**Quality gates enforce standards:**

```python
# Node: Quality Gate
system: "SDF-CVF"
operation: "check_quartet_parity"
parameters:
  code_hash: result.code_hash
  doc_hash: result.doc_hash
  test_hash: result.test_hash
  nl_tag_hash: result.nl_tag_hash
  threshold: 0.90
  
# Edge: Route based on quality
condition: "quartet_parity >= 0.90"
  true_path: success_node
  false_path: fix_issues_node
```

**Enables:**
- Quality enforcement at every step
- Automatic issue detection
- Quality-based routing

---

## 🔄 **EXECUTION ENGINE ARCHITECTURE**

### **ChainExecutor Class**

**Core execution logic:**

```python
class ChainExecutor:
    """
    Executes prompt chains with complete system integration
    
    Handles node execution, edge evaluation, condition routing,
    quality gates, confidence checks, and provenance tracking.
    """
    
    def execute_chain(
        self,
        chain: PromptChain,
        context: Dict[str, Any],
        goal_id: Optional[str] = None
    ) -> ChainExecutionResult:
        """
        Execute a chain from start to end
        
        Args:
            chain: Chain to execute
            context: Initial context (variables, state)
            goal_id: Optional goal this execution serves
            
        Returns:
            ChainExecutionResult with outputs, provenance, metrics
        """
        # Initialize execution
        execution_id = generate_execution_id()
        current_node_id = chain.start_node_id
        execution_log = []
        
        # Store execution start in CMC
        self._store_execution_start(execution_id, chain, context)
        
        # Main execution loop
        while current_node_id not in chain.end_node_ids:
            # Get current node
            node = chain.get_node(current_node_id)
            
            # Execute node
            node_result = self._execute_node(node, context)
            
            # Check confidence (if required)
            if node.confidence_threshold:
                if node_result.confidence < node.confidence_threshold:
                    # Abstain - confidence too low
                    return self._abstain_result(execution_id, node, node_result)
            
            # Check quality gate (if required)
            if node.quality_gate:
                gate_result = self._check_quality_gate(node.quality_gate, node_result)
                if not gate_result.passed:
                    # Quality gate failed
                    return self._quality_failure_result(execution_id, node, gate_result)
            
            # Log execution
            execution_log.append({
                'node_id': node.node_id,
                'result': node_result,
                'confidence': node_result.confidence,
                'timestamp': datetime.now()
            })
            
            # Evaluate outgoing edges to find next node
            next_node_id = self._evaluate_edges(chain, current_node_id, context, node_result)
            current_node_id = next_node_id
        
        # Store execution end in CMC
        result = self._store_execution_end(execution_id, execution_log)
        
        # Update goal progress (if linked)
        if goal_id:
            self._update_goal_from_chain_execution(goal_id, result)
        
        return result
```

**Key Methods:**

- **`_execute_node()`**: Executes single node (system call, decision, gate)
- **`_evaluate_edges()`**: Evaluates edge conditions to find next node
- **`_check_quality_gate()`**: Enforces SDF-CVF quality standards
- **`_store_execution_start/end()`**: CMC provenance tracking
- **`_update_goal_from_chain_execution()`**: Goal-chain bidirectional linkage

---

## 🌉 **TEMPORAL CONSCIOUSNESS INTEGRATION**

### **Bidirectional Chain-Goal Linkage**

**Goals track chains working toward them:**

```python
# In GoalTimelineNode
related_chain_ids: List[str] = field(default_factory=list)
completed_via_chain_id: Optional[str] = None

# When chain starts for goal
goal.related_chain_ids.append(chain_id)

# When chain completes goal
goal.completed_via_chain_id = chain_id
goal.status = GoalStatus.COMPLETED
goal.progress = 1.0
```

**Chains track which goal they serve:**

```python
# In PromptChain
goal_id: Optional[str] = None  # Goal this chain serves

# When creating chain for goal
chain = PromptChain(
    chain_id="chain-implement-viz",
    goal_id="OBJ-12",
    ...
)
```

**Timeline tracks chain executions:**

```python
# ChainExecutionRecord as Timeline Entry
timeline_entry = TimelineEntry(
    entry_type="chain_execution",
    content={
        'chain_id': chain.chain_id,
        'goal_id': chain.goal_id,
        'execution_id': execution_id,
        'nodes_executed': len(execution_log),
        'duration': execution_duration,
        'result': execution_result
    },
    sequence=current_sequence
)
```

**Complete Temporal Graph:**
```
Timeline Entries (Past) ← ChainExecutionRecords ← Chain Definitions
                             ↕ Bidirectional
Goals (Present) ← related_chain_ids / goal_id → Prompt Chains (Future)
```

---

## 📋 **NEXT STEPS & IMPLEMENTATION**

**Phase 1: Foundation Chains (Tier 1)**
1. Implement ChainExecutor engine
2. Create 4 foundation chains (Autonomous Operation, A-H Protocol, T0-T6 Documentation, Code Implementation)
3. Integrate with all AIM-OS systems
4. Test with real autonomous session

**Phase 2: Extended Chains (Tier 2)**
5. Build atomic operation chains
6. Build composite chains
7. Build adaptive chains
8. Create chain library

**Phase 3: Visualization & UI**
9. Temporal Consciousness Graph (chain visualization)
10. Chain execution dashboard
11. Real-time chain monitoring

---

**Status:** Design Complete (Nov 2, 2025) | **Implementation:** Planned  
**Next:** T3 Detailed with complete node/edge reference and Foundation Chains specs  
**Impact:** Enables recursive meta-orchestration for autonomous AI operation

