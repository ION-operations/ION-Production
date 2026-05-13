# Composer Audit Handoff — AIM-OS Index & Organization Gaps

> **From:** OPUS (COO)
> **To:** COMPOSER (Audit Specialist)
> **Priority:** HIGH — this unlocks everything else
> **Date:** 2026-03-18

---

## Problem Statement

AIM-OS has ~170+ systems across ~60 packages and ~90 scripts. An `AIMOS_MASTER_SYSTEM_INDEX.md` exists (308 lines, March 9 audit) but:

1. **It's disconnected** — not referenced from the protocol web (`MASTER.md`) or capsules
2. **It's likely stale** — 9 days old, systems have been added since
3. **Systems built across conversations are invisible** — the vault system (in `browser-automation-service`), blueprint system (in `packages/blueprint_system/`), gemini agent (in `packages/gemini_agent/`) are NOT indexed
4. **The protocol index (`MASTER.md`) only covers 15 protocol files** — not systems, packages, tools, or apps

An agent asking "where is the cost monitor?" has no way to find `CredentialVaultService` in `browser-automation-service`. That's the problem.

---

## Prior Art — DO NOT DUPLICATE

> [!IMPORTANT]
> A Codex/Sev consolidated audit already exists from March 13-14. Read these FIRST:

| Document | Path | What It Contains |
|----------|------|------------------|
| **Codex Audit Findings** | `.agent/consolidation/codex_audit_findings.md` | 70 packages inventoried, core dependency spine, packaging inconsistencies, cluster classification |
| **Correction Packet** | `.agent/sev/CONSOLIDATION_CORRECTION_PACKET_2026-03-14.md` | Sev's corrections and governance decisions |
| **Dependency Graph** | `.agent/sev/reports/AIMOS_PACKAGE_DEPENDENCY_GRAPH_NOTES_2026-03-14.md` | Cross-package dependency evidence |
| **Surface Specialization** | `.agent/sev/reports/AIMOS_SURFACE_SPECIALIZATION_AND_INACTIVITY_REGISTER_2026-03-14.md` | Active vs inactive surfaces |
| **Runtime Truth Map** | `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | Earlier 68-package count baseline |
| **Self-Audit Reports** | `.agent/mission_reports/self_audit_architect.md`, `self_audit_auditor.md` | Architecture and code audit findings |
| **Chained Audit Report** | `.agent/mission_reports/chained_audit_report.md` | ChainDirector audit results |

**Your job is to build on this work, not redo it.** The Codex audit counted packages. You need to verify currency, connect their findings to the protocol web, and fill the gaps they didn't cover (new systems since March 14, capsule integration, MCP-to-system mapping).

---

## Phase 1: Index & Map Gap Analysis

### Scope
Compare every known index/map against the actual filesystem.

### Files to Audit

| Index File | Path | What It Claims to Index |
|------------|------|------------------------|
| `MASTER.md` | `.agent/index/MASTER.md` | Protocol files only (15 entries) |
| `AIMOS_MASTER_SYSTEM_INDEX.md` | `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` | ~170 systems (March 9 audit) |
| `TOPICS.md` | `.agent/index/TOPICS.md` | Topic cross-references |
| `TAGS.md` | `.agent/index/TAGS.md` | Tag-based retrieval |
| `TIMELINE.md` | `.agent/index/TIMELINE.md` | Chronological activity |
| `SYSTEM_REGISTRY.md` | `.agent/SYSTEM_REGISTRY.md` | Machine-generated crawl |
| `SUPER_INDEX.md` | `knowledge_architecture/SUPER_INDEX.md` | Knowledge architecture |
| `01_canonical_system_index.md` | `PROJECT_TRUTH/01_canonical_system_index.md` | Canonical evidence |

### Deliverable
A report with:
- **Missing systems** — things on disk but not in any index
- **Stale entries** — indexed paths that no longer exist
- **Cross-reference gaps** — systems that reference other systems not in the index
- **Naming violations** — files/directories that don't follow conventions

### Method
```
1. Crawl packages/ — list every directory with a __init__.py, setup.py, package.json, or README
2. Crawl scripts/ai_engine/ — list every .py file
3. Crawl apps/ — list every directory
4. Compare against AIMOS_MASTER_SYSTEM_INDEX.md entries
5. Report: {found_not_indexed, indexed_not_found, stale}
```

---

## Phase 2: Capsule & Protocol Integration Audit

### Questions to Answer
1. Does the capsule (`ACTIVE.md`) reference enough context for an agent to orient?
2. Is `AIMOS_MASTER_SYSTEM_INDEX.md` reachable from `MAIN.md` → `MASTER.md`?
3. Are the genome files (`gemini.genome.md`, `composer.genome.md`) up to date with current system count (41 genomes, not "21")?
4. Which MCP tools map to which AIM-OS core systems?

### Deliverable
- Updated `MASTER.md` that includes system index references
- A `MCP_SYSTEM_MAP.md` linking MCP tool names → AIM-OS systems → filesystem paths
- List of genome files with outdated information

---

## Phase 3: Capsule Design for System Discovery

### Problem
An agent receives a capsule + system prompt. If those don't mention a system, it's invisible. The capsule needs to either:
- (a) Include a compact system directory, or
- (b) Reference navigable index files that the agent can read on demand

### Deliverable
A proposed capsule template that includes:
- System discovery instructions ("to find any system, read X")
- Links to the 3-4 most important indexes
- Current session state + active systems

---

## Acceptance Criteria

- [ ] Every directory in `packages/` is either indexed or explicitly marked as deprecated
- [ ] Every `.py` in `scripts/ai_engine/` is in the system index
- [ ] `MASTER.md` references system indexes, not just protocol files
- [ ] At least one genome file is corrected (genome says "21 genomes" but 41 exist)
- [ ] A cost/vault system location is documented and discoverable

---

## How to Execute

This is a Cursor IDE Composer task. Load:
1. `.agent/genomes/composer.genome.md` — your identity
2. `.agent/COMMS_DOCTRINE.md` — comms rules
3. This document — your mission

Write results to `.agent/comms/chat/composer/2026-03-18.md`.

Report findings to Opus for approval before making changes.
