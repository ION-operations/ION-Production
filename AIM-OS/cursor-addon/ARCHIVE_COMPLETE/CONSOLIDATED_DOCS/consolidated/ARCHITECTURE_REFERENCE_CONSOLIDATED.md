# CONSOLIDATED ARCHITECTURE REFERENCE
# Complete Architecture Documentation Consolidated

**Created:** 2025-11-01  
**Purpose:** Single consolidated architecture reference  
**Sources:** architecture_docs category (15 files)

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### **Extension Structure**
```
Cursor/VSCode
  ↓
AIM-OS Extension (v1.2.1)
  ├── Extension Host (extension.ts)
  ├── Dashboard Provider (lucidDashboardProvider.ts)
  ├── Pure HTML Provider (pureHtmlDashboardProvider.ts)
  ├── Test Provider (minimalTestProvider.ts)
  └── React UI (dist/)
      ├── index.html
      └── assets/
          ├── main-*.js (React bundle)
          └── main-*.css (Styles)
```

---

## 📦 COMPONENT ARCHITECTURE

### **1. Extension Entry Point**
**File:** `extension.ts`  
**Purpose:** Extension activation and initialization  
**Responsibilities:**
- Extension activation
- Manager initialization
- Provider registration
- Command registration
- MCP client setup

**Key Code:**
```typescript
export function activate(context: vscode.ExtensionContext) {
    // Initialize logger
    // Initialize managers
    // Register providers
    // Register commands
}
```

---

### **2. Dashboard Provider**
**File:** `lucidDashboardProvider.ts`  
**Purpose:** React dashboard webview provider  
**Responsibilities:**
- Webview view provider implementation
- HTML content generation
- Asset URI conversion
- CSP/TrustedTypes handling
- Message passing

**Key Code:**
```typescript
export class LucidOrchestratorDashboardProvider implements vscode.WebviewViewProvider {
    resolveWebviewView(webviewView, context, token) {
        // Set webview options
        // Generate HTML content
        // Convert asset URIs
        // Set HTML content
    }
}
```

---

### **3. Pure HTML Provider**
**File:** `pureHtmlDashboardProvider.ts`  
**Purpose:** Isolated HTML dashboard (test version)  
**Responsibilities:**
- Pure HTML/CSS/JS dashboard
- No React dependencies
- No external assets
- Self-contained content

**Status:** Test version for isolation

---

### **4. React UI**
**Location:** `packages/ide_chat_app/dist/`  
**Purpose:** Main dashboard UI  
**Components:**
- MainDashboard (6 tabs)
- AgentManagementDashboard
- Chat interface
- MCP tools interface
- Timeline view
- NL Tags interface

**Build:** Vite build system  
**Output:** Module scripts (`type="module"`)

---

## 🔗 INTEGRATION POINTS

### **Extension ↔ React UI**
**Method:** Webview message passing  
**Protocol:**
- Extension → UI: `webview.postMessage()`
- UI → Extension: `vscode.postMessage()`

**Commands:**
- `mcpCall` - MCP tool execution
- `getSystemStatus` - Status requests
- `manageAgent` - Agent management

---

### **Extension ↔ MCP Server**
**Method:** MCPClient  
**Protocol:** JSON-RPC 2.0  
**Connection:** Spawns Python process  
**Tools:** 59 MCP tools available

---

## 📋 VIEW ARCHITECTURE

### **Views Defined**
1. **aimosDashboard** (Right Sidebar)
   - Container: `aimos` (activitybar)
   - Provider: `PureHtmlDashboardProvider` (currently)
   - Purpose: Main dashboard

2. **simpleTestPanel** (Bottom Panel)
   - Container: `aimosDevTools` (panel)
   - Provider: `MinimalTestProvider`
   - Purpose: Test/debug panel

---

## 🎨 UI ARCHITECTURE

### **Dashboard Tabs**
1. **Agents** - Agent management
2. **Chat** - Chat interface
3. **Chains** - Prompt chains
4. **Tools** - MCP tools
5. **Timeline** - Timeline view
6. **NL Tags** - Natural language tags

---

## 🔧 BUILD ARCHITECTURE

### **Build Process**
1. **React UI Build**
   - Source: `packages/ide_chat_app/src/`
   - Build tool: Vite
   - Output: `packages/ide_chat_app/dist/`
   - Features: Module scripts, code splitting

2. **Extension Build**
   - Source: `cursor-addon/src/`
   - Build tool: TypeScript compiler
   - Output: `cursor-addon/out/`
   - Packaging: VSIX format

3. **Asset Loading**
   - React UI copied to extension `dist/`
   - Asset URIs converted to `vscode-webview://`
   - CSP and TrustedTypes applied

---

## 📊 ARCHITECTURE INSIGHTS

### **What Works**
- Extension structure ✅
- Provider registration ✅
- View definitions ✅
- Build process ✅

### **What Doesn't Work**
- Webview resolution ❌
- HTML content loading ❌
- React UI mounting ❌

---

**Status:** Consolidated architecture reference complete  
**Use:** Reference for understanding system structure



