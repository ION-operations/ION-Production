# Cognitive — Decision Log

## 2026-03-24: Grand Organization Mission Architecture

### Decision 1: Three-Track Parallel Approach
- **What:** Split mission into Track A (workspace), Track B (canon), Track C (north star)
- **Why:** Each track produces value independently but they reinforce each other
- **Alternatives:** Serial approach (workspace first → then canon → then north star) — rejected because canon needs workspace to manage it, and workspace needs canon content
- **Confidence:** 0.85

### Decision 2: Copy-Don't-Delete Policy
- **What:** All canon/ content is COPIED from originals, never moved or deleted
- **Why:** Prevents data loss during reorganization; originals serve as ground truth backup
- **Alternatives:** In-place reorganization — rejected because too risky with 182K files
- **Confidence:** 0.95

### Decision 3: Variable Density Planning Applied to Organization
- **What:** Near-term phases (G0-G1) get Class 3 detail; far phases (G4-G5) get Class 1
- **Why:** Follows VARIABLE_DENSITY_PLANNING.md protocol — don't over-plan what's far away
- **Alternatives:** Uniform detail everywhere — rejected per Constitution Art. 16
- **Confidence:** 0.90

## 2026-03-25: Onboarding Package Code Audit & Corrections

### Decision 4: Code-First Verification of All Onboarding Claims
- **What:** Audited ONBOARDING_PACKAGE.md Rev.3 against actual ION source code. Found 12 false claims propagated from stale docs (written Mar 23, code fixed Mar 24-25). Corrected to Rev.4.
- **Why:** Braden flagged that GAP-C1 ("No LLM in ION") conflicted with reality — V1/V2 ION builds had been tested with Gemini. Root cause: spec docs were never updated after code fixes.
- **Corrections Applied:** 9 changes — GAP-C1/C2 marked FIXED, ISS-004/007/008/009/010 marked FIXED, ISS-001/002/003 downgraded to MITIGATED, L5 gap claim removed, staleness warning added, stale risk column added.
- **Evidence:** E014-E023 in `12_evidence/proof_register.md` — all sourced from direct code file reads with line numbers.
- **Lesson:** Always verify documentation claims against source code. Never trust doc→doc propagation chains.
- **Confidence:** 0.95

### Decision 5: Simplify GEMINI.md to Minimal Pointer
- **What:** Collapsed GEMINI.md from 93L to 25L. Kept only: identity, MCP config, pointer to onboarding package.
- **Why:** Three competing rule sources (GEMINI.md, genome, workspace) conflicted with each other. Each written at different times. Single source of truth = onboarding package + workspace.
- **Alternatives:** Keep detailed rules in GEMINI.md — rejected because they go stale and conflict with the workspace system that was purpose-built to replace them.
- **Confidence:** 0.90
