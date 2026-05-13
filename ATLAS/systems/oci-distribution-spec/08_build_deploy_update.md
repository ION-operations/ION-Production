---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Build, deploy, update

**CI** pushes new manifests/blobs; **runtimes** pull on schedule or demand; **tag** updates are **registry-visible** events (`DOCUMENTED` practice).
