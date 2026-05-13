---
atlas_package: system
system_slug: openshift-dedicated
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** managed OpenShift clusters expose the Kubernetes/OpenShift API family (`DOCUMENTED` via OCP lineage).  
- **`integrates_with` `red-hat-openshift`:** Red Hat documents OSD as **OCP clusters as a managed service** (`DOCUMENTED`).  
- **`competes_with` `red-hat-openshift`:** customer-operated OCP vs Red Hat–managed OSD in procurement/ops framing (`INFERRED`).  
- **`competes_with` `aws-eks` / `azure-aks` / `gcp-gke` / `oci-oke` / `ibm-iks` / `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `vmware-tkg`:** managed Kubernetes / distribution substitution (`INFERRED`).  
- **`depends_on` `linux-kernel`:** typical worker nodes (`INFERRED`).
