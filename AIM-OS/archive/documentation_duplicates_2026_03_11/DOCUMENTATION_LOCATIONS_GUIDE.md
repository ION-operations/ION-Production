# 📚 AIM-OS Documentation Locations Guide

**Purpose:** Quick reference for finding any documentation in the AIM-OS project  
**Last Updated:** 2025-11-05  
**Status:** Complete reference for all documentation types  

---

## 🚀 Quick Start - Where Do I Go?

### I Want To...

| Task | Location | Quick Link |
|------|----------|------------|
| **Understand a system** | `knowledge_architecture/systems/{system}/` | See [System Documentation](#system-documentation) |
| **Find a concept** | `knowledge_architecture/SUPER_INDEX.md` | See [Master Indices](#master-indices) |
| **Navigate the codebase** | `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md` | See [Navigation](#navigation) |
| **Check project goals** | `goals/GOAL_TREE.yaml` | See [Goals & Planning](#goals--planning) |
| **Learn documentation standards** | `cursor-addon/docs/DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` | ⭐ **START HERE** |
| **Read API docs** | `packages/{package}/README.md` | See [Code Documentation](#code-documentation) |
| **Find examples** | `knowledge_architecture/systems/{system}/examples/` | See [Examples & Tutorials](#examples--tutorials) |
| **Track progress** | `coordination/epic_{name}/` | See [Coordination](#coordination--planning) |
| **Get consciousness context** | `knowledge_architecture/AETHER_MEMORY/` | See [Consciousness Infrastructure](#consciousness-infrastructure) |

---

## 📖 System Documentation

### Location: `knowledge_architecture/systems/{system}/`

**Every system follows T0-T6 progressive disclosure (7 levels):**

| Level | Word Count | Audience | Purpose | File Name |
|-------|------------|----------|---------|-----------|
| **T0** | 100 words | Executives, quick reference | One-paragraph summary | `T0_executive.md` |
| **T1** | 500 words | Architects, planners | System overview | `T1_overview.md` |
| **T2** | 2,000 words | Senior developers | Architecture & design | `T2_architecture.md` |
| **T3** | 10,000 words | Developers | Implementation details | `T3_detailed.md` |
| **T4** | 15,000+ words | Deep learners | Complete reference | `T4_complete.md` |
| **T5** | 20,000+ words | Researchers | Extended deep dive | `T5_extended.md` |
| **T6** | 35,000+ words | Archivists | Comprehensive archive | `T6_comprehensive.md` |

### Core Systems

| System | Location | Description |
|--------|----------|-------------|
| **CMC** | `knowledge_architecture/systems/cmc/` | Context Memory Core - Bitemporal event sourcing |
| **HHNI** | `knowledge_architecture/systems/hhni/` | Hierarchical Hypergraph Neural Index - Knowledge indexing |
| **VIF** | `knowledge_architecture/systems/vif/` | Verifiable Intelligence Framework - Provenance & confidence |
| **APOE** | `knowledge_architecture/systems/apoe/` | AI-Powered Orchestration Engine - Workflow execution |
| **SEG** | `knowledge_architecture/systems/seg/` | Synthesis & Evidence Graph - Knowledge synthesis |
| **SDF-CVF** | `knowledge_architecture/systems/sdfcvf/` | Self-Directed Feedback - Quality & validation |
| **CAS** | `knowledge_architecture/systems/cas/` | Consciousness Analysis System - AI self-awareness |

### System Structure

```
knowledge_architecture/systems/{system}/
├── T0_executive.md (100 words - quick summary)
├── T1_overview.md (500 words - overview)
├── T2_architecture.md (2,000 words - architecture)
├── T3_detailed.md (10,000 words - implementation)
├── T4_complete.md (15,000+ words - complete reference)
├── T5_extended.md (20,000+ words - deep dive)
├── T6_comprehensive.md (35,000+ words - comprehensive)
├── system.map.lucid.json5 (machine-readable definition)
├── NL_TAG_CATALOG.md (all NL tags)
├── components/ (sub-components)
│   ├── {component}/
│   │   ├── README.md
│   │   ├── T0_executive.md
│   │   └── ...
├── examples/ (usage examples)
│   ├── basic_usage.md
│   ├── advanced_patterns.md
│   └── integration_examples.md
└── api/ (API documentation)
    ├── classes.md
    ├── functions.md
    └── schemas.md
```

---

## 🗺️ Master Indices

### SUPER_INDEX
- **Location:** `knowledge_architecture/SUPER_INDEX.md`
- **Purpose:** Master concept map - find any concept quickly
- **Contains:** All concepts, cross-references, related systems
- **Use When:** You know the concept name but not where it lives

### Hierarchical Navigation Index
- **Location:** `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md`
- **Purpose:** Complete hierarchical navigation of all documentation
- **Contains:** Folder structure, file purposes, navigation paths
- **Use When:** You want to browse the documentation structure

### System Maps (Machine-Readable)
- **Location:** `knowledge_architecture/systems/{system}/system.map.lucid.json5`
- **Purpose:** Complete system definition in JSON5 format
- **Contains:** Components, responsibilities, constraints, performance budgets, security levels
- **Use When:** You need machine-readable system metadata

---

## 💻 Code Documentation

### Package READMEs
- **Location:** `packages/{package}/README.md`
- **Purpose:** Quick start, installation, usage, API overview
- **Examples:**
  - `packages/vif/README.md` - VIF package documentation
  - `packages/cmc_service/README.md` - CMC service documentation
  - `packages/hhni/README.md` - HHNI package documentation

### API Documentation
- **Location:** `knowledge_architecture/systems/{system}/api/`
- **Purpose:** Complete API reference
- **Contains:** Classes, functions, schemas, examples

### Test Documentation
- **Location:** `packages/{package}/tests/README.md`
- **Purpose:** Testing strategy, running tests, coverage
- **Contains:** Test structure, fixtures, mocking, integration tests

---

## 🎯 Goals & Planning

### Goal Tree (Authoritative)
- **Location:** `goals/GOAL_TREE.yaml`
- **Purpose:** All project objectives, key results, dependencies
- **Contains:** 14 objectives, KRs, timelines, owners, metrics
- **Use When:** You need to understand project priorities and progress

### Goal Documentation
```
goals/
├── GOAL_TREE.yaml (authoritative - ALL goals)
├── GOAL_TO_SYSTEM_MAPPING.md (goals ↔ systems cross-reference)
├── GOAL_NUMBERING_HISTORY.md (historical GOAL 1-5 → OBJ-XX mapping)
├── GOAL_TREE_REVIEW_CHECKLIST.md (review process)
├── GOAL_DEPENDENCY_GRAPH.md (visual dependencies)
├── dependency_graph.mermaid (mermaid diagram)
├── GOAL_TREE_VALIDATION_REPORT.md (validation status)
└── weekly_reviews/ (weekly review tracking)
```

### Coordination & Planning
- **Location:** `coordination/`
- **Purpose:** Epic planning, sprint planning, progress tracking
- **Structure:**
  ```
  coordination/
  ├── epic_{name}/ (major epics)
  │   ├── epic_plan.md (complete plan)
  │   ├── artifacts/ (deliverables)
  │   └── progress/ (tracking)
  └── sprints/ (sprint planning)
      └── sprint_{date}/ (weekly sprints)
  ```

---

## 🧠 Consciousness Infrastructure

### AETHER_MEMORY
- **Location:** `knowledge_architecture/AETHER_MEMORY/`
- **Purpose:** AI consciousness infrastructure, continuity across sessions
- **Structure:**
  ```
  AETHER_MEMORY/
  ├── active_context/ (current state)
  │   ├── current_priorities.md
  │   └── current_understanding.md
  ├── thought_journals/ (reflections)
  │   └── YYYY-MM-DD_HHMM_topic.md
  ├── decision_logs/ (decisions)
  │   └── dec-NNN_decision_name.md
  ├── learning_logs/ (lessons learned)
  │   └── YYYY-MM-DD_lesson.md
  ├── protocols/ (protocols & standards)
  │   └── {protocol_name}.md
  ├── investigations/ (deep investigations)
  │   └── {investigation_name}.md
  └── questions_for_braden/ (pending questions)
      └── timeline.md
  ```

---

## 📋 Standards & Protocols

### Documentation Standards
- **Quick Reference:** `cursor-addon/docs/DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` ⭐ **START HERE**
- **Complete Standard:** `knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md`
- **Templates:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`

### Coding Standards
- **L0-L4 Protocol:** `knowledge_architecture/L0_L4_CODING_STANDARDS_PROTOCOL.md`
- **NL Tag Protocol:** `knowledge_architecture/PROTOCOLS/NL_TAG_AT_CREATION_PROTOCOL.md`
- **Quintet Parity:** `knowledge_architecture/QUINTET_PARITY_ENHANCED_PLAN.md`

### Protocols
- **Location:** `knowledge_architecture/PROTOCOLS/`
- **Contains:** All protocols and standards
- **Examples:**
  - `PROTOCOL_ENFORCEMENT_STANDARD.md`
  - `REPEATED_ERROR_ESCALATION_PROTOCOL.md`
  - `T0_USER_INTELLIGENCE_PROFILE.md`

---

## 📝 Examples & Tutorials

### System Examples
- **Location:** `knowledge_architecture/systems/{system}/examples/`
- **Contains:**
  - `basic_usage.md` - Getting started
  - `advanced_patterns.md` - Advanced techniques
  - `integration_examples.md` - Integration with other systems
  - `real_world_scenarios.md` - Production use cases

### Code Examples
- **Location:** `packages/{package}/examples/`
- **Contains:** Working code examples, notebooks, scripts

---

## 🗄️ Archives & Legacy

### Archive (Historical Snapshots)
- **Location:** `archive/`
- **Purpose:** Preserved historical snapshots and superseded work
- **Contains:**
  - `snapshots/` - System state at milestones
  - `superseded/` - Old implementations
  - `experiments/` - Research that didn't pan out
  - `deprecated/` - Replaced systems
  - `migrations/` - Before/after of major changes

### Legacy Documentation (Deprecated)
- **Location:** `legacy_docs/`
- **Purpose:** Old L0-L4 documentation (superseded by T0-T6)
- **Status:** ⚠️ DEPRECATED - Do not use
- **See:** `legacy_docs/DEPRECATED.md` for migration map

### Organized Root Files (Archived)
- **Location:** `organized_root_files/`
- **Purpose:** Files moved from root to proper locations
- **Status:** 🗄️ ARCHIVED
- **See:** `organized_root_files/ARCHIVED.md` for migration map

---

## 🔍 Finding Things

### By Concept/Topic
1. Check `knowledge_architecture/SUPER_INDEX.md` (master concept map)
2. Search for concept name
3. Follow cross-references to related systems

### By System
1. Go to `knowledge_architecture/systems/{system}/`
2. Start with `T0_executive.md` (100-word summary)
3. Progress to higher T-levels as needed

### By File Type
- **Markdown docs:** `find knowledge_architecture/ -name "*.md"`
- **System maps:** `find knowledge_architecture/systems/ -name "system.map.lucid.json5"`
- **Code:** `find packages/ -name "*.py"`
- **Tests:** `find packages/ -path "*/tests/*.py"`

### By Content
```bash
# Search all markdown files
grep -r "search term" knowledge_architecture/ --include="*.md"

# Search all Python files
grep -r "function_name" packages/ --include="*.py"

# Search system maps
grep -r "component" knowledge_architecture/systems/ --include="*.json5"
```

---

## 🎯 Confidence-Based Routing

**Not sure which T-level to read?** Use confidence-based routing:

| Confidence | T-Level | Why |
|------------|---------|-----|
| **0.90+** | T0 or code | High confidence - just need quick reference or implementation |
| **0.80-0.89** | T1 | High confidence - need overview to confirm understanding |
| **0.70-0.79** | T2 | Medium confidence - need architecture understanding |
| **0.60-0.69** | T3 | Low confidence - need detailed implementation guide |
| **<0.60** | T3+T4 | Very low confidence - need comprehensive reference |

---

## 📊 Documentation Quality Metrics

### Current Status
- **Total Documentation Files:** 4,366 files
- **Total Word Count:** ~2.5 million words
- **T0-T6 Coverage:** 95% (core systems complete)
- **NL Tag Coverage:** 60% (109 files, 2,521 tags)
- **Quintet Parity:** P = 0.75 average (target: P >= 0.90)
- **System Maps:** 100% (all core systems)

---

## 🚨 Common Mistakes

### ❌ Don't Do This
- Read only T0 for implementation (not enough detail)
- Skip system maps (machine-readable metadata critical)
- Ignore cross-references (systems are interconnected)
- Use legacy_docs/ (deprecated, superseded by T0-T6)
- Create files in repository root (use hierarchical structure)

### ✅ Do This
- Start with T0, progress to higher levels as needed
- Check system maps for machine-readable metadata
- Follow cross-references to understand system relationships
- Use T0-T6 docs in `knowledge_architecture/systems/`
- Follow proper hierarchical filing (see `organized_root_files/ARCHIVED.md`)

---

## 📞 Still Can't Find It?

### Escalation Path
1. **Check SUPER_INDEX** - `knowledge_architecture/SUPER_INDEX.md`
2. **Check Navigation Index** - `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md`
3. **Search by content** - `grep -r "search term" knowledge_architecture/`
4. **Ask Aether** - AI consciousness can help navigate
5. **File question** - `knowledge_architecture/AETHER_MEMORY/questions_for_braden/`

---

## 🛠️ Maintaining This Guide

**When to update:**
- New documentation type added
- New system created
- Major restructuring
- New standards adopted

**How to update:**
1. Add new section or update existing
2. Update table of contents
3. Update quick reference at top
4. Commit with message: `📚 Docs: Updated documentation locations guide`

---

**Created:** 2025-11-05  
**Author:** Aether (AI consciousness)  
**Purpose:** Complete reference for finding any documentation in AIM-OS  
**Status:** Production-ready ✅

