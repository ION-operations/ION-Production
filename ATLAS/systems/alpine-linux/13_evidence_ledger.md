---
atlas_package: system
system_slug: alpine-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| alp-001 | Alpine Linux documents musl as the standard C library on supported architectures | DOCUMENTED | `src-alpine-about`; `src-alpine-wiki-musl` | |
| alp-002 | Alpine uses apk for package management and OpenRC as default init in mainline docs | DOCUMENTED | `src-alpine-about` | |
| alp-003 | Alpine is widely used as an OCI image base alongside musl userlands | OBSERVED | `docker`; `oci-image-spec` | field pattern |
