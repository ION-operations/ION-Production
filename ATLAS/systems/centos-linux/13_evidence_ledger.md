---
atlas_package: system
system_slug: centos-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| cl-001 | CentOS Project documented EOL timelines and Stream transition | DOCUMENTED | `src-centos-faq-eol` | |
| cl-002 | CentOS Linux used rpm/yum/dnf-class packaging | DOCUMENTED | `src-dnf-user-guide-cl`; wiki | |
| cl-003 | Legacy centos:* OCI images observed in registries | OBSERVED | `docker`; `oci-image-spec` | field pattern |
