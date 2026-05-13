---
atlas_package: system
system_slug: civo-kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| civo-001 | Managed Kubernetes is a core Civo service | DOCUMENTED | `src-civo-kubernetes-docs` | |
| civo-002 | Civo documents managed Kubernetes as **CNCF-certified** conformant; CNCF runs the Certified Kubernetes program and publishes open conformance submissions | DOCUMENTED | `src-civo-kubernetes-docs`; `src-cncf-certified-kubernetes-program`; `src-cncf-k8s-conformance` | **Per-minor Kubernetes:** confirm current certification under `vX.Y/civo/` in `k8s-conformance` when upgrading claims. |
| civo-003 | Fully compatible with wider cloud-native ecosystem (Civo claim) | DOCUMENTED | `src-civo-kubernetes-docs` | Marketing-level; narrow for production claims. |
| civo-004 | Clusters can be created in all Civo regions | DOCUMENTED | `src-civo-kubernetes-docs` | |
| civo-005 | CNCF **k8s-conformance** repo includes **civo** submissions under versioned paths (e.g. `v1.31/civo/`) | DOCUMENTED | `src-cncf-k8s-conformance` | Corroborates vendor conformance framing (`civo-002`) at artifact level. |
| civo-006 | Substitutable with DOKS-class managed Kubernetes among regional providers | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| civo-007 | Substitutable with EKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` aws-eks | |
| civo-008 | Substitutable with AKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` azure-aks | |
| civo-009 | Substitutable with GKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` gcp-gke | |
| civo-010 | Substitutable with OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| civo-011 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| civo-012 | Substitutable with LKE-class managed Kubernetes among regional providers | INFERRED | `relations.json` → `competes_with` linode-lke | |
| civo-013 | Substitutable with TKG-class customer-operated Kubernetes platform in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| civo-014 | Substitutable with Red Hat OpenShift in some footprints | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| civo-015 | Substitutable with OpenShift Dedicated in some footprints | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
