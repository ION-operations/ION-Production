---
atlas_package: system
system_slug: msvc-vcruntime
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **UCRT** **/** **`VCRUNTIME*.dll`** **as** **documented** **MSVC** **runtime** **DLL** **surfaces** (`DOCUMENTED`).  
- **Redistributable** **packages** **and** **versioning** **themes** (`DOCUMENTED` **/** `OBSERVED`).

## Out of scope

- **.NET** **CLR** **/** **managed** **runtime** — **use** **`ecma-335-cli`** (`DOCUMENTED`).

## Versioning note

**MSVC** **toolset** **and** **redistributable** **package** **versions** **track** **Visual** **Studio** **/** **VC++** **release** **notes** (`DOCUMENTED`).
