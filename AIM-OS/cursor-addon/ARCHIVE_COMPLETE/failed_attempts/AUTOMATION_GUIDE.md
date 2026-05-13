# 🤖 Complete Automation Guide - AIM-OS Cursor Extension

## 🎯 **For Opus/AI Agents: All Commands You Can Run**

---

## 📦 **BUILD & INSTALL AUTOMATION**

### **Standard Build (Full)**
```powershell
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon"
npm run build
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force
```

**When to use:** After making any changes to source code or React UI

### **Quick Build (Extension Only)**
```powershell
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon"
npm run compile
vsce package --out aimos-cursor-addon.vsix --allow-star-activation
code --install-extension aimos-cursor-addon.vsix --force
```

**When to use:** Only changed TypeScript extension code, not React UI

### **React UI Only**
```powershell
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\packages\ide_chat_app"
npm run build
# Then run standard build above
```

**When to use:** Only changed React components

---

## 🔍 **DIAGNOSTIC AUTOMATION**

### **Full System Diagnostic**
```
Command: Ctrl+Shift+P → AIM-OS: Run Full Diagnostic
Automated: vscode.commands.executeCommand('aimos.runFullDiagnostic')
```

**Output:** Comprehensive diagnostic in Output panel
- Extension info
- Workspace info
- File verification
- View container status
- Configuration verification

### **View Extension Logs**
```
Command: Ctrl+Shift+P → AIM-OS: Show Extension Logs
Automated: vscode.commands.executeCommand('aimos.showLogs')
```

**Output:** Opens log file in editor with full history

### **Legacy Debug**
```
Command: Ctrl+Shift+P → AIM-OS: Debug Dashboard
Automated: vscode.commands.executeCommand('aimos.debugDashboard')
```

**Output:** Quick file check in Output panel

---

## 🚀 **VIEW OPENING AUTOMATION**

### **Normal Dashboard Open**
```
Command: Ctrl+Shift+P → AIM-OS: Show Dashboard
Automated: vscode.commands.executeCommand('aimos.showDashboard')
```

**What it does:** Attempts to reveal dashboard using reveal() method

### **Force Dashboard Open**
```
Command: Ctrl+Shift+P → AIM-OS: Force Open Dashboard
Automated: vscode.commands.executeCommand('aimos.forceOpenDashboard')
```

**What it does:** 
- Executes `workbench.view.extension.aimos`
- Executes `aimosDashboard.focus`
- Toggles visibility
- Waits 1s then checks if resolved

### **Force Test Panel Open**
```
Command: Ctrl+Shift+P → AIM-OS: Force Open Test Panel  
Automated: vscode.commands.executeCommand('aimos.forceOpenTest')
```

**What it does:**
- Opens DevTools container
- Focuses test panel

---

## 📊 **FILE VERIFICATION AUTOMATION**

### **Check Installed Extension Files**
```powershell
$extPath = "$env:USERPROFILE\.cursor\extensions\aimos.aimos-cursor-addon-1.2.0"

# Check dist/ exists
Test-Path "$extPath\dist"

# List dist contents
Get-ChildItem "$extPath\dist"

# Check specific files
Test-Path "$extPath\dist\index.html"
Test-Path "$extPath\dist\assets\main-5fYGI1t7.js"

# Get file sizes
Get-ChildItem "$extPath\dist\assets" | Select-Object Name, @{N='Size(KB)';E={[math]::Round($_.Length/1KB,1)}}
```

### **Check Log Files**
```powershell
$extPath = "$env:USERPROFILE\.cursor\extensions\aimos.aimos-cursor-addon-1.2.0"
Get-ChildItem "$extPath\logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
```

---

## 🔄 **RELOAD AUTOMATION**

### **Reload Cursor Window**
```
Command: Ctrl+Shift+P → Developer: Reload Window  
Automated: vscode.commands.executeCommand('workbench.action.reloadWindow')
```

**When to use:** After every extension install

### **Restart Extension Host**
```
Command: Ctrl+Shift+P → Developer: Restart Extension Host
Automated: vscode.commands.executeCommand('workbench.action.restartExtensionHost')
```

**When to use:** If extension seems stuck

---

## 🛠️ **COMPLETE TESTING WORKFLOW**

### **Full Test Cycle (Automated)**
```powershell
# Navigate to extension directory
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon"

# Clean build
Write-Host "🧹 Cleaning old build..." -ForegroundColor Yellow
Remove-Item -Recurse -Force out, dist -ErrorAction SilentlyContinue

# Build React UI
Write-Host "⚛️ Building React UI..." -ForegroundColor Cyan
Set-Location "..\packages\ide_chat_app"
npm run build

# Build extension
Write-Host "🔨 Building extension..." -ForegroundColor Cyan
Set-Location "..\..\cursor-addon"
npm run compile

# Package
Write-Host "📦 Packaging..." -ForegroundColor Cyan
vsce package --out aimos-cursor-addon.vsix --allow-star-activation --allow-missing-repository

# Install
Write-Host "💿 Installing..." -ForegroundColor Cyan
code --install-extension aimos-cursor-addon.vsix --force

# Instructions
Write-Host "" 
Write-Host "✅ Build Complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Reload Cursor (Ctrl+Shift+P → Developer: Reload Window)" -ForegroundColor Yellow
Write-Host "  2. Check Output panel ('AIM-OS Extension')" -ForegroundColor Yellow
Write-Host "  3. Click sparkle icon in activity bar" -ForegroundColor Yellow
```

---

## 📝 **LOGGING & VERIFICATION**

### **Watch Live Logs**
```
1. View → Output
2. Select "AIM-OS Extension" from dropdown
3. Watch logs appear in real-time
```

### **Check Specific Log Events**
```
Expected activation sequence:
[0.001s] [SYSTEM] 🚀 AIM-OS Extension Logger Initialized
[0.002s] [ACTIVATION] 🚀 AIM-OS Extension activation started
[0.003s] [DASHBOARD] Creating dashboard provider...
[0.004s] [DASHBOARD] View ID to register: 'aimosDashboard'  ← CORRECT ID
[0.005s] [DASHBOARD:SUCCESS] ✅ Dashboard provider registered
[0.006s] [TEST:SUCCESS] ✅ Test panel registered
[0.007s] [COMMANDS:SUCCESS] ✅ Registered diagnostic commands
```

### **When Clicking Sparkle Icon**
```
Expected resolution sequence:
[WEBVIEW_RESOLVE] ═══════════════════════════════════════════
[WEBVIEW_RESOLVE] 🎯 resolveWebviewView TRIGGERED!!!
[WEBVIEW_RESOLVE] ═══════════════════════════════════════════
[WEBVIEW_RESOLVE] View ID: aimosDashboard
[DASHBOARD] Loading full HTML content...
[DIAGNOSTIC] HTML exists: true
[DIAGNOSTIC] Asset main-5fYGI1t7.js exists: true
[DIAGNOSTIC] Script replacements: 1 of 1 replaced
[DASHBOARD] ✅ Full HTML content loaded (XXXX chars)
```

---

## 🔧 **TROUBLESHOOTING AUTOMATION**

### **Complete Reset**
```powershell
# Uninstall extension
code --uninstall-extension aimos.aimos-cursor-addon

# Clean all build artifacts  
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon"
Remove-Item -Recurse -Force node_modules, out, dist -ErrorAction SilentlyContinue

# Reinstall dependencies
npm install

# Full build from scratch
Set-Location "..\packages\ide_chat_app"
npm run build
Set-Location "..\..\cursor-addon"
npm run compile
vsce package --out aimos-cursor-addon.vsix --allow-star-activation --allow-missing-repository
code --install-extension aimos-cursor-addon.vsix --force

# Reload Cursor
Write-Host "Now reload Cursor: Ctrl+Shift+P → Developer: Reload Window"
```

---

## 📋 **CURRENT STATUS CHECKS**

### **Quick Status Check**
```powershell
# Check extension installed
code --list-extensions | Select-String "aimos"

# Check version
$extPath = "$env:USERPROFILE\.cursor\extensions"
Get-ChildItem $extPath | Where-Object {$_.Name -like "*aimos*"} | Select-Object Name, LastWriteTime

# Check dist files present
$aimosExt = Get-ChildItem "$extPath\aimos.aimos-cursor-addon-*" | Select-Object -First 1
Test-Path "$($aimosExt.FullName)\dist\index.html"
Test-Path "$($aimosExt.FullName)\dist\assets\main-5fYGI1t7.js"
```

---

## 🎯 **WHAT I JUST FIXED**

### **The Problem:**
```
package.json: view ID = "aimosDashboard"
extension.ts: registered = "lucidOrchestratorDashboard"
                            ❌ MISMATCH!
```

### **The Fix:**
```
package.json: view ID = "aimosDashboard"
extension.ts: registered = "aimosDashboard"
                            ✅ MATCH!
```

---

## 🚀 **TO TEST THE FIX:**

**Just reload Cursor:**
```
Ctrl+Shift+P → Developer: Reload Window
```

**Then click the sparkle icon (✨)**

**You should see:**
- ✅ Dashboard panel opens (not "no provider")
- ✅ Shows fallback HTML or React UI
- ✅ Logs show `resolveWebviewView TRIGGERED`

---

## 💾 **SAVE THIS WORKFLOW**

For future debugging, always:
1. Build & install (script above)
2. Reload Cursor
3. Run diagnostic: `AIM-OS: Run Full Diagnostic`
4. Check logs in Output panel
5. Try to open views
6. Check if `resolveWebviewView` triggered

**The logs tell you EVERYTHING!**

---

**Created:** 2025-11-01  
**Fix Applied:** View ID mismatch corrected  
**Status:** READY TO TEST

---
