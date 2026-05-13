---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Storage, network, and IPC

## 9P everywhere

**9P** carries **file operations** to local and remote file servers — network transparency is a design goal (`DOCUMENTED`, `src-wiki-plan9-9p`).

## Storage servers

**Fossil** + **Venti** — archival and caching roles in common descriptions (`DOCUMENTED`, `src-wiki-plan9-components`).

## IPC style

Much IPC is expressed as **operations on file descriptors** / 9P resources rather than a separate heavy IPC API surface (`DOCUMENTED` design summary; **INFERRED** detail).
