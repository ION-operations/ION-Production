---
id: "context_fidelity_inspector_T1_overview"
system: "context_fidelity_inspector"
component: null
level: "T1"
type: "overview"
title: "Context Fidelity Inspector Overview"
description: "500-word overview of Context Fidelity Inspector"
audience: "developers, quick understanding"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:15:00Z"
author: "aether"
status: "complete"
tags: ["cfi", "fidelity", "inspection", "accountability", "t0-t6", "transitional"]
dependencies: ["context_fidelity_inspector_T0_executive"]
related_docs: ["context_fidelity_inspector_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Context Fidelity Inspector – T1 Overview (≈500 words)

## System Purpose

Context Fidelity Inspector (CFI) provides forensic-grade audit capabilities that capture exactly what context AI models see at decision points, enabling complete traceability of AI reasoning and preventing AI from lying about its own mental state. CFI creates cryptographic witnesses of every AI decision point, ensuring complete transparency.

## Core Capabilities

### Prompt Capture at Boundary
- Logs full textual payload sent to model
- Includes retrieved chunks, hidden system instructions, user input
- Cryptographic hashing for integrity verification
- Immutable, tamper-evident logs

### Output Capture
- Captures raw model output before post-processing
- Includes complete response, confidence scores, reasoning traces
- Hash-linking input→output pairs
- Bitemporal storage with complete provenance

### Reconstruction Queries
- Forces model to self-report its "mental map" at decision points
- Verifies what model actually understood vs. what it claims
- Structured queries about reasoning process
- Cross-reference with captured context

### Saturation Tests
- Stress-tests retention honesty with known datasets
- Learns real retention limits vs. claimed capabilities
- Controlled experiments with known information
- Calibrated retention models

### Branch Routing
- Runs multiple context routes in parallel (safety, perf, UX)
- Compares outcomes across different context slices
- Parallel processing with different context budgets
- Outcome comparison and divergence detection

## Integration Architecture

**AIM-OS System Integration:**
- **CMC:** All CFI witnesses stored as atoms with bitemporal tracking
- **VIF:** CFI data provides confidence calibration and verification
- **SEG:** CFI evidence becomes part of knowledge synthesis
- **APOE:** CFI validates execution plan reasoning
- **SDF-CVF:** CFI ensures quality gates are properly applied

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All CFI witnesses stored with agent tags

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/context_fidelity_inspector/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/context_fidelity_inspector/L0_executive.md`

