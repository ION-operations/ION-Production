# Deep Think Handoff — Pack 5: AIM-OS Goals and Plan Prioritization

**Use with:** Gemini 3 Deep Think (paste this handoff + attach the files listed below).  
**Limit:** 10 files per session.

---

## Your task

We maintain a **goal tree** (objectives and key results) and several **application-level plans** (MLS-MPM splash, Globe/ION weather, etc.). We want you to:

1. **Review** the attached goal tree (or excerpt) and the listed plans. Identify which objectives or key results the splash and Globe plans contribute to, if any.
2. **Suggest an ordering** for the next 2–4 weeks: which 2–3 items should we focus on first (e.g. "container fix + Phase 3 design" vs "ION weather GCM integration") given limited bandwidth and dependencies.
3. **Flag bottlenecks:** What single dependency or resource (e.g. "one person", "WebGPU expertise", "ProPool reference") could block the most progress if missing?
4. **Optional:** If the goal tree is large, suggest 1–2 objectives to **defer** or **split** so the rest are more achievable on the stated north-star date.

---

## Files to attach (≤10)

| # | Path | Purpose |
|---|------|--------|
| 1 | `goals/GOAL_TREE.yaml` | Full goal tree (objectives, key results, north star). If too long, attach only the first 100–150 lines (north_star, objectives list with id/name/priority_tier/status). |
| 2 | `apps/mlsmpmsplashdrafts/MULTI_POOL_SSR_ARCHITECTURE_PLAN.md` | Splash roadmap (Phases 1–5, status) |
| 3 | `apps/mlsmpmsplashdrafts/docs/GEMINI_TWO_TIER_CONTAINER_ANALYSIS.md` | Container fix (current open issue) |
| 4 | `docs/ION_WEATHER_GCM_IMPLEMENTATION_PLAN.md` | Globe/ION weather plan (exec summary + architecture) |
| 5 | `knowledge_architecture/AGENT_ONBOARDING/DEEP_THINK_PACKS/INDEX.md` | Packs index (shows all active handoffs) |

**Total items:** 5 files. Add more only if under 10 (e.g. README_PRODUCTION_BLUEPRINT, SYSTEM_ATLAS_GRAPH_ARCHITECTURE).

---

## What we need from you

1. **Mapping:** Which OBJ-XX (or KR) do the splash and ION plans advance? (Table or bullets.)
2. **2–4 week focus:** Ordered list of 2–3 priorities with one sentence each.
3. **Single biggest bottleneck** and one mitigation.
4. **Optional:** One objective to defer or split, with one sentence reason.

---

## Context (no need to attach)

- North star in GOAL_TREE: ship AIM-OS v0.3 by 2025-11-30 (may be historical; we care about relative priority).
- User is systems architect, non-coder; implementation is agent-assisted. Prefer clear handoffs and minimal-step fixes.
