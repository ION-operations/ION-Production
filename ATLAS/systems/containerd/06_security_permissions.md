---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Security and permissions

- **Unix socket permissions** for daemon access (`DOCUMENTED`).  
- **Non-root / rootful** modes as documented (`DOCUMENTED` where supported).  
- **Image signature** topics — follow containerd/notary ecosystem docs (`DOCUMENTED` feature-dependent).
