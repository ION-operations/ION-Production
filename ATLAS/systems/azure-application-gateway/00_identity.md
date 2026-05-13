---
atlas_package: system
system_slug: azure-application-gateway
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Azure Application Gateway — Identity

**Kind:** Azure layer-7 load balancer with optional WAF and ingress patterns for AKS (`DOCUMENTED`, Microsoft Learn).

## Boundaries

- Not Azure Front Door (separate global CDN/edge product) — this package is Application Gateway grain only unless expanded later.
- Not self-hosted `nginx`.
