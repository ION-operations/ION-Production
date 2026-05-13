---
atlas_package: system
system_slug: anthropic-claude-code-agent-sdk
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Anthropic Claude — Agent SDK & Claude Code (public surfaces)

**Kind:** Vendor-published **HTTP APIs**, **SDKs**, and **Claude Code** developer tooling as described in Anthropic’s public documentation — **not** claims about proprietary model internals or undisclosed training/stack details.

## Canonical definition

This package aggregates **Anthropic API** and **Claude Code** public surfaces where they share agent/tooling patterns, while keeping ledger rows separable per claim (`src-anthropic-docs`, `src-anthropic-api-ref`, `src-anthropic-claude-code-docs`).

## Boundaries

- **In scope:** Messages API shapes, tool use as documented, Claude Code CLI/IDE workflows as documented, MCP integration points **where explicitly documented**.  
- **Out of scope:** Model weights, hidden chain-of-thought, undisclosed safety classifiers — **UNKNOWN**.

## Why this system matters

- **Tool use** and **agent loop** patterns are reference designs for Llm-orchestrated workflows (`DOCUMENTED`).  
- **MCP** integration is a concrete protocol bridge for tools (`DOCUMENTED` where cited).  
- Shows how **IDE-adjacent agents** differ from raw HTTP APIs in trust boundaries.

## What this system teaches the atlas

- Same vendor may span **API**, **CLI**, and **editor** surfaces — package may split later if complexity grows.  
- **DOCUMENTED** MCP hooks are protocol-level, not OS-level.
