---
atlas_package: system
system_slug: consul
schema_version: "1.0"
last_reviewed: "2026-04-06"
evidence_grade: B
---

# HashiCorp Consul — Identity

**Kind:** Distributed service identity and networking — service catalog, health checks, KV, and Consul Connect (mTLS service-to-service) (`DOCUMENTED`, HashiCorp Consul docs).

## Boundaries

- Not Kubernetes — often runs on VMs or K8s as a workload.
- Not identical to `istio` — different control/data model; overlaps in *service mesh* problem space.
