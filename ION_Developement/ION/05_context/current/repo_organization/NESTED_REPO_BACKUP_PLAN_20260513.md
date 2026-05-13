# Nested Repo Backup Plan - 2026-05-13

Status: candidate_plan
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001

## Purpose

Before converting `/home/sev/ION - Production` into the main Git repo, preserve the current nested Git histories.

## Repos requiring backup

```text
ION_Developement
dAimon
AIM-OS
```

## Backup artifact target

```text
/home/sev/ION - Production/quarentine/git_bundles_20260513/
```

## Candidate commands, not executed by this packet

```bash
mkdir -p "/home/sev/ION - Production/quarentine/git_bundles_20260513"

git -C "/home/sev/ION - Production/ION_Developement" bundle create "/home/sev/ION - Production/quarentine/git_bundles_20260513/ION_Developement_20260513.bundle" --all

git -C "/home/sev/ION - Production/dAimon" bundle create "/home/sev/ION - Production/quarentine/git_bundles_20260513/dAimon_20260513.bundle" --all

git -C "/home/sev/ION - Production/AIM-OS" bundle create "/home/sev/ION - Production/quarentine/git_bundles_20260513/AIM-OS_20260513.bundle" --all
```

## Metadata to record

For each nested repo:

```bash
git -C <repo> branch --show-current
git -C <repo> log --oneline -5
git -C <repo> remote -v
git -C <repo> status --short
```

## Rule

Do not remove or replace nested `.git` directories until the bundle files exist and have been verified with:

```bash
git bundle verify <bundle>
```
