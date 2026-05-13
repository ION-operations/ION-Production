---
atlas_package: system
system_slug: gnu-gcc
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **gcc** / **g++** driver, common **optimization** and **warning** flags (`DOCUMENTED`, `src-gcc-manual`).  
- Relationship to **GNU as** and **GNU ld** (`DOCUMENTED`).

## Out of scope

- **glibc** / **musl** / **libc** implementation — see **`glibc`** and **`musl`** (`c-runtime`); GCC **targets** one of them per triplet (`DOCUMENTED` split).  
- **GNU libstdc++** — see **`gnu-libstdcxx`** (`cxx-runtime`); **g++** **links** it by **default** (`DOCUMENTED` split).  
- **gdb** — see **`gnu-gdb`** (separate debugger package).

## Versioning note

**GCC** major releases; distro **default** version varies (`INFERRED` deployment).
