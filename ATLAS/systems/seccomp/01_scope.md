---
atlas_package: system
system_slug: seccomp
schema_version: "1.0"
last_reviewed: "2026-04-19"
evidence_grade: B
---

# Scope

## In scope

- **Kernel** **documented** **behavior** **for** **seccomp** **modes** **and** **seccomp-filter** (`DOCUMENTED`).  
- **BPF** **filter** **programs** **as** **defined** **for** **syscall** **filtering** (`DOCUMENTED`).

## Out of scope

- **eBPF** **program** **types** **outside** **seccomp** **hook** — **`ebpf`** **package**.  
- **Non-Linux** — **out** **of** **package**.

## Versioning note

**Kernel** **features** **track** **mainline** **releases** (`OBSERVED`).
