# SAM (System Anatomy Mapping) – Definitive Docs Hub

**Purpose:** Single canonical location for SAM protocol and how-to docs across AIM-OS. Use this when creating or editing system maps, MASTER_* docs, or any System Anatomy Mapping work.

**Status:** ACTIVE  
**Date:** 2026-02-12  
**Scope:** AIM-OS repo-wide (apps, ProEarth, knowledge_architecture)

---

## Start here

| I want to… | Document | Path |
|------------|----------|------|
| **Understand what SAM is** | Protocol overview + full spec | [PROTOCOLS/SAM_PROTOCOL_COMPLETE.md](../PROTOCOLS/SAM_PROTOCOL_COMPLETE.md) |
| **Navigate the protocol** | Protocol index (by topic / use case) | [PROTOCOLS/SAM_PROTOCOL_INDEX.md](../PROTOCOLS/SAM_PROTOCOL_INDEX.md) |
| **Quick reference** (tags, schema, commands) | One-page quick reference | [SAM_QUICK_REFERENCE.md](./SAM_QUICK_REFERENCE.md) |
| **Add or update a system map** | Growth protocol (when/how, checklist) | [SAM_GROWTH_PROTOCOL.md](./SAM_GROWTH_PROTOCOL.md) |

---

## What SAM is

**SAM (System Anatomy Mapping)** is a **compiler-based documentation methodology**, not a file format or a doc tool:

- **Sources** (canonical `MASTER_*.md`) → **Compiler** → **Monolith** (for AI/RAG) + **Build evidence** (hashes, manifest).

Every system map must cover **five dimensions**:

1. **Structure** – Components, relationships, hierarchy  
2. **Behavior** – Lifecycle, flows, operations  
3. **Interfaces** – Public API, UI↔backend contracts  
4. **Constraints** – Limits, invariants, failure modes  
5. **Evidence** – Status, tests, open gaps  

**Three artifacts:** Canonical sources (editable), compiled monolith (do not edit), build evidence (verification).

---

## AIM-OS SAM sources (core systems)

| Doc | Location | Role |
|-----|----------|------|
| **SAM_MASTER_INDEX** | [SAM_MASTER_INDEX.md](./SAM_MASTER_INDEX.md) | Central index: all AIM-OS subsystem maps, code anchors |
| **Sources** | [sources/](./sources/) | MASTER_* SAM sources (CMC, HHNI, VIF, SEG, APOE, SDF-CVF, TCS, CAS, SCOR, IIS, MCP) |

---

## Definitive doc locations (this repo)

| Doc | Location | Role |
|-----|----------|------|
| **SAM_PROTOCOL_COMPLETE.md** | `knowledge_architecture/PROTOCOLS/SAM_PROTOCOL_COMPLETE.md` | Full SAM protocol (v3.0) – authoritative |
| **SAM_PROTOCOL_INDEX.md** | `knowledge_architecture/PROTOCOLS/SAM_PROTOCOL_INDEX.md` | Protocol navigation and use cases |
| **SAM_QUICK_REFERENCE.md** | `knowledge_architecture/SAM/SAM_QUICK_REFERENCE.md` | One-page: schema, tags, commands, file layout |
| **SAM_GROWTH_PROTOCOL.md** | `knowledge_architecture/SAM/SAM_GROWTH_PROTOCOL.md` | How to add/update system maps and keep alignment |

**Other copies (reference only):**

- **RenderLab:** `apps/ProEarth/GPTworking/originalPROearthGPT/ProEarth_Updated_RenderLab/docs/dev/sam/System_Architecture_Mapping_SAM/` – same protocol + quick reference.
- **ProEarth earthdocs:** `apps/ProEarth/GPTworking/earthdocs/SAM/` – ProEarth SAM hub (master index, growth protocol, sources, config).

For **AIM-OS-wide** work (any app or repo), treat **this folder** and **knowledge_architecture/PROTOCOLS** as the definitive source.

---

## For Cursor agents

- **Rule:** `.cursor/rules/SAM_PROTOCOL.mdc` – applies when working with system docs, MASTER_* files, or SAM.
- **Skill:** `.cursor/skills/sam-protocol/SKILL.md` – use when creating/editing system maps or SAM docs; points here and to the protocol.

Read `knowledge_architecture/SAM/README.md` (this file) and the doc that matches your task (protocol complete, index, quick reference, or growth protocol).

---

## Quick workflow

1. **New system map:** Follow [SAM_GROWTH_PROTOCOL.md](./SAM_GROWTH_PROTOCOL.md) (when to add, 5-dimension template, index updates, quality checklist).
2. **Tags / schema / build:** Use [SAM_QUICK_REFERENCE.md](./SAM_QUICK_REFERENCE.md).
3. **Deep protocol (compiler, evidence, implementation):** Use [PROTOCOLS/SAM_PROTOCOL_COMPLETE.md](../PROTOCOLS/SAM_PROTOCOL_COMPLETE.md).
