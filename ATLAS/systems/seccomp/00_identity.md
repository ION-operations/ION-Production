---
atlas_package: system
system_slug: seccomp
schema_version: "1.0"
last_reviewed: "2026-04-19"
evidence_grade: B
---

# seccomp — Identity

**Kind:** **Linux** **kernel** **seccomp** **facility** **—** **strict** **mode** **and** **seccomp-filter** **(BPF** **programs** **evaluated** **at** **syscall** **entry)** (`DOCUMENTED`, `src-seccomp-kernel-docs`).

## Boundaries

- **Not** **`libseccomp`** — **see** **`libseccomp`**.  
- **Not** **the** **general** **`ebpf`** **tracing**/**networking** **subsystem** — **different** **attachment** **and** **scope** (`DOCUMENTED` **boundary**).  
- **Not** **`landlock`** — **filesystem** **LSM** **rules** **vs** **syscall** **filtering**.

## Why this system matters

- **Primary** **Linux** **pattern** **for** **container** **and** **service** **sandboxing** **via** **syscall** **allow**/**deny** **lists**.

## What this system teaches the atlas

**Separate** **kernel** **seccomp** **semantics** **from** **the** **`libseccomp`** **policy** **generator** **library**.
