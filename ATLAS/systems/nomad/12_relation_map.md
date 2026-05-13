---
atlas_package: system
system_slug: nomad
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`competes_with` `kubernetes`:** orchestrator substitution class (`INFERRED`).  
- **`integrates_with` `docker`:** Docker task driver (`DOCUMENTED`).  
- **`depends_on` `linux-kernel`:** typical agent OS (`INFERRED`).  
- **`competes_with` `aws-ecs`:** orchestrator substitution class (`INFERRED`).  
- **`competes_with` `aws-eks`:** managed Kubernetes on AWS as alternative orchestrator surface (`INFERRED`).  
- **`competes_with` `azure-aks` / `gcp-gke` / `oci-oke` / `ibm-iks` / `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `vmware-tkg` / `red-hat-openshift` / `openshift-dedicated`:** managed Kubernetes on other clouds (`INFERRED`).  
- **`competes_with` `azure-container-apps`:** Azure serverless container surface as alternative (`INFERRED`).  
- **`competes_with` `azure-aci`:** ACI-class container hosting as narrow alternative (`INFERRED`).
