---
atlas_package: system
system_slug: envoy
schema_version: "1.0"
last_reviewed: "2026-04-04"
evidence_grade: B
---

# Envoy Proxy — Identity

**Kind:** **High**-**performance** **edge/middle** **proxy** **(HTTP/gRPC/TCP)** **with** **xDS** **dynamic** **configuration** **culture** (`DOCUMENTED`, Envoy docs).

## Boundaries

- **Not** **a** **service** **mesh** **control** **plane** **alone** — **see** **`istio`.**  
- **Not** **Kubernetes** **—** **often** **deployed** **as** **DaemonSet** **/** **sidecar.**
