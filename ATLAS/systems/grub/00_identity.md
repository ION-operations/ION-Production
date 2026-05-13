---
atlas_package: system
system_slug: grub
schema_version: "1.0"
last_reviewed: "2026-04-04"
evidence_grade: B
---

# GRUB — Identity

**Kind:** **GNU** **GRUB** **boot** **loader** **—** **multiboot,** **menu,** **kernel** **/** **initrd** **loading** **on** **BIOS** **/** **UEFI** **systems** (`DOCUMENTED`, GNU GRUB manual).

## Boundaries

- **Not** **Linux** **kernel** — **pre-kernel** **stage.**  
- **Not** **systemd** — **different** **lifecycle** **(PID** **1** **comes** **after** **kernel** **handoff).**
