---
atlas_package: system
system_slug: ibm-iks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# IBM Cloud Kubernetes Service (IKS) — Identity

**Kind:** **Certified, managed Kubernetes** on IBM Cloud: IBM **operates and manages the Kubernetes master**; **worker nodes** are provisioned into **customer-owned infrastructure** and described as **single-tenant** to the client (`DOCUMENTED`, `src-ibm-iks-product`).

## Boundaries

- **Not** upstream **kubernetes** — IBM **managed service** surface (`DOCUMENTED`).  
- **Not** Red Hat OpenShift on IBM Cloud — separate product line (`DOCUMENTED` related-products section).

## Why this system matters

- Completes a **major-vendor managed Kubernetes** row beyond hyperscalers in the atlas (`DOCUMENTED` / comparative).  
- Highlights **master vs worker responsibility** language IBM publishes (managed master; customer workers) (`DOCUMENTED`).

## What this system teaches the atlas

- Compare **tenant isolation** claims (single-tenant workers) to other vendors’ shared/managed node models in `comparative/orchestration_models.md`.
