---
atlas_package: system
system_slug: nixos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **Nix store** `/nix/store` holds immutable artifacts (`DOCUMENTED`).  
- **Profiles & generations** select active system (`DOCUMENTED`).  
- **Module system** composes options across packages (`DOCUMENTED`).  
- **Activation scripts** switch running system (`DOCUMENTED`).  
- **systemd** runs services on typical Linux NixOS (`DOCUMENTED`).
