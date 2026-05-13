---
atlas_package: system
system_slug: linux-kvm
schema_version: "1.0"
last_reviewed: "2026-04-26"
evidence_grade: B
---

# Process, memory, namespace

**Host** **processes** **implementing** **a** **VMM** **use** **KVM;** **guest** **memory** **and** **vCPUs** **are** **distinct** **from** **host** **PID** **namespaces** **—** **guests** **can** **run** **their** **own** **kernels** (`DOCUMENTED`/`INFERRED`).
