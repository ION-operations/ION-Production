---
atlas_package: system
system_slug: civo-kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Civo Kubernetes — Identity

**Kind:** **Managed Kubernetes** on Civo, described as **certified conformant** by **CNCF** and **fully compatible** with the wider **cloud-native ecosystem**; clusters can be created in **all Civo regions** (`DOCUMENTED`, `src-civo-kubernetes-docs`).

## Boundaries

- **Not** upstream **kubernetes** — Civo **managed service** (`DOCUMENTED`).  
- **Not** undocumented multi-tenant internals — **UNKNOWN** at depth.

## Why this system matters

- Example of **regional Kubernetes-as-a-service** with explicit **conformance** language (`DOCUMENTED`).  
- Operator paths include **web UI**, **Civo CLI**, and **Terraform** examples (`DOCUMENTED`).

## What this system teaches the atlas

- Compare **conformance certification** claims across vendors in `comparative/orchestration_models.md`.
