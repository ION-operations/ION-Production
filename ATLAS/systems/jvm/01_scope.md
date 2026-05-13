---
atlas_package: system
system_slug: jvm
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Bytecode** **semantics**, **class** **file** **structure**, **opcode** **meanings** (`DOCUMENTED`, `src-jvms-oracle`).  
- **Runtime** **areas**: **memory**, **threads**, **native** **interface** **(JNI)** — **per** **spec** (`DOCUMENTED`).

## Out of scope

- **JDK** **libraries** **as** **a** **whole** — **separate** **surface**.  
- **Single** **vendor** **JVM** **performance** **tuning** — **unless** **cited** **to** **that** **product** (`UNKNOWN` default).

## Versioning note

**JVM** **spec** **tracks** **Java** **SE** **releases** — **cite** **edition** **for** **exact** **opcode** **set** (`DOCUMENTED`).
