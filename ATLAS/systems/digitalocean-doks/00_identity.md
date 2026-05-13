---
atlas_package: system
system_slug: digitalocean-doks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# DigitalOcean Kubernetes (DOKS) — Identity

**Kind:** **Kubernetes service** with a **fully managed control plane**, **high availability**, and **autoscaling**; integrates with **standard Kubernetes toolchains** and DigitalOcean load balancers, volumes, Droplets (CPU/GPU), API, and CLI (`DOCUMENTED`, `src-digitalocean-doks-product`).

## Boundaries

- **Not** upstream **kubernetes** — DigitalOcean **managed service** (`DOCUMENTED`).  
- **Not** undocumented control-plane internals — **UNKNOWN** at depth.

## Why this system matters

- Reference **developer/SMB-oriented** managed Kubernetes distinct from hyperscaler-first narratives (`INFERRED` market framing only).  
- Shows **product-surface integration** claims (LBs, volumes, `doctl`) at doc index level (`DOCUMENTED`).

## What this system teaches the atlas

- Compare **regional provider** Kubernetes SKUs to global hyperscalers in `comparative/orchestration_models.md`.
