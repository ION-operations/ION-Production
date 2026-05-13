---
atlas_package: system
system_slug: golang
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (language)

## Concurrency

**Goroutines** + **channels** — **CSP**-influenced model (`DOCUMENTED`, `src-wiki-go`).

## Types

**Interfaces** (implicit satisfaction), **structs**, **slices**, **maps** (`DOCUMENTED`, `src-go-spec`).

## Runtime

**GC** — **stop-the-world** / **concurrent** phases evolve by version (`DOCUMENTED` release notes when load-bearing).
