---
atlas_package: system
system_slug: linux-overlayfs
schema_version: "1.0"
last_reviewed: "2026-04-23"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-overlayfs-001 | Kernel OverlayFS documentation describes upper/lower/work dirs and merged view semantics | DOCUMENTED | `src-linux-overlayfs-kernel-docs` | |
| linux-overlayfs-002 | OverlayFS is a distinct concern from OCI image manifest and layer tarball layout | INFERRED | — | survey boundary |
| linux-overlayfs-003 | OverlayFS is not interchangeable with container engines or runtimes alone | INFERRED | — | survey boundary |
