---
atlas_package: system
system_slug: android-bionic
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Android Bionic — Identity

**Kind:** **Android** **Bionic** **C** **library** **(libc)** **and** **dynamic** **linker** **surface** **for** **hosted** **native** **C**/**C++** **on** **Android** **(AOSP**/**NDK)** (`DOCUMENTED`, `src-aosp-bionic-readme`).

## Boundaries

- **Not** **`glibc`** **or** **`musl`** — **different** **ABI**, **linker** **policy**, **and** **NDK** **surface** (`DOCUMENTED`).  
- **Not** **desktop** **GNU/Linux** **libc** **—** **Android** **system** **image** **and** **API** **level** **constraints** **dominate** (`DOCUMENTED`).

## Why this system matters

- **Default** **native** **C** **runtime** **for** **apps** **/** **services** **using** **the** **NDK** **and** **on-device** **ELF** **binaries** (`DOCUMENTED`).

## What this system teaches the atlas

**Keep** **Bionic** **law** **separate** **from** **Linux** **distro** **`glibc`** **when** **reasoning** **about** **mobile** **/** **embedded** **Android** **native** **ABI**.
