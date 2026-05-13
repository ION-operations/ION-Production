---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture

## Namespace as the central abstraction

Plan 9 builds a **synthetic file tree** per process by **mounting** services and **binding** union directories. **Per-process namespace** is the primary composition mechanism (`DOCUMENTED`, `src-wiki-plan9-design`).

## 9P (Styx)

**9P** is the **file system protocol** used to access local and remote resources; messages read/write file-like operations (`DOCUMENTED`, `src-wiki-plan9-9p`). **Styx** is a variant name in some histories — treat naming per primary source (`DOCUMENTED`, `src-wiki-plan9`).

## Kernel and user space

Classic descriptions emphasize a **small kernel** with many services as **user processes**; details vary by release (`DOCUMENTED` overview; **UNKNOWN** micro-structure without kernel source citation).

## Storage stack (survey)

**Fossil** (file server) and **Venti** (block archival) appear in Plan 9 storage discussions (`DOCUMENTED`, `src-wiki-plan9-components`).

## Networking

**IL** protocol and networking stack appear in historical descriptions — treat as **HISTORICAL** unless current fork doc cited (`src-wiki-plan9-networking`).

## Comparison to Unix

Plan 9 is often framed as **rethinking Unix** — “Unix if done again” — **doctrinal** positioning in secondary sources (`DOCUMENTED`, `src-wiki-plan9`).
