---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Security and permissions

- **RBAC** for API authorization (`DOCUMENTED`).  
- **ServiceAccounts** + projected tokens for pod identity (`DOCUMENTED`).  
- **Admission webhooks** and **PSA/PSS** policies (as documented per version) (`DOCUMENTED`).  
- **Node isolation** depends on kubelet hardening + cloud provider controls (`DOCUMENTED` guides).
