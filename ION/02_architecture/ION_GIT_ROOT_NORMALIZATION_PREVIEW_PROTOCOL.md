# ION Git Root Normalization Preview Protocol

This protocol defines a candidate-only preview for recovering the active ION
shell root when Git still tracks legacy `ION_Developement/` paths while current
source exists at the repository root.

The preview may classify path names, compare ordinary non-risk file content
against tracked Git blobs, and produce candidate path chunks for review.

It must not:

- run `git add`, `git rm`, `git mv`, `git commit`, or `git push`;
- run `git add .` or `git add -A`;
- read or print contents for private/secret-risk path names;
- delete, move, or overwrite files;
- restart services or perform live/production actions;
- claim accepted ION state.

Root normalization remains blocked until an operator-reviewed path packet
accepts the active root model, deletion/archive review, and private-risk path
handling.
