---
id: "bulletproof_messaging_T5_quick"
system: "bulletproof_messaging"
component: null
level: "T5"
type: "quick_reference"
title: "Bulletproof Messaging Protocol - Quick Reference"
description: "500-word quick reference cheat sheet for bulletproof messaging protocol"
audience: "developers, quick lookup"
confidence_threshold: 0.90
token_cost: 500
word_count: 500
created: "2025-11-04T01:00:00Z"
updated: "2025-11-04T01:00:00Z"
author: "aether"
status: "complete"
tags: ["bulletproof-messaging", "quick-reference", "cheat-sheet", "t0-t6", "transitional"]
dependencies: ["bulletproof_messaging_T4_complete"]
related_docs: ["T4_BULLETPROOF_MESSAGING_COMPLETE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Bulletproof Messaging Protocol – T5 Quick Reference (≈500 words)

**Quick cheat sheet for common operations**

---

## 📨 **CREATE ENVELOPE**

**Request:**
```typescript
const env = createEnvelope('request', 'mcp.callTool', 'ui->ext', {
    tool: 'store_memory',
    args: { content: 'Test', tags: {} }
}, {
    priority: 'high',
    replyTo: 'previous-id'
});
```

**Response:**
```typescript
const env = createEnvelope('response', 'mcp.callTool', 'ext->ui', { result }, {
    replyTo: requestId
});
```

**Event:**
```typescript
const env = createEnvelope('event', 'agent.status', 'ext->ui', {
    runId: 'agent-123',
    status: 'running'
});
```

**ACK:**
```typescript
const ack = createAckEnvelope(requestId, 'ext->ui', 'mcp.callTool', true);
```

**NACK:**
```typescript
const nack = createNackEnvelope(requestId, 'ext->ui', 'mcp.callTool', {
    code: 'TOOL_NOT_FOUND',
    message: 'MCP tool not found'
});
```

---

## 🔀 **ROUTE MESSAGE**

**Via MessageRouter:**
```typescript
await router.route(envelope);
```

**Register Handler:**
```typescript
router.registerHandler('mcp.callTool', async (env) => {
    const { tool, args } = env.payload;
    const result = await mcpClient.callTool(tool, args);
    return createEnvelope('response', 'mcp.callTool', 'ext->ui', { result }, {
        replyTo: env.id
    });
});
```

---

## 🔄 **IDEMPOTENCY**

**Check for Duplicate:**
```typescript
if (await idempotencyManager.hasBeenProcessed(envelope.id)) {
    return;  // Already processed
}
await idempotencyManager.markProcessed(envelope.id);
```

---

## 📊 **ORDERING**

**Enforce FIFO:**
```typescript
// Automatically handled by OrderingManager
// Messages processed in sequence per sender
```

**Resequencer (Out-of-Order Handling):**
```typescript
// Resequencer buffers messages for 2 seconds
// Delivers in correct order automatically
```

---

## 💀 **DEAD LETTER QUEUE**

**Add Failed Message:**
```typescript
await dlqManager.addFailedMessage({
    envelope: originalEnv,
    error: { code: 'TIMEOUT', message: 'Request timeout' },
    retryCount: 3
});
```

**Retry Failed Message:**
```typescript
const failed = await dlqManager.getFailedMessages();
for (const msg of failed) {
    await router.route(msg.envelope);  // Retry
}
```

---

## 💾 **PERSISTENT OUTBOX**

**Save Message:**
```typescript
await outbox.addOutgoing(envelope);
```

**Replay Undelivered:**
```typescript
const undelivered = outbox.getUndelivered();
for (const entry of undelivered) {
    await router.route(entry.envelope);
}
```

---

## 💓 **HEARTBEAT**

**Send Heartbeat:**
```typescript
const heartbeat = createHeartbeatEnvelope('ext->ui');
await router.route(heartbeat);
```

**Monitor Connection:**
```typescript
heartbeatMonitor.start();  // Sends heartbeat every 10s
heartbeatMonitor.on('disconnected', () => {
    console.log('Connection lost');
});
```

---

## 🧪 **TEST HELPERS**

**Wait for Router Idle:**
```typescript
await router.idle();  // Wait until all messages processed
```

**Flush Microtasks:**
```typescript
await flushMicrotasks();  // Process pending promises
```

**Tick Timer:**
```typescript
await tick(100);  // Advance timer by 100ms
```

---

## ⚙️ **CONFIGURATION**

**MessageRouter Options:**
```typescript
const router = new MessageRouter(context, {
    maxRetries: 3,
    retryDelay: 500,
    ackTimeout: 500
});
```

**Resequencer Options:**
```typescript
const resequencer = new Resequencer({
    ttl: 2000,  // 2 second buffer
    maxBufferSize: 100
});
```

---

## 📚 **SEE ALSO**

- **T0:** Executive Summary
- **T1:** Overview
- **T2:** Architecture
- **T3:** Detailed Implementation
- **T4:** Complete Reference

---

**Status:** Production Ready ✅  
**Version:** v1.0.0  
**Last Updated:** 2025-11-04  
**Author:** Aether

