---
atlas_package: system
system_slug: digitalocean-doks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| doks-001 | DOKS is a Kubernetes service with fully managed control plane | DOCUMENTED | `src-digitalocean-doks-product` | |
| doks-002 | High availability and autoscaling are product claims | DOCUMENTED | `src-digitalocean-doks-product` | |
| doks-003 | Integrates with standard Kubernetes toolchains and DO LBs, volumes, Droplets, API, CLI | DOCUMENTED | `src-digitalocean-doks-product` | |
| doks-004 | CNCF **k8s-conformance** repo includes **digitalocean** submissions under versioned paths (e.g. `v1.31/digitalocean/`) | DOCUMENTED | `src-cncf-k8s-conformance` | Certification is **per Kubernetes minor**; follow current tree for active versions. |
| doks-005 | Substitutable with EKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` aws-eks | |
| doks-006 | Substitutable with AKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` azure-aks | |
| doks-007 | Substitutable with GKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` gcp-gke | |
| doks-008 | Substitutable with OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| doks-009 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| doks-010 | Substitutable with Civo managed Kubernetes among regional providers | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| doks-011 | Substitutable with LKE-class managed Kubernetes among regional providers | INFERRED | `relations.json` → `competes_with` linode-lke | |
| doks-012 | Substitutable with TKG-class customer-operated Kubernetes platform in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| doks-013 | Substitutable with Red Hat OpenShift in some footprints | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| doks-014 | Substitutable with OpenShift Dedicated in some footprints | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
