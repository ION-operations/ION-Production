---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

## Structural overview

- **Kernel mode vs user mode** split; traps and syscall dispatch (`DOCUMENTED`).  
- **HAL** abstracts CPU/I/O platform differences (`DOCUMENTED`).  
- **Executive** provides core OS services atop kernel (`DOCUMENTED`).  
- **Object Manager** namespace and handle indirection for many resources (`DOCUMENTED` in public internals literature).

## Control vs data plane

- **Control:** SCM/services, registry, WMI, various management APIs (many userspace) (`DOCUMENTED` subset).  
- **Data plane:** I/O manager path; networking stack (NDIS) (`DOCUMENTED` at driver-doc level).

## UNKNOWN

- Exact scheduling internals per build without a cited public source in this seed.
