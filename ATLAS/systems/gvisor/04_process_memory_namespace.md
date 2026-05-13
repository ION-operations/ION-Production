---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# Process, memory, namespace

**Host** **cgroups** **and** **namespaces** **still** **wrap** **the** **sandbox;** **gVisor** **adds** **its** **own** **memory** **and** **syscall** **policy** **layer** **inside** **that** **envelope** (`DOCUMENTED`/`INFERRED`).
