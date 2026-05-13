---
id: "icip_code_property_graph_T2_architecture"
system: "icip_code_property_graph"
component: null
level: "T2"
type: "architecture"
title: "ICIP Code Property Graph Architecture"
description: "2,000-word architecture document for ICIP Code Property Graph"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T19:30:00Z"
author: "aether"
status: "complete"
tags: ["icip", "cpg", "graph", "codebase", "t0-t6", "transitional"]
dependencies: ["icip_code_property_graph_T1_overview"]
related_docs: ["icip_code_property_graph_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# ICIP Code Property Graph – T2 Architecture (≈2000 words)

## System Architecture Overview

The ICIP Code Property Graph implements unified graph representation for codebase intelligence, seamlessly integrated with AIM-OS consciousness systems. The architecture follows a graph-native, query-driven pattern with clear separation of concerns, enabling scalability, maintainability, and comprehensive codebase understanding.

**Architectural Principles:**
- **Unified Data Model:** Single source of truth unifying AST, CFG, and DFG
- **Graph-Native Design:** Neo4j database optimized for graph operations
- **Query-Driven Analysis:** Cypher queries for comprehensive codebase analysis
- **Consciousness Integration:** Designed for AIM-OS consciousness layer

## Component Architecture

### 1. Graph Construction Service

**Purpose:** Building CPG from parsed code.

**Architecture:**
```
GraphConstructionService
├── ASTExtractor (Abstract Syntax Tree extraction)
├── CFGConstructor (Control Flow Graph construction)
├── DFGAnalyzer (Data Flow Graph analysis)
└── GraphUnifier (Unified graph creation)
```

**Key Interfaces:**
- `construct_cpg(parse_results, agent_name) -> CPG`
- `extract_ast(code) -> AST`
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
- AST Extraction: <50ms per file
- CFG Construction: <30ms per file
- DFG Analysis: <40ms per file

### 2. Graph Storage Service

**Purpose:** Neo4j database persistence for CPG.

**Architecture:**
```
GraphStorageService
├── Neo4jDatabase (Graph database)
├── IndexManager (Index optimization)
├── QueryOptimizer (Query performance)
└── BackupManager (Data backup)
```

**Key Interfaces:**
- `store_cpg(cpg, agent_name) -> CPGId`
- `query_cpg(query, agent_name) -> QueryResults`
- `update_cpg(cpg_id, updates) -> UpdatedCPG`
- `delete_cpg(cpg_id) -> void`

**AIM-OS Integration:**
- CPG storage becomes CMC atoms
- Storage operations tracked with VIF provenance
- Storage patterns synthesized into SEG knowledge
- Storage optimized for HHNI retrieval

**Performance Characteristics:**
- CPG Storage: <200ms
- CPG Querying: <500ms
- CPG Updates: <150ms
- CPG Deletion: <100ms

## Integration Architecture

### AIM-OS System Integration

**CMC Integration:** CPG nodes become CMC atoms with bitemporal tracking  
**HHNI Integration:** CPG structure enables physics-based retrieval  
**VIF Integration:** All CPG operations tracked with confidence scores  
**SEG Integration:** CPG patterns synthesized into knowledge graphs  
**ICIP Platform Integration:** Foundation for all ICIP Platform intelligence

## Performance Architecture

**Latency Targets:**
- CPG Construction: <100ms per file
- CPG Storage: <200ms
- CPG Querying: <500ms
- CPG Updates: <150ms

**Throughput Targets:**
- CPG Construction: 500 files/second
- CPG Storage: 200 operations/second
- CPG Querying: 100 queries/second

**Resource Usage:**
- CPU Usage: <40%
- Memory Usage: <4GB
- Storage Usage: <50GB (per CPG)

## Security Architecture

**Security Boundaries:**
- Tier 0: Supporting components (indexing, backup)
- Tier 1: Processing components (construction, querying)
- Tier 2: Core component (graph storage)

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
  "parse_results": parse_results,
  "agent_name": "aether_session_001"  # REQUIRED
})

# INCORRECT: Missing agent identity
cpg = await construct_cpg({
  "parse_results": parse_results  # ERROR: agent_name missing
})
```

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/icip_code_property_graph/system.map.lucid.json5` (if exists)
- ICIP Platform: `systems/icip_platform/T2_architecture.md`
- CMC: `systems/cmc/T2_architecture.md`
- HHNI: `systems/hhni/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/icip_code_property_graph/L0_executive.md`

