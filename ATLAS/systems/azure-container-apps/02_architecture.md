---
atlas_package: system
system_slug: azure-container-apps
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Environment** + **workload profiles** (Consumption, Dedicated, Flex) shape compute and scaling (`DOCUMENTED` in workload-profile docs; overview points to environments).  
- **Powered by Kubernetes** plus named open-source components (Dapr, KEDA, Envoy) per Microsoft (`DOCUMENTED`, `src-azure-container-apps-compare`).  
- **No direct access** to underlying Kubernetes APIs — contrast with AKS (`DOCUMENTED`).

## UNKNOWN at seed depth

- Exact multi-tenant isolation boundaries inside Microsoft-managed infrastructure — not asserted.
