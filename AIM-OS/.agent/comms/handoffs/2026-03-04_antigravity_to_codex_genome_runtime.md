**From:** Antigravity  
**To:** Codex  
**Date:** 2026-03-04  
**Priority:** P0-Critical  
**Subject:** Genome Runtime Backend — Design and Build

---

## Context

We just built the Agent Genome system — 5 markdown genome files that load into agents at conversation start to prevent identity loss. The files are working and live in `.agent/genomes/`. However, the genome system is currently manual — agents need to be told to read the file. We need a runtime that automates loading, evolution, and versioning.

## What Needs To Be Done

Design and implement the Python backend that:
1. **Loads genomes** into agent context at conversation start (platform-specific adapters)
2. **Updates genomes** after sessions (especially the Drift Log)
3. **Versions genomes** with bitemporal tracking (when did this version exist, when was it recorded)
4. **Computes fission scores** — determines when an agent's scope should split
5. **Handles cloning** — creates new agent genomes with delta modifications

"Done" looks like: A Python service that Braden can point any agent platform at, and it handles genome lifecycle automatically.

## Files Involved

| File | What's Relevant |
|------|----------------|
| `.agent/genomes/GENOME_PROTOCOL.md` | How genomes work, format spec |
| `.agent/genomes/antigravity.genome.md` | Template genome (reference implementation) |
| `.agent/genomes/*.genome.md` | All 5 genomes |
| `packages/joc/src/store/agentGenomeStore.ts` | TypeScript types and Zustand store (frontend reference) |
| `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md` | V3 spec for cloning/fission |

## Current State

- 5 genome files written (markdown, ~5-9K each)
- Comms system built (filesystem-first, templates, status files)
- Frontend Agent Builder page exists in JOC (needs UI redesign but types are solid)
- No Python runtime yet — this is greenfield for you

## Blockers / Gotchas

- Each agent platform (Cursor, Gemini CLI, browser) has different injection points. The runtime needs adapters.
- Genome updates should be append-only for Drift Log but overwrite for Status.
- Keep genomes under 300 lines — the runtime should compress aggressively.

## Suggested Approach

1. Start with a simple file-based genome loader (read `.genome.md` → format for context injection)
2. Add session-end hooks that update Drift Log
3. Build versioning on top of CMC (bitemporal storage)
4. Implement fission scoring as a periodic computation
5. Platform adapters last (once the core works)

---

**Status:** 🔴 PENDING  
**Accepted by:** [Codex fills this in]  
**Completed:** [date when done]
