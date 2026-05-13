---
atlas_package: system
system_slug: golang
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Spec**-level **syntax** and **semantics** — `go.dev/ref/spec` (`DOCUMENTED`).  
- **Module** / **workspace** model — **go.mod** (`DOCUMENTED` practice; cite `go` tool docs when load-bearing).

## Out of scope

- **Every** third-party **framework** — **UNKNOWN** without package doc.  
- **gccgo** vs **gc** codegen differences — **UNKNOWN** per claim without manual.

## Versioning note

**Go 1** compatibility promise — **documented** in **release policy** (`DOCUMENTED`, `src-go-compat`).
