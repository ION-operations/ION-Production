# 🎯 Daemon/RAG System - Quick Integration Guide

**Date:** 2025-10-31  
**Status:** Ready for Integration  
**Quick Reference:** Integration steps for Daemon/RAG System

---

## 🚀 **QUICK START**

### **1. Build the System**

```bash
# Navigate to daemon_rag_system
cd daemon_rag_system

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=$PWD/..  # macOS/Linux
# or: $env:PYTHONPATH = $PWD/..  # Windows PowerShell
```

### **2. Test the System**

```bash
# Test imports
python -c "from daemon_rag_system import DaemonRAGSystem; print('✅ OK')"

# Run tests
pytest test_daemon_rag_system.py -v
```

### **3. Start HTTP API Server** (For Cursor UI)

```bash
python http_api_server.py
# Server runs on http://localhost:5000
```

### **4. Configure Cursor IDE** (MCP Protocol)

**File:** `C:\Users\<username>\.cursor\mcp.json`

```json
{
  "mcpServers": {
    "daemon-rag-system": {
      "command": "python",
      "args": [
        "-u",
        "C:\\Users\\<username>\\OneDrive\\Desktop\\AIM-OS\\daemon_rag_system\\daemon_rag_mcp_server.py"
      ],
      "cwd": "C:\\Users\\<username>\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "PYTHONPATH": "C:\\Users\\<username>\\OneDrive\\Desktop\\AIM-OS"
      }
    }
  }
}
```

**Then:** Restart Cursor IDE

---

## 📚 **DOCUMENTATION**

- **BUILD_PLAN.md** - Complete build instructions
- **INTEGRATION_PLAN.md** - Complete integration guide
- **TROUBLESHOOTING.md** - Common issues and solutions
- **README.md** - System overview

---

## ✅ **VERIFICATION**

### **Check Daemon Status:**
```bash
# Via HTTP API
curl http://localhost:5000/api/health

# Via MCP (in Cursor)
# Tools should appear in Cursor's tool list
```

### **Test Tool Selection:**
```python
from daemon_rag_system import DaemonRAGSystem, DaemonConfig

config = DaemonConfig(max_tools=40)
daemon = DaemonRAGSystem(config)
daemon.start()

response = daemon.process_request(
    "I need to store this information in memory",
    {"session_info": {"user_id": "test"}}
)

print(f"Selected tools: {response['selected_tools']}")
daemon.stop()
```

---

**Status:** Ready for Integration ✅  
**Next:** Follow BUILD_PLAN.md and INTEGRATION_PLAN.md for detailed steps

