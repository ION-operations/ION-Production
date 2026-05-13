---
atlas_package: system
system_slug: android-aosp
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- Core architecture topics in AOSP docs: system server, Zygote, ART, HAL, Treble where documented (`DOCUMENTED`).  
- Kernel relationship and GKI direction as documented (`DOCUMENTED` — version-sensitive).

## Out of scope

- Individual OEM firmware pipelines — unless sourced per OEM package.  
- Play Services proprietary behavior without public documentation.

## Versioning note

Android releases are API-level and dessert-named; behavior is release-specific (`DOCUMENTED`).
