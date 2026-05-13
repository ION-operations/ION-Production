---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Firecracker — Identity

**Kind:** **Virtual machine monitor (VMM)** that uses **Linux KVM** to run lightweight **microVMs**, designed for high density and a minimal device model (`DOCUMENTED`, `src-firecracker-docs`, `src-firecracker-repo`).

## Boundaries

- **In scope:** Public Firecracker architecture, KVM requirements, microVM boot model as documented.  
- **Out of scope:** AWS Lambda/Fargate internal control planes — **UNKNOWN** unless primary AWS engineering publications are ledgered (product marketing pages are not architecture proofs).

## Why this system matters

- Demonstrates **VM-level isolation** as an alternative/complement to **namespaced containers** (`DOCUMENTED` comparative).  
- Reference implementation class for **microVM** density on Linux (`DOCUMENTED` performance claims require cited benchmarks).

## What this system teaches the atlas

- Same “workload isolation” problem has **process**, **container**, and **VM** seams — do not collapse tiers.
