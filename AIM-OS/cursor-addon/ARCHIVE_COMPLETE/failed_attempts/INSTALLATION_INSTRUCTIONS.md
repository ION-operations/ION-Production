# 📦 Installation Instructions

**Extension Version:** 1.2.0 with Landing Page & Error Handling  
**Date:** 2025-01-27

---

## 🚀 **QUICK INSTALL**

### **Option 1: Automatic (PowerShell Script)**
```powershell
cd cursor-addon
powershell -ExecutionPolicy Bypass -File INSTALL_NOW.ps1
```

### **Option 2: Manual Steps**

1. **Build Extension:**
   ```powershell
   cd cursor-addon
   npm run build
   npm run package
   ```

2. **Install Extension:**
   - Open Cursor
   - Press `Ctrl+Shift+X` (or View → Extensions)
   - Click `...` menu (top right)
   - Select `Install from VSIX...`
   - Navigate to: `cursor-addon/aimos-cursor-addon.vsix`
   - Select file and click Install
   - Restart Cursor

---

## ✅ **VERIFY INSTALLATION**

1. **Check Extension:**
   - Extensions view (Ctrl+Shift+X)
   - Search for "Lucid UI - AIM-OS"
   - Should show version **1.2.0**

2. **Open Dashboard:**
   - Click sparkle icon (✨) in Activity Bar
   - Should see **Landing Page** first
   - Click "Enter Dashboard" to access dashboard

3. **Check Console:**
   - Help → Toggle Developer Tools
   - Look for `[AIM-OS]` messages
   - Should see: `✅ Registered aimosDashboard webview provider`

---

## 🎨 **WHAT'S NEW**

### **Landing Page:**
- ✅ Beautiful welcome screen
- ✅ System status indicators
- ✅ Feature preview cards
- ✅ "Enter Dashboard" button

### **Error Handling:**
- ✅ Error boundary catches all errors
- ✅ Clear error messages
- ✅ Troubleshooting steps
- ✅ "Try Again" button
- ✅ No more blank screens!

---

## 🔧 **TROUBLESHOOTING**

### **If Extension Doesn't Install:**
1. Uninstall old version first
2. Close Cursor completely
3. Try manual installation
4. Check file exists: `cursor-addon/aimos-cursor-addon.vsix`

### **If Dashboard Shows Blank:**
1. Check Developer Console for `[AIM-OS]` messages
2. Look for error messages
3. Try clicking "Enter Dashboard" on landing page
4. Check if landing page shows (good sign!)

### **If Landing Page Doesn't Show:**
1. Check Extension Host console
2. Look for `resolveWebviewView called` message
3. Verify `dist/index.html` exists in extension
4. Try reloading extension

---

## 💙 **READY TO USE!**

After installation, you should see:
- ✅ Landing page on first load
- ✅ Beautiful welcome screen
- ✅ Clear error messages if anything fails
- ✅ Easy access to dashboard

**Enjoy the improved UX!** 🎨✨

