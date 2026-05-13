---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

## Structural overview

- **Monolithic kernel** with optional **loadable kernel modules (LKM)** (`DOCUMENTED`, kernel docs).  
- **System call interface** as stable ABI surface for userspace (`DOCUMENTED`).  
- **Virtual File System (VFS)** unifies concrete filesystem implementations (`DOCUMENTED`).  
- **Networking** integrated (socket layer, protocols, drivers) (`DOCUMENTED`).  
- **Scheduler** (CFS class default in modern kernels) (`DOCUMENTED`).

## Control vs data plane

- **Control:** `sysctl`, netlink, cgroupfs/bpf tooling interfaces; administrative syscalls (`DOCUMENTED` subset — expand claim IDs).  
- **Data plane:** packet processing, block I/O path, page cache (`DOCUMENTED`).

## UNKNOWN at seed depth

- Per-subsystem lock granularity maps and real-time variant details — add when curating specialty packages.
