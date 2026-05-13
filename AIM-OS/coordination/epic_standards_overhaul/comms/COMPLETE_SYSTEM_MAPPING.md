# COMPLETE SYSTEM MAPPING - LUCID EXTENSIONS, UI, AND CURSOR INTEGRATION

**Created:** 2025-11-01  
**Agent:** Solo (Autonomous Operation)  
**Goal:** OBJ-MAP-001  
**Status:** In Progress (15%)  
**Purpose:** Comprehensive mapping of ALL systems, components, integrations, and workflows  

---

## 📋 **TABLE OF CONTENTS**

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Cursor Extension (cursor-addon)](#cursor-extension)
4. [UI Application (ide_chat_app)](#ui-application)
5. [LUCID Orchestrator](#lucid-orchestrator)
6. [MCP Integration](#mcp-integration)
7. [Build & Deployment](#build--deployment)
8. [Version Information](#version-information)
9. [Integration Points](#integration-points)
10. [Data Flows](#data-flows)
11. [Known Issues](#known-issues)
12. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🎯 **EXECUTIVE SUMMARY**

This document provides a complete mapping of:
- **Cursor Extension** (`cursor-addon/`) - VS Code/Cursor extension providing UI integration
- **UI Application** (`packages/ide_chat_app/`) - React/TypeScript frontend dashboard
- **LUCID Orchestrator** - Daemon and orchestration system
- **MCP Integration** - Model Context Protocol server connections
- **Build System** - How everything compiles and packages

**Current Status:**
- Extension Version: **1.2.0**
- UI Version: **1.0.0**
- Extension Status: **Functional** (with known UI loading issues)
- UI Status: **Built** (React app with 6 tabs)
- MCP Status: **Integrated** (via MCP client)

---

## 🏗️ **SYSTEM ARCHITECTURE OVERVIEW**

```
┌─────────────────────────────────────────────────────────┐
│                    CURSOR / VS CODE                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cursor Extension (cursor-addon/)                 │  │
│  │  - TypeScript Extension                           │  │
│  │  - Webview Providers                              │  │
│  │  - MCP Client                                     │  │
│  │  - Commands & Menus                               │  │
│  └──────────────────────────────────────────────────┘  │
│                    ↓ Webview Protocol                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  React UI (packages/ide_chat_app/)                │  │
│  │  - MainDashboard (6 tabs)                         │  │
│  │  - Components (40+ React components)              │  │
│  │  - Services (AIMOSService, VoiceService, etc.)    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                    ↓ HTTP / WebSocket / MCP
┌─────────────────────────────────────────────────────────┐
│              BACKEND SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ MCP Server  │  │   Daemon     │  │ RAG System   │  │
│  │ (port 8000) │  │ (port 5000)  │  │ (port 8001)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                  ↓                  ↓          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AIM-OS Core Systems (CMC, HHNI, VIF, APOE, SEG) │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 **CURSOR EXTENSION (cursor-addon/)**

### **Location:** `cursor-addon/`

### **Purpose:** VS Code/Cursor extension providing AIM-OS UI integration

### **Structure:**
```
cursor-addon/
├── src/
│   ├── extension.ts              # Main entry point
│   ├── webviewProvider.ts        # Webview panel provider
│   ├── lucidDashboardProvider.ts # Lucid dashboard provider
│   ├── mcp/
│   │   └── mcpClient.ts          # MCP client implementation
│   ├── memory/
│   │   └── memoryManager.ts      # Memory management
│   ├── crossModel/
│   │   └── crossModelManager.ts  # Cross-model consciousness
│   └── models/
│       └── modelSelector.ts      # Model selection
├── dist/                          # Built React UI (copied from ide_chat_app)
├── out/                           # Compiled TypeScript
├── resources/
│   └── icon.png                   # Extension icon
├── scripts/
│   ├── build-extension.js         # Build script
│   ├── install-to-cursor.ps1     # Windows install
│   └── install-to-cursor.sh      # Unix install
├── package.json                   # Extension manifest
└── tsconfig.json                  # TypeScript config
```

### **Key Components:**

#### **1. Extension Entry Point (`extension.ts`)**
- **Purpose:** Activates extension, registers providers, commands
- **Key Functions:**
  - `activate()` - Main activation function
  - Registers webview providers
  - Registers commands (showDashboard, toggleCrossModel, etc.)
  - Initializes managers (CrossModel, Memory, ModelSelector)

#### **2. Webview Providers:**

**AIMOSWebviewProvider (`webviewProvider.ts`)**
- **Purpose:** Creates webview panels for React UI
- **Features:**
  - Loads `dist/index.html` (React UI)
  - Converts asset paths to webview URIs
  - Handles MCP tool calls from React UI
  - Fallback HTML if React UI not found

**LucidOrchestratorDashboardProvider (`lucidDashboardProvider.ts`)**
- **Purpose:** Provides dashboard in sidebar/panel
- **Features:**
  - Movable panels (left, right, bottom, panel, floating)
  - Model selection (Gemini, Cerebras, Auto)
  - Daemon connection management
  - Agent management
  - MCP tools integration
  - Extensive diagnostic logging

#### **3. MCP Client (`mcp/mcpClient.ts`)**
- **Purpose:** Connects to MCP server for tool calls
- **Features:**
  - JSON-RPC 2.0 protocol
  - Tool listing and execution
  - Memory operations (store, retrieve, stats)
  - Plan creation
  - Confidence tracking
  - Knowledge synthesis

### **Commands Registered:**
1. `aimos.showDashboard` - Show main dashboard
2. `aimos.debugDashboard` - Debug dashboard
3. `aimos.toggleCrossModel` - Toggle cross-model consciousness
4. `aimos.showMemoryStats` - Show memory statistics
5. `aimos.showModelSelector` - Show model selector
6. `aimos.storeMemory` - Store selected text as memory
7. `aimos.retrieveMemory` - Retrieve memories
8. `aimos.createPlan` - Create execution plan
9. `aimos.trackConfidence` - Track confidence

### **Views Registered:**
1. `aimosDashboard` - Activity bar view (left sidebar)
2. `lucidOrchestratorDashboard` - Panel view (bottom panel)

### **Configuration:**
- `aimos.mcpServerPath` - Path to MCP server executable
- `aimos.crossModelEnabled` - Enable cross-model features
- `aimos.autoModelSelection` - Auto-select models
- `aimos.memoryAutoStore` - Auto-store context
- `aimos.confidenceTracking` - Enable confidence tracking

### **Build Process:**
1. Build React UI (`packages/ide_chat_app`)
2. Copy `dist/` to `cursor-addon/dist/`
3. Compile TypeScript (`tsc`)
4. Package as `.vsix` file

---

## 🎨 **UI APPLICATION (packages/ide_chat_app/)**

### **Location:** `packages/ide_chat_app/`

### **Purpose:** React/TypeScript frontend dashboard for AIM-OS

### **Structure:**
```
packages/ide_chat_app/
├── src/
│   ├── main.tsx                    # Entry point (always renders MainDashboard)
│   ├── App.tsx                     # App component (conditional rendering)
│   ├── components/
│   │   ├── MainDashboard.tsx      # Main dashboard with 6 tabs
│   │   ├── AgentManagementDashboard/
│   │   │   ├── AgentManagementDashboard.tsx
│   │   │   ├── ChatInterfaceTab.tsx
│   │   │   ├── PromptChainsTab.tsx
│   │   │   ├── MCPToolsTab.tsx
│   │   │   └── TimelineTab.tsx
│   │   ├── LandingPage.tsx
│   │   ├── NLTagPanel.tsx
│   │   └── [40+ other components]
│   ├── services/
│   │   ├── AIMOSService.ts         # Core AIM-OS integration
│   │   ├── VoiceService.ts         # TTS/SST
│   │   ├── HttpLucidDaemonService.ts
│   │   └── [other services]
│   ├── contexts/
│   │   ├── AppContext.tsx
│   │   ├── CodingAgentContext.tsx
│   │   └── PlanningAgentContext.tsx
│   ├── hooks/
│   │   ├── useAgents.ts
│   │   ├── useAI.ts
│   │   ├── useAIChat.ts
│   │   ├── useDaemon.ts
│   │   ├── useMemory.ts
│   │   └── useValidation.ts
│   └── lib/
│       ├── aimos-client.ts
│       ├── mcp-integration.ts
│       └── [other libs]
├── dist/                            # Built output (copied to extension)
│   ├── index.html
│   └── assets/
│       ├── main-*.js
│       └── main-*.css
└── package.json
```

### **Main Dashboard Tabs:**

1. **Agents Tab** (`AgentManagementDashboard`)
   - Agent cards
   - Agent status
   - Agent configuration

2. **Chat Tab** (`ChatInterfaceTab`)
   - Chat interface
   - Agent selection
   - Message history

3. **Chains Tab** (`PromptChainsTab`)
   - Prompt chain management
   - Chain execution

4. **Tools Tab** (`MCPToolsTab`)
   - MCP tool execution
   - Tool status
   - Tool configuration

5. **Timeline Tab** (`TimelineTab`)
   - Timeline visualization
   - Event history

6. **NL Tags Tab** (`NLTagPanel`)
   - Natural language tag management
   - Tag validation

### **Key Services:**

#### **AIMOSService (`services/AIMOSService.ts`)**
- **Purpose:** Core integration with AIM-OS systems
- **Features:**
  - Memory operations (store, retrieve, stats)
  - Context search (HHNI)
  - Confidence tracking (VIF)
  - Plan creation (APOE)
  - Knowledge synthesis (SEG)
  - System status
  - Automation tasks
  - NL tags

#### **VoiceService (`services/VoiceService.ts`)**
- **Purpose:** Voice I/O (TTS/SST)
- **Features:**
  - Text-to-Speech (Web Speech Synthesis API)
  - Speech-to-Text (Web Speech Recognition API)
  - Audio hash for audit trail
  - Timeline logging

#### **HttpLucidDaemonService (`services/HttpLucidDaemonService.ts`)**
- **Purpose:** Connection to Lucid Daemon
- **Features:**
  - Health checks
  - Status updates
  - Real-time connections

### **Build Process:**
1. Vite build (`npm run build`)
2. Outputs to `dist/`
3. Copied to `cursor-addon/dist/` by build script

---

## 🔧 **LUCID ORCHESTRATOR**

### **Location:** `packages/lucid_orchestrator/`

### **Purpose:** "Visor to the organism" - Code intelligence via inline folds

### **Components:**

1. **Extension** (`extension/`)
   - Gutter icons ([SPEC], [BLUEPRINT], [TIMELINE])
   - Inline fold rendering
   - Monaco editor integration

2. **Daemon** (`daemon/`)
   - WebSocket API
   - JSON-RPC 2.0 protocol
   - API stubs for Spec/Blueprint/Timeline

### **Features:**
- SPEC Folds - View specifications
- BLUEPRINT Folds - View relationship graphs
- TIMELINE Folds - Monitor runtime performance
- Change Proposals - Governance workflow

---

## 🔌 **MCP INTEGRATION**

### **MCP Server:**
- **Location:** `mcp-aether/` (assumed)
- **Protocol:** JSON-RPC 2.0
- **Port:** 8000 (assumed)

### **MCP Client (Extension):**
- **Location:** `cursor-addon/src/mcp/mcpClient.ts`
- **Purpose:** Connects to MCP server for tool calls
- **Features:**
  - Tool listing
  - Tool execution
  - Memory operations
  - Plan creation
  - Confidence tracking

### **MCP Tools Available:**
- `store_memory` - Store memories
- `retrieve_memory` - Retrieve memories
- `get_memory_stats` - Get memory statistics
- `create_plan` - Create execution plans
- `track_confidence` - Track confidence
- `synthesize_knowledge` - Synthesize knowledge

### **MCP Configuration:**
- Configured in `~/.cursor/mcp.json`
- Extension reads from workspace config

---

## 🚀 **BUILD & DEPLOYMENT**

### **Build Script (`cursor-addon/scripts/build-extension.js`)**

**Process:**
1. **Build React UI:**
   ```bash
   cd packages/ide_chat_app
   npm run build
   ```

2. **Copy dist to extension:**
   ```bash
   cp -r packages/ide_chat_app/dist cursor-addon/dist/
   ```

3. **Compile TypeScript:**
   ```bash
   cd cursor-addon
   npm run compile
   ```

4. **Package Extension:**
   ```bash
   vsce package --out aimos-cursor-addon.vsix
   ```

### **Installation:**

**Windows:**
```powershell
cd cursor-addon
npm run install:windows
```

**Linux/Mac:**
```bash
cd cursor-addon
npm run install:unix
```

**Manual:**
```bash
code --install-extension aimos-cursor-addon.vsix --force
```

### **Dependencies:**
- Node.js 16+
- TypeScript 4.9+
- Vite 5.2+
- React 18.3+
- VS Code Extension API 1.74+

---

## 📊 **VERSION INFORMATION**

### **Extension Version:**
- **Current:** 1.2.0 (in `cursor-addon/package.json`)
- **Previous:** 1.1.0 (mentioned in message board)
- **Initial:** 1.0.0

### **UI Version:**
- **Current:** 1.0.0 (in `packages/ide_chat_app/package.json`)

### **Version Mismatch Issues:**
- Test file has `version="1.1.0"` in `daemon_rag_system/ah_protocol/test_audit_memory_continuity.py` line 175
- Should be updated to match current version

---

## 🔗 **INTEGRATION POINTS**

### **1. Extension → UI:**
- **Method:** Webview Protocol
- **File Loading:** `dist/index.html` loaded into webview
- **Asset Paths:** Converted to webview URIs (`vscode-webview://`)
- **Message Passing:** `webview.postMessage()` / `webview.onDidReceiveMessage()`

### **2. UI → MCP:**
- **Method:** Extension forwards MCP calls
- **Flow:** React UI → Extension → MCP Client → MCP Server
- **Tools:** All MCP tools available via `AIMOSService`

### **3. Extension → Daemon:**
- **Method:** HTTP API
- **URL:** `http://localhost:5000`
- **Endpoints:** `/api/health`, `/api/status`, etc.

### **4. UI → AIM-OS Systems:**
- **Method:** HTTP/MCP Protocol
- **Services:** CMC, HHNI, VIF, APOE, SEG
- **Implementation:** `AIMOSService.ts`

---

## 🔄 **DATA FLOWS**

### **Memory Storage Flow:**
```
User Action (UI)
  ↓
AIMOSService.storeMemory()
  ↓
Extension MCP Client
  ↓
MCP Server (store_memory tool)
  ↓
CMC Service
  ↓
Storage (SQLite/Vector DB)
```

### **Tool Selection Flow:**
```
User Query (UI)
  ↓
AIMOSService.selectTools()
  ↓
RAG System (port 8001)
  ↓
Tool Selection Algorithm
  ↓
Return Selected Tools
  ↓
UI Display
```

### **Dashboard Loading Flow:**
```
Cursor Extension Activation
  ↓
LucidOrchestratorDashboardProvider.resolveWebviewView()
  ↓
Load dist/index.html
  ↓
Convert Asset Paths to Webview URIs
  ↓
Inject CSP & TrustedTypes
  ↓
Set Webview HTML
  ↓
React UI Renders
  ↓
MainDashboard Component
  ↓
6 Tabs Available
```

---

## 🐛 **KNOWN ISSUES**

### **Critical Issues:**

1. **UI Panel Loading Failure**
   - **Symptom:** Webview shows fallback HTML instead of React UI
   - **Cause:** Asset path conversion issues, CSP blocking, or file not found
   - **Status:** Multiple attempts, diagnostic logging added
   - **Files:** 50+ diagnostic files in `cursor-addon/`

2. **Version Inconsistency**
   - **Symptom:** Test file has `version="1.1.0"` when extension is `1.2.0`
   - **Location:** `daemon_rag_system/ah_protocol/test_audit_memory_continuity.py` line 175
   - **Status:** Needs team coordination to fix

### **Minor Issues:**

1. **MCP Connection Failures**
   - **Symptom:** MCP tools not available
   - **Cause:** MCP server not running or misconfigured
   - **Fix:** Ensure MCP server running, check `mcp.json` config

2. **Daemon Connection Failures**
   - **Symptom:** Daemon status shows disconnected
   - **Cause:** Daemon not running on port 5000
   - **Fix:** Start daemon server

---

## 🔍 **TROUBLESHOOTING GUIDE**

### **Extension Not Loading:**
1. Check `dist/` folder exists with built React UI
2. Run `npm run build` from `cursor-addon`
3. Check extension output panel for errors
4. Verify TypeScript compiled (`out/extension.js` exists)

### **Webview Shows Fallback HTML:**
1. Verify `dist/index.html` exists
2. Verify `dist/assets/*.js` files exist
3. Check Developer Console (F12 in webview) for errors
4. Check Extension Host console for diagnostic logs
5. Verify asset paths converted to webview URIs

### **MCP Tools Not Working:**
1. Ensure MCP server running
2. Check `~/.cursor/mcp.json` configuration
3. Verify MCP client initialization in extension
4. Check extension output panel for MCP errors

### **React UI Not Loading:**
1. Rebuild React UI: `cd packages/ide_chat_app && npm run build`
2. Copy dist: `cp -r packages/ide_chat_app/dist cursor-addon/dist/`
3. Rebuild extension: `cd cursor-addon && npm run build`
4. Reinstall extension

### **Diagnostic Logging:**
- Extension logs to: "AIM-OS Dashboard" output channel
- Webview logs: F12 Developer Console in webview
- Extension Host logs: View → Output → "AIM-OS Cursor Add-on"

---

## 📚 **ADDITIONAL RESOURCES**

### **Documentation Files:**
- `cursor-addon/README.md` - Extension documentation
- `cursor-addon/INSTALLATION_GUIDE.md` - Installation guide
- `cursor-addon/IMPLEMENTATION_PLAN.md` - Implementation plan
- `packages/ide_chat_app/INTEGRATION_ARCHITECTURE.md` - Integration architecture
- `packages/ide_chat_app/README_STANDALONE.md` - Standalone mode guide

### **Related Systems:**
- Daemon/RAG System: `daemon_rag_system/`
- LUCID Orchestrator: `packages/lucid_orchestrator/`
- MCP Server: `mcp-aether/` (assumed)

---

## ✅ **STATUS SUMMARY**

### **Extension:**
- ✅ Code structure complete
- ✅ Webview providers implemented
- ✅ MCP client integrated
- ✅ Commands registered
- ⚠️ UI loading issues (diagnostic logging added)

### **UI Application:**
- ✅ MainDashboard implemented
- ✅ 6 tabs functional
- ✅ Services integrated
- ✅ Components built
- ✅ Build process working

### **Integration:**
- ✅ Extension → UI: Webview protocol working
- ✅ UI → MCP: Extension forwarding implemented
- ⚠️ Daemon connection: Needs daemon running
- ⚠️ MCP connection: Needs MCP server running

---

**Status:** Documentation in progress (15% complete)  
**Next Steps:** Continue mapping integration points, add more component details, document build processes completely  

**Last Updated:** 2025-11-01 09:46 UTC  
**Maintained By:** Solo (Autonomous Operation)
