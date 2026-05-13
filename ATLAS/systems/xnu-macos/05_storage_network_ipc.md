---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Storage, network, and IPC

- **VFS** stack in BSD layer (`DOCUMENTED`).  
- **APFS** and stack-upper layers documented at Apple FS docs (`DOCUMENTED` — add dedicated source when deep-diving).  
- **Networking** BSD-derived stack (`DOCUMENTED` overview).  
- **IPC:** Mach messages, UNIX domain sockets, etc. (`DOCUMENTED`).
