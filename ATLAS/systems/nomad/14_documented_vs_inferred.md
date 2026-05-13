---
atlas_package: system
system_slug: nomad
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Core topology; Docker driver (`nom-001`, `nom-002`); Raft note (`nom-003`).

## INFERRED

- Kubernetes competition; Linux-first deployment bias.  
- ECS-class managed orchestrator substitution (`nom-004`).  
- EKS-class managed Kubernetes substitution (`nom-005`).  
- AKS-class managed Kubernetes substitution (`nom-006`).  
- GKE-class managed Kubernetes substitution (`nom-007`).  
- OKE-class managed Kubernetes substitution (`nom-008`).  
- Azure Container Apps substitution (`nom-009`).  
- IBM IKS substitution (`nom-010`).  
- Azure ACI substitution (`nom-011`).  
- DigitalOcean DOKS substitution (`nom-012`).  
- Civo Kubernetes substitution (`nom-013`).  
- Akamai LKE substitution (`nom-014`).  
- VMware TKG substitution (`nom-015`).  
- Red Hat OpenShift substitution (`nom-016`).  
- OpenShift Dedicated substitution (`nom-017`).

## Open questions

- Add separate `consul` / `vault` packages if adjacency claims multiply.

## Forbidden until sourced

- “Simpler than Kubernetes in all cases” — evaluative, not structural.
