---
atlas_package: system
system_slug: oci-oke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Oracle Cloud Infrastructure Kubernetes Engine (OKE) — Identity

**Kind:** **Fully managed Kubernetes** on OCI: **CNCF-conformant** Kubernetes for build/deploy/scale of containerized apps (`DOCUMENTED`, `src-oci-oke-overview`).

## Boundaries

- **Not** upstream **kubernetes** — Oracle **managed service** (`DOCUMENTED`).  
- **Not** undocumented OCI control-plane layout — **UNKNOWN** at internal depth.

## Why this system matters

- Expands managed-Kubernetes atlas coverage beyond AWS/Azure/GCP (`DOCUMENTED` product facts).  
- Documents **virtual nodes vs managed vs self-managed** deployment options (`DOCUMENTED`).

## What this system teaches the atlas

- Compare **node responsibility splits** (virtual serverless vs shared vs self-managed) in `comparative/orchestration_models.md`.
