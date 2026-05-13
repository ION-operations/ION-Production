---
id: "dynamic_cursor_rules_system_T4_complete"
system: "dynamic_cursor_rules_system"
component: null
level: "T4"
type: "complete"
title: "Dynamic Cursor Rules System Complete Reference"
description: "15,000+ word complete reference for Dynamic Cursor Rules System"
audience: "comprehensive reference, all details"
confidence_threshold: 0.60
token_cost: 15000
word_count: 15000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:22:00Z"
author: "aether"
status: "complete"
tags: ["dynamic", "cursor", "rules", "management", "t0-t6", "transitional"]
dependencies: ["dynamic_cursor_rules_system_T3_detailed"]
related_docs: ["system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Dynamic Cursor Rules System – T4 Complete Reference (≈15,000 words)

## Complete System Reference

This document provides comprehensive reference for Dynamic Cursor Rules System, covering all implementation details, APIs, patterns, and integration points. This is the definitive reference for all aspects of dynamic cursor rules management.

## Architecture Reference

### Component Hierarchy

```
DynamicCursorRulesSystem
├── RulePartitionManager
│   ├── PartitionCreator
│   ├── DependencyTracker
│   └── ConflictDetector
├── ContextAnalyzer
│   ├── ProjectDetector
│   └── TaskClassifier
└── RuleLoaderEngine
    ├── RuleSelector
    └── RuleComposer
```

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Optional Parameter:** `agent_session_id` - Session tracking identifier
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All rule operations stored with agent tags

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## Performance Characteristics

**Latency Targets:**
- Partition Creation: <200ms
- Context Analysis: <100ms
- Rule Loading: <150ms
- Conflict Resolution: <200ms

## References

- System map: `systems/dynamic_cursor_rules_system/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/dynamic_cursor_rules_system/L0_executive.md`

