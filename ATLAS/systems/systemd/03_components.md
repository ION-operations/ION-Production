---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| systemd (PID 1) | Service manager | DOCUMENTED |
| journald | Logging | DOCUMENTED |
| logind | Session/seat management | DOCUMENTED |
| networkd | Network configuration (optional use) | DOCUMENTED |
| resolved | DNS stub resolver (optional use) | DOCUMENTED |
| udev (historically bundled) | Device management integration | DOCUMENTED / HISTORICAL mix |
