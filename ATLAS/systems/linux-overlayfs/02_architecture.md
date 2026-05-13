---
atlas_package: system
system_slug: linux-overlayfs
schema_version: "1.0"
last_reviewed: "2026-04-23"
evidence_grade: B
---

# Architecture (conceptual)

**A** **merged** **directory** **presents** **the** **union** **of** **one** **or** **more** **read-only** **lower** **layers** **plus** **a** **writable** **upper** **layer,** **with** **a** **workdir** **for** **internal** **filesystem** **operations** **per** **kernel** **documentation** (`DOCUMENTED`).
