---
atlas_package: system
system_slug: unified-kernel-image
schema_version: "1.0"
last_reviewed: "2026-04-05"
evidence_grade: B
---

# Unified Kernel Image (UKI) — Identity

**Kind:** **Combined boot artifact** — **PE**/**EFI** **stub** packaging **kernel**, **initrd**, and **cmdline** for **measured**/**direct** UEFI boot (`DOCUMENTED`, systemd ukify / UKI docs).

## Boundaries

- Not generic GRUB configuration syntax — artifact format and tooling (e.g. `ukify`) per systemd docs.
- Not TPM2 logic alone — may interact with `tpm2` / firmware for measured boot (pin per deployment).
