---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# XNU / Darwin (macOS kernel) — Identity

**Kind:** Hybrid **Darwin** kernel combining Mach microkernel-derived components with **BSD** personality (system calls, VFS, networking) and I/O Kit for drivers, underpinning macOS/iOS family (`DOCUMENTED`, `src-apple-xnu`, Apple kernel programming docs).

## Boundaries

- **Not** the full macOS userspace (WindowServer, Cocoa) — kernel-focused package unless sourced.  
- **iOS/iPadOS** variants share XNU lineage but differ in policy and drivers — mark **release-specific** claims.

## Why this system matters

- Major example of **Mach ports + BSD** coexistence vs pure Unix or NT models (`DOCUMENTED` at architecture level).  
- **I/O Kit** driver model for hardware (`DOCUMENTED`).

## What this system teaches the atlas

- **Capability-like IPC** (Mach) vs file-descriptor APIs (BSD layer) in one kernel.  
- How **signed kernel extensions / System Extension** policy changed driver surface over time (`DOCUMENTED` Apple security docs — add source id when expanding).
