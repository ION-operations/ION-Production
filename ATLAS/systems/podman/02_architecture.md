---
atlas_package: system
system_slug: podman
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **Fork/exec model** (default) vs optional **remote API** (`DOCUMENTED`).  
- **OCI runtime** integration (typically `runc`-class) (`DOCUMENTED`).  
- **Networking:** CNI-based patterns documented (`DOCUMENTED`).  
- **Storage:** overlay/graph driver concepts parallel to ecosystem (`DOCUMENTED`).
