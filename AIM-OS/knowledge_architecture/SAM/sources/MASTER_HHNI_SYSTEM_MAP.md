# MASTER HHNI (Hierarchical Hypergraph Neural Index) SYSTEM MAP

**Date:** 2026-02-22  
**System:** Hierarchical Hypergraph Neural Index  
**Implementation:** packages/hhni/

---

**[TAG:SAM] [TAG:MASTER] [TAG:HHNI]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:HHNI]**

HHNI (Hierarchical Hypergraph Neural Index) solves the "lost in the middle" problem — where AI loses track of information in long contexts. Combines fractal indexing at 6 resolutions (System -> Section -> Paragraph -> Sentence -> Word -> Subword) with DVNS (Dynamic Vector Navigation System) physics engine. RS-Lift +15% at precision-at-rank-5.

**[END:TAG:OVERVIEW]**

---

## 2. STATIC STRUCTURE MAP

**[TAG:STRUCTURE] [TAG:HHNI]**

### Core Components

- **Indexer:** Fractal hierarchical indexing
- **semantic_search:** Semantic retrieval
- **retrieval:** Two-stage retrieval pipeline
- **dvns_physics:** Physics engine (Gravity, Elastic, Repulse, Damping)
- **deduplication:** Dedup stage
- **conflict_resolver:** Conflict resolution
- **compressor:** Strategic compression
- **budget_manager:** Token budget fitting

### Integration

CMC (atoms), APOE (context), VIF (witnesses), SEG (evidence), SDF-CVF (parity). CMC integration via cmc_poller.

**[END:TAG:STRUCTURE]**

---

## 3. DYNAMIC BEHAVIOR MAP

**[TAG:BEHAVIOR] [TAG:HHNI]**

### Retrieval Flow

Stage 1: Coarse KNN (top-100) -> Stage 2: DVNS physics (50-100 iterations) -> Dedup -> Conflict resolution -> Compression -> Budget fit

**[END:TAG:BEHAVIOR]**

---

## 4. INTERFACE & INTEGRATION MAP

**[TAG:INTEGRATION] [TAG:HHNI]**

| System | Purpose |
|--------|---------|
| CMC | Atoms for indexing; retrieval queries |
| APOE | Context retrieval |
| VIF | Witnesses in retrieval context |
| SEG | Evidence indexing |

**[END:TAG:INTEGRATION]**

---

## 5. CONSTRAINTS & LIMITATIONS

**[TAG:PERFORMANCE] [TAG:DEPENDENCY] [TAG:HHNI]**

- **Target:** p95 < 80ms (coarse); full benchmark retrieval p95 ~29-33s (varies by profile)
- **DVNS iterations:** 50-100

**[END:TAG:PERFORMANCE] [END:TAG:DEPENDENCY]**

---

## 6. EVIDENCE & VALIDATION

**[TAG:SUMMARY] [TAG:HHNI]**

- **Tests:** 119 passed (audit baseline)
- **Status:** Operational
- **Documentation:** knowledge_architecture/systems/hhni/

**[END:TAG:SUMMARY]**

---

## 7. RELATIONSHIP MATRIX

**[TAG:RELATIONSHIP] [TAG:HHNI]**

| To System | Relationship |
|-----------|--------------|
| CMC | HHNI indexes atoms; receives retrieval queries |
| APOE | HHNI provides context for orchestration |
| VIF | HHNI includes witnesses in retrieval |
| SEG | HHNI indexes evidence |

**[END:TAG:RELATIONSHIP]**
