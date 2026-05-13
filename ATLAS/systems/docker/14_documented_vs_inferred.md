---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Documented vs inferred

## DOCUMENTED

- Daemon/client model; Linux primitives; OCI role (`dkr-001`–`dkr-003`).  
- ECS doc-level integration mention (`dkr-005`).  
- Azure Container Apps registry mention (`dkr-006`).  
- Azure Container Instances registry mention (`dkr-007`).

## INFERRED

- systemd unit packaging prevalence.

## OBSERVED

- Local `docker version` / API version matrix — record when needed.

## Open questions

- Pin Engine architecture diagram revision for containerd/runc placement details.

## Forbidden until sourced

- “Docker runs containers natively on macOS” without VM caveat — incorrect for Desktop class.
