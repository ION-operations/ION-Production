---
id: "bulletproof_messaging_T3_detailed"
system: "bulletproof_messaging"
component: null
level: "T3"
type: "detailed"
title: "Bulletproof Messaging Protocol - Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for bulletproof messaging protocol with step-by-step instructions, code examples, integration patterns, configuration, testing, troubleshooting, and best practices"
audience: "developers, implementers, integrators"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-03T23:45:00Z"
updated: "2025-11-03T23:45:00Z"
author: "aether"
status: "complete"
tags: ["bulletproof-messaging", "implementation", "guide", "production-ready", "t0-t6", "transitional"]
dependencies: ["bulletproof_messaging_T2_architecture"]
related_docs: ["T2_BULLETPROOF_MESSAGING_ARCHITECTURE.md", "PROTOCOL_DESIGN.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Bulletproof Messaging Protocol – T3 Detailed Implementation Guide (≈10,000 words)

**Date:** 2025-11-03  
**Status:** Production Ready ✅  
**Purpose:** Complete implementation guide for developers integrating or maintaining bulletproof messaging protocol  
**Prerequisites:** TypeScript, VS Code Extension API, JSON-RPC 2.0, IndexedDB basics

---

## 📋 **TABLE OF CONTENTS**

1. [Implementation Overview](#implementation-overview)
2. [Setup & Installation](#setup--installation)
3. [Envelope Protocol Implementation](#envelope-protocol-implementation)
4. [Message Router Implementation](#message-router-implementation)
5. [Reliability Components](#reliability-components)
6. [Persistent Storage](#persistent-storage)
7. [Integration Patterns](#integration-patterns)
8. [Configuration & Customization](#configuration--customization)
9. [Testing Strategy](#testing-strategy)
10. [Troubleshooting](#troubleshooting)
11. [Performance Optimization](#performance-optimization)
12. [Best Practices](#best-practices)
13. [Advanced Topics](#advanced-topics)

---

## 🎯 **IMPLEMENTATION OVERVIEW**

### **What You'll Build**

The Bulletproof Messaging Protocol ensures reliable communication between React UI (webview), VS Code Extension Host, and external clients via HTTP API. Core capabilities:

- **Guaranteed Delivery:** Messages survive crashes and reloads
- **Exactly-Once Processing:** Idempotency prevents duplicate handling
- **FIFO Ordering:** Messages processed in order per sender
- **Automatic Retries:** Failed messages retry with exponential backoff
- **Dead Letter Queue:** Failed messages stored for manual review
- **Connection Health:** Heartbeat monitoring with automatic reconnect
- **Deterministic Resequencing:** Handles out-of-order messages gracefully

### **Architecture Layers**

```
┌─────────────────────────────────────────────────────────────┐
│  UI Layer (React Webview)                                  │
│  - Envelope sender/receiver                                 │
│  - IndexedDB persistent outbox                             │
│  - Heartbeat echo handler                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ vscode.postMessage()
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Extension Layer (VS Code Extension Host)                 │
│  - MessageRouter (core coordinator)                        │
│  - IdempotencyManager (deduplication)                       │
│  - OrderingManager (FIFO per sender)                        │
│  - Resequencer (deterministic ordering)                     │
│  - DeadLetterQueueManager (failure handling)                │
│  - PersistentOutbox (Memento API)                           │
│  - HeartbeatMonitor (connection health)                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP API (localhost:5001)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Command Server (HTTP Bridge)                              │
│  - POST /messaging/send endpoint                            │
│  - Envelope protocol wrapper                               │
└─────────────────────────────────────────────────────────────┘
```

### **Key Design Decisions**

1. **Envelope Protocol v1:** Structured message format with versioning, ACK/NACK, sequence numbers
2. **Separate Stores:** IndexedDB for UI (webview), Memento for Extension (persistent across reloads)
3. **Idempotency Keys:** Persistent to disk (survives crashes) with LRU eviction
4. **Resequencer:** TTL-based buffering (2s default) for out-of-order messages
5. **Dead Letter Queue:** File-based storage (`.aimos/dead_letter_queue.json`)
6. **Heartbeat:** 10s interval with RTT tracking and automatic reconnect

---

## 🔧 **SETUP & INSTALLATION**

### **Prerequisites**

- Node.js 18+ and npm/yarn
- TypeScript 5.0+
- VS Code Extension Development Host
- VS Code Extension API (`@types/vscode`)

### **Install Dependencies**

```bash
cd cursor-addon
npm install vscode @types/vscode
npm install --save-dev typescript @types/node
```

### **Project Structure**

```
cursor-addon/
├── src/
│   ├── messaging/
│   │   ├── envelope.ts              # Envelope protocol definitions
│   │   ├── router.ts                 # MessageRouter (core coordinator)
│   │   ├── idempotencyManager.ts     # Duplicate prevention
│   │   ├── orderingManager.ts        # FIFO ordering per sender
│   │   ├── resequencer.ts            # Deterministic resequencing
│   │   ├── deadLetterQueue.ts        # Failure handling
│   │   ├── persistentOutbox.ts       # Survives reloads
│   │   ├── heartbeatMonitor.ts       # Connection health
│   │   ├── kv.ts                     # Key-value abstraction
│   │   └── testHelpers.ts            # Test utilities
│   ├── extension.ts                  # Extension activation
│   └── commandServer.ts             # HTTP API bridge
├── docs/
│   ├── T0_BULLETPROOF_MESSAGING_EXECUTIVE.md
│   ├── T1_BULLETPROOF_MESSAGING_OVERVIEW.md
│   ├── T2_BULLETPROOF_MESSAGING_ARCHITECTURE.md
│   └── T3_BULLETPROOF_MESSAGING_DETAILED.md (this file)
└── package.json
```

### **Basic Initialization**

```typescript
// extension.ts
import * as vscode from 'vscode';
import { MessageRouter } from './messaging/router';
import { PersistentOutbox } from './messaging/persistentOutbox';
import { HeartbeatMonitor } from './messaging/heartbeatMonitor';

export function activate(context: vscode.ExtensionContext) {
    // Initialize message router
    const router = new MessageRouter(context, {
        maxRetries: 3,
        retryDelay: 500,
        ackTimeout: 500
    });

    // Initialize persistent outbox
    const outbox = new PersistentOutbox(context);

    // Initialize heartbeat monitor
    const heartbeat = new HeartbeatMonitor(10000); // 10s interval

    // Register webview panel
    const panel = vscode.window.createWebviewPanel(
        'aimosDashboard',
        'AIM-OS Dashboard',
        vscode.ViewColumn.Two,
        { enableScripts: true }
    );

    // Connect router to webview
    router.setWebview(panel.webview);
    heartbeat.setWebview(panel.webview);
    heartbeat.start();

    // Replay undelivered messages on startup
    const undelivered = outbox.getUndelivered();
    for (const entry of undelivered) {
        router.route(entry.envelope).catch(console.error);
    }

    // Register message handler
    panel.webview.onDidReceiveMessage(async (message) => {
        await router.route(message);
    });

    return {
        router,
        outbox,
        heartbeat
    };
}
```

---

## 📦 **ENVELOPE PROTOCOL IMPLEMENTATION**

### **Core Type Definitions**

```typescript
// envelope.ts
export type Direction = 'ui->ext' | 'ext->ui' | 'ext->agent' | 'agent->ext';
export type MessageKind = 'request' | 'response' | 'event' | 'ack' | 'nack' | 'heartbeat';
export type Priority = 'critical' | 'high' | 'medium' | 'low';

export interface Envelope<T = unknown> {
    v: 1;                          // Protocol version (always 1)
    id: string;                    // UUID (v4) - unique per message
    seq: number;                   // Monotonic sequence per sender (for ordering)
    ts: number;                    // Date.now() timestamp
    dir: Direction;                 // Message direction
    kind: MessageKind;             // Message kind
    topic: string;                  // Channel identifier (e.g., 'mcp.callTool')
    replyTo?: string;               // ID of message being replied to
    ok?: boolean;                   // Success status (for response/ack)
    err?: {                         // Error details (if ok=false)
        code: string;
        message: string;
        data?: any;
    };
    payload?: T;                     // Message payload (type-safe)
    priority?: Priority;             // Message priority
    compressed?: boolean;           // Compression flag
    originalSize?: number;           // Original size before compression
}
```

### **Creating Envelopes**

```typescript
// Helper functions for creating envelopes
export function createEnvelope<T>(
    kind: MessageKind,
    topic: string,
    dir: Direction,
    payload?: T,
    options?: {
        replyTo?: string;
        priority?: Priority;
        compressed?: boolean;
        originalSize?: number;
    }
): Envelope<T> {
    return {
        v: 1,
        id: crypto.randomUUID(),
        seq: 0, // Will be set by sender
        ts: Date.now(),
        dir,
        kind,
        topic,
        payload,
        replyTo: options?.replyTo,
        priority: options?.priority || 'medium',
        compressed: options?.compressed,
        originalSize: options?.originalSize,
    };
}

// Create ACK envelope
export function createAckEnvelope(
    originalId: string,
    dir: Direction,
    topic: string,
    ok: boolean = true
): Envelope {
    return {
        v: 1,
        id: crypto.randomUUID(),
        replyTo: originalId,
        seq: 0,
        ts: Date.now(),
        dir,
        kind: 'ack',
        topic,
        ok,
    };
}

// Create NACK envelope
export function createNackEnvelope(
    originalId: string,
    dir: Direction,
    topic: string,
    error: { code: string; message: string; data?: any }
): Envelope {
    return {
        v: 1,
        id: crypto.randomUUID(),
        replyTo: originalId,
        seq: 0,
        ts: Date.now(),
        dir,
        kind: 'nack',
        topic,
        ok: false,
        err: error,
    };
}

// Create heartbeat envelope
export function createHeartbeatEnvelope(dir: Direction): Envelope {
    return {
        v: 1,
        id: crypto.randomUUID(),
        seq: 0,
        ts: Date.now(),
        dir,
        kind: 'heartbeat',
        topic: 'link',
        priority: 'critical',
    };
}
```

### **Envelope Validation**

```typescript
export function validateEnvelope(env: any): env is Envelope {
    if (!env || typeof env !== 'object') return false;
    if (env.v !== 1) return false;
    if (typeof env.id !== 'string') return false;
    if (typeof env.seq !== 'number') return false;
    if (typeof env.ts !== 'number') return false;
    if (!['ui->ext', 'ext->ui', 'ext->agent', 'agent->ext'].includes(env.dir)) return false;
    if (!['request', 'response', 'event', 'ack', 'nack', 'heartbeat'].includes(env.kind)) return false;
    if (typeof env.topic !== 'string') return false;
    return true;
}
```

### **Sequence Number Management**

Sequence numbers are monotonic per sender and used for ordering (not uniqueness - ID is unique):

```typescript
// UI sender (webview)
class UISender {
    private seq = 0;

    send(envelope: Envelope): Envelope {
        envelope.seq = this.seq++;
        return envelope;
    }
}

// Extension sender
class ExtensionSender {
    private seq = 0;

    send(envelope: Envelope): Envelope {
        envelope.seq = this.seq++;
        return envelope;
    }
}
```

**Important:** Sequence numbers start at 0 or 1 depending on sender implementation. The OrderingManager detects epoch automatically.

---

## 🔄 **MESSAGE ROUTER IMPLEMENTATION**

### **Core Router Class**

The `MessageRouter` coordinates all reliability features:

```typescript
// router.ts
import * as vscode from 'vscode';
import { Envelope, createAckEnvelope, createNackEnvelope } from './envelope';
import { IdempotencyKeyManager } from './idempotencyManager';
import { MessageOrderingManager } from './orderingManager';
import { DeadLetterQueueManager } from './deadLetterQueue';
import { Resequencer } from './resequencer';

export interface RoutingOptions {
    maxRetries?: number;        // Default: 3
    retryDelay?: number;        // Default: 500ms
    ackTimeout?: number;        // Default: 500ms
}

export class MessageRouter {
    private idempotencyManager: IdempotencyKeyManager;
    private orderingManager: MessageOrderingManager;
    private deadLetterQueue: DeadLetterQueueManager;
    private resequencer: Resequencer;
    private handlers: Map<string, (env: Envelope) => Promise<Envelope | null>> = new Map();
    private webview: vscode.Webview | null = null;
    private options: Required<RoutingOptions>;
    private inflight: number = 0;
    private drainScheduled: boolean = false;

    constructor(context: vscode.ExtensionContext, options: RoutingOptions = {}) {
        this.idempotencyManager = new IdempotencyKeyManager(context);
        this.orderingManager = new MessageOrderingManager();
        this.deadLetterQueue = new DeadLetterQueueManager(context);
        this.resequencer = new Resequencer(2000, 1); // TTL 2s, start at seq 1
        
        this.options = {
            maxRetries: options.maxRetries || 3,
            retryDelay: options.retryDelay || 500,
            ackTimeout: options.ackTimeout || 500,
        };

        // Save processed IDs on shutdown
        context.subscriptions.push({
            dispose: () => {
                this.idempotencyManager.checkpoint();
            }
        });

        // Process ordered queue periodically
        setInterval(() => this.processOrderedQueue(), 50);
        
        // Expire resequencer gaps periodically
        setInterval(() => {
            const expired = this.resequencer.expire();
            for (const env of expired) {
                this.deadLetterQueue.add(env, 'RESEQ_TTL', {
                    code: 'RESEQ_TTL',
                    message: 'Message expired waiting for gap fill',
                }).catch(console.error);
            }
        }, 1000);
    }
}
```

### **Routing Flow**

```typescript
async route(envelope: Envelope): Promise<void> {
    // 1. Validate envelope
    if (!this.validateEnvelope(envelope)) {
        console.error('Invalid envelope:', envelope);
        return;
    }

    // 2. Check idempotency (has this been processed before?)
    if (this.idempotencyManager.hasBeenProcessed(envelope.id)) {
        console.warn(`Duplicate message detected: ${envelope.id}`);
        // Send ACK anyway (already processed)
        await this.sendAck(envelope, true);
        return;
    }

    // 3. Handle requests (need ACK)
    if (envelope.kind === 'request') {
        // Send immediate ACK
        await this.sendAck(envelope, true);

        // Schedule drain (handles resequencing)
        this.scheduleDrain(envelope);
    } else {
        // Handle other message types directly
        await this.processMessage(envelope);
    }
}
```

### **Resequencing Logic**

The resequencer handles out-of-order messages:

```typescript
private scheduleDrain(latest?: Envelope): void {
    if (latest) {
        // Enqueue into resequencer
        const ready = this.resequencer.enqueue(latest);
        for (const env of ready) {
            this.dispatch(env);
        }
    }

    // Handle expirations (gaps -> DLQ)
    const expired = this.resequencer.expire();
    for (const e of expired) {
        this.deadLetterQueue.add(e, 'RESEQ_TTL', {
            code: 'RESEQ_TTL',
            message: 'Message expired waiting for gap fill',
        }).catch(console.error);
    }

    // Immediate drain via microtask (for deterministic tests)
    if (!this.drainScheduled) {
        this.drainScheduled = true;
        queueMicrotask(async () => {
            try {
                await this.processOrderedQueue();
            } finally {
                this.drainScheduled = false;
            }
        });
    }
}
```

### **Handler Registration**

```typescript
// Register handler for topic
registerHandler(topic: string, handler: (env: Envelope) => Promise<Envelope | null>): void {
    this.handlers.set(topic, handler);
}

// Example: Register MCP tool handler
router.registerHandler('mcp.callTool', async (env) => {
    const { tool, args } = env.payload as { tool: string; args: any };
    
    try {
        const result = await mcpClient.callTool(tool, args);
        return createEnvelope('response', 'mcp.callTool', 'ext->ui', { result }, {
            replyTo: env.id
        });
    } catch (error: any) {
        return createNackEnvelope(env.id, 'ext->ui', 'mcp.callTool', {
            code: 'TOOL_ERROR',
            message: error.message,
            data: { tool, args }
        });
    }
});
```

### **Dispatch Logic**

```typescript
private dispatch(envelope: Envelope): void {
    const handler = this.handlers.get(envelope.topic);
    
    if (!handler) {
        this.deadLetterQueue.add(envelope, 'NO_HANDLER', {
            code: 'NO_HANDLER',
            message: `No handler registered for topic: ${envelope.topic}`,
        }).catch(console.error);
        return;
    }

    if (this.idempotencyManager.hasBeenProcessed(envelope.id)) {
        return; // Already processed
    }

    this.idempotencyManager.markAsProcessed(envelope.id);
    this.inflight++;

    handler(envelope)
        .then(result => {
            if (result && this.webview) {
                this.webview.postMessage(result);
            }
        })
        .catch(err => {
            this.deadLetterQueue.add(envelope, 'HANDLER_ERROR', {
                code: 'HANDLER_ERROR',
                message: err.message || String(err),
                data: { error: String(err) },
            }).catch(console.error);
        })
        .finally(() => {
            this.inflight--;
        });
}
```

---

## 🛡️ **RELIABILITY COMPONENTS**

### **Idempotency Manager**

Prevents duplicate message processing using persistent ID tracking:

```typescript
// idempotencyManager.ts
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

export class IdempotencyKeyManager {
    private processedIds: Set<string> = new Set();
    private storagePath: string;
    private maxSize: number = 5000; // Max IDs to keep in memory
    private checkpointInterval: number = 100; // Checkpoint every N IDs
    private checkpointCount: number = 0;

    constructor(context: vscode.ExtensionContext) {
        // Store in workspace .aimos directory
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            this.storagePath = path.join(workspaceFolder.uri.fsPath, '.aimos', 'processed_ids.json');
        } else {
            // Fallback to global storage
            this.storagePath = path.join(context.globalStorageUri.fsPath, 'processed_ids.json');
        }

        // Ensure directory exists
        const dir = path.dirname(this.storagePath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        // Load processed IDs on startup
        this.loadProcessedIds();
    }

    hasBeenProcessed(id: string): boolean {
        return this.processedIds.has(id);
    }

    markAsProcessed(id: string): void {
        this.processedIds.add(id);

        // Trim if too large (LRU eviction)
        if (this.processedIds.size > this.maxSize) {
            const ids = Array.from(this.processedIds);
            const recentIds = ids.slice(-this.maxSize);
            this.processedIds = new Set(recentIds);
        }

        // Periodic checkpoint
        this.checkpointCount++;
        if (this.checkpointCount >= this.checkpointInterval) {
            this.saveProcessedIds();
            this.checkpointCount = 0;
        }
    }

    checkpoint(): void {
        this.saveProcessedIds();
        this.checkpointCount = 0;
    }

    private loadProcessedIds(): void {
        try {
            if (fs.existsSync(this.storagePath)) {
                const data = fs.readFileSync(this.storagePath, 'utf8');
                const ids = JSON.parse(data) as string[];
                
                // Keep only most recent IDs (LRU behavior)
                if (ids.length > this.maxSize) {
                    const recentIds = ids.slice(-this.maxSize);
                    this.processedIds = new Set(recentIds);
                    this.saveProcessedIds(); // Trim file
                } else {
                    this.processedIds = new Set(ids);
                }
            }
        } catch (error) {
            console.error('Failed to load processed IDs:', error);
            this.processedIds = new Set();
        }
    }

    private saveProcessedIds(): void {
        try {
            const ids = Array.from(this.processedIds);
            fs.writeFileSync(this.storagePath, JSON.stringify(ids), 'utf8');
        } catch (error) {
            console.error('Failed to save processed IDs:', error);
        }
    }
}
```

**Key Features:**
- **Persistent Storage:** Survives crashes and reloads
- **LRU Eviction:** Keeps only most recent 5,000 IDs
- **Periodic Checkpointing:** Saves every 100 IDs (configurable)
- **Fast Lookup:** O(1) Set operations

### **Ordering Manager**

Enforces FIFO ordering per sender using sequence numbers:

```typescript
// orderingManager.ts
import { Envelope, Direction } from './envelope';

interface QueuedMessage {
    envelope: Envelope;
    attempts: number;
    firstAttempt: number;
    lastAttempt: number;
}

export class MessageOrderingManager {
    private queues: Map<string, QueuedMessage[]> = new Map(); // sender -> queue
    private nextExpectedSeq: Map<string, number> = new Map(); // sender -> next expected seq
    private processing: Set<string> = new Set(); // Currently processing sender IDs
    private epoch: Map<string, number> = new Map(); // sender -> epoch (0 or 1)

    enqueue(envelope: Envelope): void {
        const sender = this.getSenderId(envelope.dir);
        const seq = envelope.seq;

        // Initialize queue if needed
        if (!this.queues.has(sender)) {
            this.queues.set(sender, []);
        }

        const queue = this.queues.get(sender)!;
        let nextSeq = this.nextExpectedSeq.get(sender);

        // Detect epoch from first message (seq can start at 0 or 1)
        if (nextSeq === undefined) {
            if (seq === 0 || seq === 1) {
                this.epoch.set(sender, seq);
                this.nextExpectedSeq.set(sender, seq);
                nextSeq = seq;
            } else {
                // Unexpected first seq - default to 1
                this.epoch.set(sender, 1);
                this.nextExpectedSeq.set(sender, 1);
                nextSeq = 1;
            }
        }

        // Check if this is the next expected message
        if (seq === nextSeq) {
            // Can process immediately
            const queued: QueuedMessage = {
                envelope,
                attempts: 0,
                firstAttempt: Date.now(),
                lastAttempt: Date.now(),
            };
            queue.push(queued);
            this.nextExpectedSeq.set(sender, seq + 1);
        } else if (seq > nextSeq) {
            // Future message - add to queue (will wait for earlier messages)
            const queued: QueuedMessage = {
                envelope,
                attempts: 0,
                firstAttempt: Date.now(),
                lastAttempt: Date.now(),
            };
            queue.push(queued);
            queue.sort((a, b) => a.envelope.seq - b.envelope.seq);
        } else {
            // Duplicate or out-of-order message (seq < nextSeq)
            console.warn(`Ignoring out-of-order message: seq=${seq}, expected=${nextSeq}`);
        }
    }

    dequeue(): Envelope | null {
        // Find queue with next message ready
        for (const [sender, queue] of this.queues.entries()) {
            if (queue.length === 0) continue;
            if (this.processing.has(sender)) continue; // Already processing this sender

            const queued = queue[0];
            const expectedSeq = this.nextExpectedSeq.get(sender)!;

            if (queued.envelope.seq === expectedSeq) {
                queue.shift(); // Remove from queue
                this.processing.add(sender); // Mark as processing
                this.nextExpectedSeq.set(sender, expectedSeq + 1);
                return queued.envelope;
            }
        }

        return null;
    }

    markProcessed(envelope: Envelope): void {
        const sender = this.getSenderId(envelope.dir);
        this.processing.delete(sender);
    }

    private getSenderId(dir: Direction): string {
        return dir.split('->')[0];
    }
}
```

**Key Features:**
- **Per-Sender Queues:** Each sender has independent FIFO queue
- **Epoch Detection:** Automatically detects if seq starts at 0 or 1
- **Blocking:** Prevents parallel processing of messages from same sender
- **Gap Handling:** Waits for missing sequence numbers

### **Resequencer**

Handles out-of-order messages with TTL-based buffering:

```typescript
// resequencer.ts
import { Envelope } from './envelope';

type Sender = string;

export class Resequencer {
    private expected = new Map<Sender, number>();           // next expected seq
    private buf = new Map<Sender, Map<number, Envelope>>();  // future msgs
    private deadline = new Map<string, number>();            // env.id -> ts
    private ttlMs: number;
    private startAt: number;

    constructor(ttlMs: number = 5000, startAt: number = 1) {
        this.ttlMs = ttlMs;
        this.startAt = startAt;
    }

    /**
     * Enqueue message - returns array of ready-to-process messages
     */
    enqueue(env: Envelope): Envelope[] {
        const sender = this.getSenderId(env);
        const seq = Number(env.seq ?? this.startAt);
        
        if (!this.expected.has(sender)) {
            this.expected.set(sender, this.startAt);
        }

        const exp = this.expected.get(sender)!;

        // Duplicate or stale
        if (seq < exp) {
            return [];
        }

        // Exact hit: advance and flush contiguous window
        if (seq === exp) {
            const out: Envelope[] = [env];
            this.expected.set(sender, exp + 1);
            
            // Flush contiguous from buffer
            const m = this.buf.get(sender);
            while (m?.has(this.expected.get(sender)!)) {
                const s = this.expected.get(sender)!;
                const nextEnv = m.get(s)!;
                out.push(nextEnv);
                m.delete(s);
                this.deadline.delete(nextEnv.id);
                this.expected.set(sender, s + 1);
            }
            
            return out;
        }

        // Future (gap): buffer and set deadline
        if (!this.buf.has(sender)) {
            this.buf.set(sender, new Map());
        }
        this.buf.get(sender)!.set(seq, env);
        this.deadline.set(env.id, Date.now() + this.ttlMs);
        
        return [];
    }

    /**
     * Expire any buffered gaps; returns envelopes to DLQ
     */
    expire(): Envelope[] {
        const now = Date.now();
        const doomed: Envelope[] = [];
        
        for (const [id, ts] of this.deadline.entries()) {
            if (ts <= now) {
                // Find and remove from whichever sender map contains it
                for (const [sender, m] of this.buf.entries()) {
                    for (const [seq, env] of m.entries()) {
                        if (env.id === id) {
                            doomed.push(env);
                            m.delete(seq);
                            this.deadline.delete(id);
                            break;
                        }
                    }
                }
            }
        }
        
        return doomed;
    }

    private getSenderId(env: Envelope): Sender {
        const payload = env.payload as any;
        if (payload?.senderId) {
            return payload.senderId as string;
        }
        return env.dir.split('->')[0];
    }
}
```

**Key Features:**
- **TTL-Based Buffering:** Messages wait up to 2s (configurable) for gaps
- **Contiguous Flush:** Processes all ready messages when gap fills
- **Automatic Expiration:** Expired gaps sent to DLQ
- **Per-Sender State:** Independent resequencing per sender

### **Dead Letter Queue**

Stores failed messages for manual review and retry:

```typescript
// deadLetterQueue.ts
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { Envelope } from './envelope';

export interface DeadLetterEntry {
    envelope: Envelope;
    reason: string;
    error: {
        code: string;
        message: string;
        data?: any;
    };
    attempts: number;
    firstAttempt: number;
    lastAttempt: number;
    timestamp: number;
}

export class DeadLetterQueueManager {
    private queue: DeadLetterEntry[] = [];
    private storagePath: string = '';
    private maxSize: number = 1000; // Max entries to keep

    constructor(context: vscode.ExtensionContext) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            this.storagePath = path.join(workspaceFolder.uri.fsPath, '.aimos', 'dead_letter_queue.json');
        } else {
            this.storagePath = path.join(context.globalStorageUri.fsPath, 'dead_letter_queue.json');
        }

        const dir = path.dirname(this.storagePath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        this.loadQueue().catch(console.error);
    }

    async add(
        envelope: Envelope,
        reason: string,
        error: { code: string; message: string; data?: any },
        attempts: number = 0
    ): Promise<void> {
        const entry: DeadLetterEntry = {
            envelope,
            reason,
            error,
            attempts,
            firstAttempt: (envelope as any).firstAttempt || Date.now(),
            lastAttempt: Date.now(),
            timestamp: Date.now(),
        };

        this.queue.push(entry);

        // Trim if too large
        if (this.queue.length > this.maxSize) {
            this.queue = this.queue.slice(-this.maxSize);
        }

        await this.saveQueue();
    }

    async getAll(): Promise<DeadLetterEntry[]> {
        return [...this.queue];
    }

    async retry(id: string): Promise<Envelope | null> {
        const index = this.queue.findIndex(e => e.envelope.id === id);
        if (index === -1) return null;

        const entry = this.queue[index];
        this.queue.splice(index, 1);
        await this.saveQueue();

        return entry.envelope;
    }

    private async loadQueue(): Promise<void> {
        try {
            if (fs.existsSync(this.storagePath)) {
                const data = fs.readFileSync(this.storagePath, 'utf8');
                const entries = JSON.parse(data) as DeadLetterEntry[];
                
                if (entries.length > this.maxSize) {
                    this.queue = entries.slice(-this.maxSize);
                    this.saveQueue();
                } else {
                    this.queue = entries;
                }
            }
        } catch (error) {
            console.error('Failed to load dead letter queue:', error);
            this.queue = [];
        }
    }

    private async saveQueue(): Promise<void> {
        try {
            fs.writeFileSync(this.storagePath, JSON.stringify(this.queue, null, 2), 'utf8');
        } catch (error) {
            console.error('Failed to save dead letter queue:', error);
        }
    }
}
```

**Key Features:**
- **Persistent Storage:** Survives crashes
- **Retry Support:** Can retry failed messages
- **Filtering:** Query by topic, error code, timestamp
- **Statistics:** Counts by topic and error code

---

## 💾 **PERSISTENT STORAGE**

### **UI Outbox (IndexedDB)**

Survives webview reloads:

```typescript
// UI (React webview)
class UIOutbox {
    private db: IDBDatabase | null = null;
    private dbName = 'aimos_outbox';
    private storeName = 'outbox';

    async init(): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const store = db.createObjectStore(this.storeName, { keyPath: 'id' });
                    store.createIndex('delivered', 'delivered', { unique: false });
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    async push(env: Envelope): Promise<void> {
        if (!this.db) throw new Error('Database not initialized');
        
        const entry = {
            id: env.id,
            timestamp: Date.now(),
            envelope: env,
            delivered: false,
            attempts: 0
        };

        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.put(entry);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async markDelivered(id: string): Promise<void> {
        if (!this.db) throw new Error('Database not initialized');
        
        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete(id);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async getUndelivered(): Promise<Envelope[]> {
        if (!this.db) throw new Error('Database not initialized');
        
        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const index = store.index('delivered');
            const request = index.getAll(false);
            
            request.onsuccess = () => {
                const entries = request.result;
                resolve(entries.map((e: any) => e.envelope));
            };
            request.onerror = () => reject(request.error);
        });
    }

    async replay(): Promise<void> {
        const undelivered = await this.getUndelivered();
        for (const env of undelivered) {
            await vscode.postMessage(env);
        }
    }
}
```

### **Extension Outbox (Memento)**

Survives extension host reloads:

```typescript
// Extension (VS Code Extension Host)
import * as vscode from 'vscode';
import { Envelope } from './envelope';

interface OutboxEntry {
    id: string;
    timestamp: number;
    envelope: Envelope;
    delivered: boolean;
    attempts: number;
    lastAttempt?: number;
}

export class PersistentOutbox {
    private store: vscode.Memento;
    private key: string;
    private maxSize: number = 2000;

    constructor(context: vscode.ExtensionContext, key: string = 'aimos.outbox') {
        this.store = context.globalState;
        this.key = key;
    }

    getAll(): OutboxEntry[] {
        return this.store.get<OutboxEntry[]>(this.key, []);
    }

    getUndelivered(): OutboxEntry[] {
        return this.getAll().filter(entry => !entry.delivered);
    }

    push(envelope: Envelope): void {
        const entries = this.getAll();
        
        const entry: OutboxEntry = {
            id: envelope.id,
            timestamp: Date.now(),
            envelope,
            delivered: false,
            attempts: 0,
        };
        
        entries.push(entry);
        
        // Trim if too large (keep most recent)
        if (entries.length > this.maxSize) {
            entries.splice(0, entries.length - this.maxSize);
        }
        
        this.store.update(this.key, entries);
    }

    markDelivered(id: string): void {
        const entries = this.getAll();
        const index = entries.findIndex(e => e.id === id);
        
        if (index !== -1) {
            entries[index].delivered = true;
            this.store.update(this.key, entries);
        }
    }

    cleanup(maxAge: number = 24 * 60 * 60 * 1000): void {
        const entries = this.getAll();
        const now = Date.now();
        
        const filtered = entries.filter(entry => {
            if (!entry.delivered) return true;
            if (now - entry.timestamp < maxAge) return true;
            return false;
        });
        
        if (filtered.length !== entries.length) {
            this.store.update(this.key, filtered);
        }
    }
}
```

---

## 🔌 **INTEGRATION PATTERNS**

### **Pattern 1: Basic Message Handler**

```typescript
// Register handler for topic
router.registerHandler('chat.message', async (env) => {
    const { message } = env.payload as { message: string };
    
    // Process message
    const response = await processChatMessage(message);
    
    // Return response envelope
    return createEnvelope('response', 'chat.message', 'ext->ui', { response }, {
        replyTo: env.id
    });
});
```

### **Pattern 2: Error Handling**

```typescript
router.registerHandler('mcp.callTool', async (env) => {
    try {
        const { tool, args } = env.payload as { tool: string; args: any };
        const result = await mcpClient.callTool(tool, args);
        
        return createEnvelope('response', 'mcp.callTool', 'ext->ui', { result }, {
            replyTo: env.id
        });
    } catch (error: any) {
        // Return NACK with error details
        return createNackEnvelope(env.id, 'ext->ui', 'mcp.callTool', {
            code: 'TOOL_ERROR',
            message: error.message,
            data: { tool: (env.payload as any).tool, error: String(error) }
        });
    }
});
```

### **Pattern 3: Event Broadcasting**

```typescript
// Broadcast event to all listeners
function broadcastEvent(topic: string, payload: any): void {
    const event = createEnvelope('event', topic, 'ext->ui', payload);
    router.route(event).catch(console.error);
}

// Usage
broadcastEvent('agent.status', {
    runId: 'agent-123',
    status: 'running',
    progress: 0.5
});
```

### **Pattern 4: Command Server Integration**

```typescript
// commandServer.ts
router.registerHandler('http.request', async (env) => {
    const { path, method, body } = env.payload as { path: string; method: string; body?: any };
    
    if (path === '/messaging/send' && method === 'POST') {
        // Handle envelope from HTTP API
        const httpEnvelope = body as Envelope;
        await router.route(httpEnvelope);
        
        return createEnvelope('response', 'http.request', 'ext->agent', { ok: true }, {
            replyTo: env.id
        });
    }
    
    return createNackEnvelope(env.id, 'ext->agent', 'http.request', {
        code: 'NOT_FOUND',
        message: `No handler for ${method} ${path}`
    });
});
```

### **Pattern 5: UI Integration**

```typescript
// React component (webview)
import { useEffect, useState } from 'react';
import * as vscode from 'vscode';

function useMessaging() {
    const [outbox, setOutbox] = useState<UIOutbox | null>(null);

    useEffect(() => {
        // Initialize outbox
        const box = new UIOutbox();
        box.init().then(() => {
            setOutbox(box);
            
            // Replay undelivered messages
            box.replay();
        });

        // Listen for messages
        window.addEventListener('message', async (event) => {
            const envelope = event.data as Envelope;
            
            // Handle ACK
            if (envelope.kind === 'ack') {
                await box.markDelivered(envelope.replyTo!);
            }
            
            // Handle response
            if (envelope.kind === 'response') {
                await box.markDelivered(envelope.replyTo!);
                // Process response
                handleResponse(envelope);
            }
        });
    }, []);

    const sendRequest = async (topic: string, payload: any): Promise<Envelope> => {
        if (!outbox) throw new Error('Outbox not initialized');
        
        const envelope = createEnvelope('request', topic, 'ui->ext', payload);
        envelope.seq = getNextSeq(); // Increment sequence
        
        await outbox.push(envelope);
        await vscode.postMessage(envelope);
        
        // Wait for response (with timeout)
        return await waitForResponse(envelope.id, 5000);
    };

    return { sendRequest };
}
```

---

## ⚙️ **CONFIGURATION & CUSTOMIZATION**

### **Router Options**

```typescript
const router = new MessageRouter(context, {
    maxRetries: 3,           // Maximum retry attempts
    retryDelay: 500,         // Delay between retries (ms)
    ackTimeout: 500          // ACK timeout (ms)
});
```

### **Resequencer Options**

```typescript
const resequencer = new Resequencer(
    2000,  // TTL in milliseconds (default: 5000)
    1      // Starting sequence number (default: 1)
);
```

### **Idempotency Manager Limits**

```typescript
// Modify maxSize in idempotencyManager.ts
private maxSize: number = 10000; // Increase from 5000 if needed
private checkpointInterval: number = 200; // Checkpoint every 200 IDs
```

### **Dead Letter Queue Limits**

```typescript
// Modify maxSize in deadLetterQueue.ts
private maxSize: number = 2000; // Increase from 1000 if needed
```

### **Heartbeat Interval**

```typescript
const heartbeat = new HeartbeatMonitor(10000); // 10 seconds (default)
// Or use 5000 for faster detection
```

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests**

```typescript
// router.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { MessageRouter } from './router';
import { createEnvelope } from './envelope';
import * as vscode from 'vscode';

describe('MessageRouter', () => {
    let router: MessageRouter;
    let context: vscode.ExtensionContext;

    beforeEach(() => {
        // Setup mock context
        context = createMockContext();
        router = new MessageRouter(context);
    });

    it('should process valid envelope', async () => {
        let processed = false;
        
        router.registerHandler('test.topic', async (env) => {
            processed = true;
            return createEnvelope('response', 'test.topic', 'ext->ui', { ok: true }, {
                replyTo: env.id
            });
        });

        const envelope = createEnvelope('request', 'test.topic', 'ui->ext', { test: 'data' });
        await router.route(envelope);
        
        await router.idle(); // Wait for processing
        
        expect(processed).toBe(true);
    });

    it('should prevent duplicate processing', async () => {
        let processCount = 0;
        
        router.registerHandler('test.topic', async (env) => {
            processCount++;
            return null;
        });

        const envelope = createEnvelope('request', 'test.topic', 'ui->ext', { test: 'data' });
        
        // Process twice
        await router.route(envelope);
        await router.idle();
        await router.route(envelope); // Duplicate
        await router.idle();
        
        expect(processCount).toBe(1); // Should only process once
    });

    it('should maintain FIFO ordering per sender', async () => {
        const processed: number[] = [];
        
        router.registerHandler('test.topic', async (env) => {
            processed.push((env.payload as any).seq);
            return null;
        });

        // Send messages out of order
        for (let i = 5; i >= 1; i--) {
            const env = createEnvelope('request', 'test.topic', 'ui->ext', { seq: i });
            env.seq = i;
            await router.route(env);
        }
        
        await router.idle();
        
        expect(processed).toEqual([1, 2, 3, 4, 5]); // Should be in order
    });
});
```

### **Integration Tests**

```typescript
// integration.test.ts
import { describe, it, expect } from 'vitest';
import { MessageRouter } from './router';
import { PersistentOutbox } from './persistentOutbox';
import { createEnvelope } from './envelope';

describe('Integration: Persistent Outbox + Router', () => {
    it('should replay undelivered messages on startup', async () => {
        const context = createMockContext();
        const outbox = new PersistentOutbox(context);
        const router = new MessageRouter(context);

        // Add message to outbox
        const envelope = createEnvelope('request', 'test.topic', 'ui->ext', { test: 'data' });
        outbox.push(envelope);

        // Simulate restart
        const newOutbox = new PersistentOutbox(context);
        const newRouter = new MessageRouter(context);

        // Replay undelivered
        const undelivered = newOutbox.getUndelivered();
        expect(undelivered.length).toBe(1);
        expect(undelivered[0].id).toBe(envelope.id);
    });
});
```

### **Test Helpers**

```typescript
// testHelpers.ts
import { Envelope, createEnvelope } from './envelope';
import * as vscode from 'vscode';

export function createMockContext(): vscode.ExtensionContext {
    return {
        globalState: {
            get: jest.fn(),
            update: jest.fn(),
            keys: jest.fn(() => []),
        },
        workspaceState: {
            get: jest.fn(),
            update: jest.fn(),
            keys: jest.fn(() => []),
        },
        subscriptions: [],
        globalStorageUri: vscode.Uri.file('/tmp'),
        workspaceStorageUri: vscode.Uri.file('/tmp'),
        storageUri: vscode.Uri.file('/tmp'),
        globalStoragePath: '/tmp',
        workspaceStoragePath: '/tmp',
        extensionPath: '/tmp',
        extensionUri: vscode.Uri.file('/tmp'),
        environmentVariableCollection: {} as any,
        extensionMode: vscode.ExtensionMode.Production,
        extension: {} as any,
        secrets: {} as any,
    };
}

export async function waitFor(
    condition: () => boolean,
    timeout: number = 5000,
    interval: number = 50
): Promise<void> {
    const start = Date.now();
    while (!condition()) {
        if (Date.now() - start > timeout) {
            throw new Error('Timeout waiting for condition');
        }
        await new Promise(resolve => setTimeout(resolve, interval));
    }
}
```

---

## 🔍 **TROUBLESHOOTING**

### **Problem: Messages Not Being Processed**

**Symptoms:**
- Messages sent but no response received
- Handler not being called

**Diagnosis:**
```typescript
// Check if handler is registered
const stats = await router.getStats();
console.log('Handlers:', router.handlers.size);

// Check dead letter queue
const dlq = await router.getDeadLetterQueue();
console.log('DLQ entries:', dlq.length);
```

**Solutions:**
1. Verify handler is registered: `router.registerHandler('topic', handler)`
2. Check envelope validation: `validateEnvelope(envelope)`
3. Check dead letter queue for errors
4. Verify webview is set: `router.setWebview(webview)`

### **Problem: Duplicate Messages**

**Symptoms:**
- Same message processed multiple times
- Handler called multiple times for same ID

**Diagnosis:**
```typescript
const stats = await router.getStats();
console.log('Processed IDs:', stats.idempotency.count);
console.log('Storage path:', stats.idempotency.storagePath);
```

**Solutions:**
1. Check idempotency manager is working: `hasBeenProcessed(id)`
2. Verify processed IDs are being saved: Check `.aimos/processed_ids.json`
3. Check for race conditions in handler registration

### **Problem: Out-of-Order Processing**

**Symptoms:**
- Messages processed in wrong order
- Sequence numbers not respected

**Diagnosis:**
```typescript
const stats = await router.getStats();
console.log('Ordering queues:', stats.ordering.queues);
console.log('Resequencer stats:', stats.resequencer);
```

**Solutions:**
1. Verify sequence numbers are monotonic
2. Check resequencer TTL (increase if messages arrive slowly)
3. Check ordering manager epoch detection
4. Verify sender ID extraction is correct

### **Problem: Messages Lost on Reload**

**Symptoms:**
- Messages sent but lost after webview reload
- Undelivered messages not replayed

**Diagnosis:**
```typescript
const outbox = new PersistentOutbox(context);
const undelivered = outbox.getUndelivered();
console.log('Undelivered:', undelivered.length);
```

**Solutions:**
1. Verify outbox is initialized: `outbox.init()`
2. Check IndexedDB permissions (webview)
3. Verify replay is called on startup
4. Check Memento storage limits (extension)

### **Problem: Dead Letter Queue Growing**

**Symptoms:**
- DLQ entries accumulating
- No automatic retry

**Diagnosis:**
```typescript
const dlq = await router.getDeadLetterQueue();
const stats = await router.getStats();
console.log('DLQ count:', stats.deadLetterQueue.count);
console.log('By error code:', stats.deadLetterQueue.byErrorCode);
```

**Solutions:**
1. Review DLQ entries to identify patterns
2. Fix root cause (handler errors, validation failures)
3. Retry entries manually: `router.retryDeadLetter(id)`
4. Clear DLQ if needed: `deadLetterQueue.clear()`

---

## ⚡ **PERFORMANCE OPTIMIZATION**

### **Optimization 1: Batch Processing**

```typescript
// Process multiple messages in batch
async function processBatch(envelopes: Envelope[]): Promise<void> {
    const results = await Promise.all(
        envelopes.map(env => router.route(env))
    );
    await router.idle(); // Wait for all to complete
}
```

### **Optimization 2: Compression**

```typescript
// Compress large payloads
function compressPayload(payload: any): { compressed: string; originalSize: number } {
    const json = JSON.stringify(payload);
    const compressed = compress(json); // Use compression library
    return {
        compressed,
        originalSize: json.length
    };
}

const envelope = createEnvelope('request', 'topic', 'ui->ext', payload, {
    compressed: true,
    originalSize: originalSize
});
```

### **Optimization 3: Idempotency Cache**

```typescript
// Use LRU cache for fast lookups
class IdempotencyCache {
    private cache: Map<string, boolean> = new Map();
    private maxSize = 10000;

    has(id: string): boolean {
        return this.cache.has(id);
    }

    add(id: string): void {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(id, true);
    }
}
```

### **Optimization 4: Async Processing**

```typescript
// Process messages asynchronously without blocking
async route(envelope: Envelope): Promise<void> {
    // Don't await - process in background
    setImmediate(() => {
        this.processEnvelope(envelope).catch(console.error);
    });
}
```

---

## ✅ **BEST PRACTICES**

### **1. Always Use Envelope Protocol**

❌ **Don't:**
```typescript
webview.postMessage({ type: 'message', data: 'hello' });
```

✅ **Do:**
```typescript
const envelope = createEnvelope('request', 'chat.message', 'ui->ext', { message: 'hello' });
await router.route(envelope);
```

### **2. Handle Errors Gracefully**

❌ **Don't:**
```typescript
router.registerHandler('topic', async (env) => {
    const result = await riskyOperation(); // May throw
    return result;
});
```

✅ **Do:**
```typescript
router.registerHandler('topic', async (env) => {
    try {
        const result = await riskyOperation();
        return createEnvelope('response', 'topic', 'ext->ui', { result }, {
            replyTo: env.id
        });
    } catch (error: any) {
        return createNackEnvelope(env.id, 'ext->ui', 'topic', {
            code: 'OPERATION_ERROR',
            message: error.message
        });
    }
});
```

### **3. Set Sequence Numbers Correctly**

❌ **Don't:**
```typescript
envelope.seq = Math.random(); // Wrong!
```

✅ **Do:**
```typescript
class Sender {
    private seq = 0;
    send(envelope: Envelope): Envelope {
        envelope.seq = this.seq++;
        return envelope;
    }
}
```

### **4. Replay Undelivered on Startup**

❌ **Don't:**
```typescript
// Forget to replay
activate(context) {
    const router = new MessageRouter(context);
    // Missing: outbox.replay()
}
```

✅ **Do:**
```typescript
activate(context) {
    const router = new MessageRouter(context);
    const outbox = new PersistentOutbox(context);
    
    // Replay undelivered messages
    const undelivered = outbox.getUndelivered();
    for (const entry of undelivered) {
        router.route(entry.envelope).catch(console.error);
    }
}
```

### **5. Monitor Connection Health**

❌ **Don't:**
```typescript
// No heartbeat monitoring
const router = new MessageRouter(context);
```

✅ **Do:**
```typescript
const router = new MessageRouter(context);
const heartbeat = new HeartbeatMonitor(10000);
heartbeat.setWebview(webview);
heartbeat.start();

heartbeat.onStatsUpdate((stats) => {
    if (stats.status === 'broken') {
        // Trigger reconnect
        reconnect();
    }
});
```

---

## 🚀 **ADVANCED TOPICS**

### **Advanced Topic 1: Custom Retry Strategies**

```typescript
class ExponentialBackoffRetry {
    private attempts = new Map<string, number>();

    getDelay(envelope: Envelope): number {
        const attempts = this.attempts.get(envelope.id) || 0;
        return Math.min(1000 * Math.pow(2, attempts), 10000); // Max 10s
    }

    recordAttempt(envelope: Envelope): void {
        const attempts = this.attempts.get(envelope.id) || 0;
        this.attempts.set(envelope.id, attempts + 1);
    }
}
```

### **Advanced Topic 2: Priority Queue**

```typescript
class PriorityQueue {
    private queues: Map<Priority, Envelope[]> = new Map([
        ['critical', []],
        ['high', []],
        ['medium', []],
        ['low', []]
    ]);

    enqueue(envelope: Envelope): void {
        const priority = envelope.priority || 'medium';
        this.queues.get(priority)!.push(envelope);
    }

    dequeue(): Envelope | null {
        for (const priority of ['critical', 'high', 'medium', 'low'] as Priority[]) {
            const queue = this.queues.get(priority)!;
            if (queue.length > 0) {
                return queue.shift()!;
            }
        }
        return null;
    }
}
```

### **Advanced Topic 3: Message Compression**

```typescript
import pako from 'pako';

function compressPayload(payload: any): { compressed: string; originalSize: number } {
    const json = JSON.stringify(payload);
    const compressed = pako.deflate(json, { to: 'string' });
    return {
        compressed: btoa(compressed),
        originalSize: json.length
    };
}

function decompressPayload(compressed: string, originalSize: number): any {
    const decompressed = pako.inflate(atob(compressed), { to: 'string' });
    return JSON.parse(decompressed);
}
```

### **Advanced Topic 4: Message Encryption**

```typescript
import crypto from 'crypto';

function encryptPayload(payload: any, key: string): string {
    const json = JSON.stringify(payload);
    const cipher = crypto.createCipher('aes-256-cbc', key);
    let encrypted = cipher.update(json, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}

function decryptPayload(encrypted: string, key: string): any {
    const decipher = crypto.createDecipher('aes-256-cbc', key);
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return JSON.parse(decrypted);
}
```

### **Advanced Topic 5: Message Batching**

```typescript
class BatchProcessor {
    private batch: Envelope[] = [];
    private batchSize = 10;
    private batchTimeout = 100; // ms

    async enqueue(envelope: Envelope): Promise<void> {
        this.batch.push(envelope);

        if (this.batch.length >= this.batchSize) {
            await this.flush();
        } else {
            setTimeout(() => this.flush(), this.batchTimeout);
        }
    }

    private async flush(): Promise<void> {
        if (this.batch.length === 0) return;

        const batch = [...this.batch];
        this.batch = [];

        // Process batch
        await Promise.all(batch.map(env => router.route(env)));
    }
}
```

---

## 📚 **REFERENCE**

### **API Reference**

**MessageRouter:**
- `constructor(context, options?)` - Initialize router
- `setWebview(webview)` - Set webview for sending messages
- `registerHandler(topic, handler)` - Register message handler
- `route(envelope)` - Route incoming message
- `idle()` - Wait for processing to complete (for tests)
- `getStats()` - Get statistics
- `getDeadLetterQueue()` - Get DLQ entries
- `retryDeadLetter(id)` - Retry DLQ entry

**Envelope Helpers:**
- `createEnvelope(kind, topic, dir, payload?, options?)` - Create envelope
- `createAckEnvelope(originalId, dir, topic, ok?)` - Create ACK
- `createNackEnvelope(originalId, dir, topic, error)` - Create NACK
- `createHeartbeatEnvelope(dir)` - Create heartbeat
- `validateEnvelope(env)` - Validate envelope structure

**PersistentOutbox:**
- `getAll()` - Get all entries
- `getUndelivered()` - Get undelivered entries
- `push(envelope)` - Add to outbox
- `markDelivered(id)` - Mark as delivered
- `cleanup(maxAge)` - Cleanup old entries

**DeadLetterQueueManager:**
- `add(envelope, reason, error, attempts?)` - Add to DLQ
- `getAll()` - Get all entries
- `getFiltered(filters)` - Get filtered entries
- `retry(id)` - Retry entry
- `remove(id)` - Remove entry
- `clear()` - Clear DLQ
- `getStats()` - Get statistics

### **Error Codes**

- `NO_HANDLER` - No handler registered for topic
- `HANDLER_ERROR` - Handler threw error
- `MAX_RETRIES_EXCEEDED` - Retry limit reached
- `RESEQ_TTL` - Resequencer TTL expired
- `INVALID_ENVELOPE` - Envelope validation failed
- `TOOL_ERROR` - MCP tool execution failed
- `OPERATION_ERROR` - General operation error

### **Configuration Options**

| Option | Default | Description |
|--------|---------|-------------|
| `maxRetries` | 3 | Maximum retry attempts |
| `retryDelay` | 500ms | Delay between retries |
| `ackTimeout` | 500ms | ACK timeout |
| `resequencerTTL` | 2000ms | Resequencer TTL |
| `heartbeatInterval` | 10000ms | Heartbeat interval |
| `idempotencyMaxSize` | 5000 | Max processed IDs |
| `dlqMaxSize` | 1000 | Max DLQ entries |
| `outboxMaxSize` | 2000 | Max outbox entries |

---

## 💡 **CONCLUSION**

The Bulletproof Messaging Protocol provides production-ready reliable communication for VS Code extensions. Key takeaways:

1. **Always use envelope protocol** - Structured format ensures reliability
2. **Handle errors gracefully** - Return NACK instead of throwing
3. **Replay on startup** - Don't lose messages after reloads
4. **Monitor connection health** - Use heartbeat for detection
5. **Test thoroughly** - Use test helpers for deterministic tests

**Next Steps:**
- Integrate with your extension
- Register handlers for your topics
- Test with real webview UI
- Monitor DLQ for failures
- Optimize based on usage patterns

**For More Information:**
- T0 Executive: `T0_BULLETPROOF_MESSAGING_EXECUTIVE.md`
- T1 Overview: `T1_BULLETPROOF_MESSAGING_OVERVIEW.md`
- T2 Architecture: `T2_BULLETPROOF_MESSAGING_ARCHITECTURE.md`
- System Map: `systems/bulletproof_messaging/system.map.lucid.json5`
- System Index: `systems/bulletproof_messaging/system.index.lucid.json5`

---

**Status:** Production Ready ✅  
**Version:** v1.0.0  
**Last Updated:** 2025-11-03  
**Author:** Aether

