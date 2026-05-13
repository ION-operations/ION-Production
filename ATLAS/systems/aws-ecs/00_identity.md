---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Amazon Elastic Container Service (ECS) — Identity

**Kind:** **Fully managed container orchestration** on AWS: scheduler/controller plus documented capacity models (EC2, Fargate, ECS Anywhere, ECS Managed Instances) (`DOCUMENTED`, `src-aws-ecs-developer-guide`).

## Boundaries

- **Not** open-source Kubernetes — different API, ownership, and integration surface (`DOCUMENTED` / comparative).  
- **Not** a portable description of AWS internal control-plane implementation — treat as **UNKNOWN** unless AWS publishes explicit internals.

## Why this system matters

- Canonical example of **vendor-managed orchestrator** vs self-managed control planes (`DOCUMENTED`).  
- Stress-tests atlas language around **capacity vs controller vs provisioning** layers (`DOCUMENTED` terminology in AWS docs).

## What this system teaches the atlas

- Compare **managed scheduler** contracts to `kubernetes` reconciliation APIs in `comparative/orchestration_models.md`.
