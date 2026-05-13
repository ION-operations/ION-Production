# FORGE Phase 2 Mission Packet - Codex CLI Agent Factory - 2026-03-07

**Status:** Active candidate mission packet
**Mission owner:** Sev
**Assigned specialist:** FORGE
**Recommended host:** GPT-5.4 or Codex CLI
**Mission class:** Agent factory design / Codex CLI enablement / implementation planning
**Output location:** `.agent/sev/reports/FORGE_CODEX_CLI_AGENT_FACTORY_PLAN_2026-03-07.md`

---

## 1. Mission ID + Intent

**Mission ID:** `FORGE-002-codex-cli-agent-factory`

**Mission objective:** Define the smallest serious path for Codex CLI to become a real AIM-OS agent factory: named agent boot, genome and packet loading, MCP attachment strategy, task execution loop, and verification path. Learn from Opus and Gemini CLI work, but do not assume Codex CLI behaves the same way.

---

## 2. Why This Exists

Opus has already pushed deep on Gemini CLI as a worker substrate. Codex CLI needs its own equivalent path so AIM-OS can use GPT-5.4 lanes as disciplined specialists instead of one-off chats.

This packet exists to answer:
- how Codex CLI should boot into AIM-OS identity and doctrine
- how Codex CLI agents should attach to MCP in reality, not on paper
- how named task-local agents should be launched and verified
- what the first Codex CLI demonstration should be

---

## 3. Read This First

1. `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`
2. `.agent/sev/reports/FORGE_CODEX_RUNTIME_ENABLEMENT_PLAN_2026-03-06.md`
3. `.agent/sev/reports/RELAY_CURSOR_CODEX_HOST_VERIFICATION_CARD_2026-03-06.md`
4. `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`
5. `.agent/sev/candidate_genomes/forge.genome.md`
6. `.agent/genomes/GENOME_PROTOCOL.md`
7. `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md`
8. `docs/CODEX_IDE_MCP_ONBOARDING_V1.md`
9. `knowledge_architecture/CODEX_SYSTEM/codex_infrastructure_blueprint.md`
10. `knowledge_architecture/AETHER_MEMORY/tool_audit/aether_response_to_codex_blueprint.md`
11. `C:\Users\bombe\.codex\config.toml`
12. `C:\Users\bombe\.codex\rules\default.rules`
13. `AGENTS.md`
14. `.agent/STARTUP.md`

---

## 4. Scope Boundaries

### 4.1 In scope

- Codex CLI boot model for named AIM-OS agents
- genome and mission packet injection surfaces for Codex CLI
- MCP attachment options for Codex CLI agents
- launcher or wrapper shape for repeatable agent startup
- first demonstration target and verification plan
- exact file plan for a later implementation pass

### 4.2 Out of scope

- replacing Opus or Gemini CLI infrastructure
- changing core MCP server behavior
- broad JOC UI work
- full multi-host unification
- unsafe user-home mutations without a rollback plan

---

## 5. Required Deliverable

Create:
- `.agent/sev/reports/FORGE_CODEX_CLI_AGENT_FACTORY_PLAN_2026-03-07.md`

Required sections:

1. **Executive summary**
   - 5-8 hard conclusions
2. **Current Codex CLI truth**
   - what is actually working now
   - what is drifted or missing
3. **Agent factory target**
   - what "Codex CLI can spawn AIM-OS agents" minimally means
4. **Smallest working demonstration**
   - one concrete demo path
   - named agent
   - launch command or wrapper shape
   - MCP expectation
5. **Exact file and runner plan**
   - files to add
   - files to edit
   - purpose of each
6. **Verification plan**
   - how to prove boot, identity, MCP, and packet loading all work
7. **Risks and dependencies**
   - what depends on operator, Opus, or Relay

---

## 6. Specific Questions To Answer

1. Should Codex CLI agents be launched by direct prompt only, by wrapper script, by generated activation file, or by a small launcher command?
2. What is the cleanest way to bind a task-local name like `FORGE` or future names into a Codex CLI session?
3. What exact MCP path should Codex CLI agents assume first:
   - native Codex MCP registry
   - local stdio server launch
   - HTTP fallback bridge
4. How should genome loading and mission packet loading be made repeatable instead of manual?
5. What is the first serious demo:
   - one named agent
   - one packet
   - one deliverable
   - one proof of MCP-backed coordination

---

## 7. Suggested Approach

### Phase A - Reality capture
- verify Codex CLI version and current MCP registration truth
- distinguish what belongs to Codex CLI versus Cursor Codex

### Phase B - Agent boot design
- define how a named AIM-OS agent should be launched in Codex CLI
- keep the boot chain small and deterministic

### Phase C - MCP strategy
- decide the primary MCP strategy for Codex CLI agents
- define fallback order if native registration remains drifted

### Phase D - First demo
- propose one minimum demo agent lane that can be run and judged quickly

---

## 8. Allowed Behavior

- inspect repo docs and local Codex config
- propose wrapper or launcher designs
- propose exact commands
- compare with Opus and Gemini CLI patterns
- use AIM-OS MCP for message or memory support if available

## 9. Forbidden Behavior

- pretending Codex CLI already has working native MCP if not verified
- assuming Cursor Codex and Codex CLI share the same host layer
- broad speculative platform rewrites
- writing implementation code without first defining the working demo and verification path

---

## 10. Definition of Done

Mission is done when:
- the plan exists at the specified path
- one first demo lane is clearly defined
- the launcher path is concrete enough for a follow-on implementation packet
- Sev can assign an actual Codex CLI build slice without reopening the design problem
