# Workspace Path Repair

Status: candidate repair note.
Date: 2026-05-13.

## Scope

This repair teaches ION about the new workspace layout after integrations were
promoted out of:

```text
ION/09_integrations/
```

and into workspace-level roots such as:

```text
ION_GPT/
browser_extension/
mcp/
systemd/
Cursor/
local_daemon/
product_packager/
```

## Changes made

Added workspace path registry:

```text
ION/03_registry/ion_workspace_path_registry.yaml
```

Added resolver:

```text
ION/04_packages/kernel/ion_workspace_paths.py
```

Updated Codex mount surfaces from old root:

```text
/home/sev/ION - Production/ION_CODEX FULL
```

to new root:

```text
/home/sev/ION - Production/ION_Developement
```

Updated:

```text
.codex/config.toml
.codex/hooks/ion_session_start_context.py
```

Updated Custom GPT Action Gateway and release tooling to resolve the promoted
OpenAPI path:

```text
../ION_GPT/custom_gpt_action_gateway/openapi.yaml
```

with legacy fallback for:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

Updated:

```text
ION/04_packages/kernel/ion_custom_gpt_action_gateway.py
ION/04_packages/kernel/ion_action_schema_release.py
ION/03_registry/ion_custom_gpt_action_release_registry.yaml
ION/02_architecture/ION_CUSTOM_GPT_ACTION_RELEASE_DOMAIN_PROTOCOL_V0_1.md
ION/docs/setup/ION_CUSTOM_GPT_ACTION_RELEASE_PROCESS.md
```

Added resolver tests:

```text
ION/tests/test_kernel_ion_workspace_paths.py
```

## Remaining hazards

Many stale references still point to `ION/09_integrations/*`. The next packets
should address MCP, systemd, browser extension, and docs/tests separately.

Do not treat this as full workspace migration completion.

## Next recommended packets

```text
PCKT-ION-MCP-AND-SYSTEMD-PATH-RESOLUTION-001
PCKT-ION-BROWSER-EXTENSION-PATH-RESOLUTION-001
PCKT-ION-WORKSPACE-INDEX-001
PCKT-ION-INTEGRATION-PROMOTION-COMMIT-PLAN-001
```

## Non-claims

No services restarted.
No GPT Actions called.
No Supabase calls made.
No commit or push claimed.
No accepted-state claim.
