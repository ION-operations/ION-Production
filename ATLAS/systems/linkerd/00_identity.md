---
atlas_package: system
system_slug: linkerd
schema_version: "1.0"
last_reviewed: "2026-04-05"
evidence_grade: B
---

# Linkerd — Identity

**Kind:** Lightweight Kubernetes-native **service mesh** with its own **data-plane proxy** (not Envoy-centric in Linkerd2 architecture) (`DOCUMENTED`, Linkerd docs).

## Boundaries

- Not Kubernetes itself — cluster add-on.
- Not Istio — different control plane and proxy; see `competes_with` edge to `istio`.
