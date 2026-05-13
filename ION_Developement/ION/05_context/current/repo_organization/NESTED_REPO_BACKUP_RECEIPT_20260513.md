# Nested Repo Backup Receipt - 2026-05-13

Status: candidate_evidence
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001
Accepted state authority: false

## Backup directory

```text
/home/sev/ION - Production/quarentine/git_bundles_20260513
```

## Bundles created and verified

```text
ION_Developement_20260513.bundle  8.1M  sha256 b9165297938fea5eaf21febee02283b0619fee56c2e47d65c8042339a31532f1
dAimon_20260513.bundle            212K  sha256 459f3d47b94b74462fed77ed8504a7c03adb36e239f626258157b35f7b86c8e7
AIM-OS_20260513.bundle            61M   sha256 89b457ce68ac7a4e12dfcf23c18a6758afd50bd617c6abdd6bb2008ce5505e24
```

## Metadata files

```text
/home/sev/ION - Production/quarentine/git_bundles_20260513/NESTED_REPO_BACKUP_METADATA_20260513.md
/home/sev/ION - Production/quarentine/git_bundles_20260513/SHA256SUMS.txt
/home/sev/ION - Production/quarentine/git_bundles_20260513/BUNDLE_SIZES.txt
```

## Verification posture

`git bundle verify` was run for each bundle and recorded in the metadata file.

## Non-claims

- No nested `.git` directories removed.
- No root repo initialized.
- No files deleted.
- No push.
- No accepted-state claim.
