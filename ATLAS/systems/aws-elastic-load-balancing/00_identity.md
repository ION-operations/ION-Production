---
atlas_package: system
system_slug: aws-elastic-load-balancing
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# AWS Elastic Load Balancing — Identity

**Kind:** AWS managed load balancing (Application, Network, Gateway, Classic families per AWS documentation).

## Boundaries

- Not self-hosted `envoy` or `nginx` — managed control/data plane by AWS.
- Not the Kubernetes Service `type: LoadBalancer` implementation itself — often backs that pattern on EKS (INFERRED integration).
