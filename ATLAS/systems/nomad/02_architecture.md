---
atlas_package: system
system_slug: nomad
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Nomad servers** maintain cluster state and schedule work (`DOCUMENTED`).  
- **Nomad clients** execute tasks via **task drivers** (`DOCUMENTED`).  
- **Leader election** / **Raft** (as documented for server clustering) (`DOCUMENTED`).

## UNKNOWN at seed depth

- Exact internal RPC schemas without citing Nomad internals docs — upgrade with specific doc sections.
