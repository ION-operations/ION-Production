---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| buildkit-001 | Upstream documents BuildKit as the modern Docker build backend and describes buildkitd architecture | DOCUMENTED | `src-buildkit-docs` | |
| buildkit-002 | BuildKit is distinct from low-level OCI runtime execution (runc/crun) at the mechanism level | INFERRED | — | survey boundary |
| buildkit-003 | Arbitrary Dockerfile reproducibility across registries without lockfiles | UNKNOWN | — | non-claim |
