# CodexGit Release Slicing Plan (2026-03-03)

## Purpose

Provide a safe, non-destructive path to land current AIM-OS work from a heavily dirty tree into production-ready commits without mixing generated artifacts, volatile memory data, or unrelated prototype churn.

## Repository Snapshot (captured 2026-03-03)

- Branch: `codexgit-mcp-fallback-offline-comms`
- Upstream: `origin/codexgit-mcp-fallback-offline-comms`
- Ahead/behind: `0/0`
- Working tree: `87` unstaged, `119` untracked, `0` conflicts
- Top impact buckets: `cursor-addon (70)`, `docs (59)`, `mcp_memory (24)`, `packages (19)`, `knowledge_architecture (11)`, `backups (7)`, `apps (6)`

Source: `python scripts/git/codexgit_status_report.py --json`

## Key Risk Profile

1. Generated/runtime churn is mixed with source changes (`cursor-addon/out/*`, `*.map`, memory index tags, message logs).
2. Multiple lanes touched simultaneously (`MCP`, `BAS`, `JOC`, docs, experiments), creating high accidental-merge risk.
3. Large untracked surfaces can be accidentally staged in bulk (`docs/*`, `apps/*`, `packages/joc/*`, `packages/shared/*`, `context_capsule_wire_and_mapper_v1/*`).
4. Live collaboration stores are mutable (`mcp_ai_messages.json`, `mcp_timeline_entries.json`, `codex_ai_messages.json`) and should not be release payload.

## Exclude-By-Default Set (do not include in production commits)

- `cursor-addon/out/**`
- `cursor-addon/tests/**/src/*.js`
- `cursor-addon/tests/**/src/*.js.map`
- `**/*.map` (unless intentionally hand-authored)
- `backups/**`
- `mcp_memory/index/tags/**`
- `mcp_ai_messages.json`
- `mcp_timeline_entries.json`
- `codex_workspace/persistence/collaboration/codex_ai_messages.json`
- `tmp_git_push_trace.json`

Note: if any excluded file is intentionally required, stage it explicitly and justify in commit notes.

## Release Slices (ordered)

### Slice 0: already landed

- Commit: `3440c1e298928547a045a950a21bac5d4e546bbf`
- Scope:
  - `docs/BAS_GATE_RECONCILIATION_2026-03-03.md`
  - `scripts/launchers/START_BAS_DETERMINISTIC.ps1`
  - `README.md` (launcher runbook pointer)
- Status: pushed and remote-synced.

### Slice 1: MCP transport/runtime reliability

- Include:
  - `cursor-addon/src/commandServer.ts`
  - `requirements.txt` (only if directly required by MCP runtime fix)
  - `scripts/mcp_http_fallback_server.py` and related launcher docs if changed
- Exclude:
  - `cursor-addon/out/**` and all sourcemaps
- Validation gate:
  - `GET :5001/health` and `GET :5003/health` return `ready=true`
  - `/mcp/list` and `/mcp/execute` pass for `get_ai_messages` and `send_ai_message`

### Slice 2: BAS hardening and API contract stabilization

- Include:
  - `packages/browser-automation-service/src/**`
  - `packages/browser-automation-service/tests/**`
  - `packages/browser-automation-service/package.json`
  - `packages/browser-automation-service/tsconfig.json`
  - `packages/browser-automation-service/README.md` (if API/runbook changed)
- Conditional include:
  - `packages/browser-automation-service/package-lock.json` (only if dependency graph changed intentionally)
- Validation gate:
  - `npm --prefix packages/browser-automation-service run build`
  - `npm --prefix packages/browser-automation-service test` (or documented substitute)
  - BAS health + smoke gates 1-6 pass

### Slice 3: JOC and shared contract surfaces

- Include:
  - `packages/joc/**`
  - `packages/shared/**`
  - `ide_orchestration/prototypes/dac/**` (only if required for active JOC/BAS seam)
- Validation gate:
  - TypeScript compile clean for JOC package(s)
  - Dispatch/session paths validated against BAS-backed IDs (no mock-only regressions)

### Slice 4: docs and governance packetization

- Include:
  - Curated docs supporting shipped behavior and runbooks
- Exclude from first pass:
  - speculative drafts not tied to merged code
  - duplicate or superseded documents without owner sign-off
- Validation gate:
  - each merged doc references a concrete runtime surface or operational gate

### Slice 5: experimental/prototype payloads (deferred lane)

- Paths currently high-risk/noise:
  - `apps/Globe/**`
  - `apps/HyperRealH20Monolith/**`
  - `apps/OpusMagnusWater/**`
  - `apps/forcing_test_quick/**`
  - `apps/mlsmpmsplashdrafts/**`
  - `IDE/**`, `UIeditor/**`, `forcing_test_flip/**`
  - `context_capsule_wire_and_mapper_v1/**`
- Policy:
  - move to dedicated feature branches and land only with explicit product acceptance criteria.

## Safe Execution Commands

```powershell
# 1) Baseline
python scripts/git/codexgit_status_report.py

# 2) Stage one slice only
git add <explicit-file-list>
git diff --cached --stat
git diff --cached

# 3) Commit
git commit -m "<slice-scoped message>"

# 4) Push
git push origin <branch>
```

## Rollback Strategy

- Preferred rollback per slice:
  - `git revert <commit_sha>`
- Multi-commit rollback:
  - revert newest-to-oldest in order, push reverts, do not rewrite shared history.
- Avoid:
  - `git reset --hard`
  - force push on shared integration branches

## Ownership and Parallelization

- `Codex-MCP`: Slice 1
- `Codex-BAS`: Slice 2
- `Claude Opus 4.6` + JOC lane: Slice 3
- `Agent Aether` adjudication: Slice 4 acceptance and Slice 5 deferral policy
- `CodexGit`: sequencing, staging hygiene, rollback enforcement

## Definition of Done

1. Each slice has isolated commit(s) with explicit path scope.
2. Generated/runtime artifacts are excluded by default.
3. Validation evidence exists per slice gate.
4. Rollback can be executed using `git revert` only.
5. No accidental cross-lane file mixing in the same commit.
