---
atlas_package: system
system_slug: libseccomp
schema_version: "1.0"
last_reviewed: "2026-04-19"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| libseccomp-001 | libseccomp documents itself as a library for generating seccomp filter BPF programs | DOCUMENTED | `src-libseccomp-github` | |
| libseccomp-002 | seccomp-filter BPF programs are a documented kernel-facing filter format (not general eBPF attach) | DOCUMENTED | `src-seccomp-kernel-docs` | |
| libseccomp-003 | Distinct from hand-written BPF for non-seccomp eBPF attach points | INFERRED | — | survey boundary |
