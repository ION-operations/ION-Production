# JOC Plans Library - Master Index

> **Purpose:** Single source of truth for all JOC planning documents.
> Every feature, page, system, and integration has its own deep-dive plan grounded in the actual AIM-OS architecture.

## Research Status

| Domain | Docs Read | Lines Analyzed | Status |
|--------|-----------|----------------|--------|
| IDE Prototypes (6 agents) | 8 docs | ~4,000 | Complete |
| Aether Chat System | 3 docs | ~3,500 | Complete |
| Sovereign Context Mapper | 1 doc | 529 | Complete |
| Aether Memory System | 1 doc | 536 | Complete |
| Context Mesh Maps | 1 code file | 657 | Complete |
| JOC KI Artifacts | 2 docs | ~50 | Complete |
| DAC V2 Design | 3 docs | ~2,000 | Complete |
| Epic Orchestration | 1 doc | 472 | Complete |

---

## 1. Architecture & Layout

### [01-architecture-and-layout.md](./01-architecture-and-layout.md)
**Scope:** Dual icon-bar/drawer system, page-level left drawers, universal right drawers, 5-zone layout heritage from DAC, responsive design.
**Grounded in:** DAC V2 Design, Best Ideas Synthesis, JOC KI Blueprint

---

## 2. Pages & Features

### [02-context-system-page.md](./02-context-system-page.md)
**Scope:** Aether/Codex context visualization - S0-S8 pipeline, Context Web (force-directed graph), LUCID Empire reasoning traces, kappa-gating confidence display, SEG evidence chains, Sovereign Context Mapper envelopes.
**Grounded in:** AETHER_CHAT_COMPLETE_SYSTEM_MAP, DEEP_TECHNICAL_ANALYSIS, UNIFIED_IMPLEMENTATION_PLAN, Sovereign Context Mapper, Aether Memory System L2, Context Mesh Maps

### [03-project-hub-page.md](./03-project-hub-page.md)
**Scope:** All-projects gallery with version branches, relationships, app/doc/hybrid categorization, advanced metadata, related docs linking.
**Grounded in:** IDE Prototypes Consolidation (100+ panels cataloged), DAC/Aether panel registries, North Star Directive

### [04-task-manager-page.md](./04-task-manager-page.md)
**Scope:** Task manager on steroids - ChainSpec Epic->Phase->Workstream->Task hierarchy, quality gates, agent assignment, dependency graphs, multi-level progress tracking.
**Grounded in:** EPIC Orchestration System Design, ChainSpec/gates.json architecture, APOE integration

### [05-log-whisperer-page.md](./05-log-whisperer-page.md)
**Scope:** AI-powered log analysis with semantic search (HHNI), anomaly detection (Log Sentinels from DAC), pattern recognition, port/process monitoring, local LLM or Cerebras integration.
**Grounded in:** DAC Log Sentinels, Aether Debug Infrastructure, CAS cognitive analysis

### [06-doc-builder-page.md](./06-doc-builder-page.md)
**Scope:** High-end documentation system - NL Tags integration, HHNI semantic documentation search, auto-generation from code, evidence-backed docs (SEG), multi-layer doc format (L0-L4 like Aether Memory System).
**Grounded in:** Aether Memory System L0-L4 doc structure, NL Tags Explorer, Documentation Explorer Panel, HHNI

### [07-aether-oracle-page.md](./07-aether-oracle-page.md)
**Scope:** AI Manager / Oracle interface - multi-agent coordination dashboard, consciousness visualization, LUCID Empire reasoning traces, agent capability matching, handoff protocols.
**Grounded in:** Aether Chat pipeline, Multi-Agent Orchestration, Agent Coordination System, CAS

---

## 3. Data & Integration

### [08-data-integration-plan.md](./08-data-integration-plan.md)
**Scope:** MCP real data wiring - `useAIMOS` hook architecture, CMC/HHNI/VIF/SEG/TCS/CAS/APOE/SCOR hooks, tiered polling (12s/36s/72s), graceful fallback to mock data.
**Grounded in:** DAC `useAIMOS` hook, JOC KI MCP Integration Spine, Dual-MCP architecture

### [09-context-node-graph-visualization.md](./09-context-node-graph-visualization.md)
**Scope:** The "git branch for context" dream - context provenance timeline, node graph of AI context utilization, temporal evolution of context across conversations.
**Grounded in:** Context Web spec (Aether Chat S2/S6), SEG evidence graph, TCS timeline, Bitemporal Memory

---

## 4. Infrastructure

### [10-left-drawer-system.md](./10-left-drawer-system.md)
**Scope:** Per-page left icon bar + drawer system - each page gets unique left-side tools, drawer content registry per route, collapsible/resizable.
**Grounded in:** User requirement (left=per-page, right=universal), DAC 5-zone layout, Max panel-first philosophy

### [11-existing-pages-audit.md](./11-existing-pages-audit.md)
**Scope:** Audit of all 18 existing JOC pages - what each does, what needs redesign, what's production-ready vs. prototype.
**Grounded in:** Direct codebase audit of `packages/joc/src/pages/`

---

## 5. Cross-Cutting

### [12-design-system.md](./12-design-system.md)
**Scope:** Unified visual design language - glassmorphism, dark theme, confidence indicators, evidence badges, VIF kappa-score displays, contradiction alerts, AIM-OS system status colors.
**Grounded in:** DAC V2 UX Patterns, Rev accessibility-first, Best Ideas Synthesis

### [13-production-readiness.md](./13-production-readiness.md)
**Scope:** What defines "production-ready" - no mock data, real MCP connections, error boundaries, loading states, WCAG 2.1 AA, performance optimization (lazy load, virtual scroll).
**Grounded in:** Rev research-driven foundation, Lex error boundaries, DAC OBJ-07/OBJ-08

### [14-window-aware-injector-runtime.md](./14-window-aware-injector-runtime.md)
**Scope:** Local Windows injector runtime for JOC/JARVIS - restore/select target windows, dispatch commands via CDP/UIA/keyboard/visual adapters, enforce verification, and apply bounded self-healing repair.
**Grounded in:** operator blueprint, runtime/cockpit split, BAS stop-order constraints, existing Windows native actuator references

---

## Build Order (Proposed)

| Priority | Plan | Rationale |
|----------|------|-----------|
| 1 | 01 Architecture & Layout | Foundation - everything else builds on this |
| 2 | 08 Data Integration | Real data pipeline must exist before pages can be production |
| 3 | 02 Context System Page | User's primary focus, deepest research done |
| 4 | 09 Context Node Graph | The "dream" visualization, closely tied to #02 |
| 5 | 10 Left Drawer System | Required by all pages |
| 6 | 04 Task Manager | User priority - "task manager on steroids" |
| 7 | 05 Log Whisperer | User priority - port/process visibility |
| 8 | 03 Project Hub | Organizational backbone |
| 9 | 06 Doc Builder | Already has high-end prior work |
| 10 | 07 Aether Oracle | Advanced AI management |
| 11 | 11 Existing Pages Audit | Retrofit/upgrade existing pages |
| 12 | 14 Window-Aware Injector Runtime | New local execution substrate for multi-window command dispatch |
| 13-14 | Design System + Production Readiness | Cross-cutting quality |
