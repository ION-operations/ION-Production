---
atlas_package: system
system_slug: gcp-gke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Node/control plane split; Autopilot vs Standard; upgrade channel pattern (`gke-001`–`gke-006`).

## INFERRED

- Multi-cloud substitution vs EKS/AKS/OKE/IBM IKS/DigitalOcean DOKS/Civo Kubernetes/Akamai LKE/VMware TKG/Red Hat OpenShift/OpenShift Dedicated (`relations.json`; `gke-007`–`gke-014`).

## Open questions

- Pin **GKE SLA** page if uptime/SLO claims become package-critical.  
- Separate **Anthos / fleet** package if multi-cluster governance claims multiply.

## Forbidden until sourced

- Google-internal scheduling or control-plane failover internals.  
- Benchmark superiority claims without cited methodology.
