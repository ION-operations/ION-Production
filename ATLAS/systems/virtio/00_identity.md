---
atlas_package: system
system_slug: virtio
schema_version: "1.0"
last_reviewed: "2026-04-27"
evidence_grade: B
---

# Virtio — Identity

**Kind:** **Paravirtual** **I/O** **transport** **and** **device** **model** **(virtqueues,** **descriptors,** **feature** **bits)** **implemented** **in** **the** **Linux** **kernel** **and** **used** **by** **guests** **under** **hypervisors** **such** **as** **KVM-class** **stacks** (`DOCUMENTED`, `src-virtio-kernel-docs`).

## Boundaries

- **Not** **`linux-kvm`** **—** **KVM** **is** **the** **hypervisor** **API;** **virtio** **defines** **how** **paravirtual** **devices** **move** **work** **between** **guest** **and** **host.**  
- **Not** **`firecracker`** **—** **Firecracker** **is** **a** **VMM** **product;** **virtio** **is** **a** **device** **interface** **it** **may** **expose** **to** **guests.**  
- **Not** **raw** **PCI** **or** **emulated** **IDE** **alone** **—** **different** **device** **paths** **(survey** **boundary).**

## Why this system matters

- **Separates** **“how** **guest** **I/O** **is** **shaped”** **(virtio)** **from** **“how** **the** **VM** **runs”** **(KVM)** **and** **from** **container** **namespaces.**

## What this system teaches the atlas

**Treat** **virtio** **as** **its** **own** **law** **slice** **adjacent** **to** **hypervisors** **and** **guest** **kernels.**
