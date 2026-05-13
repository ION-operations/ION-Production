---
id: "command_server_T0_executive"
system: "command_server"
component: null
level: "T0"
type: "executive"
title: "Command Server - Executive Summary"
description: "100-word executive summary of Command Server HTTP API bridge"
audience: "executives, stakeholders, quick reference"
confidence_threshold: 0.90
token_cost: 100
word_count: 100
created: "2025-11-03T23:50:00Z"
updated: "2025-11-03T23:50:00Z"
author: "aether"
status: "complete"
tags: ["command-server", "http-api", "bridge", "cursor-addon", "t0-t6", "transitional"]
dependencies: []
related_docs: ["SYSTEM_INTEGRATION_ARCHITECTURE_T2.md", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Command Server - T0 Executive Summary (≈100 words)

**Command Server** is an HTTP API bridge (port 5001) exposing VS Code/Cursor functionality to external clients. Enables Electron app, daemon, and external systems to access MCP tools, VS Code commands, and Cursor state without direct extension access. Core endpoints: `/mcp/execute` (MCP tool execution), `/cursor/*` (Cursor state), `/messaging/send` (bulletproof messaging), `/health` (status check). Bridges gap between Extension Host (isolated) and external clients. Production-ready, handles CORS, error responses, and request validation. Critical integration point for AIM-OS automation.

**Status:** Production Ready ✅  
**See:** [T1 Overview](./T1_COMMAND_SERVER_OVERVIEW.md) | [T2 Architecture](./T2_COMMAND_SERVER_ARCHITECTURE.md)

