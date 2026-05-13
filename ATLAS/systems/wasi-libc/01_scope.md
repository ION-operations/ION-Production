---
atlas_package: system
system_slug: wasi-libc
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Scope

## In scope

- **wasi-libc** **as** **the** **maintained** **C** **library** **sources** **and** **build** **that** **produce** **libc** **for** **WASI** **targets** (`DOCUMENTED`).  
- **Integration** **with** **clang**/**lld** **wasm** **link** **flows** **documented** **upstream** (`DOCUMENTED` / `INFERRED`).

## Out of scope

- **Browser** **Wasm** **embeddings** **that** **do** **not** **use** **WASI** **libc** **sysroots** — **separate** **stacks** (`INFERRED`).  
- **Rust** **`libc`** **crate** **/** **other** **language** **runtimes** — **unless** **given** **their** **own** **slugs** (`INFERRED`).

## Versioning note

**Upstream** **tags** **and** **WASI** **snapshot** **lines** **drive** **visible** **API** **surfaces** (`DOCUMENTED` / `OBSERVED`).
