---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Bitemporal memory model

**CMC** models **transaction time** (when recorded) and **valid time** (when true in the world), enabling as-of queries (`DOCUMENTED`, `src-aimos-cmc`).

## Atoms and snapshots

**Atoms** are the fundamental memory units; **snapshots** are content-addressed immutable bundles (`DOCUMENTED`, `src-aimos-cmc`).

## Epistemic classes (kernel)

The **KERNEL** classifies claims (e.g. OBSERVED, SOURCED, DERIVED, ASSUMED, SPECULATIVE, PENDING) — parallel in spirit to ATLAS evidence tiers but **native to AIM-OS** (`DOCUMENTED`, `src-aether-kernel-epistemic`).

## Capsule as continuity carrier

**AETHER_INTERFACE** defines **CAPSULE** as the **sole state carrier** for Aether-OS, with required fields (mission, now, must_not, evidence, blocker, next, handoff) and invariants (e.g. mission/must-not immutable unless Director changes) (`DOCUMENTED`, `src-aether-interface-capsule`).

## Namespace / registry

The **Living Atlas registry** assigns **canonical names**, **ceremonial aliases**, **module names**, **authority class**, **ontology class**, and **runtime truth** per object (`DOCUMENTED`, `src-aether-atlas-registry-schema`).
