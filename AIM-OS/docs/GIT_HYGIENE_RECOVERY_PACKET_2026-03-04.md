# Git Hygiene Recovery Packet (2026-03-04)

Status: Active  
Owner: Codex (execution), Braden/Aether (adjudication)  
Branch Snapshot: `codexgit-mcp-fallback-offline-comms` @ `0c13c65e6`

---

## 1) Current Drift Snapshot

Working tree counts:
- Tracked modifications: `89`
- Untracked paths: `125`

Largest noisy areas:
- `cursor-addon/` (`61` tracked + `9` untracked)
- `docs/` (`61` untracked)
- `mcp_memory/` (`5` tracked + `19` untracked)
- `packages/` (`14` tracked + `10` untracked)

---

## 2) Root Causes

1. Mixed artifact policy
- Some build outputs are tracked (`cursor-addon/out/*`).
- Other generated runtime state is untracked (`mcp_memory/index/tags/*`, backups, runtime JSON files).

2. Runtime/sensitive files in working tree
- Browser automation local account/vault files and script state are appearing as untracked.

3. Broken gitlink/submodule state
- Git has mode `160000` entries with no `.gitmodules` mapping:
  - `knowledge_architecture/applications/ide_chat_app/analysis/braden_previous_builds/ide_builds/Cloud Ai App/project`
  - `tmp/3d-canvas-studio`

---

## 3) Safe Changes Applied Now

Updated [`.gitignore`](C:/Users/bombe/OneDrive/Desktop/AIM-OS/.gitignore) with a dedicated local-runtime section for:
- `backups/`
- `mcp_ai_messages.json`
- `mcp_timeline_entries.json`
- `codex_workspace/persistence/collaboration/*.json`
- `mcp_memory/index/tags/*.json`
- `packages/browser-automation-service/browser-automation-accounts.json`
- `packages/browser-automation-service/browser-automation-vault.json`
- `packages/browser-automation-service/browser-automation-scripts/`
- `SHARED_MESSAGE_BOARD_ANTIGRAVITY.md`

Important:
- Ignore rules do not remove already tracked files from git history/index.

---

## 4) Required Decisions (Human Gate)

### Decision A: Build outputs in `cursor-addon/out/*`
Choose one:
1. Keep tracked (current behavior): accept frequent churn.
2. De-index and ignore compiled outputs: source-of-truth becomes `cursor-addon/src/*`.

Recommendation: `2` for long-term stability.

### Decision B: Broken gitlinks
Choose one:
1. Restore as real submodules (create `.gitmodules`, pin refs).
2. Convert to normal directories/files in main repo.
3. Remove from index and ignore as local sandboxes.

Recommendation:
- `tmp/3d-canvas-studio` -> option `3`
- `Cloud Ai App/project` -> option `2` or `3` depending on whether this content is still needed in AIM-OS.

### Decision C: `docs/` untracked packet set
Choose one:
1. Stage as canonical docs now.
2. Move non-canonical docs into an ignored staging folder.

Recommendation: `1` for canon docs; `2` for drafts/scratch.

---

## 5) Execution Plan After Decision

Phase 1: Index Repair
- De-index selected generated files (non-destructive to local content):
  - `git rm -r --cached <paths>`
- Commit hygiene baseline.

Phase 2: Canonical Stage
- Stage intended runtime changes and canonical docs only.
- Commit with bounded scope.

Phase 3: Guardrails
- Add `pre-commit` checks:
  - block secret/runtime vault files
  - block accidental `out/` artifacts (if decision A=2)
  - block orphan gitlinks without `.gitmodules`

---

## 6) Immediate Next Step

After Braden/Aether confirms Decisions A/B/C, execute cleanup in one controlled commit:
- `chore(git): baseline hygiene cleanup + ignore policy`

