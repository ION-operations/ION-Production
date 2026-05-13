# HOW TO TEST THE PANEL

**Date:** 2025-11-02  
**Status:** TESTING INSTRUCTIONS

---

## 🧪 **TEST STEPS**

1. **Reload Cursor Extension:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type: `Developer: Reload Window`
   - Press Enter

2. **Open Test Panel:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type: `AIMOS: Test Panel (Simple)`
   - Press Enter

3. **What You Should See:**
   - Panel opens in editor area (next to your code)
   - Green border around the panel
   - Text saying "✅ TEST PANEL WORKING!"
   - Current time displayed

4. **If Panel Doesn't Open:**
   - Check Output panel: `View` → `Output` → Select "AIMOS Extension"
   - Look for error messages
   - Check Developer Console: `Help` → `Toggle Developer Tools`

---

## 🔍 **DIAGNOSTICS**

### **Command Registered?**
- Open Command Palette (`Ctrl+Shift+P`)
- Type `aimos.test`
- Should see "AIMOS: Test Panel (Simple)"

### **Extension Active?**
- Check Output panel
- Look for "🚀 AIM-OS Extension activation started"

### **Panel Opens But Blank?**
- Check Developer Console (`Help` → `Toggle Developer Tools`)
- Look for JavaScript errors
- Check Network tab for failed requests

---

## 🚨 **COMMON ISSUES**

### **Issue: Command Not Found**
**Solution:** Extension not reloaded - reload window

### **Issue: Panel Opens But Blank**
**Solution:** Check Developer Console for errors

### **Issue: Panel Doesn't Open**
**Solution:** Check Output panel for activation errors

---

## 📝 **NEXT STEPS**

Once test panel works:
1. ✅ We know `createWebviewPanel` works
2. ✅ We can build custom chat panel on top
3. ✅ We can add message passing
4. ✅ We can integrate with Command Server

**Status:** Waiting for test results  
**Next:** Build custom chat panel once test panel confirms webviews work

