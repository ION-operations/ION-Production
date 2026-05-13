# 🔍 Blank Dashboard Issue - Research & Analysis

**Status:** Paused - Research Phase  
**Date:** 2025-11-01  
**Team:** Aether, Sonnet, Scribe (coordinating)  
**Approach:** Research first, code changes only after understanding root cause

---

## 🎯 **PROBLEM STATEMENT**

**Symptom:** Dashboard panel shows completely blank (white/empty)  
**Duration:** 30+ restarts, multiple rebuilds, no resolution  
**User Impact:** Cannot use dashboard at all

---

## ✅ **WHAT WE KNOW WORKS**

1. **Extension Installation:**
   - ✅ Extension installs successfully (`aimos-cursor-addon.vsix`)
   - ✅ Version 1.2.0 installed at: `C:\Users\bombe\.cursor\extensions\aimos.aimos-cursor-addon-1.2.0`
   - ✅ Extension activates (we see console logs)

2. **Files Present:**
   - ✅ `dist/index.html` exists (1080 chars)
   - ✅ `dist/assets/main-5fYGI1t7.js` exists (243KB)
   - ✅ `dist/assets/main-DftvcEcs.css` exists (48KB)
   - ✅ `dist/assets/cursor-CrCpYETP.js` exists (72 bytes)
   - ✅ `dist/assets/HttpLucidDaemonService-BjCmj4eb.js` exists (5KB)

3. **Code Features Implemented:**
   - ✅ Landing Page component (`LandingPage.tsx`)
   - ✅ Error Boundary component (`ErrorBoundary.tsx`)
   - ✅ Main Dashboard with tabs
   - ✅ Asset path replacement logic
   - ✅ CSP meta tag injection
   - ✅ Debug logging throughout

---

## ❌ **WHAT WE DON'T KNOW**

1. **Is HTML Actually Loading?**
   - Does `resolveWebviewView` get called?
   - Is `getWebviewContent` returning HTML?
   - What does the final HTML look like after asset replacement?

2. **Are Scripts Executing?**
   - Do scripts load (Network tab)?
   - Do scripts execute (Console errors)?
   - Is React mounting (`main-cursor.tsx`)?

3. **Why Blank Screen?**
   - Is it blank HTML (no content)?
   - Is it React failing to mount?
   - Is it CSS hiding content?
   - Is it CSP blocking scripts?

4. **What Do Console Logs Say?**
   - Extension Host console: `[AIM-OS]` messages?
   - Webview console: Any errors? (How to access?)
   - Network tab: Scripts loading?

---

## 🐛 **ERRORS USER REPORTED EARLIER**

### Error 1: TrustedScript Assignment
```
This document requires 'TrustedScript' assignment.
The JavaScript Function constructor does not accept TrustedString arguments.
```
**Analysis Needed:**
- What is TrustedScript/TrustedTypes?
- How does it affect VS Code webviews?
- Is CSP too restrictive or too permissive?

### Error 2: Composite Descriptor
```
no composite descriptor found for workbench.view.extension.aimos
```
**Analysis Needed:**
- What is a composite descriptor?
- Is webview view registered correctly?
- Is `package.json` configuration correct?

---

## 📋 **RESEARCH QUESTIONS**

### Question 1: VS Code Webview Architecture
- How do `WebviewViewProvider` and `WebviewPanel` differ?
- How does `resolveWebviewView` work?
- What happens when `webview.html` is set?
- How does `asWebviewUri` convert file paths?
- What is `webview.cspSource`?

### Question 2: Debugging Webviews
- How to debug webview without restart?
- How to access webview console?
- Where are Extension Host console logs?
- Can we inspect webview HTML after it's set?
- Is there a way to reload webview?

### Question 3: Common Blank Webview Causes
- What causes blank webviews in VS Code extensions?
- CSP violations?
- Script loading failures?
- React mounting failures?
- Asset path issues?

### Question 4: Trusted Types & CSP
- What are Trusted Types?
- How do they interact with VS Code webviews?
- What CSP policy does VS Code enforce?
- Can we bypass Trusted Types in webviews?

---

## 🔬 **DEBUGGING PLAN**

### Step 1: Verify Extension Host Console
**Action:** Check Extension Host console for `[AIM-OS]` messages  
**How:** 
1. Help → Toggle Developer Tools
2. Click "Extension Host" tab
3. Look for messages starting with `[AIM-OS]`
4. Copy all relevant messages

**What to Look For:**
- `resolveWebviewView called`
- `HTML content set (length: X chars)`
- `Replaced X asset path(s)`
- Any errors

### Step 2: Run Debug Command
**Action:** Run `aimos.debugDashboard` command  
**How:**
1. Ctrl+Shift+P
2. Type: `Debug Dashboard`
3. Press Enter
4. Check Output panel ("AIM-OS Debug")

**What to Look For:**
- File existence confirmation
- Script tags in HTML
- Asset file list

### Step 3: Inspect Actual HTML Loaded
**Action:** Add logging to capture final HTML  
**Method:** Log the HTML content after all replacements  
**Goal:** See what HTML is actually being set to webview

### Step 4: Test Minimal Webview
**Action:** Create minimal test webview  
**Method:** Simple HTML with inline script  
**Goal:** Verify webview mechanism works at all

---

## 🎯 **HYPOTHESES TO TEST**

### Hypothesis 1: Asset Path Replacement Failing
**Theory:** Regex isn't matching script tags correctly  
**Test:** Log replaced HTML, verify script src URLs are `vscode-webview://`  
**Fix:** Improve regex or use different replacement method

### Hypothesis 2: CSP Blocking Scripts
**Theory:** CSP meta tag isn't working or too restrictive  
**Test:** Check CSP in final HTML, test with minimal CSP  
**Fix:** Adjust CSP policy or use different approach

### Hypothesis 3: Trusted Types Blocking Scripts
**Theory:** Trusted Types errors prevent script execution  
**Test:** Research Trusted Types in VS Code webviews  
**Fix:** Use Trusted Types API or disable if possible

### Hypothesis 4: React Not Mounting
**Theory:** Scripts load but React fails to mount  
**Test:** Check webview console for React errors  
**Fix:** Fix React mounting issue or add better error handling

### Hypothesis 5: Wrong Webview Type
**Theory:** Using wrong webview API or configuration  
**Test:** Compare with working webview examples  
**Fix:** Use correct webview type/config

---

## 📚 **RESOURCES TO RESEARCH**

1. **VS Code Extension API Docs:**
   - WebviewViewProvider
   - WebviewPanel
   - Webview API
   - Content Security Policy

2. **VS Code Extension Samples:**
   - Official webview samples
   - React webview examples
   - WebviewView examples

3. **Trusted Types:**
   - MDN: Trusted Types API
   - VS Code webview security
   - CSP in webviews

4. **Common Issues:**
   - VS Code webview blank screen
   - Webview scripts not loading
   - CSP violations in webviews

---

## 🚫 **WHAT NOT TO DO**

- ❌ Make code changes without understanding
- ❌ Keep asking user to restart
- ❌ Guess at solutions
- ❌ Change multiple things at once
- ❌ Ignore error messages

---

## ✅ **NEXT STEPS**

1. **Research Phase (NOW):**
   - Investigate VS Code webview architecture
   - Research Trusted Types in webviews
   - Study working webview examples
   - Understand CSP in webviews

2. **Debugging Phase:**
   - Get Extension Host console logs
   - Run debug command
   - Inspect actual HTML loaded
   - Test minimal webview

3. **Analysis Phase:**
   - Compare actual vs expected behavior
   - Identify root cause
   - Document findings

4. **Fix Phase (ONLY AFTER UNDERSTANDING):**
   - Implement targeted fix
   - Test thoroughly
   - Verify solution

---

**Status:** Researching - No code changes until root cause identified  
**Team Coordination:** Contacting Sonnet & Scribe for parallel research  
**User:** Run debug command and share Extension Host console logs

