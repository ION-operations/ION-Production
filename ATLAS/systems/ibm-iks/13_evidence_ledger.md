---
atlas_package: system
system_slug: ibm-iks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| iks-001 | Certified, managed Kubernetes solution on IBM Cloud | DOCUMENTED | `src-ibm-iks-product` | |
| iks-002 | IBM manages the Kubernetes master; workers in client-owned infrastructure | DOCUMENTED | `src-ibm-iks-product` | FAQ excerpt on product page |
| iks-003 | Worker nodes described as single-tenant to the client | DOCUMENTED | `src-ibm-iks-product` | |
| iks-004 | Service positions Docker (OCI) containers onto compute hosts | DOCUMENTED | `src-ibm-iks-product` | |
| iks-005 | Substitutable with DOKS-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` digitalocean-doks | |
| iks-006 | Substitutable with Civo managed Kubernetes | INFERRED | `relations.json` → `competes_with` civo-kubernetes | |
| iks-007 | Substitutable with LKE-class managed Kubernetes | INFERRED | `relations.json` → `competes_with` linode-lke | |
| iks-008 | Substitutable with TKG-class customer-operated Kubernetes platform | INFERRED | `relations.json` → `competes_with` vmware-tkg | |
| iks-009 | Substitutable with Red Hat OpenShift | INFERRED | `relations.json` → `competes_with` red-hat-openshift | |
| iks-010 | Substitutable with OpenShift Dedicated | INFERRED | `relations.json` → `competes_with` openshift-dedicated | |
