---
atlas_package: system
system_slug: oci-runtime-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# OCI Runtime Specification

**Kind:** **Open Container Initiative** specification for the **runtime bundle** — **`config.json`**, **`rootfs`**, and **lifecycle** operations (`create`, `start`, …) for a container process (`DOCUMENTED`, `src-oci-runtime-spec-repo`).

## Boundaries

- **Not** **`oci-image-spec`** — images unpack **into** a bundle, but **image** JSON is not the **runtime** contract (`DOCUMENTED`).  
- **Not** **`oci-distribution-spec`** — registry **HTTP** is orthogonal to executing a bundle (`DOCUMENTED`).  
- **Not** **`runc`** — **`runc`** is a **reference implementation** of this spec, not the spec text (`DOCUMENTED`).

## Why this system matters

- **Stable contract** between high-level runtimes (**`containerd`**, **`cri-o`**, **`podman`**, **`docker`**) and low-level executors (**`runc`**, **crun**, …) on Linux (`DOCUMENTED`).  
- Separates **“what runs”** (bundle + lifecycle) from **“what was shipped”** (image layers).

## What this system teaches the atlas

- Use **`oci-runtime-spec`** whenever **`config.json`** / **hooks** / **cgroups** / **namespaces** semantics are in scope—not **`oci-image-spec`**.
