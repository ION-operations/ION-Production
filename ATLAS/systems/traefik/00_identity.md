---
atlas_package: system
system_slug: traefik
schema_version: "1.0"
last_reviewed: "2026-04-06"
evidence_grade: B
---

# Traefik — Identity

**Kind:** Cloud-native HTTP reverse proxy and ingress controller with dynamic configuration (`DOCUMENTED`, Traefik docs).

## Boundaries

- Not a full service mesh control plane like `istio` — ingress / edge routing focus (though ecosystem extends).
- Not Envoy — different implementation; see `competes_with` where deployments substitute.
