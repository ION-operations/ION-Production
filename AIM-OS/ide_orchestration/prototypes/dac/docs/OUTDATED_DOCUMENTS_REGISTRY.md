# Outdated Documents Registry

**Purpose:** Track ALL outdated documents so agents don't read them  
**Status:** CRITICAL - Prevents reading old information  
**Date:** 2025-01-27  
**Priority:** P0

---

## 🚨 **CRITICAL: ALWAYS CHECK THIS BEFORE READING DOCUMENTS**

**If a document is listed here as OUTDATED, DO NOT USE IT for current information.**

---

## 📋 **OUTDATED DOCUMENTS**

### **MCP Tool Count Documents (OUTDATED)**

1. **`knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_TEST_SUMMARY.md`**
   - **Claims:** 59 tools
   - **Actual:** 84 tools
   - **Date:** 2025-11-02 (OUTDATED)
   - **Status:** ⚠️ OUTDATED - Marked with warning
   - **Use Instead:** `lucid_mcp_server.py` lines 348-1627

2. **`knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_INVENTORY.md`**
   - **Claims:** 59 tools (likely)
   - **Actual:** 84 tools
   - **Status:** ⚠️ OUTDATED - Needs verification
   - **Use Instead:** `lucid_mcp_server.py` lines 348-1627

3. **`knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_DEEP_INVESTIGATION.md`**
   - **Status:** ⚠️ OUTDATED - Needs verification
   - **Use Instead:** `lucid_mcp_server.py` lines 348-1627

4. **`knowledge_architecture/AETHER_MEMORY/safety_audit_journey/MCP_50_TOOLS_FINAL_SUMMARY.md`**
   - **Claims:** 50 tools
   - **Actual:** 84 tools
   - **Date:** October 27, 2025 (OUTDATED)
   - **Status:** ⚠️ OUTDATED - Historical document

5. **`knowledge_architecture/AETHER_MEMORY/safety_audit_journey/MCP_50_TOOLS_COMPREHENSIVE_TEST.md`**
   - **Claims:** 50 tools
   - **Actual:** 84 tools
   - **Date:** October 27, 2025 (OUTDATED)
   - **Status:** ⚠️ OUTDATED - Historical document

6. **`organized_root_files/MCP_REPORTS/MCP_TOOLS_COUNT_VERIFICATION.md`**
   - **Claims:** 71 tools
   - **Actual:** 84 tools
   - **Status:** ⚠️ OUTDATED

7. **`organized_root_files/MCP_REPORTS/MCP_TOOLS_71_COUNT_VERIFICATION.md`**
   - **Claims:** 71 tools
   - **Actual:** 84 tools
   - **Status:** ⚠️ OUTDATED

### **Tool Limit Documents (OUTDATED)**

1. **`knowledge_architecture/FLOATING_FILES_ORGANIZED/MCP_PROTOCOLS/INTEGRATION_REPORTS/MCP_TOOL_LIMIT_ANALYSIS.md`**
   - **Claims:** 40-tool limit
   - **Actual:** ~80 tool limit (Cursor), NO LIMIT (AIM-OS)
   - **Status:** ⚠️ OUTDATED - Old Cursor limit

2. **`aim-os-minimal/knowledge_architecture/MCP_TOOL_LIMIT_ANALYSIS.md`**
   - **Claims:** 40-tool limit
   - **Actual:** ~80 tool limit (Cursor), NO LIMIT (AIM-OS)
   - **Status:** ⚠️ OUTDATED - Old Cursor limit

---

## ✅ **AUTHORITATIVE SOURCES (CURRENT)**

### **MCP Tool Count:**
- **`lucid_mcp_server.py`** lines 348-1627 - **AUTHORITATIVE**
  - 84 tools verified in code
  - Count tool definitions yourself if needed

### **Confidence Gating:**
- **`.cursor/rules/base-rules.mdc`** - **AUTHORITATIVE**
  - MANDATORY: NEVER work below 0.70 confidence
  - VIF integration required

### **Tool Limit:**
- **`.cursor/rules/base-rules.mdc`** - **AUTHORITATIVE**
  - Cursor IDE Limit: ~80 tools (Cursor's limitation, NOT AIM-OS)
  - AIM-OS Limit: NO LIMIT

---

## 🔄 **UPDATE PROTOCOL**

**When you find an outdated document:**
1. Add it to this registry
2. Mark the document itself with "OUTDATED" warning
3. Update references to point to authoritative source
4. Archive if truly historical

**Before reading ANY document:**
1. Check this registry first
2. If listed as OUTDATED, don't use for current facts
3. Use authoritative sources instead

---

**Status:** Living document - Update when finding outdated docs  
**Last Updated:** 2025-01-27  
**Next:** Continue finding and marking outdated documents

