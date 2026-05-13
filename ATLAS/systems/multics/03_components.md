---
atlas_package: system
system_slug: multics
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| Supervisor | Privileged kernel; protection enforcement | HISTORICAL (`paper-organick-1972-multics`) |
| Segment / memory subsystem | Virtual memory + protection bindings | HISTORICAL (`paper-saltzer-1974-protection`) |
| File / information system | Persistent naming and access (design-era) | HISTORICAL (`paper-corbato-1965-multics`, Organick) |
| Shell / command environment | Interactive use | HISTORICAL (primary literature; expand with source IDs) |

**UNKNOWN without further sourcing:** per-site optional subsystems (e.g., specialized I/O).
