---
atlas_package: system
system_slug: vmware-tkg
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Product purpose, upstream alignment, validated binaries, packaged services (`tkg-001`, `tkg-002`).  
- **Management cluster + Cluster API** execution model (`tkg-003`).  
- **Conformance artifact path** name in CNCF repo (`tkg-004`; program `src-cncf-certified-kubernetes-program`).

## INFERRED

- Substitution vs **Red Hat OpenShift**, **OpenShift Dedicated**, and **public/regional managed Kubernetes** SKUs in procurement/ops framing (`tkg-005`–`tkg-014`) — not mutual exclusion.  
- **Linux-class nodes** typical on workload clusters (`depends_on` `linux-kernel` in `relations.json`).

## Open questions

- Separate package for **TKG Integrated Edition** if claims fork from standalone TKG.  
- Pin **air-gapped** reference architecture only when atlas needs offline supply-chain edges.

## Forbidden until sourced

- Undocumented Broadcom/VMware control-plane internals.  
- “Always cheaper than EKS” — evaluative.
