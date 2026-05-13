---
atlas_package: system
system_slug: emissary-ingress
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# Emissary-Ingress — Identity

**Kind:** Kubernetes ingress controller and API gateway built on Envoy (`DOCUMENTED`, upstream repository and CNCF project materials).

## Boundaries

- Not raw Envoy — control plane and CRDs around Envoy data plane.
- Not Traefik — different configuration model; see `competes_with` where substitutable.
