---
atlas_package: system
system_slug: nixos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- `configuration.nix`, modules, `nixos-rebuild`, systemd integration on NixOS (`DOCUMENTED`).  
- Flakes vs channels (as documented; policy evolves) (`DOCUMENTED`).

## Out of scope

- Every third-party Nix cache operator — unless separate package.  
- Home Manager as distinct project — cross-link later.

## Versioning note

NixOS releases numbered; unstable channel differs (`DOCUMENTED`).
