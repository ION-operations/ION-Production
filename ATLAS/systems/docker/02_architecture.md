---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **`dockerd` daemon** exposes HTTP API; **`docker` CLI** is a client (`DOCUMENTED`).  
- **containerd/runc** (or platform runtime) participate in Linux execution path per current Engine architecture docs (`DOCUMENTED` — verify diagram version).  
- **Networking:** bridge/overlay drivers as documented (`DOCUMENTED`).  
- **Storage:** layered images, graph drivers / snapshotters per docs (`DOCUMENTED`).

**UNKNOWN** at seed depth: per-build internal RPC breakdown without citing Engine design doc revision.
