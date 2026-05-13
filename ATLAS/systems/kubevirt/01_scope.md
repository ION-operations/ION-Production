---
atlas_package: system
system_slug: kubevirt
schema_version: "1.0"
last_reviewed: "2026-04-06"
evidence_grade: B
---

# Scope

## In scope

- **KubeVirt** **CRDs,** **controllers,** **and** **documented** **architecture** **for** **VM** **workloads** **on** **Kubernetes** (`DOCUMENTED`).  
- **Composition** **with** **KVM/QEMU** **and** **libvirt-class** **node** **stacks** **at** **survey** **grain** (`INFERRED` **where** **marked**).

## Out of scope

- **Vendor** **SaaS** **control** **planes** **unless** **sourced.**  
- **Guest** **OS** **internals.**

## Versioning note

**KubeVirt** **releases** **track** **Kubernetes** **and** **QEMU** **ecosystem** **changes** (`DOCUMENTED`).
