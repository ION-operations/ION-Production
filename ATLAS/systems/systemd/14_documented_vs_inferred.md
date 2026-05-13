---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Documented vs inferred

## DOCUMENTED claims

- Core unit model, journal, D-Bus control (`sd-001`–`sd-004`).

## INFERRED claims

- **Kubernetes node supervision** — common but not universal; edge marked INFERRED.

## OBSERVED

- Distro-specific default targets and unit sets — capture per distribution if needed.

## Open questions

- BSD/macOS port status drift — track upstream announcements.

## Forbidden until sourced

- “systemd replaced all other inits everywhere” — quantitative global claim needs data.
