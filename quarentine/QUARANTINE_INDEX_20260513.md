# Quarantine Index - 2026-05-13

Status: archive_witness_not_active_source

## Purpose

This folder preserves evidence and legacy/candidate material that should not be treated as active source by default.

## Known contents

```text
02_architecture/                         quarantined architecture candidate(s)
04_packages/                             quarantined package/kernel candidate(s)
ION_sandbox/                             sandbox package material
browser_extension/                       extension candidate ZIPs
dAimon_ION/                              dAimon/ION rapid package candidate
ion-sandbox-gpt/                         sandbox GPT material
supabase/                                stale pre-baseline Supabase folder
git_bundles_20260513/                    verified nested repo backup bundles
git_dirs_20260513/                       retired nested .git directories
nested_repo_worktree_evidence_20260513/  dirty worktree evidence before monorepo conversion
*.zip                                    archived package/runtime evidence
```

## Active-source rule

Quarantine is not active source. If a file here is needed, it should be reviewed and promoted through a bounded packet.

## Git rule

Raw quarantine contents are ignored by `quarentine/.gitignore`. Only this index and the quarantine README are tracked by default.

## Non-claims

- This index does not accept or settle quarantined material.
- This index does not authorize deletion.
- This index does not claim quarantine files are current.
