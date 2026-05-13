---
id: "global_user_rules_T1_overview"
system: "global_user_rules"
component: null
level: "T1"
type: "overview"
title: "Global User Rules Overview"
description: "500-word overview of Global User Rules"
audience: "developers, quick understanding"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:15:00Z"
author: "aether"
status: "complete"
tags: ["global", "user", "rules", "preferences", "governance", "t0-t6", "transitional"]
dependencies: ["global_user_rules_T0_executive"]
related_docs: ["global_user_rules_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Global User Rules – T1 Overview (≈500 words)

## System Purpose

Global User Rules System provides comprehensive platform for managing user preferences, system behavior, and governance policies across all AIM-OS systems. Provides centralized rule management, dynamic rule application, and intelligent rule optimization to ensure consistent and personalized user experiences.

## Core Capabilities

### Rule Management
- Creation, modification, and deletion of user rules
- Rule hierarchy and dependency management
- Version control and rule history
- Rule validation and conflict detection

### Rule Application
- Dynamic application of rules across all systems
- Context-aware rule selection
- Priority-based rule enforcement
- Performance-optimized rule processing

### Rule Optimization
- Intelligent optimization of rule performance
- Conflict resolution between rules
- Rule efficiency analysis
- User experience enhancement

### Preference Management
- Centralized storage and management of user preferences
- Personalization settings and configurations
- User-specific rule configurations
- Preference analytics and insights

### Policy Enforcement
- Consistent enforcement of governance policies
- Compliance monitoring and validation
- Regulatory compliance management
- Policy analytics and reporting

## Integration Architecture

**AIM-OS System Integration:**
- **CMC:** Store rule data, preferences, and policy configurations
- **HHNI:** Semantic search of rules, preferences, and policies
- **VIF:** Verify rule integrity and compliance
- **APOE:** Orchestrate rule application workflows
- **SEG:** Synthesize knowledge from rule usage patterns

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All rule operations stored with agent tags

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/global_user_rules/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/global_user_rules/L0_executive.md`

