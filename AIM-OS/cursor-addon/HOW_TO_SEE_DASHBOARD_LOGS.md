# How to See Dashboard Loading Messages

## Step 1: Check Output Panel Dropdown
1. Look at the **Output panel** (bottom panel)
2. Click the **dropdown** at the top right that says "AIM-OS Debug"
3. Look for **"AIM-OS Dashboard"** in the dropdown list
4. If you see it, select it

## Step 2: Open the Dashboard Panel
1. **Open the dashboard panel** (right side panel with the dashboard)
2. When it loads, it should automatically show messages in "AIM-OS Dashboard" output channel
3. If the output panel doesn't automatically open, manually select "AIM-OS Dashboard" from the dropdown

## Step 3: What You Should See
When the dashboard loads, you should see messages like:
```
[AIM-OS] ========================================
[AIM-OS] resolveWebviewView called - setting up webview
[AIM-OS] Webview view ID: aimosDashboard
[DIAGNOSTIC] ========================================
[DIAGNOSTIC] UI PANEL LOADING DIAGNOSTIC START
[DIAGNOSTIC] Extension path: c:\Users\bombe\.cursor\extensions\aimos.aimos-cursor-addon-1.2.0
[DIAGNOSTIC] HTML exists: true
[DIAGNOSTIC] Asset main-5fYGI1t7.js exists: true
...
```

## If You Don't See "AIM-OS Dashboard" in Dropdown
- The dashboard might not have loaded yet
- Try opening/closing the dashboard panel
- Or restart Cursor to ensure extension is fully loaded

## Quick Test
1. Close the dashboard panel (if open)
2. Reopen it
3. Immediately check Output panel dropdown for "AIM-OS Dashboard"
4. Select it and see if messages appear

---

**Created:** 2025-01-27  
**Purpose:** Find dashboard loading diagnostics  
**Status:** Active troubleshooting guide

