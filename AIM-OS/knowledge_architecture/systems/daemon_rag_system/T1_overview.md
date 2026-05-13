---
id: "daemon_rag_system_T1_overview"
system: "daemon_rag_system"
component: null
level: "T1"
type: "overview"
title: "Daemon/RAG System Overview"
description: "500-word overview of Daemon/RAG System"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:55:00Z"
author: "aether"
status: "complete"
tags: ["daemon_rag", "core", "mcp", "tool_management", "t0-t6", "transitional"]
dependencies: ["daemon_rag_system_T0_executive"]
related_docs: ["daemon_rag_system_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Daemon/RAG System – T1 Overview (≈500 words)

## Purpose & Scope

The Daemon/RAG System is a revolutionary intelligent tool management infrastructure that solves Cursor IDE's critical 40-tool limit through context-aware tool selection, dynamic server management, and RAG-enhanced decision making. This system enables seamless operation of 51 LUCID-MCP tools within the 40-tool constraint through intelligent orchestration.

**Core Mission:** Provide intelligent, context-aware management of MCP tools to maximize AI consciousness capabilities while respecting Cursor IDE's 40-tool limit through dynamic tool selection, server management, and continuous learning.

## Users & Integrations

**Cursor IDE:** Integrates with Cursor IDE's MCP protocol to manage tool loading and selection.

**LUCID-MCP Servers:** Manages 12 MCP server instances across different categories (AIM-OS core, SCOR, Timeline, Goal Timeline, IIS, Co-Agency, Dataset, Application Lifecycle, Autonomous Protocol, ARD, AI Collaboration, Observability).

**AIM-OS Systems:** Integrates with CMC for memory, HHNI for retrieval, VIF for verification, APOE for orchestration, CAS for cognitive analysis.

## Core Concepts

**Intelligent Tool Selection:** Analyzes user input and environment context to select optimal subset of 40 tools from 51 available. Uses multiple selection strategies (BALANCED, PERFORMANCE, CAPABILITY, LEARNING) and adapts in real-time based on context and performance feedback.

**Dynamic Server Management:** Manages 12 MCP server instances with load balancing, resource optimization, and graceful scaling. Starts/stops servers based on tool requirements and monitors resource usage.

**RAG-Enhanced Decision Making:** Uses retrieval-augmented generation for better tool selection decisions. Learns from successful tool selections and outcomes, continuously improving accuracy over time.

**Performance Monitoring:** Tracks response times, success rates, and resource usage in real-time. Enforces timing constraints (50ms tool selection, 400ms total) and monitors memory, CPU, and server capacity.

## High-Level Data Flow

**Tool Selection Flow:**
```
User Request → Context Analysis → Tool Selection Engine → Server Management → Tool Loading → Execution
```

**Learning Flow:**
```
Execution → Outcome Analysis → Pattern Recognition → Knowledge Retrieval → Selection Improvement
```

## Non-Goals

Daemon/RAG System is NOT:
- **Tool implementation:** Implements tool management, not the tools themselves
- **Cursor IDE modification:** Works within Cursor IDE's constraints, doesn't modify Cursor
- **Static system:** Continuously learns and adapts, not a fixed configuration
- **Single server:** Manages multiple servers, not a single monolithic server

## References

- System map: `systems/daemon_rag_system/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/daemon_rag_system/L0_executive.md` through `L4_complete.md`

