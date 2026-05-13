---
atlas_package: system
system_slug: qemu
schema_version: "1.0"
last_reviewed: "2026-04-04"
evidence_grade: B
---

# QEMU — Identity

**Kind:** **Open-source** **machine** **emulator** **and** **virtual** **machine** **monitor** **(QEMU)** **that** **can** **drive** **KVM** **on** **Linux** **hosts** **and** **provide** **broad** **device** **models** **for** **guests** (`DOCUMENTED`, `src-qemu-docs-master`, `src-qemu-repo`).

## Boundaries

- **In scope:** QEMU as a userspace VMM/emulator, KVM acceleration on Linux, virtio and VFIO integration patterns as documented.  
- **Out of scope:** Specific downstream distro packaging matrices unless ledgered per distribution.

## Why this system matters

- **Composes** **kernel** **hypervisor** **APIs** **(`linux-kvm`)** **with** **virtio,** **vhost,** **and** **VFIO** **in** **real** **deployments** **—** **distinct** **from** **each** **kernel** **facility** **alone.**  
- **Contrasts** **with** **minimal** **microVM** **VMMs** **such** **as** **`firecracker`** **(different** **scope** **and** **device** **surface).**

## What this system teaches the atlas

- **Do** **not** **collapse** **“the** **hypervisor** **ioctl** **API”** **(`linux-kvm`),** **“the** **virtio** **contract”** **(`virtio`),** **and** **“the** **userspace** **VMM** **that** **wires** **them”** **(`qemu`).**
