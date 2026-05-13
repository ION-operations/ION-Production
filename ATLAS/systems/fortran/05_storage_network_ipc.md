---
atlas_package: system
system_slug: fortran
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Storage, network, and IPC

## Persistence

**File I/O** is core; **stream** vs **record** — standard-defined (`DOCUMENTED`, `src-wiki-fortran`).

## Network

No **intrinsic** TCP stack in **core** language — use **libraries** or **C** interop (`INFERRED`).

## Coarrays / MPI

**Parallel** programming via **coarrays** (2008+) or external **MPI** — **DOCUMENTED** at feature-name level; details **per book/compiler**.
