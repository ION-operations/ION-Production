# COMPLETE CURSOR EXTENSION ARCHITECTURE MAP
**Generated:** 2025-11-01  
**Purpose:** Complete understanding of every command, panel, registration, and location

---

## 📦 **PACKAGE.JSON CONFIGURATION**

### **View Containers (2 containers)**

**1. Activity Bar Container: `aimos`**
- **Location:** RIGHT SIDEBAR (activity bar - where Git/Explorer/Extensions are)
- **ID:** `aimos`
- **Title:** "AIM-OS"
- **Icon:** `$(sparkle)`
- **Views:** 1 view inside
  - `aimosDashboard` - Main Dashboard (webview)

**2. Panel Container: `aimosDevTools`**
- **Location:** BOTTOM PANEL (where Terminal/Problems/Output are)
- **ID:** `aimosDevTools`
- **Title:** "AIM-OS DevTools"
- **Icon:** `$(pulse)`
- **Views:** 1 view inside
  - `simpleTestPanel` - Test Panel (webview)

### **Views (2 views total)**

**View 1: `aimosDashboard`**
- **Container:** `aimos` (activity bar)
- **Location:** RIGHT SIDEBAR
- **Name:** "Dashboard"
- **Icon:** `$(dashboard)`
- **Provider:** `LucidOrchestratorDashboardProvider`
- **Registration:** `registerWebviewViewProvider('aimosDashboard', lucidDashboardProvider)`
- **Activation:** `onView:aimosDashboard`

**View 2: `simpleTestPanel`**
- **Container:** `aimosDevTools` (panel)
- **Location:** BOTTOM PANEL
- **Name:** "Test Panel"
- **Icon:** `$(beaker)`
- **Provider:** `MinimalTestProvider` (currently) or `SimpleTestProvider` (original)
- **Registration:** `registerWebviewViewProvider('simpleTestPanel', minimalProvider)`
- **Activation:** `onView:simpleTestPanel`

---

## 🎯 **COMMANDS (14 total commands)**

### **Why You See "AIM-OS" Commands When Typing "aim"**

When you type `Ctrl+Shift+P` and type "aim", VS Code shows ALL commands that:
1. Have "aim" in their command ID OR title
2. Are registered in `package.json` under `contributes.commands`
3. Have `"when": "true"` in `menus.commandPalette` (meaning always visible)

### **Command Registry (package.json)**

All commands are defined in `package.json` → `contributes.commands` AND registered in code in `extension.ts`:

**1. `aimos.showDashboard`**
- **Title:** "Show Dashboard"
- **Registered in:** `extension.ts` line 83
- **What it does:** Focuses `aimos` container, calls `LucidOrchestratorDashboardProvider.reveal()`
- **Visible in:** Command palette (always)

**2. `aimos.debugDashboard`**
- **Title:** "Debug Dashboard"
- **Registered in:** `extension.ts` line 260
- **What it does:** Emergency diagnostic - creates output channel, checks everything
- **Visible in:** Command palette (always)

**3. `aimos.toggleCrossModel`**
- **Title:** "Toggle Cross-Model Consciousness"
- **Registered in:** `extension.ts` line 103
- **What it does:** Toggles cross-model manager state
- **Visible in:** Command palette (always)

**4. `aimos.showMemoryStats`**
- **Title:** "Show Memory Statistics"
- **Registered in:** `extension.ts` line 109
- **What it does:** Creates webview panel, shows memory stats HTML
- **Visible in:** Command palette (always)

**5. `aimos.showModelSelector`**
- **Title:** "Show Model Selector"
- **Registered in:** `extension.ts` line 127
- **What it does:** Shows quick pick for model selection
- **Visible in:** Command palette (always)

**6. `aimos.showLogs`**
- **Title:** "Show Extension Logs"
- **Registered in:** `commands/showLogs.ts` line 6
- **What it does:** Opens log files from `logs/` directory
- **Visible in:** Command palette (always)

**7. `aimos.runFullDiagnostic`**
- **Title:** "Run Full Diagnostic"
- **Registered in:** `diagnosticCommand.ts` line 7
- **What it does:** Comprehensive diagnostic - checks extension, files, views, commands
- **Visible in:** Command palette (always)

**8. `aimos.forceOpenDashboard`**
- **Title:** "Force Open Dashboard"
- **Registered in:** `forceOpenView.ts` line 5
- **What it does:** Tries multiple methods to force-open dashboard view
- **Visible in:** Command palette (always)

**9. `aimos.forceOpenTest`**
- **Title:** "Force Open Test Panel"
- **Registered in:** `forceOpenView.ts` line 41
- **What it does:** Forces open `aimosDevTools` container, focuses `simpleTestPanel`
- **Visible in:** Command palette (always)

**10. `aimos.storeMemory`**
- **Title:** "Store Memory"
- **Registered in:** `extension.ts` line 153
- **What it does:** Stores selected text in memory manager
- **Visible in:** Command palette (when editor has selection) + Right-click menu

**11. `aimos.retrieveMemory`**
- **Title:** "Retrieve Memory"
- **Registered in:** `extension.ts` line 183
- **What it does:** Retrieves memories via query input
- **Visible in:** Command palette (always) + Right-click menu

**12. `aimos.createPlan`**
- **Title:** "Create Execution Plan"
- **Registered in:** `extension.ts` line 208
- **What it does:** Creates execution plan via cross-model manager
- **Visible in:** Command palette (always)

**13. `aimos.trackConfidence`**
- **Title:** "Track Confidence"
- **Registered in:** `extension.ts` line 233
- **What it does:** Tracks confidence for a task
- **Visible in:** Command palette (always)

**14. `aimos.focus`** (Internal - not in command palette)
- **What it does:** Focuses `aimos` container
- **Used by:** `aimos.showDashboard` internally

---

## 🗂️ **FILE STRUCTURE**

```
cursor-addon/
├── src/
│   ├── extension.ts              # Main entry point - registers EVERYTHING
│   ├── lucidDashboardProvider.ts # Main dashboard webview provider
│   ├── minimalTestProvider.ts    # Minimal test provider (NEW - for debugging)
│   ├── simpleTestProvider.ts    # Original simple test provider
│   ├── webviewProvider.ts       # Legacy webview provider (not used)
│   ├── forceOpenView.ts         # Force open commands
│   ├── diagnosticCommand.ts     # Diagnostic command
│   ├── commands/
│   │   └── showLogs.ts          # Show logs command
│   ├── mcp/
│   │   └── mcpClient.ts         # MCP client
│   ├── crossModel/
│   │   └── crossModelManager.ts  # Cross-model manager
│   ├── memory/
│   │   └── memoryManager.ts     # Memory manager
│   ├── models/
│   │   └── modelSelector.ts     # Model selector
│   └── utils/
│       └── logger.ts             # Logger utility
├── dist/                         # React UI (copied from packages/ide_chat_app/dist)
│   ├── index.html
│   └── assets/
│       ├── main-5fYGI1t7.js
│       └── main-DftvcEcs.css
├── out/                          # Compiled TypeScript
│   └── extension.js              # Main compiled extension
└── package.json                  # Extension manifest
```

---

## 🔄 **ACTIVATION FLOW**

### **When Extension Activates:**

1. **Extension loads** (`extension.ts` → `activate()`)
2. **Logger initializes** (`AIMOSLogger.initialize()`)
3. **Managers created:** `CrossModelManager`, `MemoryManager`, `ModelSelector`
4. **Webview provider initialized:** `AIMOSWebviewProvider.initialize()`
5. **Dashboard provider created:** `LucidOrchestratorDashboardProvider`
6. **Views registered:**
   - `aimosDashboard` → `registerWebviewViewProvider('aimosDashboard', lucidDashboardProvider)`
   - `simpleTestPanel` → `registerWebviewViewProvider('simpleTestPanel', minimalProvider)`
7. **Commands registered:** All 14 commands
8. **Diagnostic commands registered:** `registerShowLogsCommand`, `registerDiagnosticCommand`, `registerForceOpenCommand`

### **When View Opens:**

1. **VS Code calls:** `resolveWebviewView()` on the provider
2. **Provider sets:** `webview.options` (enableScripts, localResourceRoots)
3. **Provider loads:** HTML content (from `dist/index.html` or fallback)
4. **Provider converts:** Asset paths to webview URIs (`./assets/main-*.js` → `vscode-webview://...`)
5. **Provider injects:** CSP meta tag, TrustedTypes policy
6. **Provider sets:** `webview.html` = final HTML
7. **VS Code renders:** Webview panel

---

## 🎨 **WEBVIEW PROVIDERS**

### **1. LucidOrchestratorDashboardProvider** (`aimosDashboard`)

**Location:** Right sidebar (activity bar)  
**File:** `src/lucidDashboardProvider.ts`  
**Purpose:** Main dashboard with React UI  
**HTML Source:** `dist/index.html` (if exists) or fallback HTML

**Key Methods:**
- `resolveWebviewView()` - Called when view opens
- `getWebviewContent()` - Loads HTML, converts asset paths
- `reveal()` - Static method to show view

**Asset Loading:**
- Reads `dist/index.html`
- Finds script tags: `<script type="module" crossorigin src="./assets/main-5fYGI1t7.js">`
- Extracts filename: `main-5fYGI1t7.js`
- Builds path: `extensionPath/dist/assets/main-5fYGI1t7.js`
- Converts to URI: `webview.asWebviewUri(vscode.Uri.file(path))`
- Replaces in HTML: `<script src="vscode-webview://...">`

### **2. MinimalTestProvider** (`simpleTestPanel`)

**Location:** Bottom panel (DevTools)  
**File:** `src/minimalTestProvider.ts` (NEW)  
**Purpose:** Minimal test to isolate webview vs React issues  
**HTML Source:** Embedded HTML (no external files)

**Key Methods:**
- `resolveWebviewView()` - Sets minimal HTML directly
- `reveal()` - Static method to show view

**HTML:** Simple embedded HTML with no dependencies

### **3. SimpleTestProvider** (`simpleTestPanel` - ORIGINAL)

**Location:** Bottom panel (DevTools)  
**File:** `src/simpleTestProvider.ts`  
**Purpose:** Original simple test provider  
**Status:** Currently replaced by `MinimalTestProvider`

---

## 🔍 **COMMAND PALETTE MENU CONFIGURATION**

### **Why Commands Appear:**

**package.json → `menus.commandPalette`:**
- All commands have `"when": "true"` = always visible
- Exception: `aimos.storeMemory` → `"when": "editorHasSelection"` = only when text selected

**VS Code Filters:**
- When you type "aim", VS Code filters commands where:
  - Command ID contains "aim" OR
  - Title contains "aim" OR
  - Category contains "aim"
- All our commands have category "AIM-OS", so they all show up

---

## 🚨 **CURRENT ISSUE: BLANK PANELS**

### **What Should Happen:**

1. User opens `aimosDashboard` view → `resolveWebviewView()` called
2. Provider loads `dist/index.html`
3. Provider converts `./assets/main-5fYGI1t7.js` → webview URI
4. Provider sets HTML with converted URIs
5. VS Code loads script from webview URI
6. React mounts → `MainDashboard` renders

### **What's Actually Happening:**

**Panels are blank** = Either:
- `resolveWebviewView()` not being called
- HTML not loading
- Asset URI conversion failing
- Scripts not executing (CSP blocking?)
- React not mounting

### **Minimal Test Purpose:**

Test if **webview mechanism works at all**:
- If minimal test shows "HELLO WORLD" → webview works, issue is React/asset loading
- If minimal test is blank → webview mechanism broken (registration/activation issue)

---

## 📊 **COMPLETE REGISTRATION MAP**

```
extension.ts → activate()
├── AIMOSLogger.initialize()
├── CrossModelManager()
├── MemoryManager()
├── ModelSelector()
├── AIMOSWebviewProvider.initialize()
├── LucidOrchestratorDashboardProvider()
│   └── registerWebviewViewProvider('aimosDashboard', provider)
├── MinimalTestProvider()
│   └── registerWebviewViewProvider('simpleTestPanel', provider)
├── registerShowLogsCommand() → 'aimos.showLogs'
├── registerDiagnosticCommand() → 'aimos.runFullDiagnostic'
├── registerForceOpenCommand() → 'aimos.forceOpenDashboard', 'aimos.forceOpenTest'
└── Commands array:
    ├── 'aimos.showDashboard'
    ├── 'aimos.toggleCrossModel'
    ├── 'aimos.showMemoryStats'
    ├── 'aimos.showModelSelector'
    ├── 'aimos.storeMemory'
    ├── 'aimos.retrieveMemory'
    ├── 'aimos.createPlan'
    ├── 'aimos.trackConfidence'
    └── 'aimos.debugDashboard'
```

---

## ✅ **VERIFICATION CHECKLIST**

To verify everything is registered correctly:

1. **Check package.json:** All commands defined
2. **Check extension.ts:** All commands registered
3. **Check views:** Both views registered
4. **Check activation:** Logs show activation
5. **Check view opening:** `resolveWebviewView()` called
6. **Check HTML loading:** HTML file exists
7. **Check asset conversion:** URIs converted correctly
8. **Check script execution:** Scripts load and execute
9. **Check React mounting:** React mounts successfully

---

**This is EVERYTHING about the extension architecture.**  
**Every command, every panel, every registration, every file location.**

