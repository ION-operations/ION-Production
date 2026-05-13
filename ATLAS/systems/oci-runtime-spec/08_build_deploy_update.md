---
atlas_package: system
system_slug: oci-runtime-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Build, deploy, update

**Bundles** are produced at **pull**/**create** time; **updates** replace **rootfs**/**config** before **start** (`DOCUMENTED` operational pattern).
