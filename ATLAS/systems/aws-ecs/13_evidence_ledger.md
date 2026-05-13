---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| ecs-001 | ECS is a fully managed container orchestration service | DOCUMENTED | `src-aws-ecs-developer-guide` | |
| ecs-002 | Layers: capacity, controller, provisioning | DOCUMENTED | `src-aws-ecs-developer-guide` | |
| ecs-003 | Components include task definition, cluster, task, service | DOCUMENTED | `src-aws-ecs-developer-guide` | |
| ecs-004 | Capacity options include EC2, Fargate, on-premises (ECS Anywhere), ECS Managed Instances | DOCUMENTED | `src-aws-ecs-developer-guide` | |
| ecs-005 | Documentation names Docker among third-party integrations | DOCUMENTED | `src-aws-ecs-developer-guide` | |
| ecs-006 | AWS product-line substitution framing vs EKS | INFERRED | `relations.json` → `competes_with` aws-eks | Not API-equivalent to Kubernetes. |
| ecs-007 | Cross-vendor substitution framing vs Azure Container Apps | INFERRED | `relations.json` → `competes_with` azure-container-apps | Not API-equivalent. |
