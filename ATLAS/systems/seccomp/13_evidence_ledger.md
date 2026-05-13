---
atlas_package: system
system_slug: seccomp
schema_version: "1.0"
last_reviewed: "2026-04-19"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| seccomp-001 | Kernel docs describe seccomp modes and seccomp-filter BPF programs for syscall filtering | DOCUMENTED | `src-seccomp-kernel-docs` | |
| seccomp-002 | seccomp-filter is distinct from attaching arbitrary eBPF programs to kprobes/tracepoints | DOCUMENTED | `src-seccomp-kernel-docs` | |
| seccomp-003 | Distinct from Landlock filesystem sandboxing | INFERRED | — | survey boundary |
