---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Process, memory, namespace

**Stateless** HTTP request/response model at the spec layer; **no process** or **kernel namespace** semantics here (`DOCUMENTED` split from **`runc`**).
