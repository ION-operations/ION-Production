---
atlas_package: system
system_slug: virtio
schema_version: "1.0"
last_reviewed: "2026-04-27"
evidence_grade: B
---

# Scope

## In scope

- **Virtio** **transport** **basics** **(queues,** **descriptor** **rings,** **feature** **negotiation)** **per** **kernel** **documentation** (`DOCUMENTED`).  
- **Common** **device** **types** **(block,** **network,** **…)** **as** **named** **in** **the** **virtio** **ecosystem** (DOCUMENTED **overview** **+** **INFERRED** **details).**  
- **Relationship** **to** **KVM** **guests** **and** **microVM** **stacks** **as** **integration** **pattern** (`INFERRED`).

## Out of scope

- **Vendor-specific** **NIC** **offloads** **outside** **virtio** **semantics** **—** **unless** **added** **as** **separate** **packages.**  
- **Full** **OASIS** **virtio** **spec** **diff** **history** **—** **use** **normative** **spec** **sources** **for** **ledger** **depth.**

## Versioning note

**Feature** **bits** **and** **device** **types** **expand** **over** **time** (`OBSERVED`).
