---
id: "router_T2_architecture"
system: "router"
component: null
level: "T2"
type: "architecture"
title: "Router Architecture"
description: "2,000-word architecture document for Router (APOE-MCP Router)"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["router", "apoe", "mcp", "tool-selection", "t0-t4", "transitional"]
dependencies: ["router_T1_overview"]
related_docs: ["router_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Router – T2 Architecture (≈2000 words)

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements:**

**Code:** Router implementation files (`packages/router/core/`), Router class, ScoutLLM, BanditScorer, RulesEngine, ToolManifest, SnapshotBuilder, RouterCache  
**Docs:** T0-T4 documentation (T0_executive.md, T1_overview.md, T2_architecture.md, T3_detailed.md, T4_complete.md), usage.envelope.md  
**Tests:** Router test suite (`packages/router/tests/test_router.py`), unit tests, integration tests  
**Traces:** VIF witnesses (tool selection decisions), SEG evidence (selection chains), TCS timeline entries (decision events), CMC decision atoms (tool weights, success rates)

**Parity Requirement:** P ≥ 0.90 for all changes  
**Cross-Tagging:** All quartet elements must be tagged with change ID (router-change-YYYYMMDD-HHMMSS) and semantically aligned

### **Quartet Parity Formula:**

```
P = (C_code×docs + C_code×tests + C_code×traces +
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
- C_code×docs = semantic similarity between code and docs
- C_code×tests = semantic similarity between code and tests
- C_code×traces = semantic similarity between code and traces
- C_docs×tests = semantic similarity between docs and tests
- C_docs×traces = semantic similarity between docs and traces
- C_tests×traces = semantic similarity between tests and traces

Target: P ≥ 0.90 for all changes
```

### **Cross-Tagging Protocol:**

**Change ID Format:** `router-change-YYYYMMDD-HHMMSS` (e.g., `router-change-20250127-120000`)

**Tagging Requirements:**
- **Code:** Change ID in comments/metadata within modified code sections
- **Docs:** Change ID in frontmatter `tags` array and/or inline comments
- **Tests:** Change ID in test function docstrings/comments
- **Traces:** Change ID in VIF witness metadata, SEG provenance links, timeline entry metadata, decision log filename/content

**Workflow:**
1. Generate Change ID at start of Router modification
2. Modify code (Router implementation) → Tag with Change ID
3. Update docs (T-level docs) → Tag with Change ID
4. Update/add tests (Router test suite) → Tag with Change ID
5. Create traces (VIF witnesses, SEG, timeline, decision log) → Tag with Change ID
6. Validate quartet parity (P ≥ 0.90) before merge

---

## System Architecture

Router implements a deterministic control loop: **Observe → Propose → Score → Plan → Execute → Validate → Learn**. The system uses three "brains": Scout LLM (fast proposals), Bandit layer (learned ranking), and Rules engine (safety gates). This architecture enables autonomous operation with confidence ≥0.70 by maintaining rolling context, enforcing preconditions, and learning from outcomes.

### **Control Loop Architecture**

**1. Observe Phase:**
- **SnapshotBuilder** aggregates system state from AIM-OS systems
- Queries CMC for recent decisions and tool weights
- Queries HHNI for semantic context relevant to current goal
- Queries VIF for confidence status and quality gates
- Queries SEG for evidence chains and contradictions
- Queries TCS for timeline cursor and recent events
- Builds comprehensive **Snapshot** with all context

**2. Propose Phase:**
- **ScoutLLM** receives snapshot and tool manifest
- Checks pattern cache for similar scenarios (10-minute TTL)
- Builds optimized prompt (reduced token usage: goal 200 chars, context 300 chars, top 15 tools)
- Calls Cerebras LLM (<700ms timeout) for tool proposals
- Parses JSON response into **ToolProposal** objects with rationale
- Caches pattern for future use (LRU eviction, max 100 patterns)

**3. Score Phase:**
- **BanditScorer** receives proposals and snapshot
- Scores each proposal in parallel (ThreadPoolExecutor, 4 workers)
- Computes utility function: ContextFit + SuccessRate + PreconditionSatisfaction + ExpectedInfoGain + Parallelizability - Cost - Latency - Risk
- Checks score cache for pre-computed values
- Ranks proposals by score (descending)
- Returns **RankedTool** list sorted by utility

**4. Plan Phase:**
- **Router** compiles ranked tools into **ToolCallPlan**
- Selects top-k tools under budget constraints
- Creates **ToolCallStep** objects with tool name, arguments, preflight checks
- Determines parallelization groups (read-only tools can parallelize)
- Sets timeouts (2x average latency per tool)
- Generates plan ID and context

**5. Validate Phase:**
- **RulesEngine** validates plan against constraints
- Checks depth limit (max 3 steps)
- Checks step count (max 20 steps)
- Checks budget limits (tokens, cost, time)
- Checks VIF gates for high-risk tools
- Checks parallelization limits (max 3 parallel)
- Returns **ValidationResult** with passed status and reasons

**6. Execute Phase:**
- Plan sent to **APOE** for execution
- APOE dispatches tools via role agents
- Execution results returned to Router
- Success/failure tracked per tool

**7. Learn Phase:**
- **BanditScorer** learns from execution outcomes
- Updates tool success rates in ToolManifest
- Adjusts Bandit weights via gradient descent
- Stores updated weights in CMC
- Records evidence in SEG
- Creates timeline entry in TCS

---

## Component Details

### **1. Router (Main Orchestrator)**

**Purpose:** Coordinate control loop and generate tool call plans

**Key Methods:**
- `decide(ctx: RouterContext) -> ToolCallPlan` - Main decision method
- `_compile_plan(ranked, snapshot, ctx) -> ToolCallPlan` - Compile ranked tools into plan
- `_handle_validation_failure(plan, validation) -> ToolCallPlan` - Handle validation failures
- `update_success_rate(tool_name, success)` - Update tool success rate
- `learn_from_outcome(plan, result)` - Learn from execution outcomes

**Dependencies:** ScoutLLM, BanditScorer, RulesEngine, ToolManifest, SnapshotBuilder, RouterCache

**Performance:** Target <200ms decision time (p95)

### **2. ScoutLLM (Fast Policy LLM)**

**Purpose:** Propose candidate tools using fast LLM (Cerebras)

**Key Methods:**
- `propose(snapshot, manifest) -> List[ToolProposal]` - Propose tools based on snapshot
- `_get_pattern_key(snapshot) -> str` - Generate pattern key for caching
- `_get_cached_pattern(key) -> Optional[List[ToolProposal]]` - Retrieve cached pattern
- `_cache_pattern(key, proposals)` - Cache pattern with TTL
- `_build_optimized_prompt(snapshot, manifest) -> str` - Build token-optimized prompt
- `_call_llm(prompt) -> str` - Call Cerebras API
- `_parse_proposals(response, snapshot) -> List[ToolProposal]` - Parse LLM response

**Optimizations:**
- Pattern caching (10-minute TTL, LRU eviction, max 100 patterns)
- Request batching (50ms window)
- Reduced token usage (goal 200 chars, context 300 chars, top 15 tools)

**Performance:** Target <700ms latency

### **3. BanditScorer (Learned Policy Layer)**

**Purpose:** Score and rank tool proposals using learned weights

**Key Methods:**
- `score(proposals, snapshot, manifest) -> List[RankedTool]` - Score and rank proposals
- `_score_single_proposal(proposal, snapshot, manifest) -> RankedTool` - Score single proposal
- `_compute_context_fit(proposal, snapshot) -> float` - Compute context fit (0-1)
- `_compute_success_rate(tool_name) -> float` - Get historical success rate
- `_compute_precondition_satisfaction(proposal, tool) -> float` - Check preconditions
- `_compute_expected_info_gain(proposal, snapshot) -> float` - Estimate info gain
- `_compute_parallelizability(tool) -> float` - Check parallelization capability
- `_compute_risk_penalty(tool, snapshot) -> float` - Compute risk penalty
- `learn_from_outcome(proposal, outcome)` - Update weights via gradient descent

**Weights:**
- ContextFit: 0.3
- SuccessRate: 0.25
- Precondition: 0.2
- InfoGain: 0.15
- Parallelizability: 0.1

**Penalty Weights:**
- Cost: 0.1
- Latency: 0.05
- Risk: 0.15

**Optimizations:**
- Parallel scoring (ThreadPoolExecutor, 4 workers)
- Pre-computed score cache
- Batch embedding lookups

**Performance:** Target <100ms scoring time

### **4. RulesEngine (Safety Gates)**

**Purpose:** Validate tool call plans against safety, budget, and policy constraints

**Key Methods:**
- `validate(plan: ToolCallPlan) -> ValidationResult` - Validate plan
- `_check_vif_gates(plan) -> VIFGate` - Check VIF gates for high-risk tools

**Constraints:**
- Max depth: 3 steps
- Max steps: 20 steps
- Budget limits: tokens (100k), cost ($10), time (30s)
- Max parallel: 3 steps
- VIF gates: Required for high-risk tools

**Performance:** Target <15ms validation time

### **5. ToolManifest (Tool Registry)**

**Purpose:** Registry of all available tools with capabilities, requirements, metadata

**Key Methods:**
- `register(tool: Tool)` - Register tool in manifest
- `get_tool(name: str) -> Optional[Tool]` - Get tool by name
- `list_tools() -> List[Tool]` - List all tools
- `find_tools_by_capability(capability: str) -> List[Tool]` - Find tools by capability
- `find_tools_by_tag(tag: str) -> List[Tool]` - Find tools by tag
- `initialize_aimos_tools()` - Register AIM-OS MCP tools (59+ tools)

**Tool Schema:**
- name, version, capability (tags), inputs, outputs, preconditions, side_effects, avg_latency_ms, avg_cost, risk, success_rate, examples

**Performance:** Target <10ms lookup time

### **6. SnapshotBuilder (Context Aggregator)**

**Purpose:** Aggregate system state from AIM-OS systems

**Key Methods:**
- `build(ctx: RouterContext) -> Snapshot` - Build snapshot from context

**Aggregates:**
- CMC: Recent decisions, tool weights, success rates
- HHNI: Semantic context, relevant nodes, embeddings
- VIF: Confidence status, quality gates, validation results
- SEG: Evidence chains, contradictions, synthesis results
- TCS: Timeline cursor, recent events, sequence IDs

**Performance:** Target <150ms aggregation time

### **7. RouterCache (Performance Optimization)**

**Purpose:** Cache context snapshots and tool proposals for performance

**Key Methods:**
- `get_cached_proposals(snapshot: Snapshot) -> Optional[List[ToolProposal]]` - Get cached proposals
- `cache_proposals(snapshot: Snapshot, proposals: List[ToolProposal])` - Cache proposals
- `get_cached_embedding(text: str) -> Optional[List[float]]` - Get cached embedding
- `cache_embedding(text: str, embedding: List[float])` - Cache embedding
- `get_stats() -> Dict[str, Any]` - Get cache statistics

**Features:**
- TTL expiration (default 5 minutes, configurable)
- LRU eviction (max 1000 entries)
- Embedding cache for context fit computation
- Snapshot key generation (hash-based)

**Performance:** Target >80% cache hit rate

---

## Data Flow

### **Request Flow:**

```
User/Agent Request
  ↓
RouterContext (goal, task, confidence, files, errors, agent_intent, budget)
  ↓
SnapshotBuilder.build(ctx)
  ↓
Snapshot (cmc_decisions, hhni_context, vif_status, seg_evidence, tcs_cursor, goal, summary)
  ↓
RouterCache.get_cached_proposals(snapshot)
  ↓ (if cache miss)
ScoutLLM.propose(snapshot, manifest)
  ↓
List[ToolProposal] (tool_name, rationale, draft_arguments, confidence)
  ↓
RouterCache.cache_proposals(snapshot, proposals)
  ↓
BanditScorer.score(proposals, snapshot, manifest)
  ↓
List[RankedTool] (proposal, score, context_fit, success_rate, precondition_satisfied, expected_info_gain, parallelizable)
  ↓
Router._compile_plan(ranked, snapshot, ctx)
  ↓
ToolCallPlan (plan_id, goal, steps, context, max_depth, budget)
  ↓
RulesEngine.validate(plan)
  ↓
ValidationResult (passed, reasons, warnings)
  ↓ (if passed)
APOE.execute(plan)
  ↓
ExecutionResult (success, outputs, errors)
  ↓
Router.learn_from_outcome(plan, result)
  ↓
BanditScorer.learn_from_outcome(proposal, outcome)
  ↓
Updated weights stored in CMC, evidence in SEG, timeline in TCS
```

### **Learning Flow:**

```
Execution Outcome
  ↓
BanditScorer.learn_from_outcome(proposal, outcome)
  ↓
Compute reward signal (success: 0.5, quality_score: 0.3, user_feedback: 0.2)
  ↓
Normalize reward to [0, 1]
  ↓
Compute feature vector (context_fit, success_rate, precondition, info_gain, parallelizable)
  ↓
Gradient descent weight update (learning_rate: 0.01)
  ↓
Normalize weights to sum to 1.0
  ↓
CMC.store_tool_weights(tool_name, weights, reward)
  ↓
Updated weights used in next scoring cycle
```

---

## Interfaces

### **RouterContext**

```python
@dataclass
class RouterContext:
    goal: str  # User/agent goal
    task: str  # Current task description
    confidence: float  # Current confidence (0-1)
    files: List[str]  # Relevant files
    errors: List[str]  # Current errors
    agent_intent: str  # Agent intent (debug, build, test, etc.)
    budget: Dict[str, float]  # Budget constraints (tokens, cost, time)
    suggested_tools: Optional[List[str]] = None  # Suggested tools from Log-Sentinels
    log_insights: Optional[Dict[str, Any]] = None  # Log insights from Log-Sentinels
```

### **Snapshot**

```python
@dataclass
class Snapshot:
    cmc_decisions: List[Dict[str, Any]]  # Recent CMC decisions
    hhni_context: List[Dict[str, Any]]  # HHNI semantic context
    vif_status: Dict[str, Any]  # VIF confidence status
    seg_evidence: List[Dict[str, Any]]  # SEG evidence chains
    tcs_cursor: Dict[str, Any]  # TCS timeline cursor
    goal: str  # Current goal
    summary: str  # Context summary
```

### **ToolCallPlan**

```python
@dataclass
class ToolCallPlan:
    plan_id: str  # Unique plan identifier
    goal: str  # Plan goal
    steps: List[ToolCallStep]  # Execution steps
    context: RouterContext  # Original context
    max_depth: int = 3  # Maximum depth
    budget: Dict[str, float] = None  # Budget constraints
```

### **ToolCallStep**

```python
@dataclass
class ToolCallStep:
    id: str  # Step identifier
    tool: str  # Tool name
    args: Dict[str, Any]  # Tool arguments
    parallel_group: Optional[str] = None  # Parallel group ID
    preflight: Optional[List[VIFCheck]] = None  # VIF preflight checks
    timeout_ms: Optional[int] = None  # Timeout in milliseconds
    on_fail: Optional[List[Fallback]] = None  # Fallback actions
```

---

## Integration Points

### **APOE Integration**

Router generates **ToolCallPlan** objects that APOE executes. Plans include:
- Tool steps with arguments
- Parallelization groups
- VIF preflight checks
- Timeout constraints
- Fallback actions

APOE returns execution results, which Router uses for learning.

### **CMC Integration**

Router stores:
- Decision atoms (tool selections, plans)
- Tool weights (Bandit learned weights)
- Success rates (per-tool tracking)

Router queries:
- Recent decisions (for context)
- Tool weights (for scoring)
- Success rates (for ranking)

### **HHNI Integration**

Router queries HHNI for:
- Semantic context relevant to current goal
- Relevant nodes and embeddings
- Context fit computation

### **VIF Integration**

Router uses VIF for:
- Quality gates (preflight checks)
- Confidence tracking
- Validation requests

Router emits:
- VIF witnesses (tool selection decisions)
- Confidence scores
- Provenance traces

### **SEG Integration**

Router records in SEG:
- Decision evidence (tool selection chains)
- Outcome evidence (execution results)
- Learning evidence (weight updates)

### **TCS Integration**

Router creates TCS entries for:
- Decision events (tool selections)
- Execution events (plan execution)
- Learning events (weight updates)

### **Log-Sentinels Integration**

Router receives from Log-Sentinels:
- Tool suggestions (from Scout/Forensics reports)
- Log insights (anomaly detection)
- Forensics reports (root cause analysis)

Router uses suggestions to:
- Enhance tool proposals
- Improve context understanding
- Guide tool selection

---

## Performance Characteristics

### **Latency Targets:**

- **Router Decision:** <200ms (p95)
- **Scout Analysis:** <700ms (p95)
- **Bandit Scoring:** <100ms (p95)
- **Rules Validation:** <15ms (p95)
- **Snapshot Building:** <150ms (p95)
- **Cache Lookup:** <5ms (p95)

### **Throughput:**

- **Decisions per second:** 5+ (with caching)
- **Cache hit rate:** >80%
- **Tool selection accuracy:** >90%

### **Optimization Strategies:**

1. **Pattern Caching:** Scout caches common scenarios (10-minute TTL)
2. **Request Batching:** Scout batches similar requests (50ms window)
3. **Parallel Scoring:** Bandit scores proposals in parallel (4 workers)
4. **Pre-computed Cache:** Bandit caches pre-computed scores
5. **LRU Eviction:** Cache evicts least recently used entries
6. **Token Reduction:** Scout uses optimized prompts (reduced token usage)

---

## Security & Governance

### **Security:**

- **VIF Gates:** High-risk tools require VIF validation
- **Budget Enforcement:** Hard limits prevent resource violations
- **Precondition Checks:** Tools cannot execute without preconditions
- **Audit Logging:** All decisions recorded in CMC, SEG, TCS

### **Governance:**

- **Tool Selection:** Deterministic, inspectable process
- **Learning Tracking:** All weight updates tracked
- **Evidence Recording:** All decisions evidenced in SEG
- **Quartet Parity:** Code/Docs/Tests/Traces maintained

---

**Read T3 for detailed implementation guide.**

