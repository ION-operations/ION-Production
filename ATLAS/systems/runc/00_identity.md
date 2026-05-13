---
atlas_package: system
system_slug: runc
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# runc — Identity

**Kind:** **Reference implementation** of the **OCI Runtime Specification** — a low-level binary that creates and runs containers from an OCI **bundle** (`DOCUMENTED`, `src-runc-repo`, `std-oci-runtime-spec`).

## Boundaries

- **Not** **`oci-runtime-spec`** — that slug is the **specification**; **`runc`** **implements** it (`DOCUMENTED`).  
- **Not** an image builder or registry client — higher layers (`containerd`, `podman`, `docker`) handle images (`DOCUMENTED`).  
- **Not** the only OCI runtime — **`crun`** and others exist (`DOCUMENTED` ecosystem); **VM**-class runtimes are a different slice (`INFERRED`).

## Why this system matters

- **Decomposes** the stack: CRI/high-level runtime → **OCI bundle** → **runc-class** process (`DOCUMENTED` pattern).  
- Ground truth for **config.json** + rootfs semantics at runtime-spec level (`DOCUMENTED`).

## What this system teaches the atlas

- “Container runtime” spans **multiple layers**; runc is the **leaf executor** in many Linux stacks.
