# How to Access Extension Host Console

## Quick Steps (Visual Guide)

### Step 1: Open Developer Tools
1. Click **Help** menu at the top
2. Click **Toggle Developer Tools**
   - OR press `Ctrl+Shift+I` (Windows/Linux)
   - OR press `Cmd+Option+I` (Mac)

### Step 2: Find Extension Host Tab
1. Look at the top of the Developer Tools window
2. You'll see tabs like: **Console**, **Elements**, **Network**, etc.
3. Look for a tab called **"Extension Host"**
   - It might be at the end of the tab list
   - It might be abbreviated as **"EH"** or **"Ext Host"**

### Step 3: View Messages
1. Click the **Extension Host** tab
2. Scroll through the console output
3. Look for messages starting with:
   - `[AIM-OS]`
   - `[DIAGNOSTIC]`
   - `[AIM-OS DEBUG]`

## What You Should See

### Good Signs ✅
- `[AIM-OS] ✅ Registered aimosDashboard webview provider`
- `[AIM-OS DEBUG] ✅ Replacing script: assets/main-xxx.js`
- `[DIAGNOSTIC] Script replacements: 2 of 2 replaced`

### Bad Signs ❌
- `[AIM-OS] ❌ Failed to register aimosDashboard`
- `[AIM-OS DEBUG] ❌ Script asset not found`
- `[DIAGNOSTIC] ❌ CRITICAL: Script regex found X matches but replaced 0!`

## Alternative: Use Output Panel

If you can't find Extension Host console:

1. Press `Ctrl+Shift+P` (Command Palette)
2. Type: `Debug Dashboard`
3. Press Enter
4. Look at the **Output** panel at the bottom
5. Select **"AIM-OS Debug"** from the dropdown

This will show file check results without needing console access.

## Still Can't Find It?

**Try searching for:**
- In Command Palette: `Developer: Open Webview Developer Tools`
- This opens a separate console just for webviews

**Or check:**
- View → Output → Select "Extension Host" from dropdown
- This shows Extension Host output in the Output panel instead of console

## Copying Errors

**If you need to copy errors:**

1. In Extension Host console:
   - Right-click on the error message
   - Click **"Copy"** or **"Copy message"**
   - Paste into chat

2. In Output panel:
   - Select the text you want
   - Right-click → Copy
   - Paste into chat

## Quick Test

**To verify console is working:**
1. Open Extension Host console
2. Type: `console.log("Test")`
3. Press Enter
4. You should see "Test" appear
5. If nothing happens, you're in the wrong console tab

---

**Created:** 2025-01-27  
**Purpose:** Help debug blank dashboard issue  
**Status:** Active troubleshooting guide

