---
atlas_package: system
system_slug: webassembly
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Core** **binary** **format**, **validation**, **execution** **semantics** (`DOCUMENTED`, `src-w3c-wasm-core2`).  
- **Proposals** **/** **extensions** **(e.g.** **threads,** **SIMD)** — **cite** **proposal** **or** **standard** **phase** (`DOCUMENTED` when load-bearing).

## Out of scope

- **Component** **Model** **(WASI** / **components)** — **often** **tracked** **as** **separate** **spec** **surfaces** (`DOCUMENTED` boundary).  
- **Every** **host** **embedding** **(browser** **vs** **wasmtime)** — **implementation** (`UNKNOWN` per product).

## Versioning note

**Wasm** **features** **evolve** **by** **proposal** — **pin** **feature** **set** **for** **claims** (`DOCUMENTED`).
