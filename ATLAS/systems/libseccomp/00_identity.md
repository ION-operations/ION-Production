---
atlas_package: system
system_slug: libseccomp
schema_version: "1.0"
last_reviewed: "2026-04-19"
evidence_grade: B
---

# libseccomp — Identity

**Kind:** **Userspace** **C** **library** **for** **building** **and** **loading** **seccomp** **BPF** **policies** **against** **the** **Linux** **kernel** **seccomp** **uAPI** (`DOCUMENTED`, `src-libseccomp-github`, `src-seccomp-kernel-docs`).

## Boundaries

- **Not** **the** **kernel** **seccomp** **implementation** — **see** **`seccomp`**.  
- **Not** **a** **container** **runtime** — **see** **`docker`**, **`containerd`**, **`kubernetes`**.

## Why this system matters

- **Standard** **helper** **for** **generating** **correct** **BPF** **filters** **without** **hand-assembling** **every** **instruction** **for** **common** **policies**.

## What this system teaches the atlas

**Do** **not** **merge** **`seccomp`** **(kernel)** **with** **`libseccomp`** **(library)**.
