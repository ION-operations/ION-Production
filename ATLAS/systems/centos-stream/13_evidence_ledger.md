---
atlas_package: system
system_slug: centos-stream
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| cs-001 | CentOS Stream documents upstream-for-RHEL positioning | DOCUMENTED | `src-centos-stream-about` | |
| cs-002 | CentOS Stream uses rpm/dnf-class packaging | DOCUMENTED | `src-dnf-user-guide-cs`; project docs | |
| cs-003 | Official OCI images use centos stream bases | OBSERVED | `docker`; `oci-image-spec` | field pattern |
