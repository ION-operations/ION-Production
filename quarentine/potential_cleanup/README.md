# Potential Cleanup Quarantine Index

This folder records cleanup candidates without mutating them.

Boundary:
- No file deletion.
- No file moves.
- No `git rm`.
- No tracked-state hiding through `git update-index`.
- `.gitignore` may only hide generated, local, cache, diagnostic, or raw-run residue.

Important Git fact:

Tracked deletions remain visible even when a matching path is added to
`.gitignore`. They require an explicit deletion/staging decision later. This
folder lists those candidates for review only.

Use `GIT_CLEANUP_POTENTIAL_20260605T181217Z.md` as the current index for the
June 5, 2026 cleanup pass.
