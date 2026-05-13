---
atlas_package: system
system_slug: wasi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Sandboxed I/O

**Host** **mediates** **filesystem** **and** **network** **access** (`DOCUMENTED` model).

## Linear memory

**Still** **Wasm** **linear** **memory** **for** **module** **code** — **orthogonal** **to** **WASI** **imports** (`DOCUMENTED`).
