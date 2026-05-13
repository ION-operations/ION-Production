---
atlas_package: system
system_slug: msvcprt
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| msvc-cxx-001 | Microsoft documents MSVC C++ standard library | DOCUMENTED | `src-ms-learn-cpp-runtime` | |
| msvc-cxx-002 | msvcp*.dll ships in VC++ redistributable bundles | DOCUMENTED | `src-ms-learn-redist` | |
| msvc-cxx-003 | PE binaries list msvcp imports in typical MSVC flows | OBSERVED | dumpbin | field pattern |
