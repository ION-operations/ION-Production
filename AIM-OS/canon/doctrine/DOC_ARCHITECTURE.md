---
ion_id: docs/aether-os/doc-architecture
type: protocol
authority: A2_CANONICAL_EXTENSION
confidence: 0.92
epistemic_status: DERIVED
owner: opus
created: 2026-03-24T17:45:00-04:00
updated: 2026-03-24T18:00:00-04:00
supersedes:
  - docs/aether-os/master-index
  - docs/aether-os/full-system-map
evolved_from:
  - docs/aether-os/system-universe-map
  - docs/aether-os/aether-atlas
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: docs/aether-os/aether-atlas
    type: depends_on
  - target: docs/aether-os/aether-interface
    type: depends_on
tags: [meta, organization, ai-retrieval, progressive-disclosure, canonical]
summary: |
  Documentation architecture for ION/Aether aligned to Constitution Art. 22-25,
  Atlas Book I §6 (load order), Book IV (retrieval zones), Book IX (governed ingestion).
  Defines progressive disclosure levels using the Atlas L1-L8 framework, standardized
  registry entries per Atlas Book II schema, evolution tracking, and the consolidated
  6-phase product roadmap.
---

# ION/Aether Documentation Architecture v2.0
## Aligned to Aether Canon

> **Governing law:** AETHER_CONSTITUTION Art. 22 (Authority Stack), Art. 24 (Active Context Envelope), Art. 25 (Selective Loading), Art. 33 (Symbolic Inflation).
>
> **Foundation:** AETHER_ATLAS Book I §6 (First-Read and Load Order), Book II (Registry Schema), Book III (Runtime Truth States), Book IV (Retrieval Zones and Continuity), Book IX (Governed Ingestion).
>
> **Epistemic status:** DERIVED from deep reading of all 4 governing documents (Constitution 583 lines, Kernel 422 lines, Interface 1116 lines, Atlas 1327 lines).

---

## §1. The Problem This Solves

The system has 500K+ lines of code, 350+ research documents, 58 audit files, 55 North Star documents, and 49 roadmaps. Every new AI agent starts at zero. Current documentation is organized for human reading, not for how AI agents actually consume context.

**Constitution Art. 25 (Selective Loading)** mandates: *"Load what governs current work, the hardest truth conditions, required dependencies, and continuity surfaces. No more until justified."*

**Constitution Art. 33 (Symbolic Inflation)** warns: *"The ultimate danger is slow symbolic inflation — more functions described beautifully at the constitutional level without corresponding enforcement at the protocol and runtime level."*

This document defines how to organize documentation so agents load the minimum context needed while maintaining lawful governance.

---

## §2. Load Order — Aligned to Atlas Book I §6

The Atlas already defines the canonical load order. Documentation MUST be organized along these layers:

```
L1  SUPREME CANON              Constitution / Kernel
    What governs all behavior
    
L2  ROUTE AND EMBODIMENT       Bootloader / Genome
    Who am I, where am I
    
L3  MISSION AND CANON          North Star / Mission Brief
    What is the purpose, where are we going
    
L4  CURRENT-STATE SURFACES     State Register / Status Files
    What works, what's broken, what changed
    
L5  ACTIVE PLAN AND OBJECTIVE  Phase plan, next action
    What am I doing right now
    
L6  CONTRADICTIONS AND RISKS   Collision Register / Gap Analysis
    What is unresolved, what could break
    
L7  DEPENDENCIES               Domain maps, system cards, source code
    What I need to understand for my task
    
L8  HISTORICAL CONTEXT         Archive, old audits, evolution chains
    What came before (load only when needed)
```

### Current Files Mapped to Layers

| Layer | File(s) | Status |
|-------|---------|--------|
| **L1** | `AETHER_CONSTITUTION.md`, `AETHER_KERNEL.md` | ✅ Exist |
| **L2** | `.agent/BOOTLOADER.md`, `.agent/genomes/*.genome.md` | ✅ Exist |
| **L3** | `NORTH_STAR.md` (needs update — see §5), `ION_PREMIUM_BUILD.md` | ⚠️ Stale/fragmented |
| **L4** | **`STATE_REGISTER.md`** — must be generated from runtime probes | ❌ Doesn't exist as single file |
| **L5** | Per-agent status files in `.agent/comms/status/` | ✅ Exist |
| **L6** | Atlas Book III §6 Canon Collision Register | ⚠️ In Atlas only, not standalone |
| **L7** | Domain maps + system cards (this doc defines their structure) | ❌ Need creation |
| **L8** | `01_COMPREHENSIVE_TECHNICAL_AUDIT.md`, `UNIFIED_MASTER_INDEX.md` | ✅ Exist |

### What Must Be Created

| Document | Layer | Purpose |
|----------|-------|---------|
| **GENESIS.md** | L3 | 100-word system identity (see §4) |
| **NORTH_STAR.md** (v2) | L3 | Updated 6-phase roadmap (see §5) |
| **STATE_REGISTER.md** | L4 | Single-file runtime truth register + decisions |
| 12 domain summaries | L7 | One per operational domain (see §6) |
| System cards | L7 | Per-module registry entries using Atlas schema |

---

## §3. Document Standards — Aligned to Atlas Book II

### Every Document Is An Ion

Every `.md` in `docs/Aether-OS/` carries YAML frontmatter using ION conventions:

```yaml
---
ion_id: docs/aether-os/{name}
type: evidence|protocol|memory|branch|manifest|law
authority: A0|A1|A2|A3|A4|A5|A6|A7
confidence: 0.0-1.0
epistemic_status: OBSERVED|SOURCED|DERIVED|ASSUMED|SPECULATIVE|PENDING
owner: {callsign}
created: ISO-8601
updated: ISO-8601
supersedes: [list of ion_ids this replaces]
evolved_from: [list of ion_ids this grew from]
bonds:
  - target: {ion_id}
    type: governed_by|depends_on|informs|produces|contradicts
tags: [searchable, keywords]
summary: |
  2-3 sentence summary readable by AI without opening the file.
---
```

> **Key difference from v1:** `epistemic_status` is now REQUIRED per Constitution Art. 7 (Claim Classification). Every document's claims are tagged OBSERVED/DERIVED/ASSUMED.

### System Cards Use Atlas Registry Schema

Every system card (L7) follows the Atlas Book II §2 field schema:

```yaml
- id: {snake_case}
  canonical_name: {Full Name}
  ceremonial_name: {Acronym}
  interface_name: {User-facing label}
  module_name: {package directory}
  authority_class: A0-A7
  ontology_class: LAW|SEMANTIC_OBJECT|STATE_OBJECT|PROCESS_OBJECT|
                  EVIDENCE_OBJECT|INTERFACE_OBJECT|META_GOVERNANCE_OBJECT|
                  SUBSTRATE_OBJECT
  runtime_truth: ALIVE|FUNCTIONAL|PARTIAL|DEGRADED|BROKEN|
                 DOCTRINAL_ONLY|EXTERNAL_UNSETTLED
  owned_state: [list]
  primary_runtime_owner: {path}
  dependencies:
    upstream: [list]
    downstream: [list]
  open_gaps: [list]
  last_assessed: {date}
```

This is NOT a new schema. It is the Atlas schema, applied consistently.

### Runtime Truth States (Atlas Book III §2)

All runtime assessments use the canonical 7-state scale:

```
ALIVE > FUNCTIONAL > PARTIAL > DEGRADED > BROKEN > DOCTRINAL_ONLY > EXTERNAL_UNSETTLED
```

No informal labels (working, broken, almost done). Only these 7 states.

### Evolution Tracking

When a system is updated or superseded:

**New document** receives:
```yaml
supersedes:
  - path/to/old-version
evolution_note: |
  {What changed, why, who did it, when}
```

**Old document** receives header:
```yaml
status: SUPERSEDED
superseded_by: path/to/new-version
superseded_date: ISO-8601
```

**Evolution document** in `evolution/` explains the RELATIONSHIP:
```markdown
# Evolution: {System Name}
## Lineage
v1 (location) → v2 (location) → v3 (location)
## Why Each Version Changed
- v1→v2: {reason, who, when}
- v2→v3: {reason, who, when}
## How v3 Fits ION/Aether
{Relationship to current architecture}
```

---

## §4. GENESIS — System Identity (L3, 100 words)

> ION/Aether is a governed intelligence system. AI agents operate under constitutional law (39 articles), using typed protocol schemas (21 schemas) and a seven-step cognitive loop (contextualize→reflect→plan→gate→execute→audit→deliver). Knowledge is organized as ions — files with YAML frontmatter and typed bonds forming a traversable graph. The system enforces governance through a 10-stage governed write pipeline. It currently exists as a Python runtime (63 modules, 13K lines) being built toward: (A) MVP AI builder, (B) VS Code extension, (C) VS Code fork, (D) ground-up IDE, (E) Linux distribution, (F) quaternion-kernel OS.

---

## §5. NORTH STAR — Product Roadmap (L3)

### The Thesis

AIM-OS/ION/Aether is the **Ultimate Builder** — an AI system that builds anything users describe, while building what IT needs to become continuously more capable. This is the meta-circular development loop described in the original North Star (Nov 2025), now extended through the ION operating system vision.

### The Product Phases

```
PHASE A: MVP AI BUILDER (Web)               ◄── FIRST REVENUE
├── Lovable-style web AI chat/builder
├── ION context engine provides intelligent code understanding
├── Three-tier context (pinned/working/long-term) budget-managed
├── Governed writes enforce quality — every output auditable
├── K-Gate confidence scoring — AI admits uncertainty
├── Capsule system — sessions resume without context loss
└── Revenue: subscription, per-build pricing

PHASE B: VS CODE EXTENSION                  ◄── IDE INTEGRATION
├── Extension that wires VS Code to ION context server
├── Bidirectional: IDE workspace → ions (tree-sitter ingest)
├── Code-aware chat: querying ION graph for context
├── Ion panel in VS Code sidebar (graph browser)
├── Constitutional governance visible (confidence, authority)
└── Distribution: VS Code Marketplace

PHASE C: ION IDE — VS CODE FORK             ◄── OWN PRODUCT
├── Fork VS Code, replace command palette with cognitive loop
├── Native ion graph browser (replaces file tree)
├── Built-in agent swarm management (BOOTLOADER-powered)
├── JOC integrated as primary dashboard
├── Governed write enforcement on every save
├── Dreamspace resonance scoring for aesthetic quality
└── Distribution: standalone installer

PHASE D: ION IDE — GROUND-UP                ◄── FULL CONTROL
├── Custom IDE (Tauri/Electron), AI-first design
├── Every interaction is an ion (governed, audited, bonded)
├── ION terminal: commands = ions = traceable
├── No legacy code editor assumptions
├── Native multi-agent workspace (concurrent humans + AI)
└── Distribution: ION IDE installer

PHASE E: AETHER LINUX                       ◄── OS INTEGRATION
├── Linux distro with ION as native system intelligence
├── ION filesystem daemon (file events → ions automatically)
├── Desktop environment with governance overlay
├── Package manager using ION reasoning for dependencies
├── systemd services for ION server, MCP bridge, agent mesh
└── Distribution: bootable ISO

PHASE F: ION-OS — QUATERNION KERNEL          ◄── THE ENDGAME
├── Quaternion kernel (Rust, 4 syscalls: place/move/sense/emit)
├── S³ binning: geometric process scheduling
├── Ion graph IS the filesystem (not atop ext4)
├── Physics-based resource allocation
├── Self-modifying governance within constitutional bounds
├── Witness structures for every state transition
└── Status: A6 Research Branch (Atlas §4.28)
```

**Current position:** Between Phase A and Phase B. ION engine (63 modules) is FUNCTIONAL. Need: bootstrap fix, first live LLM e2e, VS Code extension scaffold.

### Relationship to Original North Star

The Nov 2025 AIM_OS_NORTH_STAR.md (838 lines) described the 8 core systems (CMC, HHNI, VIF, APOE, SEG, SDF-CVF, CAS, SIS) and a 4-phase roadmap (Bootstrap→Sophistication→Liberation→Ultimate). Since then:

- ION engine was built (16K lines, 547 tests)
- Aether constitutional stack was written (3.4K lines, 39 articles)
- Quaternion kernel was prototyped (Rust, 641 lines)
- Multi-agent swarm was deployed (6+ agents, BOOTLOADER-driven)
- Context compiler was enhanced (three-tier budget model)
- LLM adapter was rebuilt (Gemini+Ollama+Mock)

The original North Star's vision remains accurate. This roadmap extends it from "AI chat" to "full operating system."

---

## §6. L7 Domain Map Structure

Domain summaries provide the L7 dependency layer. Each references the SYSTEM_UNIVERSE_MAP (690 lines, 12 domains) as its source, compressed to ~500 words per domain.

### Proposed Domain Files

| File | Source | Systems Covered |
|------|--------|-----------------|
| `domains/core_infrastructure.md` | UNIVERSE_MAP §2 | CMC, HHNI, VIF, APOE, SEG, SDF-CVF, TCS, CAS, IIS |
| `domains/ion_engine.md` | ION_RUNTIME_AUDIT | 63 ION modules (13K lines) |
| `domains/victus_runtime.md` | UNIVERSE_MAP §14 | Pipeline, DAG, Mesh, Crucible, K-Gate |
| `domains/agents.md` | UNIVERSE_MAP §5, BOOTLOADER | Genomes, swarm, bootloader, comms |
| `domains/ui_cockpit.md` | UNIVERSE_MAP §7 | JOC, ide_chat_app, ion-ui, plix |
| `domains/mcp_transport.md` | UNIVERSE_MAP §6 | Lucid MCP, HTTP fallback, RAG proxy |
| `domains/constitutional.md` | Constitution, Kernel, Interface, Atlas | 4 docs, 3.4K lines |
| `domains/ai_engine.md` | UNIVERSE_MAP §3 | scripts/ai_engine/ (24K lines) |
| `domains/security.md` | UNIVERSE_MAP §8, §11 | Sentinel, SCOR, safety, consciousness |
| `domains/knowledge.md` | UNIVERSE_MAP §12 | knowledge_architecture, PROJECT_TRUTH |
| `domains/apps.md` | UNIVERSE_MAP §10 | Echo-Forge, system-atlas, ProEarth |
| `domains/quaternion.md` | Atlas §4.28 | quaternion_kernel, quaternion_math |

Each domain file:
- Opens with YAML frontmatter (ion format)
- Lists every system in the domain with Atlas runtime truth state
- Maps each system to ION integration surface
- Identifies open gaps and next actions
- Claims are classified per Constitution Art. 7

---

## §7. Retrieval Zones — Aligned to Atlas Book IV §4

Documentation falls into retrieval zones that determine default loading behavior:

| Zone | Priority | Content | Loading Rule |
|------|----------|---------|--------------|
| **Active Canon** | 1 (default) | Constitution, Kernel, Bootloader, Genome | Always loaded on boot |
| **Active Runtime Support** | 2 (loaded as needed) | STATE_REGISTER, domain summaries, system cards | Loaded per task scope |
| **Lineage** | 3 (for interpretation) | SYSTEM_UNIVERSE_MAP, DEEP_CONSOLIDATION, original North Star | Read when understanding evolution |
| **Research** | 4 (only when invoked) | Quaternion kernel, theoretical docs, UNIFIED_MASTER_INDEX | Loaded only for Phase F work |
| **Quarantine** | 5 (never default) | Stale audits, old roadmaps, redundant indexes | Do not load unless explicitly requested |

### Quarantine List

These documents should be marked `status: QUARANTINED` in their frontmatter and never loaded by default:

- 33 duplicate/stale North Star expansion documents (Nov 2025)
- 15+ old audit files superseded by Feb 2026 Codex audit
- Old roadmaps in `ide_orchestration/prototypes/dac/docs/` (DAC v2 era)
- Multiple old `MASTER_INDEX` variants (superseded by Atlas Book II registry)

---

## §8. Boot Sequence for AI Agents

The BOOTLOADER already implements the correct sequence. Documentation is loaded in dependency order:

```
BOOTLOADER (L2)                                     ~175 words
├─ 1. Identify yourself (registry lookup)
├─ 2. Load genome (role, scope, personality)          ~500 words
├─ 3. Load protocols (COMMS, IDE output, respawn)     ~1500 words
├─ 4. Load active mission                             ~500 words
├─ 5. Check crash recovery (status files)             ~200 words
├─ 6. Read peer status                                ~200 words
├─ 7. Update your status file
└─ 8. Begin work
                                                      ≈3075 words total
```

**After boot, the agent has ~5K tokens loaded.** In a 200K context window, that's 2.5%. 97.5% remains for actual work.

**When the agent needs deeper context** (L7 dependencies), it reads:
1. The relevant domain summary (~500 words)
2. The relevant system cards (~200 words each)
3. The actual source files (only when modifying)

This follows Constitution Art. 25: *"Load what governs current work...no more until justified."*

---

## §9. What Must Be Built — Priority Order

| Priority | Document | Layer | Effort | Blocked On |
|----------|----------|-------|--------|------------|
| 🔴 P0 | `GENESIS.md` | L3 | Hours | Nothing — text above in §4 |
| 🔴 P0 | `NORTH_STAR.md` v2 | L3 | Hours | Nothing — text above in §5 |
| 🟡 P1 | `STATE_REGISTER.md` | L4 | Day | Merging Atlas Book III + runtime probes |
| 🟡 P1 | 12 domain summaries | L7 | Days | Extracting from SYSTEM_UNIVERSE_MAP |
| 🔵 P2 | System cards for 32 Atlas objects | L7 | Week | Atlas registry as source |
| 🔵 P2 | Evolution docs for 5 system families | L8 | Days | DEEP_CONSOLIDATION as source |
| ⚪ P3 | Quarantine headers on stale docs | — | Day | File list in §7 |
| ⚪ P3 | YAML frontmatter migration | — | Week | All docs in docs/Aether-OS/ |

---

## §10. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Aligned to Atlas L1-L8 load order | ✅ | §2 maps directly to Atlas Book I §6 |
| Uses Atlas runtime truth states | ✅ | §3 cites 7-state scale |
| Uses Atlas registry schema for cards | ✅ | §3, Book II §2 field schema |
| Follows Constitution Art. 7 (claims) | ✅ | `epistemic_status` required in frontmatter |
| Follows Constitution Art. 22 (authority stack) | ✅ | Authority classes used throughout |
| Follows Constitution Art. 25 (selective loading) | ✅ | §8 boot sequence, retrieval zones |
| Addresses Art. 33 (symbolic inflation) | ✅ | §1 explicitly warns, §9 is concrete |
| Compatible with BOOTLOADER | ✅ | §8 references BOOTLOADER directly |
| Doesn't reinvent Atlas structures | ✅ | All structures cite Atlas sources |
| North Star updated from Nov 2025 | ✅ | §5, 6 phases, current position noted |
| Product roadmap includes MVP AI builder | ✅ | Phase A in §5 |

---

## §11. Existing Documents — Disposition

| Document | Lines | Retrieval Zone | Action |
|----------|------:|---------------|--------|
| AETHER_CONSTITUTION.md | 583 | Active Canon | ✅ Keep — supreme law |
| AETHER_KERNEL.md | 422 | Active Canon | ✅ Keep — boot projection |
| AETHER_INTERFACE.md | 1116 | Active Canon | ✅ Keep — 21 schemas |
| AETHER_ATLAS.md | 1327 | Active Canon | ✅ Keep — 32 objects, runtime truth |
| SYSTEM_UNIVERSE_MAP.md | 690 | Lineage | ✅ Keep — source for domain summaries |
| 01_COMPREHENSIVE_TECHNICAL_AUDIT.md | 339 | Lineage | ✅ Keep — Codex baseline evidence |
| ION_RUNTIME_AUDIT.md | 150 | Runtime Support | ✅ Keep — victus/ion/ file audit |
| STATE_OF_THE_UNION.md | 170 | → evolves into STATE_REGISTER.md | ⚠️ Merge |
| ION_STATE_OF_BUILD.md | 348 | Lineage | ✅ Keep — point-in-time evidence |
| ION_PREBUILD_AUDIT.md | 172 | Lineage | ✅ Keep — live test results |
| DEEP_CONSOLIDATION_ANALYSIS.md | 350 | → source for evolution/ docs | ✅ Keep |
| ION_OS_VISION.md | 300 | → absorbed into NORTH_STAR v2 | ⚠️ Supersede |
| AIM_OS_NORTH_STAR.md | 838 | Lineage (Nov 2025 vision) | ✅ Keep as A3 predecessor |
| UNIFIED_MASTER_INDEX.md | 703 | Research | ✅ Keep — 350+ doc index |
| FULL_SYSTEM_MAP.md | 473 | Quarantine | ❌ Superseded by UNIVERSE_MAP |
| MASTER_INDEX.md | 714 | Quarantine | ❌ Superseded by Atlas Book II |
| 33 old North Star expansion docs | — | Quarantine | ❌ Stale |

---

*Governed by: AETHER_CONSTITUTION.md — Art. 22, 24, 25, 33*
*Derived from: AETHER_ATLAS.md — Books I, II, III, IV, IX*
*— Opus, 2026-03-24*
