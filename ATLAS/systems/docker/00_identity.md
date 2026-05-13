---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Docker Engine / Moby — Identity

**Kind:** Container runtime and image tooling that builds, runs, and distributes **OCI** images, historically centered on `dockerd` and the Docker CLI; upstream open source is **Moby** (`DOCUMENTED`, `src-docker-docs`, `src-moby-repo`).

## Boundaries

- **Not** the **OCI Image Spec** — **`oci-image-spec`** is the interoperable **image format**; **Moby**/**`dockerd`** is one engine that **produces and runs** OCI-compatible images (`DOCUMENTED`).  
- **Not** the **OCI Distribution Spec** — **`oci-distribution-spec`** is the **registry HTTP API** class; the engine is a **client** of registries (`DOCUMENTED`).  
- **Not** the **OCI Runtime Spec** — **`oci-runtime-spec`** governs **runtime bundles**; the engine delegates to **low-level** runtimes that **implement** it (commonly **`runc`**-class) (`DOCUMENTED`).  
- **Not** Kubernetes — orchestration is separate (`kubernetes` package).  
- **Not** identical to **containerd** — CRI stack on many nodes uses containerd; Docker Desktop bundles differ by platform (`DOCUMENTED` product docs).

## Why this system matters

- Popularized **image + registry** workflow and developer-facing container UX (`HISTORICAL` / `DOCUMENTED`).  
- Sits on **Linux kernel** isolation primitives in the dominant Linux deployment class (`DOCUMENTED`).

## What this system teaches the atlas

- Separation of **image format (OCI)** from **orchestrator** and from **host OS**.  
- Platform-specific engine implementations (Linux vs Windows containers vs macOS VM-backed).
