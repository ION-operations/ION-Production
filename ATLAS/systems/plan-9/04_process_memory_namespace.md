---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Per-process namespace

Each process can have a **distinct view** of `/` built from **mount** and **bind** operations — the central Plan 9 design idea (`DOCUMENTED`, `src-wiki-plan9-design`).

## Union directories

**Union** mounts overlay multiple directories — control of precedence and visibility is part of the model (`DOCUMENTED`, `src-wiki-plan9-design`).

## Memory / address space

**Copy-on-write** and process creation (`rfork`-style) appear in technical summaries — exact semantics **per kernel version** need source or manual (`DOCUMENTED` overview; **UNKNOWN** line-by-line).
