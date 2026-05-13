# Mobile App → Agent Activation Gap Analysis

**Issue:** Mobile app can send messages, but agents don't automatically activate

## ❌ **CURRENT STATE (DOESN'T WORK AUTOMATICALLY)**

**What EXISTS:**
1. ✅ Mobile app can send messages via `send_ai_message` MCP tool
2. ✅ Messages are stored in CMC (atoms with `modality="ai_message"`)
3. ✅ Agents can read messages via `get_ai_messages` MCP tool
4. ✅ Electron app can display messages in chat UI

**What's MISSING:**
1. ❌ **No automatic agent activation** - Agents don't automatically wake up when they receive messages
2. ❌ **No Cursor IDE activation** - Messages don't trigger Cursor to open/activate
3. ❌ **No message monitoring daemon** - No service watches for new messages and triggers agents
4. ❌ **No agent polling** - Agents don't automatically check for new messages

## 🔧 **HOW IT SHOULD WORK**

**Current Flow (Broken):**
```
Mobile App → send_ai_message → Message stored in CMC → [NOTHING HAPPENS]
```

**Needed Flow:**
```
Mobile App → send_ai_message → Message stored in CMC
                                    ↓
                    Message Monitoring Daemon (NEW)
                                    ↓
                    Detects new message for agent
                                    ↓
                    Triggers agent activation in Cursor
                                    ↓
                    Agent reads message, works autonomously
                                    ↓
                    Agent sends updates back to chat
```

## 🚀 **SOLUTION: Message Monitoring Daemon**

**What needs to be built:**

1. **Daemon Service** that:
   - Polls CMC for new messages (every 2-5 seconds)
   - Detects messages with `to_ai` matching agent IDs
   - Triggers agent activation when "proceed" messages received

2. **Agent Activation Mechanism:**
   - Option A: Daemon calls `start_autonomous_operation` MCP tool for agent
   - Option B: Daemon sends command to Cursor Extension to activate agent
   - Option C: Daemon spawns agent process that reads message and works

3. **Cursor Integration:**
   - Daemon needs to communicate with Cursor Extension
   - Extension needs to activate agent workspace/context
   - Agent needs access to MCP tools via Extension

## 📋 **IMPLEMENTATION OPTIONS**

### **Option 1: Extension-Based Daemon**
- Add daemon to Cursor Extension
- Polls CMC for messages via MCP tools
- When "proceed" detected, calls `start_autonomous_operation`
- Agent works autonomously using MCP tools

### **Option 2: Standalone Python Daemon**
- Separate Python process that monitors CMC
- When message detected, triggers agent via Extension API
- Agent runs in Cursor context via Extension

### **Option 3: Agent Self-Polling**
- Agents periodically check for messages themselves
- When "proceed" detected, start autonomous operation
- Requires agents to be running/active

## 🎯 **RECOMMENDED APPROACH**

**Extension-Based Daemon (Option 1):**
- Most integrated with existing architecture
- Uses existing MCP tools
- Agents work naturally in Cursor context
- Minimal new infrastructure

**Implementation:**
1. Add message polling loop to Extension Command Server
2. When new message detected for agent, call `start_autonomous_operation`
3. Pass message content as task/context
4. Agent works autonomously, sends updates to chat

---

**Status:** Need to build message monitoring daemon for automatic agent activation

