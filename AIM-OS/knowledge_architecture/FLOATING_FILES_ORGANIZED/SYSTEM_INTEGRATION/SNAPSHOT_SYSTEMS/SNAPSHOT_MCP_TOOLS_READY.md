# Snapshot MCP Tools - Ready to Add

**Date:** 2025-10-26  
**File:** `run_mcp_snapshot_tools.py`  
**Status:** ✅ BUILT, NOT CONNECTED (ready when we expand)

---

## 🎯 WHAT'S READY

**4 New MCP Tools for Snapshot System:**
1. `create_snapshot` - Backup MCP files before changes
2. `restore_snapshot` - Restore from backup
3. `list_snapshots` - View available snapshots
4. `delete_snapshot` - Remove old snapshots

---

## 📊 CURRENT STATUS

**File Created:** ✅ `run_mcp_snapshot_tools.py`  
**Standalone Script:** ✅ `scripts/snapshot_system.py` (works now)  
**MCP Integration:** ⏳ Ready but not connected  
**Production Server:** ⏳ Will add when expanding from 6 tools

---

## 🚀 WHEN TO ADD

**Add to production when:**
1. ✅ Snapshot system tested (done - Python script works)
2. ✅ Foundations built (git fixed, snapshot ready)
3. ⏳ Ready to expand MCP tools beyond 6
4. ⏳ Want snapshot operations as IDE tools

---

## 📋 INTEGRATION PLAN

**Option 1: Keep Separate (Current)**
- Current: 6-tool MCP server (production)
- New: 4-tool snapshot server (separate, not connected)
- Benefit: Don't touch working production yet
- When add: After we expand main server

**Option 2: Merge Now**
- Merge snapshot tools into `run_mcp_6_tools.py`
- Would become 10 tools total
- Risk: Changes working production
- Benefit: Everything in one place

**Recommendation:** Keep separate for now, add later when we expand.

---

## ✅ WHAT WE CAN DO NOW

**Using Python script directly:**
```python
python scripts/snapshot_system.py
```

**Or import in code:**
```python
from scripts.snapshot_system import snapshot_mcp_production
manifest = snapshot_mcp_production()
```

**MCP tools available when we connect them later.**

---

**Status:** Built and ready, but not connected yet  
**Next:** Continue with foundations (isolation, testing protocols)  
**Then:** Connect snapshot tools when expanding MCP server
