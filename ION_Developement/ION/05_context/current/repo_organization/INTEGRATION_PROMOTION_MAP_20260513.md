# Integration Promotion Map

Status: candidate map.
Date: 2026-05-13.

## Purpose

Map the apparent promotion of `ION/09_integrations/*` out of the active repo and
into workspace-level folders.

## Old tracked root

```text
ION/09_integrations/
```

Git currently sees these old paths as deleted in the active repo.

## New workspace roots

| Old repo path | New workspace path | Status |
|---|---|---|
| `ION/09_integrations/custom_gpt_action_gateway/` | `../ION_GPT/custom_gpt_action_gateway/` | moved, critical hash match for `openapi.yaml` |
| `ION/09_integrations/chatgpt_browser_mcp_action/` | `../mcp/chatgpt_browser_mcp_action/` | moved, critical hash match for `openapi.yaml` |
| `ION/09_integrations/mcp/` | `../mcp/` | moved |
| `ION/09_integrations/browser_extension/ion_chatops_bridge/` | `../browser_extension/ion_chatops_bridge/` | moved, critical hash match for `manifest.json` |
| `ION/09_integrations/cursor_extension/` | `../Cursor/cursor_extension/` | moved |
| `ION/09_integrations/cursor_sdk/` | `../Cursor/cursor_sdk/` | moved |
| `ION/09_integrations/local_daemon/ion_chatops_bridge/` | `../local_daemon/ion_chatops_bridge/` | moved, critical hash match for daemon file |
| `ION/09_integrations/product_packager/` | `../product_packager/` | moved |
| `ION/09_integrations/systemd/user/` | `../systemd/user/` | moved, critical hash match for action-gateway service template |

## Compatibility decision needed

There are two viable strategies.

### Strategy A: keep canonical tracked copies inside ION repo

Use workspace-level folders as exports/convenience copies, but keep canonical
source under:

```text
ION/09_integrations/
```

Advantages:

- Minimal code/test/doc churn.
- Existing kernels and tests keep working.
- Git keeps integration source under the active repo.
- Action Gateway `/openapi.yaml` remains safe on restart.

Disadvantages:

- Workspace-level copies may drift unless generated/synced.

### Strategy B: promote integrations as first-class workspace siblings

Make workspace-level folders the canonical locations and update all tooling to
resolve them.

Advantages:

- Cleaner product/workspace separation.
- Browser extension, MCP, systemd, Cursor, GPT assets become obvious top-level
  domains.

Disadvantages:

- Requires a full path migration across kernels, tests, docs, registries, and
  service templates.
- Current git repo will show deletions unless those roots become separate repos,
  submodules, packages, or explicitly excluded/exported artifacts.
- Action Gateway and release tooling must be fixed before service restart.

## Recommendation

Short term:

```text
Use Strategy A for critical live control surfaces until path resolution is
updated and tested.
```

Specifically, preserve or restore a tracked canonical copy of:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
ION/09_integrations/chatgpt_browser_mcp_action/openapi.yaml
ION/09_integrations/systemd/user/
```

Long term:

```text
Adopt Strategy B only through a formal workspace path registry and compatibility
layer.
```

## Required path registry

Create:

```text
ION/03_registry/ion_workspace_path_registry.yaml
```

Required fields:

```text
workspace_root
active_repo_root
integration_roots
canonical_source_path
workspace_export_path
status
owner_domain
runtime_consumers
compatibility_required
```

## High-risk stale consumers

Observed stale references include:

```text
.codex/hooks/ion_session_start_context.py
.codex/config.toml
ION/04_packages/kernel/ion_custom_gpt_action_gateway.py
ION/04_packages/kernel/ion_action_schema_release.py
ION/04_packages/kernel/ion_local_service_status.py
ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py
ION/tests/test_kernel_ion_custom_gpt_action_gateway.py
ION/tests/test_kernel_ion_chatgpt_browser_mcp_action_openapi.py
ION/tests/test_kernel_ion_custom_gpt_carrier_instruction_gates.py
ION/tests/test_kernel_ion_chatops_action_schema.py
ION/README.md
ION/03_registry/ion_trunk_preservation_policy.yaml
ION/03_registry/ion_chatgpt_browser_mcp_tool_policy.yaml
```

## Action Gateway red line

Do not restart Action Gateway until one of these is true:

1. `ION/09_integrations/custom_gpt_action_gateway/openapi.yaml` exists again as
   a compatibility/canonical copy.
2. Gateway code and release tooling are updated to use
   `../ION_GPT/custom_gpt_action_gateway/openapi.yaml`.

## Non-claims

This map does not move files, delete files, stage changes, or claim the
promotion is accepted state.
