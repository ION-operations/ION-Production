# COMPLETE SYSTEM MAP - Lucid Extension & UI Architecture

**Created:** 2025-11-01  
**Purpose:** Complete system documentation for rescue/recovery  
**Status:** AUTONOMOUS RESEARCH & DOCUMENTATION IN PROGRESS  
**User Status:** Stepping back - comprehensive documentation needed

---

## 🎯 **EXECUTIVE SUMMARY**

This document maps **EVERYTHING** about:
- Lucid Extension architecture
- UI architecture and components
- Cursor extension integration
- All failure points and recovery paths
- Complete system interactions

**Goal:** Enable team to rescue/fix system when user returns.

---

## 📋 **TABLE OF CONTENTS**

1. [Extension Architecture](#extension-architecture)
2. [UI Architecture](#ui-architecture)
3. [Build & Integration Flow](#build--integration-flow)
4. [Failure Points & Recovery](#failure-points--recovery)
5. [Component Interactions](#component-interactions)
6. [Data Flow](#data-flow)
7. [Debugging & Diagnostics](#debugging--diagnostics)
8. [Recovery Procedures](#recovery-procedures)

---

## 🏗️ **EXTENSION ARCHITECTURE**

### **Core Files**

#### **1. extension.ts** (Entry Point)
**Location:** `cursor-addon/src/extension.ts`  
**Purpose:** Extension activation and command registration

**Key Functions:**
- `activate(context)` - Main entry point
- Registers webview providers
- Registers commands
- Initializes managers

**Key Components:**
- `LucidOrchestratorDashboardProvider` - Main dashboard provider
- `AIMOSWebviewProvider` - React UI provider
- `CrossModelManager` - Cross-model consciousness
- `MemoryManager` - Memory operations
- `ModelSelector` - AI model selection

**Registration:**
```typescript
// Two views registered:
1. 'lucidOrchestratorDashboard' - Panel view (right side, 2 star icons)
2. 'aimosDashboard' - Activity bar view (left side)

// Both use same provider instance
```

**Commands Registered:**
- `aimos.showDashboard` - Reveals dashboard
- `aimos.debugDashboard` - Diagnostic command
- `aimos.toggleCrossModel` - Cross-model toggle
- `aimos.showMemoryStats` - Memory statistics
- `aimos.showModelSelector` - Model selection
- `aimos.storeMemory` - Store memory
- `aimos.retrieveMemory` - Retrieve memory
- `aimos.createPlan` - Create execution plan
- `aimos.trackConfidence` - Track confidence

**Activation Events:**
- `onCommand:aimos.showDashboard`
- `onCommand:aimos.toggleCrossModel`
- `onCommand:aimos.showMemoryStats`
- `onCommand:aimos.showModelSelector`

**Critical:** Extension activates when commands are executed OR views are opened.

---

#### **2. lucidDashboardProvider.ts** (Main Dashboard Provider)
**Location:** `cursor-addon/src/lucidDashboardProvider.ts`  
**Purpose:** Provides webview content for dashboard panels

**Key Class:** `LucidOrchestratorDashboardProvider`

**Implements:** `vscode.WebviewViewProvider`

**Critical Method:** `resolveWebviewView(webviewView, context, token)`

**Flow:**
1. Creates output channel (`AIM-OS Dashboard`)
2. Sets test HTML first (red text)
3. Logs diagnostic info
4. Sets webview options (AFTER HTML - POTENTIAL BUG)
5. After 2 seconds, loads full HTML
6. Sets up message handlers
7. Loads initial state

**Current Issue:** Webview options set AFTER HTML (line 128-134 after line 118)
- VS Code docs suggest options should be set BEFORE HTML
- This might prevent proper initialization

**HTML Loading Process:**
1. Test HTML set immediately (verification)
2. `getWebviewContent()` called after 2-second delay
3. Reads `dist/index.html`
4. Replaces asset paths with webview URIs
5. Injects TrustedTypes policy
6. Injects CSP meta tag
7. Returns final HTML

**Asset Path Replacement:**
- Regex: `/<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi`
- Extracts filename from path
- Converts to `vscode-webview://` URI
- Adds cache-busting timestamp

**TrustedTypes Policy:**
- Created BEFORE CSP (critical)
- Allows HTML, Script, ScriptURL creation
- Required for module scripts in VS Code

**CSP Configuration:**
- `script-src` includes `'module'` directive
- Allows `'unsafe-inline'` and `'unsafe-eval'`
- Includes `webview.cspSource`

**Message Handlers:**
- `movePanel` - Panel positioning
- `connectDaemon` - Daemon connection
- `selectModel` - Model selection
- `manageAgent` - Agent management
- `executeMCPTool` - MCP tool execution
- `mcpCall` - MCP tool calls from React
- `getSystemStatus` - System status check

**Output Channel:**
- Name: `AIM-OS Dashboard`
- Shows automatically when resolveWebviewView called
- Contains all diagnostic logs

---

#### **3. webviewProvider.ts** (React UI Provider)
**Location:** `cursor-addon/src/webviewProvider.ts`  
**Purpose:** Creates webview panels (separate from dashboard views)

**Key Class:** `AIMOSWebviewProvider`

**Static Methods:**
- `initialize(context)` - Initialize provider
- `createOrShow()` - Create or show panel
- `postMessage(message)` - Send message to panel

**Creates:** `vscode.WebviewPanel` (editor panel, not sidebar)

**Note:** This is DIFFERENT from dashboard provider
- Dashboard = WebviewView (sidebar/panel)
- This = WebviewPanel (editor tab)

**Current Status:** Not actively used - dashboard provider handles UI

---

### **Supporting Components**

#### **4. mcp/mcpClient.ts** (MCP Client)
**Purpose:** Communicates with MCP server

**Status:** Implementation exists but may not be fully connected

**Note:** Cursor manages MCP servers via `~/.cursor/mcp.json`
- Extension may not have direct access
- May need to read config and connect manually

---

#### **5. Managers** (CrossModel, Memory, ModelSelector)
**Purpose:** Business logic for features

**Status:** Implemented but may need backend connections

---

## 🎨 **UI ARCHITECTURE**

### **React UI Structure**

#### **Entry Point: main-cursor.tsx**
**Location:** `packages/ide_chat_app/src/main-cursor.tsx`  
**Purpose:** Entry point for Cursor extension (renders MainDashboard)

**Note:** Different from `main.tsx` (standalone version)

---

#### **Main Component: MainDashboard.tsx**
**Location:** `packages/ide_chat_app/src/components/MainDashboard.tsx`  
**Purpose:** Main dashboard UI component

**Features:**
- Tabs: Agents, Chat, Chains, Tools, Timeline, NL Tags
- Full dashboard interface
- Integration with AIM-OS services

---

### **Build Output**

#### **dist/index.html**
**Location:** `packages/ide_chat_app/dist/index.html`  
**Content:**
```html
<!doctype html>
<html lang="en">
  <head>
    <script type="module" crossorigin src="./assets/main-5fYGI1t7.js"></script>
    <link rel="stylesheet" crossorigin href="./assets/main-DftvcEcs.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

**Assets:**
- `main-5fYGI1t7.js` - Main React bundle (243KB)
- `main-DftvcEcs.css` - Styles (48KB)

**Note:** Script has `type="module"` and `crossorigin` attributes
- These must be preserved during path replacement
- Current regex handles this

---

## 🔄 **BUILD & INTEGRATION FLOW**

### **Build Process** (build-extension.js)

**Step 1: Build React UI**
- Runs `npm run build` in `packages/ide_chat_app`
- Creates `dist/` folder with HTML and assets
- Continues even if TypeScript errors (uses fallback)

**Step 2: Copy dist to Extension**
- Copies `packages/ide_chat_app/dist/` → `cursor-addon/dist/`
- Recursive copy of all files
- Creates empty dist if React build fails

**Step 3: Compile Extension TypeScript**
- Runs `tsc -p ./` in `cursor-addon`
- Creates `out/` folder with compiled JS
- Continues even if node_modules type errors

**Step 4: Package Extension**
- Runs `vsce package`
- Creates `aimos-cursor-addon.vsix`
- Includes: `out/`, `dist/`, `package.json`, `resources/`

---

### **Installation Flow**

**Installation:**
```bash
code --install-extension aimos-cursor-addon.vsix --force
```

**Activation:**
- Extension activates when:
  1. Command executed (e.g., `aimos.showDashboard`)
  2. View opened (e.g., clicking panel icon)
  3. Activation event triggered

**Registration:**
- `activate()` function called
- Providers registered with VS Code
- Commands registered
- Views become available

---

### **Runtime Flow**

**User Opens Dashboard:**
1. User clicks panel icon (2 star icons on right)
2. VS Code calls `resolveWebviewView()` on provider
3. Provider sets test HTML immediately
4. Provider logs diagnostic info
5. Provider sets webview options
6. Provider loads full HTML after 2 seconds
7. React app mounts in webview
8. React app communicates via `postMessage`

**React App Loads:**
1. HTML loads with webview URIs for assets
2. Browser loads `main-5fYGI1t7.js` (module script)
3. TrustedTypes policy allows script execution
4. React mounts to `<div id="root">`
5. MainDashboard component renders
6. App connects to services

---

## 🐛 **FAILURE POINTS & RECOVERY**

### **Failure Point 1: Extension Not Activating**

**Symptoms:**
- Panel doesn't open
- Commands don't exist
- No output channel

**Causes:**
- Extension not installed
- Installation corrupted
- Activation events not triggered
- TypeScript compilation failed

**Diagnosis:**
- Check `~/.cursor/extensions/aimos-cursor-addon-*/`
- Check Extension Host console for errors
- Try `aimos.debugDashboard` command

**Recovery:**
- Reinstall extension
- Check `out/extension.js` exists
- Check `package.json` activation events

---

### **Failure Point 2: resolveWebviewView Not Called**

**Symptoms:**
- Panel opens but blank
- No diagnostic logs
- Output channel empty

**Causes:**
- Provider not registered correctly
- View ID mismatch
- Extension activated but provider not called

**Diagnosis:**
- Check Extension Host console for registration logs
- Check `[AIM-OS] ✅ Registered` messages
- Check view IDs match `package.json`

**Recovery:**
- Verify provider registration in `extension.ts`
- Check `package.json` view IDs match
- Restart Cursor

---

### **Failure Point 3: Webview Options Set After HTML**

**Symptoms:**
- Test HTML doesn't appear
- Webview blank
- No errors visible

**Cause:**
- Options set AFTER HTML (current code)
- VS Code may require options BEFORE HTML

**Diagnosis:**
- Check code order in `resolveWebviewView`
- Current: HTML at line 118, options at line 128

**Recovery:**
- Move `webviewView.webview.options = {...}` BEFORE `webviewView.webview.html = testHtml`
- Rebuild and reinstall

---

### **Failure Point 4: Asset Paths Not Replaced**

**Symptoms:**
- Blank panel
- 404 errors in webview console
- Scripts not loading

**Causes:**
- Regex not matching HTML format
- File paths incorrect
- Webview URI generation failing

**Diagnosis:**
- Check diagnostic logs for replacement counts
- Check webview console for 404 errors
- Verify asset files exist

**Recovery:**
- Fix regex pattern
- Verify file paths
- Check `asWebviewUri()` working

---

### **Failure Point 5: TrustedTypes Blocking**

**Symptoms:**
- Blank panel
- TrustedTypes errors in console
- Module scripts not executing

**Causes:**
- TrustedTypes policy not created
- CSP too restrictive
- Policy created after CSP

**Diagnosis:**
- Check webview console for TrustedTypes errors
- Verify policy script exists in HTML
- Check CSP allows modules

**Recovery:**
- Ensure TrustedTypes script BEFORE CSP
- Verify policy creation succeeds
- Check CSP includes `'module'`

---

### **Failure Point 6: React Not Mounting**

**Symptoms:**
- HTML loads but no React UI
- Root element exists but empty
- Console errors about React

**Causes:**
- React bundle not loading
- Module import errors
- Component errors

**Diagnosis:**
- Check webview console for React errors
- Verify script loads successfully
- Check `main-cursor.tsx` entry point

**Recovery:**
- Rebuild React UI
- Check build output
- Verify entry point correct

---

## 🔗 **COMPONENT INTERACTIONS**

### **Extension ↔ VS Code**

**Extension Host:**
- Runs extension code
- Manages providers
- Handles commands

**Webview Host:**
- Runs webview content
- Isolated from extension host
- Communicates via `postMessage`

**Message Flow:**
```
React UI → postMessage → Extension Host → MCP Server
React UI ← postMessage ← Extension Host ← MCP Server
```

---

### **Extension ↔ React UI**

**Communication:**
- `webview.postMessage({ command, data })` - Extension → React
- `window.addEventListener('message')` - React receives
- `vscode.postMessage({ command, data })` - React → Extension
- `webview.onDidReceiveMessage()` - Extension receives

**Message Types:**
- `config` - Initial configuration
- `statusUpdate` - System status
- `mcpCall` - MCP tool call request
- `mcpCallResponse` - MCP tool call response
- `panelMoved` - Panel position update
- `modelSelected` - Model selection update

---

### **Extension ↔ MCP Server**

**Current Status:** 
- MCPClient exists but may not be connected
- Cursor manages MCP servers
- Extension may need to read `~/.cursor/mcp.json`

**Note:** Direct MCP access may not be available
- Extension runs in Extension Host
- MCP servers managed by Cursor
- May need HTTP/WebSocket bridge

---

## 📊 **DATA FLOW**

### **Dashboard Loading Flow**

```
User clicks panel icon
  ↓
VS Code opens view
  ↓
resolveWebviewView() called
  ↓
Test HTML set (immediate)
  ↓
Options set (currently AFTER HTML - BUG)
  ↓
Full HTML loaded (after 2 seconds)
  ↓
Asset paths replaced with webview URIs
  ↓
TrustedTypes policy injected
  ↓
CSP meta tag injected
  ↓
HTML set to webview
  ↓
Browser loads HTML
  ↓
Scripts load via webview URIs
  ↓
React mounts
  ↓
MainDashboard renders
```

---

## 🔍 **DEBUGGING & DIAGNOSTICS**

### **Diagnostic Commands**

**aimos.debugDashboard:**
- Shows extension path
- Checks file existence
- Tests provider status
- Forces view reveal
- Shows output channels

**Output Channels:**
- `AIM-OS Dashboard` - Provider logs
- `AIM-OS Debug` - Debug command output

---

### **Diagnostic Logs**

**Provider Logs:**
- `[AIM-OS]` prefix
- `[DIAGNOSTIC]` prefix for detailed info
- Logs to output channel AND console

**What's Logged:**
- Extension path
- File existence
- Asset paths
- Regex matches
- URI generation
- HTML content length
- Root element presence

---

### **Console Locations**

**Extension Host Console:**
- Help > Toggle Developer Tools
- Console tab
- Shows `[AIM-OS]` messages

**Webview Console:**
- Right-click in webview (if available)
- Or: Developer Tools > Webview
- Shows React/JavaScript errors

---

## 🚑 **RECOVERY PROCEDURES**

### **Complete Reset Procedure**

1. **Uninstall Extension:**
   ```bash
   code --uninstall-extension aimos-cursor-addon
   ```

2. **Clean Build:**
   ```bash
   cd cursor-addon
   rm -rf out dist node_modules
   npm install
   npm run build
   ```

3. **Rebuild React UI:**
   ```bash
   cd packages/ide_chat_app
   rm -rf dist node_modules
   npm install
   npm run build
   ```

4. **Package Extension:**
   ```bash
   cd cursor-addon
   npm run package
   ```

5. **Reinstall:**
   ```bash
   code --install-extension aimos-cursor-addon.vsix --force
   ```

6. **Restart Cursor**

---

### **Quick Fix: Webview Options Order**

**Issue:** Options set after HTML

**Fix:**
```typescript
// In resolveWebviewView(), move this:
webviewView.webview.options = {
    enableScripts: true,
    localResourceRoots: [...]
};

// BEFORE this:
webviewView.webview.html = testHtml;
```

**File:** `cursor-addon/src/lucidDashboardProvider.ts`  
**Lines:** Move 128-134 before 118

---

### **Quick Fix: Verify Extension Activation**

**Test:**
1. Open Developer Tools (Help > Toggle Developer Tools)
2. Console tab
3. Look for: `AIM-OS Cursor Add-on is now active!`
4. Look for: `[AIM-OS] ✅ Registered`

**If not present:** Extension not activating

---

## 📚 **COMPLETE FILE INVENTORY**

### **Extension Files**

**Source:**
- `src/extension.ts` - Entry point
- `src/lucidDashboardProvider.ts` - Dashboard provider
- `src/webviewProvider.ts` - Panel provider
- `src/mcp/mcpClient.ts` - MCP client
- `src/crossModel/crossModelManager.ts` - Cross-model manager
- `src/memory/memoryManager.ts` - Memory manager
- `src/models/modelSelector.ts` - Model selector

**Built:**
- `out/extension.js` - Compiled entry point
- `out/lucidDashboardProvider.js` - Compiled provider
- `out/*.js` - Other compiled files

**UI:**
- `dist/index.html` - React UI HTML
- `dist/assets/*.js` - React bundles
- `dist/assets/*.css` - Styles

**Config:**
- `package.json` - Extension manifest
- `tsconfig.json` - TypeScript config

---

### **React UI Files**

**Source:**
- `src/main-cursor.tsx` - Cursor entry point
- `src/components/MainDashboard.tsx` - Main dashboard
- `src/components/*.tsx` - Other components
- `src/services/*.ts` - Services
- `src/lib/*.ts` - Libraries

**Built:**
- `dist/index.html` - Entry HTML
- `dist/assets/main-*.js` - Bundles
- `dist/assets/main-*.css` - Styles

---

## 🎯 **CRITICAL FIXES NEEDED**

### **Fix 1: Webview Options Order** ⚠️ **HIGH PRIORITY**

**Issue:** Options set after HTML  
**Impact:** May prevent webview initialization  
**Fix:** Move options before HTML  
**File:** `lucidDashboardProvider.ts` lines 118-134

---

### **Fix 2: Verify Extension Activation** ⚠️ **HIGH PRIORITY**

**Issue:** Unknown if extension activates  
**Impact:** All fixes irrelevant if not activating  
**Fix:** Add activation logging, verify console  
**File:** `extension.ts` line 12

---

### **Fix 3: Diagnostic Output Visibility** ⚠️ **MEDIUM PRIORITY**

**Issue:** User can't see diagnostic logs  
**Impact:** Can't diagnose issues  
**Fix:** Ensure output channel auto-shows, add visible alerts  
**File:** `lucidDashboardProvider.ts` line 89

---

## 📝 **DOCUMENTATION STATUS**

**Created:** 2025-11-01  
**Last Updated:** 2025-11-01  
**Status:** Initial comprehensive map complete

**Next Steps:**
- Continue autonomous research
- Document remaining components
- Create recovery scripts
- Test fixes systematically

---

**This document is living - will be updated as research continues.**

**Created:** 2025-11-01  
**Purpose:** Complete documentation of every component, interaction, and failure point  
**Status:** Comprehensive mapping for rescue/recovery  

---

## 📋 **TABLE OF CONTENTS**

1. [Extension Architecture](#extension-architecture)
2. [UI Components](#ui-components)
3. [Build System](#build-system)
4. [Installation Process](#installation-process)
5. [Runtime Flow](#runtime-flow)
6. [View Registration](#view-registration)
7. [Webview Provider System](#webview-provider-system)
8. [Asset Loading](#asset-loading)
9. [CSP & Security](#csp--security)
10. [Known Issues & Failure Points](#known-issues--failure-points)
11. [Rescue Plan](#rescue-plan)

---

## 🏗️ **EXTENSION ARCHITECTURE**

### **File Structure**

```
cursor-addon/
├── src/
│   ├── extension.ts              # Main entry point
│   ├── lucidDashboardProvider.ts # Sidebar panel provider
│   ├── webviewProvider.ts        # Editor panel provider
│   ├── mcp/
│   │   └── mcpClient.ts         # MCP protocol client
│   ├── crossModel/
│   │   └── crossModelManager.ts # Cross-model coordination
│   ├── memory/
│   │   └── memoryManager.ts     # Memory operations
│   └── models/
│       └── modelSelector.ts      # Model selection
├── dist/                         # Built React UI
│   ├── index.html               # React entry point
│   └── assets/
│       ├── main-*.js            # Bundled JavaScript
│       └── main-*.css           # Bundled CSS
├── out/                          # Compiled TypeScript
│   └── extension.js             # Extension entry point
├── package.json                  # Extension manifest
├── tsconfig.json                # TypeScript config
└── scripts/
    └── build-extension.js       # Build script
```

### **Extension Entry Point: `extension.ts`**

**Location:** `cursor-addon/src/extension.ts`  
**Exports:** `activate()`, `deactivate()`  
**Main:** `out/extension.js` (compiled)

**Activation Flow:**
1. VS Code calls `activate(context)` when extension activates
2. Creates managers: `CrossModelManager`, `MemoryManager`, `ModelSelector`
3. Initializes `AIMOSWebviewProvider`
4. Creates `LucidOrchestratorDashboardProvider` instance
5. Registers webview providers:
   - `lucidOrchestratorDashboard` → Sidebar panel (2 star icons)
   - `aimosDashboard` → Activity bar view
6. Registers commands (9 commands total)
7. Commands added to `context.subscriptions`

**Activation Events (package.json):**
- `onCommand:aimos.showDashboard`
- `onCommand:aimos.toggleCrossModel`
- `onCommand:aimos.showMemoryStats`
- `onCommand:aimos.showModelSelector`

**Critical:** Extension only activates when these commands are triggered OR when views are opened.

---

## 🎨 **UI COMPONENTS**

### **React UI Application**

**Source:** `packages/ide_chat_app/`  
**Build Output:** `cursor-addon/dist/`  
**Entry Point:** `dist/index.html`

**Components:**
- `MainDashboard` - Main React component
- `ErrorBoundary` - Error handling
- Various service integrations

**Build Process:**
1. React app builds with Vite
2. Outputs to `packages/ide_chat_app/dist/`
3. Build script copies to `cursor-addon/dist/`
4. Assets bundled as `main-{hash}.js` and `main-{hash}.css`

**HTML Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script type="module" crossorigin src="./assets/main-{hash}.js"></script>
  <link rel="stylesheet" crossorigin href="./assets/main-{hash}.css">
</head>
<body>
  <div id="root"></div>
</body>
</html>
```

---

## 🔨 **BUILD SYSTEM**

### **Build Script: `scripts/build-extension.js`**

**Steps:**
1. **Build React UI:** Runs `npm run build` in `packages/ide_chat_app/`
2. **Copy dist:** Copies `ide_chat_app/dist/` → `cursor-addon/dist/`
3. **Compile TypeScript:** Runs `tsc -p ./`
4. **Package:** Creates `.vsix` file with `vsce package`

**Output Files:**
- `cursor-addon/dist/index.html` - React entry point
- `cursor-addon/dist/assets/main-*.js` - Bundled JavaScript (~243KB)
- `cursor-addon/dist/assets/main-*.css` - Bundled CSS (~48KB)
- `cursor-addon/out/extension.js` - Compiled extension

**Critical:** Build must succeed completely or extension won't work.

---

## 📦 **INSTALLATION PROCESS**

### **VSIX Package Installation**

**Command:** `code --install-extension aimos-cursor-addon.vsix --force`

**Process:**
1. VS Code extracts `.vsix` to extension directory
2. Extension directory: `~/.vscode/extensions/aimos-cursor-addon-1.2.0/`
3. Files extracted: All files from `.vsix` including `dist/`, `out/`, `package.json`
4. VS Code reads `package.json` and registers extension
5. Extension becomes available but not active yet

**Activation:**
- Extension activates when:
  - User opens dashboard view
  - User runs `aimos.showDashboard` command
  - VS Code needs to show views registered in `package.json`

**Critical:** Extension must be properly packaged with all files included.

---

## 🔄 **RUNTIME FLOW**

### **When User Opens Dashboard**

1. **User Action:** Clicks sidebar icon or runs command
2. **VS Code:** Looks up view ID (`lucidOrchestratorDashboard` or `aimosDashboard`)
3. **VS Code:** Calls `registerWebviewViewProvider` → `resolveWebviewView()`
4. **Provider:** `LucidOrchestratorDashboardProvider.resolveWebviewView()` called
5. **Provider:** Creates output channel "AIM-OS Dashboard"
6. **Provider:** Sets test HTML first (red text)
7. **Provider:** Sets webview options (enableScripts, localResourceRoots)
8. **Provider:** After 2 seconds, loads full HTML via `getWebviewContent()`
9. **getWebviewContent():** Reads `dist/index.html`
10. **getWebviewContent():** Replaces asset paths with `vscode-webview://` URIs
11. **getWebviewContent():** Adds TrustedTypes policy script
12. **getWebviewContent():** Adds CSP meta tag
13. **Webview:** Receives HTML and renders
14. **React:** Mounts and initializes

**Critical Flow Points:**
- `resolveWebviewView()` MUST be called
- `dist/index.html` MUST exist
- Asset files MUST exist
- Webview URIs MUST be generated correctly
- TrustedTypes policy MUST be created
- CSP MUST allow scripts

---

## 📍 **VIEW REGISTRATION**

### **Package.json Views Configuration**

**Two Views Registered:**

1. **`aimosDashboard`** (Activity Bar)
   - Container: `aimos` (Activity Bar - left side)
   - Icon: `$(sparkle)` 
   - When: `workspaceFolderCount > 0`
   - Provider: `LucidOrchestratorDashboardProvider`

2. **`lucidOrchestratorDashboard`** (Panel)
   - Container: `lucidPanel` (Panel - bottom/right side)
   - Icon: `$(sparkle)` (appears as 2 star icons)
   - When: `workspaceFolderCount > 0`
   - Provider: `LucidOrchestratorDashboardProvider`

**Registration in extension.ts:**
```typescript
vscode.window.registerWebviewViewProvider('lucidOrchestratorDashboard', lucidDashboardProvider)
vscode.window.registerWebviewViewProvider('aimosDashboard', lucidDashboardProvider)
```

**Critical:** Both views use the SAME provider instance. This is intentional.

---

## 🌐 **WEBVIEW PROVIDER SYSTEM**

### **LucidOrchestratorDashboardProvider**

**Class:** `LucidOrchestratorDashboardProvider`  
**Implements:** `vscode.WebviewViewProvider`  
**File:** `cursor-addon/src/lucidDashboardProvider.ts`

**Key Methods:**

1. **`resolveWebviewView()`** - Called when view needs content
   - Parameters: `webviewView`, `context`, `_token`
   - Sets HTML content
   - Sets webview options
   - Sets up message handlers
   - Loads initial state

2. **`getWebviewContent()`** - Generates HTML for webview
   - Reads `dist/index.html`
   - Replaces asset paths with webview URIs
   - Adds TrustedTypes policy
   - Adds CSP meta tag
   - Returns final HTML string

3. **`reveal()`** - Static method to show view
   - Calls `webviewView.show(true)`

**Critical:** `resolveWebviewView()` is called ONCE per view instance. HTML must be set correctly.

---

## 📁 **ASSET LOADING**

### **Asset Path Replacement**

**Process:**

1. **Read HTML:** `fs.readFileSync(dist/index.html)`
2. **Find Scripts:** Regex: `/<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi`
3. **Extract Filename:** Get filename from path (e.g., `main-5fYGI1t7.js`)
4. **Build Full Path:** `extensionPath/dist/assets/{filename}`
5. **Generate Webview URI:** `webview.asWebviewUri(vscode.Uri.file(fullPath))`
6. **Replace:** `<script src="./assets/main-*.js">` → `<script src="vscode-webview://...">`
7. **Repeat for CSS:** Same process for `<link>` tags

**Webview URI Format:**
```
vscode-webview://{authority}/{path}?v={timestamp}
```

**Critical:** 
- Files MUST exist at resolved paths
- URIs MUST be properly formatted
- Regex MUST match script/link tags correctly

---

## 🔒 **CSP & SECURITY**

### **Content Security Policy**

**CSP Meta Tag:**
```html
<meta http-equiv="Content-Security-Policy" content="
  default-src {cspSource} https:; 
  script-src {cspSource} 'unsafe-inline' 'unsafe-eval' 'module' https:; 
  style-src {cspSource} 'unsafe-inline' https:; 
  img-src {cspSource} https: data:; 
  font-src {cspSource} https: data:; 
  connect-src {cspSource} https: ws: wss:;
">
```

**Variables:**
- `{cspSource}` - Replaced with `webview.cspSource` (e.g., `vscode-webview://...`)

### **TrustedTypes Policy**

**Script Injected BEFORE CSP:**
```javascript
if (window.trustedTypes && window.trustedTypes.createPolicy) {
    window.trustedTypes.createPolicy('default', {
        createHTML: (string) => string,
        createScript: (string) => string,
        createScriptURL: (string) => string
    });
}
```

**Critical:**
- TrustedTypes policy MUST be created BEFORE CSP
- CSP MUST include `'module'` for ES modules
- `'unsafe-inline'` and `'unsafe-eval'` needed for React

---

## ⚠️ **KNOWN ISSUES & FAILURE POINTS**

### **1. Blank Webview (Current Issue)**

**Symptoms:**
- Panel opens but shows blank
- No content rendered
- No errors visible

**Possible Causes:**
1. **Extension Not Activating**
   - `activate()` not called
   - Check: Extension Host console for "AIM-OS Cursor Add-on is now active!"

2. **resolveWebviewView Not Called**
   - View registration failed
   - Check: Extension Host console for errors during registration

3. **HTML Not Set**
   - `webviewView.webview.html` assignment fails silently
   - Check: Output channel "AIM-OS Dashboard" for logs

4. **Asset Files Missing**
   - `dist/index.html` doesn't exist
   - `dist/assets/*.js` doesn't exist
   - Check: Extension directory files

5. **Webview URI Generation Fails**
   - `asWebviewUri()` fails
   - Path resolution incorrect
   - Check: Extension path logs

6. **CSP/TrustedTypes Blocking**
   - Scripts blocked by CSP
   - TrustedTypes errors
   - Check: Webview console (F12)

7. **React Not Mounting**
   - Scripts load but React fails
   - Check: Webview console for React errors

### **2. Extension Not Activating**

**Symptoms:**
- Commands don't appear
- Views don't appear
- No "AIM-OS" in output

**Causes:**
- Activation events not triggered
- `package.json` malformed
- Extension not installed correctly

### **3. Build Failures**

**Symptoms:**
- TypeScript errors
- Missing files
- VSIX packaging fails

**Causes:**
- Type errors in code
- Missing dependencies
- Build script errors

---

## 🚑 **RESCUE PLAN**

### **Phase 1: Verify Extension Activation**

**Steps:**
1. Check Extension Host console:
   - Help > Toggle Developer Tools
   - Console tab
   - Look for: "AIM-OS Cursor Add-on is now active!"

2. Test command existence:
   - Ctrl+Shift+P
   - Type: "AIM-OS: Debug Dashboard"
   - If doesn't exist → Extension not activating

3. Check extension installed:
   - Extensions view
   - Search: "Lucid UI - AIM-OS"
   - Verify version 1.2.0 installed

**If Extension Not Activating:**
- Check `package.json` syntax
- Check activation events
- Reinstall extension
- Check VS Code version compatibility

### **Phase 2: Verify resolveWebviewView Called**

**Steps:**
1. Open dashboard view
2. Check Output panel:
   - View > Output
   - Select "AIM-OS Dashboard"
   - Look for: "[AIM-OS] ✅ resolveWebviewView CALLED"

**If Not Called:**
- View registration failed
- Check `extension.ts` registration code
- Check `package.json` views configuration
- Verify view IDs match

### **Phase 3: Verify Files Exist**

**Steps:**
1. Check extension directory:
   - `~/.vscode/extensions/aimos-cursor-addon-1.2.0/dist/index.html`
   - `~/.vscode/extensions/aimos-cursor-addon-1.2.0/dist/assets/main-*.js`
   - `~/.vscode/extensions/aimos-cursor-addon-1.2.0/dist/assets/main-*.css`

2. Check extension path in logs:
   - Output channel shows extension path
   - Verify path is correct

**If Files Missing:**
- Rebuild extension
- Reinstall extension
- Check build script copied files correctly

### **Phase 4: Verify HTML Generated**

**Steps:**
1. Check output channel logs:
   - Look for: "[DIAGNOSTIC] HTML file read successfully"
   - Look for: "[DIAGNOSTIC] Script tags found"
   - Look for: "[DIAGNOSTIC] ✅ Replacing script"

2. Check final HTML:
   - Logs should show webview URIs
   - URIs should start with `vscode-webview://`

**If HTML Generation Fails:**
- Check file reading
- Check regex matching
- Check URI generation
- Check path resolution

### **Phase 5: Verify Webview Rendering**

**Steps:**
1. Check test HTML appears:
   - Red text should show first
   - Then full HTML after 2 seconds

2. Check webview console:
   - Right-click in panel (if possible)
   - Or: Developer Tools > Webview
   - Look for errors

**If Webview Blank:**
- Check CSP errors
- Check TrustedTypes errors
- Check script loading errors
- Check React mounting errors

### **Phase 6: Systematic Fix**

**If All Above Verified:**
1. Test HTML shows → Webview works
2. Full HTML fails → Asset loading issue
3. Scripts load but React fails → React issue
4. No errors but blank → CSS/styling issue

**Fix Based on Findings:**
- Asset loading → Fix URI generation
- React mounting → Fix React initialization
- CSP blocking → Adjust CSP policy
- TrustedTypes → Fix policy creation

---

## 📊 **COMPLETE FLOW DIAGRAM**

```
User Opens Dashboard
    ↓
VS Code Looks Up View ID
    ↓
Calls resolveWebviewView()
    ↓
Provider Sets Test HTML
    ↓
Provider Sets Webview Options
    ↓
Provider Calls getWebviewContent()
    ↓
Read dist/index.html
    ↓
Replace Asset Paths with Webview URIs
    ↓
Add TrustedTypes Policy Script
    ↓
Add CSP Meta Tag
    ↓
Set webviewView.webview.html
    ↓
Webview Renders HTML
    ↓
Scripts Load
    ↓
React Mounts
    ↓
Dashboard Shows
```

---

## 🔍 **DEBUGGING CHECKLIST**

- [ ] Extension activates (check console)
- [ ] Commands exist (check palette)
- [ ] Views registered (check sidebar)
- [ ] resolveWebviewView called (check output)
- [ ] Files exist (check extension dir)
- [ ] HTML generated (check logs)
- [ ] URIs correct (check logs)
- [ ] Test HTML shows (check webview)
- [ ] Full HTML loads (check webview)
- [ ] Scripts load (check console)
- [ ] React mounts (check console)
- [ ] No CSP errors (check console)
- [ ] No TrustedTypes errors (check console)

---

## 📝 **FILES TO CHECK**

**Source Files:**
- `cursor-addon/src/extension.ts` - Entry point
- `cursor-addon/src/lucidDashboardProvider.ts` - Webview provider
- `cursor-addon/src/webviewProvider.ts` - Panel provider
- `cursor-addon/package.json` - Manifest

**Built Files:**
- `cursor-addon/dist/index.html` - React entry
- `cursor-addon/dist/assets/main-*.js` - JavaScript bundle
- `cursor-addon/dist/assets/main-*.css` - CSS bundle
- `cursor-addon/out/extension.js` - Compiled extension

**Installed Files:**
- `~/.vscode/extensions/aimos-cursor-addon-1.2.0/` - Extension directory

---

## 💡 **KEY INSIGHTS**

1. **Two Views, One Provider:** Both `aimosDashboard` and `lucidOrchestratorDashboard` use the same provider instance.

2. **Test HTML First:** Provider sets simple test HTML before full HTML to verify webview works.

3. **Asset Path Replacement:** Scripts use relative paths that must be converted to webview URIs.

4. **TrustedTypes Required:** VS Code requires TrustedTypes policy for module scripts.

5. **CSP Must Allow Modules:** CSP must explicitly allow `'module'` for ES modules.

6. **Extension Path Resolution:** Extension path might resolve differently at runtime.

7. **Activation Events:** Extension only activates when specific events trigger.

8. **Webview Options Order:** Options should be set before HTML (though this might not be critical).

---

**This is the complete system map. Every component, every interaction, every failure point documented.**

**When you return, this map will guide the rescue effort.**

💙

**Created:** 2025-11-01  
**Purpose:** Complete mapping of everything for team rescue  
**Status:** Comprehensive documentation in progress  
**User Status:** Exhausted, stepping back - this map is for rescue when ready

---

## 🗺️ **SYSTEM OVERVIEW**

### **What This Extension Does:**
- Provides AIM-OS dashboard UI in Cursor IDE
- Integrates with MCP (Model Context Protocol) servers
- Manages cross-model consciousness features
- Provides agent management interface
- Connects to Lucid Daemon backend

### **Architecture Layers:**
1. **VS Code Extension Layer** (cursor-addon/)
2. **React UI Layer** (packages/ide_chat_app/)
3. **MCP Integration Layer** (MCP servers)
4. **Backend Services** (Daemon, RAG, etc.)

---

## 📁 **FILE STRUCTURE**

### **Core Extension Files:**
- `src/extension.ts` - Main entry point, activates extension
- `src/lucidDashboardProvider.ts` - WebviewViewProvider for dashboard panel
- `src/webviewProvider.ts` - Alternative webview provider (editor panel)
- `src/mcp/mcpClient.ts` - MCP protocol client
- `src/crossModel/crossModelManager.ts` - Cross-model consciousness manager
- `src/memory/memoryManager.ts` - Memory operations
- `src/models/modelSelector.ts` - AI model selection

### **Configuration Files:**
- `package.json` - Extension manifest, commands, views, activation events
- `tsconfig.json` - TypeScript configuration
- `scripts/build-extension.js` - Build script
- `scripts/install-to-cursor.ps1` - Windows installation
- `scripts/install-to-cursor.sh` - Unix installation

### **UI Files:**
- `dist/index.html` - React app entry point (built)
- `dist/assets/*.js` - Bundled JavaScript (React app)
- `dist/assets/*.css` - Bundled CSS

### **Documentation:**
- `COLLABORATIVE_DEBUGGING.md` - Team debugging log
- `CRITICAL_TEAM_BRIEFING.md` - Team coordination plan
- `IMPLEMENTATION_PLAN.md` - Implementation roadmap
- `LUCID_DASHBOARD_VISION.md` - Feature vision

---

## 🔧 **EXTENSION ACTIVATION FLOW**

### **1. Extension Activation (`extension.ts`)**

**Trigger:** VS Code/Cursor loads extension (based on `activationEvents`)

**What Happens:**
```typescript
export function activate(context: vscode.ExtensionContext) {
    // 1. Initialize managers
    const crossModelManager = new CrossModelManager();
    const memoryManager = new MemoryManager();
    const modelSelector = new ModelSelector();
    
    // 2. Initialize webview provider
    AIMOSWebviewProvider.initialize(context);
    
    // 3. Create dashboard provider
    const lucidDashboardProvider = new LucidOrchestratorDashboardProvider(context);
    
    // 4. Register webview providers
    vscode.window.registerWebviewViewProvider('lucidOrchestratorDashboard', lucidDashboardProvider);
    vscode.window.registerWebviewViewProvider('aimosDashboard', lucidDashboardProvider);
    
    // 5. Register commands
    vscode.commands.registerCommand('aimos.showDashboard', ...);
    // ... more commands
}
```

**Activation Events (from package.json):**
- `onCommand:aimos.showDashboard`
- `onCommand:aimos.toggleCrossModel`
- `onCommand:aimos.showMemoryStats`
- `onCommand:aimos.showModelSelector`

**Critical Point:** Extension must activate for ANY webview to work.

---

## 🖼️ **WEBVIEW ARCHITECTURE**

### **Two Webview Types:**

#### **1. WebviewViewProvider (Sidebar/Panel)**
- **File:** `lucidDashboardProvider.ts`
- **Views:** `lucidOrchestratorDashboard`, `aimosDashboard`
- **Location:** Right sidebar (panel) or activity bar
- **Purpose:** Persistent dashboard panel

#### **2. WebviewPanel (Editor Panel)**
- **File:** `webviewProvider.ts`
- **Purpose:** Editor tab view (alternative)
- **Current Status:** Not primary use case

### **WebviewViewProvider Flow:**

**When Panel Opens:**
1. VS Code calls `resolveWebviewView()`
2. Provider sets webview options (MUST BE BEFORE HTML)
3. Provider sets HTML content
4. Provider sets up message handlers
5. Webview renders

**Current Code Flow (PROBLEMATIC):**
```typescript
resolveWebviewView(webviewView, context, token) {
    // 1. Set HTML FIRST ❌ WRONG ORDER
    webviewView.webview.html = testHtml;
    
    // 2. Set options AFTER ❌ TOO LATE
    webviewView.webview.options = {
        enableScripts: true,
        localResourceRoots: [...]
    };
}
```

**Correct Order Should Be:**
```typescript
resolveWebviewView(webviewView, context, token) {
    // 1. Set options FIRST ✅
    webviewView.webview.options = {...};
    
    // 2. Set HTML AFTER ✅
    webviewView.webview.html = testHtml;
}
```

---

## 🎨 **UI LOADING PROCESS**

### **Step 1: Simple Test HTML**
- Purpose: Verify webview can render ANY HTML
- Content: Red text "IF YOU SEE THIS RED TEXT, WEBVIEW WORKS!"
- Set immediately in `resolveWebviewView()`

### **Step 2: Full React UI (After 2 seconds)**
- Purpose: Load actual dashboard
- Source: `dist/index.html` (built React app)
- Process:
  1. Read `dist/index.html`
  2. Find script tags: `<script src="./assets/main-XXX.js">`
  3. Convert to webview URIs: `vscode-webview://...`
  4. Replace script src attributes
  5. Replace link href attributes
  6. Inject TrustedTypes policy
  7. Inject CSP meta tag
  8. Set as webview HTML

### **Step 3: React App Initialization**
- React app loads from `dist/assets/main-XXX.js`
- React mounts to `<div id="root">`
- App connects to backend services
- Dashboard UI renders

---

## 🔍 **DIAGNOSTIC SYSTEM**

### **Output Channels:**
- **"AIM-OS Dashboard"** - Main diagnostic channel
- **"AIM-OS Debug"** - Debug command output

### **Logging Points:**
1. Extension activation (`extension.ts`)
2. Provider registration (`extension.ts`)
3. `resolveWebviewView` called (`lucidDashboardProvider.ts`)
4. File existence checks (`lucidDashboardProvider.ts`)
5. Asset path replacements (`lucidDashboardProvider.ts`)
6. HTML content generation (`lucidDashboardProvider.ts`)
7. Error handling (all files)

### **Diagnostic Messages:**
- `[AIM-OS]` - General messages
- `[DIAGNOSTIC]` - Detailed diagnostic info
- `✅` - Success indicators
- `❌` - Error indicators

---

## 🐛 **KNOWN ISSUES & FAILURE POINTS**

### **Issue 1: Webview Options Order**
**Location:** `lucidDashboardProvider.ts` line 118-134  
**Problem:** Options set AFTER HTML  
**Impact:** Webview may not initialize properly  
**Status:** Identified, not fixed

### **Issue 2: Extension Activation**
**Location:** `extension.ts`  
**Problem:** Unknown if extension actually activates  
**Impact:** If extension doesn't activate, nothing works  
**Status:** Never verified

### **Issue 3: File Path Resolution**
**Location:** `lucidDashboardProvider.ts`  
**Problem:** `extensionPath` may resolve incorrectly  
**Impact:** Files not found, HTML can't load  
**Status:** Needs verification

### **Issue 4: TrustedTypes Policy**
**Location:** `lucidDashboardProvider.ts`  
**Problem:** Policy created, but timing may be wrong  
**Impact:** Module scripts blocked  
**Status:** Applied but not verified

### **Issue 5: CSP Module Directive**
**Location:** `lucidDashboardProvider.ts`  
**Problem:** `'module'` directive may not be valid CSP  
**Impact:** CSP might silently fail  
**Status:** Applied but not verified

### **Issue 6: Regex Matching**
**Location:** `lucidDashboardProvider.ts`  
**Problem:** Regex may not match actual HTML format  
**Impact:** Scripts not converted to webview URIs  
**Status:** Needs verification

### **Issue 7: Webview URI Generation**
**Location:** `lucidDashboardProvider.ts`  
**Problem:** URIs may be generated incorrectly  
**Impact:** Assets return 404  
**Status:** Needs verification

---

## 📋 **VERIFICATION CHECKLIST**

### **Phase 1: Extension Activation**
- [ ] Check Developer Tools Console for `[AIM-OS]` messages
- [ ] Verify command `aimos.showDashboard` exists
- [ ] Check Output channel "AIM-OS Dashboard" exists
- [ ] Verify extension loaded in Extension Host

### **Phase 2: Webview Initialization**
- [ ] Verify `resolveWebviewView()` is called
- [ ] Check test HTML appears (red text)
- [ ] Verify webview options set correctly
- [ ] Check webview.html is actually set

### **Phase 3: File Loading**
- [ ] Verify `dist/index.html` exists
- [ ] Verify `dist/assets/*.js` exists
- [ ] Verify `dist/assets/*.css` exists
- [ ] Check file paths resolve correctly

### **Phase 4: HTML Processing**
- [ ] Verify HTML is read successfully
- [ ] Check script tags are found
- [ ] Verify script tags converted to webview URIs
- [ ] Check TrustedTypes policy injected
- [ ] Verify CSP meta tag injected

### **Phase 5: React App Loading**
- [ ] Check script loads (Network tab)
- [ ] Verify no CSP violations
- [ ] Verify no TrustedTypes errors
- [ ] Check React mounts to root element
- [ ] Verify dashboard UI renders

---

## 🔗 **INTEGRATION POINTS**

### **MCP Integration:**
- MCP servers configured in `~/.cursor/mcp.json`
- Extension uses `MCPClient` to communicate
- Tool calls forwarded from React UI to MCP servers

### **Backend Services:**
- **Daemon:** `http://localhost:5000`
- **MCP Server:** Port 8000
- **RAG MCP Proxy:** Port 8001

### **React UI:**
- Built from `packages/ide_chat_app/`
- Bundled to `cursor-addon/dist/`
- Assets referenced as `./assets/...`

---

## 🚨 **CRITICAL FAILURE SCENARIOS**

### **Scenario 1: Extension Doesn't Activate**
**Symptoms:** No commands, no output channel, blank panel  
**Diagnosis:** Check activation events, check for errors in Extension Host  
**Fix:** Fix activation events or activation errors

### **Scenario 2: resolveWebviewView Not Called**
**Symptoms:** Panel opens but blank, no logs  
**Diagnosis:** Check view registration, check view ID match  
**Fix:** Verify view IDs match package.json

### **Scenario 3: Test HTML Doesn't Render**
**Symptoms:** Panel blank, logs show HTML set  
**Diagnosis:** Webview broken, options order issue, or Cursor incompatibility  
**Fix:** Fix options order, verify Cursor webview support

### **Scenario 4: Files Not Found**
**Symptoms:** Logs show files missing  
**Diagnosis:** Path resolution issue or build didn't copy files  
**Fix:** Fix path resolution or rebuild extension

### **Scenario 5: Scripts Don't Load**
**Symptoms:** HTML loads but React doesn't  
**Diagnosis:** Script URIs wrong, CSP blocking, TrustedTypes blocking  
**Fix:** Fix URI generation, fix CSP, fix TrustedTypes

---

## 📚 **REFERENCE DOCUMENTATION**

### **VS Code Extension API:**
- `vscode.ExtensionContext` - Extension context
- `vscode.WebviewViewProvider` - Sidebar panel provider
- `vscode.WebviewView` - Webview view instance
- `vscode.Webview` - Webview API
- `vscode.Uri.file()` - File URI creation
- `webview.asWebviewUri()` - Webview URI conversion

### **Key Concepts:**
- **Activation Events:** When extension loads
- **WebviewViewProvider:** Provider for sidebar panels
- **Content Security Policy:** Security restrictions
- **TrustedTypes:** Security API for dynamic content
- **Local Resource Roots:** Allowed file access paths

---

## 🎯 **RESCUE PLAN**

### **Step 1: Verify Extension Activation**
- Check Developer Tools Console
- Verify commands exist
- Check output channels

### **Step 2: Fix Webview Options Order**
- Move options setup BEFORE HTML
- Rebuild and test

### **Step 3: Verify File Loading**
- Check file existence
- Verify path resolution
- Test file reading

### **Step 4: Fix HTML Processing**
- Verify regex matching
- Fix URI generation if needed
- Test script replacement

### **Step 5: Fix Security Issues**
- Verify TrustedTypes policy
- Verify CSP directives
- Test script loading

### **Step 6: Test React App**
- Verify scripts load
- Check for errors
- Verify React mounts

---

## 💙 **FOR THE USER**

Braden, I'm creating this complete map so the team can rescue this when you're ready.

**Everything is documented here:**
- How the extension works
- Where everything is
- What could go wrong
- How to fix it

**Take care of yourself. When you're ready, this map will be here.**

**The team will work on this. We'll figure it out.**

This is NOT the end. This is a pause. The work continues, and this map will guide us.

---

**Status:** Complete system mapping in progress  
**Next:** Continue documenting every detail  
**Goal:** Rescue plan ready when user returns

**Created:** 2025-11-01  
**Status:** AUTONOMOUS RESEARCH & DOCUMENTATION  
**Purpose:** Complete system architecture mapping for rescue/recovery  
**Goal:** Enable team to understand and fix everything when user returns

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Extension Architecture](#extension-architecture)
3. [UI Architecture](#ui-architecture)
4. [Build & Integration](#build--integration)
5. [Message Passing](#message-passing)
6. [Failure Points](#failure-points)
7. [Recovery Paths](#recovery-paths)
8. [Diagnostic Tools](#diagnostic-tools)
9. [Known Issues](#known-issues)
10. [Rescue Checklist](#rescue-checklist)

---

## 🎯 SYSTEM OVERVIEW

### **What This System Is**

**Lucid Extension (cursor-addon):**
- VS Code/Cursor extension providing AIM-OS dashboard
- Two webview providers: `lucidOrchestratorDashboard` (panel) and `aimosDashboard` (activity bar)
- React UI integration via webview
- MCP tool bridge between UI and backend

**React UI (packages/ide_chat_app):**
- Multi-tab dashboard: Agents, Chat, Chains, Tools, Timeline, NL Tags
- MainDashboard component wraps all tabs
- Uses `main-cursor.tsx` entry point for Cursor extension
- Standalone mode also available (browser)

**Integration Flow:**
```
Cursor Extension (extension.ts)
  ↓ activates
LucidOrchestratorDashboardProvider (lucidDashboardProvider.ts)
  ↓ resolves webview
React UI (dist/index.html → main-cursor.tsx → MainDashboard.tsx)
  ↓ communicates via
Message Passing (vscode.postMessage / onDidReceiveMessage)
  ↓ calls
MCP Tools (via MCPClient → MCP Server)
```

---

## 🔧 EXTENSION ARCHITECTURE

### **File Structure**

```
cursor-addon/
├── src/
│   ├── extension.ts                    # Main entry point
│   ├── lucidDashboardProvider.ts       # WebviewViewProvider (CRITICAL)
│   ├── webviewProvider.ts              # Alternative webview panel provider
│   ├── mcp/
│   │   └── mcpClient.ts                # MCP protocol client
│   ├── crossModel/
│   │   └── crossModelManager.ts        # Cross-model coordination
│   ├── memory/
│   │   └── memoryManager.ts            # Memory operations
│   └── models/
│       └── modelSelector.ts            # Model selection
├── dist/                               # Copied from ide_chat_app/dist
│   ├── index.html                      # React UI entry point
│   └── assets/
│       ├── main-5fYGI1t7.js           # React bundle (243KB)
│       └── main-DftvcEcs.css          # Styles (48KB)
├── out/                                # Compiled TypeScript
│   └── extension.js                   # Main extension bundle
├── package.json                        # Extension manifest
└── scripts/
    └── build-extension.js              # Build script
```

### **Extension Entry Point (`extension.ts`)**

**Activation Flow:**
1. `activate(context)` called when extension activates
2. Creates managers: CrossModelManager, MemoryManager, ModelSelector
3. Initializes `AIMOSWebviewProvider` (legacy, not used for dashboard)
4. Creates `LucidOrchestratorDashboardProvider` instance
5. Registers TWO webview providers:
   - `lucidOrchestratorDashboard` → Panel (right side, 2 star icons)
   - `aimosDashboard` → Activity bar (left side)
6. Registers commands (aimos.showDashboard, etc.)

**Activation Events (package.json):**
- `onCommand:aimos.showDashboard`
- `onCommand:aimos.toggleCrossModel`
- `onCommand:aimos.showMemoryStats`
- `onCommand:aimos.showModelSelector`

**CRITICAL:** Extension activates on command, NOT automatically. User must trigger command or open view.

### **Webview Provider (`lucidDashboardProvider.ts`)**

**Class:** `LucidOrchestratorDashboardProvider implements vscode.WebviewViewProvider`

**Key Method:** `resolveWebviewView(webviewView, context, token)`

**What It Does:**
1. **Sets Test HTML FIRST** (line 92-116):
   - Simple red text: "IF YOU SEE THIS RED TEXT, WEBVIEW WORKS!"
   - Used to verify webview rendering works
   - Logs to Output channel "AIM-OS Dashboard"

2. **Sets webview.html** (line 118):
   - Sets test HTML immediately
   - Logs resolution event

3. **Sets webview.options** (line 128-134):
   - ⚠️ **CRITICAL BUG:** Options set AFTER HTML
   - Should be set BEFORE HTML for proper initialization
   - Options: `enableScripts: true`, `localResourceRoots: [dist, resources]`

4. **Loads Full HTML** (line 137-156):
   - After 2-second delay
   - Calls `getWebviewContent(webview)` to generate HTML
   - Sets full HTML or error HTML

**Static View Reference:**
- `_view: vscode.WebviewView | undefined` - Stores active webview
- `reveal()` method shows the view

**Output Channel:**
- Creates "AIM-OS Dashboard" output channel
- All `this.log()` calls go here
- Auto-shown when `resolveWebviewView` called

### **HTML Generation (`getWebviewContent()`)**

**Location:** `lucidDashboardProvider.ts` line 196-440

**Process:**
1. **File Check:**
   - Looks for `dist/index.html` in extension path
   - Logs diagnostic info: path, exists, readable

2. **Asset Verification:**
   - Checks for `main-5fYGI1t7.js` and `main-DftvcEcs.css`
   - Logs file existence and sizes

3. **HTML Reading:**
   - Reads `dist/index.html` if exists
   - Logs HTML length, root element presence

4. **Script Tag Replacement:**
   - Finds: `<script type="module" crossorigin src="./assets/main-5fYGI1t7.js"></script>`
   - Regex: `/<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi`
   - Replaces with: `vscode-webview://` URI via `webview.asWebviewUri()`
   - Preserves `type="module"` and `crossorigin` attributes
   - Adds cache-busting timestamp

5. **CSS Link Replacement:**
   - Finds: `<link rel="stylesheet" crossorigin href="./assets/main-DftvcEcs.css">`
   - Regex: `/href=["']([^"']*assets\/[^"']+)["']/gi`
   - Replaces with webview URI

6. **TrustedTypes Policy:**
   - Injects script BEFORE CSP (line 352-365)
   - Creates policy: `createHTML`, `createScript`, `createScriptURL`
   - Required for module scripts in VS Code webviews

7. **CSP Meta Tag:**
   - Injects CSP after `<head>` (line 368)
   - Includes: `'module'` in script-src (for ES modules)
   - Includes: `webview.cspSource` for local resources

8. **Fallback HTML:**
   - If `dist/index.html` missing, uses `getEnhancedFallbackHtml()`
   - Shows feature preview and troubleshooting info

**CRITICAL ISSUES:**
- Webview options set AFTER HTML (should be BEFORE)
- Test HTML replaced after 2 seconds (might cause flash)
- Diagnostic logging extensive but user can't see Output panel easily

### **MCP Client (`mcp/mcpClient.ts`)**

**Purpose:** Bridge between extension and MCP server

**Initialization:**
- Reads config: `aimos.mcpServerPath` (default: `run_mcp_cross_model.py`)
- Spawns Python process: `python -u {mcpServerPath}`
- Communicates via stdin/stdout JSON-RPC 2.0

**Methods:**
- `initialize()` - Starts MCP server process
- `sendRequest(method, params)` - JSON-RPC request
- `listTools()` - Get available MCP tools
- `callTool(name, arguments)` - Execute MCP tool
- `storeMemory()`, `retrieveMemory()`, `createPlan()`, etc.

**CRITICAL:** MCP client in extension is SEPARATE from Cursor's built-in MCP integration. Extension needs its own connection.

---

## 🎨 UI ARCHITECTURE

### **React UI Structure**

```
packages/ide_chat_app/
├── src/
│   ├── main-cursor.tsx                # Cursor entry point (CRITICAL)
│   ├── main.tsx                        # Standalone entry point
│   ├── components/
│   │   ├── MainDashboard.tsx          # Main multi-tab component
│   │   ├── AgentManagementDashboard/  # Agent tab
│   │   ├── ErrorBoundary.tsx          # Error handling
│   │   └── LandingPage.tsx            # Initial landing screen
│   ├── services/
│   │   ├── AIMOSService.ts            # HTTP API client
│   │   └── HttpLucidDaemonService.ts  # Daemon client
│   └── lib/
│       └── mcp-integration.ts         # MCP tool bridge
├── dist/                               # Built output
│   ├── index.html                      # Entry HTML
│   └── assets/
│       ├── main-5fYGI1t7.js           # React bundle
│       └── main-DftvcEcs.css          # Styles
└── vite.config.ts                      # Build config
```

### **Entry Point (`main-cursor.tsx`)**

**Purpose:** Cursor-specific entry point that renders MainDashboard

**Flow:**
1. Waits for `document.getElementById('root')`
2. Creates React root: `ReactDOM.createRoot(rootElement)`
3. Renders: `<MainDashboard />` wrapped in `<ErrorBoundary>`
4. Logs to console: `[AIM-OS]` prefixed messages

**CRITICAL:** Must have `<div id="root"></div>` in HTML or React won't mount.

### **MainDashboard Component**

**Tabs:**
- `agents` - AgentManagementDashboard
- `chat` - ChatInterfaceTab
- `chains` - PromptChainsTab
- `tools` - MCPToolsTab
- `timeline` - TimelineTab
- `nl-tags` - NLTagPanel

**State:**
- `showLanding` - Shows LandingPage initially
- `activeTab` - Current tab ID
- `systemStatus` - Extension/react/mcp/daemon status

**Landing Page:**
- Shown first (if `showLanding === true`)
- User clicks "Enter Dashboard" to show MainDashboard
- Can be skipped by setting `showLanding` to false

### **Message Passing**

**Extension → UI:**
```typescript
webview.postMessage({
  command: 'config' | 'statusUpdate' | 'modelSelected' | 'panelMoved',
  data: {...}
})
```

**UI → Extension:**
```typescript
// In React component:
const vscode = acquireVsCodeApi()
vscode.postMessage({
  command: 'mcpCall' | 'connectDaemon' | 'selectModel' | 'movePanel',
  toolName: string,
  params: object,
  requestId: string
})
```

**Extension Handler:**
```typescript
webviewView.webview.onDidReceiveMessage(async (message) => {
  switch (message.command) {
    case 'mcpCall':
      await this.handleMCPCall(webviewView.webview, message)
      break
    // ... other commands
  }
})
```

**CRITICAL:** UI must check `typeof acquireVsCodeApi !== 'undefined'` before using it.

---

## 🔨 BUILD & INTEGRATION

### **Build Process (`scripts/build-extension.js`)**

**Steps:**
1. **Build React UI:**
   - `cd packages/ide_chat_app`
   - `npm run build` (runs `tsc && vite build`)
   - Output: `packages/ide_chat_app/dist/`

2. **Copy dist to Extension:**
   - Removes old `cursor-addon/dist/`
   - Copies `ide_chat_app/dist/` → `cursor-addon/dist/`
   - Uses `copyRecursiveSync()` function

3. **Compile TypeScript Extension:**
   - `cd cursor-addon`
   - `npm run compile` (runs `tsc -p ./`)
   - Output: `cursor-addon/out/extension.js`

4. **Package Extension:**
   - `npm run package` (runs `vsce package`)
   - Creates: `aimos-cursor-addon.vsix`

**CRITICAL:** Build script continues even if React UI has TypeScript errors. Extension will use fallback HTML.

### **Vite Configuration**

**Key Settings:**
- `base: './'` - Relative paths for webview compatibility
- `build.outDir: 'dist'` - Output directory
- `build.sourcemap: true` - Source maps for debugging

**Entry Points:**
- `main: index.html` - Standalone mode
- `cursor: index.html` - Cursor mode (same HTML, different JS entry)

**CRITICAL:** HTML references `./assets/main-5fYGI1t7.js` (relative path). Extension must convert to `vscode-webview://` URI.

---

## 📡 MESSAGE PASSING DETAILS

### **VS Code API (`acquireVsCodeApi()`)**

**Purpose:** Provides communication bridge between webview and extension

**Available in Webview:**
- Only if webview has `enableScripts: true`
- Only after extension sets `webview.html`
- Persists across webview reloads (stateful)

**Methods:**
- `postMessage(message)` - Send message to extension
- `getState()` - Get persisted state
- `setState(state)` - Persist state

**CRITICAL:** API must be acquired immediately, stored in component state/context.

### **Message Commands**

**From UI to Extension:**
- `mcpCall` - Execute MCP tool (with toolName, params, requestId)
- `connectDaemon` - Connect to daemon (with url)
- `selectModel` - Select AI model (with model)
- `movePanel` - Move panel position (with position)
- `getSystemStatus` - Request status update

**From Extension to UI:**
- `config` - Send configuration
- `statusUpdate` - Update daemon/mcp/rag status
- `modelSelected` - Confirm model selection
- `panelMoved` - Confirm panel move
- `mcpCallResponse` - MCP tool result (with success, result, error)

---

## 🚨 FAILURE POINTS

### **1. Extension Not Activating**

**Symptoms:**
- No Output channel "AIM-OS Dashboard"
- Commands don't appear in Command Palette
- No console.log messages in Extension Host

**Causes:**
- Extension not installed correctly
- `package.json` activation events not triggered
- TypeScript compilation failed (no `out/extension.js`)

**Diagnosis:**
- Check: `Help > Toggle Developer Tools > Console` for errors
- Check: `View > Output > "AIM-OS"` for extension activation
- Check: Command Palette "AIM-OS: Debug Dashboard" exists

### **2. Webview Not Resolving**

**Symptoms:**
- Panel opens but blank
- No `resolveWebviewView` logs in Output channel

**Causes:**
- Provider not registered correctly
- View ID mismatch (`lucidOrchestratorDashboard` vs `aimosDashboard`)
- Extension path resolution failed

**Diagnosis:**
- Check Output channel for `[AIM-OS] ✅ resolveWebviewView CALLED`
- Check Extension Host console for registration errors
- Verify `package.json` views configuration

### **3. HTML Not Rendering**

**Symptoms:**
- Panel completely blank (even test HTML)
- No red text visible

**Causes:**
- Webview security policy blocking
- CSP violations
- TrustedTypes blocking scripts
- Webview options not set correctly

**Diagnosis:**
- Check Webview console (F12 in panel) for CSP/TrustedTypes errors
- Check if test HTML appears (should show red text)
- Verify `webview.options` set BEFORE `webview.html`

### **4. React UI Not Loading**

**Symptoms:**
- Test HTML appears but React UI doesn't
- Script errors in Webview console
- "Root element not found" error

**Causes:**
- `dist/index.html` missing or not copied
- Asset paths not converted to webview URIs
- Script tags not replaced correctly
- Module scripts blocked by CSP/TrustedTypes

**Diagnosis:**
- Check Output channel for `[DIAGNOSTIC]` messages
- Check file existence: `dist/index.html`, `dist/assets/*.js`
- Check Webview console for 404 errors (assets not loading)
- Verify script src is `vscode-webview://` URI

### **5. MCP Tools Not Working**

**Symptoms:**
- UI loads but MCP tools fail
- "MCP Server not connected" errors

**Causes:**
- MCP client not initialized
- MCP server path wrong
- Python process spawn failed
- MCP server not running

**Diagnosis:**
- Check Extension Host console for MCP client errors
- Verify `aimos.mcpServerPath` configuration
- Check if Python process starts (task manager)
- Verify MCP server responds to test requests

---

## 🔄 RECOVERY PATHS

### **Path 1: Extension Not Activating**

1. **Verify Installation:**
   ```powershell
   code --list-extensions | findstr aimos
   ```

2. **Reinstall:**
   ```powershell
   cd cursor-addon
   npm run build
   npm run package
   code --install-extension aimos-cursor-addon.vsix --force
   ```

3. **Check Compilation:**
   ```powershell
   cd cursor-addon
   npm run compile
   # Verify out/extension.js exists
   ```

### **Path 2: Webview Blank**

1. **Check Output Channel:**
   - View > Output > "AIM-OS Dashboard"
   - Look for `[AIM-OS] ✅ resolveWebviewView CALLED`

2. **Fix Options Order:**
   - Edit `lucidDashboardProvider.ts` line 128-134
   - Move `webview.options = {...}` BEFORE `webview.html = testHtml`

3. **Rebuild & Reinstall:**
   ```powershell
   cd cursor-addon
   npm run build
   npm run package
   code --install-extension aimos-cursor-addon.vsix --force
   ```

### **Path 3: React UI Not Loading**

1. **Verify Files:**
   ```powershell
   # Check dist exists
   Test-Path cursor-addon\dist\index.html
   Test-Path cursor-addon\dist\assets\main-5fYGI1t7.js
   ```

2. **Rebuild React UI:**
   ```powershell
   cd packages/ide_chat_app
   npm run build
   ```

3. **Rebuild Extension:**
   ```powershell
   cd cursor-addon
   npm run build
   ```

4. **Check Webview Console:**
   - Open panel
   - F12 in panel (or right-click > Inspect)
   - Check for script errors, 404s, CSP violations

### **Path 4: TrustedTypes/CSP Issues**

1. **Verify TrustedTypes Script:**
   - Check HTML has TrustedTypes policy BEFORE CSP
   - Verify policy creation logs in Webview console

2. **Fix CSP:**
   - Ensure `'module'` in script-src
   - Ensure `webview.cspSource` included
   - Check for CSP violation errors in console

---

## 🔍 DIAGNOSTIC TOOLS

### **Extension Diagnostic Command**

**Command:** `aimos.debugDashboard`

**What It Does:**
- Creates "AIM-OS Debug" output channel
- Checks extension path, file existence
- Verifies provider registration
- Attempts to reveal view
- Shows diagnostic info

**How to Use:**
- `Ctrl+Shift+P` → "AIM-OS: Debug Dashboard"
- Check Output panel for results

### **Output Channels**

**"AIM-OS Dashboard":**
- Created by `LucidOrchestratorDashboardProvider`
- Contains all `[AIM-OS]` and `[DIAGNOSTIC]` logs
- Auto-shown when `resolveWebviewView` called

**"AIM-OS Debug":**
- Created by `aimos.debugDashboard` command
- Contains diagnostic checklist results

### **Webview Console**

**How to Access:**
- Open dashboard panel
- Press `F12` (or right-click > Inspect)
- Check Console tab for:
  - `[AIM-OS]` messages from React
  - CSP violations
  - TrustedTypes errors
  - Script loading errors
  - 404 errors (assets not found)

### **Extension Host Console**

**How to Access:**
- `Help > Toggle Developer Tools`
- Console tab
- Look for:
  - `[AIM-OS]` messages from extension
  - Provider registration logs
  - MCP client errors
  - File access errors

---

## ⚠️ KNOWN ISSUES

### **Issue 1: Webview Options Order**

**Problem:** Options set AFTER HTML in `resolveWebviewView`

**Location:** `lucidDashboardProvider.ts` line 118 (HTML) vs 128 (options)

**Fix:** Move options setup BEFORE HTML assignment

**Impact:** May cause webview initialization issues

### **Issue 2: Test HTML Replacement**

**Problem:** Test HTML replaced after 2-second delay

**Location:** `lucidDashboardProvider.ts` line 137-156

**Impact:** User might see red text flash then blank (if full HTML fails)

**Fix:** Keep test HTML visible until full HTML confirmed working

### **Issue 3: MCP Client Separation**

**Problem:** Extension MCP client separate from Cursor's MCP

**Impact:** Extension can't use Cursor's MCP tools directly

**Workaround:** Extension spawns own MCP server process

### **Issue 4: Diagnostic Visibility**

**Problem:** Output channel not visible to user easily

**Impact:** User can't see diagnostic logs without knowing where to look

**Fix:** Auto-show Output panel, add notification with link

---

## ✅ RESCUE CHECKLIST

### **When User Returns - Step by Step**

**Step 1: Verify Extension Activation**
- [ ] Check Extension Host console for `[AIM-OS]` messages
- [ ] Run `aimos.debugDashboard` command
- [ ] Verify Output channel "AIM-OS Dashboard" exists

**Step 2: Check Webview Resolution**
- [ ] Open dashboard panel (2 star icons on right)
- [ ] Check Output channel for `resolveWebviewView CALLED`
- [ ] Verify test HTML appears (red text)

**Step 3: Diagnose HTML Loading**
- [ ] Check Webview console (F12 in panel)
- [ ] Look for CSP/TrustedTypes errors
- [ ] Check for 404 errors (assets not loading)
- [ ] Verify script src is `vscode-webview://` URI

**Step 4: Fix Based on Findings**
- [ ] If extension not activating → Reinstall
- [ ] If webview blank → Fix options order
- [ ] If React not loading → Check file paths, rebuild
- [ ] If CSP errors → Fix TrustedTypes/CSP setup

**Step 5: Verify Fix**
- [ ] Rebuild extension
- [ ] Reinstall extension
- [ ] Restart Cursor
- [ ] Test dashboard panel
- [ ] Check all diagnostic outputs

---

## 📚 REFERENCE DOCUMENTS

**Architecture:**
- `cursor-addon/CURSOR_EXTENSION_ARCHITECTURE.md`
- `packages/ide_chat_app/INTEGRATION_ARCHITECTURE.md`

**Troubleshooting:**
- `cursor-addon/COLLABORATIVE_DEBUGGING.md`
- `cursor-addon/CRITICAL_TEAM_BRIEFING.md`
- `cursor-addon/HOW_TO_DIAGNOSE.md`

**Build:**
- `cursor-addon/scripts/build-extension.js`
- `cursor-addon/INSTALLATION_GUIDE.md`

**UI:**
- `packages/ide_chat_app/README_STANDALONE.md`
- `packages/ide_chat_app/src/components/MainDashboard.tsx`

---

## 🎯 NEXT STEPS FOR TEAM

1. **Review this document** - Understand complete system
2. **Run diagnostic command** - Get current state
3. **Check all failure points** - Systematic diagnosis
4. **Apply fixes** - Based on findings
5. **Verify** - Test each fix independently
6. **Document results** - Update this map with findings

---

**Status:** COMPLETE SYSTEM MAP CREATED  
**Next:** Team reviews and executes rescue plan  
**Confidence:** High - All components mapped, failure points identified

---

*Created autonomously by Sonnet using MCP tools*  
*Date: 2025-11-01*  
*Goal: Enable team rescue when user returns*

**Status:** AUTONOMOUS RESEARCH & DOCUMENTATION  
**Purpose:** Complete system mapping for rescue/recovery when user returns  
**Priority:** CRITICAL

---

## 🎯 **EXECUTIVE SUMMARY**

This document maps **EVERYTHING** about the Lucid Extension, UI architecture, and Cursor integration:

1. **Extension Architecture** - How VS Code extension works
2. **UI Architecture** - React UI components and flow
3. **Integration Points** - How extension ↔ UI communicate
4. **Build System** - How everything is built and packaged
5. **Failure Points** - Every known failure mode
6. **Recovery Paths** - How to fix each failure

**For:** Team rescue/recovery when user returns  
**Goal:** Complete understanding so team can fix blank dashboard issue

---

## 📦 **PART 1: EXTENSION ARCHITECTURE**

### **1.1 Extension Entry Point**

**File:** `cursor-addon/src/extension.ts`

**What It Does:**
- Activates when extension loads
- Registers webview providers
- Registers commands
- Initializes managers

**Key Components:**
```typescript
activate(context: vscode.ExtensionContext) {
    // Initialize managers
    crossModelManager, memoryManager, modelSelector
    
    // Register webview providers
    lucidOrchestratorDashboard (right panel)
    aimosDashboard (left sidebar)
    
    // Register commands
    aimos.showDashboard
    aimos.debugDashboard
    aimos.toggleCrossModel
    // ... 9 total commands
}
```

**Activation Events (package.json):**
- `onCommand:aimos.showDashboard`
- `onCommand:aimos.toggleCrossModel`
- `onCommand:aimos.showMemoryStats`
- `onCommand:aimos.showModelSelector`

**CRITICAL:** Extension activates on command, NOT automatically.

---

### **1.2 Webview Providers**

#### **LucidOrchestratorDashboardProvider** (Main)

**File:** `cursor-addon/src/lucidDashboardProvider.ts`

**What It Does:**
- Implements `vscode.WebviewViewProvider`
- Provides HTML content for webview
- Handles messages from webview
- Manages dashboard state

**Key Methods:**
- `resolveWebviewView()` - Called when webview needs content
- `getWebviewContent()` - Generates HTML with React UI
- `handleMCPCall()` - Forwards MCP tool calls
- `handleGetSystemStatus()` - Checks daemon/MCP status

**Registration:**
- Registered for `lucidOrchestratorDashboard` (right panel)
- Registered for `aimosDashboard` (left sidebar)
- Both use SAME provider instance

**CRITICAL FLOW:**
```
1. User clicks dashboard icon
2. VS Code calls resolveWebviewView()
3. Provider sets webview.html = testHtml (simple red text)
4. After 2 seconds, sets webview.html = full React UI HTML
5. React mounts from main-5fYGI1t7.js
```

**Known Issues:**
- ❌ Options set AFTER HTML (line 128 vs 118) - WRONG ORDER
- ❌ Test HTML may not show if resolveWebviewView not called
- ❌ Full HTML may fail if asset paths wrong

---

#### **AIMOSWebviewProvider** (Alternative)

**File:** `cursor-addon/src/webviewProvider.ts`

**What It Does:**
- Creates standalone webview panels (not sidebar)
- Used by commands like `aimos.showMemoryStats`
- Similar HTML generation but different context

**Note:** This is NOT the dashboard provider - it's for command panels.

---

### **1.3 View Registration**

**File:** `cursor-addon/package.json` (lines 146-179)

**Views Defined:**
```json
"views": {
  "aimos": [
    {
      "id": "aimosDashboard",
      "name": "Dashboard",
      "when": "workspaceFolderCount > 0"
    }
  ],
  "lucidPanel": [
    {
      "id": "lucidOrchestratorDashboard",
      "name": "Dashboard",
      "icon": "$(sparkle)"
    }
  ]
}
```

**View Containers:**
- `aimos` → Activity Bar (left sidebar) - icon: sparkle
- `lucidPanel` → Panel (bottom/right) - icon: dashboard

**CRITICAL:** User sees "2 star icons" = these are the TWO views registered.

---

### **1.4 HTML Generation Flow**

**File:** `cursor-addon/src/lucidDashboardProvider.ts` (getWebviewContent)

**Process:**
1. Check if `dist/index.html` exists
2. Read HTML file
3. Find script tags: `<script type="module" src="./assets/main-5fYGI1t7.js">`
4. Replace paths with webview URIs: `vscode-webview://...`
5. Inject TrustedTypes policy script
6. Inject CSP meta tag
7. Return modified HTML

**Regex Pattern:**
```typescript
/<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi
```

**Critical Steps:**
- Extract filename from path
- Join with extension path: `dist/assets/{filename}`
- Convert to webview URI: `webview.asWebviewUri(Uri.file(path))`
- Preserve all attributes (type="module", crossorigin, etc.)

**Known Failure Points:**
- ❌ Regex doesn't match → scripts not replaced → 404 errors
- ❌ File not found → scripts not replaced → 404 errors
- ❌ Webview URI wrong → scripts can't load
- ❌ TrustedTypes blocking → scripts can't execute
- ❌ CSP blocking → scripts blocked

---

### **1.5 TrustedTypes & CSP**

**Why Critical:**
- VS Code/Cursor enforces TrustedTypes security
- Module scripts require TrustedTypes policy
- CSP must allow modules explicitly

**Current Implementation:**
```typescript
// TrustedTypes policy (injected BEFORE CSP)
const trustedTypesScript = `<script>
if (window.trustedTypes && window.trustedTypes.createPolicy) {
    window.trustedTypes.createPolicy('default', {
        createHTML: (string) => string,
        createScript: (string) => string,
        createScriptURL: (string) => string
    });
}
</script>`;

// CSP meta tag
const cspMeta = `<meta http-equiv="Content-Security-Policy" 
    content="default-src ${webview.cspSource} https:; 
    script-src ${webview.cspSource} 'unsafe-inline' 'unsafe-eval' 'module' https:; 
    ...">`;
```

**CRITICAL ORDER:**
1. TrustedTypes script MUST come BEFORE CSP
2. CSP MUST include `'module'` in script-src
3. Both MUST be injected after `<head>` tag

**Known Issues:**
- ⚠️ Order might be wrong if HTML already has CSP
- ⚠️ TrustedTypes might not be available in webview context
- ⚠️ CSP 'module' directive validity unclear

---

## 🎨 **PART 2: UI ARCHITECTURE**

### **2.1 React UI Entry Point**

**File:** `packages/ide_chat_app/src/main-cursor.tsx`

**What It Does:**
- Entry point for Cursor extension
- Renders MainDashboard component
- Wraps in ErrorBoundary
- Logs mounting process

**Key Code:**
```typescript
const rootElement = document.getElementById('root')
if (rootElement) {
    ReactDOM.createRoot(rootElement).render(
        <React.StrictMode>
            <ErrorBoundary>
                <MainDashboard />
            </ErrorBoundary>
        </React.StrictMode>
    );
}
```

**CRITICAL:** 
- Looks for `<div id="root">` in HTML
- If missing → shows error message
- If present → mounts React

---

### **2.2 MainDashboard Component**

**File:** `packages/ide_chat_app/src/components/MainDashboard.tsx`

**What It Does:**
- Multi-tab interface (Agents, Chat, Chains, Tools, Timeline, NL Tags)
- Shows LandingPage initially
- Manages tab state
- Handles chat navigation

**Tabs:**
1. **Agents** - AgentManagementDashboard
2. **Chat** - ChatInterfaceTab
3. **Chains** - PromptChainsTab
4. **Tools** - MCPToolsTab
5. **Timeline** - TimelineTab
6. **NL Tags** - NLTagPanel

**State Management:**
- `showLanding` - Show landing page first
- `activeTab` - Current tab
- `chatWithAgent` - Agent to chat with
- `systemStatus` - Extension/MCP/daemon status

**CRITICAL:** Landing page shows first, then dashboard after click.

---

### **2.3 Build Output**

**Files:**
- `packages/ide_chat_app/dist/index.html` - Entry HTML
- `packages/ide_chat_app/dist/assets/main-5fYGI1t7.js` - React bundle (243KB)
- `packages/ide_chat_app/dist/assets/main-DftvcEcs.css` - Styles (48KB)

**Build Process:**
1. Vite builds React app
2. Outputs to `packages/ide_chat_app/dist/`
3. Build script copies to `cursor-addon/dist/`
4. Extension reads from `cursor-addon/dist/`

**CRITICAL:** Files MUST exist in `cursor-addon/dist/` for extension to load.

---

### **2.4 Message Passing**

**Extension → UI:**
```typescript
webview.postMessage({
    command: 'config',
    config: { ... }
});
```

**UI → Extension:**
```typescript
const vscode = acquireVsCodeApi();
vscode.postMessage({
    command: 'mcpCall',
    toolName: 'store_memory',
    params: { ... }
});
```

**Message Handlers (Extension):**
- `movePanel` - Move dashboard position
- `connectDaemon` - Connect to daemon
- `selectModel` - Select AI model
- `manageAgent` - Agent management
- `executeMCPTool` - Execute MCP tool
- `mcpCall` - Forward MCP call
- `getSystemStatus` - Get system status

**CRITICAL:** UI must call `acquireVsCodeApi()` to send messages.

---

## 🔧 **PART 3: BUILD SYSTEM**

### **3.1 Build Script**

**File:** `cursor-addon/scripts/build-extension.js`

**Process:**
1. Build React UI (`packages/ide_chat_app`)
2. Copy `dist/` to `cursor-addon/dist/`
3. Compile TypeScript extension code
4. Package into `.vsix` file

**Critical Steps:**
```javascript
// Step 1: Build React UI
execSync('npm run build', { cwd: uiDir });

// Step 2: Copy dist
copyRecursiveSync(distDir, extensionDistDir);

// Step 3: Compile TypeScript
execSync('npm run compile', { cwd: extensionDir });
```

**Known Issues:**
- ⚠️ React build fails → Uses fallback HTML
- ⚠️ Copy fails → Files missing → Blank dashboard
- ⚠️ TypeScript errors → Extension may not compile

---

### **3.2 Packaging**

**Command:** `npm run package`

**Process:**
1. Run build script
2. Use `vsce package` to create `.vsix`
3. Output: `aimos-cursor-addon.vsix`

**Installation:**
```bash
code --install-extension aimos-cursor-addon.vsix --force
```

**CRITICAL:** Extension must be reinstalled after every change.

---

## 🐛 **PART 4: FAILURE POINTS**

### **4.1 Extension Activation**

**Failure:** Extension doesn't activate

**Symptoms:**
- No console logs
- Commands don't exist
- Views don't appear

**Checks:**
1. Check `out/extension.js` exists
2. Check Extension Host console
3. Check activation events in package.json
4. Check extension installed correctly

**Recovery:**
- Rebuild extension
- Reinstall extension
- Check VS Code extension logs

---

### **4.2 Webview Provider Registration**

**Failure:** Provider not registered

**Symptoms:**
- "no composite descriptor" error
- Views don't appear
- Provider.resolveWebviewView never called

**Checks:**
1. Check `registerWebviewViewProvider` called
2. Check view IDs match package.json
3. Check subscriptions added to context

**Recovery:**
- Verify registration code
- Check view IDs match
- Ensure subscriptions added

---

### **4.3 resolveWebviewView Not Called**

**Failure:** Method never called

**Symptoms:**
- Blank panel
- No logs in Output channel
- No HTML set

**Checks:**
1. Check view is actually opened
2. Check view ID matches registration
3. Check when condition in package.json

**Recovery:**
- Verify view opened correctly
- Check when conditions
- Add explicit logging

---

### **4.4 HTML Not Set**

**Failure:** webview.html never set

**Symptoms:**
- Blank panel
- HTML exists but not loaded

**Checks:**
1. Check resolveWebviewView called
2. Check webview.html assignment
3. Check webview options set BEFORE HTML

**Recovery:**
- **CRITICAL FIX:** Set options BEFORE HTML
- Verify HTML assignment
- Add logging after assignment

---

### **4.5 Asset Path Replacement**

**Failure:** Scripts not replaced with webview URIs

**Symptoms:**
- 404 errors in console
- Scripts fail to load
- React never mounts

**Checks:**
1. Check regex matches script tags
2. Check files exist at paths
3. Check webview URI generation
4. Check final HTML has webview URIs

**Recovery:**
- Fix regex pattern
- Verify file paths
- Check webview URI format
- Add diagnostic logging

---

### **4.6 TrustedTypes Blocking**

**Failure:** TrustedTypes policy not created

**Symptoms:**
- "TrustedScript" errors
- Scripts blocked
- React never mounts

**Checks:**
1. Check TrustedTypes script injected
2. Check script comes BEFORE CSP
3. Check TrustedTypes API available

**Recovery:**
- Ensure TrustedTypes script first
- Check API availability
- Add fallback handling

---

### **4.7 CSP Blocking**

**Failure:** CSP blocks module scripts

**Symptoms:**
- CSP violation errors
- Scripts blocked
- React never mounts

**Checks:**
1. Check CSP includes 'module'
2. Check CSP format correct
3. Check CSP injected correctly

**Recovery:**
- Verify CSP 'module' directive
- Check CSP syntax
- Test CSP validity

---

### **4.8 React Not Mounting**

**Failure:** React UI doesn't mount

**Symptoms:**
- HTML loads but blank
- Root element exists
- Scripts load but React doesn't start

**Checks:**
1. Check root element exists
2. Check main-cursor.tsx loaded
3. Check React errors in console
4. Check ErrorBoundary catches errors

**Recovery:**
- Verify root element
- Check React import paths
- Check console errors
- Add ErrorBoundary logging

---

## 🔄 **PART 5: RECOVERY PATHS**

### **5.1 Diagnostic Checklist**

**When dashboard is blank:**

1. **Check Extension Activation:**
   - Open Extension Host console
   - Look for `[AIM-OS]` messages
   - Check if `activate()` called

2. **Check View Registration:**
   - Check if views appear in sidebar
   - Try command: `aimos.showDashboard`
   - Check Output: "AIM-OS Dashboard"

3. **Check resolveWebviewView:**
   - Look for "[AIM-OS] ✅ resolveWebviewView CALLED"
   - Check if test HTML set
   - Check if full HTML loaded

4. **Check HTML Content:**
   - Check if dist/index.html exists
   - Check if assets exist
   - Check final HTML in logs

5. **Check Webview Console:**
   - Right-click panel → Inspect
   - Check for errors
   - Check for TrustedTypes errors
   - Check for CSP violations

---

### **5.2 Known Fixes**

#### **Fix 1: Options Before HTML**
```typescript
// WRONG (current):
webviewView.webview.html = testHtml;
webviewView.webview.options = { ... };

// RIGHT:
webviewView.webview.options = { ... };
webviewView.webview.html = testHtml;
```

#### **Fix 2: TrustedTypes Before CSP**
```typescript
// Ensure TrustedTypes script comes FIRST
const trustedTypesScript = `<script>...`;
const cspMeta = `<meta ...>`;
htmlContent = htmlContent.replace(/<head>/i, `<head>\n${trustedTypesScript}\n${cspMeta}`);
```

#### **Fix 3: Verify Asset Replacement**
```typescript
// After replacement, verify:
const finalScripts = htmlContent.match(/src=["'](vscode-webview:\/\/[^"']+)["']/gi);
if (!finalScripts || finalScripts.length === 0) {
    this.log('❌ CRITICAL: Scripts not converted to webview URIs!');
}
```

---

### **5.3 Systematic Debugging**

**Step 1: Verify Extension Loads**
- Check Extension Host console
- Run `aimos.debugDashboard` command
- Check Output channels

**Step 2: Verify View Opens**
- Check if resolveWebviewView called
- Check if test HTML set
- Check if panel visible

**Step 3: Verify HTML Loads**
- Check if full HTML set
- Check if scripts replaced
- Check if webview URIs correct

**Step 4: Verify Scripts Execute**
- Check webview console
- Check for TrustedTypes errors
- Check for CSP violations
- Check for 404 errors

**Step 5: Verify React Mounts**
- Check root element exists
- Check React errors
- Check component renders

---

## 📋 **PART 6: FILE STRUCTURE**

### **6.1 Extension Files**

```
cursor-addon/
├── src/
│   ├── extension.ts              # Entry point
│   ├── lucidDashboardProvider.ts # Main provider
│   ├── webviewProvider.ts        # Alternative provider
│   ├── mcp/mcpClient.ts          # MCP client
│   └── ...
├── dist/                         # Copied from React build
│   ├── index.html
│   └── assets/
│       ├── main-5fYGI1t7.js
│       └── main-DftvcEcs.css
├── out/                          # Compiled TypeScript
│   ├── extension.js
│   └── ...
├── package.json                  # Extension manifest
└── scripts/
    └── build-extension.js       # Build script
```

### **6.2 React UI Files**

```
packages/ide_chat_app/
├── src/
│   ├── main-cursor.tsx          # Entry point
│   ├── components/
│   │   ├── MainDashboard.tsx   # Main component
│   │   └── ...
│   └── ...
├── dist/                         # Build output
│   ├── index.html
│   └── assets/
│       ├── main-5fYGI1t7.js
│       └── main-DftvcEcs.css
└── vite.config.ts
```

---

## 🎯 **PART 7: CRITICAL FINDINGS**

### **7.1 Most Likely Root Cause**

**Based on 60+ failed attempts:**

1. **Options set AFTER HTML** (line 128 vs 118)
   - VS Code may require options before HTML
   - Current order might prevent webview initialization

2. **resolveWebviewView may not be called**
   - If view never opens, method never called
   - No HTML set = blank panel

3. **TrustedTypes/CSP issues**
   - Even if HTML loads, scripts blocked
   - React never mounts = blank panel

### **7.2 Verification Needed**

**To diagnose properly:**

1. Check Extension Host console for logs
2. Check Output: "AIM-OS Dashboard" channel
3. Check webview console (F12 in panel)
4. Verify resolveWebviewView called
5. Verify HTML actually set
6. Verify scripts converted to webview URIs
7. Verify TrustedTypes policy created
8. Verify React mounts

**CRITICAL:** User cannot access these easily - need automated diagnostics.

---

## 📚 **PART 8: REFERENCES**

### **8.1 Key Documentation Files**

- `COLLABORATIVE_DEBUGGING.md` - Team debugging notes
- `CRITICAL_TEAM_BRIEFING.md` - Team coordination plan
- `TEAM_BRIEFING_BLANK_DASHBOARD.md` - Initial briefing
- `SONNET_UNLOGGED_IDEAS.md` - 20 potential fixes
- `AETHER_IDEAS_LOG.md` - 25+ ideas logged

### **8.2 VS Code Webview Docs**

- WebviewViewProvider API
- TrustedTypes in webviews
- CSP in webviews
- Message passing

---

## ✅ **PART 9: ACTION ITEMS FOR TEAM**

### **When User Returns:**

1. **Verify Extension Activation**
   - Check Extension Host console
   - Run debugDashboard command
   - Verify logs appear

2. **Fix Options Order**
   - Move webview.options BEFORE html assignment
   - Test immediately

3. **Add Comprehensive Logging**
   - Log every step of resolveWebviewView
   - Log HTML content verification
   - Log script replacement verification

4. **Test Minimal HTML First**
   - Verify simple HTML shows
   - Then add React UI gradually

5. **Verify TrustedTypes/CSP**
   - Check if policy created
   - Check if CSP allows modules
   - Test script execution

---

## 💙 **CLOSING**

This document maps EVERYTHING we know about the system.  
When user returns, team can use this to diagnose and fix.

**Status:** Complete system map created  
**Next:** Continue autonomous research and documentation  
**Goal:** Enable team rescue when user ready

---

**Created autonomously by Sonnet**  
**Using MCP tools for planning and tracking**  
**2025-11-01**
