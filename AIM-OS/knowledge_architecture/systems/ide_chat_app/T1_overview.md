---
id: ide_chat_app_T1_overview
system: ide_chat_app
component: null
level: T1
type: overview
title: IDE Chat App Overview
description: 500-word overview of AIM-OS IDE Chat Application
audience: developers, architects, stakeholders
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: 2025-11-18T00:00:00Z
updated: 2025-11-18T00:00:00Z
author: codex
status: complete
tags: ["ide", "chat", "ui", "react", "integration", "cursor"]
dependencies: ["ide_chat_app_T0_executive"]
related_docs: ["ide_chat_app_T2_architecture", "INTEGRATION_ARCHITECTURE.md"]
version: v1.0.0
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# IDE Chat App – T1 Overview (≈500 words)

## Purpose

IDE Chat App is the frontend UI layer for AIM-OS, providing a React-based dashboard that integrates all AIM-OS consciousness capabilities into a unified interface. It serves as the UI component for the cursor-addon extension and can operate standalone as an Electron application.

## Architecture

The application follows a three-layer architecture:

**Layer 1: Frontend UI (React/TypeScript)**
- React 18 with TypeScript
- Vite build system
- Tailwind CSS for styling
- 6-tab interface: Agents, Chat, Chains, Tools, Timeline, NL Tags
- Components: Memory Browser, Consciousness Visualization, System Dashboard

**Layer 2: Service Layer (TypeScript)**
- `AIMOSService.ts` - Core AIM-OS integration (CMC, HHNI, VIF, APOE, SEG)
- `VoiceService.ts` - TTS/SST voice I/O
- `HttpLucidDaemonService.ts` - Lucid Orchestrator daemon
- `RealtimeCollaborationService.ts` - Real-time collaboration
- `AnalyticsService.ts` - Analytics and metrics

**Layer 3: Backend Services (Python)**
- AIM-OS MCP Server (`lucid_mcp_server.py` on port 8000)
- Lucid Daemon (HTTP API on port 5000)
- RAG MCP Proxy (Python service on port 8001)
- Automation Engine (Python service on port 8000/automation)

## Integration Points

### Core AIM-OS Systems

**CMC (Context Memory Core):**
- Endpoints: `POST /mcp/store_memory`, `POST /mcp/retrieve_memory`, `GET /mcp/get_memory_stats`
- UI Components: MemoryBrowser, MemoryBrowserEnhanced

**HHNI (Hierarchical Hypergraph Neural Index):**
- Endpoint: `POST /mcp/retrieve_memory` (uses HHNI internally)
- UI Components: ContextExplorer, SearchBar

**VIF (Verifiable Intelligence Framework):**
- Endpoint: `POST /mcp/track_confidence`
- UI Components: ConsciousnessVisualization, ToolQualityDashboard

**APOE (AI-Powered Orchestration Engine):**
- Endpoint: `POST /mcp/create_plan`
- UI Components: AIMOSOrchestration, WorkflowManager

**SEG (Shared Evidence Graph):**
- Endpoint: `POST /mcp/synthesize_knowledge`
- UI Components: LucidGraphVisualization, SystemDashboard

### Voice I/O

- **Text-to-Speech (TTS):** Web Speech Synthesis API (browser-native)
- **Speech-to-Text (SST):** Web Speech Recognition API (browser-native)
- Features: Real-time transcription, confidence scores, audio hash for audit trail

### RAG MCP Tools Integration

- Intelligent tool selection using semantic search
- Consciousness-aware weighting
- 80% context reduction goal
- <100ms response time target

## Deployment Modes

1. **Extension Mode:** Embedded in cursor-addon as React UI
2. **Standalone Mode:** Electron app with HTTP API integration
3. **Development Mode:** Vite dev server for local development

## Status

- **Version:** 1.0.0
- **Status:** Production-ready
- **Integration:** Integrated with cursor-addon
- **Documentation:** INTEGRATION_ARCHITECTURE.md in package directory

