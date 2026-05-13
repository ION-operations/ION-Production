---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed Kubernetes framing; standard vs Auto Mode; conformance claim (`eks-001`–`eks-004`).  
- Capabilities / managed controllers description at overview-linked depth (`eks-005`).

## INFERRED

- **Product-line competition** with ECS for greenfield AWS container platforms — not API equivalence.  
- **Multi-cloud managed Kubernetes** substitution vs AKS/GKE (`eks-006`), OCI OKE (`eks-007`), IBM IKS (`eks-008`), DigitalOcean DOKS (`eks-009`), Civo Kubernetes (`eks-010`), Akamai LKE (`eks-011`), VMware TKG (`eks-012`), Red Hat OpenShift (`eks-013`), and OpenShift Dedicated (`eks-014`).

## Open questions

- Deeper CRI default matrix per AMI/launch type with pinned AWS pages.  
- Explicit `eks-anywhere` sub-package if hybrid claims multiply.

## Forbidden until sourced

- Undocumented control-plane internals or etcd hosting topology inside AWS.  
- “Always cheaper than self-managed Kubernetes” — evaluative.
