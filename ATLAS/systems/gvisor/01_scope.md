---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# Scope

## In scope

- **`runsc`** **as** **an** **OCI** **runtime,** **platform** **support** **matrices,** **and** **documented** **Kubernetes** **/** **containerd** **integration** (`DOCUMENTED`).  
- **Syscall** **interposition** **and** **compatibility** **tradeoffs** **at** **survey** **grain** (`INFERRED` **where** **marked**).

## Out of scope

- **Undocumented** **Google-internal** **deployment** **policies.**  
- **Guest** **kernel** **build** **recipes** **unless** **ledgered.**

## Versioning note

**gVisor** **releases** **track** **Go** **runtime** **and** **Linux** **host** **requirements** (`DOCUMENTED`).
