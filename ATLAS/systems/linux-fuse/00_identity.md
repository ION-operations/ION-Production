---
atlas_package: system
system_slug: linux-fuse
schema_version: "1.0"
last_reviewed: "2026-04-25"
evidence_grade: B
---

# Linux FUSE — Identity

**Kind:** **Linux** **kernel** **mechanism** **that** **delegates** **filesystem** **operations** **to** **a** **userspace** **daemon** **via** **the** **FUSE** **interface** **(documented** **kernel** **FUSE** **documentation,** **`src-linux-fuse-kernel-docs`).**

## Boundaries

- **Not** **`linux-overlayfs`** **—** **OverlayFS** **is** **a** **kernel** **stacked** **filesystem** **implementation;** **FUSE** **bridges** **VFS** **to** **userspace** **handlers.**  
- **Not** **`docker`** **or** **`oci-image-spec`** **—** **those** **address** **container** **images** **and** **engines;** **FUSE** **is** **a** **general** **kernel**/**userland** **filesystem** **contract.**  
- **Not** **`libfuse`** **alone** **—** **libfuse** **is** **a** **userspace** **C** **library;** **this** **package** **centers** **the** **kernel** **FUSE** **facility.**

## Why this system matters

- **Explains** **SSHFS,** **object-store** **mounts,** **and** **custom** **agents** **without** **conflating** **them** **with** **in-kernel** **filesystems** **or** **OCI** **layers.**

## What this system teaches the atlas

**Separate** **the** **FUSE** **syscall**/**queue** **model** **from** **native** **VFS** **implementations** **and** **from** **container** **image** **formats.**
