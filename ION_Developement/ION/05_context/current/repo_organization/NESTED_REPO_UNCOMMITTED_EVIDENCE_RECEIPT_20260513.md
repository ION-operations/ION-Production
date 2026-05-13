# Nested Repo Uncommitted Evidence Receipt - 2026-05-13

Status: candidate_evidence
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001
Accepted state authority: false

## Evidence directory

```text
/home/sev/ION - Production/quarentine/nested_repo_worktree_evidence_20260513
```

## Captured for each nested repo

```text
branch
head
remotes
status --short
diff --stat
worktree diff patch
staged diff patch
untracked file list
sha256sums
```

## Repos captured

```text
ION_Developement
dAimon
AIM-OS
```

## Purpose

Git bundles preserve committed history. These files preserve the dirty worktree posture before nested `.git` directories are retired for workspace monorepo conversion.

## Non-claims

- No root Git commit yet.
- No nested source files deleted.
- No accepted-state claim.
