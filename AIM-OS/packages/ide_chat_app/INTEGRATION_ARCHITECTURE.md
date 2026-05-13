# Cursor UI Integration Architecture

**Created:** 2025-10-30  
**Agent:** Lexicon  
**Status:** Phase 1 Implementation

---

## 🎯 **Overview**

This document describes the integration architecture for the Cursor UI add-on, connecting the React/TypeScript frontend to all AIM-OS backend systems.

---

## 🏗️ **Architecture Layers**

### **Layer 1: Frontend UI (React/TypeScript)**
- **Location:** `packages/ide_chat_app/src/`
- **Framework:** React 18 + TypeScript + Vite + Tailwind CSS
- **Components:** Memory Browser, Consciousness Visualization, System Dashboard, etc.

### **Layer 2: Service Layer (TypeScript)**
- **Location:** `packages/ide_chat_app/src/services/`
- **Services:**
  - `AIMOSService.ts` - Core AIM-OS integration (CMC, HHNI, VIF, APOE, SEG)
  - `VoiceService.ts` - TTS/SST voice I/O
  - `HttpLucidDaemonService.ts` - Lucid Orchestrator daemon
  - `RealtimeCollaborationService.ts` - Real-time collaboration
  - `AnalyticsService.ts` - Analytics and metrics

### **Layer 3: Backend Services (Python)**
- **AIM-OS MCP Server:** `lucid_mcp_server.py` (port 8000)
- **Lucid Daemon:** HTTP API (port 5000)
- **RAG MCP Proxy:** Python service (port 8001)
- **Automation Engine:** Python service (port 8000/automation)

---

## 🔌 **Integration Points**

### **1. Core AIM-OS Systems (Phase 1)**

#### **CMC (Context Memory Core)**
- **Endpoint:** `POST /mcp/store_memory`, `POST /mcp/retrieve_memory`, `GET /mcp/get_memory_stats`
- **Service Method:** `aimosService.storeMemory()`, `aimosService.retrieveMemory()`, `aimosService.getMemoryStats()`
- **UI Component:** `MemoryBrowser.tsx`, `MemoryBrowserEnhanced.tsx`

#### **HHNI (Hierarchical Hypergraph Neural Index)**
- **Endpoint:** `POST /mcp/retrieve_memory` (uses HHNI internally)
- **Service Method:** `aimosService.searchContext()`
- **UI Component:** `ContextExplorer.tsx`, `SearchBar.tsx`

#### **VIF (Verifiable Intelligence Framework)**
- **Endpoint:** `POST /mcp/track_confidence`
- **Service Method:** `aimosService.trackConfidence()`, `aimosService.getConfidenceHistory()`
- **UI Component:** `ConsciousnessVisualization.tsx`, `ToolQualityDashboard.tsx`

#### **APOE (AI-Powered Orchestration Engine)**
- **Endpoint:** `POST /mcp/create_plan`
- **Service Method:** `aimosService.createPlan()`
- **UI Component:** `AIMOSOrchestration.tsx`, `WorkflowManager.tsx`

#### **SEG (Shared Evidence Graph)**
- **Endpoint:** `POST /mcp/synthesize_knowledge`
- **Service Method:** `aimosService.synthesizeKnowledge()`
- **UI Component:** `LucidGraphVisualization.tsx`, `SystemDashboard.tsx`

---

### **2. Voice I/O (TTS/SST)**

#### **Text-to-Speech (TTS)**
- **Technology:** Web Speech Synthesis API (browser-native)
- **Service Method:** `aimosService.textToSpeech()`, `voiceService.speak()`
- **UI Component:** Voice controls in chat interface, notification system

#### **Speech-to-Text (SST)**
- **Technology:** Web Speech Recognition API (browser-native)
- **Service Method:** `aimosService.speechToText()`, `voiceService.startRecording()`, `voiceService.stopRecording()`
- **UI Component:** Microphone button in chat, voice command interface

**Features:**
- Real-time transcription
- Confidence scores
- Audio hash for audit trail
- Timeline logging

---

### **3. RAG MCP Tools Integration**

#### **Intelligent Tool Selection**
- **Endpoint:** `POST http://localhost:8001/select_tools`
- **Service Method:** `aimosService.selectTools()`
- **Backend:** `packages/mcp_rag_proxy/rag_proxy.py`
- **Features:**
  - Semantic tool selection using sentence-transformers + FAISS
  - Consciousness-aware weighting
  - 80% context reduction goal
  - <100ms response time target

**UI Integration:**
- Tool selection panel
- Dynamic tool filtering
- Relevance visualization

---

### **4. AIM-OS Daemon Integration**

#### **Real-time Updates**
- **Endpoint:** `GET http://localhost:5000/api/health`
- **Service Method:** `aimosService.getDaemonStatus()`, `httpLucidDaemonService`
- **Backend:** Lucid Orchestrator daemon
- **Features:**
  - Spec blocks
  - Blueprint slices
  - Timeline summaries
  - Change proposals

**UI Integration:**
- `LucidOrchestratorPanel.tsx`
- Real-time status updates
- Spec/Blueprint/Timeline panes

---

### **5. Automation Integration**

#### **Task Management**
- **Endpoints:**
  - `POST /automation/tasks` - Create task
  - `POST /automation/tasks/{id}/execute` - Execute task
  - `GET /automation/tasks/{id}` - Get task status
  - `GET /automation/tasks` - List all tasks
- **Service Method:** `aimosService.createAutomationTask()`, `aimosService.executeAutomationTask()`, etc.
- **Features:**
  - Task creation and execution
  - Status tracking
  - Error handling
  - Result storage

**UI Integration:**
- Automation panel
- Task list and status
- Execution controls

---

## 📡 **Connection Flow**

```
┌─────────────────────────────────────────────────────────┐
│  Cursor UI (React/TypeScript)                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Components (MemoryBrowser, ConsciousnessViz)   │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Service Layer (AIMOSService, VoiceService)     │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                    ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│  Backend Services                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ MCP Server  │  │   Daemon     │  │ RAG MCP      │  │
│  │ (port 8000) │  │ (port 5000)  │  │ (port 8001)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                  ↓                  ↓          │
│  ┌─────────────────────────────────────────────────┐  │
│  │  AIM-OS Systems (CMC, HHNI, VIF, APOE, SEG)    │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 **UI Component Integration**

### **Phase 1 Components**

1. **MemoryBrowser** → `aimosService.retrieveMemory()`, `aimosService.getMemoryStats()`
2. **ConsciousnessVisualization** → `aimosService.trackConfidence()`, `aimosService.getConfidenceHistory()`
3. **SystemDashboard** → `aimosService.getSystemStatus()`
4. **AIMOSOrchestration** → `aimosService.createPlan()`, `aimosService.synthesizeKnowledge()`
5. **ChatInterface** → `voiceService.speak()`, `voiceService.startRecording()`

### **Voice-Enabled Components**

- **Chat Interface:** Microphone button for SST, speaker icon for TTS
- **Notifications:** TTS for important alerts
- **Status Updates:** Voice announcements for system changes
- **Command Interface:** Voice commands for automation

---

## 🔄 **Real-time Updates**

### **WebSocket Connections (Future)**
- Daemon → UI: Spec changes, blueprint updates
- Automation → UI: Task status updates
- VIF → UI: Confidence alerts

### **Polling (Current)**
- System status: Every 5 seconds
- Memory stats: On demand
- Task status: On demand

---

## 🧪 **Testing Strategy**

### **Unit Tests**
- Service layer methods
- Error handling
- Connection fallbacks

### **Integration Tests**
- End-to-end API calls
- Voice I/O functionality
- Real-time updates

### **E2E Tests**
- Full user workflows
- Voice commands
- Automation execution

---

## 📊 **Status Monitoring**

### **System Status Dashboard**
Shows connection status for:
- ✅ CMC (memory storage)
- ✅ HHNI (semantic search)
- ✅ VIF (confidence tracking)
- ✅ APOE (plan execution)
- ✅ SEG (knowledge synthesis)
- ✅ Daemon (real-time updates)
- ✅ RAG MCP (tool selection)
- ✅ Voice (TTS/SST)

---

## 🚀 **Next Steps**

1. **Connect UI Components** - Update existing components to use `aimosService`
2. **Build Voice UI** - Add microphone/speaker controls
3. **RAG Tool Selection UI** - Visualize tool selection process
4. **Automation Panel** - Create automation task management UI
5. **Real-time Dashboard** - System status with live updates
6. **Testing** - Comprehensive test suite

---

**Status:** Architecture designed, service layer implemented  
**Ready for:** UI component integration  
**Agent:** Lexicon 💙

