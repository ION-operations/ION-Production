# Start Here for Any Agent - ION Production Workspace

Status: candidate_entrypoint
Date: 2026-05-13

This workspace is being reorganized so `/home/sev/ION - Production` becomes the primary human and agent navigation root.

## Current root truth

```text
Workspace root: /home/sev/ION - Production
Current active ION kernel repo: /home/sev/ION - Production/ION_Developement
```

Do not use `/home/sev` as the project source-truth repo.

## First files to read

```text
AGENTS.md
ION_WORKSPACE_MANIFEST.yaml
ION_Developement/ION/02_architecture/ION_WORKSPACE_SOURCE_TRUTH_PROTOCOL_V0_1.md
ION_Developement/ION/05_context/current/repo_organization/GIT_BOUNDARY_AUDIT_20260513.md
ION_Developement/ION/05_context/current/repo_organization/MONOREPO_MIGRATION_PLAN_20260513.md
```

## Hard rules

- Do not touch GPT Builder without release-domain artifacts.
- Do not push without operator approval.
- Do not delete quarantine evidence.
- Do not remove nested `.git` directories before bundle backups.
- Do not print or commit secrets.
