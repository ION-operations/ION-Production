---
id: "seg_T1_overview"
system: "seg"
component: null
level: "T1"
type: "overview"
title: "SEG Overview"
description: "500-word overview of Shared Evidence Graph"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-10-30T00:00:00Z"
updated: "2025-11-02T16:00:00Z"
author: "aether"
status: "complete"
tags: ["seg", "core", "knowledge", "synthesis", "t0-t6", "transitional"]
dependencies: ["seg_T0_executive"]
related_docs: ["seg_T2_architecture", "system.map.lucid.json5"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# SEG – T1 Overview (≈500 words)

## Purpose & Scope

**SEG (Shared Evidence Graph)** transforms scattered evidence into a unified, temporal, contradiction-aware knowledge graph. Instead of facts living in isolated documents, SEG treats evidence as a graph where every claim, source, derivation, and agent becomes a node, and every relationship (supports, contradicts, derives, witnesses) becomes an edge.

**Core Guarantees:**
- **Complete Provenance:** Every claim traces to its source (VIF witness, document, user input)
- **Temporal Awareness:** Bitemporal storage (Transaction Time + Valid Time) enables "what was known at time T?" queries
- **Contradiction Detection:** Automatic detection of conflicting claims with semantic similarity and stance analysis
- **Auditable Knowledge:** JSON-LD export, RDF serialization, SHACL validation for external tools

**Primary Use Cases:**
- Synthesize knowledge from multiple sources (VIF witnesses, APOE plans, documents)
- Detect contradictions before they cause problems
- Trace lineage ("where did this claim come from?")
- Query temporal snapshots ("what was true on 2025-02-01?")
- Export evidence graphs for external analysis tools

## Components

**1. Graph Schema**
- **Node Types:** Claim (factual assertion), Source (origin), Derivation (how created), Agent (who created)
- **Edge Types:** supports, contradicts, derives, witnesses, cites
- **Bitemporal Fields:** Transaction time (when recorded), Valid time (when true)

**2. Graph Store**
- Storage backend (NetworkX for development, Neo4j for production)
- Node/edge persistence with bitemporal indexing
- Query engine for lineage, temporal, provenance queries

**3. Contradiction Detector**
- Semantic similarity (embedding-based) for finding similar claims
- Stance detection (positive/negative/neutral) for conflict analysis
- Automatic "contradicts" edge creation and flagging

**4. Query Engine**
- Lineage tracing (backward: find sources, forward: find derivations)
- Temporal queries (what was true at time T?)
- Provenance chains (complete source-to-claim paths)
- Contradiction queries (what conflicts with claim X?)

**5. Export System**
- JSON-LD (W3C standard, RDF-compatible)
- RDF serialization (triple store compatible)
- SHACL validation (shape validation for graph integrity)

## High-Level Data Flows

**Evidence Ingestion Flow:**
1. System/agent adds evidence (claim node + source node)
2. Graph store persists with bitemporal timestamps
3. Contradiction detector analyzes for conflicts
4. Query engine indexes for fast retrieval

**Contradiction Detection Flow:**
1. New claim added to graph
2. Semantic similarity search finds similar claims
3. Stance analysis detects opposite positions
4. "contradicts" edge created automatically
5. Flagged for resolution (human or automated)

**Synthesis Flow:**
1. Query engine finds all claims on topic
2. Contradiction detector identifies conflicts
3. Resolution strategies applied (most recent, source trust, merge)
4. Synthesized claim created with derivation node
5. Complete provenance chain preserved

## Users & Integrations

**Primary Users:**
- **AI Systems:** APOE plans record evidence, VIF witnesses link claims
- **Human Analysts:** Query graph, resolve contradictions, verify provenance
- **External Tools:** Import JSON-LD/RDF exports for analysis

**System Integrations:**
- **CMC:** Stores graph data with bitemporal support (atoms + snapshots)
- **HHNI:** Uses SEG for context retrieval (evidence-based context)
- **VIF:** Links witnesses to claims (provenance tracking)
- **APOE:** Records plan execution as derivations (lineage tracking)
- **SDF-CVF:** Links traces to evidence nodes (quality assurance)

**Integration Points:**
- `seg.add_evidence()` - Add claim + source (from VIF witness, APOE plan, document)
- `seg.find_contradictions()` - Query conflicts (used by CAS for analysis)
- `seg.synthesize()` - Create unified knowledge (used by HHNI for context)
- `seg.export_jsonld()` - Export for external tools (used by audit systems)

## Non-Goals

**Not a Generic Knowledge Base:**
- Requires provenance discipline (every claim must have source)
- Not for unstructured text storage (use CMC for that)
- Not for real-time querying (use HHNI for fast retrieval)

**Not a Conflict Resolution System:**
- Detects contradictions but doesn't automatically resolve them
- Resolution strategies are suggestions, not mandates
- Human judgment required for final resolution

**Not a Replacement for VIF/APOE:**
- SEG tracks evidence relationships, VIF tracks confidence/witnesses
- SEG stores derivations, APOE executes plans
- Complementary systems, not alternatives

## Navigation

- **L0 Executive:** [L0_executive.md](L0_executive.md) - 100-word executive summary
- **L2 Architecture:** [L2_architecture.md](L2_architecture.md) - Detailed architecture and components
- **L3 Detailed:** [L3_detailed.md](L3_detailed.md) - Complete implementation guide

## References

- **System Map:** `knowledge_architecture/systems/seg/system.map.lucid.json5`
- **L-Level Docs:** `knowledge_architecture/systems/seg/L{0-4}_*.md`
- **Gate Validation:** `coordination/epic_standards_overhaul/artifacts/gate_checks/SEG_T0_T6_GATE_RESULTS.md`
- **Templates:** `knowledge_architecture/TEMPLATES_LIBRARY/T1_OVERVIEW_TEMPLATE.md`
