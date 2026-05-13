# Workspace Reorganization Audit

Status: candidate audit.
Date: 2026-05-13.
Workspace root:

```text
/home/sev/ION - Production
```

Active ION repo after reorganization:

```text
/home/sev/ION - Production/ION_Developement
```

Previous active ION repo path observed earlier:

```text
/home/sev/ION - Production/ION_Developement
```

## Executive finding

The reorganization is directionally useful, but it crossed a repo/path boundary
that ION tooling has not yet been taught.

The largest structural change is:

```text
ION/09_integrations/*
```

was promoted out of the repo into workspace-level folders:

```text
ION_GPT/
browser_extension/
Cursor/
local_daemon/
mcp/
product_packager/
systemd/
```

The moved files appear preserved for critical samples, but the active git repo
currently sees the old tracked paths as deletions. Many tests, docs, registries,
and kernels still reference the old in-repo paths.

## Current workspace roots

Observed top-level workspace roots:

```text
AIM-OS
ATLAS
Cursor
ION_Developement
ION_GPT
Needs_Routed
browser_extension
dAimon
local_daemon
mcp
product_packager
quarentine
systemd
what is ION?
wisdomNET
```

Git repos observed:

```text
AIM-OS
ION_Developement
dAimon
```

## Major rename / relocation observations

### Active ION repo rename

Observed:

```text
ION_CODEX FULL -> ION_Developement
```

Risk:

`.codex` hook/config still refers to the old path:

```text
/home/sev/ION - Production/ION_Developement
```

Immediate effect:

Codex startup/mount tooling may mount the wrong path or fail to mount active
ION context if launched from the new repo path.

### AIM project rename

Observed:

```text
AIM-ION -> AIM-OS
```

This appears semantically cleaner, but any cross-project references to `AIM-ION`
will need a route map or compatibility note.

### Integration promotion

Moved surfaces now appear at workspace root:

```text
ION_GPT/custom_gpt_action_gateway/
browser_extension/ion_chatops_bridge/
Cursor/cursor_extension/
Cursor/cursor_sdk/
local_daemon/ion_chatops_bridge/
mcp/chatgpt_browser_mcp_action/
mcp/chatgpt_connector/
mcp/ion_mcp_server.py
product_packager/
systemd/user/
```

These correspond to previously tracked repo paths under:

```text
ION/09_integrations/
```

## Critical hash-preservation checks

The following old tracked files matched the new promoted files by SHA256:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
-> ../ION_GPT/custom_gpt_action_gateway/openapi.yaml
sha256: 9ee5e43885e85607ae51a0efccd72d780ba57635074bc6b01a2f81dff8ae72ba

ION/09_integrations/chatgpt_browser_mcp_action/openapi.yaml
-> ../mcp/chatgpt_browser_mcp_action/openapi.yaml
sha256: 32933c593667b014e477dadf4638d7133c831267c9bfd50f95b4a69656360214

ION/09_integrations/systemd/user/ion-action-gateway.service.template
-> ../systemd/user/ion-action-gateway.service.template
sha256: d3f6873ebdf29fcb59a5e9a7f8f93a69a7afbb7c80379deb3ed391a4587bac38

ION/09_integrations/browser_extension/ion_chatops_bridge/manifest.json
-> ../browser_extension/ion_chatops_bridge/manifest.json
sha256: d90e657c35a218e50835b1c48b9478f0a8fe881af7e6ccc326fa8f7ebce1a5df

ION/09_integrations/local_daemon/ion_chatops_bridge/ion_chatops_daemon.py
-> ../local_daemon/ion_chatops_bridge/ion_chatops_daemon.py
sha256: 0a5a912c0535be29faf3983b0e42276086ca57d7bdd37b1ec87d0b3ed218a993
```

Interpretation:

The move likely preserved content, but ION path ownership and tooling have not
been updated yet.

## Immediate hazards

### Action Gateway OpenAPI path hazard

Current Action Gateway code still points to:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

The moved file now exists at:

```text
/home/sev/ION - Production/ION_GPT/custom_gpt_action_gateway/openapi.yaml
```

Hazard:

If the gateway is restarted before path resolution is fixed or a compatibility
copy is restored, `/openapi.yaml` may fail or serve stale/missing content.

### Action release domain path hazard

The newly created Custom GPT Action release helper also uses:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

After the reorg, that path is deleted in the working tree. The release-domain
tooling must be updated or a tracked compatibility surface must be restored
before using it.

### MCP preview schema/test hazard

Tests and docs still reference:

```text
ION/09_integrations/chatgpt_browser_mcp_action/openapi.yaml
```

The current file is at:

```text
/home/sev/ION - Production/mcp/chatgpt_browser_mcp_action/openapi.yaml
```

### Systemd template hazard

Kernel status code still references:

```text
ION/09_integrations/systemd/user
```

The current files are at:

```text
/home/sev/ION - Production/systemd/user
```

### Git status hazard

The active repo currently records many `D` entries for moved files. If committed
without a corresponding path-migration plan, Git history will treat these as
deletions from ION rather than a governed workspace promotion.

## Supabase status after reorg

Canonical active Supabase root moved with the active repo:

```text
/home/sev/ION - Production/ION_Developement/supabase
```

It still contains:

```text
config.toml
live_schema_snapshots/
migrations/001_initial_ion_ops.sql
migrations/002_dev_private_cockpit_read_policies.sql
migrations/003_ion_ops_authority_and_rpc.sql
migrations/004_ion_ops_api_grants.sql
migrations/005_ion_ops_cockpit_readmodel_fixes.sql
seed/001_ion_ops_bootstrap_seed.sql
tests/validate_initial_ion_ops_sql.py
```

Quarantined stale Supabase remains:

```text
/home/sev/ION - Production/quarentine/supabase
```

Decision remains:

```text
keep active: ION_Developement/supabase
quarantine stale: quarentine/supabase
do not merge stale into active
```

## Recommended posture

Do not commit the broad reorganization yet.

First create a path migration map and update tooling in a bounded packet.

The current reorg should be treated as:

```text
candidate workspace promotion
not accepted repo state
```

## Recommended next packets

### PCKT-ION-WORKSPACE-ROOT-RENAME-AND-MOUNT-001

Purpose:

```text
Update active root references from ION_CODEX FULL to ION_Developement.
```

Scope:

```text
.codex/config.toml
.codex/hooks/ion_session_start_context.py
Codex mount docs
active root registry / workspace index
```

### PCKT-ION-INTEGRATION-PROMOTION-PATH-MAP-001

Purpose:

```text
Govern the move from ION/09_integrations/* to workspace-level integration roots.
```

Output:

```text
INTEGRATION_PROMOTION_MAP_20260513.md
ION_WORKSPACE_PATH_REGISTRY.yaml
compatibility strategy
```

### PCKT-ION-ACTION-GATEWAY-PATH-RESOLUTION-001

Purpose:

```text
Update Action Gateway and Custom GPT Action release domain to resolve the
canonical OpenAPI from the new workspace location or restore a compatibility
copy.
```

Critical before:

```text
Action Gateway restart
GPT Builder recovery
Action release package generation
```

### PCKT-ION-MCP-AND-SYSTEMD-PATH-RESOLUTION-001

Purpose:

```text
Update MCP preview, connector, and systemd template paths after integration
promotion.
```

### PCKT-ION-WORKSPACE-INDEX-001

Purpose:

```text
Create parent-level WORKSPACE_INDEX.md and machine-readable workspace registry.
```

## Recommended domain

Create formal domain:

```text
ION_REPO_ORGANIZATION_AND_CARTOGRAPHY
```

This domain should own:

```text
workspace root map
repo root map
integration promotion map
quarantine index
route/needs intake map
stale reference audits
move receipts
path migration compatibility strategy
```

## Non-claims

This audit does not delete, move, stage, commit, push, restart services, or run
live Action/Supabase/MCP calls.

This audit does not claim the reorganization is accepted state.
