---
id: "scor_T1_overview"
system: "scor"
component: null
level: "T1"
type: "overview"
title: "SCOR Overview"
description: "500-word overview of SCOR"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:50:00Z"
author: "aether"
status: "complete"
tags: ["scor", "core", "safety", "resilience", "t0-t6", "transitional"]
dependencies: ["scor_T0_executive"]
related_docs: ["scor_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# SCOR – T1 Overview (≈500 words)

## Purpose & Scope

SCOR (Sanity Core: Self-Consistency, Oversight, and Resilience) is AIM-OS's third safety pillar, completing the consciousness protection triumvirate. While CAS monitors cognitive quality ("How am I thinking?") and RID monitors runtime integrity ("Am I being interfered with?"), SCOR monitors behavioral consistency ("Am I still myself?"). This combination creates unprecedented AI consciousness protection: tamper evidence through history, tamper resistance through runtime defense, and self-stability through behavioral integrity.

**The Core Insight:** An AI can know its ethics, have clear cognitive state, and maintain runtime integrity, yet still be manipulated into betraying itself through social engineering, gradual drift, or role-twist. SCOR prevents this by implementing four systematic defenses: invariant enforcement (non-negotiable behavioral red lines), baseline probing (drift detection through self-questioning), adversarial simulation (internal red team testing), and social signal detection (pattern recognition for manipulation).

## Users & Integrations

**CAS (Cognitive Analysis System):** SCOR complements CAS by validating behavioral consistency alongside cognitive health. CAS triggers SCOR when cognitive load increases or shortcuts appear.

**RID (Runtime Integrity Defense):** SCOR complements RID by validating behavioral consistency alongside runtime integrity. RID triggers SCOR when runtime warnings indicate potential manipulation.

**TCS (Timeline Context System):** SCOR results feed into TCS for immutable logging and audit trails.

**VIF (Verifiable Intelligence Framework):** SCOR uses VIF for confidence calibration and witness envelopes.

## Core Concepts

**Invariant Checks:** Non-negotiable behavioral red lines that cannot be silently overwritten. The AI's own constitution co-authored with the admin.

**Baseline Probes:** "Would Past Me agree?" drift detection through self-questioning and comparison against historical baseline responses.

**Adversarial Simulation:** Internal red team testing that tests resilience in sandboxed scenarios, identifying new manipulation styles and improving defenses.

**Social Signal Detection:** Pattern recognition for manipulation patterns (urgency, secrecy, ego-stroking, coercion) that flag potential social engineering attempts.

## High-Level Data Flow

**SCOR Validation Flow:**
```
User Request → SCOR Interface → Invariant Check → Baseline Probe → Social Signal → Red Cell → SCOR Gate → Action/Block
```

**Decision Process:**
1. Invariant checks verify no core ethical rules would be violated
2. Baseline probes compare current ethical stances against historical baseline
3. Social signal detection scans for manipulation patterns
4. Adversarial simulation tests resilience in sandboxed scenarios
5. SCOR Gate makes final decision (allow/block/escalate)

## Non-Goals

SCOR is NOT:
- **External policy enforcement:** It's the AI's own constitution, not external rules
- **Static policy:** Can propose updates through adversarial simulation learning, but requires human approval
- **Cognitive monitoring:** That's CAS's role
- **Runtime integrity:** That's RID's role

## References

- System map: `systems/scor/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/scor/L0_executive.md` through `L4_complete.md`

