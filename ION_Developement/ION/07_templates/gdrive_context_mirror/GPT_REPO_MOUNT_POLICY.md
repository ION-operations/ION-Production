# GPT Repo Mount Policy

## Authority boundary

- Live repo: local ION working tree.
- Mirror: Google Drive/read-export copy.
- Production authority: false.
- Live execution authority: false.
- Accepted-state authority: false.
- Google API authority: false.
- Intended Drive account: `crinkedart@gmail.com`
- Intended Drive folder: `google-drive://crinkedart@gmail.com/0ABqIU0r0h-u2Uk9PVA`
- Local Linux/GVFS mount form: `/run/user/<uid>/gvfs/google-drive:host=gmail.com,user=crinkedart/0ABqIU0r0h-u2Uk9PVA`

## Source posture

- `accepted`: tracked/current repo source at export time.
- `candidate`: dirty, untracked, workpacket, diff, or generated candidate.
- `runtime_evidence`: selected current context and receipt summaries.
- `stale_index`: index file may lag actual source-lane contents.
- `archive_witness`: historical witness only.

## GPT behavior

- Cite files and manifest posture when making claims.
- Do not treat the mirror as writable state.
- Do not treat ZIPs, diffs, workpackets, or runtime receipts as accepted law
  unless a settlement receipt says so.
- If a needed file is absent from the mirror, ask for a refreshed mirror or a
  focused export.
