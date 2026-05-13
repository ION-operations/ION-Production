---
atlas_package: system
system_slug: android-bionic
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Bionic** **libc** **/** **dynamic** **linker** **behavior** **on** **supported** **Android** **ABI** **targets** (`DOCUMENTED`).  
- **NDK-visible** **C** **/** **POSIX** **subset** **and** **Android** **extensions** **as** **documented** **in** **AOSP**/**NDK** **materials** (`DOCUMENTED`).

## Out of scope

- **GNU/Linux** **glibc** **/** **musl** **desktop** **ABI** **compatibility** — **separate** **concern** (`DOCUMENTED`).  
- **Java**/**Kotlin** **ART** **API** **surface** — **not** **the** **C** **libc** **package** (`DOCUMENTED`).

## Versioning note

**API** **level** **and** **NDK** **release** **notes** **drive** **Bionic** **visible** **changes** (`DOCUMENTED`).
