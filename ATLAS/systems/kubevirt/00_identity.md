---
atlas_package: system
system_slug: kubevirt
schema_version: "1.0"
last_reviewed: "2026-04-06"
evidence_grade: B
---

# KubeVirt — Identity

**Kind:** **Kubernetes** **extension** **that** **adds** **virtual** **machine** **workloads** **to** **clusters** **via** **CRDs** **and** **controllers,** **running** **QEMU/KVM-class** **stacks** **on** **Linux** **nodes** (`DOCUMENTED`, `src-kubevirt-user-guide`, `src-kubevirt-github`).

## Boundaries

- **Not** **`kubernetes`** **alone** **—** **Kubernetes** **orchestrates** **workloads;** **KubeVirt** **adds** **VM** **semantics** **and** **node** **components** **distinct** **from** **default** **OCI** **pod** **sandboxes.**  
- **Not** **`libvirt`** **or** **`qemu`** **alone** **—** **those** **are** **node-local** **virtualization** **building** **blocks;** **KubeVirt** **binds** **them** **to** **the** **Kubernetes** **API.**  
- **Not** **a** **generic** **Linux** **distro** **—** **see** **`debian`**, **`rhel`**, **etc.**

## Why this system matters

- **Makes** **“VMs** **on** **Kubernetes”** **a** **first-class** **design** **pattern** **without** **pretending** **it** **is** **the** **same** **as** **plain** **container** **pods.**

## What this system teaches the atlas

**Separate** **cluster** **VM** **orchestration** **(KubeVirt)** **from** **node** **VMM** **pieces** **(QEMU)** **and** **from** **kernel** **hypervisor** **APIs** **(KVM).**
