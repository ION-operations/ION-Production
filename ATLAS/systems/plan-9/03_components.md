---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Components

Survey-level list — fork-specific packaging may rename or replace pieces (`DOCUMENTED`, `src-wiki-plan9-components`).

## Kernel / core

| Area | Role |
|------|------|
| Namespace | Mount, bind, union |
| 9P | Resource access protocol |
| Process model | `rfork`-class process creation (name varies by doc) |

## File servers

| Component | Role |
|-----------|------|
| Fossil | Primary file server (survey) |
| Venti | Archival block store (survey) |

## User interface (named in surveys)

| Component | Role |
|-----------|------|
| rio | Window system |
| acme | Text/programmer environment |
| rc | Shell |

## Compilers / languages

**Alef**, **limbo** precursors appear in historical Bell Labs context — **Inferno** carries Limbo forward (`DOCUMENTED`/`HISTORICAL`; see `inferno-os` package).

## Documentation

**man** pages and **html** help systems are part of the culture — **DOCUMENTED** as pattern, not a single URL here.
