---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** conformant clusters; Kubernetes APIs installed/managed per AWS (`DOCUMENTED`).  
- **`competes_with` `aws-ecs`:** AWS container orchestration product pair (`INFERRED`).  
- **`competes_with` `azure-aks` / `gcp-gke` / `oci-oke` / `ibm-iks` / `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `vmware-tkg` / `red-hat-openshift` / `openshift-dedicated`:** managed Kubernetes substitution across clouds (`INFERRED`).  
- **`depends_on` `linux-kernel`:** typical Linux worker nodes (`INFERRED`).
