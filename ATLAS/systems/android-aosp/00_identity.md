---
atlas_package: system
system_slug: android-aosp
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Android Open Source Project (AOSP) — Identity

**Kind:** Open-source **mobile OS stack**: Linux-based kernel, hardware abstraction layer (HAL), native/userspace services, Android Runtime (ART), framework APIs, and system apps as defined in AOSP (`DOCUMENTED`, `src-aosp-docs`).

## Boundaries

- **Not** any single OEM skin or proprietary GMS bundle unless explicitly sourced as add-on.  
- **Not** identical to mainline **linux-kernel** — vendor/device trees apply (`DOCUMENTED`).

## Why this system matters

- Dominant **open mobile base** for handset ecosystem (`OBSERVED` market + `DOCUMENTED` architecture).  
- Shows **Binder IPC**, **HAL**, and **permission model** distinct from desktop Linux (`DOCUMENTED`).

## What this system teaches the atlas

- How **kernel + framework + vendor** layers split trust and update cadence.  
- How **Java/Kotlin framework** sits over native services.
