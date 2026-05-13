---
atlas_package: system
system_slug: linux-namespaces
schema_version: "1.0"
last_reviewed: "2026-04-20"
evidence_grade: B
---

# Linux namespaces — Identity

**Kind:** **Linux** **kernel** **resource** **isolation** **abstraction** **—** **multiple** **namespace** **types** **(mount,** **UTS,** **IPC,** **PID,** **network,** **user,** **cgroup,** **time)** **with** **documented** **clone**/**unshare**/**setns** **patterns** (`DOCUMENTED`, `src-linux-namespaces-man7`).

## Boundaries

- **Not** **a** **container** **engine** — **see** **`docker`**, **`containerd`**, **`kubernetes`**.  
- **Not** **cgroup** **controller** **hierarchy** **law** **alone** — **resource** **accounting** **vs** **namespace** **views** (`INFERRED` **boundary**).  
- **Not** **`seccomp`** **/** **`landlock`** — **syscall** **filtering** **/** **LSM** **filesystem** **rules** **are** **separate** **concerns**.

## Why this system matters

- **Foundational** **for** **how** **Linux** **containers** **and** **sandboxes** **compose** **isolation** **without** **always** **using** **a** **VM**.

## What this system teaches the atlas

**Separate** **kernel** **namespace** **primitives** **from** **OCI** **runtimes** **and** **orchestrators**.
