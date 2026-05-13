---
atlas_package: system
system_slug: webassembly
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Sandboxing

**Memory** **isolation** **from** **host** **address** **space** — **unless** **explicit** **imports** (`DOCUMENTED`, `src-w3c-wasm-core2`).

## Host calls

**Imports** **/** **exports** — **capability** **boundary** (`DOCUMENTED`, `src-w3c-wasm-core2`).
