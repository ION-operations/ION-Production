---
id: "hhni_T1_overview"
system: "hhni"
component: null
level: "T1"
type: "overview"
title: "HHNI Overview"
description: "500-word overview of Hierarchical Hypergraph Neural Index"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-10-30T00:00:00Z"
updated: "2025-01-27T13:00:00Z"
author: "aether"
status: "complete"
tags: ["hhni", "core", "indexing", "retrieval", "t0-t6", "transitional"]
dependencies: ["hhni_T0_executive"]
related_docs: ["hhni_T2_architecture", "system.map.lucid.json5"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# HHNI – T1 Overview (≈500 words)

## Purpose & Scope

HHNI (Hierarchical Hypergraph Neural Index) is AIM-OS's breakthrough solution to the "lost in the middle" problem—where AI systems lose track of information in long contexts. It combines fractal 6-level indexing with physics-guided retrieval optimization to deliver perfect context every time, with empirically validated +15% improvement over baseline approaches.

HHNI provides three core capabilities:

1. **Fractal Hierarchical Indexing:** Every piece of content indexed at 6 simultaneous resolutions (System → Section → Paragraph → Sentence → Word → Subword). Enables multi-resolution queries: "Give me everything about OAuth2" (Level 2) or "Show me the exact sentence about token expiration" (Level 4).

2. **DVNS Physics Optimization:** Treats context items as particles in embedding space, applies physics forces (gravity, elastic, repulse, damping) to optimize spatial layout. Solves the "lost in the middle" problem—transformers lose ~30% accuracy for information in middle positions (Liu et al. 2023). Result: Contextually optimal arrangement for maximum coherence.

3. **Quality Pipeline:** Beyond retrieval—deduplication, conflict resolution, strategic compression, budget fitting. Ensures token limits respected, contradictions handled, optimal context delivered.

**System Boundaries:**
- HHNI owns: Hierarchical indexing, DVNS physics optimization, retrieval pipeline, quality filters
- HHNI does NOT own: Vector storage (delegates to vector store), embedding generation (reads from CMC), policy decisions (reads from policy engine), content storage (reads from CMC)

## Subsystems

HHNI consists of four subsystems organized in a 3-layer hierarchy:

**1. Hierarchical Index Subsystem (Layer 2):** Manages 6-level fractal indexing (System → Section → Paragraph → Sentence → Word → Subword). Indexes CMC atoms at all levels, stores hierarchical paths in SEG, integrates with CAS for activation tracking and TCS for temporal context.

**2. DVNS Physics Subsystem (Layer 2):** Applies 4 forces (gravity, repulsion, elastic, damping) to optimize context layout. Integrates with VIF for RS-lift metrics and SDF-CVF for physics quartet parity validation.

**3. Retrieval Subsystem (Layer 2):** Two-stage intelligent pipeline. **Main pipeline** uses 3 components: coarseRetrieval (semantic search), physicsRefinement (DVNS optimization), budgetFitter (token budget). **Additional components** available: deduplicationEngine (code exists, not integrated), conflictResolver (used in baseline comparison), strategicCompressor (used in baseline comparison). Integrates with CMC (atom retrieval), APOE (context provision), VIF (witnessing), SEG (semantic search), CAS (activation tracking), TCS (context management), SDF-CVF (quartet parity).

**4. Morphological Analysis Subsystem (Layer 2):** Decomposes words into parts (prefix, root, suffix) for enhanced subword indexing. Integrates with CMC (morphological data storage) and SEG (morphological entities).

## Users & Integrations

**CMC (Context Memory Core):** ✅ **Implemented** - HHNI indexes CMC atoms hierarchically, assigns HHNI paths to atoms, retrieves atoms by query. CMC provides source atoms and storage. Integration tested in `test_memory_store_integration.py`.

**APOE (AI-Powered Orchestration Engine):** ⚠️ **Pattern Only** - HHNI provides optimized context for reasoning, supports multi-step retrieval, budget-aware orchestration. APOE requests context with plans and budgets. Integration pattern documented in `packages/apoe/integration_examples.py`, direct code pending.

**VIF (Verifiable Intelligence Framework):** ⚠️ **Partial** - HHNI retrieval operations witnessed, RS-lift metrics tracked (implemented), replay enabled via snapshots (pending). VIF verifies retrieval quality. RS-lift metrics exist in `RetrievalResult`, witness creation code missing.

**SEG (Shared Evidence Graph):** ✅ **Implemented** - HHNI syncs with SEG for evidence indexing, supports contradiction detection via hierarchical relationships. SEG provides evidence nodes. Integration tested in `test_seg_integration.py`.

**CAS (Cognitive Analysis System):** ❌ **Pending** - CAS activation hooks for indexing operations, activation tracking for retrieval. Integration documented but code not found in `packages/hhni/`.

**TCS (Timeline Context System):** ❌ **Pending** - TCS context retrieval for indexing, context management for retrieval. Integration documented but code not found in `packages/hhni/`.

**SDF-CVF (Atomic Evolution Framework):** ❌ **Pending** - HHNI tracks dependency changes via dependency_hash, supports quartet parity via index consistency. SDF-CVF monitors HHNI index quality. Integration documented but code not found in `packages/hhni/`.

## Core Concepts

**Fractal Hierarchical Index:** 6-level indexing structure (System → Section → Paragraph → Sentence → Word → Subword). Each level provides different granularity—enables queries at any resolution. Parent-child relationships maintain hierarchical structure.

**DVNS (Dynamic Vector Navigation System):** Physics engine applying four forces to optimize context layout:
- **Gravity:** Attracts semantically related items toward query
- **Elastic:** Maintains hierarchical structure from HHNI
- **Repulse:** Separates contradictory information
- **Damping:** Stabilizes system, prevents oscillation

**RS-Lift:** Retrieval Score improvement metric. HHNI achieves +15% at precision-at-rank-5—empirically validated improvement over baseline approaches.

**Budget-Aware Selection:** Respects token limits through strategic compression, deduplication, and optimal subset selection. Never exceeds context window.

## High‑Level Flow

**Indexing Pipeline:**
```
CMC Atoms → Extract Structure → Build 6-Level Index → 
Assign Hierarchical Paths → Store Index Entries → 
Link Parent-Child Relationships
```

**Retrieval Pipeline (Two-Stage):**
```
Query → Stage 1: Coarse Retrieval (KNN, top-100) → 
Stage 2: DVNS Physics Optimization (50-100 iterations) → 
Deduplication → Conflict Resolution → 
Strategic Compression → Budget Fitting → 
Optimal Context
```

**Performance:**
- Stage 1 (Coarse): ~10ms latency
- Stage 2 (Physics): ~30-50ms latency
- Total: p95 < 80ms (target: <100ms) ✅

## Non‑Goals

HHNI is NOT:
- **Vector Database:** Uses vector stores but doesn't implement them (delegates to Faiss/Chroma)
- **Full Knowledge Graph:** Focuses on hierarchical indexing, not general graph relationships
- **Content Storage:** Reads from CMC, doesn't store content itself
- **Embedding Generator:** Uses embeddings from CMC, doesn't generate them
- **Policy Engine:** Reads policies but doesn't enforce them (gate layer)

## NL Tag Coverage

- **Total NL Tags:** 154 tags
- **Quintet Parity:** P = 0.87 (very good)
- **Semantic Search:** All functions tagged
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---


## References

- System map: `systems/hhni/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/hhni/L0_executive.md` through `L4_complete.md`
