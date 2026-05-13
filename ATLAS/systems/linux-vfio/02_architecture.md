---
atlas_package: system
system_slug: linux-vfio
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (conceptual)

**VFIO** **mediates** **device** **visibility** **and** **DMA** **isolation** **via** **IOMMU** **infrastructure** **so** **that** **userspace** **or** **guest** **assignees** **can** **own** **a** **device** **function** **without** **breaking** **host** **memory** **safety** **per** **documented** **kernel** **models** (`DOCUMENTED`/`INFERRED`).
