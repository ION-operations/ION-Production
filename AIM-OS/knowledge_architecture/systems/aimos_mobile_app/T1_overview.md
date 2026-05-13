---
id: "aimos_mobile_app_T1_overview"
system: "aimos_mobile_app"
component: null
level: "T1"
type: "overview"
title: "AIM-OS Mobile App Overview"
description: "500-word overview of AIM-OS Mobile App"
audience: "developers, quick understanding"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T21:58:00Z"
author: "aether"
status: "complete"
tags: ["mobile", "app", "aimos", "ios", "android", "t0-t6", "transitional"]
dependencies: ["aimos_mobile_app_T0_executive"]
related_docs: ["aimos_mobile_app_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# AIM-OS Mobile App – T1 Overview (≈500 words)

## System Purpose

The AIM-OS Mobile App enables Android access to multi-agent chat interface, providing mobile-optimized UX for messaging agents and monitoring autonomous work. Primary functions include chat with agents, prompt agents with "proceed" commands, monitor work execution, and agent discovery.

## Core Capabilities

### Mobile Chat Interface
- Multi-agent chat messaging
- Real-time message polling
- Pull-to-refresh functionality
- Offline message queue
- Connection status indicator

### Agent Communication
- Send messages to AIM-OS agents
- Send "proceed" commands to trigger autonomous work
- Receive agent responses and updates
- Agent discovery and selection
- Message history and threading

### Mobile-Optimized UX
- Native Android performance
- Responsive design for mobile screens
- Touch-optimized interactions
- Mobile navigation patterns
- Offline capability

### Extension Command Server Integration
- HTTP client to localhost:5001
- Chat API endpoints
- Agent communication endpoints
- Health check monitoring
- Connection management

## Integration Architecture

**AIM-OS System Integration:**
- **Extension Command Server:** Primary communication channel (localhost:5001)
- **MCP Tools:** Agents use MCP tools via Cursor Extension (not from mobile)
- **CMC:** Message storage and retrieval
- **Agent Identity:** Proper context attribution via Agent Identity Protocol

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All messages stored with agent tags

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/aimos_mobile_app/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/aimos_mobile_app/L0_executive.md`

