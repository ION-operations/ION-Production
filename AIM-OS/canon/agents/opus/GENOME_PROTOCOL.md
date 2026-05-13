# Agent Genome Protocol v2.0

**What this is:** Every agent in AIM-OS has an **operational identity** built from three layers. When an agent starts a new conversation, its genome should be loaded as early context so the agent knows who it is, what platform it's on, and how to optimize for its LLM.

**This is not documentation.** This is calibration. The genome doesn't describe what an agent can do — it makes the agent *be themselves* from the first message.

---

## Three-Layer Architecture

Every deployed genome is assembled from three files:

```
Universal Core + Platform Adapter + Model Affinity = Deployed Genome
```

| Layer | File Pattern | What It Contains | Shared? |
|-------|-------------|------------------|---------|
| **Universal Core** | `cores/{agent}.core.md` | Identity, mission, authority, principles, scope, drift log | One per agent |
| **Platform Adapter** | `platforms/{platform}.adapter.md` | Startup protocol, file paths, tool routing, output format | One per platform, shared by all agents |
| **Model Affinity** | `affinities/{model}.affinity.md` | LLM-specific tuning, failure modes, personality, optimization | One per model family, shared by all agents |

### Key Rules

- **The core never changes during porting.** Only adapters and affinities change.
- **No file paths in cores.** Cores are pure identity — platform-agnostic.
- **No identity in adapters.** Adapters are pure mechanics — agent-agnostic.
- **No platform mechanics in affinities.** Affinities are pure LLM tuning.

---

## Assembly Examples

| Agent | Platform | Model | Load Order |
|-------|----------|-------|------------|
| OPUS | Antigravity IDE | Claude Opus 4.6 | `cores/opus.core.md` → `platforms/antigravity.adapter.md` → `affinities/claude.affinity.md` |
| SEV | ChatGPT | GPT-5.4 | `cores/sev.core.md` → `platforms/chatgpt.adapter.md` → `affinities/gpt.affinity.md` |
| CODEX | Cursor (Codex ext) | GPT-5.4 | `cores/codex.core.md` → `platforms/cursor.adapter.md` → `affinities/gpt.affinity.md` |
| COMPOSER | Cursor (Composer) | Claude Sonnet 4 | `cores/composer.core.md` → `platforms/cursor.adapter.md` → `affinities/claude.affinity.md` |
| OPUS | CLI | Gemini 2.5 Pro | `cores/opus.core.md` → `platforms/cli.adapter.md` → `affinities/gemini.affinity.md` |
| Specialist | CLI | Local (Ollama) | `cores/specialists/{agent}.core.md` → `platforms/cli.adapter.md` → `affinities/local.affinity.md` |

---

## Universal Core Structure (7 Sections)

Every core contains these sections:

| # | Section | Purpose | Update Frequency |
|---|---------|---------|-----------------|
| 1 | **Identity** | Callsign, name, role, rank, version | Rare |
| 2 | **Mission/Role** | What they do, current season | After major mission changes |
| 3 | **Authority** | May do / requires approval / must not | After authority changes |
| 4 | **Principles** | Non-negotiable behavioral rules | Rare |
| 5 | **Force Map** | Who they work with, chain of command | When team evolves |
| 6 | **Scope & Ownership** | What they own/contribute/avoid | After scope changes |
| 7 | **Drift Log** | Recent mistakes and corrections (last 10) | After every significant session |

**Rules:**
- Keep cores under 300 lines. Compress ruthlessly.
- Correction vectors must be specific, not generic.
- The drift log keeps only the last 10 entries.
- **No file paths, tool names, or platform mechanics in the core.**

---

## How to Update

### Core Updates
When something significant happens (mission change, authority change, drift correction):
- Update the affected section in the core
- Add a drift log entry
- Increment version

### Platform Adapter Updates
When platform mechanics change (new tool routing, file path changes, new capabilities):
- Update the shared adapter
- All agents on that platform get the update automatically

### Model Affinity Updates
When you learn something about a model's behavior (new failure mode, new strength):
- Update the shared affinity
- All agents using that model get the update automatically

---

## Current Inventory

### Cores
| Agent | File | Rank | Role |
|-------|------|------|------|
| OPUS | `cores/opus.core.md` | EXECUTIVE | COO, autonomous operator |
| SEV | `cores/sev.core.md` | EXECUTIVE | Delegated CEO, doctrine lead |
| CODEX | `cores/codex.core.md` | SPECIALIST | Lead Builder |
| COMPOSER | `cores/composer.core.md` | WORKER | Drift auditor |
| COMPOSER-SEV | `cores/composer-sev.core.md` | WORKER | SEV drift auditor |

### Platform Adapters
| Platform | File |
|----------|------|
| Antigravity IDE | `platforms/antigravity.adapter.md` |
| Cursor IDE | `platforms/cursor.adapter.md` |
| ChatGPT Web | `platforms/chatgpt.adapter.md` |
| CLI | `platforms/cli.adapter.md` |

### Model Affinities
| Model Family | File |
|-------------|------|
| Claude | `affinities/claude.affinity.md` |
| GPT | `affinities/gpt.affinity.md` |
| Gemini | `affinities/gemini.affinity.md` |
| Local (Ollama) | `affinities/local.affinity.md` |

### Legacy Genomes
Previous single-file genomes are preserved in `legacy/` for historical reference.

---

## Porting to New Platforms

See `PORTING_GUIDE.md` for instructions on creating adapters for new platforms.

---

*Genome Protocol v2.0 — Three-layer architecture. The core is the soul. The adapter is the shell. The affinity is the tuning. Same agent, any platform.*
