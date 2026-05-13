---
atlas_package: system
system_slug: libbpf
schema_version: "1.0"
last_reviewed: "2026-04-16"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| libbpf-001 | libbpf documents itself as the reference userspace library for BPF program loading and maps on Linux | DOCUMENTED | `src-libbpf-github`, `src-libbpf-kernel-docs` | |
| libbpf-002 | Kernel docs describe libbpf as the supported userspace API for BPF | DOCUMENTED | `src-libbpf-kernel-docs` | |
| libbpf-003 | Distinct package boundary from in-kernel eBPF bytecode semantics (`ebpf`) | INFERRED | — | survey boundary |
