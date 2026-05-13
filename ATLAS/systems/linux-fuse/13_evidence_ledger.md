---
atlas_package: system
system_slug: linux-fuse
schema_version: "1.0"
last_reviewed: "2026-04-25"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-fuse-001 | Kernel FUSE documentation describes userspace delegation and the FUSE kernel interface | DOCUMENTED | `src-linux-fuse-kernel-docs` | |
| linux-fuse-002 | FUSE is a distinct concern from in-kernel stacked filesystems such as OverlayFS | INFERRED | — | survey boundary |
| linux-fuse-003 | FUSE is not interchangeable with OCI image formats or container engines alone | INFERRED | — | survey boundary |
