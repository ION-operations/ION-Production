---
atlas_package: system
system_slug: nomad
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| nom-001 | Nomad is a cluster scheduler with servers and clients | DOCUMENTED | `src-nomad-docs` | |
| nom-002 | Task drivers include Docker among other backends | DOCUMENTED | `src-nomad-docs` | |
| nom-003 | Uses Raft-based server clustering (as documented) | DOCUMENTED | `src-nomad-docs` | |
| nom-004 | Substitutable with ECS-class managed orchestrators in some deployments | INFERRED | `relations.json` → `competes_with` aws-ecs | Not API-equivalent. |
| nom-005 | Substitutable with EKS-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` aws-eks | Not API-equivalent. |
| nom-006 | Substitutable with AKS-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` azure-aks | Not API-equivalent. |
| nom-007 | Substitutable with GKE-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` gcp-gke | Not API-equivalent. |
| nom-008 | Substitutable with OKE-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` oci-oke | Not API-equivalent. |
| nom-009 | Substitutable with Azure Container Apps in some deployments | INFERRED | `relations.json` → `competes_with` azure-container-apps | Not API-equivalent. |
| nom-010 | Substitutable with IBM IKS-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` ibm-iks | Not API-equivalent. |
| nom-011 | Substitutable with Azure ACI-class hosting in narrow footprints | INFERRED | `relations.json` → `competes_with` azure-aci | Not API-equivalent. |
| nom-012 | Substitutable with DOKS-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` digitalocean-doks | Not API-equivalent. |
| nom-013 | Substitutable with Civo managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` civo-kubernetes | Not API-equivalent. |
| nom-014 | Substitutable with LKE-class managed Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` linode-lke | Not API-equivalent. |
| nom-015 | Substitutable with TKG-class Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` vmware-tkg | Not API-equivalent. |
| nom-016 | Substitutable with OpenShift-class Kubernetes in some deployments | INFERRED | `relations.json` → `competes_with` red-hat-openshift | Not API-equivalent. |
| nom-017 | Substitutable with OpenShift Dedicated in some deployments | INFERRED | `relations.json` → `competes_with` openshift-dedicated | Not API-equivalent. |
