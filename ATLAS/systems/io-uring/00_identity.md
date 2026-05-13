---
atlas_package: system
system_slug: io-uring
schema_version: "1.0"
last_reviewed: "2026-04-17"
evidence_grade: B
---

# io_uring — Identity

**Kind:** **Linux** **kernel** **asynchronous** **I/O** **facility** **with** **submission** **and** **completion** **queues** **(io_uring** **uAPI)** (`DOCUMENTED`, `src-io-uring-kernel-docs`).

## Boundaries

- **Not** **the** **`liburing`** **userspace** **library** — **see** **`liburing`**.  
- **Not** **a** **generic** **disk** **driver** **or** **filesystem** — **those** **sit** **below**/**beside** **the** **uAPI**.  
- **Not** **`ebpf`** — **distinct** **kernel** **extension** **mechanism** (`DOCUMENTED` **boundary**).

## Why this system matters

- **High-throughput** **I/O** **patterns** **for** **servers** **and** **data** **planes** **without** **polling** **every** **fd** **like** **classic** **`select`**/**`poll`**/**`epoll`** **alone** (`DOCUMENTED` **themes**).

## What this system teaches the atlas

**Separate** **kernel** **io_uring** **uAPI** **semantics** **from** **the** **`liburing`** **helper** **library**.
