---
atlas_package: system
system_slug: opencl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (API)

## Platform model

**Host** **+** **one** **or** **more** **devices**; **context** **binds** **devices** (`DOCUMENTED`, `src-khronos-opencl`).

## Memory model

**Global,** **local,** **private** **address** **spaces** — **kernel** **semantics** (`DOCUMENTED`, `src-khronos-opencl`).
