---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Build, deploy, and update

- **Build:** Kconfig/Kbuild; cross-compilation supported (`DOCUMENTED`).  
- **Deploy:** Bootloader loads kernel image; initramfs optional (`DOCUMENTED` / distro-specific).  
- **Update:** Distribution-maintained packages or image rebuilds (`OBSERVED` practice; not kernel-internal).
