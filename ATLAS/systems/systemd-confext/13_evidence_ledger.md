---
atlas_package: system
system_slug: systemd-confext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| cfx-001 | systemd-confext(1) documents merge/refresh of configuration extension images | DOCUMENTED | `src-confext-man` | |
| cfx-002 | systemd-confext.service manages configuration extension merging on systemd systems | DOCUMENTED | `src-confext-service` | |
| cfx-003 | Configuration extensions target /etc-class trees, distinct from systemd-sysext /usr merge | DOCUMENTED | `src-confext-man`; `systemd-sysext` | |
