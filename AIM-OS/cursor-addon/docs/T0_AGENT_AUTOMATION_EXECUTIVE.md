---
id: "agent_automation_T0_executive"
system: "agent_automation"
component: null
level: "T0"
type: "executive"
title: "Agent Automation Executive Summary"
description: "100-word executive summary of Cursor agent automation"
audience: "executives, quick reference"
confidence_threshold: 0.80
token_cost: 100
word_count: 100
created: "2025-11-03T00:00:00Z"
updated: "2025-11-03T21:50:00Z"
author: "aether"
status: "complete"
tags: ["agent-automation", "cursor", "autonomous", "production-ready", "t0-t6", "transitional"]
dependencies: []
related_docs: ["CURSOR_AGENT_AUTOMATION.md", "PROTOCOL_DESIGN.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Automation – T0 Executive Summary (≈100 words)

Cursor agent automation enables autonomous operation via Background Agent API (HTTP), MCP tools, and slash commands. Bulletproof messaging ensures reliable communication through envelope protocol with ACK/NACK, ordering, idempotency, and dead letter queue. Agents run for hours/days autonomously, monitored via React UI dashboard. Complete protocol: Slash commands → MCP tools → Command Server → Background Agent API → Webhooks → MessageRouter → UI. Production-ready with supervisor patterns, checkpointing, and automatic recovery.

**Key Components:** AgentMonitor, MessageRouter, Command Server, React UI  
**Status:** Protocol designed, AgentMonitor implemented, pending API research  
**Next:** Research Cursor API endpoints, register MCP tools, create slash commands

