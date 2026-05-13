---
atlas_package: system
system_slug: crun
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# crun — Identity

**Kind:** **C** implementation of the **OCI Runtime Specification** — a **low-level** container runtime often chosen for **fast startup** and **minimal footprint** on **Linux** (`DOCUMENTED`, `src-crun-repo`).

## Boundaries

- **Not** **`runc`** — different codebase; both **`implement`** **`oci-runtime-spec`** (`DOCUMENTED`).  
- **Not** **`oci-runtime-spec`** — **crun** is an **implementation**, not the spec text (`DOCUMENTED`).  
- **Not** an **image** or **registry** stack — **`containerd`**, **`podman`**, **`cri-o`** invoke low-level runtimes (`DOCUMENTED`).

## Why this system matters

- Shows **multiple conforming** low-level runtimes in production **Linux** paths (`DOCUMENTED`).  
- **Substitution** point for performance and **distro** defaults (e.g. **Fedora**/**RHEL**-class tooling) (`DOCUMENTED` / `INFERRED`).

## What this system teaches the atlas

- **`competes_with`** **`runc`** at the **leaf** executor layer without changing **OCI** **image** or **distribution** contracts.
