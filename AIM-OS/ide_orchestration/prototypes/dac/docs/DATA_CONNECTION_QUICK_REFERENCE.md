# Data Connection Quick Reference

**Purpose:** Quick lookup for data connections and panel requirements  
**Full Details:** See `DATA_CONNECTION_INVENTORY.md`  
**Last Updated:** 2025-01-27

---

## 🚀 **QUICK STATUS**

**✅ Connected (3):** SystemIndexBrowserPanel, SystemMapPanel, SuperIndexPanel  
**⏳ Needs Connection (2):** GoalTreePanel, HierarchicalNavigationPanel (need creation)  
**⚠️ Mock Data (11):** Using MCP hooks (will connect when AIM-OS running)  
**❓ Unknown (8):** Need audit

---

## 📊 **DATA SOURCES**

### **Backend API (Port 8000) - Organization Data**
- `/api/system-indexes` ✅
- `/api/system-maps` ✅
- `/api/super-index` ✅
- `/api/goal-tree` ✅
- `/api/hierarchical-navigation` ✅

### **Command Server (Port 5001) - AIM-OS Systems**
- `/mcp/execute` - 84 MCP tools
- `/mcp/list` - List tools
- `/health` - Health check

---

## 🎨 **PANEL CONNECTION STATUS**

### **✅ Connected (Backend API)**
- SystemIndexBrowserPanel → SystemIndexService
- SystemMapPanel → SystemMapService
- SuperIndexPanel → SuperIndexService

### **⏳ Needs Creation**
- GoalTreePanel → GoalTreeService (service ready)
- HierarchicalNavigationPanel → HierarchicalNavigationService (service ready)

### **⚠️ Mock Data (MCP Tools)**
- MemoryBrowser → useCMC, useHHNI, useVIF
- TimelineView → useTCS, useCMC
- ContextWeb → useSEG, useHHNI, useTCS
- SystemStatus → useCAS
- DebugConsolePanel → useCMC, useCAS, useSEG, useTCS
- CodeEditor → useVIF, useSEG, useCMC, useTCS, useCAS
- FileTree → useCMC, useVIF, useSEG, useHHNI
- OutlinePanel → useHHNI
- TerminalPanel → useCMC, useVIF
- DocumentationExplorerPanel → useHHNI
- NLTagsExplorerPanel → useHHNI
- MasterIndexPanel → useHHNI

### **❓ Needs Audit**
- AIChatManagement
- LogAnalysisDashboard
- LogSentinelsAnomalies
- LogSentinelsSummaries
- ProblemsPanel
- ResourceMonitor
- RouterPanel
- ToolQualityDashboard

---

## 🔧 **SERVICES**

### **Organization Services (Backend API)**
- SystemIndexService ✅
- SystemMapService ✅
- SuperIndexService ✅
- GoalTreeService ✅
- HierarchicalNavigationService ✅

### **AIM-OS Services (Command Server/MCP)**
- MCPService ✅
- CMCService ✅
- HHNIService ✅
- VIFService ✅
- TCSService ✅
- SEGService ✅
- CASService ✅
- APOEService ✅

---

## 📋 **WHEN ADDING NEW PANEL**

1. **Check this document** - What data does it need?
2. **Identify data source** - Backend API (8000) or Command Server (5001)?
3. **Create/use service** - Use existing service or create new one
4. **Update inventory** - Add to `DATA_CONNECTION_INVENTORY.md`
5. **Update status** - Mark as connected/mock/needs connection

---

**See:** `DATA_CONNECTION_INVENTORY.md` for complete details

