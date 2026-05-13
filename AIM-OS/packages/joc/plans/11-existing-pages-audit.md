# 11 — Existing Pages Audit

> **What we have vs. what we need.** Status of all 18 current JOC pages.

---

## Current Pages Inventory

| # | Page | File | Status | Assessment |
|---|------|------|--------|------------|
| 1 | Mission Control | `MissionControlPage.tsx` | ⚠️ Prototype | Has AI Fleet Dashboard, needs real MCP data |
| 2 | System Atlas | `SystemAtlasPage.tsx` | ⚠️ Prototype | Force-directed graph exists, needs Context Web integration |
| 3 | Timeline | `TimelinePage.tsx` | ⚠️ Prototype | Basic timeline, needs TCS bitemporal upgrade |
| 4 | Code Editor | `CodeEditorPage.tsx` | ⚠️ Prototype | Has Monaco shell, needs consciousness-awareness |
| 5 | Agent Comms | `AgentCommsPage.tsx` | ⚠️ Prototype | Basic messaging, needs MCP `send_ai_message` |
| 6 | Context Graph | `ContextGraphPage.tsx` | ❌ Toy Mock | Must be completely redesigned (see Plan 02) |
| 7 | Capsule Manager | `CapsuleManagerPage.tsx` | ✅ Functional | Template engine works, marketplace built |
| 8 | Settings | `SettingsPage.tsx` | ⚠️ Basic | Needs MCP endpoint config, theme engine |
| 9 | Synthesizer | `SynthesizerPage.tsx` | ⚠️ Prototype | Needs HHNI/SEG real integration |
| 10 | Evolution | `EvolutionPage.tsx` | ⚠️ Prototype | Needs bidirectional graph (see DAC V2) |
| 11 | AI Cockpit | `AICockpitPage.tsx` | ⚠️ Prototype | Monaco + consciousness, needs Active Context Envelopes |
| 12 | BAS | `BASPage.tsx` | ⚠️ Prototype | Browser Automation System shell |
| 13 | Knowledge Web | `KnowledgeWebPage.tsx` | ⚠️ Prototype | Related to Context Web, consider merging |
| 14 | Debug Console | `DebugConsolePage.tsx` | ⚠️ Prototype | Needs Aether debug infrastructure pattern |
| 15 | MCP Tools | `MCPToolsPage.tsx` | ⚠️ Prototype | Tool browser, needs real MCP tool calls |
| 16 | Prompt Chains | `PromptChainsPage.tsx` | ⚠️ Prototype | Visual chain editor, needs APOE integration |
| 17 | Doc Builder | `DocBuilderPage.tsx` | ❓ Unknown | Needs audit — may already be high-end |
| 18 | Dashboard | `DashboardPage.tsx` | ⚠️ Prototype | Overview dashboard, needs real metrics |

---

## Key Findings

### Pages That Need Full Redesign
- **Context Graph** → Replace with Context System Page (Plan 02)
- **Knowledge Web** → Merge into Context System Page

### Pages That Need Major Upgrade
- **Mission Control** → Real MCP fleet data
- **System Atlas** → Full Context Web w/ force-directed physics
- **Timeline** → TCS bitemporal upgrade with playback
- **Code Editor** → Consciousness-aware + temporal navigation (DAC Sam features)

### Pages That Are Missing
- **Project Hub** (Plan 03) — new page needed
- **Task Manager** (Plan 04) — new page needed
- **Log Whisperer** (Plan 05) — new page needed
- **Aether Oracle** (Plan 07) — new page needed (or upgrade Agent Comms)

### Pages That Are Close to Production
- **Capsule Manager** — functional, needs polish
- **Settings** — basic, needs MCP config
- **BAS** — working shell, needs session management

---

## Recommended Actions

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | Redesign Context Graph → Context System | Large |
| 2 | Merge Knowledge Web into Context System | Medium |
| 3 | Create Task Manager page | Large |
| 4 | Create Log Whisperer page | Large |
| 5 | Create Project Hub page | Medium |
| 6 | Upgrade Mission Control with real MCP | Medium |
| 7 | Upgrade Agent Comms → Aether Oracle | Large |
| 8 | Add consciousness to Code Editor | Medium |
| 9 | Timeline → TCS bitemporal | Medium |
| 10 | All pages: add left drawer configs | Medium |
