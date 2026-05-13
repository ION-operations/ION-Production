---
id: "icip_graph_construction_service_T2_architecture"
system: "icip_graph_construction_service"
component: null
level: "T2"
type: "architecture"
title: "ICIP Graph Construction Service Architecture"
description: "2,000-word architecture document for ICIP Graph Construction Service"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T19:41:00Z"
author: "aether"
status: "complete"
tags: ["icip", "cpg", "graph", "construction", "t0-t6", "transitional"]
dependencies: ["icip_graph_construction_service_T1_overview"]
related_docs: ["icip_graph_construction_service_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# ICIP Graph Construction Service – T2 Architecture (≈2000 words)

## System Architecture Overview

The ICIP Graph Construction Service implements CPG building and maintenance in Neo4j, seamlessly integrated with AIM-OS consciousness systems. The architecture follows a graph-native, analysis-driven pattern with clear separation of concerns, enabling scalability, maintainability, and comprehensive CPG construction.

**Architectural Principles:**
- **Unified Graph Representation:** Single source of truth combining AST, CFG, and DFG
- **Incremental Processing:** Efficient change-based CPG updates
- **Real-Time Processing:** Event-driven graph construction
- **Consciousness Integration:** Designed for AIM-OS consciousness layer

## Component Architecture

### 1. CPG Builder

**Purpose:** Constructs unified graph from ASTs.

**Architecture:**
```
CPGBuilder
├── ASTIntegrator (AST integration)
├── CFGConstructor (CFG construction)
├── DFGAnalyzer (DFG analysis)
└── GraphUnifier (Graph unification)
```

**Key Interfaces:**
- `construct_cpg(asts, agent_name) -> CPG`
- `integrate_ast(ast) -> ASTNodes`
- `construct_cfg(ast) -> CFG`
- `analyze_dfg(ast, cfg) -> DFG`
- `unify_graph(ast, cfg, dfg) -> CPG`

**AIM-OS Integration:**
- CPG nodes become CMC atoms with bitemporal tracking
- CPG construction tracked with VIF provenance
- CPG patterns synthesized into SEG knowledge
- CPG structure enables HHNI physics-based retrieval

**Performance Characteristics:**
- CPG Construction: <100ms per file
- AST Integration: <30ms per file
- CFG Construction: <40ms per file
- DFG Analysis: <50ms per file

### 2. Control Flow Analyzer

**Purpose:** Computes execution order (CFG).

**Architecture:**
```
ControlFlowAnalyzer
├── PathMapper (Execution path mapping)
├── DecisionPointAnalyzer (Decision point analysis)
└── LoopDetector (Loop detection)
```

**Key Interfaces:**
- `construct_cfg(ast) -> CFG`
- `map_paths(cfg) -> ExecutionPaths`
- `analyze_decisions(cfg) -> DecisionPoints`
- `detect_loops(cfg) -> Loops`

**AIM-OS Integration:**
- CFG nodes become CMC atoms
- CFG analysis tracked with VIF provenance
- CFG patterns synthesized into SEG knowledge

**Performance Characteristics:**
- CFG Construction: <40ms per file
- Path Mapping: <20ms per file
- Decision Analysis: <15ms per file

## Integration Architecture

### AIM-OS System Integration

**CMC Integration:** CPG nodes become CMC atoms with bitemporal tracking  
**HHNI Integration:** CPG structure enables physics-based retrieval  
**VIF Integration:** CPG construction tracked with confidence scores  
**SEG Integration:** CPG patterns synthesized into knowledge graphs  
**ICIP Platform Integration:** Foundation for all graph-based analysis

## Performance Architecture

**Latency Targets:**
- CPG Construction: <100ms per file
- AST Integration: <30ms per file
- CFG Construction: <40ms per file
- DFG Analysis: <50ms per file

**Throughput Targets:**
- CPG Construction: 500 files/second
- AST Integration: 1,000 files/second
- CFG Construction: 800 files/second

**Resource Usage:**
- CPU Usage: <45%
- Memory Usage: <4GB
- Storage Usage: <30GB (CPG cache)

## Security Architecture

**Security Boundaries:**
- Tier 0: Supporting components (caching, indexing)
- Tier 1: Processing components (CFG, DFG analysis)
- Tier 2: Core component (CPG builder)

**Security Requirements:**
- All operations require agent identity
- CPG data requires agent attribution
- Graph operations require authorization
- Comprehensive audit logging

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent identity:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Optional Parameter:** `agent_session_id` - Session tracking identifier
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All CPG data stored with agent tags

**Example:**
```python
# CORRECT: Agent identity included
cpg = await construct_cpg({
  "asts": asts,
  "agent_name": "aether_session_001"  # REQUIRED
})

# INCORRECT: Missing agent identity
cpg = await construct_cpg({
  "asts": asts  # ERROR: agent_name missing
})
```

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/icip_graph_construction_service/system.map.lucid.json5` (if exists)
- ICIP Platform: `systems/icip_platform/T2_architecture.md`
- ICIP Code Property Graph: `systems/icip_code_property_graph/T2_architecture.md`
- Parser Service: `systems/icip_parser_service/T2_architecture.md`
- CMC: `systems/cmc/T2_architecture.md`
- HHNI: `systems/hhni/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/icip_graph_construction_service/L0_executive.md`

