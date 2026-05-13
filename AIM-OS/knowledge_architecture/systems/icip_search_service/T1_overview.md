---
id: "icip_search_service_T1_overview"
system: "icip_search_service"
component: null
level: "T1"
type: "overview"
title: "ICIP Search Service Overview"
description: "500-word overview of ICIP Search Service"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T19:45:00Z"
author: "aether"
status: "complete"
tags: ["icip", "search", "semantic", "code", "t0-t6", "transitional"]
dependencies: ["icip_search_service_T0_executive"]
related_docs: ["icip_search_service_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# ICIP Search Service – T1 Overview (≈500 words)

## Purpose & Scope

ICIP Search Service provides advanced code search capabilities beyond traditional grep-based tools, enabling semantic, context-aware code discovery through hybrid AI architecture. It supports three-tier search maturity: literal search, structural search, and semantic search.

**Core Value Proposition:** Dramatically reduces code discovery time through semantic understanding, achieving 95%+ relevance with sub-second response times through hybrid AI architecture and seamless AIM-OS integration.

## Users & Integrations

**Developers:** Semantic code search for productivity  
**ICIP Platform:** Foundation for code discovery  
**LLM Inference Service:** Powers semantic understanding  
**Graph Construction Service:** Accesses CPG for context  
**CMC (Memory):** Search results become CMC atoms  
**HHNI (Indexing):** Search patterns indexed for retrieval  
**VIF (Verification):** Search accuracy tracked with confidence

## Core Concepts

**Three-Tier Search Maturity:** Literal search (text matching), structural search (AST-based pattern matching), and semantic search (natural language queries), enabling progressive sophistication based on query complexity.

**Semantic Search Architecture:** Query planning via LLM intent analysis, vector retrieval for candidate generation, graph expansion for contextual understanding, and response synthesis for comprehensive answers.

**Hybrid Ranking:** Combines multiple search approaches including literal matching, vector similarity, graph traversal, and semantic understanding, prioritizing most relevant results.

**Context-Aware Results:** Understands code relationships and dependencies, enabling intelligent result prioritization and comprehensive code discovery.

## Key Components

**Query Planner:** Analyzes user intent and decomposes queries  
**Vector Retriever:** Embedding-based candidate generation  
**Graph Expander:** CPG traversal for contextual understanding  
**Response Synthesizer:** LLM-generated comprehensive answers

## High-Level Data Flow

**Search Flow:**
```
Query → Query Planning → Vector Retrieval → Graph Expansion → Response Synthesis → Ranked Results
```

**AIM-OS Integration Flow:**
```
Search Results → CMC Atoms → HHNI Indexing → VIF Provenance → SEG Synthesis
```

## Non-Goals

ICIP Search Service is NOT:
- **Replacement for IDEs:** Search service, IDE integration handled separately
- **Static analysis tool:** Code discovery only, analysis handled downstream
- **Documentation system:** Code search focus, documentation handled separately
- **Replacement for CMC:** Search service, integrates with CMC

## References

- System map: `systems/icip_search_service/system.map.lucid.json5` (if exists)
- ICIP Platform: `systems/icip_platform/T2_architecture.md`
- LLM Inference Service: `systems/icip_llm_inference_service/T2_architecture.md` (if exists)
- Graph Construction Service: `systems/icip_graph_construction_service/T2_architecture.md`
- CMC: `systems/cmc/T2_architecture.md`
- L-level docs: `systems/icip_search_service/L0_executive.md`

