---
atlas_package: system
system_slug: wasi-libc
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| wasi-libc-001 | Upstream documents wasi-libc as a libc for WebAssembly + WASI | DOCUMENTED | `src-wasi-libc-github` | README |
| wasi-libc-002 | Build produces installable sysroot for wasm32-wasi targets | DOCUMENTED | `src-wasi-libc-github` | |
| wasi-libc-003 | Distinct from the WASI specification repository (API vs implementation) | INFERRED | — | package boundary |
