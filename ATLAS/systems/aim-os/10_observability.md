---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Observability

## VIF / witnesses

Operations can emit **witness** records linking model, prompts, tools, confidence — audit trail (`DOCUMENTED`, `src-aimos-vif`).

## HHNI performance

Audit-style **p95** figures appear in major systems reference (e.g. retrieval latency targets vs measured) — **DOCUMENTED** as cited; environment-dependent (`src-aimos-hhni-perf`).

## DORA / SDF-CVF

**DORA metrics** and deployment gates referenced under **SDF-CVF** (`DOCUMENTED`, `src-aimos-sdfcvf`).

## CAS / SCOR

Meta-cognitive and sanity **probes** — operational observability of agent behavior (`DOCUMENTED`).

## Gaps

Centralized **single-pane** SRE dashboard for all AIM-OS subsystems — **UNKNOWN** in this package without cited artifact.
