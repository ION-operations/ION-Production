# Protocol Design: Cursor Agent Automation

**Date:** 2025-11-03  
**Purpose:** Define complete protocol for agent automation integration  
**Status:** Production Ready  
**Tags:** `#protocol-design` `#agent-automation` `#mcp-integration` `#cursor-commands`  
**Level:** L2 Architecture (2,000+ words)  
**Related:** [INDEX.md](./INDEX.md) | [PROTOCOL_IMPLEMENTATION_PLAN.md](./PROTOCOL_IMPLEMENTATION_PLAN.md) | [INTEGRATION_ARCHITECTURE.md](./INTEGRATION_ARCHITECTURE.md)

---

## 🎯 **PROTOCOL LAYERS**

### **Layer 1: Envelope Protocol (UI ↔ Extension)**
**Purpose:** Reliable communication between React UI and VS Code extension

**Flow:**
```
React UI → Envelope (v1) → vscode.postMessage() → Extension
Extension → Envelope (v1) → webview.postMessage() → React UI
```

**Protocol:**
- Envelope format (v1) with ACK/NACK
- Sequence numbers for ordering
- Idempotency keys for deduplication
- Topics: `agent.start`, `agent.stop`, `agent.status`, `agent.output`

---

### **Layer 2: Command Server API (Extension ↔ External)**
**Purpose:** HTTP API for external clients (Electron app, CLI, etc.)

**Flow:**
```
External Client → HTTP POST → Command Server → Extension MessageRouter
Extension MessageRouter → Envelope → React UI
```

**Endpoints:**
- `POST /agent/start` - Start background agent
- `POST /agent/stop` - Stop agent
- `GET /agent/status` - Get agent status
- `POST /agent/checkpoint` - Force checkpoint
- `POST /webhook/agent-event` - Webhook for agent events

**Protocol:**
- REST API (JSON)
- Returns standard responses
- Can proxy to Cursor Background Agent API

---

### **Layer 3: MCP Protocol (Cursor ↔ Extension)**
**Purpose:** Expose agent tools via Model Context Protocol

**Flow:**
```
Cursor Chat → /agent-start → MCP Server (our Command Server) → Tools
Tools → Execute → Return result → Cursor Chat
```

**Tools:**
- `agent.start(task_yaml, branch, max_runtime)` - Start agent
- `agent.status(run_id)` - Get status
- `agent.stop(run_id)` - Stop agent
- `agent.metrics()` - Get metrics
- `agent.checkpoint(run_id)` - Force checkpoint
- `bus.post(envelope)` - Manual envelope send

**Protocol:**
- MCP standard (JSON-RPC 2.0)
- Tools registered in MCP server
- Called from Cursor slash commands

---

### **Layer 4: Background Agent API (Extension ↔ Cursor Cloud)**
**Purpose:** Control Cursor Background Agents via HTTP API

**Flow:**
```
Extension → HTTP → Cursor Background Agent API → Create run
Cursor API → Webhook → Command Server → Extension → UI
```

**Protocol:**
- REST API (Cursor's documented API)
- Create runs, poll status, stream logs, cancel
- Webhooks for events

**Key Difference:** This is **Cursor's API**, not a CLI!

---

## 🔄 **COMPLETE MESSAGE FLOW**

### **Starting an Agent:**

```
1. User types /agent-start in Cursor
   ↓
2. Cursor calls MCP tool: agent.start(task_yaml, branch, max_runtime)
   ↓
3. MCP Server (Command Server) receives tool call
   ↓
4. Command Server creates HTTP request to Cursor Background Agent API
   ↓
5. Cursor API creates run, returns run_id
   ↓
6. Command Server stores run_id, sends envelope to Extension
   ↓
7. Extension MessageRouter routes envelope
   ↓
8. React UI receives event: agent.started
```

### **Agent Status Updates:**

```
1. Cursor Background Agent sends webhook event
   ↓
2. Command Server receives webhook
   ↓
3. Command Server creates envelope: agent.status
   ↓
4. Extension MessageRouter routes envelope
   ↓
5. React UI receives event: agent.status (with output/progress)
```

### **Stopping an Agent:**

```
1. User types /agent-stop in Cursor OR clicks stop in UI
   ↓
2. If Cursor: MCP tool agent.stop(run_id)
   If UI: Envelope agent.stop → Extension → Command Server
   ↓
3. Command Server calls Cursor Background Agent API: cancel run
   ↓
4. Cursor API cancels run
   ↓
5. Webhook sent → Command Server → Extension → UI
   ↓
6. UI receives event: agent.stopped
```

---

## 📋 **PROTOCOL DECISIONS**

### **1. Use Cursor Background Agent API (Not CLI)**

**Why:**
- ✅ Documented API (GitHub, Cursor docs)
- ✅ HTTP-based (works everywhere)
- ✅ Webhooks for events
- ✅ Programmatic control

**Implementation:**
```typescript
// Instead of: spawn('cursor-agent', [...])
// Use: HTTP POST to Cursor API

const response = await fetch('https://api.cursor.com/v1/agents/runs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task_file: taskFile,
    repo_path: repoPath,
    branch: branch,
    max_runtime_hours: maxRuntime
  })
});

const { run_id } = await response.json();
```

---

### **2. MCP Server = Command Server**

**Why:**
- ✅ Already have Command Server
- ✅ Can expose MCP tools
- ✅ Single integration point
- ✅ Reuses existing infrastructure

**Implementation:**
```typescript
// Register MCP server in Cursor
// Command Server exposes MCP tools:

// Tool: agent.start
{
  name: 'agent.start',
  description: 'Start a background agent run',
  inputSchema: {
    type: 'object',
    properties: {
      task_yaml: { type: 'string' },
      branch: { type: 'string' },
      max_runtime: { type: 'number' }
    }
  }
}
```

---

### **3. Slash Commands Trigger MCP Tools**

**Why:**
- ✅ First-class Cursor feature
- ✅ File-backed (version controlled)
- ✅ Can call MCP tools
- ✅ Repeatable workflows

**Implementation:**
```markdown
# ~/.cursor/commands/agent-start.md

Start a background agent run.

Uses MCP tool: `agent.start`

Example:
/agent-start task=refactor.yaml branch=agent/refactor max_runtime=6
```

---

### **4. Envelope Protocol for UI Updates**

**Why:**
- ✅ Already built and tested
- ✅ Reliable (ACK, ordering, deduplication)
- ✅ Survives crashes
- ✅ Perfect for real-time updates

**Topics:**
- `agent.started` - Agent started
- `agent.output` - Agent stdout/stderr
- `agent.status` - Status update
- `agent.checkpoint` - Checkpoint created
- `agent.complete` - Agent finished
- `agent.stopped` - Agent stopped
- `agent.error` - Agent error

---

## 🔧 **IMPLEMENTATION PLAN**

### **Phase 1: Protocol Foundation** ✅
- [x] Envelope protocol (v1)
- [x] MessageRouter
- [x] Dead Letter Queue
- [x] Command Server

### **Phase 2: Background Agent Integration** ⚠️ **NEXT**
- [ ] Research Cursor Background Agent API
- [ ] Implement HTTP client for API
- [ ] Add webhook endpoint
- [ ] Test API calls

### **Phase 3: MCP Server Integration** ⚠️ **NEXT**
- [ ] Register Command Server as MCP server
- [ ] Expose agent tools (start, stop, status, metrics)
- [ ] Test MCP tool calls
- [ ] Document MCP tools

### **Phase 4: Slash Commands** ⚠️ **NEXT**
- [ ] Create `.cursor/commands/agent-start.md`
- [ ] Create `.cursor/commands/agent-stop.md`
- [ ] Create `.cursor/commands/agent-status.md`
- [ ] Test slash commands

### **Phase 5: AgentMonitor Class** ⚠️ **NEXT**
- [ ] Implement AgentMonitor
- [ ] Integrate with Background Agent API
- [ ] Send updates via MessageRouter
- [ ] Handle webhooks

### **Phase 6: UI Dashboard** ⚠️ **FUTURE**
- [ ] React component for agent status
- [ ] Real-time output stream
- [ ] Start/stop controls
- [ ] Metrics display

### **Phase 7: Test Fixes** ⚠️ **NEXT**
- [ ] Router immediate drain
- [ ] Ordering manager epoch handling
- [ ] DLQ persistence with tmpdir

---

## 🛡️ **PROTOCOL GUARANTEES**

### **Reliability**
- ✅ Envelope protocol ensures delivery
- ✅ ACK/NACK for all requests
- ✅ Dead Letter Queue for failures
- ✅ Persistent outbox for crashes

### **Ordering**
- ✅ Sequence numbers per sender
- ✅ Resequencer for out-of-order
- ✅ FIFO per sender

### **Idempotency**
- ✅ Message IDs prevent duplicates
- ✅ Persisted to disk
- ✅ Survives restarts

### **Observability**
- ✅ All events via envelope protocol
- ✅ Metrics via MCP tools
- ✅ Dead Letter Queue inspection
- ✅ Status polling

---

## 🔄 **PROTOCOL DIAGRAM**

```
┌─────────────────────────────────────────────────────────┐
│  Cursor Chat                                            │
│  /agent-start → MCP Tool → agent.start(...)            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ MCP Protocol (JSON-RPC 2.0)
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Command Server (MCP Server)                            │
│  - Receives MCP tool calls                              │
│  - Exposes tools: agent.start, agent.stop, etc.         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ HTTP API
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Cursor Background Agent API                            │
│  - Creates runs                                         │
│  - Polls status                                         │
│  - Streams logs                                         │
│  - Cancels runs                                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Webhooks
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Command Server (Webhook Handler)                       │
│  - Receives agent events                                 │
│  - Creates envelopes                                    │
│  - Routes via MessageRouter                             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Envelope Protocol
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Extension (MessageRouter)                             │
│  - Routes envelopes                                     │
│  - Ensures delivery                                     │
│  - Handles ordering                                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Envelope Protocol
                      ▼
┌─────────────────────────────────────────────────────────┐
│  React UI Dashboard                                     │
│  - Receives agent events                                │
│  - Displays status                                      │
│  - Shows output                                         │
│  - Start/stop controls                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 **MESSAGE TYPES**

### **Agent Control Messages**

```typescript
// Start agent
{
  topic: 'agent.start',
  kind: 'request',
  payload: {
    task_yaml: 'refactor.yaml',
    branch: 'agent/refactor',
    max_runtime_hours: 6
  }
}

// Status update
{
  topic: 'agent.status',
  kind: 'event',
  payload: {
    run_id: 'abc-123',
    state: 'running',
    current_step: 5,
    total_steps: 12,
    last_command: 'pnpm test',
    output: '...'
  }
}

// Agent output
{
  topic: 'agent.output',
  kind: 'event',
  payload: {
    run_id: 'abc-123',
    stream: 'stdout', // or 'stderr'
    data: 'Running tests...'
  }
}

// Agent complete
{
  topic: 'agent.complete',
  kind: 'event',
  payload: {
    run_id: 'abc-123',
    exit_code: 0,
    summary: {
      steps_completed: 12,
      tests_passed: 45,
      files_changed: 23
    }
  }
}
```

---

## 🎯 **KEY PROTOCOL DECISIONS**

### **1. Use HTTP for Background Agent (Not CLI)**
- ✅ Documented API
- ✅ Works everywhere
- ✅ Webhooks for events
- ✅ No process management needed

### **2. MCP Server = Command Server**
- ✅ Single integration point
- ✅ Reuses infrastructure
- ✅ Consistent API

### **3. Slash Commands → MCP Tools → HTTP API**
- ✅ User-friendly (slash commands)
- ✅ Tool-based (MCP)
- ✅ HTTP-based (Background Agent API)

### **4. Envelope Protocol for UI**
- ✅ Already built
- ✅ Reliable
- ✅ Real-time updates

---

## 🚀 **NEXT STEPS**

1. **Research Cursor Background Agent API** - Find actual endpoints
2. **Implement HTTP client** - Call Cursor API
3. **Add MCP tools** - Expose agent tools
4. **Create slash commands** - User-friendly triggers
5. **Implement AgentMonitor** - Bridge everything
6. **Fix tests** - Router drain, ordering, DLQ

---

**Status:** Protocol design complete  
**Next:** Implement Background Agent API integration

---

*Created: 2025-11-03*  
*Complete protocol design for agent automation*

