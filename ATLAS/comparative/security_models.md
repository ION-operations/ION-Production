# Comparative: Security Models

**Atlas scope:** Authentication, authorization, isolation primitives, policy enforcement loci.

## Structural axes (no vendor absolutes)

| Axis | linux-kernel | windows-nt | kubernetes | systemd |
|------|--------------|------------|------------|---------|
| **Privilege boundary** | user/kernel; capabilities; LSM hooks (`DOCUMENTED`) | user/kernel; integrity levels (where deployed); ACLs (`DOCUMENTED` varies by edition) | API RBAC; admission; node kubelet boundary (`DOCUMENTED`) | root vs service user; hardening profiles (`DOCUMENTED` + deployer) |
| **Identity** | UID/GID; namespaces; cgroup ownership (`DOCUMENTED`) | SID; tokens (`DOCUMENTED`) | ServiceAccount; OIDC integrations (`DOCUMENTED` patterns) | unit `User=` / `Group=` (`DOCUMENTED`) |
| **Policy language** | seccomp, AppArmor, SELinux, BPF LSM (`DOCUMENTED` / feature-dependent) | various enterprise policies (`DOCUMENTED` product lines) | RBAC, NetworkPolicy, PSA (`DOCUMENTED`) | hardening options; sandboxing adjacent tools (`DOCUMENTED` unit options) |

## AI / tool surfaces (public only)

- **MCP:** JSON-RPC over stdio/SSE — trust is **host process + server binary** (`DOCUMENTED` threat model section of spec — cite in MCP package).  
- **Cloud model APIs:** OAuth/API keys; data handling statements in vendor docs — tier per claim in AI packages.

## Unknown until packaged

`xnu-macos` sandbox model details vs iOS variants — require dedicated package rows.
