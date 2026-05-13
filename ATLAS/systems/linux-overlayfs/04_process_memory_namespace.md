---
atlas_package: system
system_slug: linux-overlayfs
schema_version: "1.0"
last_reviewed: "2026-04-23"
evidence_grade: B
---

# Process, memory, namespace

**Overlay** **mounts** **live** **in** **a** **mount** **namespace** **context;** **changing** **the** **namespace** **changes** **which** **union** **mounts** **exist** **for** **processes** **(per** **namespaces(7)** **interaction** **patterns,** **`INFERRED`).**
