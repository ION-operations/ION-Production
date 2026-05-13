---
atlas_package: system
system_slug: azure-container-apps
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Serverless container platform framing; KEDA tie-in (`aca-001`, `aca-002`).  
- Kubernetes substrate without kube API access; Kubernetes-style features (`aca-003`, `aca-004`).  
- Registry sources (`aca-005`).

## INFERRED

- Cross-vendor substitution vs ECS-class platforms (`relations.json`).  
- **Azure ACI** substitution (`aca-006`).

## Open questions

- Optional **`azure-container-instances`** package if “building block” comparisons expand.  
- Pin **networking** doc set for production-grade claims.

## Forbidden until sourced

- Undocumented multi-tenant isolation implementation.  
- “Always cheaper than AKS” — evaluative.
