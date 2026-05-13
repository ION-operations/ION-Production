---
atlas_package: system
system_slug: digitalocean-doks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** managed control plane Kubernetes service (`DOCUMENTED`).  
- **`competes_with` `aws-eks` / `azure-aks` / `gcp-gke` / `oci-oke` / `ibm-iks` / `civo-kubernetes` / `linode-lke` / `vmware-tkg` / `red-hat-openshift` / `openshift-dedicated`:** managed Kubernetes substitution (`INFERRED`).  
- **`depends_on` `linux-kernel`:** typical worker OS (`INFERRED`).
