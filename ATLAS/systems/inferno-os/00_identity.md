---
atlas_package: system
system_slug: inferno-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Inferno — Identity

**Kind:** **Distributed operating system** and **application environment** originating at **Bell Labs** (1990s), with **Limbo** programming language, **Dis** virtual machine, and **Styx** protocol (9P-class wire protocol) (`DOCUMENTED`, `src-wiki-inferno`).

**Portability:** Designed to run **hosted** on many OSes or **native** on bare metal — “OS as portable appliance” framing in surveys (`DOCUMENTED`, `src-wiki-inferno`).

## Boundaries

- **Not** identical to **Plan 9** — shared Bell Labs DNA and protocol lineage, different product (`DOCUMENTED`, `src-wiki-inferno-plan9-relation`).  
- **Not** Linux — may run **on** Linux as a host (`DOCUMENTED` portability).

## Why this system matters

- **VM + language + protocol** co-design (**Dis**, **Limbo**, **Styx**) for distributed programs (`DOCUMENTED`, `src-wiki-inferno`).  
- **Commercial** path through **Vita Nuova** and later stewardship — licensing arc is **HISTORICAL** (see wiki / primary licenses).

## What this system teaches the atlas

- How **research OS** ideas (Plan 9 family) become **portable** products.  
- How to keep **9P/Styx** naming straight across packages (`plan-9`, `inferno-os`, Linux **v9fs**).
