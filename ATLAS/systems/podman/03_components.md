---
atlas_package: system
system_slug: podman
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| podman | User-facing engine | DOCUMENTED |
| conmon / runtime stack | Container supervision | DOCUMENTED |
| netavark / pasta (network) | Networking backends | DOCUMENTED (version-dependent) |
| Quadlet / systemd integration | Service units | DOCUMENTED |
