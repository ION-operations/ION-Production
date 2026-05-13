---
id: "icip_code_property_graph_T1_overview"
system: "icip_code_property_graph"
component: null
level: "T1"
type: "overview"
title: "ICIP Code Property Graph Overview"
description: "500-word overview of ICIP Code Property Graph"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T19:30:00Z"
author: "aether"
status: "complete"
tags: ["icip", "cpg", "graph", "codebase", "t0-t6", "transitional"]
dependencies: ["icip_code_property_graph_T0_executive"]
related_docs: ["icip_code_property_graph_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# ICIP Code Property Graph – T1 Overview (≈500 words)

## Purpose & Scope

ICIP Code Property Graph provides unified data model for codebase intelligence, unifying AST (Abstract Syntax Tree), CFG (Control Flow Graph), and DFG (Data Flow Graph) into single queryable graph. It enables comprehensive semantic understanding, complex queries, and advanced analysis across 25+ programming languages with 95% semantic coverage.

**Core Value Proposition:** Single source of truth for all codebase intelligence, enabling comprehensive semantic understanding, complex queries, and advanced analysis through unified graph representation.

## Users & Integrations

**Developers:** Semantic code search and impact analysis  
**Architects:** Architectural understanding and dependency analysis  
**Security Analysts:** Vulnerability detection and data flow analysis  
**ICIP Platform:** Foundation for all codebase intelligence  
**CMC (Memory):** CPG nodes become CMC atoms with bitemporal tracking  
**HHNI (Indexing):** CPG structure enables physics-based retrieval  
**VIF (Verification):** All CPG analysis tracked with confidence scores  
**SEG (Knowledge):** CPG patterns synthesized into knowledge graphs

## Core Concepts

**AST (Abstract Syntax Tree):** Code's grammatical structure representation, capturing syntactic relationships and hierarchical code organization.

**CFG (Control Flow Graph):** Execution order mapping, representing program flow, branches, loops, and control dependencies.

**DFG (Data Flow Graph):** Data movement tracking, representing variable assignments, data dependencies, and information flow.

**Unified Graph:** All three representations (AST, CFG, DFG) unified in single Neo4j database, enabling comprehensive codebase queries and analysis.

## Key Components

**Graph Construction:** Building CPG from parsed code  
**Graph Storage:** Neo4j database for CPG persistence  
**Graph Querying:** Cypher queries for codebase analysis  
**Graph Analysis:** Pattern detection and relationship analysis

## High-Level Data Flow

**CPG Construction Flow:**
```
Parsed Code → AST Extraction → CFG Construction → DFG Analysis → Unified CPG → Neo4j Storage
```

**AIM-OS Integration Flow:**
```
CPG Nodes → CMC Atoms → HHNI Indexing → VIF Provenance → SEG Synthesis
```

## Non-Goals

ICIP Code Property Graph is NOT:
- **Replacement for source code:** Complements source code, doesn't replace it
- **Static analysis tool:** Dynamic graph construction and analysis
- **Simple AST:** Comprehensive graph including AST, CFG, and DFG
- **Replacement for CMC:** Technical foundation, integrates with CMC

## References

- System map: `systems/icip_code_property_graph/system.map.lucid.json5` (if exists)
- ICIP Platform: `systems/icip_platform/T2_architecture.md`
- CMC: `systems/cmc/T2_architecture.md`
- HHNI: `systems/hhni/T2_architecture.md`
- L-level docs: `systems/icip_code_property_graph/L0_executive.md`

