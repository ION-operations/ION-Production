---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| dist-001 | OCI Distribution Spec defines registry HTTP API for pushing/pulling OCI content (manifests, blobs) | DOCUMENTED | `src-oci-distribution-spec-repo` | |
| dist-002 | Composes with OCI Image Spec — transport separate from manifest/layer layout | DOCUMENTED | `src-oci-distribution-spec-repo`; `oci-image-spec` | |
| dist-003 | Container engines and Kubernetes stacks use distribution-compatible registry clients | DOCUMENTED | ecosystem; `docker`, `containerd`, `kubernetes` packages | |
