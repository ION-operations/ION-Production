---
atlas_package: system
system_slug: systemd-boot
schema_version: "1.0"
last_reviewed: "2026-04-05"
evidence_grade: B
---

# systemd-boot — Identity

**Kind:** **Minimal UEFI boot loader** from the systemd project — **stub** loading kernels and UKI images where configured (`DOCUMENTED`, systemd-boot docs).

## Boundaries

- Not GRUB — simpler menu/stub model; see `competes_with` to `grub`.
- Not the Linux kernel — runs in firmware context before kernel handoff.
