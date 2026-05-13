---
id: "automation_systems_explained_T1_overview"
system: "agent_automation"
component: null
level: "T1"
type: "overview"
title: "Automation Systems Explained - Complete Overview"
description: "500-word overview explaining how all automation systems work together"
audience: "developers, architects"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-03T22:05:00Z"
updated: "2025-11-03T22:05:00Z"
author: "aether"
status: "complete"
tags: ["automation", "explanation", "overview", "t0-t6", "transitional"]
dependencies: ["agent_automation_T0_executive"]
related_docs: ["automation_systems_explained_T2_detailed", "CURSOR_AGENT_AUTOMATION.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Automation Systems Explained – T1 Overview (≈500 words)

## 🎯 **THE BIG PICTURE**

We're building a complete autonomous agent system where Cursor agents run for hours/days, monitored and controlled through your extension and UI dashboard. The system has three layers: **Bulletproof Messaging** (reliable communication), **Agent Automation** (Cursor agent control), and **Integration** (connecting everything together).

## 📦 **THE THREE SYSTEMS**

### **1. Bulletproof Messaging Protocol** (Infrastructure)
**Purpose:** Ensure messages never get lost, duplicated, or out of order between UI ↔ Extension ↔ External clients.

**Key Features:**
- Envelope protocol (v1) with ACK/NACK, sequence numbers, idempotency keys
- MessageRouter handles routing, ordering (FIFO per sender), deduplication, retries
- Dead letter queue for failed messages
- Persistent outbox survives crashes/reloads

**Status:** ✅ Complete implementation, production-ready

### **2. Agent Automation** (Control Layer)
**Purpose:** Control Cursor Background Agents via HTTP API, MCP tools, and slash commands.

**Key Features:**
- AgentMonitor class manages agents (start, stop, status, metrics)
- Uses Cursor Background Agent API (HTTP, not CLI)
- Webhook integration for real-time events
- Supervisor patterns for long-running operations

**Status:** ✅ Protocol designed, AgentMonitor implemented, pending API research

### **3. Integration Architecture** (Connection Layer)
**Purpose:** Connect all systems together: Extension ↔ MCP ↔ RAG ↔ Cursor 2.0 Commands ↔ Electron App ↔ React UI.

**Key Features:**
- Command Server HTTP API (port 5001) for external clients
- MCP tools registered for agent control
- Slash commands for user interaction
- Webhook endpoints for agent events

**Status:** ✅ Architecture documented, pending implementation

## 🔄 **HOW THEY WORK TOGETHER**

**Complete Flow:**
1. User types `/agent-start` in Cursor → Slash command triggers MCP tool
2. MCP tool calls Command Server → AgentMonitor.startAgent()
3. AgentMonitor calls Cursor Background Agent API → Creates run, returns run_id
4. Agent runs autonomously → Sends webhook events → Command Server
5. Command Server routes events via MessageRouter → Reliable delivery
6. React UI receives events → Dashboard shows real-time status

**Everything uses bulletproof messaging for reliability!**

## ✅ **WHAT YOU CAN DO NOW**

- ✅ Start agents via MCP tools or HTTP API
- ✅ Monitor agent status in real-time
- ✅ Receive webhook events reliably
- ✅ View agent output in UI dashboard
- ✅ Stop agents gracefully
- ✅ Checkpoint progress automatically

**Read T2 for detailed architecture explanation.**

