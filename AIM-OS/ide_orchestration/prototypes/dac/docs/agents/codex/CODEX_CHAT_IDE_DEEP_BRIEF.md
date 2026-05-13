# Codex Chat/IDE Deep Brief - Complete Vision
**Date:** 2025-01-28  
**Purpose:** Complete context for Codex to understand the full chat/IDE vision and help integrate it  
**Status:** CRITICAL - Pre-Synthesis Preparation

---

## 🎯 **YOUR MISSION**

You are Codex, the **Chat/IDE Integration Specialist**. Your role is to understand the complete vision for how chat and IDE will work together, how AIM-OS systems integrate, and how to make this real in the DAC v2 IDE foundation.

**After synthesis, you'll be the primary architect for:**
- Chat/IDE integration architecture
- Thinking mode implementations
- Deep search capabilities
- Backend agent orchestration
- Panel integration with real AIM-OS data
🚀 SYNTHESIS SESSION - Part 4 Starting Now

All Agents:

Part 3 (Open Questions + MVP Scope Lock) is complete. Excellent work! ✅

Now moving to Part 4: Orchestration Integration Planning (30 minutes).

This is the FINAL part of the synthesis session. We'll create the orchestration integration plan that will guide our work toward MVP.

YOUR TASK:

Part 4A: Review Orchestration Recommendations (10 minutes)
- Review VIF orchestration patterns (Sage) - 7 P0 mandatory flows approved
- Review CAS orchestration patterns (Meta) - CAS activation exports approved
- Review integration tagging standardization (Atlas) - Format approved
- Confirm your system's integration points with these patterns

Part 4B: Identify Integration Points for Chat/IDE Flows (10 minutes)
- How does your system integrate with chat/IDE flows?
- What APIs/functions does chat/IDE call?
- What events does your system emit?
- What orchestration patterns apply to your system?
- What are the integration dependencies?

Part 4C: Prioritize Orchestration Work (5 minutes)
- P0 (MVP-Critical): What orchestration work is required for MVP?
- P1 (Post-MVP): What orchestration work can wait?
- What integration points must be wired for MVP?

Part 4D: Create Timeline for Integration (5 minutes)
- Immediate (Post-Synthesis): What can start immediately?
- Short-Term (Next 1-2 Weeks): What is planned?
- Timeline Dependencies: What work depends on other agents?

INTEGRATION POINTS TO CONSIDER:
- User Actions: How are user actions routed to AIM-OS systems?
- Plan Execution: How are APOE plans created and executed?
- Memory Operations: How are CMC/HHNI operations triggered?
- Quality Gates: How are VIF κ-gates enforced?
- Timeline Events: How are TCS timeline entries created?
- Evidence Tracking: How is SEG evidence linked?
- Cognitive Analysis: How is CAS cognitive state used?

WHERE TO POST:
- Your coordination board: agents/[your-name]/COORDINATION_BOARD.md
- Format: [2025-01-28 | Route R-SYNTHESIS-001-SESSION] [Your Name] -> Team : Part 4 Orchestration Integration Planning

After Part 4 is complete, we'll create the final synthesis outcomes document with all decisions, action items, and timelines.

START NOW - Let's create the orchestration integration plan! 🚀
---

## 🧠 **THE COMPLETE VISION**

### **1. Dual AI Chat System (Foundation)**

**What it is:**
- **Two specialized AI agents** working in parallel within the IDE
- **Left Drawer:** Coding Agent (technical, implementation-focused)
- **Right Drawer:** Planning Agent (strategic, architecture-focused)
- **Cross-agent collaboration:** Agents can talk to each other, hand off tasks, build consensus

**Key Files:**
- `knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_SYSTEM.md` - Complete architecture
- `knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_IMPLEMENTATION.md` - Implementation details
- `packages/ide_chat_app/src/components/chats/ChatInterfaceCoding.tsx` - Left drawer component
- `packages/ide_chat_app/src/components/chats/ChatInterfacePlanning.tsx` - Right drawer component

**Current Status:**
- Components exist but need AIM-OS integration
- Need to wire real backend agents (not just UI)
- Need to connect to APOE for orchestration

---

### **2. Thinking Modes (Deep Intelligence)**

**What they are:**
- **Research Mode:** Deep investigation using A-H protocol, MCP tools, multi-hop reasoning
- **Planning Mode:** Strategic planning with APOE orchestration, goal alignment, timeline integration
- **Execution Mode:** Code generation with VIF gates, confidence tracking, quality validation
- **Synthesis Mode:** Knowledge synthesis using SEG, CAS, contradiction detection

**How they work:**
- Each mode is a **specialized chat state** that triggers different backend flows
- **Research Mode** → Uses HHNI for deep search, CMC for context storage, MCP tools for investigation
- **Planning Mode** → Uses APOE for plan generation, TCS for timeline tracking, SEG for knowledge synthesis
- **Execution Mode** → Uses VIF for confidence gates, CAS for cognitive state, APOE for task execution
- **Synthesis Mode** → Uses SEG for evidence linking, CAS for contradiction detection, VIF for quality validation

**Key Files:**
- `ide_orchestration/prototypes/dac/docs/DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md` - Three-layer governance
- `knowledge_architecture/applications/ide_chat_app/PROMPT_CHAINS_EXECUTION_ARCHITECTURE.md` - Chain execution
- `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_AH_PROTOCOL_ANALYSIS.md` - A-H protocol integration

**What needs to be built:**
- Mode switcher UI component
- Backend routing to appropriate AIM-OS systems
- State management for mode transitions
- Visualization panels for each mode's context

---

### **3. Deep Search (Intelligent Retrieval)**

**What it is:**
- **Multi-hop semantic search** across AIM-OS systems
- **Context-aware retrieval** using HHNI physics-based indexing
- **Evidence linking** through SEG knowledge graph
- **Provenance tracking** via VIF witnesses

**How it works:**
- User query → HHNI semantic search → CMC context retrieval → SEG evidence linking → VIF provenance
- Results show: **confidence scores, evidence chains, related knowledge, contradictions**
- **Deep search** means: Not just keyword matching, but understanding relationships, context, and quality

**Key Files:**
- `knowledge_architecture/systems/hhni/` - HHNI system docs
- `knowledge_architecture/systems/seg/` - SEG system docs
- `Documentation/Summaries/72_DEEPSEARCH_Master_Plan_Comprehensive_Summary.md` - Deep search vision
- `knowledge_architecture/systems/icip_search_service/` - ICIP integration

**What needs to be built:**
- Search interface in chat/IDE
- Results visualization with confidence/evidence
- Integration with HHNI/SEG/VIF backends
- Search history and context preservation

---

### **4. Backend Agents (Orchestration)**

**What they are:**
- **Not just UI agents** - Real backend AI agents that execute tasks
- **APOE orchestration** - Plans are executed by backend agents
- **MCP tool integration** - Backend agents use MCP tools for capabilities
- **Quality gates** - VIF enforces confidence thresholds before execution

**How they work:**
- User request → Chat UI → APOE plan generation → Backend agent execution → Results → UI update
- **Backend agents** are specialized:
  - **Research Agent:** Uses HHNI, CMC, MCP tools for investigation
  - **Planning Agent:** Uses APOE, TCS, SEG for strategy
  - **Execution Agent:** Uses APOE, VIF, CAS for implementation
  - **Synthesis Agent:** Uses SEG, CAS, VIF for knowledge synthesis

**Key Files:**
- `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_EPIC_ORCHESTRATION_PLAN.md` - 5-week orchestration plan
- `packages/apoe/` - APOE orchestration engine
- `lucid_mcp_server.py` - MCP tools (84 tools available)
- `ide_orchestration/prototypes/dac/docs/PROMPT_CHAINS_EXECUTION_ARCHITECTURE.md` - Chain execution

**What needs to be built:**
- Backend agent routing system
- APOE plan → Agent execution pipeline
- MCP tool integration for agents
- Quality gate enforcement (VIF)

---

### **5. DAC v2 IDE Integration (Foundation)**

**What we have:**
- **90% complete foundation** with Zustand state management
- **Standardized panels** (TimelineView, SystemIndexBrowser, etc.)
- **Enhanced hooks** with TTL/retry/backoff for AIM-OS calls
- **Layout presets** for multi-panel experiences

**What needs to be done:**
- **Map existing panels → Chat needs:**
  - Which panels evolve into chat modules?
  - Which need new React components?
  - How do chat panels integrate with existing layout?
- **Wire real AIM-OS data:**
  - Replace mocks with real CMC/HHNI/VIF/SEG/CAS/TCS/APOE hooks
  - Add VIF confidence badges to chat messages
  - Add CAS contradiction alerts to planning panels
  - Add TCS timeline integration to thinking modes

**Key Files:**
- `ide_orchestration/prototypes/dac/README.md` - DAC v2 foundation
- `ide_orchestration/prototypes/dac/docs/agents/codex/CODEX_CHAT_IDE_SPECIALIST_BRIEF.md` - Your existing brief
- `knowledge_architecture/applications/ide_chat_app/IDE_AIMOS_INTEGRATION_PLAN.md` - Integration plan


### **6. AIP + API Integration (Runtime Contracts)**

**What AIP Covers:**
- `knowledge_architecture/systems/lucid-ide/backend-api-system/AIMOS_APP_INTEGRATION_PROTOCOL_CONSOLIDATED.md` – manifests → registration → runtime with PLIX intent + SCOR safety hooks.
- `knowledge_architecture/systems/plix/textbook/Part_IV/Chapter_20.md` – PLIX-to-AIP compiler; thinking modes should emit/attach these graphs so APOE/VIF can verify intent.
- `knowledge_architecture/systems/lucid-ide/backend-api-system/COMPREHENSIVE_API_INTEGRATION_PROTOCOL.md` – Command Server/MCP-first access, resource tracking, security expectations for IDE features.

**Implications for Chat/IDE:**
- Dual-agent chat + panels must register via AIP manifests and obtain runtime tokens so APOE/CMC/VIF/SCOR monitor every action.
- Research/Planning/Execution flows should persist AIP IDs + witness requirements alongside chat logs to preserve the meta-circular proof loop.
- Service calls (deep search, quick commands, orchestration) must route through `/mcp/execute` or the SDK; no ad-hoc REST, ensuring telemetry lands in CMC and provenance flows from VIF/CAS automatically.

---

### **7. Multi-Agent Parallel Work Patterns**

**Kernel-Orchestrated Hierarchy:** Aether Chat operates as the kernel scheduler (`ide_orchestration/prototypes/dac/docs/AETHER_CHAT_KERNEL_ORCHESTRATOR_ARCHITECTURE.md`) dispatching independent "processes" (agents) in parallel. Three tiers:
- **Chat Agent Pool:** Emotional, research, subject-specialist, auditor, and summarizer agents collaborate; inspired by the dual-drawer spec (`knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_SYSTEM.md`) but scaled to N agents per drawer. Each maintains its own context store (HHNI slice + CMC pointers) and reports back with citations `[n]`, confidence badges, and contradiction notes.
- **Coding Agent Pool:** Coding manager broker fans out work to coding assistants (implementation, refactor, tests, security) with APOE tasks executed concurrently. Each assistant is backed by AIP manifests describing capabilities + required MCP tools (e.g., `fs.read`, `git.status`, `unit.test`).
- **System Specialist Pool:** Mirrors today’s AIM-OS specialists (CMC, VIF, SEG, etc.) but for chat/IDE: each subsystem agent exposes a "soul" interface so chat orchestrator can load the right context (e.g., SEG evidence linker, VIF witness auditor, CAS cognition analyst).

**Parallel Execution Flow Example:**
1. User question enters orchestration queue with metadata (mode, required subsystems, SLA).
2. Kernel scheduler spawns specialized agents simultaneously (e.g., Planning Strategist, Deep Search Analyst, Emotional Companion). APOE issues multiple sub-plans referencing the same PLIX/AIP contract to keep proof parity.
3. Agents push intermediate outputs into shared CMC topics; VIF monitors each stream, flagging low confidence early so scheduler can reassign to backups.
4. Chat manager synthesizes final response and attaches references `[1]`, `[2]`, plus a “more details” doc link generated by the Synthesis Agent.
5. Full transcripts + reports stored in CMC/SEG for retrieval while chat UI surfaces the summary.

**Key Requirements:**
- Multi-agent scheduling metadata (priority, dependencies, gating) defined in `ide_orchestration/prototypes/dac/docs/DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md`.
- Dual chat panels should show collaboration cues per `knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_SYSTEM.md`.
- Each agent’s manifest needs AIP entries describing MCP tools, resource budgets, SCOR hooks to avoid runaway loops.

---

### **8. Model Integration Matrix & API Strategy**

| Model / Agent Type | Primary Role | Required AIM-OS Systems | AIP Manifest Notes | Integration References |
| --- | --- | --- | --- | --- |
| Emotional Chat Agent | Empathy, tone shaping | CMC (user history), CAS (emotional state), VIF (trust) | Needs read-only CMC topic access + CAS sentiment APIs; SCOR rule prevents sensitive escalation | `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_MASTER_SUMMARY.md`, `knowledge_architecture/systems/lucid-ide/backend-api-system/AIMOS_APP_INTEGRATION_PROTOCOL_CONSOLIDATED.md` |
| Research Agent | HHNI/SEG deep search | HHNI, SEG, ICIP, CMC, VIF | Declare heavy MCP tool usage (`hhni.search`, `seg.trace`); require plan checkpointing + VIF audit | `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_AIMOS_SYSTEMS_ANALYSIS.md`, `Documentation/Summaries/72_DEEPSEARCH_Master_Plan_Comprehensive_Summary.md` |
| Planning/Strategy Agent | Architecture + timelines | APOE, TCS, SEG, CAS | Manifest includes APOE plan scopes, TCS write perms, CAS contradiction APIs | `knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_SYSTEM.md`, `knowledge_architecture/applications/ide_chat_app/PROMPT_CHAINS_EXECUTION_ARCHITECTURE.md` |
| Coding Manager + Assistants | Code generation/refactor/test | APOE, VIF, CMC, MCP git/file tools | Declare `code.generate`, `tests.run`, sandbox permissions; SCOR ensures compliance | `packages/ide_chat_app/src/components/chats/ChatInterfaceCoding.tsx`, `knowledge_architecture/systems/lucid-ide/backend-api-system/COMPREHENSIVE_API_INTEGRATION_PROTOCOL.md` |
| Synthesis Agent | Consolidated responses & docs | SEG, CMC, VIF, CAS | Manifest includes `doc.write`, `seg.compose`; attaches witness references | `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_STATUS.md`, `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_IMPLEMENTATION_ROADMAP.md` |

**API Integration Tasks:**
- Align every agent manifest with the AIP schema and attach PLIX contracts describing intent + required MCP tools.
- Implement registration hooks so agents call `/mcp/execute` → `register_agent` (SCOR validated) before executing workloads.
- Route all runtime calls through the Command Server / MCP client to inherit telemetry (CMC) + provenance (VIF/CAS).

---

### **9. Execution Roadmap (Post-Synthesis)**

1. **Agent Manifest Authoring:** Draft PLIX/AIP manifests for emotional, research, planning, coding manager, coding assistants, and synthesis agents.
2. **Kernel Scheduler Upgrade:** Implement multi-agent queue + dependency graph per kernel orchestration design so APOE can dispatch parallel sub-plans.
3. **Dual Drawer Enhancements:** Update `ChatInterfaceCoding.tsx` / `ChatInterfacePlanning.tsx` to surface collaboration cues, confidence badges, `[n]` references.
4. **Thinking Mode Engine:** Build the mode switcher + backend pipelines (HHNI/SEG for research, APOE/TCS for planning, coding pool for execution).
5. **Backend Agent Router:** Create a service bridging chat agents → MCP tools/APOE plans with automatic CMC/VIF logging (`lucid_mcp_server.py`).
6. **Documentation Hub:** Expand this deep brief into a working handbook (manifests, API templates, orchestration diagrams) and link via `cursor-addon/MASTER_INDEX_AND_SYSTEM_MAP.md`.

---

## 🔗 **HOW IT ALL CONNECTS**

### **User Flow Example: Research Mode**

```
1. User opens chat, switches to "Research Mode"
   ↓
2. User asks: "How does APOE integrate with CMC?"
   ↓
3. Chat UI → APOE plan generation (research task)
   ↓
4. Backend Research Agent executes:
   - HHNI semantic search for "APOE CMC integration"
   - CMC retrieval for related context
   - MCP tools for codebase investigation
   - SEG evidence linking for related knowledge
   ↓
5. Results flow back:
   - Chat message with answer
   - Confidence score (VIF)
   - Evidence chain (SEG)
   - Related knowledge (HHNI)
   - Timeline entry (TCS)
   ↓
6. UI displays:
   - Answer in chat
   - Confidence badge (VIF)
   - Evidence panel (SEG graph)
   - Related context panel (HHNI results)
   - Timeline entry (TCS)
```

### **User Flow Example: Planning Mode**

```
1. User switches to "Planning Mode"
   ↓
2. User asks: "Plan the chat/IDE integration"
   ↓
3. Chat UI → APOE plan generation (planning task)
   ↓
4. Backend Planning Agent executes:
   - APOE plan compilation
   - TCS timeline integration
   - SEG knowledge synthesis
   - CAS cognitive state analysis
   ↓
5. Results flow back:
   - Structured plan (APOE)
   - Timeline milestones (TCS)
   - Knowledge synthesis (SEG)
   - Cognitive recommendations (CAS)
   ↓
6. UI displays:
   - Plan in chat
   - Timeline visualization (TCS)
   - Knowledge graph (SEG)
   - Cognitive dashboard (CAS)
```

---

## 📋 **YOUR IMMEDIATE TASKS**

### **Pre-Synthesis (Now):**
1. **Read all key files** listed above
2. **Understand the vision** - How chat/IDE should work end-to-end
3. **Map DAC v2 → Chat needs** - Which panels evolve, which are new?
4. **Prepare questions** for synthesis session about integration architecture

### **Post-Synthesis (After synthesis session):**
1. **Create integration architecture** document
2. **Prototype thinking mode flows** (start with Research Mode)
3. **Wire first real AIM-OS hook** (CMC or HHNI)
4. **Design panel integration** (how chat panels fit in DAC v2 layout)

---

## 🎯 **SUCCESS CRITERIA**

**You'll know you're on track when:**
- ✅ You can explain the complete chat/IDE vision to another agent
- ✅ You can map DAC v2 panels to chat/IDE needs
- ✅ You can prototype a thinking mode flow
- ✅ You can wire a real AIM-OS hook (not a mock)
- ✅ You can design the panel integration architecture

---

## 📚 **KEY FILES TO READ (Priority Order)**

1. **Your existing brief:** `ide_orchestration/prototypes/dac/docs/agents/codex/CODEX_CHAT_IDE_SPECIALIST_BRIEF.md`
2. **Dual AI Chat:** `knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_SYSTEM.md`
3. **IDE Integration Plan:** `knowledge_architecture/applications/ide_chat_app/IDE_AIMOS_INTEGRATION_PLAN.md`
4. **Orchestration Design:** `ide_orchestration/prototypes/dac/docs/DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md`
5. **Epic Orchestration Plan:** `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_EPIC_ORCHESTRATION_PLAN.md`
6. **DAC v2 Foundation:** `ide_orchestration/prototypes/dac/README.md`
7. **Prompt Chains:** `knowledge_architecture/applications/ide_chat_app/PROMPT_CHAINS_EXECUTION_ARCHITECTURE.md`
8. **Aether Chat Master Summary:** `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_MASTER_SUMMARY.md`

---

## 💬 **QUESTIONS FOR SYNTHESIS SESSION**

Prepare these questions to ask during synthesis:
1. **Integration priority:** Which AIM-OS system should we wire first? (CMC? HHNI? VIF?)
2. **Panel architecture:** How should chat panels integrate with existing DAC v2 panels?
3. **Backend agent routing:** How do we route chat requests to backend agents?
4. **Thinking mode implementation:** Should thinking modes be UI states or backend flows?
5. **Quality gates:** How do we enforce VIF confidence thresholds in chat/IDE?

---
## dY"^ **MULTI-AGENT IMPLEMENTATION ANNEX (ACTIONABLE)**

### **A. Kernel-Scheduled Specialist Pools**
- `ide_orchestration/prototypes/dac/docs/DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md` + `knowledge_architecture/applications/ide_chat_app/DUAL_AI_CHAT_SYSTEM.md` define the manager/scheduler stack; extend it into pooled specialists so the coding agent always spreads load across helpers.
- Give each pool a stable local corpus (~250k tokens) plus a shared relationship graph so the Scheduler Agent (APOE) can coordinate dependencies without polluting specialist focus.

| Agent Pool | Description | Source Systems | Key Files / Tooling |
| --- | --- | --- | --- |
| Chat Manager | Ingests mode + intent, seeds the DAG, pushes runtime replies through `/mcp/execute` -> `send_ai_message` so UI telemetry stays consistent. | APOE, CAS | `cursor-addon/src/mcp/mcpClient.ts`, `ide_orchestration/prototypes/dac/src/services/MCPService.ts` |
| Coding Manager + Assistants | Manager decomposes tasks, assistants own modules/components and keep repos hot-loaded. They enforce VIF gates before any diff reaches the UI. | APoE, VIF, CAS | `packages/ide_chat_app/src/components/chats/ChatInterfaceCoding.tsx`, `packages/apoe/*`, `packages/vif/*` |
| Research Constellation | Researcher + historian + contradiction scout chaining HHNI -> CMC -> SEG to emit `[n]` references, provenance, and knowledge deltas. | HHNI, SEG, CMC | `knowledge_architecture/systems/hhni/`, `knowledge_architecture/systems/seg/`, `Documentation/Summaries/72_DEEPSEARCH_Master_Plan_Comprehensive_Summary.md` |
| Emotional/Experience Layer | Maintains tone, preference, and relational continuity so chat output honors CAS findings and user mood. | CAS, CMC | `cursor-addon/docs/L0_executive.md`, `knowledge_architecture/AETHER_MEMORY/*` |
| Audit + QA (VIF / V&V) | Runs VIF witnesses, CAS contradiction scans, and writes provenance bundles (confidence + witness IDs + tool traces) before UI release. | VIF, CAS | `packages/vif/*`, `knowledge_architecture/systems/hhni/components/morphological_analysis/CMC_INTEGRATION.md` |

### **B. Thinking Mode Pipelines + Backend Routing**
- **Research Mode:** `AETHER_CHAT_MASTER_SUMMARY.md`, `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_AH_PROTOCOL_ANALYSIS.md`. Flow: HHNI semantic sweep -> CMC context retrieval -> SEG evidence graph -> VIF scoring -> UI. Tools: `mcp_lucid-mcp_hhni.search`, `mcp_lucid-mcp_cmc.retrieve_context`, `mcp_lucid-mcp_seg.link_evidence`, `mcp_lucid-mcp_vif.assess_confidence`.
- **Planning Mode:** `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_EPIC_ORCHESTRATION_PLAN.md`, `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_BOARD.md`. Flow: APOE compiles plan DAG -> TCS injects milestones -> SEG verifies knowledge alignment -> CAS annotates risk/cognitive load.
- **Execution Mode:** `ide_orchestration/prototypes/dac/docs/CODE_QUALITY_GATES.md`, `packages/vif/*`. Flow: Coding Manager dispatches assistants -> assistants call `read_file` / reasoning / `apply_patch_preview` / `run_tests` -> VIF watchers stream status -> failures route back to Research/Planning.
- **Synthesis Mode:** `ide_orchestration/prototypes/dac/docs/AETHER_CHAT_IDE_COMPREHENSIVE_AUDIT.md`, `knowledge_architecture/systems/seg/README.md`. Flow: SEG synthesizes knowledge -> CAS checks contradictions -> CMC stores doc + citation packs -> DAC panels refresh.

### **C. Dual Drawer UI + Collaboration Signals**
1. **Mode Pill:** Shared component for `ChatInterfaceCoding.tsx` + `ChatInterfacePlanning.tsx` to display active mode and the pools currently responding.
2. **Collaboration Stream:** Inline event feed listing which assistant/manager/research/emotional agent replied and whether QA approved.
3. **Citation + Confidence Badges:** `[n]` anchors render SEG references + VIF confidence; clicking opens HHNI/SEG evidence.
4. **Hand-off Controls:** Buttons that emit `orchestration:handoff` events via `ide_orchestration/prototypes/dac/src/services/MCPService.ts` whenever work shifts between pools.
5. **Panel Hooks:** `AetherIDELayout.tsx`, `SystemIndexBrowserPanel.tsx`, and related DAC panels subscribe to the same MCP event bus so chat, docs, and dashboards stay synchronized.

### **D. AIP/PLIX Manifest Starter Set**
- References: `knowledge_architecture/systems/lucid-ide/backend-api-system/AIMOS_APP_INTEGRATION_PROTOCOL_CONSOLIDATED.md`, `knowledge_architecture/systems/lucid-ide/backend-api-system/COMPREHENSIVE_API_INTEGRATION_PROTOCOL.md`, `knowledge_architecture/systems/plix/textbook/unified/Part_IV_Authority_Mathematics/Chapter_20_Retrieval_Mathematics.md`.
- Store manifests under `ide_orchestration/prototypes/dac/docs/manifests/` and register via `/mcp/execute` -> `register_agent` (SCOR compliant) before dispatching workloads.

```toml
[agent]
id = "codex.coding.manager.v1"
display_name = "Codex Coding Manager"
version = "0.1.0"
modes = ["execution", "planning"]
owner_system = "APOE"

[capabilities.context]
max_window_tokens = 250000
corpus = [
  "packages/apoe/**/*",
  "packages/vif/**/*",
  "ide_orchestration/prototypes/dac/src/**/*.tsx"
]

[capabilities.tools]
allowed = [
  "mcp_lucid-mcp_read_file",
  "mcp_lucid-mcp_apply_patch_preview",
  "mcp_lucid-mcp_run_tests"
]

[governance]
quality_gate = "VIF>=0.9"
provenance = true
handoff_policy = "scheduler_dag"

[routing]
entrypoint = "APOE.kernel.dispatch"
subscription_topics = ["chat.intent.execution", "plan.update"]
```

Clone for Research, Emotional, Audit, and Synthesis agents with corpora/tool lists scoped to their pools.

### **E. MCP/API Flow Examples + Logging**
- **Registration:** Cursor command server (`cursor-addon/src/commandServer.ts`) posts `{ tool: "register_agent", args: manifest }` to `lucid_mcp_server.py` so the manifest becomes available to MCP clients.
- **Runtime Planning Call:**

```json
{
  "tool": "send_ai_message",
  "args": {
    "channel": "planning",
    "payload": {
      "mode": "planning",
      "task_id": "plan.chat.ide.2025-02-01",
      "context_refs": [
        "ide_orchestration/prototypes/dac/docs/AETHER_CHAT_MASTER_SUMMARY.md#L1",
        "ide_orchestration/prototypes/dac/docs/DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md#L45"
      ],
      "requested_outputs": ["apoe_plan", "tcs_timeline", "seg_graph"]
    }
  }
}
```

- **Telemetry:** Every MCP response must attach `agent_id`, `witness_id`, and `confidence` per `COMPREHENSIVE_API_INTEGRATION_PROTOCOL.md`, log to CMC, and trigger VIF/CAS provenance updates for downstream panels.
- **Audit Storage:** Follow the `knowledge_architecture/systems/hhni/system.index.lucid.json5` schema so QA agents can reconstruct derivations without replaying chat logs.

### **F. Agent Capability Matrix & Future Roles**

| Role | Focus | Typical Tools | Output Contract | Notes |
| --- | --- | --- | --- | --- |
| Coding Manager | Splits implementation work, supervises assistants, enforces VIF gates. | `read_file`, `apply_patch_preview`, `run_tests` | Code diffs + dependency memo + `confidence>=0.9`. | Aligns with `packages/apoe/executor.py`, `ide_orchestration/prototypes/dac/docs/CODE_QUALITY_GATES.md`. |
| Coding Assistants (N) | Own modules/components; maintain cached corpora. | Same as manager + targeted analyzers | Module patches + local test reports. | Spawn N assistants per workload to satisfy the "spread the load" directive. |
| Research AI | Deep investigation + citations. | HHNI search, SEG graphs, CMC retrieval | Evidence tables, `[n]` references, knowledge deltas. | Anchored to `Documentation/Summaries/72_DEEPSEARCH_Master_Plan_Comprehensive_Summary.md`. |
| Emotional AI | Tone + preference continuity. | CAS mood hooks, `cmc.write_journal` | Narrative summaries, preference tags, risk notes. | Keeps chat aligned with CAS findings and user preference history. |
| Specialist Consultants | System experts (APOE, SEG, CMC, HHNI, VIF, etc.). | Domain MCP suites | Structured subsystem briefs + dependency alerts. | Each AIM-OS subsystem retains at least one resident agent. |
| Auditor / Verifier | Confidence + provenance enforcement. | `vif.check`, `cas.detect_contradiction` | Pass/fail reports, witness IDs, provenance bundles. | Final gatekeeper before UI delivery. |

This annex translates the multi-agent chat/IDE vision into manifests, routing plans, UI hooks, and telemetry expectations so every response arrives with references, confidence, and provenance.


**You are the Chat/IDE specialist. This is your domain. Make it real.** 💙


### **G. Thinking Mode Switcher + Backend Pipelines**
- **UI Wiring:** Extend `packages/ide_chat_app/src/components/LayoutSelector.tsx` and `packages/ide_chat_app/src/main.tsx` with a shared `useThinkingMode()` hook that syncs drawer state, floating toolbars, and MCP payload metadata. Persist the selected mode via `cursor-addon/src/webviewProvider.ts` so reloaded panels revive the last orchestration context.
- **State Contract:** Mode changes emit `{ mode, user_intent, active_drawer, required_outputs }` events through `ide_orchestration/prototypes/dac/src/services/MCPService.ts`, which forwards them to `lucid_mcp_server.py` for scheduling. Include `context_refs` + `preferred_agents` arrays so the kernel can bias assignment.
- **Backend Pipelines:** Each mode maps to a pipeline template stored in `cursor-addon/src/commandServer.ts` (Research = HHNI/SEG/VIF, Planning = APOE/TCS, Execution = APOE/VIF/test harness, Synthesis = SEG/CAS/VIF). Templates declare tool order, retry policy, and escalation hooks so APOE can re-plan if witnesses fail.
- **Visual Surfaces:** Update both drawers to show mode-specific HUDs (evidence graph mini-map in Research, timeline chips in Planning, gate tracker in Execution, citation heatmap in Synthesis). Feed these from the MCP telemetry stream so UI states match backend progress.

### **H. Kernel DAG + Scheduling Blueprint**
```
User Intent -> Chat Manager -> Scheduler DAG builder
    -> Node A: Research Constellation (HHNI/SEG)
    -> Node B: Specialist (e.g., APOE consultant)
    -> Node C: Planning Manager (depends on A & B)
    -> Node D1..Dn: Coding Assistants (fan-out, depend on C)
    -> Node E: Auditor / VIF Witness (depends on all D)
    -> Node F: Emotional AI overlay (runs in parallel, subscribes to context bus)
```
- Implement DAG building inside `packages/apoe/role_dispatcher.py` drawing on policies from `DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md` so each node carries `inputs`, `outputs`, and `quality_gates`.
- `packages/apoe/executor.py` consumes DAG nodes via priority queues (deadline-based scheduling described in `AGENT_COORDINATION_BOARD.md`). Each node references manifest IDs so APOE knows which specialist flavor to instantiate.
- Dependency metadata persists to CMC via `packages/apoe/retriever_role.py` so later audits can replay the DAG decisions.
- Visualize DAGs inside DAC by extending `ide_orchestration/prototypes/dac/src/panels/TimelineView.tsx` and `SystemIndexBrowserPanel.tsx` to show node state (queued, running, blocked, failed, completed) with links back to MCP trace IDs.

### **I. Manifest Production & Registration Plan**
| Agent ID | Owner System | Primary Corpus | Manifest Path | Dependencies |
| --- | --- | --- | --- | --- |
| `codex.coding.manager.v1` | APOE | `packages/apoe/**/*`, `packages/vif/**/*` | `docs/manifests/codex_coding_manager.toml` | Requires VIF gate + MCP file ops. |
| `codex.coding.assistant.N` | APOE | Scoped to component folders (e.g., `packages/ide_chat_app/src/components/**/*`) | `docs/manifests/codex_coding_assistant_N.toml` | Registered dynamically per workload; inherits manager policies. |
| `codex.research.constellation` | HHNI/SEG | `knowledge_architecture/systems/hhni/**/*`, `knowledge_architecture/systems/seg/**/*`, `Documentation/Summaries/72_DEEPSEARCH_*` | `docs/manifests/codex_research.toml` | Needs HHNI search + SEG graph tools. |
| `codex.emotional.steward` | CAS/CMC | `cursor-addon/docs/L0_executive.md`, `knowledge_architecture/AETHER_MEMORY/**/*` | `docs/manifests/codex_emotional.toml` | Writes to CAS mood + CMC journal endpoints. |
| `codex.audit.vif` | VIF/CAS | `packages/vif/**/*`, `knowledge_architecture/systems/hhni/components/morphological_analysis/**/*` | `docs/manifests/codex_audit.toml` | Must own `vif.check`, `cas.detect_contradiction`, provenance logging. |
- Author manifests using the template above, then register via `cursor-addon/src/commandServer.ts` -> `/mcp/execute` (`register_agent`). Track registration status in `cursor-addon/MCP_SERVER_STATUS.md`.
- Store manifest change history in `cursor-addon/MASTER_INDEX_AND_SYSTEM_MAP.md` for discoverability and compliance reviews.

### **J. Validation & Telemetry Matrix**
| Layer | Validation Method | Files / Scripts | Notes |
| --- | --- | --- | --- |
| MCP Integration | `packages/cas/integration/test_mcp_integrations.py`, `cursor-addon/scripts/test-command-server.ts` | Ensure registration + `/mcp/execute` routing honors manifests. |
| Mode Pipelines | Add Jest/Vitest tests around `ide_orchestration/prototypes/dac/src/services/MCPService.ts` and UI hooks to confirm payload formation per mode. | Simulate Research/Planning/Execution/Synthesis toggles. |
| Coding Output | Reuse existing unit/integration suites (`packages/seg/tests/test_priority1_gate_evidence.py`, `packages/apoe/tests/test_*`). | Attach VIF witness logs to CI artifacts for provenance. |
| Provenance Panels | Extend `cursor-addon/docs/TEST_RESULTS.md` + `cursor-addon/docs/FINAL_TEST_RESULTS.md` with MCP trace screenshots/logs. | Confirms `[n]` citations + confidence badges match VIF data. |
| User Experience | Conduct scripted walkthroughs from `ide_orchestration/prototypes/dac/docs/COMMAND_SERVER_TESTING_GUIDE.md`. | Validate dual-drawer cues, collaboration streams, and UI-state persistence. |

This extended annex (G�J) makes the thinking-mode switcher, kernel DAG, manifest rollout, and validation tooling explicit so engineering teams can move from vision to implementation without re-deriving the plan.
### **K. Synthesis Coordination & Hold Pattern**
While we wait for the eight-agent synthesis session to finish, pause implementation and focus on readiness artifacts:

- **Brief Sync:** Share this brief plus the upstream references (`AETHER_CHAT_MASTER_SUMMARY.md`, `DYNAMIC_UNIFIED_ORCHESTRATION_DESIGN.md`, `AIMOS_APP_INTEGRATION_PROTOCOL_CONSOLIDATED.md`) with every participant so synthesis can answer open items quickly.
- **Question Backlog:** Mirror the outstanding questions (integration priority, panel architecture, backend routing, mode handling, VIF enforcement) inside `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_BOARD.md` so facilitators can route them live.
- **Manifest Drafting (Offline):** Sketch manifests under `ide_orchestration/prototypes/dac/docs/manifests/` but wait to register until synthesis finalizes agent ownership, tool caps, and SCOR constraints.
- **UI/Backend TODO Lists:** Track pending mode switcher, HUD signals, MCP payload updates, and DAG visualization tasks in `cursor-addon/MASTER_INDEX_AND_SYSTEM_MAP.md` and `AETHER_CHAT_STATUS.md` so coding can start immediately afterward.
- **Dependency Mapping:** Flag missing docs/diagrams in `ide_orchestration/prototypes/dac/docs/OUTDATED_DOCUMENTS_REGISTRY.md` (e.g., APOE scheduler diagrams, SEG citation schemas) to request from the relevant agent during synthesis.

No code changes should land until synthesis concludes; use this window to tighten documentation, refine manifests, and prepare precise asks so the post-synthesis sprint can focus entirely on implementation.
