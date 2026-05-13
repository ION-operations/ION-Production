# Root Ignore Repair Receipt - 2026-05-13

Status: candidate_evidence
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001
Accepted state authority: false

## Purpose

Strengthen `/home/sev/ION - Production/.gitignore` before the first workspace-root commit.

## Explicitly blocked after filename scan

```text
ION_Developement/.env.supabase.local
dAimon/.env
AIM-OS/data/mcp/*.key
AIM-OS/data/mcp/*secret*
AIM-OS/data/mcp/*credential*
ION_Developement/ION/08_ui/joc_cockpit_shell/node_modules/
dAimon/.venv/
**/.venv/
**/node_modules/
**/__pycache__/
**/.pytest_cache/
quarentine/git_bundles_20260513/
quarentine/git_dirs_20260513/
quarentine/nested_repo_worktree_evidence_20260513/
```

## Non-claims

- No files staged.
- No commit.
- No push.
- No secret values inspected or printed.
