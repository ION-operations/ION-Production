---
atlas_package: system
system_slug: digitalocean-doks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Managed control plane** + **worker** model implied by “Kubernetes service” and operational how-tos (`DOCUMENTED` product summary).  
- **Cluster autoscaler** and **control plane firewall** features referenced in docs index/changelog (`DOCUMENTED`).

## UNKNOWN at seed depth

- etcd/apiserver placement inside DigitalOcean — not asserted.
