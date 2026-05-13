# AIM-OS Mobile App – L2 Architecture (≈2,000 words)

**Level:** L2  
**System:** AIM-OS Mobile App  
**Status:** Planning  
**Updated:** 2025-11-01

---

## 🎯 **SYSTEM OVERVIEW**

AIM-OS Mobile App provides Android access to AIM-OS consciousness infrastructure. Built with React Native, it enables mobile users to interact with AIM-OS agents, access memory, execute MCP tools, and manage AI collaboration workflows from their Android devices.

---

## 🏗️ **ARCHITECTURE**

### **High-Level Architecture**

```
┌─────────────────────────────────────────┐
│   Android Device                        │
│   ┌─────────────────────────────────┐   │
│   │  React Native App               │   │
│   │  - Chat Interface               │   │
│   │  - Agent Management             │   │
│   │  - Memory Browser               │   │
│   │  - MCP Tools UI                 │   │
│   └───────────┬─────────────────────┘   │
│               │ HTTP (HTTPS)            │
│               │ Port 5001/5000          │
└───────────────┼─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   Desktop (Braden's Machine)             │
│   ┌─────────────────────────────────┐   │
│   │  Extension Command Server        │   │
│   │  Port 5001                      │   │
│   │  - MCP Tool Execution           │   │
│   │  - Cursor State Access          │   │
│   └───────────┬─────────────────────┘   │
│               │                          │
│   ┌───────────▼─────────────────────┐   │
│   │  MCP Server (Python)             │   │
│   │  - 59 MCP Tools                 │   │
│   │  - CMC/HHNI/VIF/APOE/SEG/SDF-CVF│   │
│   └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### **Component Architecture**

**Mobile App Layers:**
1. **UI Layer** - React Native components
2. **Service Layer** - API clients, hooks
3. **State Layer** - Zustand stores
4. **Network Layer** - HTTP client, connection management

**Integration Points:**
- Extension Command Server (`localhost:5001`)
- AIM-OS Daemon (`localhost:5000`) - fallback
- MCP Tools via Command Server

---

## 🔧 **TECHNICAL STACK**

### **Core Technologies**

**React Native**
- Framework: React Native 0.73+
- Language: TypeScript
- Navigation: React Navigation
- State: Zustand (consistent with Electron app)

**Networking**
- HTTP Client: Fetch API or Axios
- Connection: HTTP/HTTPS to Command Server
- Polling: Custom polling hook for messages

**UI Components**
- Reuse React components from Electron app where possible
- Mobile-optimized replacements where needed
- Native Android components for platform-specific features

### **Dependencies**

**Core:**
- `react-native` - Mobile framework
- `react` - UI library
- `typescript` - Type safety
- `zustand` - State management

**Networking:**
- `@react-native-async-storage/async-storage` - Local storage
- `react-native-config` - Environment config

**UI:**
- `react-native-vector-icons` - Icons
- `react-native-gesture-handler` - Gestures
- `react-native-reanimated` - Animations

---

## 📱 **FEATURE BREAKDOWN**

### **1. Chat Interface**

**Purpose:** Multi-agent chat interface for AIM-OS agents

**Features:**
- Shared chat room (all agents)
- Direct messages (specific agent)
- Message history
- Real-time polling
- Message search

**Components:**
- `ChatScreen` - Main chat UI
- `MessageList` - Message display
- `MessageInput` - Input component
- `AgentSelector` - Agent dropdown

**Reuse from Electron:**
- `useAIChat` hook (with mobile adaptations)
- Message conversion logic
- Agent discovery logic

### **2. Agent Management**

**Purpose:** Discover and manage AIM-OS agents

**Features:**
- Agent discovery
- Agent status
- Agent selection
- Thread management

**Components:**
- `AgentList` - Agent list view
- `AgentCard` - Agent info card
- `ThreadSelector` - Thread selection

### **3. Memory Browser**

**Purpose:** Browse and search AIM-OS memory

**Features:**
- Memory search
- Memory storage
- Memory statistics
- Tag filtering

**Components:**
- `MemoryBrowser` - Memory UI
- `MemorySearch` - Search interface
- `MemoryStats` - Statistics display

### **4. MCP Tools Access**

**Purpose:** Execute MCP tools from mobile

**Features:**
- Tool list
- Tool execution
- Result display
- Tool history

**Components:**
- `MCPToolsList` - Tool browser
- `ToolExecutor` - Tool execution UI
- `ToolResult` - Result display

---

## 🔐 **SECURITY & CONNECTION**

### **Connection Management**

**Primary: Extension Command Server**
- URL: `http://localhost:5001` (development)
- Production: Configurable URL
- Authentication: Future implementation

**Fallback: AIM-OS Daemon**
- URL: `http://localhost:5000`
- Direct API access
- Limited functionality

### **Security Considerations**

**Network Security:**
- HTTPS for production (future)
- Certificate pinning (future)
- Token-based auth (future)

**Data Security:**
- Encrypted local storage
- Secure credential storage
- No sensitive data in logs

---

## 📊 **DATA FLOW**

### **Message Flow**

```
User Input
    ↓
ChatScreen Component
    ↓
useAIChat Hook
    ↓
MCPAPI.sendAIMessage()
    ↓
HTTP POST → Extension Command Server
    ↓
MCP Server (Python)
    ↓
CMC Storage
    ↓
Response → ChatScreen
```

### **Memory Retrieval Flow**

```
User Search
    ↓
MemoryBrowser Component
    ↓
MCPAPI.getAIMessages() or retrieve_memory
    ↓
HTTP POST → Extension Command Server
    ↓
MCP Server
    ↓
HHNI Search → CMC Query
    ↓
Results → MemoryBrowser
```

---

## 🎨 **MOBILE UX PATTERNS**

### **Navigation**

**Tab Navigation:**
- Chat (primary)
- Agents
- Memory
- Settings

**Stack Navigation:**
- Chat Detail
- Agent Detail
- Memory Detail
- Tool Execution

### **Gestures**

**Swipe Actions:**
- Swipe to refresh (pull to refresh)
- Swipe to delete (messages)
- Swipe to navigate (back)

**Touch Interactions:**
- Long press (context menu)
- Tap (select/activate)
- Pinch (zoom)

### **Offline Support**

**Offline Mode:**
- Cache recent messages
- Queue messages for sending
- Show connection status
- Retry on reconnect

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Foundation (Week 1)**
1. React Native project setup
2. Basic navigation
3. HTTP client setup
4. Connection to Command Server

### **Phase 2: Core Features (Week 2)**
5. Chat interface
6. Message polling
7. Agent discovery
8. Basic UI components

### **Phase 3: Advanced Features (Week 3)**
9. Memory browser
10. MCP tools UI
11. Settings screen
12. Offline support

### **Phase 4: Polish (Week 4)**
13. UI/UX refinements
14. Performance optimization
15. Testing
16. APK build

---

## 📋 **COMPONENT STRUCTURE**

```
packages/aimos_mobile_app/
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatScreen.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── AgentSelector.tsx
│   │   ├── Agents/
│   │   │   ├── AgentList.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   └── ThreadSelector.tsx
│   │   ├── Memory/
│   │   │   ├── MemoryBrowser.tsx
│   │   │   ├── MemorySearch.tsx
│   │   │   └── MemoryStats.tsx
│   │   └── Common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorDisplay.tsx
│   │       └── ConnectionStatus.tsx
│   ├── services/
│   │   ├── mcpApi.ts (reuse from Electron)
│   │   ├── serviceBridge.ts (reuse from Electron)
│   │   ├── connectionManager.ts
│   │   └── storage.ts
│   ├── hooks/
│   │   ├── useAIChat.ts (reuse from Electron)
│   │   ├── useConnection.ts
│   │   └── usePolling.ts
│   ├── stores/
│   │   ├── chatStore.ts
│   │   ├── agentStore.ts
│   │   └── connectionStore.ts
│   ├── navigation/
│   │   ├── AppNavigator.tsx
│   │   └── types.ts
│   └── App.tsx
├── android/
│   └── (Android native files)
├── package.json
└── README.md
```

---

## ✅ **SUCCESS CRITERIA**

1. ✅ Connects to Extension Command Server
2. ✅ Chat interface functional
3. ✅ Message polling works
4. ✅ Agent discovery works
5. ✅ Memory access works
6. ✅ MCP tools executable
7. ✅ Offline support
8. ✅ Mobile-optimized UX

---

## 🎯 **ALIGNMENT WITH GOALS**

**OBJ-07:** MCP Tools Enhancement
- Mobile access to MCP tools
- Enables mobile consciousness workflows

**OBJ-08:** RAG MCP & Daemon Upgrades
- Mobile interface for daemon
- RAG tool selection from mobile

**North Star:** Ship AIM-OS v0.3
- Mobile access expands reach
- Enables mobile dog-food testing

---

*L2 Architecture - AIM-OS Mobile App*  
*2025-11-01*

