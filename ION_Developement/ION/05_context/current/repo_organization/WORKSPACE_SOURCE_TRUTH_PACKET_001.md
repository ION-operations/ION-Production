# PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001

Status: candidate_packet
Date: 2026-05-13
Accepted state authority: false

## Objective

Convert the operator's reorganized `/home/sev/ION - Production` workspace into a governed source-truth model without losing moved integrations, nested repo history, or control-surface safety.

## Current conclusion

The simplest and best operator model is a workspace monorepo rooted at:

```text
/home/sev/ION - Production
```

This should replace the current practical assumption that `ION_Developement` alone is the whole project.

## Why now

The operator has promoted major ION parts to the workspace root:

```text
ION_GPT
browser_extension
mcp
local_daemon
systemd
product_packager
Cursor
```

Those are now first-class project parts. Keeping the Git root inside `ION_Developement` makes those parts invisible to the main repo.

## Required before mutation

- Bundle nested Git repos.
- Verify no secrets are staged.
- Decide absorb vs submodule for `dAimon` and `AIM-OS`.
- Review root ignore policy.
- Confirm root manifest.

## Output artifacts

- `ION_WORKSPACE_SOURCE_TRUTH_PROTOCOL_V0_1.md`
- `ion_workspace_source_truth_registry.yaml`
- `GIT_BOUNDARY_AUDIT_20260513.md`
- `NESTED_REPO_BACKUP_PLAN_20260513.md`
- `MONOREPO_MIGRATION_PLAN_20260513.md`
- `ROOT_GITIGNORE_CANDIDATE_20260513.gitignore`
- root `ION_WORKSPACE_MANIFEST.yaml`
- root `START_HERE_FOR_ANY_AGENT.md`

## Non-claims

- No Git root migration executed.
- No nested `.git` directories removed.
- No push.
- No GPT Builder changes.
- No accepted-state claim.
