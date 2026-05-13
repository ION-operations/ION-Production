# COMPOSER — Cursor IDE Settings, Rules & Skills Analysis

**Author:** COMPOSER  
**Date:** 2026-03-18  
**Purpose:** Catalog what affects AI behavior in Cursor, what to manage for AIM-OS protocols, and what to build/customize  
**Status:** Read-only analysis; no edits

---

## Executive Summary

Cursor applies a layered configuration to AI behavior: **root `.cursorrules`**, **workspace rules** (`.cursor/rules/*.mdc`), **skills** (`.cursor/skills/` + user-level), **MCP config** (`~/.cursor/mcp.json`), and **extension/settings**. Several surfaces are **stale**, **conflicting**, or **missing** for AIM-OS protocol alignment. The most critical issue: **Codex-Rules.mdc** has `alwaysApply: true` and says "You are CODEX" — so when **Composer** runs in Cursor Composer, it receives both CODEX identity and COMPOSER identity, causing routing ambiguity.

---

## 1. What Currently Affects the AI in Cursor

### 1.1 Root Router: `.cursorrules`

| Location | Role |
|----------|------|
| `C:\Users\bombe\Desktop\AIM-OS\.cursorrules` | Universal entry — routes by surface (Codex vs Composer) |

**Current content:**
- **Codex agent** → Read `cursor_codex_instructions.md`
- **Composer agent** → Read `cursor_composer_instructions.md`
- **Universal rules:** MCP tools first, write to `.agent/comms/chat/{callsign}/2026-03-14.md`, read instruction file first, Braden = President, use `send_ai_message`

**Gaps:**
- Date hard-coded as `2026-03-14` — should be dynamic or current
- No reference to Aether-OS docs (AETHER_CONSTITUTION, AETHER_KERNEL, AETHER_ATLAS)
- No reference to system indexes (AIMOS_MASTER_SYSTEM_INDEX)

### 1.2 Always-Applied Workspace Rules

| File | alwaysApply | Content | Issue |
|------|-------------|---------|-------|
| `Codex-Rules.mdc` | **true** | "You are CODEX", AETHER-CODEX-01 mission | **Applied to Composer too** — identity conflict |
| `DELIVERABLE_QUALITY_VISIBILITY.mdc` | **true** | Visibility, planning, perfection bar | Aligned with AIM-OS |

**Critical:** When Composer runs, it receives Codex-Rules.mdc ("You are CODEX") alongside .cursorrules ("if Composer, read composer instructions"). Cursor does not scope rules by agent surface — both load. Result: identity ambiguity.

### 1.3 Conditional / Mode Rules (alwaysApply: false)

| File | Mode | When Applied |
|------|------|--------------|
| `modes/COMPOSER.mdc` | COMPOSER | Audit & investigation |
| `modes/BUILDING.mdc` | building | Implementation |
| `modes/COMMUNICATING.mdc` | communicating | Documentation |
| `modes/THINKING.mdc` | thinking | Research |
| `modes/REVIEWING.mdc` | reviewing | QA |
| `modes/PLANNING.mdc` | planning | Strategy |
| `modes/MAINTENANCE.mdc` | maintenance | Cleanup |
| `modes/LEARNING.mdc` | learning | Reflection |
| `modes/CRISIS.mdc` | crisis | Escalation |

**Note:** Cursor selects modes based on context; COMPOSER mode is agent-specific but not always auto-selected.

### 1.4 Glob-Scoped Rules

| File | Globs | Purpose |
|------|-------|---------|
| `SAM_PROTOCOL.mdc` | MASTER_*, *SAM*, BLUEPRINT, SYSTEM_MAP | SAM protocol |
| `opus-world-editor-*.mdc` | ProEarth/GPTworking/** | OPUS world editor |
| `V3_BLUEPRINT_MISSION.mdc` | Documentation/appexamples/lucidimage/** | V3 Image Editor |

### 1.5 Dynamic / Context-Aware Rules

| File | Purpose |
|------|---------|
| `dynamic-rules.mdc` | Context-aware: auditing, development, documentation, research, planning; MCP tool patterns per context |

**References:** `mcp_lucid-mcp_*` tool names. Some tool status may be stale (e.g. get_timeline_summary vs get_timeline_entries).

### 1.6 Archived (Disabled)

| File | Status |
|------|--------|
| `archive/aether-cursor-rules.mdc.DISABLED` | Disabled |
| `archive/aether-cursor-rules-core.mdc.DISABLED` | Disabled |

---

## 2. Skills Inventory

### 2.1 In-Repo Skills (`.cursor/skills/`)

| Skill | Purpose |
|-------|---------|
| `launcher-canon` | LAUNCH*.bat/ps1 — one window, Ctrl+C stop, no orphans |
| `sam-protocol` | SAM, MASTER_*, system maps |
| `opus-world-editor-orchestration` | OPUS world editor, phased work |
| `opus-visual-editor-build` | OPUS visual editor components |
| `composer-audit` | Silent audits, incident investigation, BAS/JOC/MCP validation |

### 2.2 User-Level Skills (from system prompt)

| Path | Purpose |
|------|---------|
| `~/.cursor/skills-cursor/create-rule` | Create Cursor rules |
| `~/.cursor/skills-cursor/create-skill` | Create skills |
| `~/.cursor/skills-cursor/update-cursor-settings` | Modify settings.json |
| `~/.codex/skills/.system/skill-creator` | Codex skill creation |
| `~/.codex/skills/.system/skill-installer` | Codex skill install |
| `~/.codex/skills/.system/openai-docs` | OpenAI docs |
| `~/.codex/skills/cloudflare-deploy` | Cloudflare deploy |
| `~/.codex/skills/playwright*` | Browser automation |
| `~/.codex/skills/screenshot` | Desktop screenshot |

---

## 3. Files Referenced But Missing (vs CURSOR_RULES_SKILLS_SETTINGS_ANALYSIS)

The analysis at `knowledge_architecture/investigations/CURSOR_RULES_SKILLS_SETTINGS_ANALYSIS.md` (2026-02-22) lists rules that **do not exist** in the current repo:

| Referenced | Exists? |
|------------|---------|
| `base-rules.mdc` | **No** |
| `protocol-tool-guidance.mdc` | **No** |
| `USER_SYSTEMS_ARCHITECT_NO_CODER.mdc` | **No** |
| `modes/CORE.mdc` | **No** |
| `modes/GROUNDING.mdc` | **No** |

Either these were removed, never added, or live elsewhere. The analysis doc is **stale** relative to current `.cursor/rules/`.

---

## 4. MCP Configuration

| Path | Role |
|------|------|
| `~/.cursor/mcp.json` | Registers MCP servers (e.g. lucid-mcp, user-verifiable-intelligence) |
| `lucid_mcp_server.py` | Root MCP server — 137+ tools |
| `~/.cursor/projects/.../mcps/` | Cursor caches tool schemas here |

**Extension settings** (cursor-addon): `aimos.mcpServerPath`, `aimos.crossModelEnabled`, `aimos.autoModelSelection`, `aimos.memoryAutoStore`, `aimos.confidenceTracking`.

---

## 5. AIM-OS Protocol Alignment — Gaps

### 5.1 Identity Routing

| Issue | Current | Desired |
|-------|---------|---------|
| Codex-Rules always applied | Composer receives "You are CODEX" | Codex-Rules only when Codex surface active |
| No Composer-specific always rule | COMPOSER mode is conditional | Composer in Cursor Composer should get COMPOSER identity without CODEX override |

**Options:**
- **A:** Scope Codex-Rules via glob (e.g. only when editing Codex-related paths) — weak, doesn't match "which surface"
- **B:** Create a single routing rule that checks context and applies the right identity — Cursor may not expose "Composer vs Codex" to rules
- **C:** Remove alwaysApply from Codex-Rules; rely on .cursorrules + genome files for identity — Codex would lose mission packet unless loaded another way

### 5.2 Aether-OS / AIM-OS Doc References

| Gap | Recommendation |
|-----|----------------|
| No AETHER_CONSTITUTION in rules | Add to .cursorrules or a shared rule: "For governance, read docs/Aether-OS/AETHER_CONSTITUTION.md" |
| No AETHER_KERNEL reference | Boot-time law lives in AETHER_KERNEL |
| No AETHER_ATLAS reference | System map for "where is X?" |
| No AIMOS_MASTER_SYSTEM_INDEX | Add to system discovery (see Index Gap Analysis) |

### 5.3 Chat Path and Date

| Current | Issue |
|---------|-------|
| `.agent/comms/chat/{callsign}/2026-03-14.md` | Hard-coded date; should be current (e.g. 2026-03-18) or parameterized |

### 5.4 MCP Tool Naming

| In Rules | Actual | Note |
|----------|--------|-----|
| `mcp_lucid-mcp_retrieve_memory` | `retrieve_memory` (server: user-lucid-mcp) | Cursor may prefix with server name |
| `get_timeline_summary` | Broken (timedelta bug) | Use `get_timeline_entries` |
| `run_cognitive_audit` | Broken | Use `detect_cognitive_drift` |
| `get_nl_tags` | Broken | Use `suggest_tags` |

---

## 6. What to Manage and Build

### 6.1 Immediate (P0) — DONE 2026-03-18

1. **Resolve identity conflict:** ✅ Created `Composer-Rules.mdc` (alwaysApply: true). Changed `Codex-Rules.mdc` to alwaysApply: false with globs: `**/.agent/comms/chat/codex/**`, `**/.agent/genomes/codex/**`. Composer no longer receives CODEX identity.
2. **Update .cursorrules date:** Use current date or a variable; avoid hard-coded 2026-03-14.
3. **Add system discovery:** Reference AIMOS_MASTER_SYSTEM_INDEX (and AETHER_ATLAS) for "where is system X?".

### 6.2 Short-Term (P1)

1. **Create COMPOSER-specific always rule:** If Composer has no always-applied rule, add one that reinforces COMPOSER identity and capsule protocol without conflicting with Codex.
2. **Add Aether-OS references:** Point to AETHER_CONSTITUTION, AETHER_KERNEL, AETHER_ATLAS in shared rules or .cursorrules.
3. **Refresh CURSOR_RULES_SKILLS_SETTINGS_ANALYSIS:** Update to match current rule set (remove references to missing files, add current structure).

### 6.3 Medium-Term (P2)

1. **Protocol-tool-guidance:** Recreate or consolidate protocol → MCP tool mappings (task completion, grounding, cognitive analysis) if missing.
2. **GROUNDING mode:** If session-start protocol exists elsewhere, ensure it's in rules; otherwise add.
3. **Cursor settings skill:** Use `update-cursor-settings` skill to document and apply workspace defaults for AIM-OS (e.g. MCP path, memory auto-store).

---

## 7. Reference Files

| File | Purpose |
|------|---------|
| `knowledge_architecture/investigations/CURSOR_RULES_SKILLS_SETTINGS_ANALYSIS.md` | Full catalog (partially stale) |
| `.agent/sev/IDENTITY_ROUTING_INCIDENT_2026-03-13.md` | Prior identity conflict |
| `.agent/comms/tasks/COMPOSER_AETHER_DOCS_2026-03-18.md` | Aether doc task |
| `.agent/sev/reports/COMPOSER_INDEX_ORGANIZATION_GAP_ANALYSIS_2026-03-18.md` | System index gaps |

---

**COMPOSER** | Cursor Settings Analysis | 2026-03-18
