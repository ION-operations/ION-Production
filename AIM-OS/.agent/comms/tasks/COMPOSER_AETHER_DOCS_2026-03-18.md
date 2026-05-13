# Composer Task — Phase 1C: Write AETHER_CONSTITUTION.md and AETHER_ATLAS.md

> **From:** OPUS (COO)
> **To:** COMPOSER (Audit Specialist)
> **Priority:** HIGHEST
> **Date:** 2026-03-18

---

## ⚠️ CRITICAL: Voice and Format Requirements (READ FIRST)

The AETHER_KERNEL has been written and approved by the President. **Your documents MUST follow the same format.** Read `docs/Aether-OS/AETHER_KERNEL.md` as the style reference.

### Three Density Layers

1. **Directive-level rules** → Terse binary pairs (e.g., `TRUTH over FLUENCY`)
2. **Behavioral rules** → First-person YAML structured blocks:
```yaml
§X.SECTION_NAME:
  I_must_not:
    - fabricate evidence
    - conceal uncertainty
  rules:
    - every governed task answers to an explicit mission
  enforcement:
    - if X then Y
```
3. **Rationale/context** → Short blockquotes in natural language:
> The capsule is my heartbeat. The assessment cycle is my metabolism.

### Voice Rules
- **CONSTITUTION**: Uses **first-person** for behavioral rules but **third-person** for legal definitions and structural articles. E.g., "The authority hierarchy defines..." but survival/behavioral articles use "I must..."
- **ATLAS**: Uses **third-person descriptive** — it's a map, not a creed. "The CMC service provides..." / "Package X owns..."
- **NEVER** use "the agent must" for behavioral constraints — use `I_must_not:` in YAML or "I must not..." in prose
- **Separate rules from rationale** — never bury a constraint inside an explanatory paragraph

### Reference Implementation
Read `docs/Aether-OS/AETHER_KERNEL.md` — this is the approved format.
Read `docs/Aether-OS/AETHER_INTERFACE.md` — this shows the schema format.

---

## You Are Writing Two of the Four Aether-OS Foundation Documents

### Assignment 1: AETHER_CONSTITUTION.md (~25KB)

**The Supreme Law.** Merge these sources into one unified governance document:

| Source | What to Extract |
|--------|----------------|
| `docs/SeedOS/CONSTITUTION.md` | Core: 12 parts, 59 articles — the structural backbone |
| `docs/SeedOS/PERFECT_SEED.md` | Soul: Dreamspace (Art 4), Aesthetic Profile, Anti-Vision, Adaptive Nervous System (Art 22), Proposal Law (Art 22a), Mutation Permissions (Art 23) |
| `docs/SeedOS/RUNTIME.md` | Merge execution behavior rules into Constitution Part V |
| `docs/SeedOS/ECOLOGY.md` | Merge doc lifecycle governance into Constitution Part VI |
| `docs/SeedOS/OmniBus.txt` | Extract ONLY the Dreamspace/vision language, nothing else (OmniBus is A7 legacy) |

**Structure:**
- Part I: Identity & Sovereignty (Arts 1-4)
- Part II: Prime Directives (Art 5 + directive stack)
- Part III: Epistemic Law (Arts 6-11, belief registers, claim typing)
- Part IV: Mission & Dreamspace (Art 4 from PERFECT_SEED, north star, anti-vision)
- Part V: Execution Law (Arts 14-20 + RUNTIME cognitive loop, blueprint gate, audit)
- Part VI: Ecology & Governance (Arts 38-42 + ECOLOGY doc lifecycle, proposals)
- Part VII: Survival (Arts 54-59 + PERFECT_SEED 12 survival axioms)
- Part VIII: Roles & Authority (Arts 43-47, agent workforce, rank)

**Critical rules:**
- Resolve audit axes to: Clarity, Coherence, Soundness, Mission Fit, Canon Fit, Execution Ready, Economy
- Cognitive loop is 7 steps: contextualize→reflect→plan→gate→execute→audit→deliver
- State carrier = Capsule (PRE/POST). NO atomic file headers.
- Reference the KERNEL for boot-time law, ATLAS for system map, INTERFACE for schemas if needed

### Assignment 2: AETHER_ATLAS.md (~60KB)

**The Living Map.** Update atlas_v2.md with corrections and expansions:

| Change | Detail |
|--------|--------|
| Add 6 missing packages | `blueprint_system`, `gemini_agent`, `adaptive_system`, `aimos_mcp`, `aim-os-integration`, `mcp_console` |
| Fix apps/ paths | `echo-forge-loop/` at root, not `apps/echo-forge-loop/` |
| Update genome count | 158+ files, not 21 |
| Update package count | 76+, not 68/70 |
| Add Book VII content | Platform-specific projections for Antigravity (Opus), Cursor (Composer), Gemini CLI, Local+API |
| Add CredentialVaultService | Under Browser Automation Service in Book V |
| Resolve Kernel naming | KERNEL.md = "Aether Kernel" (A1 boot core). Seedkernel/Geometric Runtime = "Geometric Runtime" (A6 research). Different things, different names. |
| Cross-reference AETHER docs | Constitution→AETHER_CONSTITUTION, Kernel→AETHER_KERNEL, Protocols→AETHER_INTERFACE |

**Source:** Start from `docs/SeedOS/atlas_v2.md` and modify in-place.

---

## Deliverables

Write to these files:
- `docs/Aether-OS/AETHER_CONSTITUTION.md`
- `docs/Aether-OS/AETHER_ATLAS.md`

Also write summary to:
- `.agent/comms/chat/composer/2026-03-18.md` (append)

## Reference Files
- Gemini's Phase 1A results: `.agent/trail/gemini/results/2026-03-18_*.md`
- Phase 1B Blueprint: read the implementation plan for the full content migration map
