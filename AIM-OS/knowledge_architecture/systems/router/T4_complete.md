---
id: "router_T4_complete"
system: "router"
component: null
level: "T4"
type: "complete"
title: "Router Complete Reference"
description: "15,000+ word complete reference for Router"
audience: "reference, complete details"
confidence_threshold: 0.60
token_cost: 15000
word_count: 15000
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["router", "apoe", "mcp", "tool-selection", "t0-t4", "transitional"]
dependencies: ["router_T3_detailed"]
related_docs: ["router_T0_executive", "router_T1_overview", "router_T2_architecture", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Router – T4 Complete Reference (≈15,000 words)

## Purpose

This document provides a complete reference for Router (APOE-MCP Router), covering all aspects including architecture, implementation, API reference, configuration, troubleshooting, edge cases, performance tuning, security, and advanced topics. This is the definitive reference for Router system.

## Document Structure

- **T0 Executive Summary:** 100-word overview
- **T1 Overview:** 500-word overview
- **T2 Architecture:** 2,000-word architecture
- **T3 Detailed Implementation:** 10,000-word implementation guide
- **T4 Complete Reference:** 15,000+ word complete reference (this document)

---

## Complete API Reference

### Router Class

**File:** `packages/router/core/router.py`

**Methods:**

```python
class Router:
    async def decide(self, ctx: RouterContext) -> ToolCallPlan
    async def _compile_plan(self, ranked, snapshot, ctx) -> ToolCallPlan
    async def _handle_validation_failure(self, plan, validation) -> ToolCallPlan
    async def update_success_rate(self, tool_name: str, success: bool)
    async def learn_from_outcome(self, plan: ToolCallPlan, result: Dict[str, Any])
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### ScoutLLM Class

**File:** `packages/router/core/scout.py`

**Methods:**

```python
class ScoutLLM:
    async def propose(self, snapshot: Snapshot, manifest: ToolManifest) -> List[ToolProposal]
    def _get_pattern_key(self, snapshot: Snapshot) -> str
    def _get_cached_pattern(self, pattern_key: str) -> Optional[List[ToolProposal]]
    def _cache_pattern(self, pattern_key: str, proposals: List[ToolProposal])
    def _build_optimized_prompt(self, snapshot: Snapshot, manifest: ToolManifest) -> str
    async def _call_llm(self, prompt: str) -> str
    def _parse_proposals(self, response: str, snapshot: Snapshot) -> List[ToolProposal]
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### BanditScorer Class

**File:** `packages/router/core/bandit.py`

**Methods:**

```python
class BanditScorer:
    async def score(self, proposals: List[ToolProposal], snapshot: Snapshot, manifest: ToolManifest) -> List[RankedTool]
    async def _score_single_proposal(self, proposal, snapshot, manifest) -> Optional[RankedTool]
    async def _compute_context_fit(self, proposal, snapshot) -> float
    async def _compute_success_rate(self, tool_name: str) -> float
    async def _compute_precondition_satisfaction(self, proposal, tool) -> float
    async def _compute_expected_info_gain(self, proposal, snapshot) -> float
    def _compute_parallelizability(self, tool) -> float
    def _compute_risk_penalty(self, tool, snapshot) -> float
    async def learn_from_outcome(self, proposal: ToolProposal, outcome: Dict[str, Any])
    async def update_success_rate(self, tool_name: str, success: bool)
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### RulesEngine Class

**File:** `packages/router/core/rules.py`

**Methods:**

```python
class RulesEngine:
    def validate(self, plan: ToolCallPlan) -> ValidationResult
    def _check_vif_gates(self, plan: ToolCallPlan) -> VIFGate
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### ToolManifest Class

**File:** `packages/router/core/manifest.py`

**Methods:**

```python
class ToolManifest:
    def register(self, tool: Tool)
    def get_tool(self, name: str) -> Optional[Tool]
    def list_tools(self) -> List[Tool]
    def find_tools_by_capability(self, capability: str) -> List[Tool]
    def find_tools_by_tag(self, tag: str) -> List[Tool]
    def initialize_aimos_tools(self)
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### SnapshotBuilder Class

**File:** `packages/router/core/snapshot.py`

**Methods:**

```python
class SnapshotBuilder:
    async def build(self, ctx: RouterContext) -> Snapshot
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### RouterCache Class

**File:** `packages/router/core/cache.py`

**Methods:**

```python
class RouterCache:
    def get_cached_proposals(self, snapshot: Snapshot) -> Optional[List[ToolProposal]]
    def cache_proposals(self, snapshot: Snapshot, proposals: List[ToolProposal])
    def get_cached_embedding(self, text: str) -> Optional[List[float]]
    def cache_embedding(self, text: str, embedding: List[float])
    def get_stats(self) -> Dict[str, Any]
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

---

## Complete Type Reference

### RouterContext

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

**Complete field descriptions, types, constraints, examples.**

### Snapshot

```python
@dataclass
class Snapshot:
    cmc_decisions: List[Dict[str, Any]]
    hhni_context: List[Dict[str, Any]]
    vif_status: Dict[str, Any]
    seg_evidence: List[Dict[str, Any]]
    tcs_cursor: Dict[str, Any]
    goal: str
    summary: str
    timestamp: datetime
```

**Complete field descriptions, types, constraints, examples.**

### ToolCallPlan

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

**Complete field descriptions, types, constraints, examples.**

**All types documented with complete reference.**

---

## Configuration Reference

### Complete Configuration Options

```python
router_config = {
    "cache": {
        "ttl_seconds": 300,
        "max_size": 1000,
        "eviction_policy": "lru"
    },
    "scout": {
        "api_key": "string",
        "model": "cerebras/small:latest",
        "timeout_ms": 700,
        "max_tokens": 384,
        "pattern_cache_ttl": 600,
        "pattern_cache_size": 100
    },
    "bandit": {
        "learning_rate": 0.01,
        "weights": {
            "context_fit": 0.3,
            "success_rate": 0.25,
            "precondition": 0.2,
            "info_gain": 0.15,
            "parallelizability": 0.1
        },
        "penalty_weights": {
            "cost": 0.1,
            "latency": 0.05,
            "risk": 0.15
        },
        "parallel_workers": 4
    },
    "rules": {
        "max_depth": 3,
        "max_steps": 20,
        "max_parallel": 3,
        "budget_limits": {
            "tokens": 100000,
            "cost": 10.0,
            "time_ms": 30000
        },
        "vif_threshold": 0.70
    }
}
```

**All configuration options documented with descriptions, defaults, constraints, examples.**

---

## Troubleshooting Guide

### Common Issues

**Issue:** Router decisions are slow
- **Symptoms:** Decision time >200ms
- **Causes:** Cache miss, slow Scout, slow Bandit
- **Solutions:** Enable caching, optimize Scout prompt, parallel scoring
- **Prevention:** Monitor cache hit rate, optimize patterns

**Issue:** Tool proposals are inaccurate
- **Symptoms:** Wrong tools selected
- **Causes:** Poor Scout prompt, incorrect weights, stale cache
- **Solutions:** Improve prompt, adjust weights, clear cache
- **Prevention:** Monitor selection accuracy, update weights

**Issue:** Cache corruption
- **Symptoms:** Stale proposals, incorrect selections
- **Causes:** TTL expiration, cache corruption, eviction issues
- **Solutions:** Clear cache, check TTL, validate consistency
- **Prevention:** Monitor cache health, validate entries

**Complete troubleshooting guide with all issues, symptoms, causes, solutions, prevention.**

---

## Edge Cases

### Edge Case 1: Empty Context

**Scenario:** Router receives empty context (no files, no errors)

**Behavior:**
- Snapshot built with minimal context
- Scout proposes generic tools
- Bandit ranks by success rate
- Plan generated with safe defaults

**Handling:** Documented with examples.

### Edge Case 2: All Tools Fail Preconditions

**Scenario:** All proposed tools fail precondition checks

**Behavior:**
- Validation fails
- Minimal plan returned
- Escalation triggered
- Human intervention requested

**Handling:** Documented with examples.

**All edge cases documented with scenarios, behavior, handling, examples.**

---

## Performance Tuning

### Cache Optimization

**Strategies:**
- Increase TTL for stable contexts
- Increase cache size for better hit rates
- Optimize cache key generation
- Monitor cache hit rates

**Metrics:**
- Cache hit rate: Target >80%
- Cache size: Monitor memory usage
- TTL: Balance freshness vs hit rate

**Complete performance tuning guide with strategies, metrics, examples.**

---

## Security Reference

### Security Considerations

**VIF Gates:**
- High-risk tools require VIF validation
- Confidence threshold: 0.70
- Gate enforcement: Hard gates

**Budget Enforcement:**
- Hard limits prevent violations
- Real-time tracking
- Circuit breakers

**Audit Logging:**
- All decisions logged
- Evidence chains maintained
- Timeline entries created

**Complete security reference with all considerations, mitigations, examples.**

---

## Advanced Topics

### Custom Tool Registration

**Complete guide for registering custom tools with examples.**

### Weight Tuning

**Complete guide for tuning Bandit weights with examples.**

### Cache Management

**Complete guide for managing cache with examples.**

**All advanced topics documented with complete guides and examples.**

---

## Reference Links

- **T0 Executive Summary:** `T0_executive.md`
- **T1 Overview:** `T1_overview.md`
- **T2 Architecture:** `T2_architecture.md`
- **T3 Detailed Implementation:** `T3_detailed.md`
- **System Map:** `system.map.lucid.json5`
- **System Index:** `system.index.lucid.json5`
- **Usage Envelope:** `usage.envelope.md`

---

**This is the complete reference for Router. See T0-T3 for progressive detail levels.**

