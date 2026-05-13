---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Windows NT family — Identity

**Kind:** Commercial general-purpose OS kernel + executive subsystems forming the base of modern Windows client and server products.

## Canonical definition

The NT kernel provides preemptive multitasking, virtual memory, object-based resource management, and a hardware abstraction layer (HAL); upper layers include executive services and Win32 subsystem (`DOCUMENTED`, `src-ms-learn-windows-kernel`, standard internals references such as `paper-russinovich-solomon-2005` when cited per claim).

## Boundaries

- **Not** the full Windows product catalog (Shell, Store, Defender policies) unless sourced per feature.  
- **Not** Xbox/Azure Sphere variants in this seed — scope expansion required.

## Why this system matters

- Major **desktop and enterprise** kernel with distinct object/handle model vs Unix FD tables (`DOCUMENTED`).  
- **Driver ecosystem** (WDM, WDF) shapes security surface (`DOCUMENTED`).  
- Long **backwards compatibility** pressure influencing internal design (`HISTORICAL` / product docs mix).

## What this system teaches the atlas

- How to model **handle-based object manager** namespaces vs path-only Unix VFS.  
- How to keep **release-relative** claims versioned.
