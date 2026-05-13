# 🔍 How to Debug Extension Now

**Date:** 2025-01-27  
**Status:** Enhanced logging added - ready to debug!

---

## ✅ **WHAT I ADDED**

### **Comprehensive Logging:**
1. **Extension Host Console** - All `[AIM-OS]` messages visible in main Cursor console
2. **User Notifications** - Popup when dashboard loads
3. **React UI Logging** - Detailed logs in webview console
4. **Error Handling** - Catches and logs registration errors

---

## 🚀 **STEP-BY-STEP DEBUGGING**

### **Step 1: Rebuild & Reinstall**
```powershell
cd cursor-addon
npm run build
npm run package
# Then reinstall extension (uninstall old, install new)
```

### **Step 2: Restart Cursor**
- Close Cursor completely
- Reopen Cursor
- Wait for extension to activate

### **Step 3: Open Developer Tools**
1. **Help → Toggle Developer Tools**
2. Click **Console** tab (or look for "Extension Host" tab)
3. **Filter by:** `[AIM-OS]` (or just scroll for messages)

### **Step 4: Open Dashboard Panel**
1. Click **sparkle icon** in Activity Bar (left sidebar)
2. Should see **"Dashboard"** view
3. **Look for popup:** "AIM-OS Dashboard loading... Check Developer Console for details."

### **Step 5: Check Extension Console**
**Look for these messages (in order):**
```
[AIM-OS] AIM-OS Cursor Add-on is now active!
[AIM-OS] ✅ Registered aimosDashboard webview provider
[AIM-OS] resolveWebviewView called - setting up webview
[AIM-OS] Webview view ID: aimosDashboard
[AIM-OS] Extension path: C:\Users\...\extensions\aimos-cursor-addon-1.2.0
[AIM-OS DEBUG] Extension path: ...
[AIM-OS DEBUG] Looking for HTML at: ...
[AIM-OS DEBUG] File exists: true/false
[AIM-OS DEBUG] ✅ Found React UI HTML! Loading...
[AIM-OS] ✅ Webview HTML content set (length: XXXX chars)
```

**If you see:**
- ✅ All messages = Extension working, files found
- ❌ `dist/index.html not found` = Files missing, need rebuild
- ❌ `Failed to register` = Registration error

### **Step 6: Check Webview Console**
1. **Right-click in dashboard panel** → **Inspect**
2. Click **Console** tab
3. **Look for:**
```
[AIM-OS] ========================================
[AIM-OS] main-cursor.tsx loaded - attempting to mount React UI
[AIM-OS] Document ready state: complete
[AIM-OS] Window location: vscode-webview://...
[AIM-OS] ========================================
[AIM-OS] ✅ Root element found, mounting React...
[AIM-OS] ✅ React UI mounted successfully!
[AIM-OS] MainDashboard component loading...
[AIM-OS] ✅ MainDashboard mounted successfully!
```

**If you see:**
- ✅ All messages = React working!
- ❌ `Root element not found` = HTML structure issue
- ❌ `Error mounting React UI` = React error (check error details)

### **Step 7: Check Network Tab**
1. In webview DevTools → **Network** tab
2. **Reload panel** (close/reopen or refresh)
3. **Check if these load:**
   - `main-*.js` → Should be 200 OK
   - `main-*.css` → Should be 200 OK

**If you see:**
- ✅ 200 OK = Assets loading correctly
- ❌ 404 Not Found = Asset paths wrong, need rebuild

---

## 📋 **SHARE THESE LOGS**

**After following steps above, share:**

1. **Extension Console** (`[AIM-OS]` messages):
```
Copy all [AIM-OS] messages from Extension Host console
```

2. **Webview Console** (`[AIM-OS]` messages):
```
Copy all [AIM-OS] messages from webview console
```

3. **Any Errors:**
```
Even if you can't copy, describe what you see
```

4. **Network Tab:**
```
Do assets load? (200 OK or 404?)
```

---

## 🎯 **QUICK CHECKLIST**

- [ ] Extension rebuilt and reinstalled
- [ ] Cursor restarted
- [ ] Developer Tools open
- [ ] Dashboard panel opened
- [ ] Extension console checked
- [ ] Webview console checked
- [ ] Network tab checked
- [ ] Logs shared

---

## 💙 **WHAT TO EXPECT**

**If everything works:**
- Extension console shows all ✅ messages
- Webview console shows React mounting
- Dashboard shows tabs (Agents, Chat, Chains, etc.)
- No errors

**If something's wrong:**
- Extension console will show ❌ messages
- Webview console will show errors
- We'll know exactly what to fix!

---

**Now we can actually see what's happening!** 🔍✨

