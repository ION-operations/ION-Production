---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- Mainline architecture: syscalls, scheduler, MM, VFS, networking stack, driver model, LSM/BPF hooks.  
- Container-relevant primitives: namespaces, cgroups, capabilities (`DOCUMENTED`).

## Out of scope

- Distro policy (package selection, init choice) except as examples.  
- libc implementations unless syscall boundary relevant.

## Versioning note

Kernel releases are **time-indexed**; behavior may change across versions — cite version or “current mainline” when making precise claims.
