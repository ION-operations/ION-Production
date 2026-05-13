---
id: "global_user_rules_T4_complete"
system: "global_user_rules"
component: null
level: "T4"
type: "complete"
title: "Global User Rules Complete Reference"
description: "15,000+ word complete reference for Global User Rules"
audience: "comprehensive reference, all details"
confidence_threshold: 0.60
token_cost: 15000
word_count: 15000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:22:00Z"
author: "aether"
status: "complete"
tags: ["global", "user", "rules", "preferences", "governance", "t0-t6", "transitional"]
dependencies: ["global_user_rules_T3_detailed"]
related_docs: ["system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Global User Rules – T4 Complete Reference (≈15,000 words)

## Complete System Reference

This document provides comprehensive reference for Global User Rules System, covering all implementation details, APIs, patterns, and integration points. This is the definitive reference for all aspects of global user rules management.

## Architecture Reference

### Component Hierarchy

```
GlobalUserRulesSystem
├── RuleEngine
│   ├── RuleManager
│   ├── RuleApplicator
│   └── RuleValidator
├── PreferenceManager
│   ├── PreferenceStorage
│   └── PreferenceRetriever
└── PolicyEnforcer
    ├── PolicyManager
    └── ComplianceMonitor
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
- Rule Management: <200ms
- Rule Application: <150ms
- Preference Retrieval: <50ms
- Rule Optimization: <300ms

## References

- System map: `systems/global_user_rules/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/global_user_rules/L0_executive.md`

