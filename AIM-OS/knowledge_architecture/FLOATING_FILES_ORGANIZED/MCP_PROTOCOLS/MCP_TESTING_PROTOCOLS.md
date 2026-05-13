# MCP Testing Protocols

**Date:** 2025-10-26  
**Purpose:** Safe testing procedures for MCP tool development  
**Principle:** Test before deploy, validate before promote  

---

## 🎯 **OVERVIEW**

### **Testing Pyramid:**
```
          /\
         /  \    Production (live, 6 tools)
        /____\
       /      \   Integration (all tools working)
      /________\
     /          \  Unit (each tool individually)
    /____________\
```

**Test Order:** Unit → Integration → Production

---

## ✅ **PHASE 1: UNIT TESTING**

### **1.1 Import Validation**

**Purpose:** Verify imports work before adding to server

**Process:**
```bash
# Test each import individually
python -c "from packages.timeline_context_system.prompt_context_tracker import PromptContextTracker; print('OK')"
python -c "from packages.scor.scor.interface import SCORInterface; print('OK')"
```

**Success Criteria:**
- ✅ No import errors
- ✅ Classes instantiate
- ✅ Methods accessible

**If FAILS:** Fix import path, check dependencies, verify module structure

---

### **1.2 Tool Function Testing**

**Purpose:** Test each tool function in isolation

**Process:**
```python
# Test tool function directly
from packages.timeline_context_system.prompt_context_tracker import PromptContextTracker

tracker = PromptContextTracker()
result = tracker.add_entry("test", {"context": "test"})
print(f"Result: {result}")
```

**Success Criteria:**
- ✅ Function executes without errors
- ✅ Returns expected output
- ✅ Handles edge cases

**If FAILS:** Fix function logic, check dependencies, verify inputs/outputs

---

## ✅ **PHASE 2: INTEGRATION TESTING**

### **2.1 Tool Addition Testing**

**Purpose:** Add tool to test server and verify MCP registration

**Process:**
```python
# Add to run_mcp_test.py
@app.tool("add_timeline_entry")
async def add_timeline_entry(request: ToolRequest) -> dict:
    # Tool implementation
    return {"success": True}
```

**Success Criteria:**
- ✅ Tool registered in MCP protocol
- ✅ Tool appears in tools/list
- ✅ Tool callable via MCP

---

### **2.2 Tool Call Testing**

**Purpose:** Test tool via MCP protocol

**Manual Testing:**
```json
// Send via MCP protocol
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add_timeline_entry",
    "arguments": {
      "content": "test",
      "tags": {"test": true}
    }
  }
}
```

**Success Criteria:**
- ✅ Tool receives call
- ✅ Tool processes correctly
- ✅ Tool returns valid response

---

### **2.3 Standalone Server Testing**

**Purpose:** Test complete server standalone

**Process:**
```bash
# Run test server standalone
python run_mcp_test.py

# Send test requests via stdin
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python run_mcp_test.py
```

**Success Criteria:**
- ✅ Server starts without errors
- ✅ Responds to MCP requests
- ✅ All tools registered

---

## ✅ **PHASE 3: CURSOR INTEGRATION TESTING**

### **3.1 Test Config Testing**

**Purpose:** Test in Cursor with test config

**Process:**
1. Copy working config to test file
2. Add test server to test config
3. Restart Cursor with test config
4. Verify test server appears

**Success Criteria:**
- ✅ Test server registered
- ✅ Tools available in Cursor
- ✅ Can call tools from Cursor

---

### **3.2 Real-World Testing**

**Purpose:** Test tools with real usage patterns

**Test Cases:**
- ✅ Add entry with valid data
- ✅ Add entry with missing data (should error gracefully)
- ✅ Add entry with invalid data (should error gracefully)
- ✅ Get timeline with empty history
- ✅ Get timeline with data

**Success Criteria:**
- ✅ All valid cases work
- ✅ All error cases handled gracefully
- ✅ No crashes or hangs

---

### **3.3 Stability Testing**

**Purpose:** Test for stability over time

**Process:**
- Run test server for minimum 1 hour
- Make multiple tool calls
- Monitor for errors

**Success Criteria:**
- ✅ No crashes for 1+ hours
- ✅ Memory usage stable
- ✅ No performance degradation

---

## ✅ **PHASE 4: PRODUCTION PROMOTION**

### **4.1 Pre-Promotion Checklist**

**Requirements:**
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Cursor integration works
- ✅ Real-world tests pass
- ✅ Stability test passed (1+ hours)
- ✅ Isolation verified (separate directories)
- ✅ No conflicts with production imports

---

### **4.2 Promotion Process**

**Step 1: Snapshot Production**
```bash
python scripts/snapshot_system.py create --name "pre_tool_addition"
```

**Step 2: Copy Working Code**
```python
# Copy from run_mcp_test.py to run_mcp_6_tools.py
# Add new tool to production server
```

**Step 3: Update Tool Count**
```python
# Update header comment
# AIM-OS Core Tools (7 total):  # Was 6, now 7
```

**Step 4: Verify Production**
```bash
# Restart Cursor with production config
# Verify new tool works
```

---

### **4.3 Post-Promotion Validation**

**Check:**
- ✅ Production server starts
- ✅ New tool registered
- ✅ New tool works
- ✅ Existing tools still work
- ✅ No regressions

---

## 🚨 **ERROR HANDLING PROTOCOL**

### **Import Errors:**
- **Symptom:** ImportError when importing module
- **Action:** Check PYTHONPATH, verify module exists
- **Fix:** Add to sys.path or fix import path

### **Syntax Errors:**
- **Symptom:** SyntaxError in tool code
- **Action:** Check Python syntax
- **Fix:** Use python -m py_compile to validate

### **Runtime Errors:**
- **Symptom:** Tool crashes when called
- **Action:** Add try/except, log errors
- **Fix:** Handle edge cases, validate inputs

### **MCP Protocol Errors:**
- **Symptom:** Tool not registered in MCP
- **Action:** Check tool decoration, verify @app.tool()
- **Fix:** Ensure correct MCP SDK usage

---

## 📊 **TESTING METRICS**

### **Success Metrics:**
- All imports valid: 100%
- All tools functional: 100%
- No crashes in 1+ hours: Pass
- Error handling: All edge cases covered

### **Failure Metrics:**
- Import errors: Should be 0
- Tool failures: Should be 0
- Crashes: Should be 0
- Unhandled errors: Should be 0

---

## 🎯 **TESTING WORKFLOW SUMMARY**

### **Complete Flow:**
1. **Unit Test** → Import validation
2. **Unit Test** → Function testing
3. **Integration** → Add to test server
4. **Integration** → MCP protocol testing
5. **Integration** → Standalone testing
6. **Cursor** → Test config integration
7. **Cursor** → Real-world testing
8. **Stability** → 1+ hour test
9. **Promote** → Copy to production
10. **Validate** → Production verification

---

## ✅ **SUCCESS CRITERIA**

**Ready for Promotion:**
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Cursor integration works
- ✅ Real-world tests pass
- ✅ Stability: 1+ hours
- ✅ No errors in logs
- ✅ Performance acceptable

**Ready for Production:**
- ✅ Tested in test server
- ✅ Validated in Cursor
- ✅ Stable for 1+ hours
- ✅ No conflicts
- ✅ Complete isolation

---

**Status:** Complete testing protocols  
**Coverage:** Unit → Integration → Production  
**Safety:** Maximum through validation  
**Next:** Use for all MCP tool additions
