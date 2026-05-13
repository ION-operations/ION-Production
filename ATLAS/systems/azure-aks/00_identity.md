---
atlas_package: system
system_slug: azure-aks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Azure Kubernetes Service (AKS) — Identity

**Kind:** **Managed Kubernetes** on Azure: Azure provisions and operates the cluster **control plane**; customers pay for **nodes** running applications (`DOCUMENTED`, `src-azure-aks-intro`).

## Boundaries

- **Not** upstream **kubernetes** — this package is the **Azure product** surface (`DOCUMENTED`).  
- **Not** Azure Red Hat OpenShift, Arc-enabled Kubernetes, Container Apps, or ACI — separate products (`DOCUMENTED` table in Microsoft Learn).

## Why this system matters

- Major **hyperscaler managed Kubernetes** reference with explicit **CNCF certification** callout in Microsoft docs (`DOCUMENTED`).  
- Pairs with **aws-eks** and **gcp-gke** for multi-cloud substitution framing (`INFERRED` comparative).

## What this system teaches the atlas

- Compare **control-plane cost/ownership** claims (e.g. “no cost” control plane language) across vendors in `comparative/orchestration_models.md` — always read pricing docs for total cost.
