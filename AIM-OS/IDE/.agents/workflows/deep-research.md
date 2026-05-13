---
description: Protocol for conducting deep research and producing canonical documentation to AIM-OS standards
---

# Deep Research Protocol

This workflow produces exhaustive, architecturally sound research documents that become canonical build blueprints. It is derived from Braden's methodology of heavy discussion → master index → section expansion → adversarial stress-testing → hardened canon.

> [!IMPORTANT]
> Deep research documents are NOT brainstorming. They are engineering blueprints. Every claim must be defensible, every architecture must be implementable, every section must add value.

---

## Phase 1: Thesis & Alignment (15-30 min)

### Purpose
Establish the core problem, propose an architecture, and align on scope.

### Steps
1. **State the problem** — What system gap or capability we're addressing
2. **Propose an architecture** — High-level solution thesis (1-2 paragraphs)
3. **Define scope boundaries** — What is IN scope, what is explicitly OUT
4. **Identify prior art** — Search knowledge items, existing docs, and conversation history
5. **Declare design principles** — 3-5 non-negotiable constraints

### Quality Gate
- [ ] Problem statement is specific (not vague)
- [ ] Architecture is plausible (not magical)
- [ ] Scope has explicit exclusions
- [ ] Prior art has been checked (KIs, `docs/`, knowledge_architecture)

### Exit Criteria
A 1-page thesis document with problem, proposed solution, scope, and principles.

---

## Phase 2: Master Index (10-20 min)

### Purpose
Create the skeleton of the complete document — 20-40 numbered sections.

### Steps
1. **Top-level structure** — Major sections (5-8 top-level chapters)
2. **Sub-sections** — Break each chapter into 3-6 sub-topics
3. **Dependency ordering** — Arrange so each section builds on previous ones
4. **Estimated depth** — Mark each section as `shallow` (200w), `medium` (500w), or `deep` (1000w+)
5. **Cross-reference hooks** — Note where sections reference each other

### Quality Gate
- [ ] Index has 20+ sections minimum
- [ ] No orphan sections (each connects to at least one other)
- [ ] Section names are specific, not generic ("Token Budget Packing Algorithm" not "Optimization")
- [ ] Depth estimates total to at least 10,000 words

### Template
```markdown
# [Document Title] — Master Index

## 1. [Chapter]
### 1.1 [Subsection] (medium)
### 1.2 [Subsection] (deep)
### 1.3 [Subsection] (shallow)

## 2. [Chapter]
...
```

---

## Phase 3: Section Expansion (30-90 min)

### Purpose
Expand each section to full technical detail.

### Steps
1. **Work sequentially** — Expand sections in dependency order
2. **Include concrete examples** — Code snippets, data structures, formulas
3. **Define interfaces** — If a section describes a component, define its API
4. **Show data flow** — Inputs → processing → outputs for each system
5. **Add diagrams** — Mermaid or ASCII where architecture is complex

### Quality Gate (per section)
- [ ] Contains at least one concrete example (code, data structure, or formula)
- [ ] Defines at least one interface or data contract
- [ ] Uses specific language, not hand-waving
- [ ] References at least one related section

### Depth Targets
| Depth | Min Words | Examples | Interfaces |
|-------|----------|----------|------------|
| Shallow | 200 | 1 | 0 |
| Medium | 500 | 2 | 1 |
| Deep | 1000+ | 3+ | 2+ |

---

## Phase 4: Adversarial Stress Test (20-40 min)

### Purpose
Challenge every claim, demand evidence, catch overclaiming.

> [!CAUTION]
> This is the most critical phase. Documents that skip adversarial review become "glorious manifestos" instead of credible engineering specs.

### Steps
1. **Claim audit** — List every assertion that uses words like "always," "never," "optimal," "mathematically," "guarantees"
2. **Evidence check** — For each claim, note: measured, theorized, or assumed?
3. **Edge case hunt** — What breaks if inputs are weird, scale is extreme, or dependencies change?
4. **Alternative review** — For each architectural decision, name at least one credible alternative
5. **Overclaiming demotion** — Downgrade unsupported "laws" to "engineering hypotheses"

### Severity Levels
| Level | Meaning | Action |
|-------|---------|--------|
| 🔴 Critical | Claim is false or misleading | Must rewrite |
| 🟡 Overclaim | True-ish but overstated | Soften language |
| 🟢 Solid | Supported by evidence or clear logic | Keep |
| 🔵 Hypothesis | Reasonable but unproven | Label as hypothesis |

### Quality Gate
- [ ] Every strong claim has been classified (🔴/🟡/🟢/🔵)
- [ ] At least 3 alternatives have been considered
- [ ] Edge cases documented for each major system
- [ ] No unchallenged "mathematically optimal" statements remain

---

## Phase 5: Correction & Hardening (15-30 min)

### Purpose
Integrate critique, fix issues, harden language.

### Steps
1. **Fix all 🔴 Critical** — Rewrite false claims or remove
2. **Soften all 🟡 Overclaims** — Replace "always" with "typically," "optimal" with "effective," "guarantees" with "aims to"
3. **Label all 🔵 Hypotheses** — Mark with explicit `[HYPOTHESIS]` tag
4. **Integrate alternatives** — Add "Alternative approaches" subsections where relevant
5. **Add failure modes** — What happens when each system fails?
6. **Add versioning** — What is v1.0 scope vs future phases?

### Quality Gate
- [ ] Zero 🔴 items remaining
- [ ] All 🟡 items addressed
- [ ] Failure modes documented for every system
- [ ] Clear v1.0 scope boundary

---

## Phase 6: Canon Compilation (15-30 min)

### Purpose
Convert raw research into structured AIM-OS knowledge architecture format.

### Steps
1. **Add YAML frontmatter** — id, system, level, type, title, description
2. **Extract key interfaces** — Create separate files for major data contracts
3. **Build dependency graph** — Which existing systems does this connect to?
4. **Assign T-level** — T0 (executive), T1 (overview), T2 (architecture), T3 (detailed), T4 (complete)
5. **Register in SUPER_INDEX** — Update the global knowledge index

### T-Level Guide
| Level | Audience | Length | Detail |
|-------|----------|--------|--------|
| T0 | Executives, new agents | 200-400w | What it does, why it matters |
| T1 | Developers | 500-1000w | Architecture overview, key components |
| T2 | Implementers | 1000-3000w | Interfaces, data flow, decisions |
| T3 | Deep specialists | 3000-8000w | Full implementation detail |
| T4 | Complete reference | 8000w+ | Everything including edge cases |

---

## Phase 7: Cross-Reference & Status (10-20 min)

### Purpose
Map every concept against existing AIM-OS code.

### Steps
1. **Search codebase** — `grep_search` for key terms from each section
2. **Build status table** — For each concept: ✅ Built | ⚡ Partial | ❌ Not built
3. **Identify gaps** — What needs building?
4. **Estimate effort** — T-shirt size each gap (S/M/L/XL)
5. **Update task.md** — Add implementation items for the gaps

### Status Table Template
```markdown
| Concept | AIM-OS Implementation | Status | Gap Size |
|---------|----------------------|--------|----------|
| [concept] | [file/class/function] | ✅/⚡/❌ | S/M/L/XL |
```

---

## Agent Team

This workflow is designed for collaborative execution:

| Agent | Role | Phases |
|-------|------|--------|
| **AGENT-RESEARCH-STRATEGIST** | Plans index, sequences expansion, decides scope | 1, 2, 3 |
| **AGENT-KNOWLEDGE-AUDITOR** | Stress-tests claims, hunts edge cases | 4, 5 |
| **AGENT-CANON-COMPILER** | Converts to T-levels, cross-references code | 6, 7 |

Any single agent CAN execute the full workflow solo, but the team split produces better adversarial review (the auditor hasn't seen the original expansion, so they stress-test with fresh eyes).

---

## Anti-Patterns

- ❌ **Skipping Phase 4** — produces impressive-sounding docs that fall apart under scrutiny
- ❌ **Generic section names** — "Architecture" means nothing, "Brace-Depth Pruning Algorithm" means everything
- ❌ **No code examples** — if you can't show a data structure, you don't understand the system yet
- ❌ **Refusing to say "I don't know"** — label hypotheses honestly
- ❌ **Infinite expansion** — respect the depth targets, stop when the section is complete
