# AIM‑OS Substrate – Current State (November 2025)

> **Purpose**: Give Grok (and any external collaborator) a single document that describes what is already live, what just landed, and what remains before Wave 1 locks. Everything below reflects the real Cursor/VS Code deployment that the team uses every day.

---

## 1. Executive Summary

- **Status**: The AIM‑OS substrate (CMC + HHNI + VIF + APOE + SEG + MCP command server + IDE UI) is running in production-like fashion on localhost:5001 and drives daily development. This is already a fully stateful, evidence-native IDE, not a prototype.
- **Recent wins**: Multi-provider LLM registry + key rotation shipped, MCP server now stores tagged atoms, emits VIF witnesses, and logs timeline events for every API call, and the blocking P0 integration items from Chronos/Sev/Sage are cleared.
- **Wave 1 horizon**: ~2–4 weeks. Remaining work is polishing “intelligent quality gates,” contradiction dashboards, SIS reinforcement automation, tool-surfacing tuning, multi-agent reliability, capability-ledger enforcement, and turn-key autonomous checklists.

---

## 2. What Works Today (Battle‑tested)

| Layer | Highlights |
| --- | --- |
| **Command Server / MCP Stack** | `/mcp/execute` exposes ~80 tools (store/retrieve memory, plan, timeline, CAS metrics, etc.). `send_ai_message` + evidence.jsonl keep Cursor ↔ Electron ↔ MCP in sync. |
| **Chat/IDE UI** | Advanced chat panel in Cursor IDE automatically builds `IntegrationTagContext`, routes MCP calls through `MCPService`, and shows branch reasoning, deep search, APOE toggles, and budget tracking. |
| **CMC (Memory)** | Bitemporal atoms with standardized integration tags (`system:*`, `agent:*`, `mode:*`, `key_index:*`, etc.). All MCP/LLM calls snapshot requests/responses, costs, latencies, and references. |
| **HHNI (Retrieval)** | API responses and knowledge snippets get indexed; RAG middleware filters MCP tools based on recent context. |
| **VIF (Confidence)** | κ-gate enforcement (Critical 0.95, Important 0.85, Routine 0.70) with provider-specific baselines. Every LLM call emits a VIF witness referencing the originating atom. |
| **APOE** | Chain specs + `run_chain.py`, PlanExecutor + witness stamping. Plans can invoke LLM registry clients and store the provenance automatically. |
| **SEG / SDF‑CVF** | Quartet parity (code/docs/tests/evidence) enforced. Contradiction detection exists, though dashboarding is the remaining polish. |
| **CAS / Meta** | Cognitive monitoring hooks stream load metrics into LLM prompts, and CAS can track provider usage patterns. |
| **TCS / Chronos** | Timeline entries created for each LLM/API call (provider, model, key index, tokens, latency, cost) enabling replay, retrospectives, and context seeding. |

---

## 3. Latest Upgrades (January 2025 Checkpoints)

1. **LLM API Registry (packages/api_service_registry/llm/)**  
   - `LLMClient` abstraction, `APIKeyManager` with full 22-key rotation/quota tracking, Gemini + Cerebras clients, and registry entrypoints for both agents and MCP.
2. **MCP Server Integration**  
   - `lucid_mcp_server.call_api` now routes through the registry, handles rotation + fallback, and surfaces quota exhaustion events.  
   - Atlas/Sage/Chronos hooks implemented: CMC storage, VIF witness creation, and TCS timeline logging all fire inside the MCP tool.
3. **P0 Issues Closed**  
   - Chronos timeline logging for key rotation events, Sev’s HHNI retrieval scaffolding, and Sage’s key-index accessor were delivered.  
   - Checkpoints 5‑9 (MCP, CMC, VIF, TCS integration + Phase‑1 completion) are marked complete.

---

## 4. Remaining Delta to “Wave 1 Locked”

| Workstream | Current Status | Estimated Effort |
| --- | --- | --- |
| Intelligent quality gates (relevance/density/completeness/thoroughness) | Policies + JSON scaffolding exist; scorer/dashboard needs finishing | 2‑3 days |
| Full contradiction dashboard in SEG | Detection works, dashboard pending | ~1 week |
| SIS reinforcement loop (auto-open remediation atoms) | Manual flow works; needs automation | 3‑4 days |
| Dynamic tool surfacing (RAG filters) | ~85 % stable; requires 100 “mismatch” atoms for tuning | Few days of logging/tuning |
| Multi-agent handoff protocol (4 Cursor agents) | Works 90 % of the time; rare message loss | Reliability patch + ack protocol |
| Capability ledger + authority map enforcement | Implemented but soft-gated; need to flip blocking flag | 1–2 days |
| One-click `run_autonomous_checklist` per chapter | Exists but needs UX polish | Short polish cycle |

Parallel to these, Phase‑1 LLM work needs:
- Real-key end-to-end tests (Gemini/Cerebras) including quota/rate-limit/error scenarios.
- HHNI retrieval hook to consume stored LLM atoms (stub already placed).

---

## 5. Offers / Resources on Deck

Grok volunteered to clear any of the following immediately:
1. Finish the intelligent scorer + dashboard (`north_star_project/policy/gates.json` + `scripts/run_chain.py`).
2. Harden multi-agent reliability (Aether/Codex double-write + ack protocol from Chapter 30).
3. Ship the contradiction detector that cross-scans SEG + evidence.jsonl and auto-opens SIS tasks.
4. Package the entire substrate as a “clone + docker compose up” experience (Cursor/VSCode extension + MCP server container).

Deciding which blocker to hand off will accelerate Wave 1 closure.

---

## 6. Immediate Next Steps

1. **Testing** – Run real-key LLM calls via IDE, capture telemetry, and validate CMC/HHNI/VIF/TCS entries. Add negative tests for quota/429/network failures.
2. **HHNI Retrieval** – Wire Sev’s integration so chat/agents can pull “similar LLM responses” directly from HHNI.
3. **Quality Gate & Contradiction Dashboards** – Decide whether to accept Grok’s help; otherwise schedule internal sprint.
4. **Tool Surfacing & Multi-Agent Reliability** – Log mismatch atoms, tune RAG filter, and implement ack protocol for multi-agent loops.
5. **Capability Ledger Enforcement** – Enable blocking logic so only authorized agents invoke high-tier tools.

Once these land, the substrate can self-test, self-validate, and then compile the quaternion geometric kernel as “just another artifact.” Wave 1 will ship with evidence for every path the system takes.

---

## 7. Open Discussion: LLM Context Testing (Route R‑LLM‑API‑004)

- **Docs**:
  - `ide_orchestration/prototypes/dac/docs/LLM_API_CONTEXT_TESTING_TEAM_DISCUSSION.md`
  - `ide_orchestration/prototypes/dac/docs/LLM_API_CONTEXT_TEAM_PROMPT.md`
  - `ide_orchestration/prototypes/dac/docs/LLM_API_CONTEXT_TEAM_STATUS.md`
- **Status**: Discussion live, 0/9 agents have responded. Router + index updated with R‑LLM‑API‑004.
- **Core decision**: Whether to index AIM‑OS documents for LLM context **now**, **later**, or via **hybrid** approach (selective indexing + gating). Needs consensus before enabling HHNI-backed auto-context for the new registry.
- **Questions each agent must answer**:
  1. Preferred indexing strategy (now / wait / hybrid)
  2. Document priority list for initial ingestion
  3. Testing approach for validating context-aware responses
  4. Concerns or blockers with immediate indexing
  5. System-specific recommendations (CMC storage, VIF gating, HHNI retrieval, SEG evidence, etc.)
- **Action**: Notify all agents to respond on their coordination boards via the new prompt; update `LLM_API_CONTEXT_TEAM_STATUS.md` as replies arrive. Consolidate answers back into the discussion doc and feed results into the HHNI retrieval workstream from Section 6.

---

**Owner Notes**
- Progress docs to update as testing completes: `LLM_API_BUILD_PROGRESS_UPDATE_1.md`, `CHAT_IDE_IMPLEMENTATION_PROGRESS.md`, and `agents/codex/COORDINATION_BOARD.md`.
- Keep coordination with Grok/Aether by referencing this brief whenever asking for external help. Everything they need to sync is now in one place.
