# MCP Test Server Isolation Protocol

**Date:** 2025-10-26  
**Purpose:** Safe test server development without affecting production  
**Principle:** Complete isolation prevents contamination  

---

## 🎯 **THE PROBLEM**

### **What Happened Before:**
- Added test server with TCS tools
- Test server crashed (SimpleMCPServer class name bug)
- Production server stopped working
- Both servers share resources
- No isolation → Test failures affect production

### **Root Cause:**
- **No Isolation** - Test and production share:
  - Python process
  - Memory directory
  - Import paths
  - Error handling
- **No Rollback** - Can't easily undo test changes
- **No Proof** - Added features without testing first

---

## ✅ **ISOLATION PROTOCOL**

### **Phase 1: Complete Separation**

#### **1.1 Separate Files**
- **Production:** `run_mcp_6_tools.py`
- **Test:** `run_mcp_test.py` (separate file, never conflicts)

#### **1.2 Separate Class Names**
```python
# Production
class SimpleMCPServer:
    pass

# Test
class TestMCPServer:
    pass
```

#### **1.3 Separate Memory Directories**
```python
# Production
memory_dir = "./mcp_memory"

# Test
memory_dir = "./mcp_test_memory"  # COMPLETELY SEPARATE
```

#### **1.4 Separate Config Registration**
```json
{
  "mcpServers": {
    "aimos-6-tools": {
      "command": "python",
      "args": ["-u", "run_mcp_6_tools.py"],
      ...
    }
    // NO TEST SERVER IN PRODUCTION CONFIG
    // Test server NOT registered in Cursor
  }
}
```

**Critical:** Test server NOT registered in Cursor config!

---

### **Phase 2: Pre-Test Validation**

#### **2.1 Import Testing (BEFORE Adding to Server)**
```python
# Test imports FIRST
python -c "from packages.tcs.prompt_context_tracker import PromptContextTracker; print('Import OK')"
```

#### **2.2 Syntax Validation**
```python
# Check syntax
python -m py_compile run_mcp_test.py
```

#### **2.3 Standalone Testing**
```python
# Test server standalone (not in Cursor)
python run_mcp_test.py
# Press Ctrl+C to stop
```

**If ANY of these fail → FIX BEFORE adding to MCP!**

---

### **Phase 3: Safe Addition Process**

#### **Step 1: Snapshot Production**
```bash
python scripts/snapshot_system.py create --name "pre_test_addition"
```

#### **Step 2: Add to Test Server (NOT Production)**
```python
# ONLY modify run_mcp_test.py
# Add tools incrementally
# Test each tool individually
```

#### **Step 3: Test Standalone**
```bash
# Run test server standalone
python run_mcp_test.py
# Verify no errors
```

#### **Step 4: Register in Test Config (Separate File)**
```json
{
  "test_mcpServers": {
    "aimos-test-server": {
      "command": "python",
      "args": ["-u", "run_mcp_test.py"],
      "cwd": "C:/Users/bombe/OneDrive/Desktop/AIM-OS",
      "env": {
        "PYTHONPATH": "C:/Users/bombe/OneDrive/Desktop/AIM-OS",
        "MCP_MEMORY_DIR": "./mcp_test_memory"
      }
    }
  }
}
```

**Store in:** `cursor_mcp_config_TEST.json` (separate file!)

---

### **Phase 4: Validation Before Promotion**

#### **Requirements for Promotion to Production:**
- ✅ Test server runs standalone without errors
- ✅ All tools work in test server
- ✅ No conflicts with production imports
- ✅ Memory directory separate
- ✅ Class names unique
- ✅ Tested for minimum 1 hour of stable operation

#### **Promotion Process:**
1. Create snapshot of production
2. Copy working code from test to production
3. Verify production still works
4. Keep test server for future testing

---

## 🚨 **CRITICAL RULES**

### **NEVER:**
- ❌ Modify production server directly for testing
- ❌ Share memory directory between test and production
- ❌ Use same class names
- ❌ Register test server in production config
- ❌ Skip import testing
- ❌ Add features without standalone testing

### **ALWAYS:**
- ✅ Create snapshot before ANY changes
- ✅ Test imports before adding to server
- ✅ Use separate memory directory
- ✅ Use unique class names
- ✅ Test standalone before Cursor integration
- ✅ Keep test server separate from production

---

## 🎯 **TEST SERVER CONFIGURATION**

### **File Structure:**
```
AIM-OS/
├── run_mcp_6_tools.py         # Production (NEVER touch for testing)
├── run_mcp_test.py            # Test server
├── cursor_mcp_config.json     # Production config (MCP_TOOLS)
├── cursor_mcp_config_TEST.json  # Test config (FOR TESTING ONLY)
├── mcp_memory/                # Production memory
├── mcp_test_memory/           # Test memory (separate!)
└── scripts/
    └── snapshot_system.py     # Backup system
```

### **Class Structure:**
```python
# run_mcp_6_tools.py
class SimpleMCPServer:
    def __init__(self):
        self.memory_dir = "./mcp_memory"

# run_mcp_test.py  
class TestMCPServer:  # DIFFERENT NAME!
    def __init__(self):
        self.memory_dir = "./mcp_test_memory"  # DIFFERENT DIR!
```

---

## ✅ **SUCCESS CRITERIA**

**Isolation Works When:**
- ✅ Test server bug doesn't affect production
- ✅ Test server crashes don't crash production
- ✅ Memory directories stay separate
- ✅ Can develop in test server safely
- ✅ Production remains stable

**Promotion Ready When:**
- ✅ Test server stable for 1+ hours
- ✅ All new features working in test
- ✅ No import conflicts
- ✅ Complete isolation verified

---

## 🎯 **WORKFLOW**

### **To Add New Feature:**

1. **Snapshot** production
2. **Test import** of new feature
3. **Add to test server** ONLY
4. **Test standalone** in test server
5. **Validate** works correctly
6. **Test in Cursor** using test config
7. **Stable for 1+ hours**
8. **Promote** to production
9. **Keep test server** for next feature

### **Emergency Rollback:**
```bash
# Restore from snapshot
python scripts/snapshot_system.py restore <snapshot_id>
```

---

**Status:** Complete isolation protocol  
**Risk:** Minimized through separation  
**Safety:** Maximum through validation  
**Next:** Implement in next test server feature
