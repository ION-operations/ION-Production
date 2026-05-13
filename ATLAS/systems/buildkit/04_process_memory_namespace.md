---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Process, memory, namespace

**Build** **steps** **run** **as** **isolated** **process** **trees** **on** **the** **host** **using** **Linux** **namespaces/cgroups** **in** **typical** **configurations** **—** **distinct** **from** **the** **long-lived** **process** **sandbox** **model** **of** **a** **running** **pod** (`DOCUMENTED`/`INFERRED`).
