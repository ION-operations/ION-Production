# Deep Think Handoff — Globe Sign-Off Plan

**Use with:** Gemini Deep Think. **Attach** the files listed below (≤10). Deep Think has **no access to the project** — only these files and what you type.  
**Limit:** 10 files per prompt.

---

## Your task

You are helping a **systems architect** (no coding) decide whether to approve a **sign-off plan** for a WebGL globe app (ION). The plan covers three fixes: (1) **startup freeze** (~30 s browser freeze), (2) **moon** (port moon from non-weather to weather version), (3) **city glow** (change from directional beams to a single spreading gradient). No code will be changed until the architect signs off.

Use **only** the attached files as context. Recommend: approve full plan, approve by section, or request changes — and give risks and a clear answer to the question the architect types below.

---

## Files to attach (upload these in Gemini; ≤10 total)

Attach the following files from the repo. Paths are relative to repo root.

| # | Path | Purpose |
|---|------|--------|
| 1 | `docs/ION_GLOBE_FIXES_PLAN_SIGNOFF.md` | Full sign-off plan (startup, moon, city glow) — the thing to approve or change |
| 2 | `docs/Globe/T0_executive.md` | Globe/ION executive summary (~100 words) |
| 3 | `docs/Globe/T1_overview.md` | Globe/ION overview (~500 words): files, subsystems, current state |
| 4 | `docs/GLOBE_WEATHER_STATE.md` | Current weather state and known issues |
| 5 | `docs/ION_WEATHER_GCM_IMPLEMENTATION_PLAN.md` | Weather GCM plan — read at least §1 Executive Summary and §2 Architecture so you understand how weather fits; full file if under size limit |

**Total:** 5 files. You can attach this handoff as a 6th file so Deep Think sees the task, or paste the handoff text into the chat.

---

## What to type in the chat (your question)

After attaching the files, type your question. Examples:

- “Should I approve the full plan, or is there any section I should hold or change? Give me risks and a clear recommendation.”
- “Which startup-freeze option (A, B, or C) is best for a non-coder user who might think the app crashed?”
- “Is the city glow technical approach (radial falloff from one city center) sound? Any edge cases or alternatives?”

Or write your own question.

---

## Constraints (for context)

- Two main app files: **IONv4c.html** (globe + moon, no weather), **IONv4c-weather.html** (globe + optional weather; moon not yet ported). The plan fixes the **weather** version to match for moon and city glow.
- No code changes until the architect signs off. Deep Think is only being asked to reason and recommend.
