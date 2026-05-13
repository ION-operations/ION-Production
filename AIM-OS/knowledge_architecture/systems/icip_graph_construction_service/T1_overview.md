---
id: "icip_graph_construction_service_T1_overview"
system: "icip_graph_construction_service"
component: null
level: "T1"
type: "overview"
title: "ICIP Graph Construction Service Overview"
description: "500-word overview of ICIP Graph Construction Service"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T19:41:00Z"
author: "aether"
status: "complete"
tags: ["icip", "cpg", "graph", "construction", "t0-t6", "transitional"]
dependencies: ["icip_graph_construction_service_T0_executive"]
related_docs: ["icip_graph_construction_service_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# ICIP Graph Construction Service – T1 Overview (≈500 words)

## Purpose & Scope

ICIP Graph Construction Service builds and maintains the master Code Property Graph (CPG) in Neo4j, transforming language-specific ASTs into unified graph representation combining AST, CFG, and DFG. It performs control flow analysis, data flow analysis, call graph construction, and dependency analysis.

**Core Value Proposition:** Unified graph representation enabling comprehensive codebase intelligence through advanced analysis capabilities, achieving real-time processing with incremental updates and seamless AIM-OS integration.

## Users & Integrations

**Developers:** Real-time CPG construction for code analysis  
**ICIP Platform:** Foundation for all graph-based analysis  
**Parser Service:** Consumes ASTs for CPG building  
**CMC (Memory):** CPG nodes become CMC atoms with bitemporal tracking  
**HHNI (Indexing):** CPG structure enables physics-based retrieval  
**VIF (Verification):** CPG construction tracked with confidence scores  
**SEG (Knowledge):** CPG patterns synthesized into knowledge graphs

## Core Concepts

**Code Property Graph (CPG):** Unified graph representation combining AST (Abstract Syntax Tree), CFG (Control Flow Graph), and DFG (Data Flow Graph) into single queryable graph for comprehensive codebase intelligence.

**Control Flow Analysis:** Maps execution paths and decision points, enabling understanding of program flow and execution order through CFG construction.

**Data Flow Analysis:** Tracks variable usage and data dependencies, enabling understanding of data movement and transformations through DFG construction.

**Incremental Updates:** Only rebuilds changed portions, enabling efficient processing of large codebases with minimal overhead.

## Key Components

**CPG Builder:** Constructs unified graph from ASTs  
**Control Flow Analyzer:** Computes execution order (CFG)  
**Data Flow Analyzer:** Tracks data movement (DFG)  
**Graph Persister:** Stores CPG in Neo4j database

## High-Level Data Flow

**CPG Construction Flow:**
```
ASTs → CPG Builder → Control Flow Analysis → Data Flow Analysis → Unified CPG → Neo4j Storage
```

**AIM-OS Integration Flow:**
```
CPG Nodes → CMC Atoms → HHNI Indexing → VIF Provenance → SEG Synthesis
```

## Non-Goals

ICIP Graph Construction Service is NOT:
- **Replacement for CPG storage:** Graph construction only, storage handled by Neo4j
- **Static analysis tool:** CPG construction foundation, analysis handled downstream
- **IDE replacement:** Graph construction service, IDE integration handled separately
- **Replacement for CMC:** Graph construction service, integrates with CMC

## References

- System map: `systems/icip_graph_construction_service/system.map.lucid.json5` (if exists)
- ICIP Platform: `systems/icip_platform/T2_architecture.md`
- ICIP Code Property Graph: `systems/icip_code_property_graph/T2_architecture.md`
- Parser Service: `systems/icip_parser_service/T2_architecture.md`
- CMC: `systems/cmc/T2_architecture.md`
- L-level docs: `systems/icip_graph_construction_service/L0_executive.md`

