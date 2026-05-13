# Workspace Index Candidate

Status: candidate index.
Date: 2026-05-13.

| Path | Classification | Current role | Notes |
|---|---|---|---|
| `AIM-OS/` | active sibling repo | AIM/OS legacy-current system | Renamed from `AIM-ION`; large repo. |
| `ATLAS/` | knowledge/system workspace | atlas/index/prompts/graphs | No git repo observed at maxdepth 2. |
| `Cursor/` | promoted integration root | Cursor extension + SDK | Formerly under `ION/09_integrations`. |
| `ION_Developement/` | active ION repo | main ION development repo | Renamed from `ION_CODEX FULL`; spelling is currently `Developement`. |
| `ION_GPT/` | promoted GPT/product root | Custom GPT packages + Action Gateway schema | Contains current `custom_gpt_action_gateway/openapi.yaml`. |
| `Needs_Routed/` | intake/routing holding area | diffs/workpackets requiring routing | Should get index and triage statuses. |
| `browser_extension/` | promoted integration root | ChatOps browser extension | Formerly under `ION/09_integrations`. |
| `dAimon/` | active sibling repo | dAimon/Gemini bridge and agent builder | Separate git repo. |
| `local_daemon/` | promoted integration root | ChatOps local daemon | Formerly under `ION/09_integrations`. |
| `mcp/` | promoted integration root | MCP preview/action/connector files | Formerly under `ION/09_integrations`. |
| `product_packager/` | promoted integration root | package builder | Formerly under `ION/09_integrations`. |
| `quarentine/` | quarantine holding area | stale/candidate evidence | Misspelled; rename later only after reference audit. |
| `systemd/` | promoted integration root | user service templates | Formerly under `ION/09_integrations`. |
| `what is ION?/` | docs/product material | explanatory docs | Space/question mark path may be awkward for tooling. |
| `wisdomNET/` | placeholder/domain root | empty observed | Needs ownership decision. |

## Recommended index upgrades

Create a parent-level machine registry later:

```text
/home/sev/ION - Production/WORKSPACE_INDEX.json
```

with:

```text
path
classification
git_repo
source_truth_status
owner_domain
runtime_consumers
cleanup_status
do_not_delete
notes
```

## Non-claims

This is a candidate index only.
