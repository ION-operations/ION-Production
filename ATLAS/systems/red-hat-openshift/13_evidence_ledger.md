---
atlas_package: system
system_slug: red-hat-openshift
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| ocp-001 | OpenShift Container Platform is for developing/running containerized applications; Kubernetes is a core component | DOCUMENTED | `src-redhat-ocp-kubernetes-overview` | |
| ocp-002 | API to an OpenShift cluster is **100% Kubernetes**; workloads run the same as on other Kubernetes; OCP adds enterprise-ready enhancements | DOCUMENTED | `src-redhat-ocp-kubernetes-overview` | Vendor copy; treat “100%” as API-surface claim, not feature parity with every distro. |
| ocp-003 | `oc` is compatible with `kubectl`; Kubernetes API fully accessible within OCP | DOCUMENTED | `src-redhat-ocp-kubernetes-overview` | |
| ocp-004 | Red Hat documents extending containerized apps beyond a single cloud to on-premise and multi-cloud with OCP | DOCUMENTED | `src-redhat-ocp-kubernetes-overview` | |
| ocp-005 | CNCF **k8s-conformance** includes **openshift** submissions under versioned paths (e.g. `v1.31/openshift/`) | DOCUMENTED | `src-cncf-k8s-conformance` | Per-minor certification. |
| ocp-006 | Substitutable Kubernetes platform vs VMware TKG in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| ocp-007 | Substitutable vs DOKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| ocp-008 | Substitutable vs Civo managed Kubernetes | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| ocp-009 | Substitutable vs LKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` linode-lke | |
| ocp-010 | Substitutable vs EKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` aws-eks | |
| ocp-011 | Substitutable vs AKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` azure-aks | |
| ocp-012 | Substitutable vs GKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` gcp-gke | |
| ocp-013 | Substitutable vs OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| ocp-014 | Substitutable vs IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| ocp-015 | OpenShift Dedicated offers OCP clusters as a managed service (product family link) | DOCUMENTED | `relations.json` → `integrates_with` openshift-dedicated; `systems/openshift-dedicated/sources.yaml` | Cross-package OSD getting started. |
| ocp-016 | Substitutable vs Red Hat OpenShift Dedicated managed SKU | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
