"""
Router API Documentation

# Router API Reference

## Overview

The Router system provides intelligent tool selection for AIM-OS. It uses a Scout LLM for fast tool proposals, a Bandit layer for learned scoring, and a Rules engine for safety validation.

## Core Classes

### Router

Main Router class for intelligent tool selection.

**Methods:**

- `decide(ctx: RouterContext) -> ToolCallPlan`
  - Main decision method - generates tool call plan
  - Returns: ToolCallPlan ready for execution

- `update_success_rate(tool_name: str, success: bool)`
  - Update tool success rate after execution

- `learn_from_outcome(plan: ToolCallPlan, result: Dict)`
  - Learn from execution outcome and adjust weights

**Example:**

```python
from router.core.router import Router
from router.types import RouterContext

router = Router(scout, bandit, rules, manifest, snapshot_builder)

ctx = RouterContext(
    goal="Fix test failures",
    task="Run tests",
    confidence=0.8,
    files=["test.py"],
    errors=["Test failed"],
    agent_intent="debug",
    budget={"tokens": 1000}
)

plan = await router.decide(ctx)
```

### ScoutLLM

Fast policy LLM for tool proposal.

**Methods:**

- `propose(snapshot: Snapshot, manifest: ToolManifest) -> List[ToolProposal]`
  - Propose candidate tools based on snapshot
  - Uses pattern caching for performance
  - Returns: List of tool proposals

**Example:**

```python
from router.core.scout import ScoutLLM

scout = ScoutLLM(api_key="your_key")
proposals = await scout.propose(snapshot, manifest)
```

### BanditScorer

Learned policy for tool ranking.

**Methods:**

- `score(proposals: List[ToolProposal], snapshot: Snapshot, manifest: ToolManifest) -> List[RankedTool]`
  - Score and rank tool proposals
  - Uses parallel scoring for performance
  - Returns: List of ranked tools sorted by score

- `learn_from_outcome(proposal: ToolProposal, outcome: Dict)`
  - Learn from execution outcome and adjust weights

**Example:**

```python
from router.core.bandit import BanditScorer

bandit = BanditScorer(cmc_client, hhni_client, vif_client)
ranked = await bandit.score(proposals, snapshot, manifest)
```

### RouterCache

Caching system for performance optimization.

**Methods:**

- `get_cached_proposals(snapshot: Snapshot) -> Optional[List[ToolProposal]]`
  - Get cached tool proposals for snapshot

- `cache_proposals(snapshot: Snapshot, proposals: List[ToolProposal])`
  - Cache tool proposals for snapshot

- `get_stats() -> Dict[str, Any]`
  - Get cache statistics

**Example:**

```python
from router.core.cache import RouterCache

cache = RouterCache(ttl_seconds=300, max_size=1000)
cached = await cache.get_cached_proposals(snapshot)
```

## Types

### RouterContext

Context for router decision-making.

```python
@dataclass
class RouterContext:
    goal: str
    task: str
    confidence: float
    files: List[str]
    errors: List[str]
    agent_intent: str
    budget: Dict[str, float]
    suggested_tools: Optional[List[str]] = None
    log_insights: Optional[Dict[str, Any]] = None
```

### ToolCallPlan

Complete tool call plan (DAG).

```python
@dataclass
class ToolCallPlan:
    plan_id: str
    goal: str
    steps: List[ToolCallStep]
    context: RouterContext
    max_depth: int = 3
    budget: Dict[str, float] = None
```

## Performance

- **Router Decision Time:** <200ms average (with caching)
- **Scout Analysis Time:** <700ms average
- **Cache Hit Rate:** ~80% for repeated contexts

## Integration

Router integrates with:
- **APOE:** Tool execution
- **VIF:** Quality gates
- **SEG:** Evidence chains
- **CMC:** Decision storage
- **HHNI:** Context retrieval
- **TCS:** Timeline tracking

