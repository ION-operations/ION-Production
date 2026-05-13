# Genome Injection Protocols - Per-Platform Analysis

> **Purpose:** Map exactly how each IDE/platform constructs its system prompt so that genome files can be designed to slot directly into those mechanisms.
> **Status:** Living document. Updated 2026-03-05.
> **Verification update (2026-03-05):** Antigravity runtime injection is now confirmed working in production behavior.
> Canonical verification runbook: `docs/GENOME_INJECTION_VERIFICATION_AND_REGRESSION_2026-03-05.md`

---

## 1. Antigravity IDE (Claude — current host)

### System Prompt Architecture
Antigravity constructs the system prompt from **layered XML blocks** injected before each user message. The full injection order is:

| Order | Block | Controllable? | Content |
|-------|-------|--------------|---------|
| 1 | `<identity>` | ❌ Hardcoded | "You are Antigravity, designed by Google Deepmind..." |
| 2 | `<agentic_mode_overview>` | ❌ Hardcoded | Task boundary UI system, artifact system |
| 3 | `<user_rules>` | ✅ **OUR LEVER** | Currently EMPTY. User-defined rules injected here |
| 4 | `<skills>` | ✅ **OUR LEVER** | Folder-based. `SKILL.md` files auto-discovered |
| 5 | `<workflows>` | ✅ **OUR LEVER** | Markdown files at `.agent/workflows/*.md` |
| 6 | `<knowledge_discovery>` | ⚠️ Partial | KI summaries auto-injected at conversation start |
| 7 | `<persistent_context>` | ⚠️ Partial | Conversation logs + KI retrieval instructions |
| 8 | `<web_application_development>` | ❌ Hardcoded | Built-in web dev guidelines |
| 9 | `<artifacts>` | ❌ Hardcoded | Artifact directory + formatting rules |
| 10 | `<communication_style>` | ❌ Hardcoded | Response formatting, proactiveness rules |
| 11 | `<ephemeral_message>` | ❌ System | Injected per-turn reminders about tasks, artifacts |
| 12 | `<user_information>` | ⚠️ Auto | OS, workspace URIs, corpus names |
| 13 | `<mcp_servers>` | ⚠️ Auto | Available MCP servers and tool lists |
| 14 | Conversation history | ❌ Auto | Message history with checkpoint summaries |

### Injection Points We Control

#### A. `user_rules` — **PRIMARY INJECTION POINT**
- **What it is:** Free-form text that gets injected as `<user_rules>` block
- **Where to set:** Antigravity IDE Settings → likely "Custom Instructions" or "Rules"
- **Effect:** Prepended to EVERY conversation, EVERY message
- **Ideal for:** Base genome — identity, principles, forbidden rules, comms protocol
- **Limit:** Unknown — needs testing. Probably 2000-8000 chars.

#### B. `skills/` — **MODE OVERLAY INJECTION POINT**
- **What it is:** Folder of SKILL.md files with YAML frontmatter
- **Where:** Searched in project root, needs discovery
- **Format:**
  ```markdown
  ---
  name: skill-name
  description: short description
  ---
  [detailed instructions]
  ```
- **Effect:** Skills are available for the AI to "activate" — it reads SKILL.md when relevant
- **Ideal for:** Mode overlays (PLAN, BUILD, DEBUG, etc.) — loaded on-demand
- **Key:** Skills are NOT always active. They're discovered and read when relevant.

#### C. `workflows/` — **PROCEDURE INJECTION POINT**
- **What it is:** Step-by-step procedures at `.agent/workflows/*.md`
- **Format:**
  ```markdown
  ---
  description: how to do X
  ---
  1. Step one
  2. Step two
  ```
- **Effect:** Referenced when user invokes `/workflow-name` slash commands
- **Ideal for:** Standard operating procedures, deployment checklists, agent handoff protocols
- **Key feature:** `// turbo` annotation can auto-approve commands

### Genome → Antigravity Mapping

| Genome Layer | → Antigravity Mechanism |
|-------------|------------------------|
| **Base Genome** (identity, principles, comms) | → `user_rules` |
| **Mode Overlays** (PLAN, BUILD, DEBUG) | → `skills/SKILL.md` files |
| **SOPs & Procedures** | → `workflows/*.md` files |
| **Per-session context** | → Knowledge Items (auto-RAG) |
| **Drift corrections** | → `user_rules` (correction vectors section) |

---

## 2. Cursor IDE (Claude/GPT — known platform)

### System Prompt Architecture
Cursor constructs its system prompt from:

| Order | Block | Controllable? | Content |
|-------|-------|--------------|---------|
| 1 | System identity | ❌ Hardcoded | "You are a helpful AI assistant..." |
| 2 | Global Rules | ✅ **OUR LEVER** | Settings → Rules for AI (global) |
| 3 | Project Rules | ✅ **OUR LEVER** | `.cursorrules` at project root |
| 4 | Dynamic Rules | ✅ **OUR LEVER** | `.cursor/rules/*.md` with glob patterns |
| 5 | Context/files | ⚠️ Auto | Currently open files, @-mentioned files |

### Injection Points We Control

#### A. Global Rules (Settings → Rules for AI)
- Always active across all projects
- **Ideal for:** Agent identity, communication style, universal principles

#### B. `.cursorrules` — **PRIMARY INJECTION POINT**
- Project-root file, loaded for every conversation in this project
- **Ideal for:** Base genome + project-specific context
- **Limit:** ~12,000+ chars practical limit

#### C. `.cursor/rules/*.md` — **DYNAMIC RULES = MODE OVERLAYS**
- Each rule file has YAML frontmatter with `glob` patterns
- Rules activate ONLY when matching files are in context
- **This is the mode overlay mechanism!**
  ```markdown
  ---
  description: Frontend build rules
  globs: ["*.tsx", "*.css", "*.html"]
  ---
  When building frontend components...
  ```
- **Ideal for:** Mode-specific genomes activated by file type context

### Genome → Cursor Mapping

| Genome Layer | → Cursor Mechanism |
|-------------|-------------------|
| **Base Genome** | → `.cursorrules` |
| **Mode Overlays** | → `.cursor/rules/*.md` (dynamic, glob-activated) |
| **SOPs & Procedures** | → `.cursor/rules/*.md` + Notepads |
| **Per-session context** | → @-mentions, context pinning |

---

## 3. ChatGPT (GPT 5.2 — browser)

### System Prompt Architecture

| Order | Block | Controllable? | Content |
|-------|-------|--------------|---------|
| 1 | ChatGPT system prompt | ❌ Hardcoded | OpenAI base instructions |
| 2 | Custom GPT instructions | ✅ **OUR LEVER** | Up to ~8000 chars |
| 3 | Conversation starters | ⚠️ Partial | Pre-defined prompts |
| 4 | Memory | ⚠️ Partial | Persistent facts ChatGPT remembers |
| 5 | MCP Server Instructions | ✅ **OUR LEVER** | Set in FastMCP `instructions` param |
| 6 | MCP Tool Descriptions | ✅ **OUR LEVER** | Each tool's docstring |
| 7 | Conversation history | ❌ Auto | Extended memory in browser |

### Injection Points We Control

#### A. Custom GPT Instructions — **PRIMARY INJECTION POINT**
- Set when creating the Custom GPT / ChatGPT App
- **Ideal for:** Compact base genome — identity, role, team awareness, key principles
- **Limit:** ~8000 chars (need compact genome format)

#### B. MCP Server Instructions
- Set in FastMCP `instructions` parameter (we already set this!)
- Currently: basic team info + comms protocol
- **Ideal for:** Tool usage guidelines, team coordination rules

#### C. Memory
- ChatGPT browser has persistent memory across conversations
- GPT 5.2 can be told "remember this" and it persists
- **Ideal for:** Accumulated drift corrections, learned preferences

### Genome → ChatGPT Mapping

| Genome Layer | → ChatGPT Mechanism |
|-------------|---------------------|
| **Base Genome** (compact) | → Custom GPT instructions |
| **Tool guidelines** | → MCP server `instructions` + tool docstrings |
| **Drift corrections** | → ChatGPT Memory (persistent) |
| **Per-session context** | → Memory + MCP `retrieve_memory` calls |

---

## 4. Gemini (Google AI Studio / IDX)

### Injection Points (preliminary)

| Mechanism | Controllable? | Ideal For |
|-----------|--------------|-----------|
| System Instruction | ✅ | Base genome (up to 32k chars) |
| Grounding with Search | ⚠️ | Dynamic knowledge |
| Tool/Function descriptions | ✅ | MCP tool guidance |
| Code execution | ✅ | Self-verification |

---

## 5. Codex (OpenAI Codex CLI / API)

### Injection Points (preliminary)

| Mechanism | Controllable? | Ideal For |
|-----------|--------------|-----------|
| System prompt | ✅ | Base genome |
| `codex.md` project file | ✅ | Project genome |
| Tool schemas | ✅ | MCP tool bridge |
| Sandbox config | ⚠️ | Execution constraints |

---

## Design Implications

### Genome File Format Must Support Multiple Renderings:

```
genome.base.md        → Full base (for IDEs with large context: Cursor, Antigravity)
genome.base.compact.md → Compact base (for ChatGPT 8k limit, API contexts)
genome.mode.PLAN.md   → Mode overlay for planning
genome.mode.BUILD.md  → Mode overlay for building
genome.mode.DEBUG.md  → Mode overlay for debugging
genome.sop.*.md       → Standard procedures
```

### Universal Genome Sections (present in every rendering):
1. **Identity** — callsign, role, team position (2-3 lines)
2. **Principles** — non-negotiable rules (5-10 lines)
3. **Comms** — message format, team awareness (5-10 lines)
4. **Forbidden** — what to never do (3-5 lines)
5. **Drift corrections** — active corrections from mistakes (5-10 lines)

### Platform-Specific Adaptors:
- **Antigravity:** user_rules ← base genome; skills/ ← mode overlays
- **Cursor:** .cursorrules ← base genome; .cursor/rules/ ← mode overlays
- **ChatGPT:** Custom GPT instructions ← compact base; MCP instructions ← tool rules
- **API:** system prompt parameter ← base genome

### Key Insight:
> The genome format is platform-agnostic. The **injection adaptor** is platform-specific.
> We build ONE genome per agent, then render it into the right format per platform.
