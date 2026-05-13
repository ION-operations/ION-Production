---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- Kernel/executive responsibilities: scheduling, memory manager, I/O manager, object manager, security reference monitor interfaces at a **documentation-aligned** level.  
- Syscall/Win32 boundary as public API surface (`DOCUMENTED`, `src-ms-win32-api`).

## Out of scope

- Undocumented kernel structures not in public references — mark **UNKNOWN**.  
- Specific undisclosed security mitigations.

## Versioning note

Windows 10/11 continuous servicing changes internals; prefer **build or release** when making precise claims.
