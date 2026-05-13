# Git Boundary Audit - 2026-05-13

Status: candidate_evidence
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001

## Observed roots

```text
/home/sev                              existing Git root, safety-blocked, not project source truth
/home/sev/ION - Production             intended workspace root, not yet standalone project repo
/home/sev/ION - Production/ION_Developement/.git
/home/sev/ION - Production/dAimon/.git
/home/sev/ION - Production/AIM-OS/.git
```

## Important finding

The workspace is already under a parent Git root at `/home/sev`, but that root is explicitly safety-blocked by `/home/sev/.gitignore`.

Therefore the project should not use `/home/sev` as the real repo. The intended repo root should be `/home/sev/ION - Production`.

## Current risk

Promoted integration folders now sit beside `ION_Developement`:

```text
ION_GPT/
browser_extension/
mcp/
local_daemon/
systemd/
product_packager/
Cursor/
```

Those folders are outside the current `ION_Developement` Git repo. If `ION/09_integrations/*` deletions are pushed from `ION_Developement` before the workspace root is tracked, the remote source tree will lose those integration files.

## Recommendation

Do not push broad integration deletion from `ION_Developement` as a final source-truth move until `/home/sev/ION - Production` has a governed Git model.

Recommended model:

```text
ION - Production = monorepo root
```

Nested repo histories should be bundled before absorption or explicitly retained as submodules.
