---
atlas_package: system
system_slug: azure-aks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed Kubernetes framing; Azure-managed control plane; CNCF certification callout (`aks-001`–`aks-004`).  
- **ACI virtual nodes** integration (`aks-007`).

## INFERRED

- Multi-cloud substitution vs other managed Kubernetes offerings (`relations.json`).  
- **Azure Container Apps** substitution (`aks-005`); **OCI OKE** substitution (`aks-006`); **IBM IKS** substitution (`aks-008`); **DigitalOcean DOKS** (`aks-009`); **Civo Kubernetes** (`aks-010`); **Akamai LKE** (`aks-011`); **VMware TKG** (`aks-012`); **Red Hat OpenShift** (`aks-013`); **OpenShift Dedicated** (`aks-014`).

## Open questions

- Pin primary operator interfaces (CLI vs portal) to a stable Microsoft Learn page set.

## Forbidden until sourced

- Azure-internal SRE playbooks or undisclosed failure domains.  
- “Always cheaper than EKS/GKE” — evaluative.
