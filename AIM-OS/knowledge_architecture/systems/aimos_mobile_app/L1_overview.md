# AIM-OS Mobile App – Updated L1 Overview (≈500 words)

**Level:** L1  
**System:** AIM-OS Mobile App  
**Status:** Planning (Updated)  
**Updated:** 2025-11-01

---

## 🎯 **PURPOSE**

AIM-OS Mobile App enables Android access to multi-agent chat interface. Primary functions:
1. **Chat with agents** - Send/receive messages from AIM-OS agents
2. **Prompt agents** - Send "proceed" commands to trigger autonomous work
3. **Monitor work** - See agent responses and autonomous task execution
4. **Agent discovery** - See which agents are available

**Key Insight:** Agents execute MCP tools via Cursor Extension, not from mobile. Mobile is a chat/prompting interface, not a tool executor.

---

## 🏗️ **ARCHITECTURE**

**Mobile App (React Native)**
- React Native framework (Android first)
- Chat interface (primary feature)
- Agent management
- Message polling
- "Proceed" command sending

**Connection Layer**
- HTTP client to Extension Command Server (`localhost:5001`)
- Chat API endpoints
- Agent communication endpoints

**Agent Workflow**
```
Mobile App → Send "proceed" message → Extension Command Server
                                    ↓
                              Agent receives message
                                    ↓
                         Agent works autonomously in Cursor
                                    ↓
                         Uses MCP tools via Extension
                                    ↓
                         Sends updates back to chat
                                    ↓
                              Mobile App displays
```

---

## 🔗 **INTEGRATION POINTS**

**Extension Command Server (Port 5001)**
- `GET /health` - Health check
- `POST /mcp/execute` - For agent communication (send_ai_message)
- `GET /cursor/*` - Cursor state (future)

**Chat API**
- Send messages via `send_ai_message` MCP tool
- Receive messages via `get_ai_messages` MCP tool
- Agent discovery from messages

**Agent Communication**
- Agents receive messages via CMC
- Agents respond autonomously
- Agents use MCP tools in Cursor context
- Mobile app displays results

---

## 📱 **MOBILE UX CONSIDERATIONS**

**Primary Screen: Chat**
- Message list (all agents)
- Message input
- Agent selector (optional)
- "Proceed" quick action button

**Secondary Screens:**
- Agent list
- Settings (connection config)

**Key Features:**
- Real-time message polling
- Pull-to-refresh
- Offline message queue
- Connection status indicator

---

## 🚀 **DEPLOYMENT**

**Development**
- React Native development environment
- Metro bundler
- Android emulator/testing

**Production**
- Android APK build
- Direct APK distribution
- Network configuration for Command Server access

---

## 📊 **SUCCESS METRICS**

- Chat functionality works
- "Proceed" commands trigger agent work
- Messages display in real-time
- Connection reliability
- User satisfaction with mobile chat experience

---

*L1 Overview - AIM-OS Mobile App (Updated)*  
*2025-11-01*
