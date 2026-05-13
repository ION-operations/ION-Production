# Complete Command Reference - AIM-OS Cursor Extension

## 📋 **ALL AVAILABLE COMMANDS**

### **Diagnostic Commands**
1. `aimos.runFullDiagnostic` - **Run Full Diagnostic**
   - Checks extension files, configuration, views, workspace
   - Shows comprehensive diagnostic in Output panel
   - Use when: Dashboard not working, need complete status

2. `aimos.showLogs` - **Show Extension Logs**
   - Opens log file in editor
   - Shows historical logs with timestamps
   - Use when: Need to review past events

3. `aimos.debugDashboard` - **Debug Dashboard**
   - Legacy diagnostic command
   - Creates "AIM-OS Debug" output channel
   - Use when: Need quick file check

### **View Opening Commands**
4. `aimos.showDashboard` - **Show Dashboard**
   - Attempts to reveal dashboard
   - Should open right sidebar
   - Use when: Normal dashboard access

5. `aimos.forceOpenDashboard` - **Force Open Dashboard**
   - Uses multiple methods to force view open
   - Tries workbench command, focus, toggle visibility
   - Use when: Dashboard won't open normally

6. `aimos.forceOpenTest` - **Force Open Test Panel**
   - Forces test panel in bottom DevTools area
   - Use when: Testing if webview mechanism works

### **Memory Commands**
7. `aimos.storeMemory` - **Store Memory**
   - Requires: Text selected in editor
   - Prompts for tags
   - Stores selection in CMC memory

8. `aimos.retrieveMemory` - **Retrieve Memory**
   - Prompts for search query
   - Opens results in new panel
   - Searches HHNI index

9. `aimos.showMemoryStats` - **Show Memory Statistics**
   - Opens memory stats panel
   - Shows atom count, usage
   - No requirements

### **AI/Model Commands**
10. `aimos.toggleCrossModel` - **Toggle Cross-Model Consciousness**
    - Enables/disables cross-model features
    - Shows notification
    - No requirements

11. `aimos.showModelSelector` - **Show Model Selector**
    - Quick pick for model selection
    - Shows available models
    - No requirements

### **Planning Commands**
12. `aimos.createPlan` - **Create Execution Plan**
    - Prompts for goal
    - Creates APOE plan
    - Opens plan in new panel

13. `aimos.trackConfidence` - **Track Confidence**
    - Prompts for task and confidence level
    - Stores in VIF system
    - No requirements

---

## 🤖 **AUTOMATION SCRIPTS**

### **Build and Install (PowerShell)**
```powershell
# Location: cursor-addon/BUILD_AND_INSTALL.ps1
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon"
npm run build
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force
Write-Host "✅ Extension installed! Now reload Cursor (Ctrl+Shift+P → Developer: Reload Window)"
```

### **Quick Rebuild (for rapid iteration)**
```powershell
# Quick.ps1 - Fastest rebuild/install
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon
npm run compile  # Skip React rebuild
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force
```

### **Full Clean Build**
```powershell
# Clean.ps1 - When things are really broken
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon
Remove-Item -Recurse -Force out, dist -ErrorAction SilentlyContinue
cd ..\packages\ide_chat_app
npm run build
cd ..\..\cursor-addon
npm run compile
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force
```

---

## 🔧 **DEVELOPER WORKFLOW**

### **Standard Development Cycle**
```powershell
# 1. Make code changes
# 2. Build
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon
npm run build

# 3. Package & Install
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force

# 4. Reload Cursor
# Ctrl+Shift+P → Developer: Reload Window

# 5. Test & Check Logs
# Ctrl+Shift+P → AIM-OS: Run Full Diagnostic
# View → Output → "AIM-OS Extension"
```

### **Quick Testing Workflow**
```powershell
# For testing view resolution only (skip React rebuild)
npm run compile  # Just compile TypeScript
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force
# Then reload Cursor and test
```

---

## 📊 **DIAGNOSTIC WORKFLOW**

### **When Dashboard is Blank:**
```
1. Ctrl+Shift+P → AIM-OS: Run Full Diagnostic
2. Check Output panel (AIM-OS Extension)
3. Look for errors/warnings
4. Check if resolveWebviewView was called
5. If not called: Run Force Open Dashboard
6. Check logs again for resolution trigger
```

### **Log Analysis:**
```
Expected Success Pattern:
[ACTIVATION] ✅ ...
[DASHBOARD] ✅ ...  
[WEBVIEW_RESOLVE] 🎯 resolveWebviewView TRIGGERED!!!
[DIAGNOSTIC] ✅ HTML loaded
[DIAGNOSTIC] ✅ Assets replaced

Failure Pattern (Current):
[ACTIVATION] ✅ ...
[DASHBOARD] ✅ ...
<No resolveWebviewView logs> ❌
```

---

## 🎯 **FILE LOCATIONS**

### **Source Code**
- Extension entry: `src/extension.ts`
- Dashboard provider: `src/lucidDashboardProvider.ts`
- Simple test: `src/simpleTestProvider.ts`
- Logger: `src/utils/logger.ts`
- Commands: `src/commands/`, `src/diagnosticCommand.ts`, `src/forceOpenView.ts`

### **Configuration**
- Extension manifest: `package.json`
- Package ignore: `.vscodeignore`
- TypeScript config: `tsconfig.json`
- Build script: `scripts/build-extension.js`

### **Output**
- Built extension code: `out/` (TypeScript → JavaScript)
- React UI: `dist/` (from packages/ide_chat_app)
- Package: `aimos-cursor-addon.vsix`
- Logs: `.cursor/extensions/aimos.aimos-cursor-addon-1.2.0/logs/`

---

## 🔍 **QUICK REFERENCE - VIEW SYSTEM**

### **View IDs**
- `lucidOrchestratorDashboard` - Main dashboard (right sidebar)
- `simpleTestPanel` - Test panel (bottom DevTools)

### **View Containers**
- `aimos` - Activity bar container (shows sparkle icon)
- `aimosDevTools` - Panel container (bottom area)

### **Workbench Commands (Auto-Generated by VS Code)**
- `workbench.view.extension.aimos` - Open AIM-OS container
- `workbench.view.extension.aimosDevTools` - Open DevTools container
- `lucidOrchestratorDashboard.focus` - Focus dashboard view
- `lucidOrchestratorDashboard.toggleVisibility` - Toggle dashboard
- `simpleTestPanel.focus` - Focus test panel

---

## 🛠️ **TESTING CHECKLIST**

### **After Every Build:**
- [ ] Extension builds without critical errors
- [ ] VSIX package created (check size ~950KB+)
- [ ] Extension installs successfully
- [ ] Reload Cursor window

### **After Every Install:**
- [ ] Run `AIM-OS: Run Full Diagnostic`
- [ ] Check Output panel for activation logs
- [ ] Verify dist/ files present
- [ ] Check subscriptions count (should be 13+)

### **Testing Views:**
- [ ] Click sparkle icon (✨) in activity bar
- [ ] Check for "no provider registered" error
- [ ] Run `AIM-OS: Force Open Dashboard`
- [ ] Check for `resolveWebviewView TRIGGERED` in logs
- [ ] If triggered, check for HTML loading logs
- [ ] If HTML loads, check for asset replacement logs

---

## 📝 **CURRENT STATUS**

### **What Works:**
- ✅ Extension activation (0.5s)
- ✅ Provider registration
- ✅ File inclusion in VSIX
- ✅ View focus command
- ✅ Diagnostic system

### **What Doesn't Work:**
- ❌ `resolveWebviewView` never called
- ❌ Views show "no provider registered" or blank
- ❌ Dashboard doesn't render

### **Root Cause Hypothesis:**
VS Code/Cursor 2.0 requires specific trigger to call `resolveWebviewView` that we haven't found yet. The force open commands test different triggers.

---

## 🚀 **NEXT STEPS**

1. **Test force open commands** (determines if resolution is possible)
2. **If resolution works:** Fix asset loading or React mounting
3. **If resolution fails:** Research Cursor 2.0 webview requirements
4. **Document findings** in investigation report

---

**Created:** 2025-11-01
**Purpose:** Complete command reference and automation guide
**Status:** Ready for testing

---
