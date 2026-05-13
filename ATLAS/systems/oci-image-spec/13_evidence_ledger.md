---
atlas_package: system
system_slug: oci-image-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| oci-001 | OCI Image Spec defines manifest, index, config, and layer conventions for interoperable container images | DOCUMENTED | `src-oci-image-spec-repo` | |
| oci-002 | Image format is distinct from OCI Runtime Spec / runtime bundle though stacks compose both | DOCUMENTED | `src-oci-image-spec-repo` | |
| oci-003 | Docker Engine / Moby builds and runs OCI-compatible images; engine is not the spec | DOCUMENTED | `src-oci-image-spec-repo`; `docker` package | |
