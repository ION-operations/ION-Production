---
atlas_package: system
system_slug: ebpf
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# eBPF — Identity

**Kind:** **Linux** **kernel** **bytecode** **VM** **and** **verifier** **for** **safe** **extensibility** **(tracing,** **networking,** **security)** (`DOCUMENTED`, Linux kernel docs + BPF docs).

## Boundaries

- **Not** **the** **whole** **Linux** **kernel** — **see** **`linux-kernel`**.  
- **Not** **a** **userspace** **language** **runtime** — **clang** **/** **libbpf** **are** **tooling.**

## Why this matters for ION

- **Primary** **pattern** **for** **in-kernel** **observability** **and** **policy** **hooks** **without** **custom** **kernel** **forks.**
