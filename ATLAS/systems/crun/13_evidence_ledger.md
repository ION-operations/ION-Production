---
atlas_package: system
system_slug: crun
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| cr-001 | crun is an OCI runtime implementation (Linux) | DOCUMENTED | `src-crun-repo` | |
| cr-002 | Podman, CRI-O, and containerd stacks can use crun as low-level runtime | DOCUMENTED | upstream docs / `containerd`, `podman`, `cri-o` | |
| cr-003 | Substitutes for runc at the leaf executor layer on Linux | INFERRED | comparative | |
