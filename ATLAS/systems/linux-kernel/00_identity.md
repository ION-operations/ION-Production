---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Linux kernel — Identity

**Kind:** Open-source monolithic Unix-like kernel with loadable modules, implementing hardware abstraction, scheduling, memory management, VFS, networking, and security hooks.

## Canonical definition

The Linux kernel is the privileged core of GNU/Linux systems, developed upstream on kernel.org with a distributed maintainer model (`DOCUMENTED`, `src-kernel-source-tree`, `src-kernel-documentation`).

## Boundaries

- This package is **the kernel**, not a specific distribution userspace.  
- **Not** POSIX itself; POSIX is a userspace-visible standard partially satisfied by libc + kernel features (`std-posix`).

## Why this system matters

- Dominant **open kernel** for servers, Android, embedded, and cloud hosts (`OBSERVED` market fact — optional economic source).  
- **Extensibility** via loadable modules and eBPF influences how security and observability attach (`DOCUMENTED`).  
- **Cgroups + namespaces** underpin modern container runtimes (`DOCUMENTED`).

## What this system teaches the atlas

- How **DOCUMENTED** claims scale when primary evidence is source + official docs.  
- How to separate **kernel** from **service-manager** (`systemd`) and **container runtime** (`docker`).
