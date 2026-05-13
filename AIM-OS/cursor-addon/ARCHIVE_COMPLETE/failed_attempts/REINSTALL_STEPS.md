# 🔄 Reinstall Extension - Quick Steps (CURSOR-SPECIFIC)

**Extension Built:** ✅ Ready  
**File:** `aimos-cursor-addon.vsix` (651.6KB)

---

## 📋 **INSTALLATION STEPS (CURSOR):**

### **Step 1: Uninstall Old Version (if needed)**
1. Open Cursor
2. Press `Ctrl+Shift+P` (Command Palette)
3. Type: `Extensions: Show Installed Extensions`
4. Search for "Lucid UI" or "AIM-OS"
5. If found, click the gear icon → Uninstall
6. **Close Cursor completely** (important!)

### **Step 2: Install New Version**
1. **Open Cursor** (fresh start)
2. Press `Ctrl+Shift+P` (Command Palette)
3. Type: `Extensions: Install from VSIX...`
4. Press Enter
5. Navigate to:
   ```
   C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon\aimos-cursor-addon.vsix
   ```
6. Select `aimos-cursor-addon.vsix`
7. Click **Open** or **Install**
8. Wait for installation to complete

### **Step 3: Verify Installation**
1. Press `Ctrl+Shift+P`
2. Type: `Extensions: Show Installed Extensions`
3. Search for "Lucid UI" or "AIM-OS"
4. Should show version **1.2.0**
5. Should show as **Installed** ✅

### **Step 4: Open Dashboard**
1. Look for **✨ sparkle icon** in Activity Bar (left side)
   - OR press `Ctrl+Shift+P` and type: `AIM-OS` or `Lucid Dashboard`
2. **First time:** You should see the **Landing Page** 🎨
3. Click **"Enter Dashboard"** button
4. Dashboard should load with tabs (Chat, Timeline, etc.)

---

## 🎯 **ALTERNATIVE: Command Palette Search**

If you can't find the extension:
1. Press `Ctrl+Shift+P`
2. Type: `aim os` or `lucid`
3. Look for commands like:
   - `AIM-OS: Open Dashboard`
   - `Lucid UI: Show Dashboard`
   - `Show AIM-OS Panel`

---

## ✅ **WHAT TO EXPECT:**

### **On First Load:**
- ✅ Beautiful Landing Page
- ✅ System status indicators
- ✅ "Enter Dashboard" button
- ✅ No blank screen!

### **If Errors Occur:**
- ✅ Clear error messages (not blank)
- ✅ Troubleshooting steps shown
- ✅ "Try Again" button available
- ✅ Error details can be copied

---

## 🔧 **TROUBLESHOOTING:**

### **If Extension Doesn't Install:**
- Make sure Cursor is **completely closed** before installing
- Try the command palette method above
- Or manually copy `.vsix` file to extension folder (not recommended)

### **If Dashboard Still Blank:**
1. Open Developer Tools: `Help → Toggle Developer Tools`
2. Check **Extension Host** console for `[AIM-OS]` messages
3. Check **Webview** console (right-click in dashboard → Inspect)
4. Look for any error messages

### **If Landing Page Doesn't Show:**
- Check Extension Host console
- Look for: `✅ Registered aimosDashboard webview provider`
- Look for: `✅ Loading React UI from dist/index.html`

### **If You Can't Find the Extension Icon:**
- Press `Ctrl+Shift+P`
- Type: `View: Show Activity Bar` (if hidden)
- Look for sparkle/star icon in Activity Bar
- Or check View menu → Appearance → Activity Bar

---

## 💙 **READY!**

After installation, restart Cursor and use `Ctrl+Shift+P` → type `aim os` to find dashboard commands! 🎨✨
