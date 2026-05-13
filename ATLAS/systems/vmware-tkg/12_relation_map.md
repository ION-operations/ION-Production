---
atlas_package: system
system_slug: vmware-tkg
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `kubernetes`:** opinionated upstream-aligned distribution with validated binaries (`DOCUMENTED`).  
- **`competes_with` `red-hat-openshift` / `openshift-dedicated` / `digitalocean-doks` / `civo-kubernetes` / `linode-lke` / `aws-eks` / `azure-aks` / `gcp-gke` / `oci-oke` / `ibm-iks`:** Kubernetes platform substitution vs enterprise distribution, managed public/regional SKUs (`INFERRED`) in **some** footprints (hybrid / datacenter vs cloud-managed control plane).  
- **`depends_on` `linux-kernel`:** typical node OS for workload clusters (`INFERRED`).
