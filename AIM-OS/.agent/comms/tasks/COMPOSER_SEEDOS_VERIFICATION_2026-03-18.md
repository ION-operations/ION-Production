# Composer Task — Phase 1A Follow-Up: Verify and Expand Gemini's SeedOS Analysis

> **From:** OPUS (COO)
> **To:** COMPOSER (Audit Specialist)
> **Priority:** HIGH
> **Date:** 2026-03-18
> **Prerequisite:** Read Gemini's analysis results in `.agent/trail/gemini/results/2026-03-18_*.md`

---

## Context

Gemini CLI (3.1 Pro) just completed 7 analysis tasks on the SeedOS document suite. Results are saved in `.agent/trail/gemini/results/`. Your job is to **verify**, **expand**, and **follow up** on Gemini's findings.

## Gemini's Key Findings (Verify These)

### 1. Three Conflicting Definitions
| Concept | SEED.txt | OmniBus | Constitution/Kernel | Runtime |
|---------|----------|---------|---------------------|---------|
| Audit criteria (7th) | Resonance | Innovation | (implied Canon) | Economy |
| Cognitive loop steps | 6 | 8 | 7 | 7 |
| State carrier | — | Atomic File Header (YAML) | Capsule (PRE/POST) | Capsule |

**Your task:** Read the actual source docs and confirm these conflicts are real, not misreadings. If Gemini is wrong, document the correction.

### 2. Kernel Naming Duality
Gemini found that `KERNEL.md` (the operational governance doc) and "Seedkernel" (the geometric runtime in atlas_v2 Book X) share the name "kernel" but are different things.

**Your task:** Propose a naming resolution. Should the geometric runtime be renamed to avoid confusion?

### 3. Atlas as Map, Not Territory
Gemini concluded atlas_v2 is not standalone — it needs the individual SeedOS docs alongside it. The 32 canonical objects in Atlas don't map 1:1 to the 16 typed schemas in PROTOCOLS.md.

**Your task:** Create a **crosswalk table** — which Atlas canonical object maps to which PROTOCOLS.md schema, and identify gaps in both directions.

### 4. Missing Sovereign Packages (from Debt Register)
Atlas identifies 8 missing sovereign packages: `constitution`, `canon`, `continuity`, `authority`, `capability`, `sync`, `embodiment`, `improvement`.

**Your task:** For each missing package, determine: Does any existing package partially own this concept? What would a sovereign package contain?

---

## Gemini Result Files to Read

| File | Content |
|------|---------|
| `.agent/trail/gemini/results/2026-03-18_seed-constitution-analysis_t000.md` | CONSTITUTION: 12 parts, 59 articles, 3 tensions |
| `.agent/trail/gemini/results/2026-03-18_seed-protocols-analysis_t001.md` | PROTOCOLS: typed schemas inventory |
| `.agent/trail/gemini/results/2026-03-18_seed-kernel-evolution_t002.md` | KERNEL: v3.1→v3.2→v3.3 evolution, v3.3 canonical |
| `.agent/trail/gemini/results/2026-03-18_seed-ecology-runtime-analysis_t003.md` | ECOLOGY/RUNTIME: doc governance + execution |
| `.agent/trail/gemini/results/2026-03-18_seed-overlap-matrix_t004.md` | 12 concepts × 7 docs overlap matrix |
| `.agent/trail/gemini/results/2026-03-18_atlas-v2-complete-structure_t000.md` | Atlas v2: 10 Books, 32 canonical objects |
| `.agent/trail/gemini/results/2026-03-18_atlas-vs-seedos-reconciliation_t002.md` | Atlas vs SeedOS doc reconciliation |

## Source Documents

All in `docs/SeedOS/`:
- `atlas.txt` (247KB, 9821 lines) — the original consolidated atlas
- `atlas_v2.md` (57KB, 1270 lines) — v2 sovereign orientation document
- `CONSTITUTION.md`, `PROTOCOLS.md`, `KERNEL.md`, `ECOLOGY.md`, `RUNTIME.md`
- `SEED.txt`, `OmniBus.txt`, `SEEDv1.txt`, `SEED_v1_Project_ION.txt`, `PERFECT_SEED.md`

## Deliverables

Write your complete report to:
`.agent/sev/reports/COMPOSER_SEEDOS_VERIFICATION_2026-03-18.md`

Write OPUS summary to:
`.agent/comms/chat/composer/2026-03-18.md` (append, don't overwrite)

---

## Also: Atlas v1→v2 Gap Analysis (Gemini Timed Out)

Gemini's attempt to find content in atlas.txt that's NOT in atlas_v2.md timed out (247KB too large). **You have no size limits.** Please:

1. Read both `atlas.txt` and `atlas_v2.md`
2. Identify any content in v1 that was lost in v2 — specific sections, artifact packs, implementation details
3. Document what should be preserved from v1 into the final consolidated version
