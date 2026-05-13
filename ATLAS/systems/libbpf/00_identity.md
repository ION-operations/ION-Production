---
atlas_package: system
system_slug: libbpf
schema_version: "1.0"
last_reviewed: "2026-04-16"
evidence_grade: B
---

# libbpf — Identity

**Kind:** **Reference** **userspace** **C** **library** **for** **loading** **and** **managing** **eBPF** **programs** **and** **maps** **on** **Linux** **via** **the** **BPF** **syscall** **uAPI** (`DOCUMENTED`, `src-libbpf-github`, `src-libbpf-kernel-docs`).

## Boundaries

- **Not** **the** **in-kernel** **eBPF** **bytecode** **instruction** **set** **or** **verifier** — **see** **`ebpf`**.  
- **Not** **the** **Linux** **kernel** **as** **a** **whole** — **see** **`linux-kernel`**.  
- **Not** **a** **C** **standard** **library** — **see** **`glibc`** **/** **`musl`** **/** **`c-runtime`** **packages**.

## Why this system matters

- **Separates** **userspace** **BPF** **loader** **API** **from** **kernel** **BPF** **execution** **semantics** **for** **ION** **observability** **and** **policy** **tooling** **surveys**.

## What this system teaches the atlas

**Do** **not** **merge** **`ebpf`** **(kernel** **facility)** **with** **`libbpf`** **(userspace** **library)**.
