---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Mach** primitives: tasks, threads, IPC ports (`DOCUMENTED`, kernel programming guide).  
- **BSD layer:** POSIX-ish syscalls, VFS, signals (`DOCUMENTED`).  
- **I/O Kit:** C++ driver framework (`DOCUMENTED`).  
- **VM** subsystem integrates Mach VM with BSD (`DOCUMENTED` overview).

**UNKNOWN** without source: full real-time scheduling story for all product lines.
