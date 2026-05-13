---
atlas_package: system
system_slug: red-hat-openshift
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** OCP documented as Kubernetes-core platform (`DOCUMENTED`).  
- **`integrates_with` `openshift-dedicated`:** Red Hat documents OSD as **OCP clusters as a managed service** (`DOCUMENTED`).  
- **`competes_with` `openshift-dedicated`:** customer-operated OCP vs Red Hat–managed OSD (`INFERRED`).  
- **`competes_with` `vmware-tkg` / `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `aws-eks` / `azure-aks` / `gcp-gke` / `oci-oke` / `ibm-iks`:** platform substitution in **some** enterprise / hybrid vs public-cloud footprints (`INFERRED`).  
- **`depends_on` `linux-kernel`:** typical OpenShift nodes (`INFERRED`).
