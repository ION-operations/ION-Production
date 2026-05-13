---
atlas_package: system
system_slug: systemd-portable
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| sp-001 | portablectl(1) documents attach/detach of portable service images | DOCUMENTED | `src-portablectl` | |
| sp-002 | systemd.io describes portable services architecture | DOCUMENTED | `src-portable-io` | |
| sp-003 | Portable services are distinct from OCI container images | DOCUMENTED | `src-portable-io`; contrast `docker` | |
