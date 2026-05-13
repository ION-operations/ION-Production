# CRITICAL DEBUGGING STEPS

## Step 1: Check Output Panel
1. Open **Output panel** (bottom of Cursor)
2. Click dropdown → Select **"AIM-OS Dashboard"**
3. Look for diagnostic messages starting with `[DIAGNOSTIC]`
4. **Copy ALL messages** and share them

## Step 2: Check Extension Host Console
1. Press `Ctrl+Shift+P`
2. Type: `Developer: Toggle Developer Tools`
3. Go to **Console** tab
4. Look for messages starting with `[AIM-OS]` or `[DIAGNOSTIC]`
5. **Copy any errors** (red text)

## Step 3: Check Webview Console
1. With dashboard panel open (even if blank)
2. Right-click in the blank panel → **Inspect** (or F12)
3. Check **Console** tab for JavaScript errors
4. **Copy ALL errors** (especially red ones)

## Step 4: Verify Files Exist
Run this command in terminal:
```powershell
cd cursor-addon
Test-Path dist/index.html
Test-Path dist/assets
Get-ChildItem dist/assets -Recurse | Select-Object Name, Length
```

## What We're Looking For:
- ✅ Is HTML file found?
- ✅ Are assets being loaded?
- ✅ Any JavaScript errors?
- ✅ Is React mounting?
- ✅ Any CSP/TrustedTypes errors?

**Please share the output from Steps 1-3 above.**

