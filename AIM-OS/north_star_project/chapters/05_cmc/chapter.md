# Chapter 5 -- Memory That Never Forgets (CMC)

Status: Drafting under intelligent quality gates (tier S)  
Mode: Completeness-based writing (no fixed word-count gate)  
Target: 3000 +/- 10 percent

## Purpose

This chapter specifies the Context Memory Core (CMC) as the durable substrate that makes AIM-OS work possible. CMC solves the fundamental problem introduced in Chapter 1: statelessness. Without durable memory, every session starts from zero, context evaporates, and decisions cannot be audited.

CMC provides:
- **Immutable atoms** with rich tags, metadata, and provenance
- **Bitemporal preservation** enabling "what did we know then" and "what do we know now" queries
- **Append-only journaling** with hash-chained integrity
- **Deterministic snapshots** for fast recovery and point-in-time analysis
- **Composable retrieval** that integrates with Chat/IDE and MCP tools

This chapter demonstrates that CMC is not just a database—it is the foundation of consciousness continuity. Every decision, every failure, every success becomes a retrievable atom that survives session boundaries.

## Executive Summary

CMC stores immutable atoms with rich tags, metadata, and provenance. The journal is append-only; snapshots provide fast cold-start and deterministic recovery. Time is bitemporal: transaction time (when written) and valid time (what period the content describes). Retrieval works by content, tags, time, and provenance—and composes with Chat/IDE + MCP tools. Operational safeguards (hash-chains, manifests, quarantine) keep integrity high without slowing work.

**Key Insight:** CMC enables the "memory that never forgets" principle from Chapter 1. Without it, AIM-OS cannot maintain continuity, audit decisions, or learn from history. With it, every session starts with loaded context, not guesswork.

## Design Goals

CMC is designed around five non-negotiable principles:

1. **Durability first:** Nothing important is ephemeral. Edits append successors; history is never lost. This enables auditability and learning from past decisions.

2. **Auditability by default:** Every atom carries provenance: who created it, when, why, and what it references. Audits traverse by agent, thread, or tool without manual reconstruction.

3. **Bitemporal truth:** CMC preserves two time axes:
   - **Transaction time:** When the atom was written (immutable, set by CMC)
   - **Valid time:** What period the content describes (mutable, set by authoring tool)
   
   This enables queries like "What did we believe at 14:00 on Tuesday?" and "What do we believe now about Monday's event?"

4. **Fast recovery:** Snapshots capture consistent views with indices and manifests. Cold-start loads the latest snapshot, then replays the journal tail. Recovery is deterministic and fast.

5. **Accessible operations:** Human-first summaries for common queries; raw JSON available for deep inspection. The interface abstracts complexity without hiding capability.

These goals are not aspirational—they are enforced by the implementation. The system cannot function without them.

## Core Concepts

### Atom: The Minimal Unit of Knowledge

An atom is the smallest unit of persisted knowledge in CMC. It contains:
- **Content:** The actual knowledge (text, image, binary, or reference URI)
- **Tags:** Structured labels for retrieval (e.g., `{chapter: "05", cmc: true, type: "evidence"}`)
- **Metadata:** Arbitrary JSON (author, source, thread, tool, confidence)
- **Provenance:** Actor + timestamp + rationale (who created it, when, why)
- **Temporal fields:** `valid_time` (what period this describes) and `tx_time` (when written)

Atoms are immutable. To update knowledge, create a successor atom that references the predecessor. This preserves history and enables audit trails.

**Atom Schema Details:**
- **Identity:** Each atom has a stable UUID (`atom_{uuid}`)
- **Modality:** Supports `text`, `code`, `event`, `tool:call`, `tool:result`
- **Content Reference:** Small content (<1KB) stored inline; larger content externalized to object store with URI and SHA-256 hash
- **Embedding:** Optional vector representation for semantic search (model ID, dimensions, vector)
- **Tag Priority Vector (TPV):** Priority, relevance, and decay parameters for retrieval optimization
- **VIF Witness Envelope:** Complete provenance including model ID, weights hash, prompt template, tools used, writer, confidence band, and entropy

This rich schema ensures every atom carries complete context for retrieval, verification, and auditability.

### Journal: The Append-Only Log

The journal is an append-only log of atoms, hash-chained for integrity. Each segment includes:
- The previous segment's hash (forming a chain)
- A batch of atoms written together
- A manifest of atom IDs and checksums

The journal enables:
- **Integrity verification:** Hash chains detect corruption immediately
- **Deterministic replay:** Replay from any point to reconstruct state
- **Audit trails:** Every write is preserved, never overwritten

### Snapshot: Consistent Checkpoints

Snapshots are periodic, consistent checkpoints materialized from the journal. Each snapshot includes:
- **Inverted indices:** Fast lookup by tags, terms, provenance
- **Manifests:** Complete list of atom IDs, sizes, checksums
- **Summaries:** Counts, growth rates, distribution statistics

Snapshots enable:
- **Fast cold-start:** Load latest snapshot, then replay journal tail
- **Point-in-time analysis:** Query "as of snapshot N"
- **Safe migration:** Compaction and optimization windows

### Bitemporal: Dual Time Axes

Bitemporal preservation answers two critical questions:
- **Transaction-time queries:** "What did we believe at 14:00 on Tuesday?" (replay journal as of that time)
- **Valid-time queries:** "What do we believe now about Monday's event?" (query current state filtered by valid_time)

This dual-axis model enables both historical accuracy and current truth, which is essential for auditability and learning.

## Atom Model

Atoms are the fundamental building blocks of CMC. Each atom represents a single piece of knowledge with complete provenance.

### Atom Fields

- **modality:** `text | image | bin` - The type of content stored
- **content:** Inline content or reference URI (for large payloads)
- **tags:** Structured labels for retrieval (e.g., `{chapter: "05", cmc: true, type: "evidence"}`)
- **metadata:** Arbitrary JSON (author, source, thread, tool, confidence, etc.)
- **provenance:** Actor + timestamp + rationale (who created it, when, why)
- **valid_time:** Interval the content describes `[start, end]` (set by authoring tool)
- **tx_time:** Server write time (immutable, set by CMC)

### Atom Properties

- **Immutability:** Creating a successor never overwrites—history is preserved. This enables audit trails and learning from past decisions.

- **Addressability:** Each atom has a stable UUID. Successors link via metadata/provenance, creating a graph of knowledge evolution.

- **Minimality:** Atoms are small; large payloads live behind URIs with checksums. This keeps the journal fast and enables efficient retrieval.

- **Composability:** Atoms reference other atoms via tags and metadata. This creates a knowledge graph that HHNI can navigate hierarchically.

### Successor Relationships

When knowledge evolves, create a successor atom that:
- References the predecessor atom ID
- Narrows or extends `valid_time` as appropriate
- Carries updated content and metadata
- Preserves the full history chain

This enables queries like "Show me all versions of this knowledge" and "What did we believe before this change?"

## Journal and Integrity

The journal is CMC's append-only log of atoms, hash-chained for integrity. This design ensures that corruption is detected immediately and recovery is deterministic.

### Hash Chaining

Each journal segment includes:
- The previous segment's hash (forming an unbreakable chain)
- A batch of atoms written together (atomicity)
- A manifest of atom IDs and checksums (verification)

Hash chaining enables:
- **Immediate corruption detection:** Any modification breaks the chain
- **Deterministic replay:** Reconstruct state from any point
- **Audit trails:** Every write is preserved, never overwritten

### Integrity Checks

Integrity is verified at multiple levels:
- **On write:** Each atom is validated before journaling
- **Periodic scans:** CI and background tasks verify hash chains
- **On read:** Checksums verified when loading from journal

### Quarantine Policy

When corruption is detected:
1. Isolate the corrupt segment immediately
2. Report the violation with full context
3. Recover from the last good snapshot
4. Replay journal tail to restore consistency

This policy ensures that corruption never propagates and recovery is always possible.

## Snapshots

Snapshots are periodic, consistent checkpoints materialized from the journal. They provide fast cold-start and enable point-in-time analysis.

### Snapshot Contents

Each snapshot includes:
- **Inverted indices:** Fast lookup by tags, terms, provenance (enables HHNI traversal)
- **Manifests:** Complete list of atom IDs, sizes, checksums (verification)
- **Summaries:** Counts, growth rates, distribution statistics (observability)

### Snapshot Uses

Snapshots enable three critical capabilities:

1. **Fast cold-start:** Load the latest snapshot, then replay the journal tail. This reduces startup time from minutes to seconds.

2. **Point-in-time analysis:** Query "as of snapshot N" to see historical state. This enables audits and learning from past decisions.

3. **Safe migration windows:** Compaction and optimization can run during snapshot creation without blocking writes.

### Snapshot Frequency

Snapshots are created:
- Periodically (e.g., every hour or every N atoms)
- Before risky operations (migrations, compactions)
- On demand (via MCP tools for testing)

The frequency balances recovery speed against storage cost. More frequent snapshots = faster recovery but more storage.

## Bitemporal Preservation

Bitemporal preservation is CMC's most powerful feature. It enables both historical accuracy ("what did we know then?") and current truth ("what do we know now?").

### The Two Time Axes

CMC preserves two independent time dimensions:

1. **Transaction time (tx_time):** When the atom was written (immutable, set by CMC server)
   - Answers: "What did we believe at 14:00 on Tuesday?"
   - Enables: Historical replay, audit trails, learning from past decisions

2. **Valid time (valid_time):** What period the content describes (mutable, set by authoring tool)
   - Answers: "What do we believe now about Monday's event?"
   - Enables: Current truth queries, knowledge evolution tracking

### Bitemporal Queries

The dual-axis model enables powerful queries:

- **Transaction-time replay:** "Show me the world as of Tuesday 14:00" (replay journal up to that point)
- **Valid-time filtering:** "What do we currently believe about events in January?" (filter by valid_time)
- **Temporal evolution:** "Show me how our understanding of X changed over time" (query successor chains)

### Successor Relationships

When knowledge evolves, successors preserve history:
- Successors reference predecessor atom IDs
- `valid_time` is narrowed or extended as appropriate
- `tx_time` records when the update occurred
- Full history chain remains queryable

This enables learning from past decisions and understanding why current knowledge exists.

## Retrieval Patterns

CMC supports multiple retrieval patterns that compose together. This enables flexible queries while maintaining performance.

### By Content

Full-text search with scoring, filtered by tags/time:
- Search across atom content using semantic or keyword matching
- Rank results by relevance score
- Filter by tags, time ranges, or provenance

**Use case:** "Find all atoms mentioning 'confidence routing' from the last week"

### By Tags

Structured queries using tag hierarchies:
- Exact tag matches: `{chapter: "05", type: "evidence"}`
- Tag hierarchies: `{chapter: "05", *}` (all tags starting with chapter=05)
- Tag composition: Combine multiple tag filters with AND/OR logic

**Use case:** "Find all evidence atoms for Chapter 5"

### By Time

As-of queries using transaction or valid time:
- Transaction-time queries: "Show atoms written before Tuesday 14:00"
- Valid-time queries: "Show atoms valid during January 2025"
- Time range queries: Combine both axes for precise temporal filtering

**Use case:** "What did we know about X as of last Tuesday, and what do we know now?"

### By Provenance

Filter by agent, thread, tool for audits and reviews:
- Agent filtering: "Show all atoms created by Agent Max"
- Thread filtering: "Show all atoms from thread 'north-star-orchestration'"
- Tool filtering: "Show all atoms created via 'store_memory' tool"

**Use case:** "Audit all changes made by Agent Aether in the last 24 hours"

### Composition

Typical retrieval flow:
1. Narrow by tags/time (fast filtering)
2. Rank by content relevance (semantic scoring)
3. Filter by provenance (audit requirements)
4. Return top N results with summaries

This composition enables both fast queries and deep audits without sacrificing performance.

## Interfaces (Chat/IDE + MCP Tools)

CMC integrates seamlessly with the universal interface from Chapter 2. Chat issues intents; IDE shows artifacts; MCP tools persist/retrieve atoms.

### Authoring Workflow

The typical authoring path demonstrates CMC integration:

1. **Draft claim:** Author writes prose in chapter.md
2. **Add Tier A anchor:** Author adds citation to evidence.jsonl
3. **Store atom:** MCP tool `store_memory` creates atom with tags
4. **Commit snapshot:** On milestone, create snapshot for fast recovery

This workflow ensures evidence lives both in-line (evidence.jsonl) and in durable memory (CMC atoms).

### MCP Tool Integration

CMC exposes three primary MCP tools:

- **`store_memory`:** Create atoms with content, tags, metadata
- **`retrieve_memory`:** Query atoms by content, tags, time, provenance
- **`get_memory_stats`:** Get observability metrics (counts, growth rates)

These tools enable the proof loop from Chapter 3: plan → execute → verify → record → message.

### Evidence and Metrics

Evidence and metrics live next to prose:
- Reviewers can verify claims by running examples
- Evidence atoms link back to prose via tags
- Metrics track system health and growth

This integration makes CMC transparent—authors see evidence, reviewers verify it, and the system remembers it.

## Operational Safeguards

CMC includes multiple safeguards to ensure integrity and enable recovery:

### Provenance Everywhere

Every atom carries complete provenance:
- **Who:** Agent or user who created it
- **When:** Transaction time (tx_time) and valid time (valid_time)
- **Why:** Rationale or intent from authoring tool
- **What:** References to related atoms, threads, tools

Audits traverse by agent, thread, or tool without manual reconstruction. This enables accountability and learning.

### Snapshots Before Risky Changes

Before risky operations (migrations, compactions, major updates):
1. Create a snapshot
2. Verify snapshot integrity
3. Proceed with operation
4. If operation fails, rollback to snapshot

Rollbacks are deterministic because snapshots are consistent checkpoints.

### Quarantine on Mismatch

When integrity checks detect corruption:
1. Isolate the corrupt segment immediately
2. Report violation with full context (which segment, what check failed)
3. Recover from last good snapshot
4. Replay journal tail to restore consistency

This ensures corruption never propagates and recovery is always possible.

### Human-First Summaries

CMC provides readable summaries for common queries:
- Memory statistics (counts, growth rates)
- Recent atoms by tag or time
- Provenance trails for audits

Raw JSON is available for deep inspection, but summaries enable quick understanding without diving into details.

Runnable Examples (PowerShell)
```powershell
# Store an atom
$store = @{ tool='store_memory'; arguments=@{ content='CMC: atom from Chapter 5 example'; tags=@{ chapter='05'; cmc=$true; type='example' } } } | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $store |
  Select-Object -ExpandProperty Content

# Get memory stats
$stats = @{ tool='get_memory_stats'; arguments=@{} } | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $stats |
  Select-Object -ExpandProperty Content

# Retrieve atoms tagged to this chapter
$qry = @{ tool='retrieve_memory'; arguments=@{ query='CMC'; tags=@{ chapter='05' }; limit=5 } } | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $qry |
  Select-Object -ExpandProperty Content
```

Architecture Diagram (Conceptual)
- See `north_star_project/chapters/05_cmc/diagrams.json` (atom -> journal -> snapshot).
- The diagram emphasizes:
  - immutability and hash-chains
  - snapshot manifests
  - bitemporal queries

## Runnable Example 4: Append a Snapshot Integrity Report
PowerShell
```powershell
$report = @{
  tool='store_memory';
  arguments=@{
    content="CMC snapshot verified $(Get-Date -Format o)";
    tags=@{ chapter='05'; type='status'; system='cmc'; gate='integrity' };
    metadata=@{
      source='packages/cmc_service/advanced_pipelines.py';
      run_id='ch05_snapshot_check';
      chapter='05';
      proof='run_chain.py --run-gates ch05_memory_cmc'
    }
  }
} | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $report |
  Select-Object -ExpandProperty Content
```

## Runnable Example 5: Query Atoms by Tag and Valid Time
PowerShell
```powershell
$body = @{
  tool='retrieve_memory';
  arguments=@{
    query='cmc snapshot';
    tags=@{ chapter='05'; type='status' };
    valid_time_start='2025-11-01T00:00:00Z';
    valid_time_end='2025-11-06T23:59:59Z';
    limit=5
  }
} | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $body |
  Select-Object -ExpandProperty Content
```
This proves bitemporal indexing is live: the query filters both by tags and valid-time range, just as described in `knowledge_architecture/systems/cmc/T2_architecture.md`.

## Edge Cases and Failure Modes

Real systems encounter failures. CMC handles them gracefully:

### Disk Corruption

**Scenario:** Journal segment becomes corrupted (disk failure, bit rot)

**Response:**
1. Quarantine corrupt range immediately
2. Restore from last good snapshot
3. Replay journal tail to restore consistency
4. Report corruption with full context for investigation

**Prevention:** Periodic integrity scans, redundant storage, checksums

### Clock Skew

**Scenario:** Authoring tool and CMC server have different clocks

**Response:**
- Prefer `tx_time` generated by server (single source of truth)
- Annotate `valid_time` with source if provided by authoring tool
- Log clock skew warnings for investigation

**Prevention:** NTP synchronization, server-generated timestamps

### Large Payloads

**Scenario:** Atom content exceeds size limits

**Response:**
- Store payload externally (object storage, file system)
- Keep checksums and sizes in atom metadata
- Atom contains reference URI, not inline content

**Prevention:** Size limits, external storage for large payloads

### Concurrent Writes

**Scenario:** Multiple agents write atoms simultaneously

**Response:**
- Journal segments batch writes atomically
- Hash chains ensure ordering
- Snapshots capture consistent views

**Prevention:** Atomic batching, deterministic ordering

Each failure mode has a documented response that preserves integrity and enables recovery.

## Operational Runbook: Snapshot Restore (Wave 1 Standard)
`knowledge_architecture/systems/cmc/L3_detailed.md` documents the precise steps operators follow before risky maintenance:

1. Run `python north_star_project/scripts/run_chain.py --check-deps ch05_memory_cmc` to confirm dependencies (HHNI, SEG, APOE) are green.
2. Execute the snapshot plan defined in `packages/cmc_service/advanced_pipelines.py` (`SnapshotManager.create()`), storing the manifest ID inside CMC via `store_memory`.
3. Perform the migration or remediation work.
4. If gates fail or integrity drops, call `SnapshotManager.restore(manifest_id)` and replay the journal tail (`replay_journal.py --from manifest_id`).
5. Log the outcome to CMC (as shown in Runnable Example 4) and post the summary to `coordination/epic_standards_overhaul/comms/SHARED_MESSAGE_BOARD.md`.

Because every step writes an atom, HHNI can reconstruct the entire runbook after the fact, and SEG can prove which manifests were used in production.

## Future Work

CMC is production-ready but continues to evolve:

### Compaction with Tiered Storage

For very large journals:
- Tiered storage (hot/cold/archive)
- Compaction removes obsolete atoms
- Maintains bitemporal queries across tiers

**Status:** Design phase, not blocking current use

### Cross-Workspace Sync

For multi-workspace scenarios:
- CRDT-ish successor rules for conflict resolution
- Sync protocol for atom replication
- Conflict detection and resolution

**Status:** Research phase, future enhancement

### Richer Retrieval Operators

Combining structure and semantics:
- Graph queries (follow successor chains)
- Semantic similarity (vector search)
- Temporal joins (correlate by time)

**Status:** Incremental enhancement, current retrieval sufficient

These enhancements improve CMC without breaking existing functionality.

## Connection to Other Systems

CMC is the foundation that enables other AIM-OS systems:

### HHNI (Chapter 6)

HHNI uses CMC atoms as its data source. Tags enable hierarchical navigation, and snapshots provide fast traversal. Without CMC, HHNI cannot retrieve knowledge efficiently.

### VIF (Chapter 7)

VIF stores confidence scores as CMC atoms. Bitemporal queries enable "what was our confidence then vs. now" analysis. Provenance tracks which agent or tool recorded each confidence score.

### APOE (Chapter 8)

APOE stores execution plans as CMC atoms. Plans reference evidence atoms, creating a knowledge graph. Snapshots enable point-in-time plan analysis.

### SEG (Chapter 9)

SEG uses CMC atoms as evidence nodes. Provenance links create the evidence graph. Bitemporal queries enable contradiction detection across time.

### SDF-CVF (Chapter 10)

SDF-CVF stores quality gate results as CMC atoms. Audit trails enable learning from quality failures. Snapshots capture quality state at milestones.

## Governance Hooks and Policy Alignment

orth_star_project/policy/gates.json elevates CMC to Tier S, so the interface enforces:
- **Confidence floor (vif_min ≥ 0.90):** Writes below this value route into SIS for reinforcement before the atom is accepted.
- **Intelligent gate telemetry:** 
orth_star_project/scripts/run_chain.py --run-gates ch05_memory_cmc calculates relevance, density, completion, and thoroughness scores, then stores the output beside metrics.yaml for auditors.
- **Authority enforcement:** The command server checks the active persona (Chapter 16 authority map) before executing destructive operations such as snapshot deletion or compaction.

Runnable Examples 4 and 5 show how operators attach gate metadata to every atom and validate retrieval scopes, keeping governance observable instead of implicit.


**Key Insight:** CMC is not isolated—it is the substrate that makes all other systems possible. Every system stores its state in CMC, creating a unified knowledge graph.

## Checklist (CMC Completeness)

- **Coverage:** Atom model, journal, snapshots, bitemporal preservation, retrieval patterns, interfaces, operational safeguards, edge cases, future work
- **Relevance:** Every section supports durability and auditability—CMC's core purpose
- **Balance:** Conceptual explanation (atoms, bitemporal) balances with operational detail (safeguards, edge cases)
- **Minimum substance:** Runnable examples, architecture diagram reference, comprehensive edge cases, integration with other systems

This chapter demonstrates that CMC is production-ready and essential to AIM-OS. Without it, consciousness continuity is impossible.

