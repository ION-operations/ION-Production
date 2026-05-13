---
id: "log-sentinels_T1_overview"
system: "log-sentinels"
component: null
level: "T1"
type: "overview"
title: "Log-Sentinels Overview"
description: "500-word overview of Log-Sentinels (Hybrid Log Analysis System)"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["log-sentinels", "log-analysis", "hybrid", "privacy", "t0-t4", "transitional"]
dependencies: ["log-sentinels_T0_executive"]
related_docs: ["log-sentinels_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Log-Sentinels – T1 Overview (≈500 words)

## Purpose

Log-Sentinels solves the log analysis problem—where developers drown in logs without proactive insights, leading to reactive debugging, missed patterns, and privacy risks. Log-Sentinels provides hybrid log analysis: fast cloud summaries (Cerebras Scout) for rolling insights, deep local forensics (Ollama) for root cause analysis. Privacy-first: cloud sees only redacted/templated windows; local has raw for deep analysis. Escalates based on severity, confidence, novelty. Enables proactive issue detection with privacy protection.

## Architecture

Log-Sentinels uses a pipeline architecture: Collectors → Normalizer → Template Miner → Windower → Scout (cloud) → Router Policy → Forensics (local) → SEG/VIF/CMC/TCS. **Collectors** gather logs from sources (browser console, terminal, backend API). **Normalizer** redacts PII/secrets before cloud calls (bearer tokens, emails, IPs, API keys). **Template Miner** (Drain3) extracts log templates, clusters similar logs. **Windower** creates time-based windows (60s roll, 12+ min records). **Scout** (Cerebras) analyzes windows fast (<700ms), cloud-only sees redacted. **Router Policy** decides escalation (severity ≥medium AND (confidence <0.80 OR novelty ≥0.70)). **Forensics** (Ollama) deep analysis (<8s), local-only sees raw.

## Key Components

**LogSentinelsPipeline:** Main orchestrator coordinating collectors, normalizer, template miner, windower, scout, forensics, router policy.

**LogCollector:** Abstract base for log sources. Implementations: BrowserConsoleCollector (WebSocket), TerminalCollector (file), BackendAPICollector (OTEL).

**LogNormalizer:** PII redaction before cloud calls. Pattern-based redaction (regex), hash raw for local storage, preserve structure.

**LogTemplateMiner:** Template extraction using Drain3 algorithm. Clusters similar logs, computes novelty scores, cache management (LRU, 5000 templates).

**Windower:** Time-based windowing system. Rolling windows (60s), minimum records (12), burst detection (2.5x baseline).

**ScoutAdapter:** Fast cloud LLM adapter (Cerebras). Analyzes redacted windows, returns summary, confidence, severity, tags, suggested tools.

**ForensicsAdapter:** Deep local LLM adapter (Ollama). Analyzes raw windows with context, returns root cause, fix suggestion, evidence.

**RouterPolicy:** Escalation decision logic. Severity scoring, confidence thresholds, novelty detection, keep/escalate decisions.

## Relationships

**Depends On:** Router (tool suggestions), SEG (evidence), VIF (gates), CMC (decisions), TCS (timeline)

**Feeds Data To:** Router (tool suggestions), SEG (evidence chains), VIF (quality gates), CMC (decision atoms), TCS (incident markers), IDE panels (AI Summaries, Anomalies)

**Integrates With:** IDE panels (React hooks, SSE/WS events), Router (tool suggestions), AIM-OS systems (SEG, VIF, CMC, TCS)

## Use Cases

**Proactive Issue Detection:** Logs analyzed continuously, Scout identifies issues early, Forensics provides root cause when escalated.

**Privacy-Preserving Analysis:** PII redacted before cloud, raw logs stay local, hash-based references enable forensics without exposure.

**Tool Suggestion:** Scout/Forensics suggest MCP tools, Router receives suggestions, generates tool plans, executes via APOE.

## Current Status

**Completion:** 100% (Phase 4 complete)

**Status:** Production-ready

**Next Milestone:** Production deployment with monitoring

**Read T2 for detailed architecture.**

