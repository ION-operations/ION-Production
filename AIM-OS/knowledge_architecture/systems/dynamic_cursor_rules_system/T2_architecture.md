---
id: "dynamic_cursor_rules_system_T2_architecture"
system: "dynamic_cursor_rules_system"
component: null
level: "T2"
type: "architecture"
title: "Dynamic Cursor Rules System Architecture"
description: "2,000-word architecture document for Dynamic Cursor Rules System"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:18:00Z"
author: "aether"
status: "complete"
tags: ["dynamic", "cursor", "rules", "management", "t0-t6", "transitional"]
dependencies: ["dynamic_cursor_rules_system_T1_overview"]
related_docs: ["dynamic_cursor_rules_system_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Dynamic Cursor Rules System – T2 Architecture (≈2000 words)

## System Architecture Overview

Dynamic Cursor Rules System provides sophisticated rule management framework through intelligent partition and context-aware loading architecture. The system follows partition-native, context-driven patterns with clear separation of concerns, enabling scalability, maintainability, and comprehensive rule management.

**Architectural Principles:**
- **Rule Partitioning:** Modular rule organization
- **Context Awareness:** Intelligent rule selection
- **Dynamic Loading:** Performance-optimized loading
- **Agent Identity Required:** All operations MUST include agent_name parameter (CRITICAL PROTOCOL)

## Component Architecture

### 1. Rule Partition Manager

**Purpose:** Manages rule partitions and their metadata.

**Architecture:**
```
RulePartitionManager
├── PartitionCreator (Partition creation)
├── DependencyTracker (Dependency tracking)
├── ConflictDetector (Conflict detection)
└── VersionController (Version control)
```

**Key Interfaces:**
- `create_partition(partition, agent_name) -> PartitionResult`
- `track_dependencies(partition_id, agent_name) -> DependencyResult`
- `detect_conflicts(partitions, agent_name) -> ConflictResult`
- `control_version(partition_id, agent_name) -> VersionResult`

**AIM-OS Integration:**
- Partitions stored as CMC atoms with bitemporal tracking
- Partition patterns indexed in HHNI for retrieval
- Partition quality tracked with VIF confidence scores

**Performance Characteristics:**
- Partition Creation: <200ms
- Dependency Tracking: <150ms
- Conflict Detection: <300ms
- Version Control: <100ms

### 2. Context Analyzer

**Purpose:** Analyzes current context to determine relevant rules.

**Architecture:**
```
ContextAnalyzer
├── ProjectDetector (Project detection)
├── TaskClassifier (Task classification)
├── ProtocolAnalyzer (Protocol analysis)
└── EnvironmentAssessor (Environment assessment)
```

**Key Interfaces:**
- `analyze_context(context, agent_name) -> ContextAnalysis`
- `detect_project(context, agent_name) -> ProjectType`
- `classify_task(task, agent_name) -> TaskCategory`
- `analyze_protocols(context, agent_name) -> ProtocolRequirements`

**AIM-OS Integration:**
- Context data stored as CMC atoms
- Context patterns synthesized into SEG knowledge
- Context quality tracked with VIF provenance

**Performance Characteristics:**
- Context Analysis: <100ms
- Project Detection: <50ms
- Task Classification: <75ms
- Protocol Analysis: <80ms

## Integration Architecture

### AIM-OS System Integration

**CMC Integration:** Rule storage and versioning  
**HHNI Integration:** Semantic rule search and retrieval  
**VIF Integration:** Rule validation and quality assurance  
**APOE Integration:** Rule application orchestration  
**CAS Integration:** Meta-cognitive rule analysis

## Performance Architecture

**Latency Targets:**
- Partition Creation: <200ms
- Context Analysis: <100ms
- Rule Loading: <150ms
- Conflict Resolution: <200ms

**Throughput Targets:**
- Partition Operations: 300+ operations/second
- Context Analyses: 500+ analyses/second
- Rule Loads: 400+ loads/second

**Resource Usage:**
- CPU Usage: <30%
- Memory Usage: <1GB
- Storage Usage: <20GB (rule data)

## Security Architecture

**Security Boundaries:**
- Tier 0: Supporting components (caching, validation)
- Tier 1: Processing components (partition, context)
- Tier 2: Core component (rule manager)

**Security Requirements:**
- All operations require agent identity
- Rule data requires agent attribution
- Rule operations require authorization
- Comprehensive audit logging

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Optional Parameter:** `agent_session_id` - Session tracking identifier
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All rule operations stored with agent tags

**Example:**
```python
# CORRECT: Agent identity included
result = await create_partition({
  "partition": partition_data,
  "agent_name": "aether_session_001"  # REQUIRED
})

# INCORRECT: Missing agent identity
result = await create_partition({
  "partition": partition_data  # ERROR: agent_name missing
})
```

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## References

- System map: `systems/dynamic_cursor_rules_system/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/dynamic_cursor_rules_system/L0_executive.md`

