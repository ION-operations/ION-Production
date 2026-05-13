---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| eks-001 | Amazon EKS is a fully managed Kubernetes service | DOCUMENTED | `src-aws-eks-user-guide` | |
| eks-002 | EKS standard: AWS manages the Kubernetes control plane | DOCUMENTED | `src-aws-eks-user-guide` | |
| eks-003 | EKS Auto Mode extends management to Kubernetes nodes (data plane) | DOCUMENTED | `src-aws-eks-user-guide` | |
| eks-004 | EKS is certified Kubernetes-conformant | DOCUMENTED | `src-aws-eks-user-guide` | |
| eks-005 | EKS installs Kubernetes APIs; controllers/components can run in EKS and be fully managed (Capabilities) | DOCUMENTED | `src-aws-eks-user-guide` | |
| eks-006 | Substitutable with AKS/GKE-class managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` azure-aks, gcp-gke | Not feature parity claim. |
| eks-007 | Substitutable with OKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` oci-oke | |
| eks-008 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| eks-009 | Substitutable with DOKS-class managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` digitalocean-doks | Not feature parity claim. |
| eks-010 | Substitutable with Civo managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| eks-011 | Substitutable with LKE-class managed Kubernetes in multi-cloud framing | INFERRED | `relations.json` → `competes_with` linode-lke | |
| eks-012 | Substitutable with TKG-class customer-operated Kubernetes platform in some footprints | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| eks-013 | Substitutable with Red Hat OpenShift in some footprints | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| eks-014 | Substitutable with OpenShift Dedicated in some footprints | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
