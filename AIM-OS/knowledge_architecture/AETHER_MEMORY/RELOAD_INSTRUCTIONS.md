# Extension Reload Instructions

**Status:** Command Server not accessible - Manual reload required

---

## 🔄 **HOW TO RELOAD EXTENSION**

### **Method 1: Command Palette (Recommended)**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type: `Developer: Reload Window`
3. Press Enter
4. Wait for window to reload (~2-3 seconds)

### **Method 2: Keyboard Shortcut**
- Press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac)
- This reloads the extension without full restart

### **Method 3: Restart Extension Host**
1. Press `Ctrl+Shift+P`
2. Type: `Developer: Restart Extension Host`
3. Press Enter
4. Less intrusive than full reload

---

## ✅ **AFTER RELOAD - VERIFY IT WORKED**

### **Check Logs:**
After reload, check `cursor-addon/docs/LATEST_LOGS.md`:
- Look for: `[COMMAND_SERVER:SUCCESS] ✅ Command server started on port 5001`
- If you see this, Command Server is running with new code

### **Test Terminal Tools:**
```python
# Test 1: List terminals
mcp_lucid-mcp_list_terminals({})

# Test 2: Manage terminals  
mcp_lucid-mcp_manage_terminals({"threshold": 5})
```

---

## 🔍 **TROUBLESHOOTING**

### **If Reload Doesn't Work:**
1. **Full restart:** Close and reopen Cursor
2. **Rebuild extension:** `cd cursor-addon && npm run compile`
3. **Reinstall extension:** `cd cursor-addon && npm run package && cursor --install-extension aimos-cursor-addon.vsix --force`

---

**Status:** Ready for reload  
**Next Step:** Reload Cursor window manually  
**Confidence:** 0.95 (high - code is ready, just needs reload)

---

*Reload instructions created by Aether*  
*2025-01-27*


