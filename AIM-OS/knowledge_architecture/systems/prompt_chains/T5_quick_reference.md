---
id: "prompt_chains_T5_quick_reference"
system: "prompt_chains"
component: null
level: "T5"
type: "quick_reference"
title: "Prompt Chains Quick Reference"
description: "Quick reference guide for Prompt Chains"
audience: "developers, quick lookup"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-05T14:00:00Z"
updated: "2025-11-05T14:00:00Z"
author: "aether"
status: "complete"
tags: ["prompt-chains", "quick-reference", "foundation-chains", "t0-t6"]
dependencies: ["apoe", "cmc", "hhni", "vif"]
related_docs: ["T0_executive.md", "T3_detailed.md", "T4_complete.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Prompt Chains – T5 Quick Reference

## Quick Start

```python
from packages.prompt_chains.executor.chain_executor import ChainExecutor
from packages.prompt_chains.models.prompt_chain import PromptChain
import yaml

# Load chain definition
with open('chains/autonomous_operation.yaml') as f:
    chain_data = yaml.safe_load(f)

chain = PromptChain.from_dict(chain_data)

# Execute chain
executor = ChainExecutor()
result = executor.execute_chain(
    chain=chain,
    context={'session_type': 'autonomous'}
)

# Check result
if result.success:
    print(f"Nodes executed: {len(result.nodes_executed)}")
    print(f"Confidence: {result.confidence:.2f}")
```

---

## Foundation Chains (Tier 1)

**Chain 1: Autonomous Operation** → `chains/autonomous_operation.yaml`
- Orchestrates complete autonomous sessions
- Task generation → Selection → Execution → Loop
- Integrates: CMC, APOE, VIF, SDF-CVF, CAS

**Chain 2: A-H Protocol** → `chains/ah_protocol.yaml`
- Executes A-H development protocol
- Intent → Hypothesis → Context → Expansion → Mesh → Gates → Implementation → Audit

**Chain 3: T0-T6 Documentation** → `chains/t0_t6_documentation.yaml`
- Generates complete T0-T6 hierarchies
- T0 (100w) → T1 (500w) → T2 (2000w) → T3 (10000w) → T4 (15000w) → T5 → README

**Chain 4: Code Implementation** → `chains/code_implementation.yaml`
- Implements code with all protocols
- Documentation → Code+Tags → Tests → Quartet Parity → Commit

---

## Chain Definition Quick Format

```yaml
chain_id: "my-chain"
name: "My Chain"
chain_type: "atomic"  # meta | atomic | composite | adaptive
tier: 1
priority: "high"

start_node_id: "start"
end_node_ids: ["end"]

nodes:
  - node_id: "start"
    operation_type: "system_call"
    system: "CMC"
    operation: "store_atom"
    confidence_threshold: 0.70

edges:
  - edge_id: "e1"
    from_node_id: "start"
    to_node_id: "end"
```

---

## Node Types

| Type | Purpose | Example |
|------|---------|---------|
| **system_call** | Call AIM-OS system | Store in CMC |
| **decision** | Conditional branch | Route by confidence |
| **gate** | Quality enforcement | Quartet parity ≥ 0.90 |
| **branch** | Parallel execution | Execute multiple paths |
| **merge** | Combine results | Aggregate outputs |

---

## System Integration

**CMC:** `system: "CMC"`, `operation: "store_atom"`  
**HHNI:** `system: "HHNI"`, `operation: "semantic_search"`  
**VIF:** `system: "VIF"`, `operation: "check_confidence"`  
**APOE:** `system: "APOE"`, `operation: "compile_plan"`  
**SEG:** `system: "SEG"`, `operation: "synthesize_knowledge"`  
**SDF-CVF:** `system: "SDF-CVF"`, `operation: "check_quartet_parity"`

---

## Edge Conditions

```yaml
# Confidence-based
condition_type: "confidence"
condition_expression: "confidence > 0.70"

# Quality-based
condition_type: "quality"
condition_expression: "quartet_parity >= 0.90"

# Result-based
condition_type: "result"
condition_expression: "status == 'success'"

# Custom
condition_type: "custom"
condition_expression: "context['x'] > 100"
```

---

## Quality Gates

```yaml
quality_gate:
  gate_type: "quartet_parity"
  threshold: 0.90
  parameters:
    check_code: true
    check_docs: true
    check_tests: true
    check_nl_tags: true
```

---

## Common Patterns

### Pattern 1: Simple Linear Chain
```
Start → CMC Store → VIF Check → CMC Retrieve → End
```

### Pattern 2: Confidence-Gated
```
Start → Operation → VIF Gate (≥0.70) → {Proceed | Abstain}
```

### Pattern 3: Quality-Gated
```
Start → Build → Test → Quartet Parity (≥0.90) → {Success | Fix}
```

### Pattern 4: Meta-Chain
```
Start → APOE Plan → Select Sub-Chain → Execute → Aggregate → End
```

---

## Goal-Chain Integration

```python
# Link chain to goal
chain.goal_id = "OBJ-12"

# Execute for goal
result = executor.execute_chain(
    chain=chain,
    context={},
    goal_id="OBJ-12"  # Auto-updates goal progress
)

# Goal automatically updated with:
# - related_chain_ids.append(chain_id)
# - progress incremented
# - completed_via_chain_id (if completes goal)
```

---

## Troubleshooting

**Chain won't execute:** Check start_node_id exists in nodes  
**Infinite loop:** Verify edges have proper stop conditions  
**Low confidence:** Check node.confidence_threshold settings  
**Quality gate fail:** Review quartet parity (code/doc/test/tag alignment)  
**Missing system:** Ensure all AIM-OS systems running

---

**Full Documentation:** [T0](T0_executive.md) | [T1](T1_overview.md) | [T2](T2_architecture.md) | [T3](T3_detailed.md) | [T4](T4_complete.md)

**Status:** Design Complete (Nov 2, 2025) | **Implementation:** Planned  
**Files:** Complete data models, execution engine, 4 Foundation Chains

