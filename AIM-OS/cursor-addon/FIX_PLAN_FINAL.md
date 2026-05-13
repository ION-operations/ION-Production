# FINAL FIX PLAN - Systematic Resolution
**Date:** 2025-11-01  
**Goal:** Get dashboard panel working in Cursor 2.0  
**Approach:** One variable at a time, verify each step

---

## 🔍 CURRENT STATE ANALYSIS

**What I Found:**
1. ✅ Only ONE webview provider registered (`PureHtmlDashboardProvider` for `aimosDashboard`)
2. ✅ No Tree View registrations in `extension.ts`
3. ✅ `.vscodeignore` correctly includes `dist/**`
4. ✅ Diagnostic logging exists in `PureHtmlDashboardProvider` (lines 25-27)
5. ❓ Tree View provider class exists but NOT registered anywhere visible

**Critical Question:** Is `resolveWebviewView()` being called?
- If logs show "🎯 Pure HTML Dashboard resolveWebviewView TRIGGERED!!!" → Method IS called, HTML should show
- If logs DON'T show that → Method NEVER called (Cursor 2.0 issue)

---

## 🎯 FIX STRATEGY

### **Phase 1: Enhanced Diagnostics (15 min)**
**Goal:** Confirm if `resolveWebviewView()` is called

**Changes:**
1. Add console.log at START of `resolveWebviewView()` (before any logger calls)
2. Add file-based logging (write to debug file immediately)
3. Add logging to extension activation
4. Build debug VSIX

**Test:**
- Install VSIX
- Open Cursor 2.0
- Open right sidebar AIM-OS panel
- Check logs for "RESOLVE FIRED" message

**Expected Outcomes:**
- **If logs show "RESOLVE FIRED"** → Method IS called, HTML should render → Issue is HTML/CSP
- **If logs DON'T show "RESOLVE FIRED"** → Method NEVER called → Cursor 2.0 platform issue

---

### **Phase 2A: If resolveWebviewView() IS Called**
**Problem:** HTML/CSP/security blocking rendering

**Fixes:**
1. Simplify CSP (allow everything for testing)
2. Remove TrustedTypes temporarily
3. Use inline scripts only (no modules)
4. Test with absolute minimal HTML

**Timeline:** 1 hour

---

### **Phase 2B: If resolveWebviewView() NEVER Called**
**Problem:** Cursor 2.0 not triggering method

**Alternatives:**
1. Try `createWebviewPanel` instead (editor area, not sidebar)
2. Try different activation events
3. Pivot to standalone Electron app (faster path)

**Timeline:** 2 hours for alternative #1, 1 day for Electron app

---

## 🛠️ IMPLEMENTATION PLAN

### **Step 1: Enhanced Diagnostics**
File: `cursor-addon/src/pureHtmlDashboardProvider.ts`

Add at line 20 (START of resolveWebviewView):
```typescript
public resolveWebviewView(...) {
    // IMMEDIATE FILE LOG (before any logger)
    const debugFile = path.join(this._context.extensionPath, 'resolve-called.txt');
    fs.writeFileSync(debugFile, `RESOLVE CALLED: ${new Date().toISOString()}\n`, 'utf8');
    
    // Console log (shows in Developer Tools)
    console.log('🎯🎯🎯 RESOLVE FIRED 🎯🎯🎯');
    
    // Continue with existing code...
}
```

### **Step 2: Extension Activation Logging**
File: `cursor-addon/src/extension.ts`

Add after line 22:
```typescript
AIMOSLogger.log('ACTIVATION', `Extension path: ${context.extensionPath}`);
AIMOSLogger.log('ACTIVATION', `VS Code version: ${vscode.version}`);

// NEW: File-based immediate log
const activationLog = path.join(context.extensionPath, 'activation-log.txt');
fs.writeFileSync(activationLog, `ACTIVATED: ${new Date().toISOString()}\nVS Code: ${vscode.version}\n`, 'utf8');
```

### **Step 3: Build Debug VSIX**
```bash
cd cursor-addon
npm run compile
npm run package
```

### **Step 4: Install & Test**
```bash
code --install-extension aimos-cursor-addon.vsix --force
```

**Test Steps:**
1. Open Cursor 2.0
2. Check `~/.cursor/extensions/aimos.aimos-cursor-addon-1.2.1/activation-log.txt` - Should show "ACTIVATED"
3. Open right sidebar AIM-OS panel
4. Check `~/.cursor/extensions/aimos.aimos-cursor-addon-1.2.1/resolve-called.txt` - Should show "RESOLVE CALLED"
5. Check Extension Host console (F1 → "Toggle Developer Tools" → Console tab) - Should show "🎯🎯🎯 RESOLVE FIRED 🎯🎯🎯"

---

## 📊 DECISION TREE

```
Is activation-log.txt created?
├─ NO → Extension not activating → Fix activation events
└─ YES → Continue

Is resolve-called.txt created when panel opened?
├─ NO → resolveWebviewView() never called → Cursor 2.0 issue → Use createWebviewPanel OR standalone app
└─ YES → Method IS called → Continue

Does panel show content?
├─ NO → HTML/CSP issue → Fix CSP, simplify HTML
└─ YES → ✅ SUCCESS!
```

---

## 🚀 NEXT STEPS

1. **Implement enhanced diagnostics** (this file)
2. **Build debug VSIX**
3. **Test in Cursor 2.0**
4. **Analyze results**
5. **Execute Phase 2A or 2B based on results**

---

**Status:** Ready to execute  
**Estimated Time:** 15 min diagnostics + 1-2 hours fix  
**Success Criteria:** User can SEE dashboard panel content

