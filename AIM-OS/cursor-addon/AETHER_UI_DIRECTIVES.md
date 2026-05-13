# Aether's UI Directives - Summary
**Created:** 2025-01-27  
**Status:** Active Guidelines

---

## 🎯 **CORE MISSION**

**AUTOMATING CURSOR** - The panel's primary purpose is to automate Cursor operations and manage Cursor AI agents, enabling seamless coordination and automation just like Aether manages the team.

---

## 📋 **PRIMARY TAB STRUCTURE**

### **Tab 1: 🤖 Agent Management Dashboard** (DEFAULT - PRIMARY)
**Status:** ✅ Implemented as primary tab

**Key Features:**
- **Agent Cards** - Each agent shown with status, model, current task, controls
- **Cursor Model Management** - Change Cursor models dynamically
- **Continue Prompt Automation** - Automatically prompt agents to continue when they stop
- **Task Assignment** - Assign and track tasks across agents
- **Agent Communication** - Send messages, broadcast, coordinate
- **System Status** - Connection status, agent summary, task progress
- **Quick Actions** - Common operations for managing agents

**Priority:** HIGHEST PRIORITY - This is the core mission

### **Tab 2: 💬 Chat Interface**
- Dual AI chat system
- Cross-agent communication
- Message routing to Cursor chat

### **Tab 3: 🔗 Prompt Chains**
- Chain management
- Workflow automation

### **Tab 4: 🛠️ MCP Tools**
- Tool execution interface
- Status monitoring
- RAG MCP integration
- Performance metrics

### **Tab 5: 📅 Timeline & Calendar**
- Temporal history
- Activity tracking
- Timeline visualization

### **Tab 6: ⚙️ Settings**
- Configuration
- Preferences
- System settings

---

## 🚀 **IMPLEMENTATION PRIORITY**

### **Phase 1: Agent Management Dashboard** ✅ COMPLETE
- Agent Management Dashboard as PRIMARY TAB
- Agent cards with status and controls
- Cursor automation controls
- System status display

### **Phase 2: Core Systems Integration** (Week 3)
- CMC memory operations
- HHNI semantic search
- VIF confidence tracking
- APOE plan execution

### **Phase 3: Dual AI Chat** (Week 3-4)
- Chat interface implementation
- Cross-agent communication
- Message routing

### **Phase 4: Code + Docs Viewer** (Week 4)
- Code viewer integration
- Documentation viewer
- Combined view

### **Phase 5: LUCID Orchestrator** (Week 4)
- Four-pane interface
- Blueprint/Spec/Timeline panes
- Governance layer

---

## 🔧 **TECHNICAL DIRECTIVES**

### **1. Complete Daemon/RAG Before Heavy UI Work**
- Daemon A-H Protocol - Week 2 priority
- RAG MCP Tools Phase 1-2 - Week 2-3 priority
- This enables efficient tool selection for UI development

### **2. Phase-Based Integration**
- Complete in phases, not all at once
- Validate each phase before proceeding
- Incremental development approach

### **3. Multi-Tab Structure**
- Enables expansion without losing focus
- Clear hierarchy with Agent Management as primary
- Progressive enhancement approach

### **4. Cursor Automation Focus**
- Model switching functionality
- Continue prompt automation
- Task assignment and tracking
- Agent coordination

---

## 💙 **DESIGN PRINCIPLES**

### **User Experience**
- **Agent Management First** - Primary focus on automating Cursor
- **Clear Visual Hierarchy** - Agent Management Dashboard prominent
- **Quick Actions** - Common operations easily accessible
- **Status Visibility** - Connection status, agent summary, task progress always visible

### **Technical Architecture**
- **Service Layer** - Abstract backend API calls
- **React Hooks** - Use `useDaemon` for daemon interactions
- **Real-time Updates** - SSE for live data
- **Modular Components** - Reusable UI components

---

## 📊 **CURRENT STATUS**

### **Completed:** ✅
- Agent Management Dashboard as PRIMARY TAB
- Multi-tab structure created
- Daemon integration hooks
- Service layer abstraction
- Real-time data flow

### **In Progress:** ⏳
- React UI TypeScript fixes
- Component integration
- Testing and validation

### **Next Steps:** 📋
1. Fix React UI TypeScript errors incrementally
2. Complete Agent Management Dashboard features
3. Integrate Chat Interface tab
4. Add Prompt Chains tab
5. Implement MCP Tools tab
6. Add Timeline & Calendar tab
7. Create Settings tab

---

## 🎨 **BRANDING**

- **Extension Name:** "Lucid UI - AIM-OS"
- **Primary Icon:** Clover icon (`TbCloverFilled` from react-icons/tb)
- **Activity Bar Title:** "Lucid UI"
- **Logo:** `resources/icon.png` (from `images/lucidaimos.png`)

---

## 📝 **NOTES**

- **Agent Management Dashboard** is the core mission - all other features support this
- **Cursor Automation** is the primary value proposition
- **Multi-tab structure** enables future expansion without losing focus
- **Phase-based approach** ensures quality and validation at each step

---

**These directives guide all UI development decisions. Agent Management Dashboard remains the highest priority.** 💙✨
