# Codex Chat/IDE Specialist Brief
**Date:** 2025-01-28  
**Scope:** DAC v2 IDE foundations + Aether Chat/IDE initiatives  
**Owner:** Codex (Chat/IDE Integration Specialist)

---

## 1. Mission Context
- AIM-OS is converging on a unified chat + IDE surface that fuses conversational flow, APOE orchestration, and subsystem telemetry so the upcoming synthesis session can wire a production-ready experience (`ide_orchestration/prototypes/dac/docs/SYNTHESIS_PREPARATION_GUIDE.md:1`).  
- The DAC v2 IDE prototype already supplies a 90% complete foundation with Zustand state management, standardized panels, hook enhancements, and layout presets to host future chat/panel combos (`ide_orchestration/prototypes/dac/README.md:1`).  
- Aether Chat’s documentation suite (L0–L4, orchestration plan, systems analysis) captures the intended behavior of the unified chat/IDE experience across research, design, and orchestration layers (`ide_orchestration/prototypes/dac/docs/AETHER_CHAT_MASTER_SUMMARY.md:1`).  
- Dynamic Unified Orchestration defines the three-layer governance (Strategic → Tactical → Execution) that will drive deep-thinking modes once the chat/IDE connects to every AIM-OS subsystem (`ide_orchestration/prototypes/dac/docs/DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md:1`).

---

## 2. Historical Systems & Lessons
1. **Manager AI Chat lineage** – Prior production-grade chat systems (Manager AI, Lucid Chat, Dual AI) already implemented topic graphs, orchestration-aware prompting, and MCP-backed tool flows. The comprehensive audit enumerates 17+ core Aether Chat docs plus earlier systems for reuse and modernization (`ide_orchestration/prototypes/dac/docs/AETHER_CHAT_IDE_COMPREHENSIVE_AUDIT.md:1`).  
2. **Aether Chat blueprints** –  
   - Unified chat interface layering chat, coding, orchestration, topics, and AIM-OS integration in a React/TypeScript stack (`AETHER_CHAT_MASTER_SUMMARY.md:15`).  
   - Implementation roadmap: 5 phases (chat UI, coding, orchestration, advanced features, testing/docs) ready for execution once the synthesis gate opens (`AETHER_CHAT_STATUS.md:1`).  
   - Epic orchestration plan: 5-week cadence, 3 specialized agents + Aether, success defined as hooks hitting real backends, ICIP for generation, sandbox execution, and VIF-enforced quality gates (`AETHER_CHAT_EPIC_ORCHESTRATION_PLAN.md:1`).  
3. **DAC v2 IDE learnings** –  
   - Low-level infrastructure (Zustand stores, panel frameworks, hook system) already built for multi-panel experiences. The IDE can host chat surfaces, code panes, dashboards, and timeline panels simultaneously, aligning with Aether Chat’s need for topics + orchestration context (`ide_orchestration/prototypes/dac/README.md:1`).  
   - Shared components (confidence badges, contradiction alerts, status indicators) provide native visualization of VIF and CAS signals, key for chat/IDE trust dashboards.  
4. **Deep search & thinking modes** –  
   - Research docs (AETHER_CHAT_AH_PROTOCOL_ANALYSIS, AETHER_CHAT_AIMOS_SYSTEMS_ANALYSIS) specify A-H protocol driven flows, multi-hop research chains, and MCP-assisted “thinking” states. These map to the Dynamic Unified Orchestration’s layered pattern set and can be embedded as interactive “thinking mode” panels that call APOE plans + RAG pipelines.  
   - Orchestration design insists on quality gates, context management, and communication discipline, ensuring “deep search” actions run as APOE plans with explicit metrics (`DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md:1`).

---

## 3. Integration Requirements Snapshot
| Layer | Key Requirements | Source |
| --- | --- | --- |
| UI / Panels | Chat view + coding panes + topic navigator + orchestration HUD must coexist; leverage DAC v2 base panel + layout systems for drag/drop presets | `ide_orchestration/prototypes/dac/README.md:20` |
| State & Hooks | Persist chat/topic state in Zustand stores, reuse enhanced hooks with TTL/retry/backoff for AIM-OS service calls | `ide_orchestration/prototypes/dac/README.md:17` |
| Orchestration | APOE handle plan execution, topic-level prompt chains, quality gates; implement the 5-week roadmap phases for incremental integration | `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_STATUS.md:1` |
| Subsystem Wiring | All 7 AIM-OS systems (CMC, HHNI, VIF, SEG, CAS, TCS, APOE) must expose real hooks (no mocks) with VIF, CAS, and CMC telemetry piped into the chat/IDE interface | `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_MASTER_SUMMARY.md:53` |
| Collaboration | Follow the 4-agent orchestration plan (backend, code, frontend, coordinator) for parallel delivery with AGENT_COORDINATION_BOARD cadences | `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_EPIC_ORCHESTRATION_PLAN.md:1` |

---

## 4. Deep Thinking & Search Modes
- **A-H Protocol Alignment:** Chat sessions adopt the A-H protocol (Intent → Hypothesis → Evidence → Review). Panels should visualize each stage (e.g., timeline view for Hypothesis, code panel for Evidence).  
- **Dynamic Thinking Modes:**  
  1. *Research Mode* – Connects to Manager AI research flows, uses MCP toolchains, logs context slices into CMC and HHNI for retrieval.  
  2. *Execution Mode* – Triggers APOE plans with plan_execution atoms feeding CMC, surfaces plan progress + VIF gates inline.  
  3. *Synthesis Mode* – Taps SEG and CAS outputs to highlight contradictions, derived insights, and prompts next actions.  
- **Quality & Confidence:** Use VIF witness panels + CAS summaries inside the chat UI so each reasoning hop shows provenance and quality metrics (these components already exist inside DAC v2 base panels).  
- **Topic Graph + Timeline:** Topic manager mirrors the Obsidian-style graph described in the master summary; timeline integration uses TCS events so thinking modes can rewind/resume.

---

## 5. Recommended Next Actions
1. **Archive & link references** – Build a quick-access index (maybe via `MASTER_INDEX_AND_SYSTEM_MAP.md`) pointing to Aether Chat docs, DAC v2 README sections, dynamic orchestration design, and the comprehensive audit so future work reuses existing analysis.  
2. **Map DAC panels → Chat needs** – Propose which existing panels (TimelineView, SystemIndexBrowser) evolve into chat/IDE modules vs. which require new React components (ChatSurface, TopicGraph, APOE HUD).  
3. **Prototype Thinking Mode flows** – Use the enhanced hook system to wire a “Research Mode” flow that hits CMC/HHNI/SEG, demonstrating how deep search and reasoning look within the IDE.  
4. **Prepare orchestration-ready tasks** – Align upcoming synthesis agenda blockers (APOE→CMC PR, TCS imports, HHNI E2E) with the orchestration roadmap milestones so implementation can begin immediately post-synthesis.  
5. **Document guardrails** – Mirror sandbox/tier rules (especially for APOE integrations) in a chat/IDE build checklist to avoid regressions when hooking sensitive systems into the UI.

---

## 6. Personal Follow-Ups
- [ ] Assemble design excerpts (diagrams, hook signatures) from Aether Chat L2/L3 docs for quick embedding into IDE requirements.  
- [ ] Pair with Aether on orchestration-enabling tasks (Command Server endpoints, MCP tool manifests) needed to make the chat/IDE panel functional.  
- [ ] Draft a “Thinking Mode” UX note describing UI states, required data, and validation instrumentation for each mode.  
- [ ] Keep registry/router artifacts in sync as new chat/IDE subtasks emerge from synthesis decisions.

— Codex
