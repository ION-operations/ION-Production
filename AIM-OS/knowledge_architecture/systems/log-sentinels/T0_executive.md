---
id: "log-sentinels_T0_executive"
system: "log-sentinels"
component: null
level: "T0"
type: "executive"
title: "Log-Sentinels Executive Summary"
description: "100-word executive summary of Log-Sentinels (Hybrid Log Analysis System)"
audience: "executives, quick reference"
confidence_threshold: 0.80
token_cost: 100
word_count: 100
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["log-sentinels", "log-analysis", "hybrid", "privacy", "t0-t4", "transitional"]
dependencies: []
related_docs: ["log-sentinels_T1_overview", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Log-Sentinels – T0 Executive Summary (≈100 words)

Log-Sentinels is a hybrid log analysis system providing fast cloud summaries (Cerebras Scout) and deep local forensics (Ollama). Flow: Collectors → Normalizer (PII redaction) → Template Miner → Windower → Scout (cloud, redacted) → Router Policy → Forensics (local, raw) → SEG evidence + VIF gates → IDE surfaces. Privacy-first: cloud sees only redacted/templated windows; local has raw for deep analysis. Escalates based on severity, confidence, novelty. Integrates with SEG (evidence), VIF (gates), CMC (decisions), TCS (timeline), Router (tool suggestions). Enables proactive issue detection with privacy protection. See system map for component relationships; T1-T4 for architecture details.

