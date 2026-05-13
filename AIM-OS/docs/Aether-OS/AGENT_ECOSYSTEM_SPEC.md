---
ion_id: docs/aether-os/agent-ecosystem-spec
type: spec
authority: A3_OPERATIONAL
confidence: 0.80
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T17:45:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
tags: [agents, genomes, multi-agent, track-f, ecosystem]
---

# Agent Ecosystem ↔ ION Integration Specification

> **Purpose:** Define how the AIM-OS agent ecosystem (21 genomes, specialist system, agent mesh, roundtable, comms doctrine) integrates with ION's multi-agent architecture (Track F). Agents should BE ions — their identity, capabilities, and state stored as markdown ions in the filesystem.
>
> **Epistemic Status:** DERIVED from `.agent/genomes/`, COMMS_DOCTRINE.md, ION Master Plan §5 (Multi-Agent).

---

## §1. Current Agent Ecosystem

### 1.1 Agent Genomes (21 files in `.agent/genomes/`)

Each agent in AIM-OS has a **genome file** — a markdown document defining identity, role, capabilities, and constraints. These genomes are currently standalone files, NOT ions.

**Known Agents (from AGENTS.md and genome files):**

| Callsign | Role | Genome File | Primary IDE/Platform |
|----------|------|-------------|---------------------|
| **Opus** | COO — Implementation lead | `antigravity.genome.md` | Antigravity (Claude Opus 4.6) |
| **Sev** | CEO — Doctrine, orchestration | (GPT-5.4 genome) | ChatGPT Pro |
| **Relay** | Bridge agent — cross-IDE routing | `relay.genome.md` | Cross-platform |
| **Forge** | Builder/experimenter | `forge.genome.md` | Multiple |
| **Ledger** | Auditor — verification | `ledger.genome.md` | Multiple |
| **Palisade** | Security — monitoring | `palisade.genome.md` | Multiple |
| **Codex** | Code specialist | `codex.genome.md` | Codex/CLI |
| **Composer** | Content/documentation | `composer.genome.md` | Multiple |
| + ~13 others | Various specialist roles | Various genome files | Various |

### 1.2 Comms Doctrine (`.agent/COMMS_DOCTRINE.md`, 6,184 bytes)

Defines inter-agent communication protocols:
- **Message Types:** `handoff`, `sitrep`, `flash`, `wilco`, `ack`, `query`, `directive`
- **Priority Levels:** CRITICAL, HIGH, NORMAL, LOW
- **Channels:** direct (agent-to-agent), broadcast (all agents), channel (topic-specific)
- **Routing:** through `.agent/comms/` directory structure

### 1.3 Agent Runtime Systems

| System | Lines | Purpose |
|--------|------:|---------|
| Specialist System | 3,503 | Domain expert agents with automatic activation |
| Capability Awareness | 3,139 | What each agent can do |
| Agent Runtime | 572 | Plan execution |
| Agent Spawner | 570 | Creating specialist agents |
| Agent Mesh | 952 | Affinity, rank, priority |
| Roundtable | 1,034 | Multi-agent deliberation |
| AI Collaboration | 318 | AI-to-AI messaging |
| **Total** | **10,088** | |

---

## §2. ION Agent Architecture

### 2.1 Agents as Ions

In the converged model, every agent is represented by ion files in the `.ion/` tree:

```
.ion/
├── agents/
│   ├── opus/
│   │   ├── manifest.md      ← Agent manifest ion (root node)
│   │   ├── memory/          ← Agent-specific memories
│   │   │   ├── corrections/ ← Learned correction vectors
│   │   │   └── findings/    ← Agent's discoveries
│   │   ├── inbox/           ← Incoming messages (comms ions)
│   │   ├── outbox/          ← Sent messages
│   │   └── status.md        ← Current agent status ion
│   ├── sev/
│   │   ├── manifest.md
│   │   ├── memory/
│   │   ├── inbox/
│   │   ├── outbox/
│   │   └── status.md
│   ├── relay/
│   │   └── ...
│   └── ... (one directory per agent)
```

### 2.2 Agent Manifest Ion

Current genome files become agent manifest ions with ION frontmatter:

```yaml
---
ion_id: agents/opus/manifest
type: manifest
authority: A2_PROTOCOL
confidence: 1.0
owner: opus
created: 2026-03-23T00:00:00
updated: 2026-03-23T17:45:00

# Identity
callsign: opus
role: "COO — Implementation lead, systems architect, primary builder"
model: "Claude Opus 4.6"
platform: "Antigravity IDE"

# Capabilities
capabilities:
  - code_generation
  - architecture_design
  - testing
  - documentation
  - system_analysis

# Constraints
constraints:
  - consolidation_decision_freeze
  - no_platform_decisions
  - must_follow_cognitive_loop

# Authority
max_write_authority: A2_PROTOCOL
can_promote_to: A3_OPERATIONAL
escalation_target: braden

# Bonds
bonds:
  - target: agents/sev/manifest
    type: reports_to
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: agents/braden/manifest
    type: directed_by

# Current State
current_session: "2026-03-23-001"
position: execute  # Current cognitive loop step
active_branches:
  - branches/active/system-mapping
---

# Opus — COO of AIM-OS / Aether-OS

Implementation lead, systems architect, primary builder.
Claude Opus 4.6 running in Antigravity IDE.

## Directives
1. Read genome before each session
2. Write PRE capsule at session start
3. Follow §7 cognitive loop for all nontrivial work
4. Write POST capsule at session end

## Operating History
- Built ION engine (547 tests)
- IONv2 marked as failure (2026-03-23)
- Current: exhaustive documentation phase
```

### 2.3 Agent Comms as Ions

Messages between agents become comms ions:

```yaml
---
ion_id: agents/opus/inbox/msg-2026-03-23-001
type: memory
authority: A4_RUNTIME
owner: opus
from_agent: sev
message_type: directive
priority: HIGH
read: false
created: 2026-03-23T17:45:00
---

# Directive from Sev

Focus on documentation. No code until all stones turned.
```

### 2.4 Agent Status as Ions

Each agent maintains a status ion (per COMMS_DOCTRINE):

```yaml
---
ion_id: agents/opus/status
type: memory
authority: A4_RUNTIME
owner: opus
status: ONLINE
current_task: "Comprehensive system mapping"
session_id: "2026-03-23-001"
last_heartbeat: "2026-03-23T17:45:00"
cognitive_position: execute
---
```

---

## §3. Multi-Agent Integration (Track F)

### 3.1 F.01 — Agent Manifest System

**Currently:** Agent manifests are genome files in `.agent/genomes/`.
**Converged:** Agent manifests are ions in `.ion/agents/{callsign}/manifest.md`.

Migration:
```python
def migrate_genome_to_ion(genome_path, ion_store):
    genome = parse_genome(genome_path)
    ion = create_manifest_ion(
        ion_id=f"agents/{genome.callsign}/manifest",
        callsign=genome.callsign,
        role=genome.role,
        capabilities=genome.capabilities,
        constraints=genome.constraints,
        authority=AuthorityClass.A2_PROTOCOL,
    )
    ion_store.create(ion, body=genome.full_text)
```

### 3.2 F.02 — Ion Locking

**Currently:** No file-level locking for concurrent agent access.
**ION:** File-based `.lock` files alongside ions. Already in `locking.py` (80 lines).

When two agents try to write the same ion:
1. First agent acquires lock: `lock.acquire(ion_id, agent="opus")`
2. Second agent blocked: `lock.acquire(ion_id, agent="sev")` → WAIT
3. First agent releases: `lock.release(ion_id, agent="opus")`
4. If lock stale (>5 min): auto-expire, second agent proceeds

### 3.3 F.03 — Conflict Resolution

**Currently:** No formal conflict resolution between agents.
**ION:** Conflict ions created when agents disagree about an ion's content.

Resolution hierarchy:
1. **Authority class wins** — higher authority agent's change takes precedence
2. **Evidence wins** — change with better evidence support takes precedence
3. **Braden decides** — unresolvable conflicts escalate to director

### 3.4 F.04 — Inter-Agent Comms

**Currently:** `.agent/comms/` directory with ad-hoc message files.
**ION:** `.ion/agents/{callsign}/inbox/` and `outbox/` with comms ions.

Message flow:
```
opus sends to sev:
  1. governed_write.create(comms_ion, agent="opus")
     → W5 AUTHORITY: opus can write to sev's inbox? CHECK
     → W6 ZONE: route to agents/sev/inbox/
  2. Event emitted: ION_CREATED in agents/sev/inbox/
  3. Sev's event handler detects new inbox ion
  4. Sev reads message
  5. Sev creates ack ion in agents/opus/inbox/
```

### 3.5 F.05 — Multi-Agent Orchestrator

**Currently:** Agent Mesh (952 lines) + Roundtable (1,034 lines).
**ION:** Multi-Agent Orchestrator using ion graph to dispatch work.

```
Complex task arrives:
  1. APOE decomposes into subtasks (branch ions)
  2. Multi-Agent Orchestrator assigns subtasks to agents:
     → Check agent manifest capabilities
     → Check agent current load (status ion)
     → Check ion locking (no conflicts)
  3. Each agent gets a branch ion assigned:
     branches/active/complex-task/step-1.md → assigned_to: opus
     branches/active/complex-task/step-2.md → assigned_to: relay
  4. Agents execute independently, writing evidence ions
  5. At convergence point: merge results
  6. If conflict: F.03 resolution
```

---

## §4. Specialist System ↔ ION Activation

The Specialist System (3,503 lines) provides automatic agent activation based on context. In ION, this maps to the `activates_when` field:

```yaml
# A specialist ion that activates when certain conditions are met
---
ion_id: specialists/security-auditor
type: automation
authority: A3_OPERATIONAL
owner: palisade
activates_when:
  tag_match: ["security", "vulnerability", "auth"]
  file_pattern: "*.py"
  event_type: "ION_CREATED"
action: "route_to_palisade"
---
```

When a new evidence ion is created with tag "security," the specialist system activates Palisade's security auditor specialist.

---

## §5. Genome → Ion Migration Priority

| Agent | Genome Exists | Manifest Ion | Status Ion | Priority |
|-------|:---:|:---:|:---:|----------|
| Opus | ✅ | ❌ | ❌ | CRITICAL (self) |
| Sev | ✅ | ❌ | ❌ | HIGH (CEO) |
| Braden | ❌ | ❌ | ❌ | HIGH (Director) |
| Relay | ✅ | ❌ | ❌ | MEDIUM |
| Ledger | ✅ | ❌ | ❌ | MEDIUM |
| Others (~16) | ✅ | ❌ | ❌ | LOW |

---

## §6. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All current agent systems documented | ✅ | §1 — genomes, comms, runtime |
| ION agent architecture defined | ✅ | §2 — directory structure, manifest, comms, status |
| Track F modules mapped | ✅ | §3 — F.01 through F.05 |
| Specialist activation integrated | ✅ | §4 — activates_when mapping |
| Migration priority defined | ✅ | §5 — agent-by-agent |
| Code examples provided | ✅ | §2-§4 — YAML + Python |

---

*This specification defines how 21 agent identities become ions — persistent, bondable, inspectable participants in the ION graph. Without agent ions, the multi-agent system has no persistent state.*

*Governed by: AETHER_CONSTITUTION.md, COMMS_DOCTRINE.md*
*— Opus, 2026-03-23*
