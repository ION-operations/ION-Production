---
id: "agent_genome_T1_overview"
system: "agent_genome"
component: null
level: "T1"
type: "overview"
title: "Agent Genome System Overview"
description: "500-word overview of Agent Genome System"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "ra"
status: "complete"
tags: ["agent_genome", "agents", "versioning", "cloning", "evolution", "t0-t6", "transitional"]
dependencies: ["agent_genome_T0_executive"]
related_docs: ["agent_genome_T2_architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Genome System – T1 Overview (≈500 words)

## Purpose & Scope

Agent Genome System enables persistent, specialized, cloneable agents that grow dynamically within AIM-OS. Each agent is a versioned, bitemporal bundle (genome) containing identity, policies, competence, context, metrics, and experience. Agents can be snapshotted, cloned with delta mutations (Lex A/B/C/D variants), and evolved through tournament-based promotion with quality gates (VIF + SDF-CVF quartet parity).

**Core Value Proposition:** Persistent agent identity enabling specialization, controlled evolution, and complete provenance tracking with full AIM-OS integration.

**System Boundaries:**
- Agent Genome owns: Genome lifecycle, versioning, cloning, evolution, memory isolation
- Agent Genome does NOT own: Agent execution (orchestrated by APOE), memory storage (uses CMC), indexing (uses HHNI), verification (uses VIF)

## Users & Integrations

**Developers:** Create and manage specialized agents with versioning and evolution  
**AIM-OS Systems:** Full integration with all AIM-OS systems  
**CMC (Memory):** Bitemporal storage of genomes, episodes, memory channels  
**HHNI (Indexing):** Semantic indexing of genomes, skills, tools, playbooks  
**VIF (Verification):** Confidence tracking, witness envelopes, gate enforcement  
**SEG (Knowledge):** Knowledge synthesis, evidence linking, learning extraction  
**APOE (Orchestration):** Playbook execution, task orchestration, budget management  
**SDF-CVF (Quality):** Quartet parity validation, change tracking, gate enforcement

## Core Concepts

**Agent Genome:** Versioned, bitemporal bundle containing identity (ID, lineage), policies (objectives, guardrails, budgets), competence (skills, tools, playbooks), context (memory channels, RAG collections), metrics (eval scores, performance history), and experience (episodes, evidence links).

**Bitemporal Versioning:** Every genome has transaction time (when recorded) and valid time (when valid). Enables time-travel queries ("what was Lex's capability on Tuesday?") and corrections without deletion.

**Delta Cloning:** Create specialized clones (Lex A/B/C/D) with delta mutations. Clones inherit from parent, track lineage, and have isolated memories with shared knowledge via SEG pointers.

**Tournament Evolution:** Compare agent variants through eval suites, rank by performance (win-rate, cost, latency, confidence), and promote winner if quality gates pass (VIF confidence, SDF-CVF parity, eval thresholds).

## High-Level Data Flow

**Genome Creation:**
```
Agent Definition → Validate → Create Genome → Store in CMC → 
Index in HHNI → Create VIF Witness → Register → Ready
```

**Genome Evolution:**
```
Episode Recording → Compress Traces → Store in CMC → 
Create SEG Links → Update Metrics → Tournament → 
Promotion Gates → Promote Winner
```

**Clone Creation:**
```
Source Genome → Delta Mutations → Create Clone → 
Isolated Memory Channels → Index in HHNI → 
Create VIF Witness → Register Clone
```

## Non-Goals

Agent Genome System is NOT:
- **Agent Execution Engine:** Orchestrates agents, doesn't execute them (APOE handles execution)
- **Memory Storage:** Uses CMC for storage, doesn't replace it
- **Indexing System:** Uses HHNI for indexing, doesn't replace it
- **Verification System:** Uses VIF for verification, doesn't replace it
- **Generic Version Control:** Agent-specific genomes, not Git replacement

## References

- System map: `systems/agent_genome/system.map.lucid.json5` (to be created)
- Implementation plan: `knowledge_architecture/AETHER_MEMORY/RA_AGENT_GENOME_IMPLEMENTATION_PLAN.md`
- Operational protocols: `knowledge_architecture/AETHER_MEMORY/RA_AGENT_GENOME_OPERATIONAL_PROTOCOLS.md`
- Research: `knowledge_architecture/AETHER_MEMORY/RA_AGENT_GENOME_RESEARCH.md`
- CMC: `systems/cmc/T2_architecture.md`
- HHNI: `systems/hhni/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- APOE: `systems/apoe/T2_architecture.md`
- SEG: `systems/seg/T2_architecture.md`
- SDF-CVF: `systems/sdfcvf/T2_architecture.md`

