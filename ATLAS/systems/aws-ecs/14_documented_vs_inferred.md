---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed orchestrator framing; capacity/controller/provisioning layering (`ecs-001`, `ecs-002`).  
- Core object names and capacity options (`ecs-003`, `ecs-004`).  
- Docker named in integration overview (`ecs-005`).

## INFERRED

- Competition with self-managed Kubernetes / Nomad footprints — market and architecture pattern, not API sameness.  
- **AWS product-line** competition with EKS (`ecs-006`) — ECS vs Kubernetes-on-AWS.  
- **Cross-vendor** managed container platform class vs Azure Container Apps (`ecs-007`).

## Open questions

- Deeper task networking / IAM matrices with section-level AWS citations.

## Forbidden until sourced

- Internal AWS placement algorithms or hypervisor implementation details for Fargate.  
- “Always cheaper/better than Kubernetes” — evaluative, not structural.
