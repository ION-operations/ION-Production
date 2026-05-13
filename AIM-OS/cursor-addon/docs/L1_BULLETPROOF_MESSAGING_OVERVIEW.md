# L1: Bulletproof Messaging Protocol - Overview

**Date:** 2025-11-03  
**Status:** Production Ready  
**Purpose:** High-level overview of bulletproof messaging protocol  
**Tags:** `#bulletproof-messaging` `#overview` `#protocol` `#production-ready`  
**Level:** L1 Overview (500 words)  
**Related:** [L0_BULLETPROOF_MESSAGING_EXECUTIVE.md](./L0_BULLETPROOF_MESSAGING_EXECUTIVE.md) | [L2_BULLETPROOF_MESSAGING_ARCHITECTURE.md](./L2_BULLETPROOF_MESSAGING_ARCHITECTURE.md) | [INDEX.md](./INDEX.md)

---

## 🎯 **THE PROBLEM**

Current extension communication has gaps:
- No guaranteed delivery (messages can be lost)
- No deduplication (duplicate messages processed multiple times)
- No link health monitoring (can't detect when connection is broken)
- No persistent queues (messages lost on reload/crash)
- No capability negotiation (don't know what each side supports)
- No command sandboxing (unsafe commands can be executed)
- No state checkpointing (can't resume after interruption)

**Result:** Can't trust autonomous operation - messages might be lost, duplicates might cause issues, and there's no way to resume after crashes.

---

## ✅ **THE SOLUTION**

**8 Core Components:**

1. **Versioned Envelope Protocol** - Structured message format with IDs, sequence numbers, direction, and error handling
2. **Heartbeat + Link Status** - Monitor connection health with RTT tracking and automatic reconnect
3. **Persistent Queues** - Survive reloads/crashes using IndexedDB (webview) and Memento (extension)
4. **Capability Negotiation** - Handshake protocol to exchange supported features and versions
5. **Command Gate + Sandbox** - Whitelist-only command execution with sandboxing for terminal/MCP calls
6. **State-of-World Log** - Checkpoint system for resuming autonomous plans mid-execution
7. **Observability** - Event timeline, watchdogs, commit cadence tracking
8. **Smoke Tests** - Comprehensive validation suite for all failure modes

---

## 🏗️ **ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│              CURSOR EXTENSION (Extension Host)              │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Message Router                                       │ │
│  │  - Envelope processing                                │ │
│  │  - Deduplication (LRU cache)                          │ │
│  │  - Retry logic                                        │ │
│  └───────────────────┬───────────────────────────────────┘ │
│                      │                                      │
│  ┌───────────────────▼───────────────────────────────────┐ │
│  │  Persistent Outbox (Memento)                         │ │
│  │  - Survives reloads                                   │ │
│  │  - Replays on startup                                 │ │
│  └───────────────────┬───────────────────────────────────┘ │
│                      │                                      │
│  ┌───────────────────▼───────────────────────────────────┐ │
│  │  Heartbeat Monitor                                    │ │
│  │  - Ping every 10s                                     │ │
│  │  - Track RTT                                          │ │
│  │  - Reconnect on failure                               │ │
│  └───────────────────┬───────────────────────────────────┘ │
│                      │                                      │
│  ┌───────────────────▼───────────────────────────────────┐ │
│  │  Command Gate                                         │ │
│  │  - Capability whitelist                                │ │
│  │  - Sandbox execution                                   │ │
│  │  - Audit log                                          │ │
│  └───────────────────┬───────────────────────────────────┘ │
│                      │                                      │
│  ┌───────────────────▼───────────────────────────────────┐ │
│  │  State Checkpoint System                               │ │
│  │  - .aimos/runtime/state.json                           │ │
│  │  - Plan step tracking                                  │ │
│  │  - Resume capability                                   │ │
│  └───────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Envelope Protocol (v1)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              REACT UI (Webview)                            │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Persistent Outbox (IndexedDB)                        │ │
│  │  - Survives reloads                                   │ │
│  │  - Replays on reconnect                               │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Event Timeline (Observability)                       │ │
│  │  - All envelopes logged                               │ │
│  │  - Performance metrics                                 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 **MESSAGE FLOW**

**Normal Operation:**
```
1. UI sends request envelope → Extension
2. Extension immediately sends ACK (< 500ms)
3. Extension processes request → Route to handler
4. Extension sends response envelope → UI
5. UI marks as delivered → Remove from outbox
```

**With Failure:**
```
1. UI sends request envelope → Extension
2. No ACK received after 500ms → Retry with same ID
3. Extension receives duplicate → Dedupe (seen ID)
4. Extension sends ACK → UI stops retrying
5. Extension processes → Response sent
```

**On Reload:**
```
1. Extension starts → Load outbox from Memento
2. Replay all undelivered envelopes → Process in order
3. UI starts → Load outbox from IndexedDB
4. Replay all undelivered envelopes → Send to extension
5. Normal operation resumes
```

---

## 🔧 **KEY TECHNOLOGIES**

- **Envelope Protocol:** Custom message format with versioning, IDs, sequence numbers
- **IndexedDB:** Browser-based persistent storage for webview
- **Memento API:** VS Code extension persistent storage
- **Deduplication:** LRU cache (4K recent IDs)
- **Heartbeat:** Timer-based ping/pong with RTT tracking
- **Command Sandbox:** Whitelist + execution isolation

---

## 🎯 **SUCCESS CRITERIA**

- ✅ Messages never lost (persistent queues)
- ✅ No duplicate processing (deduplication)
- ✅ Connection health visible (heartbeat status)
- ✅ Autonomous operation resumable (state checkpoints)
- ✅ Safe command execution (sandboxing)
- ✅ Full observability (event timeline)

---

**Next:** See L2_architecture.md for detailed protocol design

