---
atlas_package: system
system_slug: openai-agents-chatgpt-public-runtime
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# OpenAI Agents / ChatGPT — Public runtime & API surface

**Kind:** Vendor-operated model inference and agent-oriented **public APIs**, plus consumer **ChatGPT** product behavior as described in public documentation — **not** an ATLAS claim about internal datacenter architecture.

## Canonical definition

This package records **DOCUMENTED** facts from OpenAI’s published API reference, platform guides, and product pages, and explicitly marks **UNKNOWN** for non-public internals (`src-openai-platform-docs`, `src-openai-api-ref`).

## Boundaries

- **In scope:** HTTP/WebSocket (where documented) API resources, authentication models at doc level, rate limits as published, tool/function calling as documented.  
- **Out of scope:** GPU clusters, weight storage layouts, geographic routing, proprietary safety filter internals — **UNKNOWN** unless primary engineering publication is ledgered.

## Why this system matters

- Reference **public contract** for a major commercial LLM API surface (`DOCUMENTED`).  
- **Tool/function calling** pattern influences agent architectures cross-vendor (`DOCUMENTED` API docs).  
- Demonstrates ATLAS discipline: **product docs ≠ kernel**.

## What this system teaches the atlas

- How to catalog **AI runtimes** as **operator surfaces** with hard internal boundaries.  
- How to separate **ChatGPT product** claims from **OpenAI API** claims unless docs explicitly unify them.
