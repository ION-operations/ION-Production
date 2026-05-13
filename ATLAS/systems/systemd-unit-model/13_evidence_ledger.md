---
atlas_package: system
system_slug: systemd-unit-model
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| su-001 | systemd.unit(5) defines common unit sections and directives | DOCUMENTED | `src-systemd-unit` | |
| su-002 | Drop-in `.d/*.conf` fragments override vendor units | DOCUMENTED | `src-systemd-unit` | |
| su-003 | systemd.generator(7) describes generator exit codes and early-boot unit creation | DOCUMENTED | `src-systemd-generator` | |
