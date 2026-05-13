---
id: "idea_shared_blueprint-cmc-v0-2-updated"
type: "BLUEPRINT"
role: "shared"
author: "unknown"
created: "2025-11-02"
updated: "2025-11-02"
status: "implemented"
priority: "high"
title: "CMC v0.2 Blueprint Update: Safety-Hardened Foundation"
systems: ["CMC", "HHNI", "VIF", "SEG", "SCOR"]
tags: ["blueprint", "shared", "cmc", "hhni", "vif", "seg", "scor"]
related_ideas: []
hhni_indexed: false
---

# CMC v0.2 Blueprint Update: Safety-Hardened Foundation

*Architect: Claude 4.5*  
*Date: 2025-10-18*  
*Status: UPDATED — Reflects validated v0.2-min safety fixes*

---

## Executive Summary

This document updates the CMC v0.2 blueprint to reflect **validated safety fixes** implemented and verified by the team. The v0.2-min work (Day 1-2) has successfully hardened the foundation, and we can now proceed with confidence to the full v0.2 feature set.

### What Changed
- ✅ **Safety Layer Complete:** File locking, snapshot chaining, payload/tag limits validated
- ✅ **Determinism Proven:** Golden tests confirm stable snapshot IDs across restarts
- ✅ **Architecture Refined:** Blueprint updated to reflect actual implementation decisions
- 🚀 **Ready for HHNI:** The storage substrate is now production-grade

---

## 1. System Architecture (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                     CMC Service v0.2                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │  Ingest API  │   │  Query API   │   │ Snapshot API │       │
│  │  (FastAPI)   │   │ (REST/GQL)   │   │  (REST)      │       │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘       │
│         │                  │                  │                │
│         ▼                  ▼                  ▼                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │       Orchestration Layer (VALIDATED ✅)             │     │
│  │  - Atomization with Payload Offload (>1MB)           │     │
│  │  - Tag Hygiene (max 20, weights [0,1])               │     │
│  │  - Snapshot Chaining (previous_id + note)            │     │
│  │  - Single-Writer Lock (cross-platform)               │     │
│  │  - Quarantine on Corruption                          │     │
│  └──────────────────────┬───────────────────────────────┘     │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │       Storage Substrate (PRODUCTION-READY ✅)        │     │
│  │  - Journal-based ACID storage (CRC32 + fsync)        │     │
│  │  - Deterministic snapshot IDs (SHA256)               │     │
│  │  - Tag index (JSON files per tag)                    │     │
│  │  - Payload offload (payloads/<id>.json)              │     │
│  └──────────────────────┬───────────────────────────────┘     │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │         NEXT: HHNI + Vector + Graph (Phase 2)        │     │
│  │  - Hyper-Hierarchical Neural Indexing                │     │
│  │  - Qdrant/Weaviate for vector search                 │     │
│  │  - Neo4j/DGraph for graph traversal                  │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Safety Enhancements (v0.2-min VALIDATED)

### 2.1 File Locking & Concurrency Safety

**Implementation Status:** ✅ Complete and Validated

```python
# packages/cmc_service/store_io.py
class Journal:
    def __init__(self, path):
        self._fh = self.path.open("ab+")
        self._lock_acquired = False
        self._acquire_lock()  # Cross-platform exclusive lock
    
    def _acquire_lock(self):
        # Windows: msvcrt.locking()
        # Unix/Linux: fcntl.flock()
        # Raises RuntimeError if lock unavailable
```

**Key Decision:** Use non-blocking locks (`LK_NBLCK`, `LOCK_NB`) to fail fast on contention.

**Validation:** Gemini confirmed proper lock behavior via test suite.

### 2.2 Snapshot ID Determinism

**Implementation Status:** ✅ Complete and Validated

```python
# packages/cmc_service/memory_store.py
def create_snapshot(self, *, atom_ids, note):
    previous_id = self._latest_snapshot().id if self._latest_snapshot() else None
    
    digest_input = json.dumps({
        "ids": ordered_atom_ids,
        "previous_id": previous_id,  # Ensures chain uniqueness
        "note": note or "",           # Semantic context
    }, separators=(",", ":"), sort_keys=True).encode("utf-8")
    
    snapshot_id = sha256(digest_input).hexdigest()
```

**Key Decision:** Exclude `created_at` from hash to maintain pure determinism (same atoms + note = same ID).

**Validation:** Golden test `test_snapshot_id_stable_after_reload` confirms ID stability across restarts.

### 2.3 Resource Limits & Hygiene

**Implementation Status:** ✅ Complete and Validated

| Limit | Value | Enforcement Point |
|-------|-------|-------------------|
| Inline payload | 1 MB | `_prepare_content()` |
| Total payload | 100 MB | `_prepare_content()` |
| Tags per atom | 20 | `_validate_tags()` |
| Tag key length | 50 chars | `_validate_tags()` |
| Tag weight range | [0.0, 1.0] | `_validate_tags()` |

**Payload Offload:** Content >1MB automatically written to `payloads/<atom_id>.json` with URI reference.

**Validation:** Gemini code review confirms correct enforcement.

---

## 3. Updated Migration Path (v0.1 → v0.2)

### Phase 1: Safety Hardening (COMPLETE ✅)
**Duration:** 2 days  
**Owner:** GPT-5 Codex + Gemini 2.5 Pro

- [x] File locking (single-writer safety)
- [x] Snapshot ID chaining
- [x] Payload/tag limits with offload
- [x] Golden determinism tests
- [x] Corruption quarantine tests
- [x] Bug fix: `iter_records` file handle reuse

### Phase 2: Observability & Documentation (IN PROGRESS)
**Duration:** 1-2 days  
**Owner:** GPT-5 Codex

- [ ] Replace `datetime.utcnow()` with `datetime.now(timezone.utc)`
- [ ] Integrate `structlog` for JSON logging
- [ ] Add Prometheus metrics (counters, histograms)
- [ ] Update README with safety policies
- [ ] Document snapshot ID logic and limits

### Phase 3: HHNI Implementation (NEXT)
**Duration:** 2 weeks  
**Owner:** GPT-5 Codex + o3pro (Integrator)

- [ ] Design HHNI node schema (5 levels: system → token)
- [ ] Implement graph database layer (Neo4j or DGraph)
- [ ] Build indexing pipeline (NLP parsing → HHNI nodes)
- [ ] Dependency hash computation
- [ ] Tag Priority Vector (TPV) assignment

### Phase 4: Hybrid Storage (FOLLOWING)
**Duration:** 2 weeks  
**Owner:** GPT-5 Codex + Cheetah (Performance)

- [ ] SQLite schema migration from journal files
- [ ] Qdrant/Weaviate vector store integration
- [ ] Transaction coordinator (ACID first, async propagation)
- [ ] Performance benchmarking (10K atoms, <100ms retrieval)

### Phase 5: Quality Scoring & κ-Gating (FINAL)
**Duration:** 1 week  
**Owner:** GPT-5 Codex + Gemini (Validation)

- [ ] Implement QS/IDS/DD formulas per original blueprint
- [ ] κ-gating logic with UQ integration
- [ ] Empirical tuning with validation dataset
- [ ] VIF/SEG contract implementation

---

## 4. Revised Acceptance Criteria (v0.2)

### Tier 1: Safety (BLOCKING) — Status: ✅ COMPLETE
- [x] AC1: Single-writer lock prevents concurrent corruption
- [x] AC2: Snapshot ID includes `previous_id` for chaining
- [x] AC3: Payload size limits enforced (1MB inline, 100MB total)
- [x] AC4: Tag hygiene validated (count, key length, weight range)
- [x] AC6: Golden test: identical snapshot IDs across clean runs
- [x] AC7: Corruption test: quarantine behavior on bad frames

### Tier 2: Observability (BLOCKING) — Status: 🟡 IN PROGRESS
- [ ] AC5: Structured JSON logging with correlation IDs
- [ ] AC9: Observability dashboard shows ingest/retrieval metrics

### Tier 3: Core Features (REQUIRED)
- [ ] AC1b: Ingest 10K atoms from `analysis/raw/` with HHNI indexing
- [ ] AC3b: Retrieval returns atoms ranked by RS with p95 latency <100ms
- [ ] AC8: Migration script successfully imports Phase 1 data

### Tier 4: Integration (REQUIRED)
- [ ] AC4b: VIF witnesses emitted for 100% of atoms + snapshots
- [ ] AC5b: SEG nodes created with valid temporal bounds
- [ ] AC10: Documentation includes API reference, HHNI query examples

---

## 5. Architecture Decisions Record (Updated)

### ADR-001: Snapshot ID Composition (FINALIZED)
**Decision:** Include `{atom_ids, previous_id, note}` in hash; exclude `created_at`.  
**Rationale:** Pure determinism + chain uniqueness without temporal coupling.  
**Status:** ✅ Implemented and validated.

### ADR-002: Payload Offload Threshold (FINALIZED)
**Decision:** 1MB inline, automatic offload to JSON files for larger content.  
**Rationale:** Balance between simplicity (inline) and scalability (offload).  
**Status:** ✅ Implemented and validated.

### ADR-003: File Locking Strategy (FINALIZED)
**Decision:** Non-blocking exclusive locks at journal initialization.  
**Rationale:** Fail-fast on contention; prevents silent corruption.  
**Status:** ✅ Implemented with cross-platform support.

### ADR-004: Tag Limits (FINALIZED)
**Decision:** Max 20 tags per atom, weights clamped to [0, 1].  
**Rationale:** Prevent tag explosion; simplify retrieval logic.  
**Status:** ✅ Implemented and validated.

### ADR-005: HHNI Storage Backend (PENDING)
**Decision:** TBD — Neo4j vs DGraph vs Apache AGE.  
**Rationale:** Evaluate based on: (1) query performance, (2) deployment complexity, (3) HHNI schema fit.  
**Status:** ⏳ Deferred to Phase 3.

---

## 6. Risk Register (Updated)

| Risk | Status | Mitigation |
|------|--------|------------|
| Journal corruption from concurrent writes | ✅ RESOLVED | File locking implemented and tested |
| OOM from unbounded payloads | ✅ RESOLVED | Size limits + offload |
| Non-deterministic snapshot IDs | ✅ RESOLVED | Include previous_id in hash |
| Tag explosion degrading performance | ✅ RESOLVED | Tag limits enforced |
| Undiagnosable production issues | 🟡 IN PROGRESS | Structured logging (Day 2) |
| Graph DB performance at scale | 🔴 OPEN | Benchmark with 1M nodes in Phase 3 |
| VIF/SEG services unavailable | 🔴 OPEN | Queue-based async + retry in Phase 5 |

---

## 7. Next Steps for Team

### Immediate (Day 2): GPT-5 Codex
1. Fix `datetime.utcnow()` deprecation
2. Add `structlog` + Prometheus metrics
3. Update README with safety policies

### Week 2: Claude 4.5 (Architect) + GPT-5 Codex (Builder)
1. Design HHNI node schema and graph structure
2. Select graph database (Neo4j, DGraph, or AGE)
3. Prototype HHNI level 0-2 indexing

### Week 3-4: Full Team
1. Implement hybrid storage (SQLite + vector + graph)
2. Build QS/IDS/DD scoring pipeline
3. Integration testing with VIF/SEG stubs

---

## 8. Conclusion

The v0.2-min safety foundation is **production-grade and validated**. The team executed flawlessly:
- **GPT-5 Codex** implemented all critical fixes in <2 days
- **Gemini 2.5 Pro** discovered and resolved a file-locking bug, validated all changes
- **Opus 4.1** provided clear safety requirements and acceptance criteria

We are now ready to build the advanced features (HHNI, hybrid storage, scoring) on a stable, deterministic substrate.

---

*Blueprint updated by Claude 4.5 (Architect) — reflects validated implementation state as of 2025-10-18*

