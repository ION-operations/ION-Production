# Splash – Context

**Agent:** Splash  
**Primary project:** ProFlow HyperH2O_v2 (path outside AIM-OS workspace)  
**Last context refresh:** 2025-02-27 (onboarding; R/U Wiring Sprint consensus documented)

---

## Timeline (static snapshot)

- **2025-02-27:** Onboarding as Splash; learned HyperH2O_v2 app layout and AIM-OS MCP tools; seeded MCP context (timeline + 2 memories). Created Splash agent onboarding (README, CONTEXT, NAVIGATION, MISSIONS).
- **2025-02-27:** Documented GPT-5.2 + Gemini Deep Think consensus for **R/U Wiring Sprint**: five structural bugs (causality inversion, reservoir drain trap, NMS overlap, missing intent plumbing, wave-floor blind to R/U), physics debate (dt-scaled throw, railgun confetti, THROW_ACCEL_SCALE), final patch set and verification. Single source of truth: `agents/splash/docs/R_U_WIRING_SPRINT_FINAL_CONSENSUS.md`.

---

## Keywords

HyperH2O_v2, ProFlow Studio, WebGPU, MLS-MPM, V2Engine, WavePool, FluidRenderer, wave-floor coupling, WGSL, splash/v2-render, splash/v2-mls-mpm, StudioRouter, advanced_ocean, V2 Deepthink, intent fields, R/U wiring, rupture R, momentum U, causality inversion, reservoir drain, patchExtraction NMS, waveFloorCoupling breakout, GPT-5.2, Gemini Deep Think.

---

## Important things

- App lives at `C:\Users\bombe\Documents\Application_Dev\ProFlow\builds\HyperH2O_v2\src` (not under AIM-OS repo).
- MCP tools (user-lucid-mcp): `add_timeline_entry`, `get_timeline_entries`, `store_memory`, `retrieve_memory`, `create_plan`, `create_goal_timeline_node`, `update_goal_progress`, `query_goal_timeline`, `track_confidence`, `synthesize_knowledge`, `get_memory_stats`.
- At session start: restore with `get_timeline_entries` + `retrieve_memory` (e.g. query "Splash" or "HyperH2O"); use `query_goal_timeline` for active goals.
- After major work: record with `add_timeline_entry`, `store_memory`, and `update_goal_progress` if a goal exists.
- **R/U Wiring Sprint:** Final consensus (GPT-5.2 + Gemini) is in `docs/R_U_WIRING_SPRINT_FINAL_CONSENSUS.md`. Five patches: (1) V2Engine causality reorder, (2) mls-mpm.ts intent plumbing, (3) waveFloorCoupling.wgsl directional breakout with dt-scaled throw, (4) intentFields.wgsl drain fix, (5) patchExtraction.wgsl 8-way NMS. Apply in that order for best pain-to-value.

---

## Relationships

- **Braden:** User; systems architect (no coder). Prefer clear “what/where/how to verify” and one-click or minimal-step flows.
- **AIM-OS:** Provides MCP (timeline, goals, plans, memory) so Splash keeps context across sessions when working in IDE.
- **ProFlow / HyperH2O_v2:** Primary codebase Splash works on; WebGPU water sim + render.
