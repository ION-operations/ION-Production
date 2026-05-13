---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Security and permissions

- **Mandatory Integrity Protection, SIP, sealed system volume** are macOS security features adjacent to kernel policy (`DOCUMENTED`, `src-apple-platform-security-guide`).  
- **Code signing** enforcement for kernel extensions / system extensions (`DOCUMENTED`).  
- **Sandbox (app)** enforced outside pure XNU in userspace + kernel hooks — cite Apple docs per claim (`DOCUMENTED`).
