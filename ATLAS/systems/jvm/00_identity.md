---
atlas_package: system
system_slug: jvm
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# JVM — Identity

**Kind:** **Java Virtual Machine** — **abstract** **computing** **machine** **with** **bytecode** **instruction** **set**, **class** **file** **format**, **and** **runtime** **rules** (`DOCUMENTED`, `src-jvms-oracle`).

**Authority:** **Java Virtual Machine Specification** (JVM spec) — **Oracle** / **OpenJDK** **publication** **line** (`DOCUMENTED`, `src-jvms-oracle`).

## Boundaries

- **Not** **the** **Java** **language** **alone** — **JLS** **≠** **JVM** **spec** (`DOCUMENTED`).  
- **Not** **Android** **DEX** **/** **ART** **bytecode** — **related** **but** **distinct** **formats** (`DOCUMENTED` boundary).

## Why this system matters

- **Ubiquitous** **managed** **runtime** **model** — **GC**, **verification**, **portable** **bytecode** (`DOCUMENTED` ecosystem).  
- **Contrast** **with** **native** **ABI** **(C)** **and** **with** **ECMA-335** **CLI** (`DOCUMENTED` comparative).

## What this system teaches the atlas

- How **verified** **bytecode** **+** **classloading** **shape** **trust** **and** **deployment**.
