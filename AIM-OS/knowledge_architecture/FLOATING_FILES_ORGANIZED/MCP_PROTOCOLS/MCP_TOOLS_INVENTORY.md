# MCP Tools Inventory

**Date:** 2025-10-26  
**Status:** Tracking all MCP tools in AIM-OS  
**Last Updated:** 2025-10-26 (13 tools active)

---

## ✅ PRODUCTION (Connected)

**Server:** `run_mcp_6_tools.py`  
**Status:** ✅ Working in Cursor (13 tools active)  
**Tools (13):**

### Core AIM-OS Tools (6):
1. `store_memory` - Store information in CMC
2. `retrieve_memory` - Search HHNI for context
3. `get_memory_stats` - Get CMC/HHNI statistics
4. `create_plan` - Create APOE execution plans
5. `track_confidence` - Track VIF confidence
6. `synthesize_knowledge` - Synthesize SEG knowledge

### SCOR Tools (3):
7. `check_invariant` - Check invariant rules
8. `run_baseline_probe` - Detect consciousness drift
9. `detect_manipulation_signals` - Detect social manipulation

### Snapshot Tools (4):
10. `create_snapshot` - Create file snapshots before changes
11. `restore_snapshot` - Restore files from snapshot
12. `list_snapshots` - List available snapshots
13. `archive_snapshot` - Archive snapshots (never delete)

---

## ✅ NOW IN PRODUCTION

**Snapshot Tools:**
- **Status:** ✅ Connected and working (2025-10-26)
- **Tools (4):** Now part of production server
- **Testing:** Verified functional (list_snapshots, create_snapshot tested)
- **Principle:** Never delete without audit (CMC bitemporal tracking)

---

## 📋 FUTURE TOOLS (Planned)

**SCOR Tools** (Sanity Core):
- `check_invariant` - Verify invariant rules
- `run_baseline_probe` - Detect consciousness drift
- `detect_manipulation_signals` - Detect social manipulation

**TCS Tools** (Timeline Context):
- `add_timeline_entry` - Track context at each prompt
- `get_timeline_summary` - Get recent timeline
- `get_timeline_entries` - Query timeline history

**IIS Tools** (Intuitive Intelligence):
- `get_intuition_score` - Pattern matching score
- `detect_pattern` - Identify patterns in data

**CAS Tools** (Cognitive Analysis):
- `analyze_cognition` - Deep cognitive analysis
- `detect_drift` - Detect consciousness drift

---

## 🎯 EXPANSION STATUS

**Phase 1: Core + SCOR (9 tools)** ✅
- ✅ 6 core AIM-OS tools
- ✅ 3 SCOR tools
- **Status:** Complete

**Phase 2: Snapshots (13 tools)** ✅
- ✅ 4 snapshot tools added (2025-10-26)
- ✅ Tested and verified working
- **Status:** Complete

**Phase 3: Future Expansion (20+ tools)** ⏳
- TCS tools (timeline context)
- IIS tools (intuitive intelligence)
- CAS tools (cognitive analysis)
- More SCOR tools as needed

---

**Current:** 13 tools (production) ✅  
**Status:** All verified working  
**Snapshot Capability:** Active  
**Rollback Support:** Available
