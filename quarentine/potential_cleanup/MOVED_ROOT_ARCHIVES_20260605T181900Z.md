# Moved Root Archives - 2026-06-05T18:19:00Z

## Scope

The operator approved moving cleanup candidates into `quarentine/` for root
cleanliness. This packet moved only root-level ZIP package artifacts that were
already ignored by `.gitignore` through the global `*.zip` rule.

No source directories, tracked files, tracked deletions, or modified tracked
files were moved.

Destination:

```text
quarentine/potential_cleanup/moved_artifacts/20260605T181900Z/root_archives/
```

## Moved Files

| File | Bytes |
|---|---:|
| `ATLAS.zip` | 1964087 |
| `ION.zip` | 142043562 |
| `ION_.zip` | 276424277 |
| `ION__.zip` | 474384064 |
| `ION_GPT.zip` | 272291529 |
| `ION_VNEXT.zip` | 1871241 |
| `ION_VNEXT_.zip` | 1885916 |
| `Needs_Routed.zip` | 85594361 |
| `Needs_Routed_.zip` | 95660630 |
| `browser_extension.zip` | 603063 |
| `dAimon.zip` | 172578731 |
| `supabase.zip` | 25541 |

Total bytes moved: `1525327002`.

## Verification

- `find . -maxdepth 1 -type f -name '*.zip'` returned no root-level ZIP files.
- `git check-ignore -v` confirmed moved archive paths remain ignored by
  `.gitignore:54:*.zip`.
- `git status` does not show the moved archive files because they remain ignored.

## Boundaries

- No file deletion.
- No `git rm`.
- No tracked-state hiding.
- No Git push.
- Remaining tracked deletion and source-like untracked families still require
  explicit owner review before relocation or staging.
