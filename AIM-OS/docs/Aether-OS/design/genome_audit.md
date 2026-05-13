# Genome & Persistent Context Audit

**Date:** 2026-03-12  
**Root Cause Found:** `GEMINI.md` was empty → every new chat had zero context about MCP server name

## Files Audited

| File | Status | Issue |
|------|--------|-------|
| `/home/sev/.gemini/GEMINI.md` | 🔴 **WAS EMPTY** — FIXED | Root cause of MCP discovery failure. Now populated with server name + project structure |
| `/home/sev/.gemini/antigravity/mcp_config.json` | ✅ Correct | Has `lucid-mcp` server config |
| `/home/sev/.gemini/settings.json` | ✅ Correct | Has `lucid-mcp` server config |
| `.agent/CEO_DIRECTIVE_PERMANENT.md` | ⚠️ Outdated | References port 9090 bridge server, not current MCP port 5001 |
| `.agent/genomes/antigravity.genome.md` | ⚠️ Partially outdated | Says "92 tools" (now 106). References port 9090. MCP soul tools section good but doesn't mention `lucid-mcp` server name |
| `.agent/STARTUP.md` | ✅ Good | References port 5001 correctly. Has MCP check order |
| `.agent/SYSTEM_REGISTRY.md` | ✅ Good | Comprehensive package map, dated 2026-03-09 |
| `.agent/COMMS_DOCTRINE.md` | Not audited yet | |
| `.agent/KNOWN_ISSUES.md` | Not audited yet | |
| `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` | Not audited yet | |

## Critical Gaps Found

### 1. No file stated MCP server name `lucid-mcp` ← **FIXED in GEMINI.md**
Every new chat guessed random names (mcp, joc, filesystem, context7). Fixed by adding to GEMINI.md.

### 2. CEO Directive references dead port 9090
Still references `http://192.168.2.25:9090` bridge server. Current MCP is on port 5001 (localhost).

### 3. Genome references dead port 9090
Section 10 (Autonomous Operation) references "Bridge (:9090)" — should be "MCP Fallback (:5001)".

### 4. Genome says 92 tools, actually 106
Line 64: `| **MCP** | 🟢 Active | 92 tools via lucid-mcp + 14 via AI Engine |`

### 5. JOC not mentioned in genome
JOC/Jarvis management capabilities not documented in genome at all. New MCP management page exists.

### 6. HTTP fallback not documented in genome
The systemd auto-start fallback server on port 5001 isn't mentioned in any genome/instruction file.

### 7. GEMINI.md not referenced anywhere
No instruction file tells agents about `/home/sev/.gemini/GEMINI.md`. Agents wouldn't know to update it.

## What Still Needs Updating

- [ ] CEO_DIRECTIVE_PERMANENT.md — update port 9090 → 5001 references  
- [ ] antigravity.genome.md — update tool count, port refs, add JOC/MCP management info
- [ ] COMMS_DOCTRINE.md — audit for outdatedness
- [ ] KNOWN_ISSUES.md — audit and update
- [ ] AIMOS_MASTER_SYSTEM_INDEX.md — audit
