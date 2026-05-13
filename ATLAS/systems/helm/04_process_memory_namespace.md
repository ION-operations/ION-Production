---
atlas_package: system
system_slug: helm
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Process, memory, namespace

**Helm** **CLI** **runs** **as** **a** **userspace** **client** **on** **operator** **workstations** **or** **CI** **agents;** **it** **does** **not** **define** **pod** **process** **namespaces** **(those** **are** **Kubernetes** **objects)** (`DOCUMENTED`/`INFERRED`).
