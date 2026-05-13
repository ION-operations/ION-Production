---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** node OS foundation (`DOCUMENTED`).  
- **`integrates_with` `systemd`:** common service packaging (`INFERRED` edge).  
- **`integrates_with` `docker`:** ecosystem overlap; CRI implementations vary (`DOCUMENTED`).  
- **`integrates_with` `containerd`:** common CRI runtime (`DOCUMENTED`).  
- **`integrates_with` `cri-o`:** alternative CRI runtime (`DOCUMENTED`).  
- **`competes_with` `nomad`:** orchestrator substitution class (`INFERRED`).  
- **`competes_with` `aws-ecs`:** managed orchestrator substitution (`INFERRED`).  
- **`competes_with` `apache-mesos`:** historical parallel (`HISTORICAL`).  
- **`integrates_with` `aws-eks`:** managed conformant Kubernetes offering on AWS (`DOCUMENTED`).  
- **`integrates_with` `azure-aks`:** managed Kubernetes on Azure (`DOCUMENTED`).  
- **`integrates_with` `gcp-gke`:** managed Kubernetes on Google Cloud (`DOCUMENTED`).  
- **`integrates_with` `azure-container-apps`:** Kubernetes-powered Azure surface without direct kube API (`DOCUMENTED`).  
- **`integrates_with` `oci-oke`:** CNCF-conformant managed Kubernetes on OCI (`DOCUMENTED`).  
- **`integrates_with` `ibm-iks`:** IBM certified managed Kubernetes (`DOCUMENTED`).  
- **`integrates_with` `azure-aci`:** AKS virtual nodes can back Kubernetes pods on ACI (`DOCUMENTED`).  
- **`integrates_with` `digitalocean-doks`:** DigitalOcean managed Kubernetes with managed control plane (`DOCUMENTED`).  
- **`integrates_with` `civo-kubernetes`:** Civo managed Kubernetes; CNCF conformance language in vendor docs (`DOCUMENTED`).  
- **`integrates_with` `linode-lke`:** Akamai LKE managed Kubernetes built on Kubernetes (`DOCUMENTED`).  
- **`integrates_with` `vmware-tkg`:** TKG as VMware/Broadcom-documented Kubernetes distribution (Cluster API management cluster model) (`DOCUMENTED`).  
- **`integrates_with` `red-hat-openshift`:** OCP as Red Hat–documented Kubernetes-core enterprise platform (`DOCUMENTED`).  
- **`integrates_with` `openshift-dedicated`:** Red Hat managed OpenShift (OCP clusters) on AWS/GCP (`DOCUMENTED`).
