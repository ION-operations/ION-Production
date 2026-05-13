---
atlas_package: system
system_slug: c-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (language)

## Translation units

**`.c`** files → **object** → **link**; **header** `.h` for declarations (`DOCUMENTED`).

## Memory

**Automatic**, **static**, **thread-local** (`_Thread_local` / `thread_local` in C11), **heap** via library (`malloc`) (`DOCUMENTED`, `src-wiki-c`).

## Undefined behavior

Operations with **no** required semantics — compiler may optimize aggressively — **security** relevance (`DOCUMENTED`, `src-wiki-c`).

## Preprocessor

**`#include`**, **`#define`**, conditional compilation — **first** translation phase (`DOCUMENTED`, `src-wiki-c`).
