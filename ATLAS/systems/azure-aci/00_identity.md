---
atlas_package: system
system_slug: azure-aci
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Azure Container Instances (ACI) — Identity

**Kind:** **Serverless container host** on Azure to run **Linux or Windows** containers **without managing VMs** and **without adopting a higher-level service** (`DOCUMENTED`, `src-azure-aci-overview`). Microsoft positions ACI as a **lower-level building block** compared to services like Azure Container Apps (`DOCUMENTED`, Microsoft container comparison article — cross-ref in `azure-container-apps` package).

## Boundaries

- **Not** a full **Kubernetes** cluster product — use **azure-aks** for Kubernetes API (`DOCUMENTED` ACI overview virtual-nodes section + comparison doc pattern).  
- **Not** **azure-container-apps** — different operational abstraction (`INFERRED` / Microsoft comparison framing).

## Why this system matters

- **Fast/single-command** container starts; **Hyper-V isolation** claims (`DOCUMENTED`).  
- **AKS virtual nodes** integration path (`DOCUMENTED`).

## What this system teaches the atlas

- Contrast **orchestrated platform** vs **schedulable building block** in `comparative/orchestration_models.md`.
