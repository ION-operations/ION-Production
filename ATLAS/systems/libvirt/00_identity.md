---
atlas_package: system
system_slug: libvirt
schema_version: "1.0"
last_reviewed: "2026-04-05"
evidence_grade: B
---

# libvirt — Identity

**Kind:** **Virtualization** **management** **library** **and** **daemon** **that** **configures** **and** **operates** **VMs** **(commonly** **QEMU/KVM** **on** **Linux)** **via** **a** **stable** **API** (`DOCUMENTED`, `src-libvirt-docs`, `src-libvirt-gitlab`).

## Boundaries

- **Not** **`qemu`** **alone** **—** **QEMU** **is** **the** **VMM** **/** **emulator** **binary;** **libvirt** **is** **the** **management** **layer** **that** **drives** **it.**  
- **Not** **`linux-kvm`** **alone** **—** **KVM** **is** **the** **kernel** **hypervisor** **API;** **libvirt** **composes** **KVM** **with** **QEMU** **and** **host** **policy.**  
- **Not** **`kubernetes`** **alone** **—** **Kubernetes** **orchestrates** **cluster** **workloads;** **libvirt** **may** **sit** **under** **VM** **add-ons** **such** **as** **KubeVirt** **on** **nodes.**

## Why this system matters

- **Separates** **“start** **this** **QEMU** **process”** **from** **“cluster-level** **VM** **workloads”** **—** **different** **failure** **domains** **and** **operator** **surfaces.**

## What this system teaches the atlas

**Treat** **host** **virtualization** **management** **(`libvirt`)** **as** **distinct** **from** **the** **VMM** **(`qemu`)** **and** **from** **the** **kernel** **hypervisor** **API** **(`linux-kvm`).**
