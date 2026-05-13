# Simple Solution: Load Extension from Folder

**Problem:** Cursor is loading an old installed extension with old commands.

**Easiest Solution:** Load extension directly from folder (no F5 needed!)

## Steps:

1. **Open Command Palette:** `Ctrl+Shift+P`

2. **Type:** `Developer: Install Extension from Location...`

3. **OR** Type: `Extensions: Install from VSIX...` and navigate to `cursor-addon` folder

4. **OR** Even simpler - just navigate to the extension folder:
   - `Ctrl+Shift+P` → `Extensions: Show Installed Extensions`
   - Click the `...` menu (top right)
   - Select `Install from VSIX...`
   - Navigate to `cursor-addon` folder

## Alternative: Use Command to Load Folder

1. `Ctrl+Shift+P`
2. Type: `Developer: Install Extension from Location...`
3. Select the `cursor-addon` folder
4. Reload window

## After Loading:

In the NEW window that opens, type "aim" - you should see ONLY:
- **"Open AIM-OS Dashboard"** ✅

This will open the React dashboard in the **editor area** (central panel).

