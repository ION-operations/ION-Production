# Discovery 013: Actual MCP Tool Count Verified
**Timestamp:** 2025-01-27 ~2:35 PM  
**Source:** Direct grep of lucid_mcp_server.py

---

## 📊 **VERIFIED COUNT**

**Actual tools defined: 92** (Tool 1 through Tool 92)

But there's a **NUMBERING BUG**:
- `# Tool 67: get_tag_issues` (line 1379)
- `# Tool 67: list_terminals` (line 1392)

Tool 67 is used twice! So actual unique tools = **92** (with duplicate number)

---

## 🔢 **TOOL BREAKDOWN**

```
Tools 1-6:   Core AIM-OS (store_memory, get_memory_stats, etc.)
Tools 7-9:   SCOR (check_invariant, run_baseline_probe, detect_manipulation)
Tools 10-13: Snapshots
Tools 14-16: Timeline
Tools 17-19: Goal Timeline
Tools 20-22: IIS (Intuition)
Tools 23-25: Co-Agency
Tools 26-29: Dataset
Tools 30-32: Application Lifecycle
Tools 33-41: Autonomous Protocol (9 tools)
Tools 42-44: ARD
Tools 45-50: AI Collaboration
Tools 51-57: Prompt Chains
Tool 58:     Consciousness Metrics
Tools 59-60: HHNI
Tools 61-63: CAS
Tools 64-68: NL Tags (note: 67 is duplicate)
Tools 67-71: Cursor Integration (67 reused!)
Tools 72-81: Cursor Commands
Tools 82-84: API Integration
Tools 85-87: Specialist System
Tools 88-92: Math Tools
```

---

## ⚠️ **DISCREPANCY ANALYSIS**

| Source | Claims | Reality |
|--------|--------|---------|
| Header comment | 93 | ❌ |
| Class docstring | 92 | ✅ (but wrong breakdown) |
| Init log | 78 | ❌ |
| FACTS.md | 84 | ❌ |
| **Actual count** | **92** | ✅ |

---

## ✅ **FIXES NEEDED**

1. Fix Tool 67 duplicate numbering (lines 1379 and 1392)
2. Update header comment to 92
3. Update init log to 92
4. Update FACTS.md to 92
5. Verify breakdown math in comments

---

## 🏷️ **CLASSIFICATION**

- **Type:** Documentation/Numbering Error
- **Impact:** Low (cosmetic, tools still work)
- **Effort to Fix:** 10 minutes
- **Priority:** Low

