---
atlas_package: system
system_slug: linux-overlayfs
schema_version: "1.0"
last_reviewed: "2026-04-23"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **OverlayFS** **filesystem** **implementation** (`DOCUMENTED`).  
- **`integrates_with` `linux-namespaces`:** **mount** **namespaces** **scope** **union** **mounts** (`INFERRED`).  
- **`integrates_with` `oci-image-spec` + `oci-runtime-spec` + container** **runtimes** **(INFERRED):** **layers** **/** **bundles** **/** **engines** **vs** **kernel** **union** **driver** — **do** **not** **merge** **concepts**.
