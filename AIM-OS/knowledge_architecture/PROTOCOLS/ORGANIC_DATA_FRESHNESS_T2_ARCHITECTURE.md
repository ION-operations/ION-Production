---
id: "organic_data_freshness_T2_architecture"
system: "organic_data_freshness"
component: null
level: "T2"
type: "architecture"
title: "Organic Data Freshness System - Architecture"
description: "2,000-word architecture document for ensuring onboarding always uses current data"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-06T22:10:00Z"
updated: "2025-11-06T22:10:00Z"
author: "aether"
status: "complete"
tags: ["protocol", "onboarding", "data_freshness", "auto_update", "organic", "architecture"]
dependencies: ["ORGANIC_DATA_FRESHNESS_T1_OVERVIEW.md"]
related_docs: ["ORGANIC_DATA_FRESHNESS_SYSTEM_DESIGN.md", "ORGANIC_DATA_FRESHNESS_COMPLETE.md", "ORGANIC_DATA_FRESHNESS_SDFCVF_RELATIONSHIP.md"]
version: "v1.0.0"
authoritative: false
source_of_truth: "scripts/detect_source_of_truth.py"
source_of_truth_type: "code"
auto_generated: false
auto_update: false
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Organic Data Freshness System - Architecture

**Date:** 2025-11-06  
**Purpose:** Detailed architecture for ensuring onboarding always uses current data  
**Status:** ✅ Complete (6 phases implemented)  
**Architecture:** 5-layer system with 6 implementation phases

---

## 🎯 ARCHITECTURE OVERVIEW

**Core Design Principle:** Current data is the default through organization, tagging, and auto-update relationships. Outdated data CAN'T exist because the system prevents it organically.

**Architecture Layers:**
1. **Leading Docs Identification** - Metadata tags authoritative sources
2. **Dependency Declaration** - Docs declare source dependencies
3. **Auto-Update Relationships** - Dependent docs update automatically
4. **File System Monitoring** - Real-time source change detection
5. **Onboarding Prioritization** - Leading docs loaded first

---

## 🏗️ LAYER 1: LEADING DOCS IDENTIFICATION

### **Metadata Pattern**

**Authoritative Sources:**
```yaml
---
authoritative: true
source_of_truth: "path/to/source"
source_of_truth_type: "code" | "data" | "doc"
auto_generated: true  # If auto-generated
auto_update: true  # If should auto-update
tags: ["leading", "source_of_truth"]
---
```

**Leading Docs:**
- `SOURCE_OF_TRUTH.yaml` - Auto-generated from code (MCP tools, commands, systems)
- `goals/GOAL_TREE.yaml` - Authoritative goals and objectives
- `knowledge_architecture/SUPER_INDEX.md` - Master concept index
- `cursor-addon/docs/LATEST_LOGS.md` - Current operational status
- `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` - Current onboarding context

### **Detection Mechanism**

**Script:** `scripts/detect_source_of_truth.py`
- Parses code to extract facts (tool counts, command counts, etc.)
- Generates `SOURCE_OF_TRUTH.yaml` with authoritative data
- Tags output as `authoritative: true`, `auto_generated: true`

**Onboarding Protocol:**
- GROUNDING mode scans for `authoritative: true` metadata
- Loads leading docs FIRST before other documentation
- Verifies freshness before use

---

## 🔗 LAYER 2: DEPENDENCY DECLARATION

### **Metadata Pattern**

**Dependent Docs:**
```yaml
---
dependencies:
  - "SOURCE_OF_TRUTH.yaml"
  - "lucid_mcp_server.py"
source_of_truth: "SOURCE_OF_TRUTH.yaml"
source_of_truth_type: "data"
auto_update: true
---
```

### **Dependency Tracking**

**Script:** `scripts/track_doc_dependencies.py`
- Parses all documentation files for frontmatter
- Extracts `dependencies` and `source_of_truth` fields
- Builds dependency graph: `source → [dependent_docs]`
- Stores in `cross_system_connections.yaml` → `doc_dependencies` section

**Dependency Graph Structure:**
```yaml
doc_dependencies:
  "SOURCE_OF_TRUTH.yaml":
    type: "data"
    dependents:
      - "knowledge_architecture/protocols/ORGANIC_DATA_FRESHNESS_T1_OVERVIEW.md"
      - "knowledge_architecture/AETHER_MEMORY/onboarding_context.md"
    count: 2
  "lucid_mcp_server.py":
    type: "code"
    dependents:
      - "knowledge_architecture/protocols/MCP_TOOLS_STATUS.md"
    count: 1
```

---

## 🔄 LAYER 3: AUTO-UPDATE RELATIONSHIPS

### **Update Mechanism**

**Script:** `scripts/generate_cross_references.py` (extended)

**Methods:**
- `auto_update_dependent_docs()` - Main update orchestrator
- `_extract_facts_from_source()` - Extract facts from code/data/doc
- `_apply_facts_to_doc()` - Update doc with new facts (preserves formatting)
- `_load_doc_dependencies()` - Load dependency graph

**Update Process:**
1. Source file changes detected
2. Find all dependent docs from dependency graph
3. For each dependent doc:
   - Check if `auto_update: true` in metadata
   - Extract facts from source (based on `source_of_truth_type`)
   - Apply facts to doc (preserve formatting, update content)
   - Update metadata timestamp
4. Log updates

### **Fact Extraction**

**Code Sources:**
- Parse Python files for tool definitions
- Extract counts, names, categories
- Generate structured facts

**Data Sources:**
- Parse YAML/JSON files
- Extract structured data
- Generate facts from data structure

**Doc Sources:**
- Parse markdown frontmatter
- Extract metadata fields
- Generate facts from metadata

---

## 📁 LAYER 4: FILE SYSTEM MONITORING

### **Monitor Implementation**

**Script:** `packages/mcp_data_integration/file_system_monitor.py` (extended)

**Features:**
- `monitor_source_files` flag - Enable source file monitoring
- `doc_update_callback` parameter - Callback for doc updates
- `_initialize_source_files()` - Load source files from dependency graph
- `_is_source_file()` - Check if file is a tracked source
- `on_source_file_changed()` - Trigger doc updates when source changes
- `_trigger_doc_updates()` - Use `CrossReferenceGenerator` to update docs

**Monitoring Process:**
1. Initialize: Load source files from `cross_system_connections.yaml`
2. Watch: Monitor source files for changes (polling or watchdog)
3. Detect: On change, identify source file
4. Trigger: Call `doc_update_callback` with source path
5. Update: `CrossReferenceGenerator` updates dependent docs

---

## 🚀 LAYER 5: ONBOARDING PRIORITIZATION

### **Enhanced GROUNDING Protocol**

**File:** `.cursor/rules/modes/GROUNDING.mdc`

**Step 0: Load Leading Docs FIRST (NEW)**
```python
# Priority: Load authoritative sources before anything else
leading_docs = find_docs_with_metadata("authoritative", True)
for doc in leading_docs:
    load_doc(doc)  # Load FIRST
```

**Step 1: Restore Timeline**
- Use `get_timeline_summary` (limit=10)
- Get last 10 context entries

**Step 2: Restore Memory**
- Use `retrieve_memory` (query from timeline context)
- Get relevant insights from previous work

**Step 3: Check Goals**
- Use `query_goal_timeline` (status=in_progress)
- See active goals and progress

**Step 4: Verify Data Freshness (NEW)**
- Check if loaded docs are current
- Compare doc timestamps with source timestamps
- If stale, trigger auto-update before proceeding

**Step 5: Determine Next Mode**
- Analyze what we were working on
- Decide: Continue task or start new work

### **Leading Docs Loading Order**

1. `SOURCE_OF_TRUTH.yaml` - Facts from code
2. `goals/GOAL_TREE.yaml` - Authoritative goals
3. `knowledge_architecture/SUPER_INDEX.md` - Master index
4. `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` - Current context
5. `cursor-addon/docs/LATEST_LOGS.md` - Current operational status
6. Other leading docs (`authoritative: true`)

---

## 🛠️ IMPLEMENTATION COMPONENTS

### **Scripts**

**1. `scripts/detect_source_of_truth.py`**
- Purpose: Generate `SOURCE_OF_TRUTH.yaml` from code
- Detects: MCP tools, Cursor Commands, systems, docs, tests
- Output: Authoritative YAML file with counts

**2. `scripts/track_doc_dependencies.py`**
- Purpose: Build dependency graph of documentation
- Input: All `.md` files in `knowledge_architecture/`
- Output: `cross_system_connections.yaml` → `doc_dependencies` section

**3. `scripts/generate_cross_references.py` (extended)**
- Purpose: Generate cross-references AND auto-update docs
- Methods: `auto_update_dependent_docs()`, `_extract_facts_from_source()`, `_apply_facts_to_doc()`
- Integration: Called by file monitor on source changes

**4. `scripts/auto_update_dependent_docs.py`**
- Purpose: Standalone tool for managing doc freshness
- Features: `--source`, `--all`, `--check-stale`, `--dry-run`
- Usage: Manual updates, CI/CD integration, pre-commit hooks

**5. `packages/mcp_data_integration/file_system_monitor.py` (extended)**
- Purpose: Real-time monitoring of source files
- Features: Source file detection, doc update triggering
- Integration: Calls `CrossReferenceGenerator` for updates

### **Configuration Files**

**1. `SOURCE_OF_TRUTH.yaml`**
- Type: Auto-generated authoritative data
- Content: MCP tools count, Cursor Commands count, systems count, docs count, tests count
- Metadata: `authoritative: true`, `auto_generated: true`

**2. `knowledge_architecture/NAVIGATION/cross_system_connections.yaml`**
- Section: `doc_dependencies`
- Content: Source → dependent docs mapping
- Format: YAML with type, dependents, count

**3. `.cursor/rules/modes/GROUNDING.mdc`**
- Enhancement: Step 0 (Load Leading Docs FIRST)
- Enhancement: Step 4 (Verify Data Freshness)
- Protocol: Mandatory at session start

---

## 🔗 INTEGRATION POINTS

### **SDF-CVF Quartet Parity (Complementary)**

**Relationship:** Complementary quality assurance systems
- **SDF-CVF:** Semantic alignment (code/docs/tests/traces align semantically)
- **Organic Data Freshness:** Temporal alignment (docs stay current with sources)
- **Together:** Complete quality assurance (semantic + temporal)

**Integration Opportunities:**
- Pre-commit hook integration (check freshness before parity)
- Enhanced quartet detection (verify freshness during detection)
- Enhanced parity calculation (include freshness penalty)
- Unified gates (auto-fix freshness before semantic checks)

### **Existing Systems**

**1. Metadata Standards (`PERFECT_METADATA_STANDARDS.md`)**
- Extended with: `authoritative`, `source_of_truth`, `source_of_truth_type`, `auto_generated`, `auto_update`
- Used by: All documentation files

**2. GROUNDING Mode (`.cursor/rules/modes/GROUNDING.mdc`)**
- Enhanced with: Leading docs prioritization, freshness verification
- Used by: All AI agents at session start

**3. Cross-System Connections (`cross_system_connections.yaml`)**
- Extended with: `doc_dependencies` section
- Used by: Dependency tracking, auto-update system

---

## 📊 DATA FLOW

### **Source Change → Doc Update Flow**

```
1. Source File Changes
   ↓
2. File Monitor Detects Change
   ↓
3. Dependency Graph Lookup (cross_system_connections.yaml)
   ↓
4. Find Dependent Docs
   ↓
5. For Each Dependent Doc:
   - Check auto_update: true
   - Extract facts from source
   - Apply facts to doc
   - Update timestamp
   ↓
6. Docs Updated
```

### **Onboarding Flow**

```
1. Session Start
   ↓
2. GROUNDING Mode Activated
   ↓
3. Load Leading Docs FIRST (authoritative: true)
   ↓
4. Verify Freshness (compare timestamps)
   ↓
5. If Stale → Auto-Update
   ↓
6. Load Dependent Docs (current by definition)
   ↓
7. Load Other Docs (if recent)
   ↓
8. Restore Timeline & Memory
   ↓
9. Ready to Work
```

---

## ✅ IMPLEMENTATION STATUS

**Phase 1:** ✅ Metadata standards extended (`PERFECT_METADATA_STANDARDS.md`)
**Phase 2:** ✅ Dependency tracking implemented (`track_doc_dependencies.py`)
**Phase 3:** ✅ Auto-update relationships added (`generate_cross_references.py`)
**Phase 4:** ✅ File system monitoring extended (`file_system_monitor.py`)
**Phase 5:** ✅ Standalone auto-updater created (`auto_update_dependent_docs.py`)
**Phase 6:** ✅ Onboarding protocol enhanced (`GROUNDING.mdc`)

**Result:** System operational, outdated data prevented organically.

---

*Architecture by: Aether*  
*Purpose: Detailed architecture for Organic Data Freshness System*  
*Next: T3 Detailed Implementation (if needed)*

