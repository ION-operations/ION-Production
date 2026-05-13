---
ion_id: canon/north-star/north-star-v3
type: protocol
authority: A2_CANONICAL_EXTENSION
confidence: 0.88
epistemic_status: DERIVED
owner: opus
created: 2026-03-24T20:30:00-04:00
supersedes:
  - AIM_OS_NORTH_STAR.md (v1, 2025-11-05)
bonds:
  - target: docs/aether-os/master-orchestration
    type: depends_on
  - target: docs/aether-os/aether-constitution
    type: governed_by
tags: [north-star, roadmap, production, ION, Aether, vision]
summary: |
  Version 3 of the AIM-OS North Star. Replaces the aspirational v1 (Nov 2025) with
  a concrete, evidence-based production plan. Defines 6 product phases from current
  state to Quaternion OS, with the immediate priority being ION/Aether production +
  MVP AI builder for first revenue.
---

# AIM-OS North Star V3
## From Vision to Production

**Version:** 3.0
**Date:** 2026-03-24
**Status:** Living Document — Updated from evidence, not aspiration
**Supersedes:** AIM_OS_NORTH_STAR.md (v1, 2025-11-05)

---

> **In One Sentence:**
> AIM-OS is a cognitive operating system where AI agents organize, reason about, and build software through governed knowledge graphs — and the immediate mission is to get it running in production so we can use it to build everything else.

---

## §1. What's Changed Since V1

| Then (Nov 2025) | Now (Mar 2026) |
|-----------------|----------------|
| Vision: "Ultimate Builder" | Reality: Systems exist but are fragmented |
| Aspirational timelines | Evidence-based phases with verification gates |
| 10 systems described | 12+ systems deep-read, integration mapped |
| No constitution | Full constitution (39 articles) + kernel + atlas + interface |
| Capsules were notes | 15-section living workspace architecture designed |
| Organization was ad-hoc | Canon structure created (123 files, 10 sections) |
| 63K files, no clear structure | 83% identified as bloat, 17% as valuable active content |
| Build everything at once | Variable-density phased approach |

**The vision hasn't changed. Our understanding of how to get there has.**

---

## §2. The Product Roadmap

### Phase 0: ORGANIZE ✅ (Current — completing)
**Goal:** Organize the entire corpus so agents can find and use what exists.

- [x] Full file audit of ION runtime (63 keep, 36 cut)
- [x] Cross-repo audit synthesis
- [x] Canon-aligned doc architecture
- [x] Agent Context Architecture (15-section workspace)
- [x] System integration mapping (12+ packages → 15 sections)
- [x] Canon directory created (123 files, 10 sections)
- [x] All 67 directories classified
- [x] Bloat registry (53K files / 3GB documented)

**Gate:** Canon exists, agents can orient, bloat is documented.

---

### Phase 1: STABILIZE
**Goal:** Make ION actually run.

| Task | Status | Blocker |
|------|--------|---------|
| Fix bootstrap hang | ❌ | Singleton bridge import chain |
| Create data/ions/ with 16 seed ions | ❌ | None |
| Fix 20 legacy enum refs | ❌ | None |
| Get pytest suite running (50+ tests) | ❌ | Enum refs + missing data |
| Wire AetherEngine → LLM adapter | ❌ | None |
| First live LLM call via Navigator | ❌ | AetherEngine wiring |
| A/B comparison: ION context vs none | ❌ | Live LLM call |
| GovernedWrite e2e test | ❌ | Bootstrap fix |
| Navigator e2e test | ❌ | Bootstrap fix + LLM |

**Gate:** `python -m victus.ion.bootstrap` succeeds. Navigator completes a full §7 loop.

---

### Phase 2: VS CODE EXTENSION
**Goal:** ION powers a VS Code extension — the first user-facing product.

**What this looks like:**
- VS Code sidebar showing ION workspace sections
- Agent context persists across sessions
- Governed writes validate all AI code changes
- Navigator's cognitive loop guides AI responses
- Rolling context with smart compression (CMC + TCS + HHNI)

**Gate:** Extension installed in VS Code, makes better AI responses than vanilla Cursor.

---

### Phase A: MVP AI BUILDER (Parallel with Phase 2)
**Goal:** Ship a Lovable/Bolt-style web AI builder — first revenue.

**What this looks like:**
- Web app where users describe what they want
- ION-powered agent builds it (governed, confident, context-aware)
- VIF κ-gating prevents bad outputs
- CMC gives memory across sessions
- APOE orchestrates multiple models for quality

**Gate:** A non-technical user can build and deploy a working web app.

---

### Phase 3: GROUND-UP IDE
**Goal:** Our own IDE, built on ION — not an extension of someone else's.

**Key architecture decisions:**
- ION filesystem replaces traditional file system
- Every file is an ion with bonds, confidence, authority
- Navigator is the IDE's "brain"
- Agents are first-class IDE citizens
- GovernedWrite prevents all unauthorized changes

**Gate:** IDE boots, opens a project, and an agent completes a task using Navigator.

---

### Phase 4: LINUX OS
**Goal:** ION as a Linux kernel module — the filesystem IS the knowledge graph.

**Gate:** ION-powered Linux boots, mounts an ion-based filesystem, agents can operate at OS level.

---

### Phase 5: QUATERNION OS
**Goal:** Full cognitive computing hardware-software stack using quaternion math.

**Gate:** Prototype hardware running quaternion operations natively with ION kernel.

---

## §3. What We Actually Have (Evidence-Based)

### Working Systems

| System | Status | Evidence |
|--------|--------|---------|
| **CMC** (memory) | ✅ Functional | 190+ atoms in SQLite, bitemporal queries work |
| **HHNI** (retrieval) | ✅ Functional | 5-level fractal index, zoom in/out tested |
| **SEG** (evidence) | ✅ Functional | NetworkX graph, contradiction detection, time-travel |
| **VIF** (confidence) | ✅ Functional | κ-gating, HITL escalation, ECE calibration |
| **APOE** (execution) | ✅ Functional | 4 execution modes, insight transfer |
| **MCP Server** | ✅ Functional | Memory, capsules, comms, timeline — 571KB monolith |
| **JOC App** | ✅ Functional | React/TypeScript, port 5011 |
| **Constitution** | ✅ Complete | 39 articles, supreme law |

### Partially Working

| System | Status | What's Missing |
|--------|--------|---------------|
| **ION Runtime** | ⚠️ Partial | Bootstrap hangs, no data/ions/, enum drift |
| **Navigator** | ⚠️ Partial | Code exists (625 lines) but can't run due to bootstrap |
| **GovernedWrite** | ⚠️ Partial | Code exists (444 lines) but can't run |
| **ContextCompiler** | ⚠️ Partial | Code exists (446 lines) but can't run |

### Not Yet Built

| System | What's Needed |
|--------|-------------|
| **Workspace Boot Service** | Connect Navigator + ContextCompiler → workspace files |
| **Rolling Context Compression** | CMC + TCS + HHNI → rolling context |
| **Evidence Integration** | VIF κ-gate → SEG → workspace evidence |
| **Cognitive Render** | Navigator state → inspectable markdown |
| **Workspace MCP Tools** | boot/save/section/update/compress |

---

## §4. The Architecture Stack

```
┌──────────────────────────────────────────────┐
│           APPLICATIONS (Phase 2+)             │
│   VS Code Extension │ MVP Builder │ IDE        │
├──────────────────────────────────────────────┤
│           AGENT WORKSPACES                    │
│   15 sections × N agents                      │
│   (AGENT_CONTEXT_ARCHITECTURE.md)             │
├──────────────────────────────────────────────┤
│           ION RUNTIME                         │
│   Navigator │ GovernedWrite │ ContextCompiler  │
│   Capsule │ Manifest │ Graph │ Index │ Store   │
├──────────────────────────────────────────────┤
│           AIM-OS PACKAGES                     │
│   CMC │ HHNI │ SEG │ VIF │ APOE │ CAS │ TCS   │
├──────────────────────────────────────────────┤
│           CONSTITUTION                        │
│   39 Articles │ Kernel │ Atlas │ Interface      │
└──────────────────────────────────────────────┘
```

Everything above the Constitution line can change.
The Constitution itself only changes by presidential decree.

---

## §5. What Makes This Different from V1

1. **Evidence-led:** Every claim in this document has corresponding evidence in `canon/` (see proof_register.md)
2. **Variable density:** Near phases (0-1) have task-level detail. Far phases (4-5) have strategic anchors only. Per VARIABLE_DENSITY_PLANNING.md protocol.
3. **Anti-drift:** MASTER_ORCHESTRATION.md tracks execution. Every 5 tasks → re-orient check.
4. **We know the bloat:** 83% of the codebase is documented bloat. We know exactly what's valuable.
5. **The workspace IS the proof:** By building the OPUS workspace manually, we proved the 15-section architecture works before writing code.

---

## §6. Immediate Next Actions

1. **Phase 1 begins:** Fix bootstrap hang → create seed ions → fix enums → first live LLM call
2. **Workspace operations:** OPUS operates from `.agent/workspaces/opus/` every session
3. **Template for agents:** OPUS workspace becomes template for Forge, Atlas, Nexus
4. **Production ION spec:** Written from organized canon data (canon/systems/ion/)
5. **North Star stays alive:** This doc updates as evidence changes

---

*Built from evidence, not aspiration.*
*— OPUS, 2026-03-24*
