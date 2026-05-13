---
atlas_package: system
system_slug: linux-netfilter
schema_version: "1.0"
last_reviewed: "2026-04-24"
evidence_grade: B
---

# Process, memory, namespace

**Each** **network** **namespace** **has** **its** **own** **netfilter** **rule** **tables;** **moving** **a** **process** **between** **namespaces** **changes** **which** **rules** **apply** (`DOCUMENTED` **interaction** **patterns,** **INFERRED).**
