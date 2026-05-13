---
atlas_package: system
system_slug: podman
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Podman — Identity

**Kind:** **Daemonless** (by default) container engine implementing **OCI** images and **Docker-compatible** CLI patterns where documented, with emphasis on **rootless** operation (`DOCUMENTED`, `src-podman-docs`).

## Boundaries

- **Not** identical to `dockerd` architecture — no central daemon in default model (`DOCUMENTED`).  
- **Not** the same as `containerd` — different project; may share components (e.g. `containers` ecosystem) (`DOCUMENTED` / `INFERRED`—cite per component).

## Why this system matters

- Demonstrates **fork/exec vs daemon** tradeoffs for container management (`DOCUMENTED`).  
- **Rootless** defaults inform security deployment patterns (`DOCUMENTED`).

## What this system teaches the atlas

- “Docker-compatible” means **CLI/workflow overlap**, not identical implementation (`DOCUMENTED` caveat).
