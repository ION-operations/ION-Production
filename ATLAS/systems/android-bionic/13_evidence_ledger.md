---
atlas_package: system
system_slug: android-bionic
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| bionic-001 | AOSP documents Bionic as the platform C library | DOCUMENTED | `src-aosp-bionic-readme` | |
| bionic-002 | Bionic participates in ELF dynamic linking for Android native binaries | DOCUMENTED | NDK docs | |
| bionic-003 | NDK builds link native code against Bionic | DOCUMENTED | `src-android-ndk-cpp` | |
