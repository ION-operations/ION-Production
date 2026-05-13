---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lk-001 | Monolithic kernel with loadable modules | DOCUMENTED | `src-kernel-documentation` | |
| lk-002 | Namespaces + cgroups underpin Linux containers | DOCUMENTED | `src-kernel-documentation` (namespaces, cgroups) | |
| lk-003 | VFS unifies filesystem implementations | DOCUMENTED | `src-kernel-source-tree` fs/ | |
| lk-004 | eBPF provides verifiable kernel attachment | DOCUMENTED | BPF docs in kernel tree | |
| lk-005 | CFS is default scheduling class (modern mainline) | DOCUMENTED | scheduler docs | Version-sensitive |
