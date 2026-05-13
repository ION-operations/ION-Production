---
atlas_package: system
system_slug: golang
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Memory safety

**GC** + **bounds-checked** slices — **no** raw pointers as default (`DOCUMENTED` vs C).  
**unsafe** package — **escape hatch** (`DOCUMENTED`, `src-go-spec`).

## Supply chain

**Module** **checksum** database — **go** **sumdb** (`DOCUMENTED` `go` tool docs).
