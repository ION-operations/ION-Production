# FORGE Mission Packet - Codex Runtime Enablement - 2026-03-06

**Status:** Active candidate mission packet  
**Mission owner:** Sev  
**Assigned specialist:** FORGE  
**Recommended host:** GPT-5.4 or Codex CLI  
**Mission class:** Runtime enablement / protocol hardening / implementation sequencing  
**Output location:** `.agent/sev/reports/FORGE_CODEX_RUNTIME_ENABLEMENT_PLAN_2026-03-06.md`

---

## 1. Mission ID + Intent

**Mission ID:** `FORGE-001-codex-runtime-enablement`

**Mission objective:** Define the smallest viable AIM-OS enablement slice that turns Codex CLI and related Codex lanes into properly governed agents with explicit project rule layers, genome/protocol injection points, and verification steps.

---

## 2. Northstar Mapping

This packet converts abstract genome and runtime doctrine into an actionable Codex-specific enablement plan.

This supports:
- reliable Codex staffing
- repeatable Codex agent spawning
- less hidden host behavior
- a path from doctrine to runnable infrastructure

---

## 3. Read This First

1. `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`
2. `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`
3. `.agent/sev/candidate_genomes/forge.genome.md`
4. `.agent/genomes/GENOME_PROTOCOL.md`
5. `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md`
6. `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md`
7. `docs/CODEX_IDE_MCP_ONBOARDING_V1.md`
8. `.agent/STARTUP.md`
9. `.agent/workflows/startup.md`
10. `C:\Users\bombe\.codex\config.toml`
11. `C:\Users\bombe\.codex\rules\default.rules`

---

## 4. Scope Boundaries

## 4.1 In scope

- Codex CLI project rule and genome injection surfaces
- Codex-specific startup/protocol layering
- minimum viable file plan for AIM-OS Codex enablement
- exact verification steps for future implementation
- one local report in `.agent/sev/reports/`

## 4.2 Out of scope

- broad multi-host governance rewrites
- live changes to user-home config as part of this packet
- unrelated JOC or browser work
- global identity canon promotion

---

## 5. Implementation Expectations

### Allowed behavior

- inspect repo docs and host config
- design a minimal Codex project layer
- recommend exact files to add, edit, or generate
- define verification steps and rollback posture

### Forbidden behavior

- proposing a grand clean-room rewrite
- assuming Codex CLI and Cursor Codex are the same host
- shipping changes without a clear verification plan

---

## 6. Required Deliverable

Create:
- `.agent/sev/reports/FORGE_CODEX_RUNTIME_ENABLEMENT_PLAN_2026-03-06.md`

Required sections:

1. **Executive summary**
   - 5-8 high-signal conclusions
2. **Enablement target**
   - what a "governed Codex lane" should minimally include
3. **Smallest viable implementation slice**
   - exact sequence
   - what to do first
   - what to defer
4. **Exact file plan**
   - files to add
   - files to edit
   - purpose of each
5. **Verification plan**
   - how to prove the layer works
6. **Risks and dependencies**
   - what could break
   - what depends on Relay or Opus findings

---

## 7. Recommended Surfaces To Analyze

- `C:\Users\bombe\.codex\config.toml`
- `C:\Users\bombe\.codex\rules\default.rules`
- Codex system skills under `C:\Users\bombe\.codex\skills\`
- `.agent/STARTUP.md`
- `.agent/workflows/startup.md`
- `.agent/genomes/*`
- any missing AIM-OS-specific `codex.md` or equivalent project layer

---

## 8. Suggested MCP / Host Usage

- optional MCP: `retrieve_memory`, `get_timeline_entries`, `store_memory`
- if MCP is unavailable, continue using repo + host config only
- do not force an MCP dependency just to complete the plan

---

## 9. Reporting Format

Every meaningful update from FORGE should use:

### A. What changed
- exact design surfaces inspected or plan sections completed

### B. Assumptions
- what is inferred versus proven

### C. Merge impact
- planning only, no runtime mutation

### D. Drift check
- confirm no live host config was rewritten

### E. Validation result
- whether the proposed slice is specific enough to implement

### F. Next move
- immediate next design or dependency check

### G. Deliverable summary
- What
- Where
- How to verify

---

## 10. Escalation Triggers

Escalate back to Sev if:
- the minimal slice still requires unresolved Antigravity or Relay decisions
- the host lacks a stable project-level injection point
- the plan would require replacing too many legacy surfaces at once

---

## 11. Definition of Done

Mission is done when:
- the enablement plan exists at the specified path
- the file plan is specific enough for a follow-on implementation packet
- Sev can assign the first Codex runtime build slice without reopening the whole design problem
