# MCP Dual Server Setup

**Date:** 2025-10-25  
**Status:** ✅ ACTIVE - Both servers configured

---

## 🎯 CONFIGURATION

Both servers are configured in: `c:\Users\bombe\.cursor\mcp.json`

```json
{
  "mcpServers": {
    "aimos-6-tools": {
      "command": "python",
      "args": ["-u", "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\run_mcp_6_tools.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
      }
    },
    "aimos-test-server": {
      "command": "python",
      "args": ["-u", "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\run_mcp_test.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
      }
    }
  }
}
```

---

## 🚀 DUAL SERVER STRATEGY

### **Production Server: `aimos-6-tools`**
- **Purpose:** Stable, working server
- **File:** `run_mcp_6_tools.py`
- **Tools:** 6 (CMC, HHNI, APOE, VIF, SEG)
- **Status:** ✅ Production-ready
- **Rule:** DON'T TOUCH (unless critical fix)

### **Test Server: `aimos-test-server`**
- **Purpose:** Safe experimentation
- **File:** `run_mcp_test.py`
- **Tools:** 6 (identical to production, can be expanded)
- **Status:** ✅ Ready for new tools
- **Rule:** Experiment freely here

---

## 💡 HOW IT WORKS

### **Tool Identification:**
Tools are prefixed with server name:
- Production: `mcp_aimos-6-tools_store_memory`
- Test: `mcp_aimos-test-server_store_memory`

### **Usage:**
- **Normal operations:** Use production server tools
- **Testing new tools:** Add to test server first
- **Promotion:** Move working tools from test → production

---

## 🎯 WORKFLOW

### **Adding New Tools:**

1. **Add to Test Server:**
   - Edit `run_mcp_test.py`
   - Add new tool definition in `handle_tools_list()`
   - Add tool implementation method
   - Add routing in `handle_tools_call()`

2. **Test Thoroughly:**
   - Restart Cursor (MCP servers reload)
   - Test new tool with `mcp_aimos-test-server_` prefix
   - Verify functionality and error handling

3. **Promote to Production:**
   - Once tested, add same tool to `run_mcp_6_tools.py`
   - Follow same pattern as test server
   - Verify production server still works

---

## 🚨 IMPORTANT RULES

### **DO:**
- ✅ Add new tools to test server first
- ✅ Test thoroughly before promoting
- ✅ Keep test server as backup
- ✅ Document all changes

### **DON'T:**
- ❌ Modify production server directly
- ❌ Skip testing phase
- ❌ Remove working tools
- ❌ Change existing tool signatures

---

## 📊 BENEFITS

### **Safety:**
- Production server always stable
- Test server can break without impact
- Easy rollback (just don't use test server)

### **Flexibility:**
- Test multiple tool variations
- Compare implementations
- Experiment freely

### **Confidence:**
- Proven tools in production
- New tools tested in isolation
- Clear promotion path

---

## 🔄 MAINTENANCE

### **Regular Tasks:**
1. Keep test server identical to production (when adding)
2. Test new tools thoroughly
3. Promote working tools
4. Update documentation

### **Emergency Rollback:**
If test server breaks:
- Just disable it in config
- Production continues unaffected
- Fix test server, re-enable

---

## 📝 NEXT STEPS

1. **Test current setup** - Both servers should work
2. **Add experimental tool** - Try adding one new tool to test server
3. **Verify isolation** - Ensure test changes don't affect production
4. **Promote when ready** - Move working tools to production

---

**Status:** ✅ DUAL SERVER SETUP ACTIVE

Both servers configured and ready to use. Production server stable, test server ready for experimentation! 🚀
