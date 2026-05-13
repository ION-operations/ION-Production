# Extension Command Cache Issue - Solution

**Problem:** Cursor is showing OLD commands because it's loading an installed extension, not the development version.

**Solution:** We need to tell Cursor to use the LOCAL development version instead of the installed one.

## Option 1: Load Extension from Folder (Development Mode)

1. **Open Command Palette:** `Ctrl+Shift+P`
2. **Type:** `Developer: Reload Window with Extension Development Host`
3. **OR** Press `F5` to launch extension host

This will load the extension from your local `cursor-addon` folder, not the installed version.

## Option 2: Uninstall and Reinstall

If Option 1 doesn't work:

1. **Uninstall extension:**
   - `Ctrl+Shift+P` → `Extensions: Show Installed Extensions`
   - Find "AIM-OS Cursor Add-on"
   - Click Uninstall

2. **Install from local folder:**
   - `Ctrl+Shift+P` → `Extensions: Install from VSIX...`
   - Navigate to `cursor-addon/aimos-cursor-addon.vsix` (if it exists)
   - OR load directly from folder using Option 1 above

## Option 3: Force Reload (Quick Fix)

1. Close Cursor completely
2. Delete extension cache: `%USERPROFILE%\.cursor\extensions\aimos-cursor-addon-*`
3. Restart Cursor
4. Load extension from folder (Option 1)

**The command you need after reload:**
- **"Open AIM-OS Dashboard"** - Only one command now!

