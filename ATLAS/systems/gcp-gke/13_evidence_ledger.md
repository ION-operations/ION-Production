---
atlas_package: system
system_slug: gcp-gke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| gke-001 | GKE clusters consist of GCE VM nodes | DOCUMENTED | `src-gcp-gke-overview` | |
| gke-002 | Workloads use Kubernetes API (pods, scaling, monitoring) | DOCUMENTED | `src-gcp-gke-overview` | |
| gke-003 | Google Cloud manages control plane and system components | DOCUMENTED | `src-gcp-gke-overview` | |
| gke-004 | Autopilot: Google Cloud also manages worker nodes | DOCUMENTED | `src-gcp-gke-overview` | |
| gke-005 | Standard vs Autopilot modes differ in who manages node pools | DOCUMENTED | `src-gcp-gke-overview` | |
| gke-006 | Control plane auto-upgrades tied to release channel selection | DOCUMENTED | `src-gcp-gke-overview` | |
| gke-007 | Substitutable with OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| gke-008 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| gke-009 | Substitutable with DOKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| gke-010 | Substitutable with Civo managed Kubernetes | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| gke-011 | Substitutable with LKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` linode-lke | |
| gke-012 | Substitutable with TKG-class customer-operated Kubernetes platform | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| gke-013 | Substitutable with Red Hat OpenShift | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| gke-014 | Substitutable with OpenShift Dedicated | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
