---
atlas_package: system
system_slug: linux-kvm
schema_version: "1.0"
last_reviewed: "2026-04-26"
evidence_grade: B
---

# Scope

## In scope

- **KVM** **kernel** **virtualization** **model** **and** **documented** **userspace** **API** **overview** (`DOCUMENTED`).  
- **Relationship** **to** **VMMs** **(e.g.** **Firecracker-class)** **on** **Linux** **as** **integration** **pattern** (`INFERRED`/`DOCUMENTED` **per** **product).**  
- **Architectural** **contrast** **with** **Linux** **namespaces** **/** **cgroups** **for** **isolation** **(survey).**

## Out of scope

- **Specific** **QEMU** **/** **libvirt** **releases** **—** **use** **those** **products’** **docs** **unless** **added** **as** **separate** **packages.**  
- **Non-Linux** **hypervisors** **—** **out** **unless** **scoped** **later.**

## Versioning note

**CPU** **features,** **KVM** **ioctls,** **and** **guest** **ABI** **details** **evolve** **with** **kernel** **and** **hardware** **generations** (`OBSERVED`).
