---
atlas_package: system
system_slug: golang
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Goroutine scheduling

**M:N** scheduling — **runtime** responsibility (`DOCUMENTED`, `src-wiki-go`).

## Memory

**GC** — **no** manual free for Go heap (`DOCUMENTED`, `src-go-spec` summary).

## cgo boundary

**C** memory rules apply **inside** **C** allocations — **documented** hazards (`DOCUMENTED`, `src-cgo`).
