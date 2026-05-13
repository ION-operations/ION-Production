---
atlas_package: system
system_slug: pl-i
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Storage, network, and IPC (language-level)

## Storage

**Data aggregates** (arrays, structures) and **string** handling are first-class in language summaries (`DOCUMENTED`, `src-wiki-pl-i-summary`). **Persistence** is via language I/O and environment — not a language-internal single-level store.

## Network

**No** intrinsic network stack in the **core language** as commonly summarized — networking is via libraries/OS (`INFERRED` from absence in standard feature tables; confirm with full standard for edition-specific additions).

## IPC

Inter-program communication is **OS and library** mediated (files, pipes, subsystems), not PL/I-intrinsic in the same sense as a distributed object protocol (`INFERRED`).
