---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# Architecture

- **Userspace** **Sentry** **kernel** **and** **Go** **runtime** **components** **that** **mediate** **application** **syscalls** **per** **upstream** **architecture** **docs** (`DOCUMENTED`, `src-gvisor-docs`).  
- **Contrasts** **with** **direct** **host** **syscall** **paths** **used** **by** **default** **runc** **sandboxes** (`INFERRED` **comparative**).
