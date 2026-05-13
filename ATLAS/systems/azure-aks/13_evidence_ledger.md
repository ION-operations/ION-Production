---
atlas_package: system
system_slug: azure-aks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| aks-001 | AKS is a managed Kubernetes service for containerized applications | DOCUMENTED | `src-azure-aks-intro` | |
| aks-002 | Azure creates/configures control plane when you create a cluster; Azure manages the control plane | DOCUMENTED | `src-azure-aks-intro` | |
| aks-003 | You pay for AKS nodes running applications (control plane framing per intro) | DOCUMENTED | `src-azure-aks-intro` | Pricing detail: follow Azure pricing pages. |
| aks-004 | AKS is CNCF-certified (per Microsoft Learn note) | DOCUMENTED | `src-azure-aks-intro` | |
| aks-005 | Substitutable with Container Apps for Azure container platforms without full kube API | INFERRED | `relations.json` → `competes_with` azure-container-apps | Microsoft documents differentiation in compare article. |
| aks-006 | Substitutable with OKE-class managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` oci-oke | |
| aks-007 | Virtual nodes can run AKS pods as Azure Container Instances container groups | DOCUMENTED | `relations.json` → `integrates_with` azure-aci; `systems/azure-aci/sources.yaml` | |
| aks-008 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| aks-009 | Substitutable with DOKS-class managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| aks-010 | Substitutable with Civo managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| aks-011 | Substitutable with LKE-class managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` linode-lke | |
| aks-012 | Substitutable with TKG-class customer-operated Kubernetes platform in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| aks-013 | Substitutable with Red Hat OpenShift in some footprints | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| aks-014 | Substitutable with OpenShift Dedicated in some footprints | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
