---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- Task definitions, tasks, services, clusters, and documented capacity options (`DOCUMENTED`).  
- Documented integration mentions (e.g. ECR, ELB, third-party tools named in AWS docs) (`DOCUMENTED`).

## Out of scope

- Undocumented AWS service internals, regional rollout mechanics, pricing optimization — **UNKNOWN** unless sourced.  
- Non-ECS AWS orchestrators (EKS, Batch-only deep dives) — separate packages.

## Versioning note

Feature availability is AWS-account, Region, and API-version specific (`DOCUMENTED` general pattern).
