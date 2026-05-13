# Repo Organization Audit

Status: candidate organization audit.
Date: 2026-05-13.
Scope: `/home/sev/ION - Production` and active ION repo layout.

## Current posture

The active ION working repo is:

```text
/home/sev/ION - Production/ION_Developement
```

The parent folder is becoming a multi-project workspace, not a single repo:

```text
/home/sev/ION - Production/
```

Observed sibling project / holding areas include:

```text
AIM-ION/
ATLAS/
ION_Developement/
ION_GPT/
Needs_Routed/
browser_extension/
dAimon/
dAimon_ION/
quarentine/
```

This means ION needs a workspace-level cartography lane in addition to
repo-internal indexes.

## Supabase folder finding

Observed Supabase-like folders:

```text
/home/sev/ION - Production/ION_Developement/supabase
/home/sev/ION - Production/quarentine/supabase
/home/sev/ION - Production/ION_Developement/ION/05_context/current/supabase_event_mirror
```

### Canonical Supabase root

The canonical repo-managed Supabase root is:

```text
/home/sev/ION - Production/ION_Developement/supabase
```

Reasons:

- Contains `config.toml`.
- Contains Supabase CLI `.temp/` link metadata.
- Contains migrations `001` through `005`.
- Contains live schema snapshot evidence.
- Contains current seed file.
- Contains current validator with 306 lines.
- Size: `160K`.
- File count: `20`.

### Quarantined Supabase copy

The quarantined copy is:

```text
/home/sev/ION - Production/quarentine/supabase
```

Observed contents:

```text
README_ION_LOCAL_SETUP.md
migrations/001_initial_ion_ops.sql
seed/001_ion_ops_bootstrap_seed.sql
tests/validate_initial_ion_ops_sql.py
```

Reasons it is stale/candidate evidence:

- Missing `config.toml`.
- Missing Supabase CLI `.temp/` link metadata.
- Missing migrations `002`, `003`, `004`, and `005`.
- Missing live schema snapshot evidence.
- Validator is only 61 lines versus active validator at 306 lines.
- Seed and migration hashes differ from active repo files.
- Size: `40K`.
- File count: `4`.

### Hash comparison summary

The only identical file between active and quarantined Supabase folders was:

```text
README_ION_LOCAL_SETUP.md
```

These differ and should be treated as stale evidence until reviewed:

```text
migrations/001_initial_ion_ops.sql
seed/001_ion_ops_bootstrap_seed.sql
tests/validate_initial_ion_ops_sql.py
```

## Supabase consolidation decision

Recommended decision:

```text
Keep: /home/sev/ION - Production/ION_Developement/supabase
Quarantine: /home/sev/ION - Production/quarentine/supabase
Do not merge quarantined Supabase files into the active repo.
Do not delete quarantined Supabase until a cleanup receipt records hashes.
```

Recommended next rename, after review:

```text
/home/sev/ION - Production/quarentine/supabase
-> /home/sev/ION - Production/quarentine/supabase_legacy_pre_baseline_20260513
```

Reason: avoid future confusion that quarantined `supabase/` is a live root.

## Current organization risks

- Parent workspace now contains multiple project roots and holding areas with
  overlapping concepts.
- `quarentine` is misspelled and should eventually become `quarantine`, but only
  after references are checked.
- Some repo-internal candidate systems are uncommitted and should not be mixed
  into cleanup commits.
- Runtime evidence, candidate diffs, release packages, and accepted source roots
  are currently visually close enough to confuse future agents.

## Proposed workspace-level zones

Recommended parent workspace grammar:

```text
/home/sev/ION - Production/
  ACTIVE_REPOS/
  ION_Developement/              # current active repo until renamed/migrated
  dAimon/
  AIM-ION/
  ATLAS/
  Needs_Routed/
  quarantine/
  archive/
  exports/
  mirrors/
```

Do not immediately move active repos. First create an index.

Recommended first index:

```text
/home/sev/ION - Production/WORKSPACE_INDEX.md
```

Recommended fields:

```text
path
owner_project
status
source_truth | candidate | quarantine | archive | mirror | export
active_git_repo
do_not_delete
notes
```

## Proposed repo-internal organization lane

Create a formal ION domain:

```text
DOMAIN_ID: ION_REPO_ORGANIZATION_AND_CARTOGRAPHY
```

Purpose:

```text
Govern folder moves, stale duplicate detection, quarantine, indexes, maps,
summaries, and cleanup receipts.
```

Risk class:

```text
high_context_integrity_surface
```

This domain should prevent agents from making broad moves without:

- before/after map
- source truth classification
- duplicate/stale proof
- cleanup receipt
- rollback route
- index update

## Proposed domain agents

### repo_cartographer

Maps current folders, roots, and ownership.

Outputs:

```text
WORKSPACE_TREE_SNAPSHOT.txt
WORKSPACE_INDEX.md
REPO_SOURCE_ROOT_MAP.md
```

### duplicate_staleness_auditor

Compares apparent duplicates using file lists, hashes, timestamps, and known
authority surfaces.

Outputs:

```text
DUPLICATE_STALENESS_REPORT.md
STALE_CANDIDATE_MANIFEST.json
```

### quarantine_steward

Moves or renames stale folders only after approval.

Outputs:

```text
QUARANTINE_RECEIPT.json
QUARANTINE_INDEX.md
```

### index_scribe

Maintains human-readable maps and summaries.

Outputs:

```text
WORKSPACE_INDEX.md
ION_REPO_INDEX.md
CURRENT_CONTEXT_INDEX.md
```

### codex_cli_workflow_custodian

Maintains Codex skills, hooks, commands, and startup surfaces so agents mount
the right repo and do not confuse workspace roots.

Outputs:

```text
CODEX_WORKSPACE_MOUNT_POLICY.md
CODEX_CLI_ORGANIZATION_COMMANDS.md
```

## Proposed Codex CLI customization

Add a bounded helper later:

```text
ION/04_packages/kernel/ion_repo_organization.py
```

Initial commands:

```text
inspect-workspace
classify-path
compare-duplicates
build-index
write-quarantine-receipt
```

Rules:

- No deletes by default.
- No moves without explicit approval.
- Never treat `ION_Developement/supabase` as duplicate of quarantined Supabase.
- Emit candidate maps before mutation.
- Require receipt for every rename/move/delete.

## Immediate recommendations

1. Keep active Supabase under `ION_Developement/supabase`.
2. Keep quarantined Supabase as evidence for now.
3. Rename quarantined Supabase to `supabase_legacy_pre_baseline_20260513` after approval.
4. Create a parent `WORKSPACE_INDEX.md` before more manual moves.
5. Create `ION_REPO_ORGANIZATION_AND_CARTOGRAPHY` as a formal domain before broad cleanup.
6. Do cleanup in small packets: Supabase quarantine, Needs_Routed intake, candidate diffs/workpackets indexing, current-context runtime evidence indexing.

## Non-claims

No files were deleted by this audit.
No folders were moved by this audit.
No Supabase migrations were run.
No git push or commit is claimed here.
This is candidate organization evidence, not accepted state.
