---
atlas_package: system
system_slug: linux-kvm
schema_version: "1.0"
last_reviewed: "2026-04-26"
evidence_grade: B
---

# Linux KVM — Identity

**Kind:** **Linux** **kernel** **subsystem** **that** **exposes** **hardware-assisted** **virtualization** **to** **userspace** **via** **the** **KVM** **API** **(e.g.** **`/dev/kvm`)** **per** **documented** **virtualization** **guides** (`DOCUMENTED`, `src-linux-kvm-kernel-docs`).

## Boundaries

- **Not** **`linux-namespaces`** **—** **namespaces** **isolate** **process** **views** **in** **one** **kernel;** **KVM** **runs** **guest** **VMs** **with** **their** **own** **kernel** **context** **(when** **configured).**  
- **Not** **`docker`** **/** **`kubernetes`** **—** **those** **are** **container** **engines/orchestrators;** **KVM** **is** **a** **hypervisor** **primitives** **surface.**  
- **Not** **`firecracker`** **—** **Firecracker** **is** **a** **VMM** **product;** **KVM** **is** **the** **kernel** **facility** **it** **uses** **on** **Linux.**

## Why this system matters

- **Clarifies** **when** **documentation** **means** **hardware** **virtualization** **(KVM)** **vs** **OS-level** **containers** **(namespaces/cgroups).**

## What this system teaches the atlas

**Separate** **KVM** **hypervisor** **ABI** **from** **container** **runtimes** **and** **from** **specific** **VMM** **implementations.**
