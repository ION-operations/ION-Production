---
atlas_package: system
system_slug: cilium
schema_version: "1.0"
last_reviewed: "2026-04-05"
evidence_grade: B
---

# Cilium — Identity

**Kind:** **Linux** networking and security using **eBPF**, commonly as **Kubernetes CNI** with optional **Gateway** / **mesh** features (`DOCUMENTED`, Cilium docs).

## Boundaries

- Not a pure L7-only sidecar mesh clone of Istio — different dataplane (eBPF + optional Envoy where documented).
- Not the Linux kernel — builds on `linux-kernel` and `ebpf`.
