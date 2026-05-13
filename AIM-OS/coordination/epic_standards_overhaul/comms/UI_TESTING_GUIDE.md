# Cursor UI Extension - Testing Guide (Before Daemon Ready)

**Created:** 2025-10-31  
**Purpose:** Test UI extension look and feel before Solo completes HTTP API server  
**Status:** Ready for Testing  
**Agent:** Lexicon + Aether

---

## 🎯 **TESTING GOAL**

**Test the UI extension NOW** to:
- ✅ See how it looks and feels
- ✅ Test panel positioning
- ✅ Test UI interactions
- ✅ Provide feedback on UX
- ✅ Identify improvements before backend integration

**Note:** The extension has **fallback HTML** that works without the daemon running, so we can test the UI immediately!

---

## 🚀 **QUICK INSTALL & TEST**

### **Step 1: Verify Extension File**

```powershell
# From AIM-OS root directory
cd cursor-addon
dir aimos-cursor-addon.vsix
```

**Expected:** File should exist (~4.6 MB)

### **Step 2: Install Extension**

**Windows (PowerShell):**
```powershell
cd cursor-addon
npm run install:windows
```

**Or Manual Installation:**
```powershell
# Close Cursor/VSCode first!
code --install-extension cursor-addon\aimos-cursor-addon.vsix --force
```

**Linux/Mac:**
```bash
cd cursor-addon
npm run install:unix
```

### **Step 3: Reload Cursor/VSCode**

- Close Cursor/VSCode completely
- Reopen Cursor/VSCode
- Extension should be active

### **Step 4: Open Dashboard**

**Method 1: Command Palette**
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type: `AIM-OS: Show Lucid Orchestrator Dashboard`
3. Select the command

**Method 2: Activity Bar**
1. Look for 🧠 (brain) icon in Activity Bar
2. Click it → Click "Dashboard"

**Method 3: Bottom Panel**
1. Look for 📊 (dashboard) icon in bottom panel
2. Click it → Click "Lucid Dashboard"

---

## 🎨 **WHAT YOU'LL SEE**

### **Fallback HTML (Current State)**

The extension will show **fallback HTML** with:
- ✅ **Feature Preview** - All planned features visible
- ✅ **UI Layout** - Panel positioning works
- ✅ **Controls** - Buttons and UI elements visible
- ⚠️ **Mock Data** - Uses placeholder data (daemon not running)

### **Features to Test:**

1. **Panel Positioning**
   - Move panel to different positions
   - Test sidebar (left/right)
   - Test bottom panel
   - Test floating window

2. **UI Elements**
   - Model selector (Gemini/Cerebras/Auto)
   - Daemon connection controls
   - Agent management buttons
   - MCP tools interface
   - Status indicators

3. **Visual Design**
   - Colors and styling
   - Layout and spacing
   - Typography
   - Icons and buttons

4. **User Experience**
   - Navigation flow
   - Button interactions
   - Panel resizing
   - Responsive design

---

## ✅ **TESTING CHECKLIST**

### **Installation:**
- [ ] Extension installs successfully
- [ ] No errors in extension output panel
- [ ] Extension appears in Extensions list

### **Dashboard Access:**
- [ ] Command Palette command works
- [ ] Activity Bar icon appears
- [ ] Dashboard opens successfully
- [ ] No console errors

### **Panel Positioning:**
- [ ] Panel can be moved to left sidebar
- [ ] Panel can be moved to right sidebar
- [ ] Panel can be moved to bottom panel
- [ ] Panel position persists after reload

### **UI Elements:**
- [ ] Model selector visible and functional
- [ ] Daemon connection controls visible
- [ ] Agent management interface visible
- [ ] MCP tools interface visible
- [ ] Status indicators visible

### **Visual Design:**
- [ ] Colors look good
- [ ] Layout is clean and organized
- [ ] Typography is readable
- [ ] Icons are clear
- [ ] Spacing is appropriate

### **User Experience:**
- [ ] Navigation feels intuitive
- [ ] Buttons are clearly labeled
- [ ] Panel resizing works smoothly
- [ ] No UI glitches or bugs

---

## 📊 **FEEDBACK TO PROVIDE**

After testing, please provide feedback on:

1. **What Works Well:**
   - What do you like about the UI?
   - What feels intuitive?
   - What looks good?

2. **What Needs Improvement:**
   - What's confusing?
   - What's missing?
   - What needs better design?

3. **Specific Issues:**
   - Any bugs or errors?
   - Any UI glitches?
   - Any performance issues?

4. **Suggestions:**
   - Layout improvements
   - Feature additions
   - UX enhancements
   - Visual design tweaks

---

## 🔄 **NEXT STEPS**

### **After Testing:**

1. **Report Feedback** → Share findings with Lexicon
2. **Fix Issues** → Lexicon addresses UI problems
3. **Iterate** → Test again after fixes
4. **Wait for Solo** → Once HTTP API server ready, test full integration

### **When Solo Completes HTTP API:**

1. **Start Daemon** → Run HTTP API server on port 5000
2. **Test Connection** → Verify UI connects to daemon
3. **Test Functionality** → Test real-time updates, tool selection, etc.
4. **Final Polish** → Complete integration testing

---

## 🚨 **TROUBLESHOOTING**

### **Extension doesn't install:**
- Ensure Cursor/VSCode is closed
- Try manual installation: `code --install-extension cursor-addon\aimos-cursor-addon.vsix --force`
- Check extension output panel for errors

### **Dashboard doesn't open:**
- Check extension output panel for errors
- Try reloading Cursor/VSCode
- Verify extension is activated (check Extensions list)

### **Fallback HTML shows:**
- **This is expected!** Fallback HTML is intentional when daemon isn't running
- It provides full feature preview with mock data
- Real functionality will work once Solo's HTTP API server is ready

### **UI looks broken:**
- Check browser console in webview (right-click → Inspect)
- Check extension output panel for errors
- Report specific issues to Lexicon

---

## 💙 **SUMMARY**

**You can test the UI NOW!** The extension is ready, has fallback HTML for testing, and will work perfectly for UI/UX evaluation even without the daemon running.

**Install → Test → Feedback → Iterate → Wait for Solo → Full Integration!**

---

**Status:** Ready for testing! Install and test UI now! 💙✨

