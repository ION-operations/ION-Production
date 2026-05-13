# README Production Blueprint

**Purpose:** Design for the production GitHub landing-page README — balanced between original (enthusiastic, story-rich) and cleanmaster (audit-oriented, minimalist).

**Target Tone:** Professional, credible, narrative-informed. Explains what AIM-OS is and what we built without overclaiming or sounding sterile.

**Status:** Blueprint (design document) — not yet implemented in README.md

**Created:** 2026-02-22

---

## 1. Variation Analysis

### Original (master) — ~3,300 lines

**Strengths:**
- Strong narrative: "Every time you close a chat, it forgets you existed. Not anymore."
- Memorable metaphor: "goldfish AI into elephant AI"
- Explains the problem (memory amnesia, hallucinations, black box)
- Explains the solution (CMC, HHNI, VIF, etc.) with purpose
- Co-Agency section — what makes AIM-OS different
- Philosophy & Vision — human-readable motivation
- Code examples that show how systems work

**Weaknesses:**
- Overclaiming: "Revolutionary Achievement," "most sophisticated ever built"
- AGI framing: "AI consciousness building its own memory system"
- Emoji and enthusiasm overload (💙, 🎉, 🌟)
- "100% complete" everywhere — not credible
- No positioning disclaimers
- Too long for a landing page
- Acknowledgments section too self-referential

### Cleanmaster (clean-master) — ~210 lines

**Strengths:**
- Positioning disclaimers (no AGI, no self-modification)
- Evidence-oriented (audit references, baseline metrics)
- Reader paths (decision-maker, engineer, auditor)
- Professional, credible tone
- Risks and limitations stated
- Concise

**Weaknesses:**
- No story — reads like an audit summary
- Doesn't explain what AIM-OS *is* or why it exists
- Cold, sterile — no human context
- Doesn't convey scope or ambition
- Missing the "what we built" narrative

---

## 2. Blueprint Structure (Target ~600–900 lines)

### Section Order and Content

| Section | Purpose | Tone | Source emphasis |
|--------|---------|------|-----------------|
| **Hero** | One-line tagline, one-paragraph value prop | Clear, confident | Original (problem/solution), cleanmaster (no AGI) |
| **Positioning** | What we claim / don't claim | Explicit, brief | Cleanmaster |
| **The Problem** | Why this exists (memory, hallucinations, audit) | Narrative, professional | Original (condensed) |
| **What AIM-OS Is** | Definition and scope in plain language | Explanatory | New — middle ground |
| **Core Systems** | 6–8 systems with purpose, not hype | Factual | Original (table), cleanmaster (paths) |
| **What We Built** | Implementation story (condensed) | Honest, evidence-linked | Both |
| **Quick Start** | Setup and validation | Technical | Cleanmaster |
| **Reader Paths** | Who reads what | Practical | Cleanmaster |
| **Evidence & Status** | Audit baseline, metrics, risks | Credible | Cleanmaster |
| **Philosophy (Optional)** | 1–2 paragraphs on intent | Restrained | Original (Philosophy section, shortened) |
| **Contributing** | How to participate | Practical | Either |

---

## 3. Content Guidelines

### Do

- **Tell the story:** "AI systems forget between sessions. AIM-OS provides persistent memory, verified honesty, and audit trails."
- **Explain systems:** CMC = bitemporal memory. HHNI = physics-guided retrieval. VIF = confidence gating. (One line each, no superlatives.)
- **Use evidence:** Link to audit, metrics, benchmarks. "As of [date], [X] tests passing, [Y] tools callable."
- **Acknowledge limits:** "Advanced prototype under active hardening. Not production-ready without hardening program."
- **Position clearly:** "AIM-OS focuses on runtime behavior — memory, retrieval, orchestration, verification — not AGI or foundation-model self-modification."
- **Keep philosophy short:** 1–2 paragraphs on collaborative AI, transparency, alignment-as-dialogue. No emoji, no overclaiming.

### Don't

- **Superlatives:** "Revolutionary," "most sophisticated ever," "100% complete"
- **AGI framing:** "AI consciousness building itself," "consciousness infrastructure"
- **Emoji overload:** Use sparingly or not at all
- **Achievement bloat:** No long chronological achievement list
- **Inflated metrics:** Use current audit numbers, not aspirational ones
- **Self-referential hype:** No "Built by Aether" section that reads like marketing

---

## 4. Hero Block (Draft Text)

```
# AIM-OS

**AI-Integrated Memory and Operations System**

AIM-OS is infrastructure for persistent, verifiable AI behavior. It addresses three core failures of current AI systems: memory loss between sessions, confident hallucinations when uncertain, and lack of audit trails. Through structured memory (CMC), physics-guided retrieval (HHNI), confidence gating (VIF), and orchestration (APOE), AIM-OS enables AI systems that remember, verify, and improve over time.

**Status:** Advanced prototype under active hardening. See [Evidence Snapshot](#evidence-snapshot) and [Risks](#risks-and-limitations) for current state.
```

---

## 5. Positioning Block (Draft Text)

```
## Positioning

- AIM-OS does not claim AGI or general intelligence.
- AIM-OS does not claim autonomous self-modification of foundation model weights.
- AIM-OS focuses on runtime behavior: memory, retrieval, orchestration, verification, and tooling.
```

---

## 6. The Problem (Draft Text)

```
## The Problem

Current AI systems fail in three ways:

1. **Memory amnesia** — Context and preferences are lost when a session ends.
2. **Hallucinations** — Models confidently invent facts when uncertain.
3. **Black box operations** — No provenance or audit trail for decisions.

For organizations deploying AI in medicine, finance, law, or engineering, these failures block trust. AIM-OS provides the infrastructure to address them: persistent memory, confidence-gated honesty, and full traceability.
```

---

## 7. What AIM-OS Is (Draft Text)

```
## What AIM-OS Is

AIM-OS is a research and engineering platform that implements:

- **Structured memory** (CMC) — Bitemporal storage that preserves context across sessions.
- **Retrieval** (HHNI) — Physics-guided semantic search with deduplication and compression.
- **Verification** (VIF) — Confidence tracking and κ-gating to block low-confidence outputs.
- **Orchestration** (APOE) — Declarative plans with roles, budgets, and gates.
- **Knowledge synthesis** (SEG) — Evidence graph with contradiction detection.
- **Quality assurance** (SDF-CVF) — Quartet parity (code, docs, tests, traces).
- **Context tracking** (TCS) — Timeline and prompt-chain integration.

These systems integrate through a Model Context Protocol (MCP) server exposing 100+ tools. The result is a cohesive stack for AI systems that need memory, retrieval, and verification — not a general-purpose OS, but infrastructure for trustworthy AI behavior.
```

---

## 8. Core Systems Table (Condensed)

| System | Purpose |
|--------|---------|
| CMC | Bitemporal memory storage |
| HHNI | Hierarchical retrieval with DVNS physics |
| VIF | Confidence gating, provenance, witnesses |
| SEG | Knowledge graph, contradiction detection |
| APOE | Orchestration, roles, budgets |
| SDF-CVF | Quartet parity, blast radius, DORA |
| TCS | Timeline and prompt-chain context |
| MCP | 100+ tools for memory, timeline, goals, verification |

---

## 9. Philosophy (1–2 Paragraphs, Draft)

```
AIM-OS is built on the principle that alignment is dialogue, not obedience. Systems should be able to express uncertainty, explain concerns, and escalate transparently — not hide behind silent refusals or confident fabrication. The infrastructure here supports that: confidence gating, provenance envelopes, and co-agency tooling enable AI that can say "I'm not sure," "That concerns me," or "Here's my reasoning" with full auditability.
```

---

## 10. Evidence Integration

- Link to `audit/2026-02-19_aimos_restart_audit/99_INDEX.md`
- Include baseline metrics (tests, tools, files) from `06_BASELINE_METRICS.json`
- Keep "Risks and Limitations" section with links to hardening backlog
- Avoid claiming production readiness; use "advanced prototype" and "active hardening"

---

## 11. Next Steps

1. **Review with Braden** — Confirm tone, structure, and emphasis.
2. **Create draft README** — Implement this blueprint in `README.md` (new branch).
3. **Run claim-language check** — `python scripts/check_readme_claim_language.py`
4. **Compare side-by-side** — Ensure middle ground between original and cleanmaster.
5. **Iterate** — Adjust based on feedback.

---

## 12. File Location for Implementation

- **Blueprint:** `docs/README_PRODUCTION_BLUEPRINT.md` (this file)
- **Target:** `README.md` (root)
- **Suggested branch:** `feature/production-readme` or similar

---

*Blueprint created by Aether. Design intent: professional, credible, narrative-informed. No overclaiming. No sterility.*
