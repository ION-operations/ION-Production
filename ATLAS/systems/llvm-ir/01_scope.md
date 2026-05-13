---
atlas_package: system
system_slug: llvm-ir
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **LangRef**-**defined** **instruction** **set**, **types**, **SSA** **rules** (`DOCUMENTED`, `src-llvm-langref`).  
- **Bitcode** **/** **IR** **file** **forms** as **documented** **by** **LLVM** (`DOCUMENTED`).

## Out of scope

- **Specific** **LLVM** **release** **schedule** — **cite** **release** **notes** **when** **load-bearing**.  
- **Non-LLVM** **IRs** (**MIR**, **GCC** **GIMPLE**) — **separate** **packages**.

## Versioning note

**IR** **semantics** **can** **shift** **between** **LLVM** **major** **versions** — **pin** **version** **for** **precise** **claims** (`DOCUMENTED`).
