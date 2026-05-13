# PLIx System - T1 Overview

**System:** Programmatic-Linguistic Interface (PLIx)  
**Purpose:** Typed intent/contract layer bridging NL intents to executable multi-agent/tool plans  
**Status:** 🚀 **ACTIVE** - Research & Implementation Phase  
**Date:** 2025-11-09

---

## Overview

PLIx is a **typed intent/contract layer** that bridges natural language intents and executable multi-agent/tool plans. It provides human-legible yet machine-strict intent contracts with pre/post conditions, durable recoverable execution graphs, evidence chains, confidence gates, and bitemporal memory integration.

---

## Core Concepts

### Intent Contracts
- **Preconditions:** Must be true before execution
- **Postconditions:** Must be true after execution
- **Capabilities:** Required agent/tool capabilities
- **Policies:** Constraint policies (security, quality, etc.)
- **Invariants:** Must hold throughout execution

### Execution Plans
- **Steps:** Multi-step agent/tool orchestration
- **Dependencies:** Step ordering and prerequisites
- **Retries:** Configurable retry logic with backoff
- **Compensations:** Rollback actions on failure
- **Parallelization:** Steps that can run concurrently

### Evidence System
- **Required Evidence:** Artifacts that must be produced
- **Evidence Types:** Code diffs, tests, docs, decisions, lineage
- **Evidence Chains:** Links between claims and supporting artifacts
- **SEG Integration:** Evidence stored as graph edges

### Confidence Gates
- **Thresholds:** Minimum, warning, critical confidence levels
- **Degradation:** Handling of confidence drops
- **Fallbacks:** Alternative actions on low confidence
- **VIF Integration:** Confidence tracked via witnesses

### Interoperability
- **Temporal:** Compile plans to durable workflows
- **OPA:** Emit policy queries from contracts
- **PROV:** Serialize evidence as provenance
- **PDDL:** Export/import for planning problems

---

## Architecture Layers

1. **Intent Layer** - NL → Typed Contracts
2. **Plan Layer** - Contracts → Execution Graphs
3. **Evidence Layer** - Execution → Evidence Chains
4. **Gate Layer** - Confidence/Policy Enforcement
5. **Interop Layer** - Compilation to External Systems

---

## Integration with AIM-OS

- **CMC:** Store PLIx contracts/plans as atoms
- **HHNI:** Index by intent, contract, plan structure
- **SEG:** Evidence chains as graph edges
- **VIF:** Confidence gates as witnesses
- **APOE:** Plan execution orchestration
- **TCS:** Bitemporal timeline for auditability

---

## Research Status

- ✅ Research protocol defined
- ✅ Comparison matrix populated (initial findings)
- ⏳ PLIx v1 schema design (in progress)
- ⏳ Compiler stub implementation
- ⏳ Interop adapters (Temporal, OPA, PROV)
- ⏳ IDE integration

---

**Next:** Complete PLIx v1 schema and begin compiler stub implementation

