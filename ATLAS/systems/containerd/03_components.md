---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| containerd | Core daemon | DOCUMENTED |
| CRI plugin | kubelet interface | DOCUMENTED |
| Snapshotters | Layer/rootfs | DOCUMENTED |
| ctr / nerdctl (ecosystem) | CLI tooling | DOCUMENTED / ecosystem |
