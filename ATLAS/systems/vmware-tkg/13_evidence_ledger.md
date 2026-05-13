---
atlas_package: system
system_slug: vmware-tkg
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| tkg-001 | TKG makes Kubernetes available as a utility; operators/developers create/manage clusters declaratively; keep clusters version-compatible with upstream Kubernetes | DOCUMENTED | `src-broadcom-tkg-about` | |
| tkg-002 | TKG deploys clusters using opinionated open-source Kubernetes configuration supported by VMware; validated component binaries; packaged networking, authentication, ingress, logging | DOCUMENTED | `src-broadcom-tkg-about` | |
| tkg-003 | TKG uses a management cluster; client CLI or UI requests executed with Cluster API | DOCUMENTED | `src-broadcom-tkg-about` | |
| tkg-004 | CNCF **k8s-conformance** includes **vmware-tanzu-kubernetes-grid** under versioned paths (e.g. `v1.31/vmware-tanzu-kubernetes-grid/`) | DOCUMENTED | `src-cncf-k8s-conformance` | Per-minor certification; follow current tree. |
| tkg-005 | Substitutable operations model vs DigitalOcean DOKS in some footprints | INFERRED | `relations.json` → `competes_with` digitalocean-doks | Not API-equivalent. |
| tkg-006 | Substitutable vs Civo managed Kubernetes in some footprints | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| tkg-007 | Substitutable vs Akamai LKE in some footprints | INFERRED | `relations.json` → `competes_with` linode-lke | |
| tkg-008 | Substitutable vs EKS-class managed Kubernetes in some footprints | INFERRED | `relations.json` → `competes_with` aws-eks | |
| tkg-009 | Substitutable vs AKS-class managed Kubernetes in some footprints | INFERRED | `relations.json` → `competes_with` azure-aks | |
| tkg-010 | Substitutable vs GKE-class managed Kubernetes in some footprints | INFERRED | `relations.json` → `competes_with` gcp-gke | |
| tkg-011 | Substitutable vs OKE-class managed Kubernetes in some footprints | INFERRED | `relations.json` → `competes_with` oci-oke | |
| tkg-012 | Substitutable vs IBM IKS-class managed Kubernetes in some footprints | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| tkg-013 | Substitutable vs Red Hat OpenShift in some enterprise footprints | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| tkg-014 | Substitutable vs OpenShift Dedicated in some footprints | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
