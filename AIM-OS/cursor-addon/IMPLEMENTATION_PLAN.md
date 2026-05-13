# Lucid Orchestrator Dashboard - Implementation Plan

**Created:** 2025-10-30  
**Agent:** Lexicon  
**Status:** In Progress

---

## 🎯 **COMPREHENSIVE VISION**

Based on research from `lucid-daemon.txt`, `lucid_orchestrator_specification.md`, and UI architecture docs:

### **Core Features:**

1. **Movable Panels** ✅
   - Left sidebar, Right sidebar, Bottom panel, Floating window
   - Panel position persistence
   - Drag-and-drop repositioning

2. **Gemini/Cerebras Integration** ⏳
   - Model selection UI
   - Task-specific routing
   - Performance tracking
   - Cost optimization

3. **Agent Management** ⏳
   - Start/stop Cursor agents
   - Configuration UI
   - Cross-agent communication
   - Message routing to Cursor chat

4. **Daemon Connection** ⏳
   - Real-time status
   - Health monitoring
   - Event streaming
   - Spec/Blueprint/Timeline data

5. **MCP Tools** ⏳
   - Tool execution interface
   - Status monitoring
   - RAG MCP integration
   - Performance metrics

6. **Four-Pane Interface** ⏳
   - Code Pane (Monaco editor)
   - Blueprint Pane (system structure)
   - Spec Pane (SpecBlocks)
   - Timeline Pane (temporal history)

7. **Voice I/O** ⏳
   - TTS/SST integration
   - Voice commands
   - Timeline logging

---

## 📦 **CURRENT STATUS**

### **Completed:**
- ✅ Extension manifest configured
- ✅ Webview provider created
- ✅ Lucid Dashboard provider created
- ✅ Build scripts created
- ✅ Installation scripts created
- ✅ Fallback HTML with feature preview

### **In Progress:**
- ⏳ TypeScript compilation (fixing errors)
- ⏳ React UI build
- ⏳ Service integration

### **Next Steps:**
1. Fix TypeScript compilation errors
2. Build React UI progressively
3. Connect to AIMOSService
4. Integrate daemon/MCP/agents
5. Test installation in Cursor

---

## 🚀 **QUICK START GUIDE**

### **Build Extension:**

```powershell
# From AIM-OS root directory
cd cursor-addon
npm install
npm run build
npm run package
```

### **Install to Cursor:**

```powershell
# Windows
npm run install:windows

# Or manually
code --install-extension aimos-cursor-addon.vsix --force
```

### **Open Dashboard:**

1. **Command Palette** (Ctrl+Shift+P):
   - `AIM-OS: Show Dashboard` - Full React UI
   - `AIM-OS: Show Lucid Orchestrator Dashboard` - Lucid Dashboard

2. **Activity Bar:**
   - Click 🧠 (brain) icon → Dashboard
   - Click 📊 (dashboard) icon in bottom panel → Lucid Dashboard

---

## 🏗️ **ARCHITECTURE**

```
┌─────────────────────────────────────────────────────┐
│  Cursor/VSCode Extension                            │
│  ┌─────────────────────────────────────────────┐  │
│  │  Lucid Dashboard Provider (WebviewView)     │  │
│  │  ├─ Movable panels                         │  │
│  │  ├─ Model selection                        │  │
│  │  ├─ Agent management                       │  │
│  │  ├─ Daemon connection                      │  │
│  │  └─ MCP tools                              │  │
│  └─────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────┐  │
│  │  React UI (Webview)                         │  │
│  │  ├─ Four-pane interface                    │  │
│  │  ├─ Voice I/O                              │  │
│  │  ├─ Consciousness visualization            │  │
│  │  └─ Real-time updates                     │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                    ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────┐
│  AIM-OS Backend Services                             │
│  ├─ MCP Server (port 8000)                          │
│  ├─ Daemon (port 5000)                              │
│  ├─ RAG MCP Proxy (port 8001)                       │
│  └─ Gemini/Cerebras APIs                            │
└─────────────────────────────────────────────────────┘
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

- [x] Extension manifest configured
- [x] Webview provider created
- [x] Lucid Dashboard provider created
- [x] Build scripts created
- [x] Installation scripts created
- [ ] TypeScript compilation fixed
- [ ] React UI built
- [ ] AIMOSService integration
- [ ] Daemon connection
- [ ] Model selection UI
- [ ] Agent management
- [ ] MCP tools integration
- [ ] Voice I/O controls
- [ ] Four-pane interface
- [ ] Panel persistence
- [ ] Testing and validation

---

**Status:** Foundation complete, building UI progressively  
**Next:** Fix compilation, build React UI, test installation  

