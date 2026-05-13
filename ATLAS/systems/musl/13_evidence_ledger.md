---
atlas_package: system
system_slug: musl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| msl-001 | musl is a POSIX-conforming C library implementation for Linux | DOCUMENTED | `src-musl-wiki` | |
| msl-002 | musl and glibc are not ABI-interchangeable as drop-in substitutes | DOCUMENTED | comparative; `glibc` | |
| msl-003 | Widely used in minimal Linux container images (e.g. Alpine-class bases) | INFERRED | `docker` ecosystem | |
