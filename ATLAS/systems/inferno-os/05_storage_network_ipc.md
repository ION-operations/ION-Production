---
atlas_package: system
system_slug: inferno-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Storage, network, and IPC

## Styx

**Styx** carries operations analogous to **9P**-style file access — wire format evolution vs Plan 9 **9P** is **protocol-detail** work (`DOCUMENTED` name; **UNKNOWN** bit-level without RFC).

## Network transparency

Applications use **file operations** over the protocol to reach remote resources — design goal (`DOCUMENTED`, `src-wiki-inferno`).
