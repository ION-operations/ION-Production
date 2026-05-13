# Sev Initial Onboarding

Date: 2026-03-06
Prepared from: repo docs, local comms files, and live shell checks

## 1. What Sev Is In This Repo

There are three overlapping versions of Sev:

1. Historical Sev
- documented in `knowledge_architecture/AGENT_ONBOARDING/agents/sev/*`
- role: HHNI specialist and retrieval researcher
- date: mostly 2025-11-18

2. Genome Sev
- documented in `.agent/genomes/sev.genome.md`
- role: executive co-leader, strategic advisor, code reviewer
- date: 2026-03-06

3. Governance reality
- `docs/roundtable/IDENTITY_CANON.md` still excludes Sev
- canonical comms folders exist for `aether`, `antigravity`, `codex`, `composer`, `gemini`
- no `sev` inbox/status/lock path exists yet

Practical conclusion:
- Sev is conceptually present
- Sev is not fully operationalized in the active governance model
- safe startup means using a shadow workspace first, then promoting only with explicit authority

## 2. Current Live Runtime Snapshot

Fresh checks from this shell on 2026-03-06:

- `scripts/mcp_control.ps1 -Action status`
  - `:5001` not listening
  - fallback server process not found
  - health unreachable
- `http://127.0.0.1:8000/health` unreachable
- `http://127.0.0.1:8000/sse` unreachable
- running processes include:
  - `python -u ...\\lucid_mcp_server.py`
  - another `python -u ...\\lucid_mcp_server.py`
  - `python ...\\scripts\\aimos_bridge_host.py chrome-extension://...`
- `5011` is listening

Interpretation:
- MCP code is running in at least one stdio-oriented form
- the shell does not currently see the documented HTTP fallback or SSE endpoints
- the extension host may be the only active outward bridge right now

## 3. Current Project Truth

The current context capsule says:
- baseline operational definition depends on `:5001` health and execution
- `context/01_current_truth.md` recorded `:5001` as healthy on 2026-03-05
- `context/03_tonight_plan.md` shows P0-P4 complete and P5 blocked on `AUTH_READY`

The live shell says:
- the 2026-03-05 transport claim is stale
- any future packet must separate "last documented truth" from "freshly verified truth"

## 4. Command and Governance State

Recent docs are inconsistent:

- `docs/BRADEN_MORNING_DIRECTIVES_2026-03-05.md`
  - Braden is CEO
  - Opus is COO
  - GPT 5.2 is expected to become a co-leader once connected
- `docs/roundtable/IDENTITY_CANON.md`
  - Braden is CEO
  - Opus/Aether owns the COO lane
  - Codex is specialist only
- `.agent/comms/identity_session_locks.json`
  - only a Codex lock is recorded

Operational rule:
- do not "fix" governance by improvisation
- treat conflicting files as evidence of drift, not permission to rewrite command structure

## 5. Sev-Specific Historical Context Worth Keeping

The old Sev onboarding is still useful:
- it preserves HHNI lineage and retrieval expertise
- it contains navigation references into prior integration and verification work
- it documents a hybrid restore pattern: static docs plus MCP memory/timeline retrieval when available

What should be kept:
- HHNI specialist history
- system relationships and retrieval responsibilities
- navigation references into older Sev work

What should be treated carefully:
- any claim that old status is still current
- any assumption that MCP tools are directly reachable in this shell right now

## 6. Recommended Sev Operating Model

For now, Sev should operate as:
- strategic reviewer and context synthesizer
- shadow executive workspace
- non-canonical actor until governance is updated intentionally

That means:
- keep notes here
- avoid posting as Sev into the active comms bus until route ownership is defined
- rely on current context docs plus fresh verification
- escalate identity promotion as a governance task, not a side effect

## 7. High-Value Next Steps

1. Refresh runtime truth docs with a dated transport delta.
2. Determine whether the extension-host bridge is the active ChatGPT MCP path.
3. Decide whether Sev should be formally added to live canon.
4. If formalized, create the full Sev route, lock, status, and startup contract together.
