# Discovery 003: MCP Tool Count Inconsistency (CRITICAL)
**Timestamp:** 2025-01-27 ~12:25 PM  
**Severity:** HIGH - Multiple conflicting claims in authoritative documents

---

## 📍 **THE PROBLEM**

The number of MCP tools is stated differently in multiple places:

| Source | Tool Count Claimed |
|--------|-------------------|
| `lucid_mcp_server.py` header comment (line 5) | **93 total** |
| `lucid_mcp_server.py` class docstring (line 70) | **92 tools** |
| `lucid_mcp_server.py` init log (line 346) | **78 tools** |
| `FACTS.md` (the "single source of truth") | **84 tools** |
| Actual `# Tool N:` comments in code | **94 matches** |

---

## 🔍 **EVIDENCE**

### From lucid_mcp_server.py:

**Header (lines 5-26):**
```python
AIM-OS Tools (93 total):
Core AIM-OS (6): store_memory, get_memory_stats, retrieve_memory, create_plan, track_confidence, synthesize_knowledge
...
```

**Class docstring (line 70):**
```python
class SimpleMCPServer:
    """MCP Server with AIM-OS tools (92 total: 6 core + 3 SCOR + ...)"""
```

**Init log (line 346):**
```python
log("SUCCESS: LUCID-MCP Server initialized with 78 tools (6 core + 3 SCOR + ...)")
```

### From FACTS.md:
```markdown
### **Tool Count:**
- **Total MCP Tools:** 84 tools ✅ **VERIFIED IN CODE**
```

### Actual tool definitions:
```bash
grep -c "# Tool \d+:" lucid_mcp_server.py
# Result: 94 matches
```

---

## ⚠️ **WHY THIS MATTERS**

1. **FACTS.md claims to be "Single Source of Truth"** but contains incorrect count
2. **Multiple places in same file disagree** - 93 vs 92 vs 78
3. **Agents using FACTS.md will have wrong information**
4. **Quality/trust issue** - if authoritative docs are wrong, what else is?

---

## 🎯 **ROOT CAUSE ANALYSIS**

Likely causes:
1. Tools were added/removed without updating all references
2. Different counts represent different stages of development
3. Copy-paste errors when updating documentation
4. No automated validation of tool counts

---

## ✅ **RECOMMENDED FIX**

1. **Count actual tools programmatically:**
   ```python
   # Add to server startup
   actual_count = len(all_tools)
   log(f"Loaded {actual_count} tools")
   ```

2. **Update all references to use actual count**

3. **Add validation to prevent future drift:**
   ```python
   EXPECTED_TOOL_COUNT = 94  # Update when tools change
   assert len(all_tools) == EXPECTED_TOOL_COUNT, f"Tool count mismatch!"
   ```

4. **Update FACTS.md with actual verified count**

---

## 🏷️ **CLASSIFICATION**

- **Type:** Documentation/Implementation Mismatch
- **Impact:** Medium (affects accuracy of information)
- **Effort to Fix:** Low (update numbers)
- **Priority:** High (undermines trust in documentation)

