---
atlas_package: system
system_slug: linux-fuse
schema_version: "1.0"
last_reviewed: "2026-04-25"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **FUSE** **is** **a** **kernel** **filesystem** **facility** (`DOCUMENTED`).  
- **`integrates_with` `linux-namespaces` + `linux-overlayfs` (INFERRED):** **mount** **namespaces** **scope** **FUSE** **mounts;** **OverlayFS** **is** **in-kernel** **stacked** **fs** **—** **different** **mechanism** **from** **FUSE.**
