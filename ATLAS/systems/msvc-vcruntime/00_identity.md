---
atlas_package: system
system_slug: msvc-vcruntime
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# MSVC VCRUNTIME / UCRT — Identity

**Kind:** **Microsoft** **Visual** **C++** **redistributable** **runtime** **surface** **on** **Windows** — **Universal** **C** **Runtime** **(UCRT)** **and** **`VCRUNTIME*.dll`** **family** **shipping** **as** **user**-**mode** **DLLs** **for** **MSVC**-**hosted** **C**/**C++** **builds** (`DOCUMENTED`, `src-ms-learn-ucrt`).

## Boundaries

- **Not** **`glibc`** **or** **`musl`** — **Windows** **CRT** **ABI** **and** **deployment** **model** (`DOCUMENTED`).  
- **Not** **`msvcprt`** **(C++** **stdlib** **DLLs)** — **separate** **package** (`DOCUMENTED`).  
- **Not** **the** **MSVC** **compiler** **/** **linker** **toolchain** **itself** — **runtime** **DLLs** **only** (`DOCUMENTED`).

## Why this system matters

- **Default** **Windows** **hosted** **C** **entry** **points** **and** **redistributable** **packaging** **for** **native** **MSVC** **ABI** **binaries** (`DOCUMENTED`).

## What this system teaches the atlas

**Split** **Windows** **CRT** **from** **Unix** **libcs** **when** **reasoning** **about** **ABI** **and** **deployment** **graphs**.
