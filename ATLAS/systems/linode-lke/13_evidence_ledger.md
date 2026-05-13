---
atlas_package: system
system_slug: linode-lke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lke-001 | LKE is Akamai’s managed container orchestration engine built on Kubernetes | DOCUMENTED | `src-akamai-lke-techdocs` | |
| lke-002 | Through LKE you can deploy/manage containerized apps without building and maintaining your own Kubernetes cluster | DOCUMENTED | `src-akamai-lke-techdocs` | Meta/summary consistent with techdocs landing. |
| lke-003 | CNCF **k8s-conformance** repo includes **linode** submissions under versioned paths (e.g. `v1.31/linode/`) | DOCUMENTED | `src-cncf-k8s-conformance` | Certification is **per Kubernetes minor**; follow current tree. |
| lke-004 | Substitutable with DOKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| lke-005 | Substitutable with Civo managed Kubernetes | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| lke-006 | Substitutable with EKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` aws-eks | |
| lke-007 | Substitutable with AKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` azure-aks | |
| lke-008 | Substitutable with GKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` gcp-gke | |
| lke-009 | Substitutable with OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| lke-010 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| lke-011 | Substitutable with TKG-class customer-operated Kubernetes platform in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| lke-012 | Substitutable with Red Hat OpenShift in some footprints | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| lke-013 | Substitutable with OpenShift Dedicated in some footprints | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
