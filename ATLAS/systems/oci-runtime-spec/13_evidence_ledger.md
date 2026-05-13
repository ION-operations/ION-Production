---
atlas_package: system
system_slug: oci-runtime-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| rt-001 | OCI Runtime Spec defines bundle layout (config.json, rootfs) and lifecycle operations | DOCUMENTED | `src-oci-runtime-spec-repo` | |
| rt-002 | Distinct from OCI Image Spec — images unpack into runtime bundles | DOCUMENTED | `src-oci-runtime-spec-repo`; `oci-image-spec` | |
| rt-003 | runc is the reference implementation of the OCI Runtime Spec | DOCUMENTED | `runc` package; `src-oci-runtime-spec-repo` | |
