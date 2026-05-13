---
atlas_package: system
system_slug: gcp-load-balancing
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Google Cloud Load Balancing — Identity

**Kind:** Google Cloud managed load balancing (global/regional, L4/L7 families per GCP docs).

## Boundaries

- Not GKE Ingress controller implementation detail — this package is the GCP LB product surface.
- Not `envoy` unless the customer runs Envoy separately.
