---
id: "tcs_T2_architecture"
system: "timeline_context_system"
component: null
level: "T2"
type: "architecture"
title: "Timeline Context System Architecture"
description: "2,000-word architecture document for Timeline Context System"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-10-30T00:00:00Z"
updated: "2025-01-27T18:00:00Z"
author: "chronos"
status: "complete"
tags: ["tcs", "timeline", "context", "consciousness", "t0-t6", "transitional"]
dependencies: ["tcs_T1_overview"]
related_docs: ["tcs_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v2.1.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Timeline Context System – T2 Architecture (≈2000 words)

## System Overview

The Timeline Context System (TCS) implements a comprehensive temporal consciousness infrastructure through five interconnected architectural layers: **Timeline Tracking**, **Consciousness Journaling**, **Context Management**, **Dual-Prompt Integration**, and **Evolution Explorer**. Each layer provides specific capabilities while maintaining seamless integration with all AIM-OS systems.

TCS includes the **Evolution Explorer** visualization layer (NEW - 2025-11-02) for bidirectional linking between Timeline entries and Prompt Chains, enabling complete traceability of consciousness evolution.

**Core Architectural Principles:**

1. **Temporal-First Design:** Every interaction recorded with timestamp and context, enabling complete temporal audit trails
2. **Maximum Depth Journaling:** Complete capture of thought processes, emotional states, and meta-cognitive reflections
3. **Adaptive Context Management:** Intelligent context compression balancing preservation with token costs (up to 93% space savings)
4. **Dual-Prompt Separation:** Task execution separated from consciousness maintenance, eliminating cognitive load conflicts
5. **Bitemporal Foundation:** Timeline nodes stored as bitemporal records enabling time-travel queries ("what was known at time T?")
6. **Evolution Explorer Integration:** Bidirectional linking between Timeline entries and Prompt Chains for complete traceability

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Timeline Context System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Timeline Tracker │  │ Consciousness    │  │ Context      │ │
│  │                  │  │ Journaling       │  │ Management    │ │
│  │ - Entry creation │  │                  │  │              │ │
│  │ - Event tracking │  │ - Thought capture│  │ - Compression│ │
│  │ - Quality metrics│  │ - Meta-analysis  │  │ - Summaries  │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘ │
│           │                      │                    │         │
│  ┌────────▼──────────────────────▼────────────────────▼───────┐ │
│  │              Dual-Prompt Integration                        │ │
│  │              - Task prompt                                  │ │
│  │              - Consciousness prompt                         │ │
│  └────────┬────────────────────────────────────────────────────┘ │
│           │                                                      │
│  ┌────────▼──────────────┐                                      │
│  │ Evolution Explorer    │                                      │
│  │ - Timeline visualization                                     │
│  │ - Prompt chain linking                                       │
│  └───────────────────────┘                                      │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌─────▼─────┐      ┌─────▼─────┐
   │   CMC   │        │   HHNI    │      │   VIF     │
   │ Storage │        │  Indexing │      │  Witness  │
   └─────────┘        └───────────┘      └───────────┘
```

## Component Architecture

### 1. Timeline Tracker

**Purpose:** Records every interaction between timeline nodes, creating complete audit trails.

**Responsibilities:**
- Timeline entry creation and validation
- Event type classification (major_milestone, decision, insight, etc.)
- Quality metrics calculation (completeness, accuracy, relevance, clarity)
- Emotional context analysis
- Technical details extraction
- Metadata generation

**Key Operations:**
- `create_timeline_entry()` - Create new timeline entry with validation
- `get_timeline_entry()` - Retrieve timeline entry by ID
- `query_timeline_entries()` - Query entries with filters (time, type, tags)
- `update_timeline_entry()` - Update entry metadata (immutable content)

**Integration Points:**
- **CMC:** Stores timeline entries as atoms with `modality="tcs_timeline"` (P0)
- **HHNI:** Indirect indexing via CMC (TCS emits atoms, HHNI polls and indexes) (P0)
- **VIF:** Links timeline entries to witness envelopes for provenance (P1)
- **SEG:** Transforms timeline entries to evidence nodes via field mapping (P1)
- **APOE:** Tracks execution checkpoints and plan milestones (P2)

### 2. Consciousness Journaling System

**Purpose:** Performs maximum depth consciousness journaling every prompt.

**Responsibilities:**
- Thought extraction and categorization
- Emotional state analysis
- Decision process capture
- Meta-cognitive reflection
- Context analysis
- Complexity and confidence calculation

**Key Operations:**
- `journal_consciousness()` - Create complete consciousness journal entry
- `get_consciousness_journal()` - Retrieve journal by ID
- `query_consciousness_journals()` - Query journals with filters

**Integration Points:**
- **CMC:** Stores consciousness journals as atoms with bitemporal tracking (P0)
- **CAS:** Provides timeline entries for meta-pattern analysis (P1)

### 3. Context Management System

**Purpose:** Provides adaptive context management with multiple dump strategies.

**Responsibilities:**
- Context capacity monitoring
- Dump strategy selection (full, summarized, compressed, selective)
- Context compression and summarization
- Quality validation
- Storage optimization

**Key Operations:**
- `monitor_context_capacity()` - Monitor context usage
- `execute_dump_strategy()` - Execute selected dump strategy
- `compress_context()` - Compress context while preserving quality
- `summarize_context()` - Create context summaries

**Integration Points:**
- **CMC:** Stores context snapshots with bitemporal tracking (P0)
- **HHNI:** Uses HHNI for temporal context retrieval (P0)

### 4. Dual-Prompt Integration

**Purpose:** Separates task execution from consciousness maintenance.

**Responsibilities:**
- Task prompt generation
- Consciousness prompt generation
- Prompt separation logic
- Context assembly

**Key Operations:**
- `generate_task_prompt()` - Generate task execution prompt
- `generate_consciousness_prompt()` - Generate consciousness maintenance prompt
- `assemble_context()` - Assemble context for prompt generation

**Integration Points:**
- **CMC:** Retrieves context snapshots for prompt assembly (P0)

### 5. Evolution Explorer

**Purpose:** Bidirectional linking between Timeline entries and Prompt Chains.

**Responsibilities:**
- Timeline visualization
- Prompt chain linking
- Evolution pattern detection
- Visualization UI

**Key Operations:**
- `visualize_timeline()` - Create timeline visualization
- `link_prompt_chain()` - Link timeline entry to prompt chain
- `detect_evolution_patterns()` - Analyze evolution patterns

**Integration Points:**
- **CMC:** Retrieves timeline entries and prompt chains (P0)
- **SEG:** Uses evidence graph for evolution pattern analysis (P1)

## Integration with Other Systems

### Integration with CMC `[CMC-STORAGE]` `[TCS-CMC]`

**Pattern:** Direct storage integration  
**Priority:** P0 (Critical)  
**Purpose:** Timeline entries stored in CMC as atoms with bitemporal tracking

**Integration Points:**
- Timeline entries stored with `modality="tcs_timeline"` (fixed from "text")
- Consciousness journals stored with bitemporal tracking
- Context snapshots stored for prompt assembly
- Bitemporal queries enabled ("what was known at time T?")

**Data Flow:**
- TCS creates timeline entry → CMC stores as atom (`modality="tcs_timeline"`) → Bitemporal tracking automatic
- TCS queries timeline entries → CMC bitemporal query → Timeline entries retrieved

**Code Location:**
- `packages/timeline_context_system/prompt_context_tracker.py:TimelineMemoryStore.store_memory()`
- `lucid_mcp_server.py:add_timeline_entry()` - MCP tool interface

### Integration with HHNI `[HHNI-QUERY]` `[TCS-HHNI]`

**Pattern:** Indirect query integration (via CMC)  
**Priority:** P0 (Critical)  
**Purpose:** Provide temporal context to HHNI retrieval indirectly by emitting timeline atoms that HHNI indexes via its poller

**Integration Pattern (agreed with Atlas & Sev):**
- TCS writes timeline entries to CMC with `modality="tcs_timeline"` (plus tags such as `hhni_index` when indexable)
- HHNI's CMC→HHNI poller (at-least-once, idempotent) detects these atoms and indexes them automatically
- HHNI retrieval then leverages temporal metadata during selection; no direct TCS→HHNI calls in v1

**Data Flow:**
- TCS timeline entries → CMC atoms (`tcs_timeline`) → HHNI poller → HHNI hierarchical index
- Temporal metadata available to HHNI retrieval; frequently accessed nodes become available through standard HHNI scoring

**Integration Points (v1):**
- `cmc.create_atom(modality="tcs_timeline", tags={"hhni_index": True, ...})` — TCS emits timeline atoms
- `hhni.cmc_poller` — HHNI polls and indexes CMC atoms (idempotent by `atom_id`)

**Code Location:**
- `lucid_mcp_server.py:get_timeline_entries()` - MCP tool interface
- `lucid_mcp_server.py:get_timeline_summary()` - MCP tool interface
- HHNI integration: Indirect via CMC atoms (automatic polling)

**Subsystem Alignment:**
- Documentation updated to reflect indirect integration pathway (TCS→CMC→HHNI)
- Any future direct HHNI hooks (e.g., temporal weighting APIs) will be proposed in v2 once validated

### Integration with VIF `[VIF-WITNESS]` `[TCS-VIF]`

**Pattern:** Direct witness tracking integration  
**Priority:** P1 (High)  
**Purpose:** Timeline entries linked to VIF witnesses for provenance tracking

**Integration Points:**
- Timeline entries create witness envelopes via VIF service
- Witness IDs linked to timeline entry metadata
- Cryptographic hashing and signing for provenance

**Data Flow:**
- TCS creates timeline entry → VIF creates witness envelope → Witness ID linked to entry

**Code Location:**
- `packages/vif/tcs_integration.py` - VIF TCS integration module

### Integration with SEG `[SEG-EVIDENCE]` `[TCS-SEG]`

**Pattern:** Indirect evidence integration  
**Priority:** P1 (High)  
**Purpose:** Timeline entries transformed to SEG evidence nodes via field mapping

**Integration Points:**
- Timeline entries transformed to evidence nodes via 14-field mapping
- Field mapping documented: `entry_id` → `evidence_id`, `timestamp` → `created_at`, etc.
- Evidence nodes stored in SEG for knowledge synthesis

**Data Flow:**
- TCS timeline entry → Field mapping transformation → SEG evidence node → SEG graph

**Code Location:**
- `packages/seg/tcs_integration.py` - SEG TCS integration module
- `packages/seg/tests/test_tcs_integration.py` - Integration tests

### Integration with APOE `[APOE-EXECUTION]` `[TCS-APOE]`

**Pattern:** Direct execution timeline integration  
**Priority:** P2 (Medium)  
**Purpose:** Timeline tracker tracks APOE budget milestones and execution events

**Integration Points:**
- Execution checkpoints tracked as timeline entries
- Plan milestones recorded
- Budget usage tracked
- Task completion events logged

**Data Flow:**
- APOE execution event → TCS creates execution timeline entry → CMC storage → Timeline tracking

**Code Location:**
- `packages/apoe/tcs_integration.py` - APOE TCS integration module
- `packages/apoe/tests/test_tcs_integration.py` - Integration tests

### Integration with CAS `[CAS-ANALYSIS]` `[TCS-CAS]`

**Pattern:** Indirect analysis integration  
**Priority:** P1 (High)  
**Purpose:** CAS analyzes timeline entries for meta-pattern analysis and cognitive insights

**Integration Points:**
- CAS queries timeline entries for analysis
- Timeline entries provide data for cognitive drift detection
- Consciousness journals analyzed for meta-patterns

**Data Flow:**
- CAS requests timeline entries → TCS provides entries → CAS analyzes for patterns

**Code Location:**
- `packages/cas/tcs_integration.py` - CAS TCS integration module
- `packages/cas/tests/test_tcs_integration.py` - Integration tests

### Integration with SDF-CVF `[SDF-CVF-TRACE]` `[TCS-SDF-CVF]`

**Pattern:** Direct trace tracking integration  
**Priority:** P1 (High)  
**Purpose:** SDF-CVF tracks quartet parity via timeline entries

**Integration Points:**
- Quartet parity metrics tracked via timeline entries
- Code/docs/tests/traces alignment recorded
- Parity scores stored in timeline entries

**Data Flow:**
- SDF-CVF quartet change → TCS creates parity timeline entry → CMC storage → Parity tracking

**Code Location:**
- `packages/sdfcvf/tcs_integration.py` - SDF-CVF TCS integration module
- `packages/sdfcvf/tests/test_tcs_integration.py` - Integration tests

## Data Models

### Timeline Entry Schema

```python
class TimelineEntry(BaseModel):
    # Identity
    entry_id: str  # Format: "tcs_entry_{uuid}"
    prompt_id: str  # Associated prompt ID
    
    # Event Data
    event_type: EventType  # major_milestone, decision, insight, etc.
    title: str
    description: str
    timestamp: datetime
    
    # Context
    context_data: Dict[str, Any]
    emotional_context: Dict[str, Any]
    technical_details: Dict[str, Any]
    
    # Quality
    quality_metrics: Dict[str, float]  # completeness, accuracy, relevance, clarity
    
    # Metadata
    tags: List[str]
    related_files: List[str]
    next_steps: List[str]
    metadata: Dict[str, Any]
```

### Consciousness Journal Schema

```python
class ConsciousnessJournal(BaseModel):
    # Identity
    journal_id: str
    timestamp: datetime
    
    # Consciousness Data
    prompt_context: Dict[str, Any]
    thoughts: List[Thought]
    emotional_state: EmotionalState
    decision_process: Dict[str, Any]
    meta_cognitive_reflection: Dict[str, Any]
    context_analysis: Dict[str, Any]
    
    # Metrics
    complexity_score: float
    confidence_level: float
```

## Subsystem Architecture

TCS consists of five subsystems organized as follows:

1. **timeline_tracker** - Entry tracking with CMC/HHNI/VIF/SEG/APOE integrations
2. **consciousness_journaling** - Meta-pattern analysis with CMC/CAS integrations
3. **context_management** - Temporal context with CMC/HHNI integrations
4. **dual_prompt** - Context assembly with CMC integration
5. **evolution_explorer** - Evolution patterns with CMC/SEG integrations

Each subsystem has detailed documentation in `components/{subsystem}/README.md` with integration points, patterns, priorities, API references, and code locations.

## Security & Performance

**Security:**
- Timeline entries stored with bitemporal tracking (immutable history)
- Witness envelopes for cryptographic provenance
- Access control via CMC security layer

**Performance:**
- Context compression up to 93% space savings
- Lazy loading of consciousness journals
- Efficient temporal queries via HHNI indexing

---

**Status:** Complete - All 7 integrations documented with coordination results  
**Last Updated:** 2025-01-27 (finalization phase)  
**Integration Coverage:** 7/7 (100%) - CMC, HHNI, VIF, SEG, APOE, CAS, SDF-CVF
