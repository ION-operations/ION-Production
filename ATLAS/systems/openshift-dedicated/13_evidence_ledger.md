---
atlas_package: system
system_slug: openshift-dedicated
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| osd-001 | OpenShift Dedicated offers OpenShift Container Platform clusters as a managed service on AWS or Google Cloud | DOCUMENTED | `src-redhat-osd-getting-started` | |
| osd-002 | CCS model deploys Red Hat–managed OSD in a customer-owned AWS or GCP account; supported by Red Hat SRE | DOCUMENTED | `src-redhat-osd-getting-started` | |
| osd-003 | Alternative: deploy OSD in AWS/GCP accounts owned by Red Hat | DOCUMENTED | `src-redhat-osd-getting-started` | |
| osd-004 | CNCF **k8s-conformance** includes **openshift-dedicated** under versioned paths (e.g. `v1.31/openshift-dedicated/`) | DOCUMENTED | `src-cncf-k8s-conformance` | Per-minor certification. |
| osd-005 | Substitutable vs customer-operated OpenShift Container Platform | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| osd-006 | Substitutable vs EKS-class managed Kubernetes on AWS | INFERRED | `relations.json` → `competes_with` aws-eks | |
| osd-007 | Substitutable vs AKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` azure-aks | |
| osd-008 | Substitutable vs GKE-class managed Kubernetes on GCP | INFERRED | `relations.json` → `competes_with` gcp-gke | |
| osd-009 | Substitutable vs OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| osd-010 | Substitutable vs IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| osd-011 | Substitutable vs DOKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| osd-012 | Substitutable vs Civo managed Kubernetes | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| osd-013 | Substitutable vs LKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` linode-lke | |
| osd-014 | Substitutable vs VMware TKG in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
