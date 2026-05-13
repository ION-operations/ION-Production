# MASTER APOE (AI-Powered Orchestration Engine) SYSTEM MAP

**Date:** 2026-02-22  
**System:** AI-Powered Orchestration Engine  
**Implementation:** packages/apoe/

---

**[TAG:SAM] [TAG:MASTER] [TAG:APOE]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:APOE]**

APOE (AI-Powered Orchestration Engine) compiles intent into typed, budgeted, gated execution plans. ACL (AIMOS Chain Language) -> typed DAG. Eight roles: Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness. Quality/Safety/Policy gates; budget gates; DEPP (self-rewriting plans via evidence).

**[END:TAG:OVERVIEW]**

---

## 2. STATIC STRUCTURE MAP

**[TAG:STRUCTURE] [TAG:APOE]**

### Components

ACL parser, role dispatch, budget management, gate enforcement. Types validated, budgets computed, gates positioned before execution.

**[END:TAG:STRUCTURE]**

---

## 3. DYNAMIC BEHAVIOR MAP

**[TAG:BEHAVIOR] [TAG:APOE]**

ACL input -> Parse -> Compile DAG -> Validate types/budgets -> Position gates -> Execute -> Gather evidence -> (DEPP) Rewrite plan

**[END:TAG:BEHAVIOR]**

---

## 4. INTERFACE & INTEGRATION MAP

**[TAG:INTEGRATION] [TAG:APOE]**

| System | Purpose |
|--------|---------|
| HHNI | Context retrieval |
| VIF | Witnesses, gates (abstention) |
| CMC | State persistence |
| SEG | Evidence |
| SDF-CVF | Parity |

**[END:TAG:INTEGRATION]**

---

## 5. CONSTRAINTS & LIMITATIONS

**[TAG:PERFORMANCE] [TAG:DEPENDENCY] [TAG:APOE]**

- Budgets: tokens, time, tools (hard constraints)
- Gates: PASS, FAIL, WARN, ABSTAIN
- VIF confidence used for abstention

**[END:TAG:PERFORMANCE] [END:TAG:DEPENDENCY]**

---

## 6. EVIDENCE & VALIDATION

**[TAG:SUMMARY] [TAG:APOE]**

- **Tests:** 381 passed (audit baseline)
- **Status:** Operational

**[END:TAG:SUMMARY]**

---

## 7. RELATIONSHIP MATRIX

**[TAG:RELATIONSHIP] [TAG:APOE]**

| To System | Relationship |
|-----------|--------------|
| HHNI | APOE retrieves context |
| VIF | APOE uses gates |
| CMC | APOE persists state |
| SEG | APOE provides derivations |

**[END:TAG:RELATIONSHIP]**
