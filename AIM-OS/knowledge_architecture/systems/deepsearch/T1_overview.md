---
id: "deepsearch_T1_overview"
system: "deepsearch"
component: null
level: "T1"
type: "overview"
title: "DeepSearch Overview"
description: "500-word overview of DeepSearch system"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-18T00:00:00Z"
updated: "2025-11-18T00:00:00Z"
author: "aether"
status: "complete"
tags: ["deepsearch", "integration", "search", "sovereign", "t1"]
dependencies: ["deepsearch_T0_executive"]
related_docs: ["deepsearch_T2_architecture"]
version: "1.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# DeepSearch - T1 Overview (≈500 words)

## Purpose & Scope

**DeepSearch** is a sovereign local intelligence engine designed for web and filesystem search capabilities within AIM-OS IDE systems. Unlike HHNI (which provides hierarchical semantic retrieval for AIM-OS internal data), DeepSearch focuses on external search—web content, filesystem files, and code repositories. It operates as an **Integration System**, connecting AIM-OS to external search capabilities rather than enhancing internal retrieval systems.

**Core Guarantees:**
- **Sovereign Operation:** Local-first search with no external dependencies
- **Trust Scoring:** Algorithmic trust assessment for search results
- **Entropy Calculation:** Shannon entropy for content quality measurement
- **Persistent Index:** SQLite-based master index for search history
- **Polite Crawling:** Async web crawling with rate limiting

**Primary Use Cases:**
- Web search for IDE systems (lucid-chat, lucid-ide)
- Filesystem search for code repositories
- Code search across projects
- External content discovery

## Components

**1. TrustScorer**
- Trust scoring algorithm for search results
- Evaluates source reliability and content quality
- Provides trust scores for ranking

**2. EntropyCalculator**
- Shannon entropy calculation for content analysis
- Measures information density and quality
- Helps filter low-quality results

**3. WebCrawler**
- Async web crawling with polite rate limiting
- Respects robots.txt and rate limits
- Handles various content types

**4. MasterIndex**
- SQLite-based persistent index
- Stores search history and results
- Enables fast retrieval of previously indexed content

## Architecture

DeepSearch uses a modular architecture with four core components working together:
- **TrustScorer** evaluates result quality
- **EntropyCalculator** measures information density
- **WebCrawler** fetches external content
- **MasterIndex** persists search history

The system operates independently from HHNI, using its own index (SQLite vs HHNI's hierarchical index) and search algorithms (trust scoring vs semantic search).

## Integration

**Integrates With:**
- **IDE Systems:** lucid-chat, lucid-ide (provides search capabilities)
- **Filesystem:** Local file search
- **Web:** External web content search

**Does NOT Integrate With:**
- **HHNI:** Separate system (not an enhancement to HHNI)
- **CMC:** No direct integration (uses own SQLite index)
- **Other Core Systems:** Standalone integration system

## Relationship to HHNI

DeepSearch is **NOT** an enhancement to HHNI. It's a separate integration system:
- **Different Purpose:** External search (web/filesystem) vs internal semantic retrieval
- **Different Architecture:** SQLite index vs hierarchical index
- **Different Algorithms:** Trust scoring vs semantic search
- **No Integration:** No imports, no references, no shared components

**Classification:** Integration System (not an enhancement to HHNI)

## Status

**Package:** `packages/deepsearch/` (9 Python files)
**Status:** ✅ Implemented
**Documentation:** ✅ T0-T1 complete (this document)
**Integration:** ✅ Connected to IDE systems

---

**Next:** T2 Architecture (detailed architecture documentation)
