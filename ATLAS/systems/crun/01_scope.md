---
atlas_package: system
system_slug: crun
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **crun** as **OCI** low-level **runtime** on **Linux** — **bundle** execution, **`config.json`** consumption (`DOCUMENTED`, `src-crun-repo`).  
- **Integration** with **Podman**, **CRI-O**, **containerd** as a **selectable** runtime (`DOCUMENTED` upstream/docs).

## Out of scope

- **Windows**/**macOS** host runtimes — **crun** is **Linux**-centric (`DOCUMENTED` project scope).  
- **VM**/**Kata**-class isolation — different runtime class (`INFERRED`).

## Versioning note

Feature parity with **`runc`** and **kernel** knobs evolves per release (`INFERRED`).
