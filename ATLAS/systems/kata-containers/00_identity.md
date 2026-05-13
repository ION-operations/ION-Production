---
atlas_package: system
system_slug: kata-containers
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# Kata Containers — Identity

**Kind:** **Open-source** **container** **runtime** **stack** **that** **runs** **OCI** **workloads** **inside** **lightweight** **virtual** **machines** **(commonly** **QEMU/KVM** **on** **Linux),** **exposing** **an** **OCI-compatible** **interface** (`DOCUMENTED`, `src-kata-docs`, `src-kata-github`).

## Boundaries

- **Not** **`runc`** **alone** **—** **runc** **implements** **OCI** **with** **Linux** **namespaces/cgroups;** **Kata** **targets** **VM-level** **isolation** **for** **the** **same** **bundle** **class.**  
- **Not** **`kubevirt`** **—** **KubeVirt** **models** **VMs** **as** **Kubernetes** **workloads;** **Kata** **models** **container** **sandboxes** **with** **VM** **technology** **under** **CRI/OCI.**  
- **Not** **`qemu`** **alone** **—** **QEMU** **is** **a** **VMM** **building** **block;** **Kata** **is** **the** **runtime** **integration** **and** **policy** **around** **OCI** **execution.**

## Why this system matters

- **Shows** **the** **third** **isolation** **seam** **in** **the** **matrix:** **namespaced** **containers,** **microVM** **VMMs,** **and** **VM-backed** **OCI** **runtimes.**

## What this system teaches the atlas

**Do** **not** **collapse** **“stronger** **isolation”** **marketing** **into** **one** **slug** **—** **compare** **mechanisms** **and** **operator** **surfaces** **explicitly.**
