# Bulletproof Messaging - Command Server Integration

**Date:** 2025-11-03  
**Status:** Enhancement Plan  
**Purpose:** Add envelope protocol support to Command Server

---

## 🎯 **ENHANCEMENT OVERVIEW**

Add envelope protocol support to Command Server to enable bulletproof messaging between Electron app and Extension.

---

## 📋 **IMPLEMENTATION PLAN**

### **1. Add Envelope Endpoint**

**New Endpoint:** `POST /mcp/execute/envelope`

**Purpose:** Accept envelope protocol messages directly

**Request Format:**
```json
{
  "v": 1,
  "id": "uuid",
  "seq": 1,
  "ts": 1234567890,
  "dir": "electron->ext",
  "kind": "request",
  "topic": "mcp.callTool",
  "payload": {
    "tool": "store_memory",
    "arguments": { ... }
  }
}
```

**Response Format:**
```json
{
  "v": 1,
  "id": "uuid",
  "replyTo": "request-id",
  "ts": 1234567890,
  "dir": "ext->electron",
  "kind": "response",
  "topic": "mcp.callTool",
  "ok": true,
  "payload": {
    "success": true,
    "result": { ... }
  }
}
```

---

### **2. Enhance Existing Endpoint**

**Current Endpoint:** `POST /mcp/execute`

**Enhancement:** Accept optional envelope format

**Request (Legacy):**
```json
{
  "tool": "store_memory",
  "arguments": { ... }
}
```

**Request (Envelope):**
```json
{
  "envelope": true,
  "v": 1,
  "id": "uuid",
  ...
}
```

**Response (Legacy):**
```json
{
  "success": true,
  "result": { ... }
}
```

**Response (Envelope):**
```json
{
  "v": 1,
  "kind": "response",
  ...
}
```

---

### **3. Integration Points**

**A. Command Server Handler:**
```typescript
private async handleMCPExecute(request: any): Promise<any> {
    // Check if envelope format
    if (request.envelope || request.v === 1) {
        return await this.handleEnvelopeRequest(request);
    }
    
    // Legacy format
    return await this.handleLegacyRequest(request);
}
```

**B. Envelope Handler:**
```typescript
private async handleEnvelopeRequest(env: Envelope): Promise<Envelope> {
    // Route through MessageRouter
    const router = this.getMessageRouter();
    await router.route(env);
    
    // Wait for response
    return await this.waitForResponse(env.id);
}
```

**C. MessageRouter Integration:**
```typescript
// In CommandServer constructor
this.messageRouter = new MessageRouter(context);
this.messageRouter.registerHandler('mcp.callTool', async (env) => {
    return await this.executeMCPTool(env);
});
```

---

## 📝 **CODE CHANGES NEEDED**

### **File: `cursor-addon/src/commandServer.ts`**

**Changes:**
1. Import MessageRouter and envelope types
2. Initialize MessageRouter in constructor
3. Add `handleEnvelopeRequest` method
4. Modify `handleMCPExecute` to support envelopes
5. Add response waiting mechanism

**Estimated LOC:** +150 lines

---

## ✅ **BENEFITS**

- ✅ Electron app gets reliable messaging
- ✅ Automatic retry for failed requests
- ✅ Dead letter queue for failures
- ✅ Connection health monitoring
- ✅ Backward compatible (legacy format still works)

---

*Created: 2025-11-03*  
*Status: Enhancement Plan*  
*Priority: High*

