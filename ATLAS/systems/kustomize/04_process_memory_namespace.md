---
atlas_package: system
system_slug: kustomize
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Process, memory, namespace

**Kustomize** **runs** **as** **a** **client-side** **build** **step** **(local** **or** **CI)** **—** **it** **does** **not** **define** **pod** **namespaces** **for** **workloads** **until** **applied** **to** **the** **cluster** (`DOCUMENTED`/`INFERRED`).
