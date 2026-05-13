# Part II: Architecture - L0 Executive Summary

**Part:** II - Architecture  
**Level:** L0 (Executive Summary)  
**Word Count:** 100 words (exact)  
**Purpose:** Quick summary of Part II architecture

---

PLIx architecture rests on four pillars: Contract (intent specification via CNL), Execution (durable execution with Saga pattern), Safety (confidence gates and policy-as-code), and Evidence (provenance and lineage). CNL grammar provides controlled natural language design, enabling unambiguous intent expression. Formal validation (Alloy, TLA+) ensures invariant correctness. The compiler transforms PLIx contracts through IR to execution plans, integrating with APOE for orchestration. This architecture enables intent-aware systems with verifiable correctness, durable execution, and complete provenance.

