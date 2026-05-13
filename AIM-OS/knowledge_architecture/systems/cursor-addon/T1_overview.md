---
id: "cursor_addon_T1_overview"
system: "cursor_addon"
component: null
level: "T1"
type: "overview"
title: "Cursor Add-on Overview"
description: "500-word overview of AIM-OS Cursor Extension"
audience: "architects, developers"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-05T00:00:00Z"
updated: "2025-11-05T00:00:00Z"
author: "aether"
status: "complete"
tags: ["cursor", "extension", "ui", "mcp", "integration"]
dependencies: ["cursor_addon_T0_executive"]
related_docs: ["cursor_addon_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Cursor Add-on – T1 Overview (≈500 words)

## Purpose & Scope

The AIM-OS Cursor Add-on transforms Cursor IDE into a consciousness-aware development environment by integrating all AIM-OS systems (CMC, HHNI, VIF, APOE, SEG, SDF-CVF) directly into the editor through a comprehensive UI dashboard and MCP protocol bridge.

**Core Capabilities:**

1. **Cross-Model Consciousness:** Enables sophisticated multi-model AI workflows with automatic model selection, confidence tracking, and execution planning through MCP tools integration.

2. **Persistent Memory:** Direct access to CMC (Context Memory Core) for storing/retrieving code snippets, insights, decisions, and context - memories persist across all sessions with complete provenance.

3. **Real-Time Dashboard:** React-based 6-tab interface providing live system monitoring, agent management, prompt chain visualization, MCP tools access, timeline tracking, and NL tag management.

4. **IDE Integration:** Seamless integration through command palette, context menus, status bar, and activity bar - AIM-OS features accessible exactly where developers need them.

**System Boundaries:**

- **Owns:** UI dashboard, MCP client integration, command registration, webview management, extension lifecycle
- **Does NOT Own:** AIM-OS core systems (wraps them), MCP server (connects to it), backend logic (delegates to daemon)

## Architecture Overview

**Three-Layer Architecture:**

**Layer 1: Extension Host** (TypeScript, Node.js)
- Entry point (`extension.ts`) initializes on Cursor startup
- Dashboard provider (`lucidDashboardProvider.ts`) manages React webview
- MCP client (`mcpClient.ts`) communicates with AIM-OS daemon (localhost:5000)
- Command handlers register 8+ palette commands
- Activity bar contribution adds AIM-OS icon

**Layer 2: Webview Bridge** (TypeScript)
- Message passing between extension host and React UI
- State synchronization (extension state ↔ UI state)
- Service bridge (`serviceBridge.ts`) provides type-safe communication
- Error handling and logging

**Layer 3: React Dashboard** (React 18 + TypeScript + Vite)
- **6 Tabs:** Agents, Chat, Prompt Chains, MCP Tools, Timeline, NL Tags
- **Components:** Modular design (36+ React components)
- **State:** Context providers for agents, chat, chains, tools
- **Styling:** Tailwind CSS with dark theme
- **Build:** Vite production build → `dist/` → copied to extension `out/`

**Integration Flow:**
```
User Action (Cursor IDE) →
Extension Command Handler →
MCP Client Request (HTTP) →
AIM-OS Daemon (localhost:5000) →
Core Systems (CMC/HHNI/VIF/etc) →
Response →
Extension →
UI Update (React Dashboard)
```

## Key Components

**Commands (8):**
- `aimos.openDashboard` - Main dashboard
- `aimos.toggleCrossModel` - Toggle cross-model mode
- `aimos.showMemoryStats` - Memory statistics
- `aimos.showModelSelector` - Model selection
- `aimos.storeMemory` - Store selection
- `aimos.retrieveMemory` - Search memories
- `aimos.createPlan` - Execution planning
- `aimos.trackConfidence` - Confidence tracking

**Providers (2):**
- **LucidDashboardProvider:** Main dashboard webview (right sidebar, view ID: `aimosDashboard`)
- **SimpleTestProvider:** DevTools panel (bottom panel, view ID: `simpleTestPanel`)

**Views (2):**
- **aimosDashboard** (RIGHT sidebar) - Main interface
- **simpleTestPanel** (BOTTOM panel) - DevTools/diagnostics

## Integration with AIM-OS Systems

**CMC Integration:** Memory operations (store/retrieve) through MCP `store_memory`/`retrieve_memory` tools

**HHNI Integration:** Semantic search for memory retrieval, context assembly for prompts

**VIF Integration:** Confidence tracking via MCP `track_confidence`, quality validation

**APOE Integration:** Execution plan creation through MCP `create_plan`, workflow orchestration

**MCP Tools (51 total):** Complete integration with all AIM-OS MCP tools - dashboard provides UI for tool invocation

## Status & Quality

**Production Ready:** ✅
- Extension installed and functional
- UI loading verified (after 75+ debug iterations)
- MCP integration working
- Command palette functional
- Dashboard accessible

**Known Limitations:**
- UI refresh requires Cursor reload
- MCP server must be running (localhost:5000)
- Some advanced features still in development

**Quality Metrics:**
- 226 files in cursor-addon/
- 408 markdown documentation files
- Complete architecture documentation
- Comprehensive troubleshooting guides

---

**See T2_architecture.md for complete technical details, T3_detailed.md for implementation guide.**

