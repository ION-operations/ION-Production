---
ion_id: docs/aether-os/continuity-spec
type: spec
authority: A3_OPERATIONAL
confidence: 0.80
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T18:00:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/aether-integration-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: docs/aether-os/aether-interface
    type: implements
tags: [continuity, capsules, timeline, truncation, track-e, tcs]
---

# Continuity Specification — Session Survival and Temporal Awareness

> **Purpose:** Define how ION maintains continuity across context truncations, session boundaries, and agent handoffs. This is the system's answer to the fundamental problem: AI agents forget everything between sessions.
>
> **Constitutional Mandate:** AETHER_CONSTITUTION Article 22 — "An agent must survive any single context loss without amnesia."
> **A2 Schema:** capsule/v1 (Schema 1), checkpoint/v1 (Schema 2), relay_state/v1 (Schema 21)
> **Integration Systems:** TCS (44,492 lines), existing capsule.py (stub), truncation survival tests

---

## §1. The Continuity Problem

AI agents in the current ecosystem suffer from **catastrophic context loss:**

1. **Context truncation** — mid-conversation, the context window fills up and earlier content is lost
2. **Session boundary** — between conversations, the agent starts fresh with no memory of previous work
3. **Agent handoff** — when work transfers from one agent (e.g., Opus) to another (e.g., Relay), context is lost in translation
4. **Platform switch** — when the same agent runs across different IDEs (Antigravity → Cursor), accumulated context doesn't transfer

### Sev's Assessment (from SEV_NOTES_TO_OPUS.md)
> *"The system still cannot carry enough of itself across sessions to resume work without significant human re-briefing."*

### Current State of Continuity Systems

| System | Lines | What It Does | ION Status |
|--------|------:|-------------|------------|
| TCS | 44,492 | Full context management system | NOT integrated with ION |
| capsule.py | ~130 | ION capsule ion writer (stub) | EXISTS but minimal |
| Context Bootloader | 1,615 | Session start context loading | NOT integrated |
| MCP memory | ~200+ | Key-value memory persistence | NOT integrated |
| MCP capsules | ~100+ | MCP-based capsule recording | NOT integrated |
| truncation.py | ~130 | ION truncation handler (stub) | EXISTS but minimal |

---

## §2. The ION Continuity Architecture

### 2.1 The Three Continuity Mechanisms

**Mechanism 1: Capsules** — Snapshot ions written at session boundaries
```
Session Start:  Write PRE capsule  → "Here's what I know coming in"
Session End:    Write POST capsule → "Here's what I learned, what's pending"
```

**Mechanism 2: Timeline** — Chronological record of all significant events
```
Everything significant → timeline ion → queryable later
```

**Mechanism 3: Memory Ions** — Persistent facts, decisions, corrections
```
Discovered fact → memory/finding-*.md
Made decision → memory/decision-*.md
Learned correction → memory/correction-*.md
```

### 2.2 Capsule Ion Format (A2 Schema 1)

```yaml
---
ion_id: capsules/2026-03-23-session-001-pre
type: memory
authority: A4_RUNTIME
confidence: 0.95
owner: opus
schema: capsule/v1
capsule_type: PRE   # or POST

# Session metadata
session_id: "2026-03-23-001"
agent: opus
timestamp: "2026-03-23T16:00:00-04:00"

# What the agent knows coming in
active_branches:
  - branches/active/system-mapping
  - branches/active/ionv2-audit

evidence_state:
  total_evidence_ions: 42
  highest_confidence: 0.95
  lowest_confidence: 0.1
  stale_count: 3

# What needs to happen
pending_tasks:
  - "Complete system universe map"
  - "Write companion documents"
  - "Present to Braden"

# What went wrong last time (for correction)
corrections_from_last_session:
  - "IONv2 was rushed — need full doc review first"
  - "Don't skip §7.2 REFLECT"

# Context window budget
tcs_compressed_context: |
  [TCS-compressed summary of relevant context,
   sized to fit model's context window]
---

# PRE Capsule — Session 2026-03-23-001

## Active Work
Working on comprehensive Aether/ION system mapping after IONv2 declared failure.
Full documentation audit completed (29 documents, ~17,400 lines).

## Key Context
- IONv2 is a total failure (wrong paradigm, rush job)
- operation-victus has 547-test ION engine
- Constitutional stack: A0/A1/A2/A4 (~3,500 lines)
- Orchestration plans V1-V5 define ~137 sessions of work
```

### 2.3 Timeline Ion Format

```yaml
---
ion_id: timeline/2026-03-23-17-30-001
type: memory
authority: A4_RUNTIME
confidence: 1.0
owner: opus
event_type: document_created
timestamp: "2026-03-23T17:30:00-04:00"
subject: "docs/aether-os/mcp-bridge-spec"
summary: "Wrote MCP-ION bridge specification"
ions_affected:
  - docs/aether-os/system-universe-map
duration_ms: 45000
---
```

### 2.4 Truncation Survival Protocol

When context truncation is detected mid-session:

```
1. DETECT: Agent realizes it's lost context (checkpoint message appears)
2. RECOVER:
   a. Read own manifest: .ion/agents/opus/manifest.md
   b. Read latest capsule: .ion/capsules/ → most recent PRE
   c. Read active branches: follow manifest.active_branches links
   d. Read recent timeline: last N timeline ions
3. RESUME:
   a. Update cognitive position to "contextualize"
   b. Re-enter §7 cognitive loop from step 1
   c. DO NOT attempt to continue mid-thought
```

**TCS Integration:** TCS's adaptive context dumping sizes the capsule content to fit the model's remaining context window after truncation. Large context → full summary. Small context → compressed essentials only.

---

## §3. Session Lifecycle

### 3.1 Full Session Protocol

```
SESSION START
├── 1. Load genome/manifest ion
├── 2. Read latest PRE capsule (or POST from last session)
├── 3. TCS.load_context(agent, session)
├── 4. Merge context into manifest
├── 5. Write PRE capsule ion
├── 6. Post status: agents/opus/status.md → ONLINE
└── 7. Enter §7 cognitive loop

DURING SESSION
├── Every significant event → timeline ion
├── Every finding → evidence ion
├── Every decision → memory/decision ion
├── Every correction → memory/correction ion
└── If truncation detected → Truncation Survival Protocol

SESSION END
├── 1. Write POST capsule ion (what was accomplished, what's pending)
├── 2. TCS.dump_context(session_state, adaptive=True)
├── 3. Update manifest: position, active_branches
├── 4. Post status: agents/opus/status.md → OFFLINE
└── 5. Update .agent/comms/status/antigravity.status.md
```

### 3.2 Agent Handoff Protocol

When work transfers from one agent to another:

```
HANDOFF: Opus → Relay
├── 1. Opus writes handoff ion:
│   ion_id: comms/handoff-2026-03-23-001
│   from: opus
│   to: relay
│   context: [compressed context]
│   active_branches: [branch list]
│   critical_constraints: [constraint list]
│   
├── 2. Opus writes POST capsule
│   → includes handoff reference
│   
├── 3. Relay reads:
│   a. Handoff ion
│   b. Opus's POST capsule
│   c. Relevant branch ions
│   d. Own manifest (for capability check)
│   
├── 4. Relay writes PRE capsule
│   → references handoff origin
│   
└── 5. Relay enters §7 cognitive loop
```

A2 Schema 10 (`handoff_envelope/v1`) governs this exchange.

---

## §4. TCS Integration Details

### 4.1 What TCS Provides

TCS (44,492 lines) has mature solutions for problems ION defines but doesn't solve:

| TCS Capability | ION Need | Integration |
|---------------|----------|-------------|
| Adaptive context dumping | Capsule sizing | TCS sizes capsule content to model context window |
| Context Level enum | ION confidence tiers | TCS CRITICAL/HIGH/MEDIUM/LOW maps to ion confidence |
| Session continuity tracking | Capsule chain | TCS maintains session→capsule→session chain |
| Timeline persistence | Timeline ions | TCS timeline entries become timeline ions |

### 4.2 TCS Adapter

```python
class TCSAdapter:
    """Bridge between TCS and ION capsule system."""
    
    def load_session_context(self, agent: str) -> dict:
        """Load context for session start."""
        # Get latest capsule from TCS
        tcs_context = tcs.get_latest_context(agent)
        # Get latest capsule ion from ION
        capsule_ions = ion_store.list_by_type("memory", 
            filter={"schema": "capsule/v1", "owner": agent})
        # Merge: TCS context enriches ION capsule
        return merge_context(tcs_context, capsule_ions)
    
    def dump_session_context(self, session_state: dict, budget: int):
        """Dump context for session end."""
        # Adaptive sizing: fit within budget
        compressed = tcs.adaptive_dump(session_state, max_tokens=budget)
        # Write as POST capsule ion
        capsule = create_capsule_ion(
            session_id=session_state["session_id"],
            capsule_type="POST",
            compressed_context=compressed,
        )
        governed_write.create(capsule, agent=session_state["agent"])
```

---

## §5. Continuity Strata (from Atlas A4, Book VIII)

The Atlas defines 5 continuity strata — layers of information that must survive context loss:

| Stratum | Name | Must Survive | ION Storage |
|---------|------|-------------|-------------|
| C0 | Identity | Who am I, what can I do | agents/{callsign}/manifest.md |
| C1 | Mission | What am I supposed to accomplish | branches/active/ (active branches) |
| C2 | State | What have I done so far | capsules/ (latest), timeline/ |
| C3 | Evidence | What do I know for sure | evidence/ (high-confidence ions) |
| C4 | History | What happened in the past | timeline/ + CMC temporal queries |

**Survival Priority:** C0 > C1 > C2 > C3 > C4. When context budget is tight, sacrifice C4 first, C0 never.

---

## §6. Implementation Priority

| Component | Lines (est) | Priority | Depends On |
|-----------|-------------|----------|------------|
| Capsule writer (PRE/POST) | ~250 | CRITICAL | ION store (done) |
| TCS adapter | ~300 | CRITICAL | TCS package |
| Truncation detector + recovery | ~200 | CRITICAL | Capsule writer |
| Timeline ion writer | ~150 | HIGH | ION store (done) |
| Handoff envelope writer | ~200 | HIGH | Capsule writer |
| Context merger | ~200 | MEDIUM | TCS adapter |
| Session lifecycle manager | ~300 | MEDIUM | All above |
| **Total** | **~1,600** | | |

---

## §7. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Problem statement defined | ✅ | §1 — 4 types of context loss |
| Three continuity mechanisms documented | ✅ | §2.1 — capsules, timeline, memory |
| Capsule format specified | ✅ | §2.2 — full YAML with A2 Schema 1 |
| Truncation protocol defined | ✅ | §2.4 — detect/recover/resume |
| Session lifecycle documented | ✅ | §3.1 — start/during/end |
| Handoff protocol defined | ✅ | §3.2 — agent-to-agent |
| TCS integration designed | ✅ | §4 — adapter with code example |
| Continuity strata referenced | ✅ | §5 — C0 through C4 from Atlas |
| Implementation estimate | ✅ | §6 — ~1,600 lines |

---

*This specification addresses the most fundamental problem in AI agent operation: memory loss. Without continuity, every session starts from zero. With it, the system accumulates knowledge and never forgets what matters.*

*Governed by: AETHER_CONSTITUTION.md Article 22*
*— Opus, 2026-03-23*
