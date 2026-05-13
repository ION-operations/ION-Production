---
atlas_package: system
system_slug: oci-oke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| oke-001 | OKE is a fully-managed service for Kubernetes on OCI | DOCUMENTED | `src-oci-oke-overview` | |
| oke-002 | Uses open-source Kubernetes; CNCF conformant | DOCUMENTED | `src-oci-oke-overview` | |
| oke-003 | Deployment options include virtual nodes, managed nodes, self-managed nodes | DOCUMENTED | `src-oci-oke-overview` | |
| oke-004 | Access via Console, REST API, CLI; kubectl/Dashboard/Kubernetes API | DOCUMENTED | `src-oci-oke-overview` | |
| oke-005 | Integrates with OCI IAM, Registry, Storage, Networking | DOCUMENTED | `src-oci-oke-overview` | |
| oke-006 | Substitutable with IBM IKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` ibm-iks | |
| oke-007 | Substitutable with DOKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| oke-008 | Substitutable with Civo managed Kubernetes | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| oke-009 | Substitutable with LKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` linode-lke | |
| oke-010 | Substitutable with TKG-class customer-operated Kubernetes platform | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| oke-011 | Substitutable with Red Hat OpenShift | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| oke-012 | Substitutable with OpenShift Dedicated | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
