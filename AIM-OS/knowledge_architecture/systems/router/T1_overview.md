---
id: "router_T1_overview"
system: "router"
component: null
level: "T1"
type: "overview"
title: "Router Overview"
description: "500-word overview of Router (APOE-MCP Router)"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["router", "apoe", "mcp", "tool-selection", "t0-t4", "transitional"]
dependencies: ["router_T0_executive"]
related_docs: ["router_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Router – T1 Overview (≈500 words)

## Purpose

Router (APOE-MCP Router) solves the tool selection problem—where AI agents must choose from 59+ MCP tools without clear guidance, leading to inefficient tool usage, redundant calls, and missed opportunities. Router provides intelligent tool selection through a three-brain architecture: Scout LLM (fast proposals), Bandit layer (learned ranking), and Rules engine (safety gates). Enables autonomous operation with confidence ≥0.70 by maintaining rolling context, enforcing preconditions, and learning from outcomes.

## Architecture

Router uses a deterministic control loop: Observe → Propose → Score → Plan → Execute → Validate → Learn. **Scout LLM** (Cerebras) proposes candidate tools based on snapshot context. **Bandit Scorer** ranks proposals using learned weights (context fit, success rate, preconditions, info gain, parallelizability, cost, latency, risk). **Rules Engine** validates plans (depth limits, budgets, VIF gates, rate limits). **RouterCache** caches proposals for performance (80%+ hit rate). **SnapshotBuilder** aggregates context from CMC, HHNI, VIF, SEG, TCS.

## Key Components

**Router:** Main orchestrator implementing control loop, plan compilation, execution coordination.

**ScoutLLM:** Fast policy LLM adapter using Cerebras for tool proposals. Pattern caching, request batching, optimized prompts reduce token usage.

**BanditScorer:** Learned policy layer scoring tools via utility function. Parallel scoring, pre-computed cache, gradient descent learning from outcomes.

**RulesEngine:** Hard gates for safety, budget, preconditions, rate limits. VIF integration for quality gates, depth/width limits, budget enforcement.

**ToolManifest:** Registry of all available tools with capabilities, requirements, metadata. Precondition resolvers, success rate tracking.

**SnapshotBuilder:** Aggregates system state from AIM-OS systems. CMC decisions, HHNI context, VIF status, SEG evidence, TCS cursor.

**RouterCache:** Performance optimization caching context snapshots and tool proposals. LRU eviction, TTL expiration, embedding cache.

## Relationships

**Depends On:** APOE (execution), CMC (decisions), HHNI (context), VIF (gates), SEG (evidence), TCS (timeline)

**Feeds Data To:** APOE (tool plans), VIF (confidence tracking), SEG (decision evidence), CMC (decision atoms), TCS (timeline events)

**Integrates With:** Log-Sentinels (tool suggestions), IDE panels (tool selection UI), MCP tools (59+ tools)

## Use Cases

**Autonomous Tool Selection:** Agent needs to choose tools for task. Router observes context, proposes tools, scores, generates plan, validates, executes.

**Tool Learning:** Router learns from execution outcomes, adjusts Bandit weights, improves future selections.

**Performance Optimization:** Caching reduces redundant LLM calls, parallel scoring improves latency, pattern recognition accelerates common scenarios.

## Current Status

**Completion:** 100% (Phase 4 complete)

**Status:** Production-ready

**Next Milestone:** Production deployment with monitoring

**Read T2 for detailed architecture.**

