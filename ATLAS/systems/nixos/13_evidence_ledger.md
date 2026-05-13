---
atlas_package: system
system_slug: nixos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| nix-001 | System config is declared and built via NixOS modules | DOCUMENTED | `src-nixos-manual` | |
| nix-002 | /nix/store holds immutable artifacts | DOCUMENTED | `src-nix-manual` | |
| nix-003 | Generations enable rollback | DOCUMENTED | `src-nixos-manual` | |
| nix-004 | systemd integrates for service management | DOCUMENTED | `src-nixos-manual` | |
