---
atlas_package: system
system_slug: azure-aks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** managed Kubernetes service (`DOCUMENTED`).  
- **`competes_with` `aws-eks` / `gcp-gke`:** managed Kubernetes substitution across clouds (`INFERRED`).  
- **`competes_with` `azure-container-apps`:** Azure container hosting model substitution (`INFERRED`).  
- **`competes_with` `oci-oke`:** managed Kubernetes substitution vs OCI (`INFERRED`).  
- **`competes_with` `ibm-iks`:** managed Kubernetes substitution vs IBM Cloud (`INFERRED`).  
- **`competes_with` `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `vmware-tkg` / `red-hat-openshift` / `openshift-dedicated`:** managed Kubernetes substitution vs regional providers (`INFERRED`).  
- **`integrates_with` `azure-aci`:** virtual nodes / pods on ACI (`DOCUMENTED`).  
- **`depends_on` `linux-kernel`:** common node OS; Windows pools also exist (`INFERRED`).
