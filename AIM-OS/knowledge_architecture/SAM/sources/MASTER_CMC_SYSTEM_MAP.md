# MASTER CMC (Context Memory Core) SYSTEM MAP

**Date:** 2026-02-22  
**System:** Context Memory Core - Bitemporal Memory Substrate  
**Implementation:** packages/cmc_service/

---

**[TAG:SAM] [TAG:MASTER] [TAG:CMC]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:CMC]**

CMC (Context Memory Core) is the foundational memory substrate of AIM-OS. Transforms ephemeral AI context into structured, queryable, reversible memory. Every memory has transaction time and valid time; every atom includes a VIF witness envelope for provenance. Snapshots provide immutable, content-addressed bundles for time-travel queries and rollback.

**[END:TAG:OVERVIEW]**

---

## 2. STATIC STRUCTURE MAP

**[TAG:STRUCTURE] [TAG:CMC]**

### Core Components

| Component | Kind | Responsibility |
|-----------|------|----------------|
| atomManager | core | Manages atoms with bitemporal tracking |
| snapshotEngine | core | Creates immutable content-addressed snapshots |
| storageManager | storage | Multi-tier persistence (vector, object, metadata, graph) |
| writePipeline | pipeline | Parse -> Atomize -> Enrich -> Index -> Gate -> Snapshot |
| readPipeline | pipeline | Query -> HHNI -> DVNS -> Dedupe -> Budget -> Context |
| moleculeComposer | semantic | Groups related atoms into semantic structures |
| bitemporalQueryEngine | query | Time-travel queries with transaction and valid time |

### Subsystems

- **atoms:** Fundamental memory units; integration with HHNI, VIF, SEG
- **pipelines:** Write/Read pipelines; integration with HHNI, VIF, SDF-CVF, APOE, SEG, TCS
- **snapshots:** Immutable atom bundles; integration with VIF, SEG, APOE, SDF-CVF, TCS
- **storage:** Vector, Object, Metadata, Graph stores

### Internal Edges

```
writePipeline -> atomManager (creates_atoms)
atomManager -> snapshotEngine (provides_atoms)
snapshotEngine -> storageManager (stores_snapshots)
readPipeline -> bitemporalQueryEngine (queries_temporal_data)
bitemporalQueryEngine -> storageManager (retrieves_data)
```

**[END:TAG:STRUCTURE]**

---

## 3. DYNAMIC BEHAVIOR MAP

**[TAG:BEHAVIOR] [TAG:CMC]**

### Data Flow (Write)

Input -> Parse -> Create Atoms -> Enrich -> Index via HHNI -> Quality Gate -> Snapshot -> Persist

### Data Flow (Read)

Query -> HHNI Lookup -> DVNS Physics -> Dedup -> Conflict Resolution -> Compression -> Optimal Context

### Lifecycle

1. **Ingestion:** Context parsed, atomized, enriched, indexed
2. **Retrieval:** HHNI lookup, DVNS physics, dedup, budget fit
3. **Snapshot:** Immutable bundles created; never modified after creation

**[END:TAG:BEHAVIOR]**

---

## 4. INTERFACE & INTEGRATION MAP

**[TAG:INTEGRATION] [TAG:CMC]**

### Integration Points

| System | Purpose | Type |
|--------|---------|------|
| HHNI | Atoms indexed for hierarchical retrieval | required |
| VIF | Atoms store witness envelopes for provenance | required |
| SEG | Atoms referenced by graph nodes | required |
| APOE | Execution traces, state persistence | required |
| SDF-CVF | Trace storage, quartet snapshots | required |
| TCS | Timeline nodes stored as atoms | required |
| CAS | Introspection analysis storage | required |

### Ports

hhniIntegration, apoeIntegration, vifIntegration, segIntegration, sdfcvfIntegration, tcsIntegration, casIntegration, externalStorage, vectorStore

**[END:TAG:INTEGRATION]**

---

## 5. CONSTRAINTS & LIMITATIONS

**[TAG:PERFORMANCE] [TAG:DEPENDENCY] [TAG:CMC]**

### Must Never (per component)

- **atomManager:** Allow concurrent writes; delete atoms; modify after creation
- **snapshotEngine:** Modify snapshots; create without deterministic ordering; allow hash collisions
- **writePipeline:** Skip quality gates; create atoms without validation; allow race conditions

### Performance Budgets (ms)

| Component | Budget |
|-----------|--------|
| atomManager | 10 |
| snapshotEngine | 50 |
| storageManager | 100 |
| writePipeline | 200 |
| readPipeline | 150 |
| bitemporalQueryEngine | 100 |

### Governance

single_writer_discipline, bitemporal_integrity, content_addressing, never_delete_policy, audit_trail_required

**[END:TAG:PERFORMANCE] [END:TAG:DEPENDENCY]**

---

## 6. EVIDENCE & VALIDATION

**[TAG:SUMMARY] [TAG:CMC]**

- **Tests:** 65+ passing (packages/cmc_service/)
- **Status:** production
- **Implementation:** SQLite backend, bitemporal query engine, compression (gzip, lz4, brotli, zlib)
- **Documentation:** knowledge_architecture/systems/cmc/ (L0-L4, system.map, system.index)

**[END:TAG:SUMMARY]**

---

## 7. RELATIONSHIP MATRIX

**[TAG:RELATIONSHIP] [TAG:CMC]**

| To System | Relationship |
|-----------|--------------|
| HHNI | CMC provides atoms for indexing |
| VIF | CMC stores witnesses and confidence |
| SEG | CMC provides provenance data |
| APOE | CMC provides context retrieval |
| SDF-CVF | CMC validates schema, quartet parity |
| TCS | CMC stores timeline entries |
| CAS | CMC stores introspection analyses |

**[END:TAG:RELATIONSHIP]**
