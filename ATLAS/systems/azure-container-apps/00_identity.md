---
atlas_package: system
system_slug: azure-container-apps
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Azure Container Apps — Identity

**Kind:** **Serverless container platform** on Azure for APIs, jobs, event-driven work, and microservices, with scaling tied to HTTP/events/CPU/memory/**KEDA** scalers (`DOCUMENTED`, `src-azure-container-apps-overview`). Microsoft also states it is **powered by Kubernetes** (with **no direct Kubernetes API access**) (`DOCUMENTED`, `src-azure-container-apps-compare`).

## Boundaries

- **Not** **azure-aks** — AKS exposes full Kubernetes API and cluster ownership patterns (`DOCUMENTED`, Microsoft comparison).  
- **Not** internal Azure implementation detail beyond what Microsoft publishes — **UNKNOWN** at depth.

## Why this system matters

- Shows a **managed “Kubernetes-style apps without kube-apiserver access”** pattern (`DOCUMENTED`).  
- Natural comparator to **ECS/Fargate-class** models (`INFERRED`).

## What this system teaches the atlas

- Split **Kubernetes as substrate** vs **Kubernetes as operator API** in `comparative/orchestration_models.md`.
