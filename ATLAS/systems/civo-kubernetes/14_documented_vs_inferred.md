---
atlas_package: system
system_slug: civo-kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Core service; vendor conformance language (`civo-001`, `civo-002`); ecosystem + regions (`civo-003`, `civo-004`).  
- **Artifact-level** conformance submissions for **civo** under CNCF’s versioned tree (`civo-005`; program `src-cncf-certified-kubernetes-program`).

## INFERRED

- Multi-vendor substitution vs other managed Kubernetes (`relations.json`; `civo-006`–`civo-015`).

## Open questions

- On Kubernetes minor upgrades, re-check the latest `vX.Y/civo/` directory in `k8s-conformance` before tightening marketing copy.  
- Child pages for networking/storage when comparative matrices need detail.

## Forbidden until sourced

- Civo-internal scheduling/control-plane design.  
- “Fastest Kubernetes in the world” — evaluative.
