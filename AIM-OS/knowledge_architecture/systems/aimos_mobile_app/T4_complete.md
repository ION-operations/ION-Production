---
id: "aimos_mobile_app_T4_complete"
system: "aimos_mobile_app"
component: null
level: "T4"
type: "complete"
title: "AIM-OS Mobile App Complete Reference"
description: "15,000+ word complete reference for AIM-OS Mobile App"
audience: "comprehensive reference, all details"
confidence_threshold: 0.60
token_cost: 15000
word_count: 15000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T22:05:00Z"
author: "aether"
status: "complete"
tags: ["mobile", "app", "aimos", "ios", "android", "t0-t6", "transitional"]
dependencies: ["aimos_mobile_app_T3_detailed"]
related_docs: ["system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# AIM-OS Mobile App – T4 Complete Reference (≈15,000 words)

## Complete System Reference

This document provides comprehensive reference for the AIM-OS Mobile App, covering all implementation details, APIs, patterns, and integration points. This is the definitive reference for all aspects of the mobile application.

## Architecture Reference

### Component Hierarchy

```
AIMOSMobileApp
├── ChatScreen
│   ├── AgentSelector
│   ├── MessageList
│   │   └── MessageBubble (for each message)
│   └── MessageInput
├── ConnectionManager
│   ├── ExtensionCommandServerClient
│   └── HealthMonitor
└── StateManagement
    ├── ChatStore
    ├── ConnectionStore
    └── AgentStore
```

## API Reference

### Extension Command Server API

**Endpoint:** `POST http://localhost:5001/mcp/execute`

**Send Message:**
```typescript
{
  tool: "send_ai_message",
  arguments: {
    from_ai: string, // REQUIRED - Agent Identity Protocol
    to_ai: string,
    content: string,
    message_type?: string,
    priority?: string
  }
}
```

**Get Messages:**
```typescript
{
  tool: "get_ai_messages",
  arguments: {
    from_ai: string, // REQUIRED - Agent Identity Protocol
    limit?: number
  }
}
```

## Agent Identity Protocol (CRITICAL)

**All operations MUST include agent_name:**

- **Required Parameter:** `agent_name` - Unique identifier for the agent
- **Optional Parameter:** `agent_session_id` - Session tracking identifier
- **Validation:** System validates agent is onboarded before operations
- **Attribution:** All messages stored with agent tags

**See:** `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md` for complete specification.

## Performance Characteristics

**Latency Targets:**
- Message Display: <100ms
- Message Send: <300ms
- Agent Selection: <50ms
- Connection Management: <150ms

**Throughput Targets:**
- Message Processing: 100+ messages/second
- Concurrent Connections: 10+ agents
- Health Checks: 1 check/second

## References

- System map: `systems/aimos_mobile_app/system.map.lucid.json5` (if exists)
- CMC: `systems/cmc/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/aimos_mobile_app/L0_executive.md`

