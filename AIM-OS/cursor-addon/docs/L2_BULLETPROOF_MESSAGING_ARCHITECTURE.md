# L2: Bulletproof Messaging Protocol - Architecture

**Date:** 2025-11-03  
**Status:** Production Ready  
**Purpose:** Detailed architecture for bulletproof messaging protocol  
**Tags:** `#bulletproof-messaging` `#architecture` `#protocol` `#production-ready`  
**Level:** L2 Architecture (2,000+ words)  
**Related:** [L1_BULLETPROOF_MESSAGING_OVERVIEW.md](./L1_BULLETPROOF_MESSAGING_OVERVIEW.md) | [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) | [INDEX.md](./INDEX.md)

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Boundaries**

```
┌─────────────────────────────────────────────────────────────┐
│  UI Layer (React Webview)                                  │
│  - Envelope sender/receiver                                 │
│  - Persistent outbox (IndexedDB)                           │
│  - Event timeline (observability)                           │
└────────────────────┬────────────────────────────────────────┘
                     │ Envelope Protocol (v1)
                     │ vscode.postMessage()
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Extension Layer (VS Code Extension Host)                 │
│  - Message router                                           │
│  - Deduplication engine                                    │
│  - Retry coordinator                                       │
│  - Persistent outbox (Memento)                             │
│  - Heartbeat monitor                                        │
│  - Command gate + sandbox                                   │
│  - State checkpoint system                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP API (localhost:5001)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Electron App Layer (External)                             │
│  - Optional: Direct HTTP communication                      │
│  - Uses Command Server endpoints                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 **ENVELOPE PROTOCOL v1**

### **Type Definition**

```typescript
type Direction = 'ui->ext' | 'ext->ui' | 'ext->agent' | 'agent->ext';

export interface Envelope<T = unknown> {
  v: 1;                          // Protocol version
  id: string;                    // UUID (unique per message)
  seq: number;                   // Monotonic sequence per sender
  ts: number;                    // Date.now() timestamp
  dir: Direction;                 // Message direction
  kind: 'request' | 'response' | 'event' | 'ack' | 'nack' | 'heartbeat';
  topic: string;                 // Channel identifier (e.g., 'mcp.callTool', 'chat.message')
  replyTo?: string;              // ID of message being answered
  ok?: boolean;                  // For response/ack: success status
  err?: {                        // Error details (if ok=false)
    code: string;
    message: string;
    data?: any;
  };
  payload?: T;                   // Message payload (type-safe)
}
```

### **Message Kinds**

- **`request`**: Requires response (must receive `ack` within 250-500ms)
- **`response`**: Answers a request (uses same `id` or `replyTo`)
- **`event`**: One-way notification (no response needed)
- **`ack`**: Acknowledgment (received, processing)
- **`nack`**: Negative acknowledgment (rejected, error)
- **`heartbeat`**: Link health check (no payload)

### **Rules**

1. **Every `request` must receive `ack` within 250-500ms**
   - If no `ack` → Retry with same `id` (dedupe on receiver)
   - Maximum 3 retries before marking as failed

2. **`response` uses same `id` or includes `replyTo`**
   - Allows matching request → response

3. **Keep recent-ids LRU (2-5k) to drop duplicates**
   - Prevents duplicate processing
   - Circular buffer implementation

4. **Sequence numbers are monotonic per sender**
   - UI: Starts at 0, increments per message
   - Extension: Starts at 0, increments per message
   - Used for ordering, not uniqueness (ID is unique)

---

## 🔄 **MESSAGE FLOW PATTERNS**

### **Pattern 1: Normal Request/Response**

```
UI sends:
{
  v: 1,
  id: "uuid-1",
  seq: 1,
  ts: Date.now(),
  dir: "ui->ext",
  kind: "request",
  topic: "mcp.callTool",
  payload: { tool: "store_memory", args: {...} }
}

Extension receives → Immediately sends ACK:
{
  v: 1,
  id: "uuid-ack-1",
  replyTo: "uuid-1",
  seq: 1,
  ts: Date.now(),
  dir: "ext->ui",
  kind: "ack",
  topic: "mcp.callTool",
  ok: true
}

Extension processes → Sends response:
{
  v: 1,
  id: "uuid-resp-1",
  replyTo: "uuid-1",
  seq: 2,
  ts: Date.now(),
  dir: "ext->ui",
  kind: "response",
  topic: "mcp.callTool",
  ok: true,
  payload: { result: {...} }
}
```

### **Pattern 2: Retry on ACK Timeout**

```
UI sends request → Starts timeout timer (500ms)
No ACK received after 500ms → Retry with SAME ID:
{
  v: 1,
  id: "uuid-1",  // SAME ID
  seq: 2,        // Incremented seq
  ts: Date.now(),
  dir: "ui->ext",
  kind: "request",
  topic: "mcp.callTool",
  payload: {...}
}

Extension receives duplicate → Checks recent-ids LRU
Seen "uuid-1" → Dedupe → Send ACK (already processing)
```

### **Pattern 3: Error Handling**

```
Extension processes request → Error occurs:
{
  v: 1,
  id: "uuid-resp-1",
  replyTo: "uuid-1",
  seq: 2,
  ts: Date.now(),
  dir: "ext->ui",
  kind: "response",
  topic: "mcp.callTool",
  ok: false,
  err: {
    code: "TOOL_NOT_FOUND",
    message: "MCP tool 'invalid_tool' not found",
    data: { available_tools: [...] }
  }
}
```

---

## 💾 **PERSISTENT QUEUES**

### **UI Outbox (IndexedDB)**

**Schema:**
```typescript
interface OutboxEntry {
  id: string;           // Envelope ID
  ts: number;           // Timestamp when added
  env: Envelope;        // Full envelope
  delivered: boolean;   // Delivery status
  attempts: number;     // Retry count
  last_attempt_ts?: number; // Last retry timestamp
}
```

**Operations:**
- `push(env: Envelope)`: Add to outbox
- `markDelivered(id: string)`: Mark as delivered, remove
- `getUndelivered()`: Get all undelivered entries
- `replay()`: On startup, replay all undelivered

**Implementation:**
```typescript
class Outbox {
  private db: IDBDatabase;
  
  async push(env: Envelope): Promise<void> {
    const entry: OutboxEntry = {
      id: env.id,
      ts: Date.now(),
      env,
      delivered: false,
      attempts: 0
    };
    await this.db.put('outbox', entry);
  }
  
  async markDelivered(id: string): Promise<void> {
    await this.db.delete('outbox', id);
  }
  
  async getUndelivered(): Promise<OutboxEntry[]> {
    // Query IndexedDB for delivered=false
  }
  
  async replay(): Promise<void> {
    const undelivered = await this.getUndelivered();
    for (const entry of undelivered) {
      await this.send(entry.env);
    }
  }
}
```

### **Extension Outbox (Memento)**

**Storage:**
- Uses `context.globalState` (Memento API)
- Key: `'aimos.outbox'`
- Value: `Envelope[]` (JSON serialized)

**Operations:**
```typescript
class ExtensionOutbox {
  constructor(private store: vscode.Memento, private key = 'aimos.outbox') {}
  
  all(): Envelope[] {
    return this.store.get(this.key, []);
  }
  
  push(env: Envelope): void {
    const arr = this.all();
    arr.push(env);
    this.store.update(this.key, arr);
  }
  
  markDelivered(id: string): void {
    const arr = this.all();
    const filtered = arr.filter(e => e.id !== id);
    this.store.update(this.key, filtered);
  }
  
  async replay(): Promise<void> {
    const undelivered = this.all().filter(e => !e.delivered);
    for (const env of undelivered) {
      await this.send(env);
    }
  }
}
```

---

## 💓 **HEARTBEAT + LINK STATUS**

### **Heartbeat Protocol**

**Extension → UI:**
```typescript
// Extension sends heartbeat every 10s
setInterval(() => {
  const heartbeat: Envelope = {
    v: 1,
    id: crypto.randomUUID(),
    seq: 0,
    ts: Date.now(),
    dir: 'ext->ui',
    kind: 'heartbeat',
    topic: 'link'
  };
  webview.postMessage(heartbeat);
}, 10000);
```

**UI → Extension (Echo):**
```typescript
// UI receives heartbeat → Echoes with ACK
window.addEventListener('message', (e) => {
  const env = e.data as Envelope;
  if (env.kind === 'heartbeat') {
    const rtt = Date.now() - env.ts;
    const echo: Envelope = {
      v: 1,
      id: crypto.randomUUID(),
      replyTo: env.id,
      seq: seq++,
      ts: Date.now(),
      dir: 'ui->ext',
      kind: 'ack',
      topic: 'link',
      ok: true,
      payload: { rtt }
    };
    vscode.postMessage(echo);
  }
});
```

### **Link Status Indicators**

**RTT Calculation:**
- UI measures: `Date.now() - env.ts` (from heartbeat)
- Extension measures: `Date.now() - env.ts` (from echo)

**Status Levels:**
- **Green** (< 500ms): Healthy connection
- **Amber** (0.5-2s): Degraded, but functional
- **Red** (> 2s or missed 3 beats): Broken → Trigger reconnect

**Reconnect Protocol:**
1. Mark link as broken (red status)
2. Reload webview (re-initialize connection)
3. Re-handshake (capability negotiation)
4. Replay unacked outbox (resend pending messages)

---

## 🤝 **CAPABILITY NEGOTIATION**

### **Handshake Protocol**

**On Connect:**
```typescript
// UI sends handshake request
const handshake: Envelope = {
  v: 1,
  id: crypto.randomUUID(),
  seq: 0,
  ts: Date.now(),
  dir: 'ui->ext',
  kind: 'request',
  topic: 'handshake',
  payload: {
    protoVersion: 1,
    uiVersion: '1.0.0',
    capabilities: ['chat', 'mcp', 'state']
  }
};

// Extension responds with capabilities
const response: Envelope = {
  v: 1,
  id: crypto.randomUUID(),
  replyTo: handshake.id,
  seq: 1,
  ts: Date.now(),
  dir: 'ext->ui',
  kind: 'response',
  topic: 'handshake',
  ok: true,
  payload: {
    protoVersion: 1,
    extensionVersion: '1.0.0',
    agentCaps: ['chat', 'plan', 'run:test', 'run:lint', 'mcp:tools:writeFile,searchCode'],
    supportedCommands: ['mcp.callTool', 'chat.message', 'state.get'],
    maxPayloadSize: 10 * 1024 * 1024, // 10MB
    heartbeatInterval: 10000 // 10s
  }
};
```

**Capability Format:**
```typescript
interface Capabilities {
  protoVersion: number;        // Protocol version
  extensionVersion: string;    // Extension version
  agentCaps: string[];         // Agent capabilities (e.g., ['chat', 'plan', 'run:test'])
  supportedCommands: string[]; // Supported command topics
  maxPayloadSize: number;      // Maximum payload size (bytes)
  heartbeatInterval: number;   // Heartbeat interval (ms)
}
```

### **Capability Mapping**

**Agent Capabilities → Whitelisted Commands:**
```typescript
const capabilityMap: Record<string, string[]> = {
  'chat': ['chat.message', 'chat.send'],
  'plan': ['plan.create', 'plan.execute'],
  'run:test': ['cmd.run', 'cmd.test'],
  'run:lint': ['cmd.run', 'cmd.lint'],
  'mcp:tools:writeFile': ['mcp.callTool'], // Only writeFile tool
  'mcp:tools:searchCode': ['mcp.callTool'], // Only searchCode tool
};
```

**Command Gate:**
- Check if command topic is in `supportedCommands`
- Check if agent capability matches command requirement
- If not permitted → Return `nack` with `code: "NOT_PERMITTED"`

---

## 🛡️ **COMMAND GATE + SANDBOX**

### **Command Gate Rules**

**Whitelist-Only:**
- Only commands in `supportedCommands` are allowed
- Only tools in `agentCaps` are allowed
- Everything else returns `nack {code: "NOT_PERMITTED"}`

**Sandbox Requirements:**
- Terminal invocations must be idempotent (`--ci`, `-q`, no prompts)
- Record every shell run in ring buffer (visible in panel)
- Maximum execution time: 5 minutes
- Maximum output size: 10MB

**Implementation:**
```typescript
class CommandGate {
  private allowedCommands: Set<string>;
  private allowedCaps: Set<string>;
  
  constructor(capabilities: Capabilities) {
    this.allowedCommands = new Set(capabilities.supportedCommands);
    this.allowedCaps = new Set(capabilities.agentCaps);
  }
  
  async execute(command: string, args: any): Promise<Envelope> {
    // Check whitelist
    if (!this.allowedCommands.has(command)) {
      return {
        v: 1,
        id: crypto.randomUUID(),
        seq: 0,
        ts: Date.now(),
        dir: 'ext->ui',
        kind: 'nack',
        topic: command,
        ok: false,
        err: {
          code: 'NOT_PERMITTED',
          message: `Command '${command}' not in whitelist`
        }
      };
    }
    
    // Execute in sandbox
    return await this.sandbox.execute(command, args);
  }
}
```

---

## 📊 **STATE-OF-WORLD LOG + CHECKPOINTS**

### **State Checkpoint Format**

**File:** `.aimos/runtime/state.json`

```json
{
  "plan_id": "passkeys-01",
  "step": 5,
  "since": "2025-11-03T16:29:00Z",
  "last_ok_commit": "agent/passkeys-WIP@a1b2c3d",
  "next_action": "write test for resident key fallback",
  "budget": {
    "minutes_remaining": 72
  },
  "checkpoint": {
    "timestamp": "2025-11-03T16:29:00Z",
    "step": 5,
    "status": "in_progress",
    "context": {
      "files_modified": ["src/auth.ts", "tests/auth.test.ts"],
      "tests_passing": 12,
      "tests_failing": 0
    }
  }
}
```

### **Checkpoint Operations**

**Create Checkpoint:**
```typescript
async function createCheckpoint(planId: string, step: number, context: any): Promise<void> {
  const state = {
    plan_id: planId,
    step,
    since: new Date().toISOString(),
    last_ok_commit: await getLastCommit(),
    next_action: context.nextAction,
    budget: context.budget,
    checkpoint: {
      timestamp: new Date().toISOString(),
      step,
      status: 'in_progress',
      context
    }
  };
  
  await fs.writeFile('.aimos/runtime/state.json', JSON.stringify(state, null, 2));
}
```

**Resume from Checkpoint:**
```typescript
async function resumeFromCheckpoint(): Promise<State | null> {
  const statePath = '.aimos/runtime/state.json';
  if (!fs.existsSync(statePath)) {
    return null;
  }
  
  const state = JSON.parse(await fs.readFile(statePath, 'utf8'));
  
  // Prompt user: "Resume plan at step 5?"
  // If auto-resume enabled: Continue after 10s grace timer
  
  return state;
}
```

---

## 🔍 **OBSERVABILITY**

### **Event Timeline**

**Panel Tab:** "Event Timeline"

**Display:**
- Every envelope compact-logged with `topic`, `Δt`, `size`
- Sortable by timestamp, topic, direction
- Filterable by kind, topic, direction

**Format:**
```
[2025-11-03 16:29:00] ui->ext | request | mcp.callTool | 250ms | 1.2KB
[2025-11-03 16:29:00] ext->ui | ack     | mcp.callTool | 5ms   | 200B
[2025-11-03 16:29:01] ext->ui | response| mcp.callTool | 350ms | 2.1KB
```

### **Watchdogs**

**No Output Watchdog:**
- If no output for N minutes → Post `diagnostic.request` to agent
- If still silent → Restart agent with last `state.json`

**Heartbeat Watchdog:**
- If missed 3 heartbeats → Mark link broken
- Trigger reconnect protocol

### **Commit Cadence**

**Enforcement:**
- Commit every 10-20 minutes with tag `agent:<plan>#<step>`
- Push to WIP branch: `agent/<plan>-wip`

**Checkpoint Before Commit:**
- Create state checkpoint
- Commit with checkpoint reference
- Push to WIP branch

---

## 🧪 **SMOKE TESTS**

### **Test 1: Load/Reload**

**Scenario:** Webview reload doesn't lose pending messages

**Steps:**
1. Send 5 messages from UI
2. Close webview (don't wait for responses)
3. Reopen webview
4. Verify: Outbox replays all 5 messages

**Expected:** All 5 messages delivered, no duplicates

---

### **Test 2: Network Blip**

**Scenario:** Disconnect agent for 60s → UI stays responsive, buffer drains on reconnect

**Steps:**
1. Send 10 messages
2. Disconnect extension (kill process)
3. Wait 60s (UI should show "Disconnected" status)
4. Reconnect extension
5. Verify: All 10 messages delivered

**Expected:** No messages lost, all delivered after reconnect

---

### **Test 3: Dedupe**

**Scenario:** Send duplicate `id` → Processed once

**Steps:**
1. Send message with `id: "test-1"`
2. Immediately send same message with `id: "test-1"`
3. Verify: Only one response received

**Expected:** Extension deduplicates, processes once

---

### **Test 4: Command Gate**

**Scenario:** Attempt disallowed command → `nack NOT_PERMITTED`

**Steps:**
1. Send command: `{topic: "dangerous.command", ...}`
2. Verify: Receives `nack` with `code: "NOT_PERMITTED"`
3. Verify: Toast notification shown

**Expected:** Command rejected, user notified

---

### **Test 5: Resume**

**Scenario:** Kill VS Code → Reopen → Panel shows state and resumes

**Steps:**
1. Create checkpoint: `{plan_id: "test", step: 3}`
2. Close VS Code completely
3. Reopen VS Code
4. Open panel
5. Verify: Shows "Resume plan at step 3?" prompt

**Expected:** State persisted, resume prompt shown

---

**Next:** See L3_detailed.md for implementation guide

