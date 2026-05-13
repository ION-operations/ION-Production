---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Plan 9 from Bell Labs — Identity

**Kind:** **Distributed operating system** research lineage from **Bell Labs** (1980s–1990s onward), built by many contributors associated with **Unix** lineage, emphasizing **per-process namespace**, **9P** protocol, **union directories**, and **simple interfaces** (`DOCUMENTED`, `src-wiki-plan9`, `src-plan9-paper`).

**Core technical identity:** “Everything is a file” pushed toward a **unified file–network** model; resources imported into a **namespace** (`DOCUMENTED`, `src-wiki-plan9-design`).

## Boundaries

- **Not** “Linux” or “POSIX-only” — Plan 9 is a **distinct** system with its own conventions (`DOCUMENTED`).  
- **Not** Inferno — related but **separate** product/lineage (see `systems/inferno-os/`).  
- **Community forks** (e.g. **9front**) are **separate packages** — do not merge identities.

## Why this system matters

- **Namespace-centric OS design** — influential on later “resources as files” thinking and **9P**-style RPC file access (`DOCUMENTED`, `src-wiki-plan9`).  
- **Bell Labs** pipeline from **Unix** research to post-Unix experiments (`HISTORICAL`, `src-wiki-plan9-history`).  
- Connects to **Go** language origin (robust tooling culture — **INFERRED** cultural link; cite primary talks/blogs for upgrade).

## What this system teaches the atlas

- How to document **research OS** properties without pretending **deployment share** equals Linux.  
- How **distributed systems** can be framed as **file namespace composition**.
