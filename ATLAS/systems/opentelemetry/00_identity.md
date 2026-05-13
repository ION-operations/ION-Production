---
atlas_package: system
system_slug: opentelemetry
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# OpenTelemetry — Identity

**Kind:** **CNCF** **observability** **framework** **(traces,** **metrics,** **logs)** **with** **OTLP** **wire** **formats** (`DOCUMENTED`, OpenTelemetry spec).

## Boundaries

- **Not** **a** **storage** **backend** — **exporters** **/** **collectors** **bridge** **to** **vendors.**  
- **Not** **application** **metrics** **without** **instrumentation** **—** **SDK** **layer** **is** **separate.**
