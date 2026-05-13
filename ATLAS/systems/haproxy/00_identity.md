---
atlas_package: system
system_slug: haproxy
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# HAProxy — Identity

**Kind:** High-performance TCP/HTTP load balancer and proxy (`DOCUMENTED`, HAProxy documentation).

## Boundaries

- Not Kubernetes — though HAProxy Ingress Controller and similar patterns exist (INFERRED deployment).
- Not Envoy — different implementation; overlapping edge/L7 deployment class.
