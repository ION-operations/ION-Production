---
atlas_package: system
system_slug: debian
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| deb-001 | Debian stable releases document systemd as default init alongside glibc userland | DOCUMENTED | `src-debian-systemd-wiki`; `src-debian-releases` | |
| deb-002 | Debian uses dpkg/apt for package management | DOCUMENTED | Debian documentation / policy themes | |
| deb-003 | Official and community OCI images commonly use debian/slim bases | OBSERVED | `docker`; `oci-image-spec` | field pattern |
