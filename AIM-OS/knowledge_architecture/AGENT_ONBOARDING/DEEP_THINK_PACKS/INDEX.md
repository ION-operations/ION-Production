# Deep Think Context Packs — Master Index

**Purpose:** Ready-to-use context packs and handoffs for **Gemini 3 Deep Think**. Each pack has a **handoff** (task brief) and a **file list** of ≤10 items to paste or attach in chat.  
**Constraint:** 10 files max per Deep Think session.  
**Last updated:** 2026-02-22

**Store Deep Think replies:** Save all Deep Think responses in **[RESPONSES/](RESPONSES/)**. See [RESPONSES/README.md](RESPONSES/README.md) for naming and [RESPONSES/RESPONSES_INDEX.md](RESPONSES/RESPONSES_INDEX.md) for the running index.

---

## How to use

1. Pick a pack below.
2. Open the pack’s **HANDOFF_*.md** — it contains the task and the exact file list.
3. In Gemini (or your AI chat), paste the handoff text, then attach or paste the listed files (≤10 total).
4. Send; let Deep Think reason and respond.

---

## Pack 1: Two-tier container physics (pool + deck)

| Item | Path |
|------|------|
| **Handoff** | [HANDOFF_TWO_TIER_CONTAINER.md](HANDOFF_TWO_TIER_CONTAINER.md) |
| **Files (≤10)** | See handoff § "Files to attach" |

**One-line ask:** Review and validate the two-tier container (deck + pool) WGSL/CPU design so particles stop falling through the deck; suggest any corrections or edge cases.

---

## Pack 2: Phase 3 — Soft boundary between inner and outer pools

| Item | Path |
|------|------|
| **Handoff** | [HANDOFF_PHASE3_SOFT_BOUNDARY.md](HANDOFF_PHASE3_SOFT_BOUNDARY.md) |
| **Files (≤10)** | See handoff § "Files to attach" |

**One-line ask:** Design or refine the soft-boundary coupling between the inner MPM sim (le) and outer MPM sim (leOuter): zone-attraction force, overlap band, and tuning so waves can cross without hard walls.

---

## Pack 3: Phase 4 — Heightfield–particle bidirectional coupling

| Item | Path |
|------|------|
| **Handoff** | [HANDOFF_PHASE4_HEIGHTFIELD.md](HANDOFF_PHASE4_HEIGHTFIELD.md) |
| **Files (≤10)** | See handoff § "Files to attach" |

**One-line ask:** Design bidirectional coupling between the outer particle pool and the heightfield wave solver (particles → waves, waves → particles) and integration with the existing wave floor.

---

## Pack 4: MLS-MPM full roadmap (container + Phase 3 + Phase 4)

| Item | Path |
|------|------|
| **Handoff** | [HANDOFF_MLS_MPM_FULL_ROADMAP.md](HANDOFF_MLS_MPM_FULL_ROADMAP.md) |
| **Files (≤10)** | See handoff § "Files to attach" |

**One-line ask:** Given the full multi-pool architecture, recommend implementation order, dependency graph, and any design conflicts or simplifications across container fix, Phase 3, and Phase 4.

---

## Pack 5: AIM-OS goals and plan prioritization

| Item | Path |
|------|------|
| **Handoff** | [HANDOFF_GOALS_PRIORITIZATION.md](HANDOFF_GOALS_PRIORITIZATION.md) |
| **Files (≤10)** | See handoff § "Files to attach" |

**One-line ask:** Given GOAL_TREE and the MLS-MPM / Globe / AIM-OS plans, suggest ordering and focus for the next 2–4 weeks and flag risks or bottlenecks.

---

## Pack 6: Globe sign-off (startup, moon, city glow)

| Item | Path |
|------|------|
| **Handoff** | [HANDOFF_GLOBE_SIGNOFF.md](HANDOFF_GLOBE_SIGNOFF.md) |
| **Files (≤10)** | See handoff § "Files to attach" — 5 files: sign-off plan, T0, T1, weather state, GCM plan |

**One-line ask:** Reason about the ION Globe sign-off plan (startup freeze, moon, city glow); recommend approve / approve by section / request changes; give risks. **Deep Think has no project** — only the attached files + your message.

---

## Quick reference: all handoff files

| Pack | Handoff file |
|------|----------------|
| 1. Two-tier container | `DEEP_THINK_PACKS/HANDOFF_TWO_TIER_CONTAINER.md` |
| 2. Phase 3 soft boundary | `DEEP_THINK_PACKS/HANDOFF_PHASE3_SOFT_BOUNDARY.md` |
| 3. Phase 4 heightfield | `DEEP_THINK_PACKS/HANDOFF_PHASE4_HEIGHTFIELD.md` |
| 4. MLS-MPM full roadmap | `DEEP_THINK_PACKS/HANDOFF_MLS_MPM_FULL_ROADMAP.md` |
| 5. Goals prioritization | `DEEP_THINK_PACKS/HANDOFF_GOALS_PRIORITIZATION.md` |
| 6. Globe sign-off | `DEEP_THINK_PACKS/HANDOFF_GLOBE_SIGNOFF.md` |

All paths relative to repo root: `knowledge_architecture/AGENT_ONBOARDING/`.
