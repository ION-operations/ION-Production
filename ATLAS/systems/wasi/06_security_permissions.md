---
atlas_package: system
system_slug: wasi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Capability discipline

**No** **ambient** **filesystem** — **imports** **only** (`DOCUMENTED` design goal).

## Host policy

**Runtime** **maps** **capabilities** **to** **OS** **resources** (`DOCUMENTED` wasmtime-style hosts).
