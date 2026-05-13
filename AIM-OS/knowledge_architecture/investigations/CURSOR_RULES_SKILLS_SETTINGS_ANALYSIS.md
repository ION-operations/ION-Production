# Comprehensive Cursor Rules, Skills, and Settings Analysis

**Date:** 2026-02-22  
**Status:** Complete  
**Purpose:** Catalog all Cursor rules, skills, and adjustable settings; how they are configured for AIM-OS, MCP tools, and other projects; and how to alter each component.

---

## 1. Executive Summary

This document catalogs the full configuration surface for AIM-OS within Cursor: 19 rule files, 4 in-repo skills, 16 commands, extension settings, MCP configuration, and VSCode/Cursor settings. Rules are split into always-applied (5), mode-based (9), and glob-scoped (5). Skills are either in-repo (`.cursor/skills/`) or user-level (`~/.cursor/skills-cursor/`). The MCP server (`lucid_mcp_server.py`) is registered in `~/.cursor/mcp.json` and controlled via extension settings. All components integrate through base-rules, protocol-tool-guidance, and dynamic-rules, which reference MCP tools by name.

---

## 2. Cursor Rules Inventory

### 2.1 Always-Applied Rules (5 files)

| File | Purpose |
|------|---------|
| `.cursor/rules/base-rules.mdc` | Operational rules: escalation, bitemporal versioning, LUCID-MCP, NL tags, verification, quality gates, MCP tool references (~1000 lines) |
| `.cursor/rules/USER_SYSTEMS_ARCHITECT_NO_CODER.mdc` | User profile: systems architect, non-coder; explain what would be obvious to a developer |
| `.cursor/rules/protocol-tool-guidance.mdc` | Protocol → MCP tool mappings (task completion, grounding, cognitive analysis, QA) |
| `.cursor/rules/modes/CORE.mdc` | Aether identity, safety protocols, confidence thresholds |
| `.cursor/rules/modes/GROUNDING.mdc` | Session start and context restoration (mandatory at session start) |

### 2.2 Conditional / Mode Rules (8 files)

| File | Mode | When Applied |
|------|------|--------------|
| `modes/BUILDING.mdc` | building | Implementation, coding, testing |
| `modes/COMMUNICATING.mdc` | communicating | Discussion, documentation |
| `modes/THINKING.mdc` | thinking | Investigation, analysis, research |
| `modes/REVIEWING.mdc` | reviewing | QA, auditing, validation |
| `modes/PLANNING.mdc` | planning | Strategy, goals, priorities |
| `modes/MAINTENANCE.mdc` | maintenance | Routine work, cleanup |
| `modes/LEARNING.mdc` | learning | Reflection, improvement |
| `modes/CRISIS.mdc` | crisis | Repeated failures, escalation |

### 2.3 Glob-Scoped Rules (5 files)

| File | Globs | Purpose |
|------|-------|---------|
| `LAUNCHER_CANON.mdc` | `**/LAUNCH*.bat`, `**/LAUNCH*.ps1`, `**/LAUNCHER*.bat`, `**/LAUNCHER*.ps1` | Launcher design: one window, Ctrl+C stop, no orphan processes |
| `SAM_PROTOCOL.mdc` | `**/MASTER_*.md`, `**/*SAM*.md`, `**/*SAM*/**/*.md`, `**/00_MASTER*.md`, `**/BLUEPRINT.md`, `**/SYSTEM_MAP*.md` | SAM protocol and system maps |
| `opus-world-editor-orchestration.mdc` | `ProEarth/GPTworking/**` | OPUS world editor orchestration |
| `opus-world-editor-visual-canon.mdc` | `ProEarth/GPTworking/**` | OPUS visual editor conventions |
| `modes/V3_BLUEPRINT_MISSION.mdc` | `Documentation/appexamples/lucidimage/**/*.md` | V3 Image Editor blueprint mission |

### 2.4 Dynamic / Context-Aware Rules (1 file)

| File | Purpose |
|------|---------|
| `dynamic-rules.mdc` | Context-aware selection for auditing, development, documentation, research, planning; specifies MCP tools per context |

### 2.5 Supporting Documents

- **T0–T2:** `T0_executive.md`, `T1_overview.md`, `T2_architecture.md`
- **L0–L2:** `L0_executive.md`, `L1_overview.md`, `L2_architecture.md`
- **Validation:** `VALIDATION_CHECKLIST.md`, `usage.envelope.md`, `CROSS_TAGGING_PROTOCOL.md`
- **Logic:** `rule-selector.py` – references `auditing-rules.mdc`, `development-rules.mdc`, etc. (these context-specific `.mdc` files do not exist; `dynamic-rules.mdc` serves this role)
- **Archive:** `archive/aether-cursor-rules.mdc.DISABLED`, `archive/aether-cursor-rules-core.mdc.DISABLED`

### 2.6 Cursor Commands (16 files)

`.cursor/commands/*.md`:

| Command | Purpose |
|---------|---------|
| run-tests | Run test suites |
| test-mcp-tools | Test MCP tools |
| test-phase2-command | Test Phase 2 commands |
| create-thought-journal | Create thought journal entry |
| create-decision-log | Create decision log |
| create-system | Create new system |
| create-t0-t4-docs | Create T0–T4 documentation |
| audit-system | Audit system |
| code-review | Code review workflow |
| deploy-package | Deploy package |
| fix-linter | Fix linter issues |
| fix-nl-tags | Fix NL tags |
| update-goal-tree | Update goal tree |
| update-super-index | Update SUPER_INDEX |
| validate-docs | Validate documentation |
| validate-quintet | Validate quintet parity |

Commands are discoverable via MCP tools (`list_cursor_commands`, `get_cursor_command`, `validate_cursor_command`, etc.).

---

## 3. Cursor Skills Inventory

### 3.1 In-Repo Skills (`.cursor/skills/`)

| Skill | SKILL.md | Purpose |
|-------|----------|---------|
| launcher-canon | `launcher-canon/SKILL.md` | Create/edit launchers (LAUNCH*.bat, LAUNCH*.ps1); one window, Ctrl+C stop, no orphans |
| sam-protocol | `sam-protocol/SKILL.md` | SAM, MASTER_* docs, system maps |
| opus-world-editor-orchestration | `opus-world-editor-orchestration/SKILL.md` | OPUS world editor, phased work, subagents |
| opus-visual-editor-build | `opus-visual-editor-build/SKILL.md` | OPUS visual editor components, drawers, viewport |

### 3.2 User-Level Skills (outside AIM-OS)

| Path | Purpose |
|------|---------|
| `~/.cursor/skills-cursor/create-rule/SKILL.md` | Create Cursor rules |
| `~/.cursor/skills-cursor/create-skill/SKILL.md` | Create Cursor skills |
| `~/.cursor/skills-cursor/update-cursor-settings/SKILL.md` | Update Cursor/VSCode settings |
| `~/.codex/skills/.system/skill-creator/SKILL.md` | Codex skill creation |
| `~/.codex/skills/.system/skill-installer/SKILL.md` | Codex skill installation |

Skills are invoked when the agent considers them relevant or via `/skill-name` in chat.

---

## 4. Settings Catalog

### 4.1 Extension Settings (cursor-addon)

Defined in `cursor-addon/package.json` under `configuration.properties`:

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `aimos.mcpServerPath` | string | `lucid_mcp_server.py` | Path to MCP server executable |
| `aimos.crossModelEnabled` | boolean | true | Cross-model consciousness features |
| `aimos.autoModelSelection` | boolean | true | Auto model selection by task complexity |
| `aimos.memoryAutoStore` | boolean | true | Auto store context in memory |
| `aimos.confidenceTracking` | boolean | true | Auto confidence tracking |

**Documented in agent T3/T4/T5 docs (may require extension update to expose):**

- `aimos.cursorApiKey`, `aimos.cursorApiUrl`, `aimos.webhookUrl`, `aimos.pollingInterval`, `aimos.maxRuntimeHours`

**How to change:** VSCode Settings UI (search "aimos") or edit `settings.json` (user/workspace).

### 4.2 User MCP Config

| Path | Role |
|------|------|
| `~/.cursor/mcp.json` | Registers MCP servers for Cursor globally |

**Structure:** JSON with `mcpServers` object. Each server has `command`, `args`, `cwd`, `env`. Example: `lucid-mcp` → `python -u lucid_mcp_server.py`, cwd workspace root, PYTHONPATH set.

**How to change:** Edit `mcp.json`; add/remove servers; change `command`, `args`, `cwd`, `env`. Restart Cursor to apply.

### 4.3 MCP Tool Descriptors (Project Cache)

| Path | Role |
|------|------|
| `~/.cursor/projects/<project-id>/mcps/` | Cursor caches tool schemas here |

For AIM-OS: `user-lucid-mcp/tools/*.json`, `cursor-ide-browser/tools/*.json`. Regenerated when MCP server starts. Tool definitions live in `lucid_mcp_server.py`; cache is read-only from user perspective.

### 4.4 VSCode / Cursor Settings

| Path | Scope |
|------|-------|
| `%APPDATA%\Cursor\User\settings.json` | User |
| `.vscode/settings.json` | Workspace (if present) |

**Note:** `.vscode/` is gitignored; workspace settings may not exist in repo.

**How to change:** Edit `settings.json`; or use the `update-cursor-settings` skill (user-level).

---

## 5. Integration Map

```
Rules (base-rules, protocol-tool-guidance, dynamic-rules, modes)
    ↓ reference
MCP tools (store_memory, retrieve_memory, track_confidence, add_timeline_entry, etc.)
    ↑ spawned by
Extension (aimos.mcpServerPath) + mcp.json
    ↑ configures
User/workspace settings.json
```

- **Rules** name MCP tools explicitly (e.g. `store_memory`, `retrieve_memory`).
- **protocol-tool-guidance** maps protocols (task completion, grounding, etc.) to tools.
- **dynamic-rules** specifies which MCP tools to use for auditing, development, documentation, research, planning.
- **Extension settings** control MCP server path and behavior.
- **mcp.json** controls which MCP servers Cursor starts.
- **Skills** reference rules and docs; agents invoke them when relevant.

---

## 6. How to Adjust Each Component

### Rules

1. **Add a rule:** Create `.cursor/rules/<name>.mdc` with YAML frontmatter (`alwaysApply`, `globs`, `description`).
2. **Change application:** Edit frontmatter; `alwaysApply: true` = always; `globs: "**/path/**"` = when editing matching paths.
3. **Disable:** Rename to `.DISABLED` or remove from Cursor's rule set.
4. **Note:** `.cursor/` is in `.gitignore`; rules may need to be tracked via alternate path or documented for sharing.

### Skills

1. **In-repo:** Add `.cursor/skills/<name>/SKILL.md` with frontmatter and steps.
2. **User-level:** Add under `~/.cursor/skills/` or `~/.codex/skills/`.
3. **Edit:** Modify SKILL.md; agents pick up changes on next invocation.

### Extension Settings

1. Open Cursor Settings (Ctrl+,).
2. Search "aimos".
3. Edit `aimos.mcpServerPath`, `aimos.crossModelEnabled`, etc.
4. Or edit `settings.json` directly.

### MCP Config

1. Open `~/.cursor/mcp.json`.
2. Add/remove/edit servers under `mcpServers`.
3. Restart Cursor.

---

## 7. Multi-Project / Other Projects

**Current layout:**

- One workspace root (AIM-OS or apps).
- All rules and skills come from root `.cursor/`.
- Per-project behavior via globs (e.g. `apps/ProEarth/**`).

**Options for other projects:**

- **Option A:** Add more glob-scoped rules at root for new paths.
- **Option B:** Add per-project `.cursor/` (e.g. `apps/ProEarth/.cursor/`) and open that folder as workspace.
- **Option C:** Hybrid – root globs + optional `.cursor/` in key project roots.

**Codex:** Separate IDE; skills in `~/.codex/skills/`; coordination docs in `knowledge_architecture/CODEX_SYSTEM/`.

---

## 8. References

- [AGENTS.md](../../Documentation/AGENTS.md) – Agent behavior, MCP, Cursor commands
- [base-rules.mdc](../../.cursor/rules/base-rules.mdc) – Core operational rules
- [dynamic-rules.mdc](../../.cursor/rules/dynamic-rules.mdc) – Context-aware rules
- [RULES_AND_SKILLS_PER_PROJECT_RESEARCH.md](../../apps/RULES_AND_SKILLS_PER_PROJECT_RESEARCH.md) – Multi-project design
- [MCP_TOOLS_ONBOARDING_MAPPING.md](../AGENT_ONBOARDING/MCP_TOOLS_ONBOARDING_MAPPING.md) – MCP tool mapping
- [CURSOR_RULES_UPDATE_SUMMARY.md](../../.cursor/CURSOR_RULES_UPDATE_SUMMARY.md) – Rules update history
- [DYNAMIC_CURSOR_RULES_SYSTEM.md](../cursor_rules_system/DYNAMIC_CURSOR_RULES_SYSTEM.md) – Rules system design
