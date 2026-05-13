---
atlas_package: system
system_slug: pl-i
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (language architecture)

## Layering model (conceptual)

PL/I is a **high-level language** compiled or translated to **target machine code** for a given platform. The **language definition** (syntax + semantics) is **separate** from any one **code generator** (`DOCUMENTED`, `src-wiki-pl-i-summary`).

## Major semantic pillars (survey)

1. **Procedures and block structure** — Algol-like nesting; recursion (`DOCUMENTED`, `src-wiki-pl-i-goals`).  
2. **Data typing** — numeric (fixed/float/complex), strings, bit strings, aggregates (arrays, structures) (`DOCUMENTED`, `src-wiki-pl-i-summary`).  
3. **Storage classes** — automatic, static, controlled, based (implementation details vary — `DOCUMENTED` overview vs **UNKNOWN** per compiler).  
4. **I/O** — stream vs record models; `GET`/`PUT` vs `READ`/`WRITE` families (`DOCUMENTED`, `src-wiki-pl-i-summary`).  
5. **Exception / interrupt handling** — `ON`, `SIGNAL`, `REVERT` class of constructs in standard summaries (`DOCUMENTED`, `src-wiki-pl-i-summary`).  
6. **Separate compilation** — external entry points, linker binding (`DOCUMENTED`, `src-wiki-pl-i-goals`).

## Machine and assembly relationship

Programs are expressed in **PL/I source**; runtimes execute **machine instructions** produced by the implementation. **Assembly language** is not the PL/I programmer’s primary surface — unlike macro assemblers on the same iron (`INFERRED` layering; see `comparative/language_machine_and_assembly_stack.md`).

## Formal methods connection

The **IBM Vienna** work on **VDM** is historically tied to formalizing PL/I semantics (`HISTORICAL`, `src-wiki-pl-i-vienna`); depth of mechanized proof in this package — **PARTIAL** unless primary citation added per claim.
