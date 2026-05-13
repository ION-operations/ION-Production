---
atlas_package: system
system_slug: microsoft-agent-framework
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Microsoft Agent Framework — Identity

**Kind:** Microsoft-documented **SDK/framework** for building agents and workflows (Python/C# per docs), integrating multiple model providers and **MCP** tooling as described on Microsoft Learn (`DOCUMENTED`, `src-ms-agent-framework-learn`).

## Boundaries

- **Not** a single cloud runtime like a vendor-only chat API — developers host/run agents per deployment (`DOCUMENTED` patterns).  
- **Not** Windows-only by definition — verify cross-platform statements in docs per release (`DOCUMENTED`).

## Why this system matters

- Shows **workflow graphs + checkpointing + human-in-the-loop** as first-class in a vendor framework (`DOCUMENTED` overview).  
- **MCP** integration in a major enterprise SDK line (`DOCUMENTED`).

## What this system teaches the atlas

- **Framework vs API-only** distinction in `comparative/ai_runtime_models.md`.
