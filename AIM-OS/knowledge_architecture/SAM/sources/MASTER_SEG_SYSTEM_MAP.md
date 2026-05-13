# MASTER SEG (Shared Evidence Graph) SYSTEM MAP

**Date:** 2026-02-22  
**System:** Shared Evidence Graph  
**Implementation:** packages/seg/

---

**[TAG:SAM] [TAG:MASTER] [TAG:SEG]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:SEG]**

SEG (Shared Evidence Graph) transforms scattered evidence into a unified, temporal, contradiction-aware knowledge graph. Every claim, source, derivation, and agent becomes a node; relationships (supports, contradicts, derives, witnesses) become edges. Bitemporal awareness, contradiction detection, auditable export (JSON-LD, RDF, SHACL).

**[END:TAG:OVERVIEW]**

---

## 2. STATIC STRUCTURE MAP

**[TAG:STRUCTURE] [TAG:SEG]**

### Components

Graph schema, graph store, contradiction detector, query engine, export system. VIF witnesses linked as provenance.

**[END:TAG:STRUCTURE]**

---

## 3. DYNAMIC BEHAVIOR MAP

**[TAG:BEHAVIOR] [TAG:SEG]**

Evidence ingestion -> Graph update -> Contradiction detection -> Query/synthesis -> Export

**[END:TAG:BEHAVIOR]**

---

## 4. INTERFACE & INTEGRATION MAP

**[TAG:INTEGRATION] [TAG:SEG]**

| System | Purpose |
|--------|---------|
| CMC | Storage |
| HHNI | Context retrieval |
| VIF | Witnesses as provenance |
| APOE | Derivations |
| SDF-CVF | Traces |

**[END:TAG:INTEGRATION]**

---

## 5. CONSTRAINTS & LIMITATIONS

**[TAG:PERFORMANCE] [TAG:DEPENDENCY] [TAG:SEG]**

- Bitemporal consistency required
- Provenance must trace to source (VIF witness, document, user input)

**[END:TAG:PERFORMANCE] [END:TAG:DEPENDENCY]**

---

## 6. EVIDENCE & VALIDATION

**[TAG:SUMMARY] [TAG:SEG]**

- **Tests:** 104 passed (audit baseline)
- **Status:** Operational

**[END:TAG:SUMMARY]**

---

## 7. RELATIONSHIP MATRIX

**[TAG:RELATIONSHIP] [TAG:SEG]**

| To System | Relationship |
|-----------|--------------|
| CMC | SEG stores graph; atoms referenced |
| VIF | SEG links witnesses as provenance |
| APOE | SEG receives derivations |

**[END:TAG:RELATIONSHIP]**
