---
atlas_package: system
system_slug: linux-capabilities
schema_version: "1.0"
last_reviewed: "2026-04-22"
evidence_grade: B
---

# Linux capabilities — Identity

**Kind:** **Linux** **kernel** **splitting** **of** **traditional** **superuser** **privileges** **into** **distinct** **`CAP_*`** **capability** **bits** **and** **sets** **(per** **documented** **capabilities(7)** **and** **kernel** **credential** **model)** (`DOCUMENTED`, `src-linux-capabilities-man7`).

## Boundaries

- **Not** **`linux-security-modules`** **(SELinux/AppArmor-class** **MAC)** **by** **itself** — **capabilities** **gate** **which** **privileged** **operations** **a** **thread** **may** **attempt;** **LSM** **layers** **policy** **on** **top** (`DOCUMENTED` **boundary**).  
- **Not** **`seccomp`** **/** **`libseccomp`** — **syscall** **allow/deny** **filters** **vs** **capability** **checks** **for** **permitted** **privileged** **operations**.  
- **Not** **`linux-namespaces`** **or** **`linux-cgroups`** — **visibility**/**resource** **isolation** **vs** **privilege** **decomposition**.

## Why this system matters

- **Explains** **`--cap-drop`**/**`--cap-add`**, **ambient** **capabilities,** **and** **file** **capabilities** **without** **conflating** **them** **with** **namespaces** **or** **MAC** **policy** **languages**.

## What this system teaches the atlas

**Separate** **fine-grained** **capability** **sets** **from** **namespace** **sandboxes,** **cgroup** **limits,** **and** **container** **engine** **defaults.**
