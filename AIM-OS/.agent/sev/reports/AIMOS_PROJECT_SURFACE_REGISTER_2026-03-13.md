# AIMOS Project Surface Register - 2026-03-13

Status: evidence-only register for `CONSOLIDATION-WORK-PACKAGE-01`

Legend:
- `direct-evidence` - verified from this machine/repo in this pass
- `operator-reported-only` - stated by operator or packet, not directly inspectable here
- `inaccessible` - named surface exists in the evidence chain but is not reachable from this machine
- `stale-unknown` - authoritative-looking doc exists but conflicts with current disk evidence

## 1. Branch Register

Current checkout observed in this pass:
- local current branch: `aimos-march-2026-update`
- local branches visible: `aimos-march-2026-update`, `clean-master`, `codexgit-mcp-fallback-offline-comms`, `master`
- remote refs visible: `origin/aimos-march-2026-update`, `origin/clean-master`, `origin/codexgit-mcp-fallback-offline-comms`, `origin/feature/phase-2-hhni`, `origin/main`, `origin/master`
- remote HEAD observed: `origin/HEAD -> origin/feature/phase-2-hhni`

| Branch surface | Evidence tag | Evidence source | Current visible state |
|---|---|---|---|
| `aimos-march-2026-update` | `direct-evidence` | `git branch --show-current`; `git for-each-ref refs/heads` | current local checkout |
| `clean-master` | `direct-evidence` | `git for-each-ref refs/heads` | local branch present |
| `codexgit-mcp-fallback-offline-comms` | `direct-evidence` | `git for-each-ref refs/heads` | local branch present |
| `master` | `direct-evidence` | `git for-each-ref refs/heads` | local branch present |
| `origin/aimos-march-2026-update` | `direct-evidence` | `git for-each-ref refs/remotes` | remote ref present |
| `origin/clean-master` | `direct-evidence` | `git for-each-ref refs/remotes` | remote ref present |
| `origin/codexgit-mcp-fallback-offline-comms` | `direct-evidence` | `git for-each-ref refs/remotes` | remote ref present |
| `origin/feature/phase-2-hhni` | `direct-evidence` | `git for-each-ref refs/remotes` | remote ref present; also remote HEAD target |
| `origin/main` | `direct-evidence` | `git for-each-ref refs/remotes` | remote ref present |
| `origin/master` | `direct-evidence` | `git for-each-ref refs/remotes` | remote ref present |
| other-laptop branch / JOC evolution | `operator-reported-only`; `inaccessible` | operator statement recorded in `.agent/comms/chat/sev/2026-03-13.md`; work package packet | no local or remote ref visible from this machine |

## 2. Direct Repo Surface Register

| Surface | Evidence tag | Primary evidence | Visible state in this pass |
|---|---|---|---|
| AIM-OS repo root | `direct-evidence` | repo root directories including `.agent/`, `packages/`, `scripts/`, `docs/`, `PROJECT_TRUTH/`, `tests/` | active working repository on this machine |
| package surface | `direct-evidence` | `packages/` directory scan | 71 directories total under `packages/`; 70 excluding `__pycache__`; 43 with `__init__.py`; 27 without |
| core package cluster | `direct-evidence` | `packages/cmc_service/`, `packages/hhni/`, `packages/vif/`, `packages/apoe/`, `packages/seg/`, `packages/cas/`, `packages/sis/`, `packages/sdfcvf/` | local kernel/core package surfaces present |
| JOC app surface | `direct-evidence` | `packages/joc/` | local JOC package present |
| JOC-adjacent surfaces | `direct-evidence` | `IDE/`, `packages/joc-tournament/`, `packages/ide_chat_app/` | multiple JOC-labeled or JOC-adjacent UI surfaces exist locally |
| Antigravity extension | `direct-evidence` | `packages/antigravity-extension/` | local extension package present; service layer includes MCP, Gemini CLI, Ollama, IDE automation |
| Echo Forge Loop | `direct-evidence` | `echo-forge-loop/` | local app surface present at repo root |
| Cursor addon | `direct-evidence` | `cursor-addon/` | local Cursor-related surface present |
| transport surface | `direct-evidence` | `lucid_mcp_server.py`, `scripts/mcp_http_fallback_server.py`, `packages/mcp_server/`, `packages/mcp_rag_proxy/`, `packages/mcp_data_integration/`, `scripts/aimos_relay/`, `scripts/aimos_bridge_host.py` | multiple transport and adapter surfaces present in the same checkout |
| provider and host-routing surface | `direct-evidence` | `AGENTS.md`, `scripts/ai_engine/providers/` | host routing and provider adapter code present for Codex CLI, Gemini CLI, and API providers |
| governance and evidence surface | `direct-evidence` | `.agent/`, `PROJECT_TRUTH/`, `docs/` | large local doctrine/evidence surface present |

## 3. Operator-Reported External or Cross-Branch Surfaces

| Surface | Evidence tag | Evidence source | Current visible state |
|---|---|---|---|
| JOC work outside the checked-out branch | `operator-reported-only` | operator statement in `.agent/comms/chat/sev/2026-03-13.md`; `.agent/sev/CONSOLIDATION_WORK_PACKAGE_01_2026-03-13.md` | local JOC code exists, but off-branch or off-machine work is not inspectable from this pass |
| EchoForge work outside the checked-out branch | `operator-reported-only` | operator statement in `.agent/comms/chat/sev/2026-03-13.md`; `.agent/sev/CONSOLIDATION_WORK_PACKAGE_01_2026-03-13.md` | local `echo-forge-loop/` exists, but external or off-branch work is not inspectable from this pass |
| Antigravity extension work outside the checked-out branch | `operator-reported-only` | operator statement in `.agent/comms/chat/sev/2026-03-13.md`; `.agent/sev/CONSOLIDATION_WORK_PACKAGE_01_2026-03-13.md` | local package exists, but external or off-branch work is not inspectable from this pass |
| other-laptop branch / JOC evolution | `operator-reported-only`; `inaccessible` | operator statement in `.agent/comms/chat/sev/2026-03-13.md`; `.agent/sev/CONSOLIDATION_WORK_PACKAGE_01_2026-03-13.md` | no filesystem, git ref, or runtime access from this machine |

## 4. Direct Evidence Notes

- `echo-forge-loop/` exists locally, but `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` still points Echo Forge to `apps/echo-forge-loop/`. This is a current stale-canon mismatch.
- the older runtime truth map says `packages/` had `68` directories with `44` importable and `24` non-importable surfaces. The live directory scan in this pass does not match that older count.
- the direct repo evidence proves local surfaces for JOC, Antigravity extension, Echo Forge Loop, Cursor addon, relay/bridge code, and provider adapters.
- operator-reported external work remains explicitly separate from the local direct-evidence surfaces above.
