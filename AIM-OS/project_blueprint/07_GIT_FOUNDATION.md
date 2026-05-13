# Git foundation — AIM-ION (orphan repository)

## What changed

AIM-ION is **not** a branch of AIM-OS. The inherited `.git` directory (history, `origin`, branches) was **removed** and replaced with:

- **New repository:** `git init -b main`
- **Single root commit** containing the working tree (subject to `.gitignore`)

There is **no** git-level ancestry to `812bc34a…` or any prior commit — only **documented** lineage in `manifests/INITIAL_REPO_AUDIT.md` and the initial commit message body.

## Why orphan history

- Clean **legal/identity boundary** for a renamed or spun-out product (“AIM-ION”).
- No accidental `git push` to the old `AIM-OS` remote.
- Smaller clone if you later filter or LFS-migrate without dragging old graph noise.

## Policy

| Topic | Rule |
|--------|------|
| **Remotes** | Empty until you add `origin` intentionally. |
| **Default branch** | `main` |
| **Secrets** | Never `git add -f` `.env` or vault files; keep `.gitignore` strict. |
| **Large trees on disk** | `Documentation_Consolidated/` may exist locally but is **ignored** — decide in a follow-up if AIM-ION should track it (Git LFS or separate artifact store). |

## Files to read next

1. `manifests/INITIAL_REPO_AUDIT.md` — counts, exclusions, lineage table  
2. `manifests/COMMIT_MSG_initial.txt` — text of the root commit message  
3. `99_COPY_PROVENANCE.md` — rsync + refoundation notes  

## When hosting exists (full guide)

**Do not treat “no `origin`” as a broken repo.** Add a remote only when you have an empty upstream repository.

Complete step-by-step (HTTPS, SSH, `gh`, troubleshooting): **[08_GIT_WHEN_READY.md](./08_GIT_WHEN_READY.md)**  
Short checklist: **[manifests/REMOTE_PUSH_CHECKLIST.md](./manifests/REMOTE_PUSH_CHECKLIST.md)**

Use branch protection, required reviews, and (if public) a clear `LICENSE` in root when you publish.
