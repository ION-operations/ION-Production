---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| k8s-001 | Declarative API + reconciling controllers | DOCUMENTED | `src-kubernetes-docs` | |
| k8s-002 | kubelet uses CRI to manage containers | DOCUMENTED | `src-kubernetes-docs` | |
| k8s-003 | CNI standardizes pod networking plugins | DOCUMENTED | `std-cni` | |
| k8s-004 | RBAC authorizes API actions | DOCUMENTED | `src-kubernetes-docs` | |
| k8s-005 | Substitutable with Nomad-class orchestrators in some deployments | INFERRED | `relations.json` → `competes_with` nomad | Market / ops pattern; not an API relationship. |
| k8s-006 | Substitutable with AWS ECS for AWS-centric container ops | INFERRED | `relations.json` → `competes_with` aws-ecs | Not API-equivalent. |
| k8s-007 | Historical overlap with Mesos-era cluster management | HISTORICAL | `relations.json` → `competes_with` apache-mesos | Mesos retired; discourse-era comparison. |
| k8s-008 | Amazon EKS runs Kubernetes-conformant clusters (managed offering relationship) | DOCUMENTED | `relations.json` → `integrates_with` aws-eks; `systems/aws-eks/sources.yaml` | Cross-package AWS user guide. |
| k8s-009 | Azure AKS is a managed Kubernetes service (managed offering relationship) | DOCUMENTED | `relations.json` → `integrates_with` azure-aks; `systems/azure-aks/sources.yaml` | Cross-package Microsoft Learn. |
| k8s-010 | Google GKE provides Kubernetes clusters with Google-managed control plane (managed offering relationship) | DOCUMENTED | `relations.json` → `integrates_with` gcp-gke; `systems/gcp-gke/sources.yaml` | Cross-package Google Cloud docs. |
| k8s-011 | Azure Container Apps is powered by Kubernetes (no direct Kubernetes API access) | DOCUMENTED | `relations.json` → `integrates_with` azure-container-apps; `systems/azure-container-apps/sources.yaml` | Microsoft Learn compare article. |
| k8s-012 | Oracle OKE runs CNCF-conformant Kubernetes (managed offering relationship) | DOCUMENTED | `relations.json` → `integrates_with` oci-oke; `systems/oci-oke/sources.yaml` | Oracle OCI documentation. |
| k8s-013 | IBM Cloud Kubernetes Service is a certified managed Kubernetes offering | DOCUMENTED | `relations.json` → `integrates_with` ibm-iks; `systems/ibm-iks/sources.yaml` | IBM product page. |
| k8s-014 | AKS virtual nodes can run Kubernetes pods as ACI container groups | DOCUMENTED | `relations.json` → `integrates_with` azure-aci; `systems/azure-aci/sources.yaml` | Microsoft Learn ACI overview. |
| k8s-015 | DigitalOcean Kubernetes (DOKS) is a managed Kubernetes service with managed control plane | DOCUMENTED | `relations.json` → `integrates_with` digitalocean-doks; `systems/digitalocean-doks/sources.yaml` | DigitalOcean product docs. |
| k8s-016 | Civo documents managed Kubernetes as CNCF-certified conformant | DOCUMENTED | `relations.json` → `integrates_with` civo-kubernetes; `systems/civo-kubernetes/sources.yaml` | See `civo-002` / `civo-005` in `systems/civo-kubernetes/13_evidence_ledger.md` for vendor + CNCF artifact cross-links. |
| k8s-017 | Akamai LKE is a managed Kubernetes offering built on Kubernetes | DOCUMENTED | `relations.json` → `integrates_with` linode-lke; `systems/linode-lke/sources.yaml` | Akamai Cloud techdocs LKE hub. |
| k8s-018 | VMware Tanzu Kubernetes Grid is a documented Kubernetes distribution with management cluster + Cluster API | DOCUMENTED | `relations.json` → `integrates_with` vmware-tkg; `systems/vmware-tkg/sources.yaml` | Broadcom TKG about hub. |
| k8s-019 | Red Hat documents OpenShift Container Platform with Kubernetes as a core component and Kubernetes API access to the cluster | DOCUMENTED | `relations.json` → `integrates_with` red-hat-openshift; `systems/red-hat-openshift/sources.yaml` | OCP getting started Kubernetes overview. |
| k8s-020 | Red Hat documents OpenShift Dedicated as managed OpenShift Container Platform clusters on AWS or Google Cloud | DOCUMENTED | `relations.json` → `integrates_with` openshift-dedicated; `systems/openshift-dedicated/sources.yaml` | OSD getting started (single-page). |
