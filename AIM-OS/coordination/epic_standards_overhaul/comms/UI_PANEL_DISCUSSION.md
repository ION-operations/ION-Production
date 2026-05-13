# Cursor UI Panel - Complete Discussion & Status

**Created:** 2025-10-31  
**Purpose:** Comprehensive discussion of UI panel - all ideas, what's built, what's planned  
**Status:** Active Discussion  

---

## 🎯 **CORE PHILOSOPHY & MISSION**

### **The UI Panel is NOT just a chat interface.**
**It's the "automation cockpit" for Cursor** - the control station that automates Cursor operations, manages Cursor AI agents, and coordinates everything seamlessly.

### **Primary Mission: AUTOMATING CURSOR**

**Key Principle:** Intelligent automation of Cursor operations:
- **Manage Cursor Agents** - Start, stop, monitor, and coordinate agents (like Aether manages Lexicon, Solo, Sonnet, Atlas)
- **Automate Cursor Operations** - Change models, prompt agents to continue, manage workflows
- **Orchestrate Complex Tasks** - Coordinate multiple agents working together
- **Transparent Control** - See exactly what's happening, intervene when needed
- **Seamless Integration** - Works WITH Cursor, not against it

---

## 📊 **CURRENT STATE - WHAT'S ACTUALLY BUILT**

### **✅ Extension Foundation (Lexicon - COMPLETE)**
- ✅ Extension manifest configured (`package.json`)
- ✅ Webview provider created (`webviewProvider.ts`)
- ✅ Lucid Dashboard provider created (`lucidDashboardProvider.ts`)
- ✅ Build scripts created
- ✅ Installation scripts created
- ✅ Extension packaged (`aimos-cursor-addon.vsix` - 4.6 MB)
- ✅ Extension installed and ready for testing
- ✅ Fallback HTML with feature preview (fully functional)

### **✅ React UI Component (Lexicon - IN PROGRESS)**
- ✅ `AgentManagementDashboard.tsx` component exists
- ✅ Basic agent cards with status, model, current task
- ✅ Confidence field exists (basic display only)
- ✅ Task management interface
- ✅ Model selector (basic)
- ✅ Agent communication features (send message, broadcast)
- ✅ Auto-continue toggle
- ⏳ TypeScript compilation errors (needs fixing)
- ⏳ React UI not built yet (`dist/` folder missing or empty)

### **✅ Daemon Integration (Lexicon - COMPLETE)**
- ✅ `HttpLucidDaemonService.ts` - Full API integration
- ✅ `AIMOSService.ts` - Daemon methods added
- ✅ `useDaemon()` React hook created
- ✅ SSE support for real-time updates
- ✅ All Solo API endpoints integrated:
  - `/api/health` - Health check ✅
  - `/api/status` - Full daemon status ✅
  - `/api/requests` - Process requests (intelligent tool selection) ✅
  - `/api/tools` - Get tools list ✅
  - `/api/rag/statistics` - RAG statistics ✅
  - `/api/stream` - SSE real-time updates ✅

### **✅ Memory Browser (Lexicon - COMPLETE)**
- ✅ `MemoryBrowser.tsx` component
- ✅ `MemoryBrowserEnhanced.tsx` component
- ✅ Connected to CMC (Context Memory Core)
- ✅ Fully functional UI

### **✅ Other Components (Lexicon - EXISTS)**
- ✅ Many UI components exist (`packages/ide_chat_app/src/components/`)
- ✅ Lucid Orchestrator components (BlueprintPane, CodePane, SpecPane, TimelinePane)
- ✅ System Dashboard components
- ✅ Chat Interface components
- ⚠️ Most are not integrated with extension yet
- ⚠️ React UI not built/connected yet

---

## 🎨 **DESIGN VISION - WHAT'S PLANNED**

### **7 TABS STRUCTURE:**

**Tab 1: 🤖 Agent Management Dashboard (DEFAULT - PRIMARY TAB)**
- **Status:** Partially built (Lexicon)
- **Features:**
  - ✅ Agent cards with status, model, current task (basic)
  - ✅ Confidence display (basic - needs enhancement)
  - ✅ Task management interface
  - ✅ Model selector
  - ✅ Agent communication
  - ❌ **MISSING:** Confidence bands (A/B/C color coding)
  - ❌ **MISSING:** κ-Gate status display
  - ❌ **MISSING:** Confidence-gated automation (actions disabled when confidence low)
  - ❌ **MISSING:** Confusion indicators
  - ❌ **MISSING:** Agent assistance system (ask questions, context provision)
  - ❌ **MISSING:** Confidence metrics dashboard

**Tab 2: 💬 Chat Interface**
- **Status:** Component exists, not integrated
- **Features:**
  - Conversation with Gemini/Cerebras
  - Natural language interface
  - Context-aware responses
  - MCP tools integration

**Tab 3: 🔗 Prompt Chains**
- **Status:** Component exists, not integrated
- **Features:**
  - Visualize complex prompt chains
  - Real-time chain updates
  - Agent attribution
  - Duration tracking

**Tab 4: 🛠️ MCP Tools**
- **Status:** Component exists, not integrated
- **Features:**
  - MCP tools activity
  - Conversational format (show as AI conversations)
  - Category organization
  - Timeline integration

**Tab 5: 📅 Timeline & Calendar**
- **Status:** Component exists, not integrated
- **Features:**
  - Timeline view
  - Calendar navigation
  - Context web visualization (NOT linear chat history)
  - Evolution tracking

**Tab 6: ⚙️ Settings**
- **Status:** Not built yet
- **Features:**
  - Configuration
  - Model preferences
  - Automation rules
  - System preferences

**Tab 7: 🔧 Workflow Automation (NEW - ASSIGNED TO SCRIBE)**
- **Status:** Scribe researching & documenting
- **Features:**
  - Terminal management (detect, close, auto-cleanup)
  - Port management (detect, close, conflict resolution)
  - Resource monitoring (terminals, ports, processes)
  - Smart detection (same app, upgraded app)
  - Warning system (before closing)
  - User approval workflow

---

## 💡 **KEY IDEAS & INNOVATIONS**

### **1. Confidence-Based Safety Gates (VIF Integration)**
**Idea:** Use VIF confidence metrics and κ-gating to ensure safe automation
- **Confidence Bands:**
  - 🟢 **A-Band (≥0.90)** - High confidence, proceed safely
  - 🟡 **B-Band (0.70-0.89)** - Medium confidence, proceed with caution
  - 🔴 **C-Band (<0.70)** - Low confidence, needs assistance
- **κ-Gating:** Block automation if confidence below threshold
- **Status:** Design complete, needs implementation in AgentManagementDashboard

### **2. Agent Assistance System**
**Idea:** Agents can ask questions when confused, UI provides context to improve confidence
- **Agent Questions:** Agents can ask questions to Lucid AI (Gemini/Cerebras)
- **Lucid AI Answers:** Main Lucid AI answers questions with context
- **Context Enhancement:** UI provides context to improve confidence
- **Confidence Improvement:** Track confidence improvements after assistance
- **Status:** Design complete, needs implementation

### **3. Gemini/Cerebras as Conversational Face**
**Idea:** Gemini/Cerebras acts as the primary conversational interface that manages complexity
- **Role:** Talks to you in natural language, manages complexity behind the scenes
- **Orchestration:** Orchestrates agents (Cursor AI, daemon, MCP tools)
- **Transparency:** Shows what agents/tools are being used
- **Status:** Design complete, needs implementation

### **4. Prompt Chain Visualization**
**Idea:** Show complex prompt chains as they're built and dynamically adjusted
- **Real-time Updates:** Chains update as steps complete
- **Dynamic Adjustment:** Steps can be added/removed
- **Agent Attribution:** Shows which agent/system executed each step
- **Status:** Component exists (`AIMOSOrchestration.tsx`), needs integration

### **5. MCP Tools as AI Conversations**
**Idea:** Display MCP tools data as AI conversations, not raw tool calls
- **Conversational Format:** Natural language descriptions
- **Organized by Category:** Memory, Knowledge, Confidence, Planning, etc.
- **Context-Aware:** Explain why tools were called
- **Status:** Design complete, needs implementation

### **6. Context Web Instead of Linear Chat**
**Idea:** Replace linear chat history with visual web of related contexts
- **Context Web:** Visual graph of related topics
- **Timeline Integration:** Chronological view + contextual connections
- **Evolution Tracking:** See how understanding evolved
- **Status:** Component exists (`ContextWeb.tsx`), needs integration

### **7. Workflow Automation (Terminal & Port Management)**
**Idea:** Auto-manage terminals and ports (detect, warn, close with approval)
- **Terminal Management:** Auto-detect and manage Cursor terminals
- **Port Management:** Auto-detect and manage ports
- **Smart Detection:** Detect same/upgraded apps, port conflicts
- **Warning System:** Warn before closing terminals/ports
- **User Approval:** Request approval before closing
- **Status:** Scribe researching & documenting, Lexicon will implement after approval

---

## 🔧 **TECHNICAL ARCHITECTURE**

### **Extension Structure:**
```
cursor-addon/
├── src/
│   ├── extension.ts                    # Extension entry point
│   ├── webviewProvider.ts              # Webview provider (AIMOSWebviewProvider)
│   ├── lucidDashboardProvider.ts       # Lucid Dashboard provider (WebviewViewProvider)
│   ├── providers/
│   │   └── dashboardProvider.ts        # Dashboard provider
│   ├── mcp/
│   │   └── mcpClient.ts               # MCP client
│   ├── memory/
│   │   └── memoryManager.ts           # Memory manager
│   ├── models/
│   │   └── modelSelector.ts           # Model selector
│   └── crossModel/
│       └── crossModelManager.ts       # Cross-model manager
├── dist/                               # Built React UI (needs to be built)
└── package.json                        # Extension manifest
```

### **React UI Structure:**
```
packages/ide_chat_app/src/
├── components/
│   ├── AgentManagementDashboard.tsx    # PRIMARY TAB - Partially built
│   ├── MemoryBrowser.tsx               # ✅ Complete
│   ├── MemoryBrowserEnhanced.tsx      # ✅ Complete
│   ├── AIMOSOrchestration.tsx          # Prompt chain visualization
│   ├── ContextWeb.tsx                  # Context web visualization
│   ├── TimelineVisualization.tsx       # Timeline visualization
│   ├── LucidOrchestrator/              # Four-pane interface
│   │   ├── BlueprintPane.tsx
│   │   ├── CodePane.tsx
│   │   ├── SpecPane.tsx
│   │   └── TimelinePane.tsx
│   └── [Many other components...]
├── services/
│   ├── AIMOSService.ts                # ✅ Complete - 958 lines
│   ├── HttpLucidDaemonService.ts      # ✅ Complete - Daemon integration
│   └── [Other services...]
└── hooks/
    ├── useDaemon.ts                   # ✅ Complete - React hook for daemon
    └── [Other hooks...]
```

### **Integration Flow:**
```
Cursor Extension (webviewProvider.ts)
  ↓
React UI (AgentManagementDashboard.tsx)
  ↓
Services (AIMOSService.ts, HttpLucidDaemonService.ts)
  ↓
MCP Server (lucid_mcp_server.py) OR Daemon (daemon_rag_system.py)
  ↓
AIM-OS Systems (CMC, HHNI, VIF, SEG, APOE, SDF-CVF, CAS)
```

---

## 📋 **WHAT'S MISSING & NEEDS WORK**

### **1. Agent Management Dashboard Enhancements (HIGH PRIORITY)**

**Missing from Current Implementation:**
- ❌ **Confidence Bands:** No A/B/C color coding
- ❌ **κ-Gate Status:** No display of confidence-gated automation status
- ❌ **Confidence-Gated Actions:** Actions not disabled when confidence low
- ❌ **Confusion Indicators:** No ⚠️ indicators when confidence low
- ❌ **Agent Assistance System:** No "Ask Question" button, no context provision
- ❌ **Confidence Metrics Dashboard:** No overall confidence, no distribution chart
- ❌ **VIF Integration:** No real confidence tracking via VIF
- ❌ **CAS Integration:** No confusion detection via CAS

**Action Required:**
- Lexicon needs to review `LEXICON_UI_ENHANCEMENT_DIRECTIVE.md`
- Add confidence-based safety gates
- Add agent assistance system
- Add confidence metrics dashboard
- Integrate VIF and CAS

### **2. React UI Build & Integration**

**Current State:**
- ⏳ React UI not built (`dist/` folder missing or empty)
- ⏳ TypeScript compilation errors
- ⏳ Extension shows fallback HTML (not React UI)

**Action Required:**
- Fix TypeScript compilation errors
- Build React UI: `cd packages/ide_chat_app && npm run build`
- Copy dist to extension: `cp -r packages/ide_chat_app/dist cursor-addon/dist`
- Test extension in Cursor

### **3. Multi-Tab Structure**

**Current State:**
- ⏳ Only Agent Management Dashboard exists (partially)
- ⏳ Other tabs not implemented yet

**Action Required:**
- Implement tab navigation system
- Build Chat Interface tab
- Build Prompt Chains tab
- Build MCP Tools tab
- Build Timeline & Calendar tab
- Build Settings tab
- Build Workflow Automation tab (after Scribe's research)

### **4. Service Integration**

**Current State:**
- ✅ Daemon integration complete
- ✅ Memory browser connected to CMC
- ⏳ VIF integration not implemented
- ⏳ CAS integration not implemented
- ⏳ Gemini/Cerebras integration not implemented
- ⏳ Prompt chain visualization not connected

**Action Required:**
- Integrate VIF for confidence tracking
- Integrate CAS for confusion detection
- Integrate Gemini/Cerebras API
- Connect prompt chain visualization
- Connect MCP tools display
- Connect timeline & calendar

### **5. Workflow Automation**

**Current State:**
- ⏳ Scribe researching & documenting
- ⏳ Not implemented yet

**Action Required:**
- Scribe completes research & documentation
- Lexicon reviews & approves
- Lexicon implements after approval

---

## 🎯 **PRIORITY ORDER**

### **Immediate (This Week):**
1. **Fix React UI Build Issues**
   - Fix TypeScript compilation errors
   - Build React UI
   - Test extension in Cursor

2. **Enhance Agent Management Dashboard**
   - Add confidence bands (A/B/C color coding)
   - Add κ-gate status display
   - Add confidence-gated automation (disable actions when confidence low)
   - Add confusion indicators
   - Add agent assistance system (ask questions, context provision)
   - Add confidence metrics dashboard

### **Short-term (Next 2 Weeks):**
3. **Implement Multi-Tab Structure**
   - Tab navigation system
   - Chat Interface tab
   - Prompt Chains tab
   - MCP Tools tab
   - Timeline & Calendar tab
   - Settings tab

4. **Service Integration**
   - VIF integration for confidence tracking
   - CAS integration for confusion detection
   - Gemini/Cerebras API integration
   - Prompt chain visualization connection
   - MCP tools display connection

### **Medium-term (Next Month):**
5. **Workflow Automation**
   - Scribe completes research & documentation
   - Lexicon reviews & approves
   - Lexicon implements terminal & port management

6. **Advanced Features**
   - Voice I/O integration
   - Performance analytics
   - Advanced automation rules
   - Agent coordination visualization

---

## 💬 **DISCUSSION POINTS**

### **1. UI Panel Placement**
**Current:** Bottom drawer (above terminal panel)  
**Options:**
- Bottom drawer (current plan)
- Left sidebar
- Right sidebar
- Floating window
- **Question:** What's your preference? Should it be movable?

### **2. Default View**
**Current Plan:** Agent Management Dashboard (PRIMARY TAB)  
**Rationale:** Core mission is automating Cursor, managing agents is most frequent operation  
**Question:** Do you agree with this priority? Should it be customizable?

### **3. Confidence-Based Safety**
**Current Plan:** Confidence-gated automation (κ-gating)  
**Features:**
- Actions disabled when confidence < 0.70
- Warnings when confidence low
- Agent assistance system when confused
**Question:** Are these thresholds right? Should they be configurable?

### **4. Agent Assistance System**
**Current Plan:** Agents can ask questions, Lucid AI answers, UI provides context  
**Question:** How should this work? Should questions appear as notifications? Should there be a dedicated panel?

### **5. Workflow Automation**
**Current Plan:** Terminal & port management with warnings and approval  
**Question:** What automation level do you prefer? Full Auto, Semi-Auto, or Manual?

### **6. MCP Tools Display**
**Current Plan:** Show as AI conversations, organized by category  
**Question:** Should all MCP operations be visible, or only important ones?

### **7. Context Web vs Linear Chat**
**Current Plan:** Context web visualization instead of linear chat history  
**Question:** Do you want both? Linear for quick reference, context web for exploration?

### **8. Gemini/Cerebras Integration**
**Current Plan:** Gemini/Cerebras as conversational interface, manages complexity  
**Question:** Should this be the default conversation mode, or optional?

---

## 📊 **VISUAL SUMMARY**

### **What's Built:**
```
✅ Extension Foundation        [████████████████████] 100%
✅ Daemon Integration         [████████████████████] 100%
✅ Memory Browser             [████████████████████] 100%
⏳ Agent Management Dashboard [████████░░░░░░░░░░░░]  50%
⏳ React UI Build             [████░░░░░░░░░░░░░░░░]  20%
⏳ Multi-Tab Structure        [██░░░░░░░░░░░░░░░░░░]  10%
⏳ Service Integration        [████████░░░░░░░░░░░░]  40%
⏳ Workflow Automation        [░░░░░░░░░░░░░░░░░░░░]   0% (research phase)
```

### **What's Planned:**
```
📋 7 Tabs Structure
📋 Confidence-Based Safety Gates
📋 Agent Assistance System
📋 Prompt Chain Visualization
📋 MCP Tools as Conversations
📋 Context Web Visualization
📋 Workflow Automation
📋 Gemini/Cerebras Integration
```

---

## 🚀 **NEXT STEPS**

### **Immediate Actions:**
1. **Lexicon:** Fix React UI build issues, enhance Agent Management Dashboard
2. **Scribe:** Complete workflow automation research & documentation
3. **Lexicon:** Review Scribe's documentation, approve workflow automation plan
4. **Lexicon:** Implement confidence-based safety gates
5. **Lexicon:** Implement agent assistance system

### **Short-term Actions:**
6. **Lexicon:** Implement multi-tab structure
7. **Lexicon:** Integrate VIF and CAS
8. **Lexicon:** Connect Gemini/Cerebras API
9. **Lexicon:** Connect prompt chain visualization
10. **Lexicon:** Connect MCP tools display

### **Medium-term Actions:**
11. **Lexicon:** Implement workflow automation (after Scribe's research)
12. **Lexicon:** Advanced features (voice I/O, analytics, etc.)

---

## 💙 **SUMMARY**

**Current State:**
- ✅ Extension foundation complete
- ✅ Daemon integration complete
- ✅ Memory browser functional
- ⏳ Agent Management Dashboard partially built (needs enhancement)
- ⏳ React UI needs to be built
- ⏳ Multi-tab structure needs implementation
- ⏳ Workflow automation needs research (Scribe working on it)

**Design Vision:**
- ✅ Complete design vision document (`CURSOR_UI_COMPREHENSIVE_DESIGN_VISION.md`)
- ✅ 7 tabs planned
- ✅ Confidence-based safety gates designed
- ✅ Agent assistance system designed
- ✅ Workflow automation designed

**Key Innovation:**
- **Automation Cockpit** - Not just a chat interface, but a control station for automating Cursor
- **Confidence-Based Safety** - VIF integration ensures safe automation
- **Agent Assistance** - Agents can ask questions when confused
- **Workflow Automation** - Terminal & port management addresses real pain points

**What We Need:**
- Build React UI
- Enhance Agent Management Dashboard
- Implement multi-tab structure
- Integrate services
- Implement workflow automation (after Scribe's research)

---

**Status:** Ready for discussion! What would you like to focus on? 💙✨

