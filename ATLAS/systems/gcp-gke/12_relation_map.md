---
atlas_package: system
system_slug: gcp-gke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** managed Kubernetes clusters on GCE nodes (`DOCUMENTED`).  
- **`competes_with` `aws-eks` / `azure-aks` / `oci-oke` / `ibm-iks` / `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `vmware-tkg` / `red-hat-openshift` / `openshift-dedicated`:** managed Kubernetes substitution across clouds (`INFERRED`).  
- **`depends_on` `linux-kernel`:** typical node OS for Linux workloads (`INFERRED`).
