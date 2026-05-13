---
atlas_package: system
system_slug: linux-vfio
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Linux VFIO — Identity

**Kind:** **Linux** **kernel** **framework** **for** **IOMMU-backed** **device** **assignment** **to** **userspace** **(VFIO)** **and** **related** **driver** **interfaces** **per** **kernel** **VFIO** **documentation** (`DOCUMENTED`, `src-linux-vfio-kernel-doc`).

## Boundaries

- **Not** **`virtio`** **alone** **—** **virtio** **is** **the** **paravirtual** **device** **model;** **VFIO** **is** **primarily** **about** **assigning** **physical** **(or** **virtualized)** **devices** **with** **IOMMU** **isolation** **to** **userspace** **/** **guests.**  
- **Not** **`linux-kvm`** **alone** **—** **KVM** **exposes** **`/dev/kvm`;** **VFIO** **exposes** **device** **containers** **and** **IOMMU** **groups** **for** **passthrough** **composition.**  
- **Not** **`linux-vhost`** **—** **vhost** **accelerates** **virtio** **queues** **on** **the** **host;** **VFIO** **addresses** **device** **ownership** **and** **DMA** **isolation** **for** **passthrough** **and** **userspace** **drivers.**

## Why this system matters

- **Separates** **“paravirtual** **I/O”** **from** **“give** **this** **PCI** **function** **to** **a** **VM** **or** **userspace** **driver”** **—** **different** **trust** **and** **failure** **modes.**

## What this system teaches the atlas

**Treat** **VFIO-mediated** **passthrough** **as** **its** **own** **kernel** **contract,** **not** **as** **virtio** **or** **KVM** **alone.**
