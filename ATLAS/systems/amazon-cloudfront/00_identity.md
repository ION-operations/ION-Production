---
atlas_package: system
system_slug: amazon-cloudfront
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Amazon CloudFront — Identity

**Kind:** AWS content delivery network (CDN) with edge caching and request routing (`DOCUMENTED`, AWS developer guide).

## Boundaries

- Not `amazon-s3` — S3 is often an origin, not the CDN control plane.
- Not `aws-elastic-load-balancing` — different edge product (though architectures combine).
