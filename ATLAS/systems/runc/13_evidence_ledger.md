---
atlas_package: system
system_slug: runc
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| rc-001 | runc implements OCI runtime spec for bundles | DOCUMENTED | `std-oci-runtime-spec`, `src-runc-repo` | |
| rc-002 | runc applies Linux namespaces/cgroups per bundle | DOCUMENTED | `src-runc-repo` | |
| rc-003 | Other OCI runtimes exist (crun, etc.) | DOCUMENTED | Ecosystem docs / distros | Add ids if needed |
| rc-004 | runC announced as part of Docker/OCI modularization (2015-era) | HISTORICAL | `src-docker-blog-runc-intro` | Pair with OCI primary sources as needed |
