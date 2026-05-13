# Command Cleanup Issue - Root Cause Found

**Problem:** Cursor is showing OLD commands from cached extension state

**What You're Seeing:**
- "AIM-OS: Open Dashboard Panel (Editor Area)"
- "AIM-OS: Show Dashboard"  
- "AIM-OS: Debug Dashboard"
- "AIM-OS: Force Open Dashboard"
- etc.

**What Should Be There:**
- "Open AIM-OS Dashboard" (only one!)

**Root Cause:**
1. Old compiled files in `out/` directory (not imported, but might be cached)
2. Cursor/VS Code caches extension commands - needs full reload
3. Old package.json commands still registered in Cursor's command registry

**Solution:**
1. Completely reload Cursor window (Ctrl+R or Developer: Reload Window)
2. If that doesn't work, uninstall and reinstall the extension
3. OR manually delete `out/` and rebuild fresh

**The Exact Command You Need:**
- **"Open AIM-OS Dashboard"** - This is the ONLY dashboard command now

This will open the React dashboard in the **editor area** (central panel), not the sidebar.

