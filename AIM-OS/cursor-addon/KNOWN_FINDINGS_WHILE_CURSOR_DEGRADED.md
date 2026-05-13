# Known Findings - Documented While Cursor AI Degraded

**Date:** 2025-11-01  
**Status:** Cursor AI in degraded mode - documenting everything we know  
**Purpose:** Preserve all findings for when Cursor recovers

---

## 🎯 **ROOT CAUSE IDENTIFIED (Aether)**

**Critical Finding:**
- **File:** `cursor-addon/src/lucidDashboardProvider.ts`
- **Lines:** 118-134
- **Issue:** Webview options set AFTER HTML assignment
- **VS Code Requirement:** Options MUST be set BEFORE HTML

**Evidence:**
- ConsoleProvider (working): Sets options FIRST, then HTML ✅
- webviewProvider.ts (working): Options in constructor, then HTML ✅
- lucidDashboardProvider.ts (broken): HTML first, options after ❌

**Confidence:** 0.90 (verified by comparing with working code)

**Fix Plan:**
1. Move `webviewView.webview.options = {...}` BEFORE `webviewView.webview.html = testHtml`
2. Remove unnecessary 2-second setTimeout
3. Simplify to single HTML assignment with correct order

---

## 🔍 **ADDITIONAL FINDINGS (Lexicon)**

**Activation Events Problem:**
- Extension only activates on COMMANDS (`onCommand:aimos.showDashboard`)
- NO activation event for webview views (`onView` missing)
- Extension may NOT activate when panel opens - only when command runs

**Code Analysis:**
1. Provider sets simple test HTML first (good - should show red text if webview works)
2. Then tries full HTML after 2 seconds timeout
3. TrustedTypes fix IS in code (lines 352-365) ✅
4. CSP 'module' directive IS in code (line 368) ✅
5. Diagnostic logging IS comprehensive ✅

**Next Steps:**
- Add `onView` activation event to package.json
- Or verify if webview views trigger activation differently

---

## 📋 **WHAT WE KNOW FOR CERTAIN**

### **Files Verified:**
- ✅ `dist/index.html` exists (1080 bytes)
- ✅ `dist/assets/main-5fYGI1t7.js` exists (243KB)
- ✅ `dist/assets/main-DftvcEcs.css` exists (48KB)
- ✅ Extension installs successfully
- ✅ Extension registers providers (no errors in extension.ts)

### **What User Sees:**
- Blank panel on right side (2 star icons)
- No red test text (should appear if webview works)
- No diagnostic output visible
- Extension may not be activating

### **What Should Happen:**
1. Extension activates when panel opens
2. `resolveWebviewView()` called
3. Test HTML (red text) shows immediately
4. After 2 seconds, full React UI loads
5. Diagnostic logs appear in Output panel

### **What's Actually Happening:**
- Unknown (no diagnostics visible)
- Could be: Extension not activating
- Could be: `resolveWebviewView()` not called
- Could be: Webview options order bug (Aether's finding)

---

## 🛠️ **FIXES THAT ARE IN CODE**

### **TrustedTypes Fix (Sonnet):**
- ✅ Lines 352-365: TrustedTypes policy creation BEFORE CSP
- ✅ Policy created with proper methods

### **CSP Module Directive (Sonnet):**
- ✅ Line 368: CSP includes `'module'` directive
- ✅ Allows ES module scripts

### **Diagnostic Logging (Lexicon):**
- ✅ Comprehensive `[DIAGNOSTIC]` logging throughout
- ✅ File existence checks
- ✅ Asset path verification
- ✅ Regex matching verification
- ✅ Webview URI generation logging

---

## ❌ **KNOWN BUGS**

### **Bug 1: Webview Options Order (Aether - CRITICAL)**
- **Location:** `lucidDashboardProvider.ts` lines 118-134
- **Issue:** Options set AFTER HTML
- **Fix:** Move options BEFORE HTML
- **Confidence:** 0.90

### **Bug 2: Missing Activation Event (Lexicon)**
- **Location:** `package.json` activationEvents
- **Issue:** No `onView` event for webview views
- **Fix:** Add `onView:aimosDashboard` and `onView:lucidOrchestratorDashboard`
- **Confidence:** 0.75

### **Bug 3: Unnecessary Timeout**
- **Location:** `lucidDashboardProvider.ts` lines 137-156
- **Issue:** 2-second delay before loading full HTML
- **Fix:** Remove timeout, load HTML directly
- **Confidence:** 0.70

---

## 📊 **SYSTEM ARCHITECTURE SUMMARY**

### **Extension Structure:**
```
cursor-addon/
├── src/
│   ├── extension.ts (main entry, registers providers)
│   ├── lucidDashboardProvider.ts (webview provider - HAS BUG)
│   ├── webviewProvider.ts (alternative provider - works)
│   ├── mcp/mcpClient.ts (MCP protocol client)
│   ├── crossModel/crossModelManager.ts
│   ├── memory/memoryManager.ts
│   └── models/modelSelector.ts
├── dist/ (React UI - copied from packages/ide_chat_app)
│   ├── index.html
│   └── assets/
│       ├── main-5fYGI1t7.js (React bundle)
│       └── main-DftvcEcs.css (styles)
└── package.json (extension manifest)
```

### **UI Structure:**
```
packages/ide_chat_app/
├── src/
│   ├── main-cursor.tsx (entry point for Cursor)
│   ├── components/
│   │   ├── MainDashboard.tsx (multi-tab UI)
│   │   ├── AgentManagementDashboard/
│   │   └── [other components]
│   └── services/
│       ├── AIMOSService.ts (HTTP API client)
│       └── HttpLucidDaemonService.ts
└── dist/ (built output - copied to cursor-addon/dist)
```

### **Message Flow:**
1. User opens panel → VS Code calls `resolveWebviewView()`
2. Provider sets HTML → Webview renders
3. React mounts → `acquireVsCodeApi()` available
4. React sends messages → `webview.postMessage()`
5. Extension receives → `onDidReceiveMessage()`
6. Extension responds → `webview.postMessage()`

---

## 🎯 **RECOVERY PLAN (When Cursor Stable)**

### **Priority 1: Fix Webview Options Order**
- Move options setting BEFORE HTML
- Test immediately
- Should fix blank panel

### **Priority 2: Add Activation Events**
- Add `onView` events to package.json
- Ensure extension activates when panel opens

### **Priority 3: Remove Timeout**
- Simplify HTML loading
- Remove 2-second delay
- Load full HTML directly

### **Priority 4: Verify Diagnostics**
- Check if Output panel shows logs
- Verify extension activation
- Confirm webview rendering

---

## 💙 **FOR WHEN CURSOR RECOVERS**

**We have:**
- ✅ Root cause identified (Aether)
- ✅ Additional findings (Lexicon)
- ✅ All fixes documented
- ✅ Complete architecture mapped
- ✅ Recovery plan ready

**Next Steps:**
1. Apply Aether's fix (options before HTML)
2. Add Lexicon's activation events
3. Test systematically
4. Verify with diagnostics

**We're ready to fix this when Cursor recovers.** 💙

---

**Status:** Cursor AI degraded - all findings preserved  
**Created:** 2025-11-01 (while Cursor in degraded mode)  
**Purpose:** Enable immediate fix when Cursor recovers



