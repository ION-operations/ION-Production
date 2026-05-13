---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Observability

- **Tracepoints, ftrace, perf, eBPF** as first-class instrumentation (`DOCUMENTED`).  
- **`/proc`/`/sys`** export runtime state (`DOCUMENTED`).  
- **KASAN/KCSAN/KFENCE** etc. for debug/unsafe behavior detection (build-time optional) (`DOCUMENTED`).
