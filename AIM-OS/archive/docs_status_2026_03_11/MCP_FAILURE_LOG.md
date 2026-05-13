# MCP Failure Log

**Purpose:** Note and diagnose MCP tool failures. Every failure gets logged here so we can fix root causes and prevent recurrence.

**Protocol:** When an MCP tool returns an error:
1. Log the failure below (date, tool, args summary, error, diagnosis)
2. Add to FINDINGS_MASTER_LIST if severity warrants
3. Fix or document workaround

---

## Log Format

| Date | Tool | Args (summary) | Error | Diagnosis | Fix |
|------|------|----------------|-------|-----------|-----|
| 2026-03-05 | store_memory | tags as list | 'list' object has no attribute 'items' | tags expected dict; caller passed list | Normalize list→dict in lucid_mcp_server.py |

---

## Entries

### 2026-03-05 — store_memory tags type mismatch

**Tool:** `store_memory`  
**Args:** `content="AUDIT_01...", tags=["audit", "system_map", "2026-03-05", "composer"]`  
**Error:** `'list' object has no attribute 'items'`  
**Root cause:** `tags` schema says `"type": "object"` (dict). Caller passed list. CMC/store_memory does `tags.items()` which fails on list.  
**Fix applied:** `lucid_mcp_server.py` lines 2598–2602 — normalize list tags to dict: `{str(t): 1.0 for t in tags}` before processing.  
**Caller guidance:** Use `tags: {"audit": 1, "system_map": 1}` (dict) or `tags: ["audit", "system_map"]` (list now supported).

---

## How to Add

When you see an MCP failure:

1. Copy the error message
2. Note the tool name and args (truncate if large)
3. Add a row to the table above
4. Diagnose: what parameter/type caused it?
5. Fix if possible, or document workaround

---

## Related

- `scripts/check_mcp_tool_parity.py` — validates tool callability
- `data/mcp/mcp_tool_calls.jsonl` — tool call log (if HTTP fallback logging enabled)
- `docs/Composer/FINDINGS_MASTER_LIST.md` — findings that warrant handoff
