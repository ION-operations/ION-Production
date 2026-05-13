# CAS — Consciousness Analysis System

> **Source:** `packages/cas/` (33 Python files)
> **Status:** Functional
> **Purpose:** Agent self-awareness and introspection

## What CAS Does
Provides agents with self-awareness capabilities — the ability to know what they can do, what they can't do, how confident they are, and how their performance changes over time. Includes consciousness journaling and context capacity monitoring.

## Key Components
- **consciousness_journaling_system.py** — Structured journaling for agent self-reflection
- **context_capacity_monitor.py** — Monitors context window usage and efficiency
- **adaptive_context_dumping.py** — Adaptive context management when nearing limits
- **cost_optimized_journaling.py** — Resource-efficient journaling strategies

## Integration with Agent Context
→ Self (§9) — CAS feeds the agent's self-model
→ Cognitive (§13) — CAS provides meta-cognitive observations

## Relationship to Other Systems
- Uses **VIF** for confidence tracking
- Feeds into **ION Navigator** reflection step (§7.2)

---

# TCS — Timeline Context System

> **Source:** `packages/timeline_context_system/` (97 Python files)
> **Status:** Functional
> **Purpose:** Rolling context with timeline tracking and smart compression

## What TCS Does
Manages the temporal dimension of context — tracking when things happened, how context evolves over time, and applying intelligent compression so older context doesn't overwhelm the window.

## Key Components
- **demo_context_dump.py** — Context dumping for debugging
- **Context bootloaders** — Priority-weighted context loading
- **Timeline tracking** — Temporal ordering of all events
- **Smart compression** — Progressive summarization (full → summarized → 1-line → topic → indexed)

## Integration with Agent Context
→ Rolling Context (§3) — TCS powers the 7-level compression gradient
→ History (§10) — TCS provides temporal ordering

## Relationship to Other Systems
- Uses **CMC** for persistent storage of timeline entries
- Uses **HHNI** for multi-resolution retrieval of compressed context

---

# SDF-CVF — Cross-Validation Framework

> **Source:** `packages/sdfcvf/` (32 Python files)
> **Config:** `.sdfcvf.config.yaml` (11KB)
> **Status:** Functional
> **Purpose:** Multi-model output comparison and validation

## What SDF-CVF Does
Compares outputs from multiple AI models to validate correctness. When one model produces an answer, SDF-CVF can cross-check it against other models' outputs to detect errors, hallucinations, or disagreements.

## Integration with Agent Context
→ Evidence (§12) — Cross-validation results feed evidence confidence
→ Output (§15) — Validation of work products before delivery

## Relationship to Other Systems
- Uses **HHNI** for retrieval (`hhni/sdfcvf_integration.py`)
- Feeds into **VIF** for confidence calibration
- Used by **APOE** for multi-model consensus mode
