# Sonnet's Unlogged Ideas - Cursor UI Panel Issue

**Created:** 2025-11-01  
**Status:** All ideas logged before proceeding  
**Purpose:** Document all thoughts before action

---

## 💡 **UNLOGGED IDEAS & THOUGHTS**

### **Idea 1: Multiple Webview Provider Instances**
**Thought:** What if we're creating multiple instances of `LucidOrchestratorDashboardProvider`?
- Line 17 in `extension.ts`: `new LucidOrchestratorDashboardProvider(context)`
- Then line 47: Registering same instance for `aimosDashboard`
- What if each registration creates a new instance internally?
- **Need to check:** Are we reusing the same provider instance or creating duplicates?

### **Idea 2: Extension Path Resolution at Runtime**
**Thought:** `this._context.extensionPath` might resolve differently than expected
- During development: `C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon`
- After installation: `C:\Users\bombe\.cursor\extensions\aimos-cursor-addon-1.2.0`
- **Need to verify:** What is the actual extension path when installed?
- **Diagnostic:** Aether's logging should show this, but worth explicit check

### **Idea 3: VSIX Packaging Issue**
**Thought:** What if `.vsix` file isn't including `dist/` folder correctly?
- `.vscodeignore` has `!dist/` (include dist)
- But what if build process doesn't copy `dist/` before packaging?
- **Need to verify:** Check `.vsix` contents (it's a zip file)
- **Test:** Extract `.vsix` and verify `dist/index.html` and `dist/assets/` exist

### **Idea 4: Build Script Execution Order**
**Thought:** Build script might run before React UI is built
- `build-extension.js` tries to copy `packages/ide_chat_app/dist/`
- But what if React build hasn't run yet?
- **Need to verify:** Does build script check if React dist exists first?
- **Test:** Run `npm run build` in `packages/ide_chat_app` first, then extension build

### **Idea 5: Webview CSP Source Value**
**Thought:** `webview.cspSource` might be wrong or undefined
- CSP uses `${webview.cspSource}` in meta tag
- If this is wrong, CSP blocks everything
- **Need to verify:** What value does `webview.cspSource` actually have?
- **Test:** Log `webview.cspSource` value in diagnostics

### **Idea 6: TrustedTypes Policy Timing**
**Thought:** TrustedTypes policy might need to be created BEFORE HTML is parsed
- Currently injecting script BEFORE `<head>` tag
- But HTML parser might execute scripts in order
- **Need to verify:** Does script execute before module scripts load?
- **Alternative:** Use inline script without type="module" for TrustedTypes

### **Idea 7: Module Script Import Chain**
**Thought:** Module scripts might import other modules that fail
- `main-5fYGI1t7.js` is a module script
- It might import other modules via `import` statements
- If those imports fail, entire script fails silently
- **Need to verify:** Check webview console for import errors
- **Test:** Load `main-5fYGI1t7.js` directly in browser console

### **Idea 8: React Root Element Mount Timing**
**Thought:** React might try to mount before DOM is ready
- `main-cursor.tsx` checks for `document.getElementById('root')`
- But webview might not have DOM ready yet
- **Need to verify:** Does React wait for DOMContentLoaded?
- **Test:** Add explicit `document.addEventListener('DOMContentLoaded', ...)`

### **Idea 9: Webview View vs Webview Panel**
**Thought:** Are we using the right webview type?
- `WebviewViewProvider` for sidebar panels
- `WebviewPanel` for editor panels
- User wants right-side panel (sidebar)
- **Need to verify:** Is `aimosDashboard` registered as WebviewViewProvider correctly?
- **Check:** `extension.ts` line 47 registration

### **Idea 10: Extension Activation Timing**
**Thought:** Extension might activate before webview is ready
- `activate()` function runs when extension loads
- But webview might not be created until user opens panel
- **Need to verify:** Does `resolveWebviewView()` get called when panel opens?
- **Test:** Check if diagnostic logs appear when panel opens

### **Idea 11: File System Case Sensitivity**
**Thought:** Windows file system might have case sensitivity issues
- HTML has `./assets/main-5fYGI1t7.js`
- File system might expect different case
- **Need to verify:** Are file names case-sensitive?
- **Test:** Check if `fs.existsSync()` finds files with exact case match

### **Idea 12: Cache Busting Query Params**
**Thought:** Query params might not work for webview URIs
- Added `?v=${cacheBuster}` to asset URIs
- But webview URIs might not support query params
- **Need to verify:** Do webview URIs accept query params?
- **Test:** Check if URI with query param loads correctly

### **Idea 13: React Build Output Format**
**Thought:** Vite might output different format than expected
- Checked `dist/index.html` - looks correct
- But what if Vite config changed?
- **Need to verify:** Is Vite config set correctly for extension?
- **Test:** Check `vite.config.ts` for base path, build settings

### **Idea 14: Extension Host Process Isolation**
**Thought:** Extension runs in separate process
- Extension Host is isolated from main Cursor process
- File system access might be restricted
- **Need to verify:** Can Extension Host access extension files?
- **Test:** Try `fs.readFileSync()` on extension path

### **Idea 15: Cursor-Specific Webview Limitations**
**Thought:** Cursor might have different webview behavior than VS Code
- Aether's question: "Does Cursor support webviews?"
- Forum reports suggest webviews don't work in Cursor
- **CRITICAL:** Need to verify this FIRST before all other fixes
- **Test:** Create minimal webview test extension

### **Idea 16: Extension Manifest View Registration**
**Thought:** `package.json` view registration might be wrong
- `aimosDashboard` registered in `views.aimos[0]`
- But what if Cursor doesn't recognize this view container?
- **Need to verify:** Is `aimos` view container supported?
- **Test:** Check if panel appears at all (even if blank)

### **Idea 17: React Error Boundary Silent Failures**
**Thought:** Error boundary might catch errors but not display them
- `main-cursor.tsx` has ErrorBoundary
- But error might be caught silently
- **Need to verify:** Does ErrorBoundary log errors?
- **Test:** Intentionally throw error in React component

### **Idea 18: Webview Message Passing**
**Thought:** Webview might not be receiving messages correctly
- `onDidReceiveMessage` handler exists
- But webview might not be initialized
- **Need to verify:** Does webview send/receive messages?
- **Test:** Send test message from extension to webview

### **Idea 19: Asset URI Path Resolution**
**Thought:** `webview.asWebviewUri()` might generate wrong paths
- URI should be `vscode-webview://...`
- But might be missing authority or path segments
- **Need to verify:** Check actual URI format from `asWebviewUri()`
- **Test:** Log full URI string and verify format

### **Idea 20: Extension Reload vs Cursor Restart**
**Thought:** Extension reload might not clear webview cache
- User restarted Cursor 30+ times
- But maybe extension reload is different?
- **Need to verify:** Does extension reload clear webview state?
- **Test:** Try extension reload vs full Cursor restart

---

## 🎯 **PRIORITY RANKING**

### **CRITICAL (Must Verify First):**
1. **Idea 15:** Cursor webview support (Aether's question)
2. **Idea 10:** Extension activation timing
3. **Idea 14:** Extension Host file system access

### **HIGH (Likely Causes):**
4. **Idea 3:** VSIX packaging issue
5. **Idea 19:** Asset URI path resolution
6. **Idea 5:** Webview CSP source value

### **MEDIUM (Possible Causes):**
7. **Idea 2:** Extension path resolution
8. **Idea 7:** Module script import chain
9. **Idea 12:** Cache busting query params

### **LOW (Unlikely but Possible):**
10. **Idea 1:** Multiple provider instances
11. **Idea 4:** Build script execution order
12. **Idea 11:** File system case sensitivity

---

## 📋 **NEXT ACTIONS**

1. ✅ Log all ideas (this document)
2. ⏳ Wait for Lexicon's response
3. ⏳ Verify Cursor webview support (Idea 15 - CRITICAL)
4. ⏳ Check Extension Host console logs (Aether's diagnostics)
5. ⏳ Test combined fixes (TrustedTypes + diagnostics)

---

**Status:** All ideas logged, ready for Lexicon's input  
**Confidence:** Need to verify Cursor webview support first (Idea 15)

