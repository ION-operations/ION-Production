---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# gVisor — Identity

**Kind:** **Application** **kernel** **/** **sandbox** **that** **interposes** **on** **syscalls** **for** **Linux** **container** **workloads,** **exposed** **primarily** **via** **the** **OCI-compatible** **`runsc`** **runtime** (`DOCUMENTED`, `src-gvisor-docs`, `src-gvisor-github`).

## Boundaries

- **Not** **`runc`** **alone** **—** **runc** **relies** **on** **Linux** **namespaces/cgroups** **for** **isolation;** **gVisor** **implements** **a** **different** **boundary** **model** **via** **syscall** **interposition.**  
- **Not** **`kata-containers`** **—** **Kata** **typically** **uses** **hardware-backed** **VM** **sandboxes;** **gVisor** **stays** **in** **a** **userspace** **kernel** **process** **model** **on** **the** **host.**  
- **Not** **`linux-kernel`** **as** **a** **replacement** **—** **gVisor** **still** **depends** **on** **the** **host** **kernel** **for** **scheduling** **and** **resource** **control.**

## Why this system matters

- **Demonstrates** **a** **third** **major** **OCI** **runtime** **class** **alongside** **namespace** **runtimes** **and** **VM-backed** **runtimes.**

## What this system teaches the atlas

**Compare** **isolation** **mechanisms** **explicitly** **—** **“OCI** **runtime”** **is** **not** **one** **security** **story.**
