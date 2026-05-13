---
atlas_package: system
system_slug: msvc-vcruntime
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| msvc-crt-001 | Microsoft documents Universal C Runtime on Windows | DOCUMENTED | `src-ms-learn-ucrt` | |
| msvc-crt-002 | MSVC redistributable packages ship VCRUNTIME/UCRT DLLs | DOCUMENTED | `src-ms-learn-redist` | |
| msvc-crt-003 | PE/COFF binaries depend on listed CRT DLLs | OBSERVED | loader | field pattern |
