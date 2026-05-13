---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| HAL | Hardware portability | DOCUMENTED |
| Kernel | Scheduling, IRQL, synchronization primitives | DOCUMENTED |
| Memory manager | Virtual memory, working sets | DOCUMENTED (internals refs) |
| Object manager | Handles, namespace | DOCUMENTED (internals refs) |
| I/O manager | IRPs, device stacks | DOCUMENTED (driver docs) |
| Security reference monitor | Access checks per policy | DOCUMENTED (high-level) |
