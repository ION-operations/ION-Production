---
atlas_package: system
system_slug: gcp-gke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Google Kubernetes Engine (GKE) — Identity

**Kind:** **Managed Kubernetes** on Google Cloud: clusters of **Compute Engine VMs** as nodes; **Kubernetes API** for workloads; Google Cloud manages the **control plane** (and **Autopilot** manages worker nodes) (`DOCUMENTED`, `src-gcp-gke-overview`).

## Boundaries

- **Not** upstream **kubernetes** — this package is the **Google Cloud product** (`DOCUMENTED`).  
- **Not** GKE Enterprise / fleet abstractions at seed depth — expand with separate doc pins if needed.

## Why this system matters

- Reference for **Autopilot vs Standard** responsibility split (`DOCUMENTED`).  
- Pairs with **aws-eks** and **azure-aks** for managed-Kubernetes comparison (`INFERRED`).

## What this system teaches the atlas

- Compare **release channels** and **automatic control plane upgrades** claims to other vendors in `comparative/orchestration_models.md`.
