---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Three layers** in Amazon ECS per AWS: **Capacity** (where containers run), **Controller** (deploy/manage applications on containers), **Provisioning** (console/CLI/SDK/CDK interfaces) (`DOCUMENTED`).  
- **Scheduler** manages applications as described in the developer guide (`DOCUMENTED`).

## UNKNOWN at seed depth

- Internal service decomposition (microservices behind ECS API) — not asserted.
