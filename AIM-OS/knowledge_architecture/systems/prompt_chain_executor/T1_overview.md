---
id: "prompt_chain_executor_T1_overview"
system: "prompt_chain_executor"
component: null
level: "T1"
type: "overview"
title: "Prompt Chain Executor Overview"
description: "500-word overview of Prompt Chain Executor system"
audience: "developers, architects"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-18T00:00:00Z"
updated: "2025-11-18T00:00:00Z"
author: "aether"
status: "complete"
tags: ["prompt_chain_executor", "prompt_chains", "execution", "orchestration", "t0-t6", "transitional"]
dependencies: ["prompt_chains"]
related_docs: ["prompt_chain_executor_T0_executive", "prompt_chain_executor_T2_architecture", "prompt_chains_T1_overview"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Prompt Chain Executor – T1 Overview (≈500 words)

## Purpose

Prompt Chain Executor is the execution engine for prompt chains, providing runtime execution of multi-step prompt workflows with dependency resolution, state management, and full AIM-OS integration. While the prompt_chains system defines chain structures and compilation, Prompt Chain Executor actually executes those chains step-by-step with error handling, retries, and provenance tracking.

## Key Capabilities

**Chain Execution:**
- Executes prompt chains step-by-step
- Resolves step dependencies automatically
- Manages execution state and intermediate results
- Handles errors and retries gracefully
- Supports both linear and branching chains

**State Management:**
- Maintains execution state across steps
- Stores intermediate results for downstream steps
- Manages variable scoping and context
- Supports state persistence via CMC

**Error Handling:**
- Graceful degradation on errors
- Retry logic with exponential backoff
- Fallback strategies for failed steps
- Detailed error reporting and recovery

**AIM-OS Integration:**
- CMC: Stores chain execution state and history
- VIF: Creates witnesses for each step
- HHNI: Retrieves context for chain steps
- SEG: Synthesizes knowledge from chain execution
- CAS: Monitors chain execution quality
- TCS: Tracks chain execution timeline

## Architecture

Prompt Chain Executor consists of three main components:

**1. Execution Engine:**
- Parses compiled chain definitions
- Manages execution state
- Handles step dependencies
- Coordinates step execution

**2. State Manager:**
- Maintains execution state
- Manages variable scoping
- Handles state persistence
- Provides state access to steps

**3. Integration Layer:**
- Connects to AIM-OS systems
- Manages CMC storage
- Creates VIF witnesses
- Retrieves HHNI context

## Usage Patterns

**Command-Line Execution:**
```bash
prompt-chain-executor execute chain.json
prompt-chain-executor batch chains/ --parallel 4
prompt-chain-executor validate chain.json
```

**Programmatic Execution:**
```python
from prompt_chain_executor import ChainExecutor
from prompt_chains import ChainParser

parser = ChainParser()
chain = parser.parse(chain_definition)

executor = ChainExecutor()
executor.register_step_handler("llm", llm_handler)
executor.register_step_handler("retrieve", hhni_handler)

result = executor.execute(chain)
print(f"Success: {result.success}")
print(f"Steps completed: {result.completed_steps}")
```

## Integration with Prompt Chains

Prompt Chain Executor is the execution layer for prompt_chains:
- **prompt_chains** compiles chain definitions → ChainDefinition
- **prompt_chain_executor** executes ChainDefinition → Results

This separation allows:
- Chain definition independent of execution
- Multiple execution strategies (single, batch, parallel)
- Execution testing without full prompt_chains setup
- Reusable execution engine for different chain sources

## Quality Assurance

**Provenance Tracking:**
- Every step creates VIF witness
- Complete execution trail in CMC
- Deterministic replay capability
- Full audit trail

**Error Handling:**
- Graceful degradation on errors
- Retry logic with exponential backoff
- Detailed error reporting
- Recovery strategies

**Performance Monitoring:**
- Execution time tracking
- Step performance monitoring
- Chain execution statistics
- Quality gate statistics

## Status

**Current:** Implementation in progress
**Target:** Production-ready execution engine
**Integration:** Full AIM-OS integration planned

This T-level overview follows the latest standards without modifying legacy L-level docs. After review, it will become canonical. See prompt_chains system docs for chain definition details; use validation gate before cutover.

