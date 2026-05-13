---
atlas_package: system
system_slug: systemd-sysext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| syx-001 | systemd-sysext(1) documents merge/refresh of system extension images | DOCUMENTED | `src-sysext-man` | |
| syx-002 | systemd-sysext.service manages extension merging on systemd systems | DOCUMENTED | `src-sysext-service` | |
| syx-003 | System extensions merge read-only layers into configured hierarchies (e.g. /usr), distinct from OCI container roots | DOCUMENTED | `src-sysext-man`; contrast `oci-image-spec` | |
