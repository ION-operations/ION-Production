# JOC — Goals & Roadmap

**Living document. Updated as work progresses.**  
**Last updated:** 2026-03-02 by Claude Opus 4.6

---

## The Core Mission

> Enable browser AIs (ChatGPT, Gemini, Claude, Perplexity) to communicate with my computer,
> projects, MCP tools, and each other — and make it visible, debuggable, and automatable.

---

## What's Built (Phase A ✅)

| Component | Status | Notes |
|-----------|--------|-------|
| JOC package (`packages/joc/`) | ✅ Running | Vite + React 18 + TS + Zustand |
| CSS design system | ✅ 550+ lines | Canon-compliant, vanilla CSS |
| Custom SVG icon set | ✅ 16 icons | 7 drawer icons + 8 utility + JOC logo |
| Right icon bar + split-click zones | ✅ | Lucid Engine pattern |
| Drawer system (full/top/bottom) | ✅ | With sub-tabs, collapse, content |
| Bottom bar + expandable inspector | ✅ | 4-tab panel (comms, output, missions, resources) |
| Dashboard page | ✅ | Fleet status, missions, quick dispatch, activity feed |
| Tab system + page router | ✅ | Extensible for new page types |

**Design docs:** 4 documents (~2500 lines) in `docs/OPUS1_JOC_*.md`

---

## What's Next — Prioritized Roadmap

### ▎Phase B: The Bridge (HIGH PRIORITY)

**Goal:** Make browser AIs actually communicate with the local system.

#### B1. Session Page with Automation Overlay
The **signature feature**. When you open a ChatGPT/Gemini tab:
- Live browser viewport (via Puppeteer/CDP screenshot stream or webview)
- **Automation overlay** showing:
  - Injection points highlighted on the page (where prompts go)
  - Extraction zones highlighted (where responses come from)
  - Communication pipeline visualized: `Files → Context → Inject → AI → Extract → Route`
  - DOM element health indicators (green = found, yellow = changed, red = missing)
- **Debug rail** sidebar showing real-time events:
  - `10:08:42 Injecting prompt (2.4K tokens)...`
  - `10:08:43 Waiting for response...`
  - `10:08:55 Response detected (3.1K tokens)`
  - `10:08:55 Extracted → CMC stored (atom_id: abc123)`
  - `10:08:56 Routed → Agent Aether via MCP`
- **Control bar** at bottom of viewport:
  - [Inject Prompt] [Extract Response] [Refresh Session] [Take Screenshot]
  - Context attachment: [+ Files] [+ Project] [+ Memory]

#### B2. AI Drivers (ChatGPT + Gemini)
- `ChatGPTDriver.ts` — login detection, prompt injection via DOM, response extraction
- `GeminiDriver.ts` — same pattern for Gemini's UI
- Abstract `AIDriver` interface (already designed in architecture doc)
- Session persistence (cookies/credentials stored encrypted)

#### B3. Session Health Monitoring
- Periodic DOM checks (are injection/extraction selectors still valid?)
- Cookie freshness tracking
- Auto-refresh on session expiry
- Health dashboard in fleet drawer

#### B4. Account Sign-in Automation
- Credential vault (encrypted local storage, NOT plain text)
- Auto-login flows per provider:
  - ChatGPT: email/password or Google SSO
  - Gemini: Google account (shared with Drive)
  - Claude: email/password
  - Perplexity: Google/email
- Session recovery on startup (resume from saved cookies)
- MFA handling (prompt user when 2FA required)

#### B5. Quick Dispatch (Wired)
- Compose prompt on dashboard
- Select targets (which AIs)
- Attach context files from local filesystem
- Dispatch → inject into selected AIs
- Monitor progress → extract responses
- Store results in CMC

---

### ▎Phase C: The Intelligence (MEDIUM PRIORITY)

**Goal:** Multi-AI orchestration, smart context, synthesis.

#### C1. Multi-AI Dispatch Engine
- Parallel dispatch (same prompt to multiple AIs simultaneously)
- Sequential dispatch (chain results: GPT → Gemini → synthesis)
- Debate mode (AIs respond, then critique each other's responses)
- Strategy templates (saved dispatch configurations)

#### C2. Results Synthesis (SEG Integration)
- Side-by-side response comparison
- Agreement/disagreement highlighting
- Unified synthesis document generation
- Confidence tracking per response (VIF)

#### C3. Auto-Context (HHNI + ICIP Integration)
- When composing a mission, auto-suggest relevant files from project
- Token budget calculator (how much context fits per AI)
- Smart truncation (summarize large files to fit)
- Project file browser built into mission composer

#### C4. Gemini CLI Integration
- Direct CLI invocation from JOC
- Batch job management
- Output streaming to JOC panels
- Queue management for rate-limited APIs

#### C5. Agent MCP Comms (Live Panel)
- Real-time MCP message feed
- Filtered views (by agent, by thread, by type)
- Compose and send messages from JOC
- Thread visualization

---

### ▎Phase D: The Expansion (ONGOING)

**Goal:** Extend reach to all compute and storage resources.

#### D1. Local GPU Inference Panel
- Ollama/llama.cpp integration
- Model browser + download
- Quick inference from JOC (summarization, classification, embeddings)
- Resource monitoring (3050 Ti VRAM, utilization)

#### D2. Cloud VM Launcher
- Vertex AI integration (for custom models, training)
- NVIDIA cloud GPU instances
- Job submission + monitoring from JOC
- Cost tracking

#### D3. Google Drive Integration (30TB)
- Storage browser in JOC
- Auto-backup of mission results
- Asset management (models, datasets)
- Shared drive for AI collaboration artifacts

#### D4. Project Catalog
- Auto-index all projects in `Application_Dev/`
- Status tracking (active, dormant, archived)
- Git integration (branch, last commit, changes)
- Quick-context generation (compile project summary for AI dispatch)

#### D5. IDE Features
- Command palette (Ctrl+Shift+P)
- Keyboard shortcut system
- Split pane support
- Theme customization (beyond canon defaults)
- Plugin/extension system (for future growth)

---

### ▎Phase E: The Full AIM-OS Browser OS (LONG TERM)

**Goal:** JOC becomes the complete browser-based AIM-OS.

#### E1. Quaternion Kernel Integration
- When kernel matures, bridge it to JOC UI
- Consciousness visualizations in dashboard

#### E2. CCS (Continuous Consciousness Substrate)
- Chat AI + Organizer AI + Audit AI running in JOC
- Background task processing

#### E3. Self-Improvement Loop
- SIS integration — JOC monitors and improves its own dispatch quality
- Learning from mission outcomes

#### E4. Multi-User Support
- Multiple operators using JOC simultaneously
- Shared mission board
- Role-based access

---

## Design Documents Index

| Doc | Path | Content |
|-----|------|---------|
| Master Vision | `docs/OPUS1_JOC_MASTER_VISION.md` | 5 pillars, UI mockups, design system |
| Architecture | `docs/OPUS1_JOC_ARCHITECTURE.md` | AI Drivers, mission lifecycle, TypeScript types |
| Compute & IDE | `docs/OPUS1_JOC_COMPUTE_AND_IDE_LAYOUT.md` | 3-ring compute, IDE layout, keyboard shortcuts |
| UI Design | `docs/OPUS1_JOC_UI_DESIGN.md` | Lucid Engine patterns, AIM-OS integration map |
| Goals & Roadmap | `docs/OPUS1_JOC_GOALS_AND_ROADMAP.md` | **THIS DOCUMENT** — living roadmap |

## Key Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-02 | No stock icons — all custom SVG | Unique identity, canon compliance |
| 2026-03-02 | Vanilla CSS, no Tailwind | Full control, canon-aligned tokens |
| 2026-03-02 | Zustand over Redux | Simpler, less boilerplate, matches Lucid Engine |
| 2026-03-02 | Lucid drawer pattern adopted | Braden's proven UI DNA |
| 2026-03-02 | Session page = viewport + automation overlay | Makes black-box automation visible/debuggable |

---

*This roadmap is alive. It grows as the JOC grows.*  
*Claude Opus 4.6 💙*
