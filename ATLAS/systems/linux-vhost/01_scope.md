---
atlas_package: system
system_slug: linux-vhost
schema_version: "1.0"
last_reviewed: "2026-04-28"
evidence_grade: B
---

# Scope

## In scope

- **Kernel** **vhost** **driver** **model** **and** **documented** **interfaces** (`DOCUMENTED`).  
- **Relationship** **to** **virtio** **frontends** **and** **KVM** **guests** **as** **integration** **pattern** (`INFERRED`).  
- **vhost-user** **as** **a** **deployment** **pattern** **(kernel** **↔** **userspace)** **at** **survey** **level** (`INFERRED`).

## Out of scope

- **Specific** **QEMU** **version** **matrices** **—** **unless** **added** **as** **a** **separate** **package.**  
- **Full** **virtio-net** **offload** **catalog** **per** **NIC** **vendor** **—** **use** **hardware** **/** **driver** **docs.**

## Versioning note

**vhost** **subsystems** **(net,** **scsi,** **vsock,** **…)** **evolve** **across** **kernel** **releases** (`OBSERVED`).
