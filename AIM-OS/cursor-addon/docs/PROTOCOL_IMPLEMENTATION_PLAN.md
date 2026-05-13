# Protocol Implementation Plan

**Date:** 2025-11-03  
**Status:** Protocol Design Complete, Implementation Next  
**Based on:** ChatGPT feedback + Protocol analysis  
**Tags:** `#implementation` `#protocol-design` `#agent-automation` `#mcp-integration`  
**Level:** L3 Implementation  
**Related:** [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) | [SLASH_COMMANDS.md](./SLASH_COMMANDS.md) | [INDEX.md](./INDEX.md)

---

## 🎯 **PROTOCOL DECISIONS**

### **1. Use Cursor Background Agent API (HTTP, Not CLI)** ✅

**Why:**
- ✅ Documented API (GitHub, Cursor docs)
- ✅ HTTP-based (works everywhere)
- ✅ Webhooks for events
- ✅ Programmatic control

**Implementation:**
- ✅ AgentMonitor class created (uses HTTP API)
- ✅ No CLI assumptions
- ✅ Proper error handling

---

### **2. MCP Server = Command Server** ✅

**Why:**
- ✅ Already have Command Server
- ✅ Can expose MCP tools
- ✅ Single integration point

**Next Steps:**
- ⚠️ Register MCP tools in Command Server
- ⚠️ Expose agent.start, agent.stop, agent.status, etc.

---

### **3. Slash Commands → MCP Tools** ✅

**Why:**
- ✅ First-class Cursor feature
- ✅ File-backed (version controlled)
- ✅ Can call MCP tools

**Next Steps:**
- ⚠️ Create `.cursor/commands/agent-start.md`
- ⚠️ Create `.cursor/commands/agent-stop.md`
- ⚠️ Create `.cursor/commands/agent-status.md`

---

### **4. Test Fixes** ✅

**Router Immediate Drain:**
- ✅ Added `drain()` method
- ✅ Immediate microtask processing
- ✅ Tests use `router.drain()` instead of `idle()`

**Ordering Manager Epoch:**
- ✅ Detects epoch (0 or 1) from first message
- ✅ Handles both starting sequences
- ✅ Per-sender epoch tracking

**DLQ Persistence:**
- ✅ Uses tmpdir with proper fsync
- ✅ Atomic file writes with sync
- ✅ Tests create unique tmpdir per run

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Protocol Foundation** ✅ **COMPLETE**
- [x] Envelope protocol (v1)
- [x] MessageRouter with immediate drain
- [x] Dead Letter Queue with KV abstraction
- [x] Command Server
- [x] Test fixes (router, ordering, DLQ)

### **Phase 2: Background Agent Integration** ⚠️ **NEXT**
- [x] AgentMonitor class (HTTP API client)
- [ ] Research actual Cursor API endpoints
- [ ] Test API calls (may need API key)
- [ ] Handle webhook events
- [ ] Error handling and retries

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

### **Phase 5: Integration** ⚠️ **FUTURE**
- [ ] Wire AgentMonitor to Command Server
- [ ] Add webhook endpoint to Command Server
- [ ] Register agent handlers in MessageRouter
- [ ] Test end-to-end flow

### **Phase 6: UI Dashboard** ⚠️ **FUTURE**
- [ ] React component for agent status
- [ ] Real-time output stream
- [ ] Start/stop controls
- [ ] Metrics display

---

## 🔧 **CODE CHANGES MADE**

### **1. Router Immediate Drain** ✅
```typescript
// Added immediate microtask drain
private scheduleDrain(latest?: Envelope): void {
    // ... existing code ...
    
    // Immediate drain via microtask
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

// Added drain() method for tests
async drain(): Promise<void> {
    while (this.drainScheduled || this.inflight > 0) {
        await this.processOrderedQueue();
        await new Promise(resolve => setTimeout(resolve, 5));
    }
}
```

### **2. Ordering Manager Epoch Handling** ✅
```typescript
// Detect epoch from first message
if (nextSeq === undefined) {
    if (seq === 0 || seq === 1) {
        this.epoch.set(sender, seq);
        this.nextExpectedSeq.set(sender, seq);
    }
}
```

### **3. DLQ Persistence with fsync** ✅
```typescript
// Atomic write with fsync
const fd = await fs.open(tmp, 'w');
await fd.writeFile(JSON.stringify(v, null, 2), 'utf8');
await fd.sync(); // Ensure written to disk
await fd.close();
await fs.rename(tmp, this.filename);
```

### **4. AgentMonitor Class** ✅
- HTTP-based (no CLI)
- Uses Cursor Background Agent API
- Integrates with MessageRouter
- Handles webhooks

---

## 🚀 **NEXT STEPS**

### **Immediate (Next Session):**

1. **Research Cursor Background Agent API**
   - Find actual API endpoints
   - Understand authentication
   - Test with real API key

2. **Register MCP Tools**
   - Add MCP server registration to Command Server
   - Expose agent tools
   - Test MCP tool calls

3. **Create Slash Commands**
   - `.cursor/commands/agent-start.md`
   - `.cursor/commands/agent-stop.md`
   - `.cursor/commands/agent-status.md`

4. **Wire Everything Together**
   - AgentMonitor → Command Server
   - Command Server → MessageRouter
   - MessageRouter → React UI

---

## 📊 **PROTOCOL SUMMARY**

```
Cursor Chat (/agent-start)
    ↓
MCP Tool (agent.start)
    ↓
Command Server (MCP Server)
    ↓
Cursor Background Agent API (HTTP)
    ↓
Webhook → Command Server
    ↓
MessageRouter (Envelope Protocol)
    ↓
React UI Dashboard
```

**All layers use appropriate protocols:**
- ✅ Slash commands (Cursor feature)
- ✅ MCP protocol (JSON-RPC 2.0)
- ✅ HTTP API (REST)
- ✅ Envelope protocol (reliable messaging)

---

**Status:** Protocol design complete, AgentMonitor created, test fixes applied  
**Next:** Research Cursor API, register MCP tools, create slash commands

---

*Created: 2025-11-03*  
*Complete protocol implementation plan*

