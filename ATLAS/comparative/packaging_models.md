# Comparative: Packaging Models

**Atlas scope:** Artifact formats, dependency resolution, update mechanics.

## Matrix (initial)

| Model | Representative | Mechanism | Atlas package |
|-------|----------------|-----------|---------------|
| **OCI image** | Docker, Podman, Kubernetes CRI | Layered FS + manifest (`DOCUMENTED` OCI); execution via `runc`-class runtime (`DOCUMENTED`) | `docker`, `podman`, `containerd`, `cri-o`, `runc` (seeded) |
| **dpkg/rpm + upstream** | Typical Linux distros | Package manager + repositories (`DOCUMENTED` ecosystems) | (distro packages TBD) |
| **Nix store** | NixOS | Content-addressed store; generations (`DOCUMENTED` Nix manual) | `nixos` (seeded) |
| **VSIX / extension host** | VS Code | Extension marketplace + host loader (`DOCUMENTED` extension API) | `vscode` |
| **API-only “artifact”** | LLM weights in cloud | Not user-packaged; usage via API (`DOCUMENTED` billing/limits docs) | AI public-runtime packages |

## Teaching point

Packaging comparisons must not conflate **filesystem packages**, **container images**, and **API consumption**; they differ in trust and reproducibility guarantees.
