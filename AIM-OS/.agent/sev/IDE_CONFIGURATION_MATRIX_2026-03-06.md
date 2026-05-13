# IDE Configuration Matrix (2026-03-06)

**Status:** active local doctrine
**Owner:** Sev
**Purpose:** map the real control surfaces for each host so AIM-OS rules, genomes, commands, skills, and MCP paths are governed per IDE instead of assumed to be universal.

---

## Executive Summary

- AIM-OS does not run inside one prompt environment. Cursor Composer, Cursor Codex, Codex CLI, Antigravity, Gemini CLI, and browser ChatGPT each attach identity, tools, and rules through different mechanisms.
- The repo already contains a dense Cursor control stack, but several runtime-critical layers live in user-home config or host-injected prompts outside version control.
- The main governance risk is drift between repo-tracked doctrine and real host/runtime configuration.
- No host should be called "configured" unless three things are known: the instruction source, the MCP/tool source, and the manual operator steps required to keep it alive.

---

## Host Matrix

| Host | Identity + Rules Surface | Skills / Commands / Subagents | MCP / Tool Surface | Current Judgment | Required Action |
|------|--------------------------|--------------------------------|--------------------|------------------|-----------------|
| **Cursor Composer 1.5** | `.cursorrules`, `.cursor/rules/*.mdc`, Cursor global "Rules for AI" | `.cursor/skills/*`, `.cursor/commands/*`; skill-level subagent pattern exists | `C:\\Users\\bombe\\.cursor\\mcp.json` stdio mount; cached tool schemas under `C:\\Users\\bombe\\.cursor\\projects\\...\\mcps\\` | Strongest repo-tracked host, but doctrine drifted | Decide one authoritative base-rule surface and neutralize stale Aether-era rule text |
| **Cursor Codex pane** | Host/session injected instructions; repo has no committed `AGENTS.md` or `codex.md` in this checkout | Unknown whether Cursor skills/commands attach to Codex pane; treat as unproven | Tool path is not fully proven from disk in this pass | Highest ambiguity | Run a dedicated zero-context + MCP verification pass for Codex-in-Cursor as its own host |
| **Codex CLI** | `C:\\Users\\bombe\\.codex\\config.toml`, `C:\\Users\\bombe\\.codex\\rules\\default.rules`, system skills in `C:\\Users\\bombe\\.codex\\skills\\` | Codex system skills present; AIM-OS-specific project rule layer absent | On-disk `lucid-mcp` stanza in `config.toml`; native registration still unproven | Unverified and not meaningfully set up yet | Do first-time AIM-OS Codex CLI setup, prove native MCP registration, then create the project rule layer |
| **Antigravity / Opus** | `.agent/genomes/opus_user_rules.md`, `.agent/workflows/startup.md`, user-home `.gemini` config | `.agent/workflows/*`; `C:\\Users\\bombe\\.gemini\\antigravity\\skills.txt` points at Opus user rules | `C:\\Users\\bombe\\.gemini\\settings.json` and `C:\\Users\\bombe\\.gemini\\antigravity\\mcp_config.json` mount MCP | Operational, but injection proof drifted | Re-prove the live Opus injection file and keep a fresh zero-context boot witness |
| **Gemini CLI** | `C:\\Users\\bombe\\.gemini\\GEMINI.md`; provider wrapper in `scripts/ai_engine/providers/gemini_cli_provider.py` | Headless worker lane via provider and subprocess spawning | `.gemini/settings.json` mounts `lucid-mcp` and `ai-engine`, but provider defaults to `allowed_mcp_servers=['none']` unless explicitly enabled | Available, intentionally conservative | Define when Gemini workers stay MCP-free versus MCP-enabled |
| **Browser ChatGPT** | Custom instructions / Custom GPT instructions / MCP server instructions; external to repo | No direct repo-native command or skill surface; context packaging is the control mechanism | SSE via `scripts/mcp_sse_server.py` plus `scripts/ngrok_tunnel.py` | Manual/external lane | Keep one tracked source text for browser instructions and one owner for context packaging |

---

## Confirmed Control Surfaces

### Cursor / Composer

- Project rule stack exists in `.cursor/rules/`.
- Project skills exist in `.cursor/skills/`.
- Project commands exist in `.cursor/commands/`.
- Global Cursor MCP mount exists in `C:\\Users\\bombe\\.cursor\\mcp.json` and directly launches `lucid_mcp_server.py` with stdio.
- Composer-specific audit behavior exists in `.cursor/rules/modes/COMPOSER.mdc`.
- Skill-level subagent guidance exists in `.cursor/skills/opus-world-editor-orchestration/SKILL.md`.

### Codex CLI

- `C:\\Users\\bombe\\.codex\\config.toml` is real and contains a `lucid-mcp` stdio stanza on disk.
- `C:\\Users\\bombe\\.codex\\rules\\default.rules` exists, but it is dominated by unrelated `ProFlow` command allowlists.
- `C:\\Users\\bombe\\.codex\\skills\\.system\\skill-creator` and `skill-installer` are present.
- Operator clarification: Codex CLI has not actually been used or set up yet as an AIM-OS lane.
- Live verification on 2026-03-07: `codex mcp list` still returns `No MCP servers configured yet.`
- No repo `codex.md` was found in this checkout.

### Antigravity / Gemini Home Layer

- `C:\\Users\\bombe\\.gemini\\settings.json` mounts both `lucid-mcp` and `ai-engine`.
- `C:\\Users\\bombe\\.gemini\\antigravity\\mcp_config.json` mounts `lucid-mcp`.
- `C:\\Users\\bombe\\.gemini\\antigravity\\skills.txt` points to `.agent/genomes/opus_user_rules.md`.
- `.agent/workflows/startup.md` is part of the shared workflow layer used by this stack.

### Browser ChatGPT

- Native browser MCP path is documented as SSE + ngrok in `docs/MCP_RUNBOOK.md`.
- External ChatGPT packaging ownership already exists in `context/` and related roundtable canon.
- Browser instructions themselves still live outside repo-enforced control unless explicitly mirrored back into tracked files.

---

## Confirmed Drift / Conflicts

1. `.cursorrules` still presents a generated "Aether / Project Aether" identity and quality model that does not match current Sev/Opus governance.
2. `.cursor/rules/base-rules.mdc` still opens with Project Aether framing.
3. `.cursor/rules/agents/AGENT_ONBOARDING_INTEGRATION.md` freezes a 2025 agent roster and outdated Sev/Codex roles.
4. `docs/GENOME_INJECTION_VERIFICATION_AND_REGRESSION_2026-03-05.md` says `C:\\Users\\bombe\\.gemini\\GEMINI.md` contains Opus identity, but the current file content is a Gemini CLI identity block. That means the documented Antigravity injection proof is no longer trustworthy without re-verification.
5. `C:\\Users\\bombe\\.codex\\rules\\default.rules` is not AIM-OS-specific.
6. Earlier matrix language overstated Codex CLI readiness from on-disk residue alone. Current verified state is weaker: config files exist, but native MCP registration is still absent and the lane is effectively unproven.
7. This Codex session received `AGENTS.md`-style instructions from the host, but there is no committed `AGENTS.md` file in the repo root here. Part of Codex behavior is therefore being injected outside version control.

---

## Cross-Host Governance Rules

1. Treat each host as a separate operating environment even when they point at the same repo.
2. Keep one authoritative record for each host with:
   - identity injection source
   - MCP/tool source
   - commands/skills/subagent surface
   - manual setup path
   - last verified date
3. Prefer repo-tracked shim files that point to home-directory runtime files when the host requires external config.
4. Never infer that one host inherits another host's rules just because both are inside Cursor or both can reach the same MCP server.

---

## Immediate Hardening Order

1. **Cursor:** decide whether `.cursorrules` remains a real base layer or becomes a thin shim that points to the modern `.cursor/rules/` stack.
2. **Antigravity:** reproduce the live Opus injection path and re-freeze the proof with a fresh zero-context boot witness.
3. **Codex:** do the first real AIM-OS Codex CLI setup and native MCP proof, then create an AIM-OS-specific project rule layer and separately verify whether the Cursor Codex pane inherits it.
4. **Browser ChatGPT:** create one repo-tracked source text for custom instructions and one for MCP instruction text so packaging is not the only durable control surface.
5. **Gemini CLI:** define explicit policy for MCP-disabled versus MCP-enabled swarm workers.

---

## Operator Guidance

- If the task is **audit, indexing, document variance, or report generation**, start in **Cursor Composer**.
- If the task is **surgical code work with local repo access**, use **Codex CLI** or **Cursor Codex**, but do not assume they share identical rule layers.
- If the task is **broad build execution, JOC/frontend architecture, or high-context pair building**, use **Antigravity / Opus**.
- If the task is **parallel headless research or swarm slicing**, use **Gemini CLI** with an explicit MCP policy.
- If the task is **external deliberation or browser-native experimentation**, use **browser ChatGPT**, but treat it as an externally configured lane.

---

## Next Artifacts To Produce

1. `HOST_VERIFICATION_CARD_CURSOR_CODEX.md`
2. `HOST_VERIFICATION_CARD_ANTIGRAVITY.md`
3. `CODEX_PROJECT_RULE_LAYER.md`
4. `BROWSER_CHATGPT_INSTRUCTION_SOURCE.md`
