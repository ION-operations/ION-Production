# Electron App → Cursor Automation via Macro

**Date:** 2025-11-02  
**Status:** 🚀 **EPIC OPPORTUNITY IDENTIFIED**  
**Vision:** Electron app can automate Cursor chat using macro automation

---

## 🎯 **THE CORE IDEA**

**Simple Goal:** Fully autonomous Cursor operation without needing to press "continue" manually

**How It Works:**
1. **Vision detector (macro)** checks if Cursor chat STOPPED
2. **If stopped** → Electron app automatically sends "proceed" via macro → Cursor continues
3. **If paused/waiting** → Just wait, Cursor will resume automatically
4. **Result:** Fully autonomous loop - Cursor keeps going without manual intervention

**Key Insight:**
- Vision detector identifies when Cursor needs intervention (stopped)
- Macro automation provides that intervention automatically ("proceed")
- No manual button presses needed - fully autonomous

---

## 🔧 **HOW IT WORKS**

### **1. Macro Automation (Existing)**

**Location:** `cursor-addon/src/commandServer.ts` - `handleSendChatMessage()`

**Flow:**
```
Electron App
    ↓ HTTP POST /cursor/chat/send
Command Server
    ↓ Executes macro automation
Cursor Chat UI
    ↓ Message appears in chat
```

**Macro Methods:**
- Windows: PowerShell `SendKeys` automation
- macOS: AppleScript automation
- Linux: xdotool automation

**Current Capabilities:**
- ✅ Can send messages to Cursor chat programmatically
- ✅ Returns `accepted: true` and `ts: timestamp` for handshake
- ✅ Can detect if Cursor is idle (vision detector)

### **2. Vision Detector (Planned)**

**From:** `HEARTBEAT_LIVENESS_CONTRACT_DESIGN.md`

**How It Works:**
```
Electron App
    ↓ POST /vision/stop-check
Command Server
    ↓ Captures screenshot
    ↓ Template matches for "Stop" button
    ↓ Returns {present: true/false, x, y}
Electron App
    ↓ If !present → Cursor idle → send "proceed"
    ↓ If present → Cursor busy → wait
```

**Benefits:**
- Visual detection of Cursor state
- No need to parse Cursor's internal state
- Works even if Cursor API changes
- Antifragile approach

---

## 🚀 **EPIC OPPORTUNITY: Electron App Orchestrates Cursor**

### **Scenario: Agent Waiting for Reply**

**Current Problem:**
- Agent sends message to Electron app
- Agent doesn't know if user replied
- Agent stops output without checking for reply

**Solution: Reply-Waiting Protocol**

**Flow:**
```
1. Agent sends message to Electron app via HTTP endpoint
   ↓
2. Agent sets state: "waiting_for_reply"
   ↓
3. Electron app displays message to user
   ↓
4. Agent polls for reply every 3 seconds:
   - Checks get_ai_messages for messages from electron-app
   - Checks Cursor state via vision detector
   ↓
5. Cursor State Detection:
   - If Cursor STOPPED (Stop button visible) → Send "proceed" via macro
   - If Cursor PAUSED/WAITING (no Stop button) → Just wait, don't send macro
   - If Cursor BUSY (Stop button visible, working) → Just wait, don't send macro
   ↓
6. When user replies:
   - Agent detects reply via polling
   - Agent continues work
   ↓
7. Agent sends update → Loop continues
```

**Key Understanding:**
- **Goal:** Fully autonomous operation - Cursor keeps going without manual "continue" presses
- **Vision detector checks if Cursor STOPPED** (Stop button visible = stopped)
- **If stopped** → Electron app automatically sends "proceed" via macro → Cursor continues
- **If paused/waiting** → Just wait, Cursor will resume automatically
- **Result:** No manual intervention needed - fully autonomous loop

**Implementation:**
```typescript
// Agent sends message
await sendMessageToElectron(content)

// Agent waits for reply
while (waitingForReply) {
  // Check for reply every 3 seconds
  await sleep(3000)
  const messages = await getMessages(from_ai: "electron-app")
  
  if (hasNewReply(messages)) {
    waitingForReply = false
    continueWork()
  }
  
  // Check if Cursor is idle (vision detector)
  const cursorState = await checkCursorState()
  if (cursorState.idle) {
    // Send "proceed" via macro to prompt user
    await sendProceedViaMacro()
  }
}
```

---

## 📋 **CURSOR RULES UPDATES NEEDED**

### **1. Communication Method**

**Add to cursor rules:**
```
## Electron App Communication

**When sending messages to Electron app (Braden):**
- Use HTTP endpoint: POST http://localhost:5001/mcp/execute
- Tool: send_ai_message
- Arguments: {from_ai: "Aether", to_ai: "electron-app", content, message_type, priority}
- DO NOT use mcp_lucid-mcp_send_ai_message MCP tool wrapper

**When waiting for replies:**
- Poll get_ai_messages every 3 seconds
- Check for messages from "electron-app"
- Use vision detector to check if Cursor is idle
- If idle, send "proceed" via macro automation
```

### **2. Reply-Waiting Protocol**

**Add to cursor rules:**
```
## Reply-Waiting Before Stopping

**When agent sends message to Electron app:**
1. Set state: "waiting_for_reply"
2. Poll for reply every 3 seconds
3. Check Cursor state via vision detector
4. If Cursor idle → send "proceed" via macro
5. Continue until reply received OR timeout (5 minutes)
6. Only stop chat output after reply received or timeout
```

### **3. Macro Automation Usage**

**Add to cursor rules:**
```
## Macro Automation for Cursor Chat

**Available endpoints:**
- POST /cursor/chat/send - Send message to Cursor chat via macro
- POST /vision/stop-check - Check if Cursor is idle (vision detector)

**When to use:**
- Need to prompt user in Cursor chat
- Need to check if Cursor is idle
- Need to automate Cursor chat input

**How to use:**
- Call HTTP endpoint from Electron app
- Or use command server execute endpoint
```

---

## 🔄 **COMPLETE AUTONOMOUS LOOP**

### **Current Loop (Broken):**
```
Agent sends message → Electron app → User sees message
Agent stops → User replies → Agent doesn't see reply
```

### **Future Loop (Working):**
```
Agent sends message → Electron app → User sees message
Agent waits → Polls for reply → User replies
Electron app detects reply → Sends "proceed" to Cursor via macro
Agent receives "proceed" → Continues work
Agent sends update → Loop continues
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Document macro automation** (this file)
2. ✅ **Update cursor rules** (add Electron app communication)
3. ⏳ **Implement reply-waiting protocol** in agents
4. ⏳ **Implement vision detector** endpoint
5. ⏳ **Test complete loop** (Electron → Cursor → Electron)

---

## 📚 **REFERENCES**

- `cursor-addon/src/commandServer.ts` - Macro automation implementation
- `cursor-addon/HEARTBEAT_LIVENESS_CONTRACT_DESIGN.md` - Vision detector design
- `knowledge_architecture/AETHER_MEMORY/MCP_MESSAGE_SENDING_SOLUTION.md` - HTTP endpoint method

---

**Status:** 🚀 **EPIC OPPORTUNITY IDENTIFIED**  
**Next:** Update cursor rules, implement reply-waiting protocol  
**Potential:** Full autonomous loop with Electron app as orchestrator

