---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| nt-001 | User/kernel mode split with syscall dispatch | DOCUMENTED | `src-ms-learn-windows-kernel` | |
| nt-002 | Object manager provides handles to resources | DOCUMENTED | Internals book (`paper-russinovich-solomon-2005`) | Cite edition/page on upgrade |
| nt-003 | HAL abstracts hardware differences | DOCUMENTED | Kernel docs | |
| nt-004 | Win32 API is primary userspace surface for many apps | DOCUMENTED | `src-ms-win32-api` | |
