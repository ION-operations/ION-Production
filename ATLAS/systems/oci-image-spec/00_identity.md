---
atlas_package: system
system_slug: oci-image-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# OCI Image Format

**Kind:** **Open Container Initiative** specification for **container images** — manifest/index, layer blobs, config, and **filesystem bundle** semantics consumed by OCI-compatible runtimes and registries (`DOCUMENTED`, `src-oci-image-spec-repo`).

## Boundaries

- **Not** **Docker Engine** — **Moby**/`dockerd` is one implementation that builds and runs **OCI** images (`DOCUMENTED`; see `docker`).  
- **Not** the **OCI Runtime Spec** — defines the **runtime bundle** / `config.json` contract; **`runc`** implements that layer (`DOCUMENTED` adjacent).  
- **Not** **systemd portable** images — **OS-tree** portable bundles are a different format (`DOCUMENTED`; see `systemd-portable`).

## Why this system matters

- **Interoperable** artifact format across **registries**, **Kubernetes** workloads, and multiple **container runtimes** (`DOCUMENTED`).  
- Separates **“what is shipped”** (image layers + config) from **“who runs it”** (engine, CRI, orchestrator).

## What this system teaches the atlas

- Treat **image spec** as its own witness when comparing **OCI stacks** to **systemd portable** or **VM** delivery.
