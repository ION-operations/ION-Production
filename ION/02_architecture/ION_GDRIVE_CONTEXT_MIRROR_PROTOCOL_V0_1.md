# ION Google Drive Context Mirror Protocol v0.1

Status: candidate operational protocol
Packet: PCKT-ION-GDRIVE-CONTEXT-MIRROR-001

## Purpose

Provide GPT-001, Sev/ION PRO, and future GPT chats with a curated Google Drive
context mirror of ION without making Google Drive the active repo and without
requiring manual ZIP uploads.

## Core law

- The live repo remains local and is the only working tree.
- Google Drive is a read/export mirror, not the active repo.
- The mirror is curated, source-postured, and manifest-driven.
- Exported files are evidence and mounting material, not accepted state by
  themselves.
- The mirror must not include `.git`, secrets, virtualenvs, caches, raw noisy
  runtime, or credential/vault paths.

## Source posture classes

- `accepted`: current tracked repo material with no local dirty marker at export
  time.
- `candidate`: untracked, dirty, workpacket, diff, or generated candidate
  material.
- `runtime_evidence`: selected current context, receipt summaries, status
  summaries, and generated operational evidence.
- `stale_index`: source-lane indexes that may lag actual loose files.
- `archive_witness`: contained historical material retained as witness only.

## Required export shape

```text
ION_GDRIVE_CONTEXT_MIRROR/
  LATEST.json
  exports/
    <export_id>/
      00_START_HERE/
      01_LATEST_CONTEXT/
      repo/
      EXPORT_MANIFEST.json
      SHA256SUMS.json
      LATEST.json
      TREE_SNAPSHOT.txt
      LATEST_DIFF_STAT.txt
      LATEST_DIFF.patch      optional
```

## GPT mount order

1. Read root `LATEST.json`.
2. Open the referenced export folder.
3. Read `00_START_HERE/START_HERE_FOR_GPT.md`.
4. Read `00_START_HERE/GPT_REPO_MOUNT_POLICY.md`.
5. Read `EXPORT_MANIFEST.json`.
6. Read `01_LATEST_CONTEXT/CURRENT_CONTEXT_SUMMARY.md`.
7. Treat source posture as binding.

## Default mirror path

```text
/home/sev/ION - Production/ION_GDRIVE_CONTEXT_MIRROR
```

## Google Drive account

The intended Drive account is:

```text
crinkedart@gmail.com
```

The intended Drive folder URI is:

```text
google-drive://crinkedart@gmail.com/0ABqIU0r0h-u2Uk9PVA
```

This protocol does not use Google APIs. If Google Drive is mounted locally, the
export builder may receive either a normal local synced folder path or a
`google-drive://<account>/<folder_id>` URI. On Linux/GVFS, the URI resolves to a
local path such as:

```text
/run/user/1000/gvfs/google-drive:host=gmail.com,user=crinkedart/0ABqIU0r0h-u2Uk9PVA
```

The builder copies the generated mirror there only when that destination is
explicitly supplied.

## Non-claims

- No production deployment.
- No git push.
- No accepted-state claim.
- No queue worker authority.
- No live Action/MCP mutation.
- No Google API authority.
