---
id: "dynamic_cursor_rules_system_T1_overview"
system: "dynamic_cursor_rules_system"
component: null
level: "T1"
type: "overview"
title: "Dynamic Cursor Rules System Overview"
description: "500-word overview of Dynamic Cursor Rules System"
audience: "developers, quick understanding"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:15:00Z"
author: "aether"
status: "complete"
tags: ["dynamic", "cursor", "rules", "management", "t0-t6", "transitional"]
dependencies: ["dynamic_cursor_rules_system_T0_executive"]
related_docs: ["dynamic_cursor_rules_system_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Dynamic Cursor Rules System – T1 Overview (≈500 words)

## System Purpose

Dynamic Cursor Rules System provides sophisticated rule management framework that intelligently partitions, loads, and applies Cursor IDE rules based on context and protocol requirements. Addresses limitations of monolithic rule files by creating modular, context-aware system.

## Core Capabilities

### Rule Partition Management
- Partition creation and organization
- Rule dependency tracking
- Conflict detection and resolution
- Version control and updates

### Context Analysis
- Project type detection
- Task classification
- Protocol requirement analysis
- Environment state assessment

### Dynamic Rule Loading
- Rule selection based on context
- Rule composition and merging
- Performance optimization
- Memory management

### Protocol Integration
- L0-L4 documentation protocol integration
- A-H Protocol workflow integration
- LUCID Development Protocol integration
- Custom protocol support

### Conflict Resolution
- Rule precedence management
- Conflict detection algorithms
- Resolution strategy application
- User notification and override

## Integration Architecture

**AIM-OS System Integration:**
- **CMC:** Rule storage and versioning
- **HHNI:** Semantic rule search and retrieval
- **VIF:** Rule validation and quality assurance
- **APOE:** Rule application orchestration
- **CAS:** Meta-cognitive rule analysis

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All rule operations stored with agent tags

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/dynamic_cursor_rules_system/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/dynamic_cursor_rules_system/L0_executive.md`

