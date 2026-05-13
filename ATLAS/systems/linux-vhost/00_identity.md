---
atlas_package: system
system_slug: linux-vhost
schema_version: "1.0"
last_reviewed: "2026-04-28"
evidence_grade: B
---

# Linux vhost — Identity

**Kind:** **Linux** **kernel** **framework** **that** **implements** **virtio** **device** **backends** **in** **kernel** **space** **(and** **coordinates** **with** **userspace** **vhost-user** **peers** **where** **configured)** **per** **kernel** **vhost** **documentation** (`DOCUMENTED`, `src-linux-vhost-kernel-doc`).

## Boundaries

- **Not** **`virtio`** **alone** **—** **virtio** **defines** **the** **guest-visible** **device** **contract;** **vhost** **is** **the** **host-side** **acceleration** **path.**  
- **Not** **`linux-kvm`** **alone** **—** **KVM** **is** **the** **hypervisor** **API;** **vhost** **is** **about** **how** **I/O** **is** **handled** **on** **the** **host** **for** **virtio** **devices.**  
- **Not** **a** **container** **runtime** **—** **see** **`docker`**, **`kubernetes`.**

## Why this system matters

- **Explains** **why** **“virtio** **in** **the** **guest”** **does** **not** **automatically** **describe** **host** **I/O** **threading** **or** **vhost-user** **dataplane** **layout.**

## What this system teaches the atlas

**Separate** **vhost** **acceleration** **from** **virtio** **feature** **negotiation** **and** **from** **KVM** **VM** **lifecycle** **control.**
