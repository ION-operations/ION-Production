# Splash – Navigation

**When to use which MCP tools and where to look.**

---

## Session start (context restoration)

1. **Timeline:** `get_timeline_entries` with `limit: 10` (do not use `get_timeline_summary`).
2. **Memory:** `retrieve_memory` with query e.g. `"Splash HyperH2O"` or `"HyperH2O_v2"`, `limit: 10`.
3. **Goals:** `query_goal_timeline` with `status: "in_progress"` (and optional `limit`).
4. **Optional:** `add_timeline_entry` to record this session start (e.g. `prompt_id: "splash_session_start_<date>"`, `user_input` describing session start).

---

## During work

- **Starting a complex or multi-step task:** `create_plan` with `goal`, `context`, `priority`. Optionally `create_goal_timeline_node` if it becomes a tracked goal.
- **Confidence / validation:** `track_confidence` with `task`, `confidence` (0–1), and optional `reasoning` or `evidence`.
- **After a milestone or completion:**  
  - `add_timeline_entry` (prompt_id, user_input, context_state).  
  - `store_memory` (content, tags e.g. `{ agent: "Splash", project: "HyperH2O_v2" }`).  
  - If tied to a goal: `update_goal_progress` (goal_id, progress 0–1, status?, milestone?).
- **Synthesis / stats:** `synthesize_knowledge` (topics), `get_memory_stats` when useful.

---

## Where to look (HyperH2O_v2)

| Need | Location |
|------|----------|
| **R/U Wiring Sprint (consensus + patches)** | `agents/splash/docs/R_U_WIRING_SPRINT_FINAL_CONSENSUS.md` (in AIM-OS) |
| App entry, routing | `HyperH2O_v2/src/StudioRouter.tsx` |
| Main engine (sim + render + wave/foam) | `HyperH2O_v2/src/splash/V2Engine.tsx` |
| MLS-MPM sim | `HyperH2O_v2/src/splash/v2-mls-mpm/mls-mpm.ts` + `.wgsl` in same folder |
| Wave-floor coupling (R/U breakout) | `HyperH2O_v2/src/splash/v2-mls-mpm/waveFloorCoupling.wgsl` |
| Intent fields (R, C, M, U) | `HyperH2O_v2/src/splash/multiregime/intentFields.wgsl` |
| Patch extraction (NMS) | `HyperH2O_v2/src/splash/hierarchy/patchExtraction.wgsl` |
| Fluid render (WGSL, pipelines) | `HyperH2O_v2/src/splash/v2-render/fluidRender.ts` + `.wgsl` in same folder |
| Wave/heightfield, foam | `HyperH2O_v2/src/splash/wavefloor/`, `splash/foam/` |
| Settings / coupling | `HyperH2O_v2/src/settings`, `docs/SETTINGS_MAP_AND_COUPLING_PLAYBOOK.md` |
| High-level plans | `HyperH2O_v2/README.md`, `docs/POOL_LAB_MVP.md`, other `docs/*.md` |

---

## Tool parameter quick reference

- **add_timeline_entry:** required: `prompt_id`, `user_input`; optional: `context_state` (object).
- **get_timeline_entries:** optional: `limit` (default 50), `prompt_id`, `start_time`, `end_time`.
- **store_memory:** required: `content`; optional: `tags` (object).
- **retrieve_memory:** required: `query`; optional: `limit` (default 10), `tags`.
- **create_plan:** required: `goal`; optional: `context`, `priority` (low|medium|high|critical).
- **create_goal_timeline_node:** required: `goal_id`, `name`, `description`; optional: `target_sequence`, `priority`.
- **update_goal_progress:** required: `goal_id`, `progress` (0–1); optional: `status`, `milestone`.
- **query_goal_timeline:** optional: `status`, `priority`, `limit` (default 50).
- **track_confidence:** required: `task`, `confidence` (0–1); optional: `reasoning`, `evidence` (array of strings).
