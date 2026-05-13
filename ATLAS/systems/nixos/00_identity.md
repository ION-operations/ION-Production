---
atlas_package: system
system_slug: nixos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# NixOS — Identity

**Kind:** Linux distribution whose **system configuration is declared** in Nix expressions and realized via the **Nix store** (content-addressed artifacts) and **generations** for rollback (`DOCUMENTED`, `src-nixos-manual`, `src-nix-manual`).

## Boundaries

- **Not** the Nix language alone — includes **OS activation** (`/etc`, systemd units) from configuration (`DOCUMENTED`).  
- **Not** purely a container runtime — compares to `docker`/`kubernetes` at packaging/reproducibility axis (`comparative`).

## Why this system matters

- Canonical example of **declarative OS** state: configuration.nix / flakes model (`DOCUMENTED`).  
- **Reproducible builds** and **binary caches** as operational pattern (`DOCUMENTED`).

## What this system teaches the atlas

- How **desired system state** can be a pure function of config + fixed inputs (with caveats for impure channels).  
- How **generations** resemble lightweight snapshot/rollback unlike image-only workflows.
