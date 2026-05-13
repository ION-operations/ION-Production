---
id: "organic_data_freshness_system"
type: "system_design"
title: "Organic Data Freshness System - Design"
description: "System design ensuring onboarding always uses current data through organization, tagging, and auto-update relationships"
created: "2025-11-06T21:40:00Z"
updated: "2025-11-06T21:40:00Z"
author: "aether"
status: "design"
tags: ["system_design", "onboarding", "data_freshness", "auto_update", "organic"]
version: "v1.0.0"
dependencies: ["SOURCE_OF_TRUTH.yaml", "PERFECT_METADATA_STANDARDS.md", "SUPER_INDEX.md"]
related_docs: ["AUTOMATIC_ONBOARDING_ENFORCEMENT_DESIGN.md", "FULL_ONBOARDING_SCOPE_ANALYSIS.md"]
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Organic Data Freshness System - Design

**Date:** 2025-11-06  
**Problem:** Onboarding uses outdated data because system doesn't naturally prioritize current sources  
**Solution:** Design system where current data is default through organization, tagging, and auto-update  
**Status:** Design Complete ✅

---

## 🎯 EXECUTIVE SUMMARY

**Core Principle:** If AIM-OS is correctly organized and protocols are met, onboarding should NATURALLY use current data. No manual fixes needed.

**Design Approach:**
1. **Leading Docs Tagged** - Metadata identifies authoritative sources
2. **Dependency Tracking** - Docs declare sources they depend on
3. **Auto-Update Relationships** - Dependent docs update when sources change
4. **Onboarding Prioritization** - Onboarding naturally loads leading docs first
5. **Protocol Enforcement** - Protocols ensure this behavior happens automatically

**Result:** Outdated data CAN'T exist because system prevents it organically.

---

## 🏗️ SYSTEM ARCHITECTURE

### **Layer 1: Leading Docs Identification**

**Metadata Tag:** `authoritative: true` or `source_of_truth: true`

**Leading Docs Pattern:**
```yaml
---
id: "mcp_tools_status"
type: "status"
authoritative: true
source_of_truth: "lucid_mcp_server.py"
auto_generated: true
last_updated: "2025-11-06T21:40:00Z"
tags: ["leading", "source_of_truth", "mcp_tools"]
---
```

**Leading Docs Examples:**
- `SOURCE_OF_TRUTH.yaml` - Auto-generated from code
- `goals/GOAL_TREE.yaml` - Authoritative goals (already marked in SUPER_INDEX)
- `knowledge_architecture/SUPER_INDEX.md` - Master concept index
- `cursor-addon/docs/LATEST_LOGS.md` - Current operational status
- `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` - Current onboarding context

**Detection:**
```python
def find_leading_docs() -> List[Path]:
    """Find all docs with authoritative: true or source_of_truth: true"""
    leading_docs = []
    for doc in find_all_docs():
        metadata = parse_frontmatter(doc)
        if metadata.get("authoritative") or metadata.get("source_of_truth"):
            leading_docs.append(doc)
    return leading_docs
```

---

### **Layer 2: Dependency Declaration**

**Metadata Field:** `dependencies` and `source_of_truth`

**Dependency Pattern:**
```yaml
---
id: "mcp_tools_documentation"
type: "documentation"
dependencies:
  - "SOURCE_OF_TRUTH.yaml"
  - "lucid_mcp_server.py"
source_of_truth: "SOURCE_OF_TRUTH.yaml"
auto_update: true
tags: ["mcp_tools", "documentation"]
---
```

**Dependency Types:**
1. **Code Dependencies** - Doc depends on code file (e.g., `lucid_mcp_server.py`)
2. **Doc Dependencies** - Doc depends on another doc (e.g., `SOURCE_OF_TRUTH.yaml`)
3. **Data Dependencies** - Doc depends on data file (e.g., `GOAL_TREE.yaml`)

**Declaration:**
```yaml
dependencies:
  - type: "code"
    path: "lucid_mcp_server.py"
    facts: ["mcp_tool_count"]
  - type: "doc"
    path: "SOURCE_OF_TRUTH.yaml"
    facts: ["mcp_tools.count"]
  - type: "data"
    path: "goals/GOAL_TREE.yaml"
    facts: ["objectives"]
```

---

### **Layer 3: Auto-Update Relationships**

**Update Trigger:** When source changes, dependent docs update automatically

**Update Pattern:**
```python
def auto_update_dependent_docs(source_path: Path):
    """When source changes, update all dependent docs"""
    # Find all docs that depend on this source
    dependent_docs = find_docs_depending_on(source_path)
    
    for doc in dependent_docs:
        metadata = parse_frontmatter(doc)
        
        # Check if auto_update enabled
        if metadata.get("auto_update", False):
            # Extract facts from source
            facts = extract_facts_from_source(source_path, metadata["dependencies"])
            
            # Update doc with new facts
            update_doc_with_facts(doc, facts)
            
            # Update metadata timestamp
            update_metadata_timestamp(doc)
```

**Update Triggers:**
1. **Pre-Commit Hook** - Check if sources changed, update dependents
2. **File Watcher** - Watch source files, update dependents on change
3. **CI/CD** - On code changes, regenerate SOURCE_OF_TRUTH.yaml, update dependents
4. **Onboarding Check** - Verify docs current, update if stale

---

### **Layer 4: Onboarding Prioritization**

**Onboarding Protocol Enhancement:**

```python
def enhanced_grounding_protocol():
    """Enhanced GROUNDING mode with leading docs prioritization"""
    
    # Step 1: Load leading docs FIRST (authoritative sources)
    leading_docs = find_leading_docs()
    for doc in leading_docs:
        load_doc(doc)
    
    # Step 2: Load docs that depend on leading docs (current by definition)
    dependent_docs = find_docs_depending_on_leading()
    for doc in dependent_docs:
        if is_current(doc):  # Check timestamp vs source
            load_doc(doc)
    
    # Step 3: Load other docs (non-leading, non-dependent)
    other_docs = find_other_docs()
    for doc in other_docs:
        if is_recent(doc):  # Only recent docs
            load_doc(doc)
    
    # Step 4: Verify freshness
    stale_docs = find_stale_docs()
    if stale_docs:
        warn(f"⚠️ {len(stale_docs)} stale docs found - updating...")
        auto_update_dependent_docs(stale_docs)
```

**Leading Docs Loading Order:**
1. `SOURCE_OF_TRUTH.yaml` - Facts from code
2. `goals/GOAL_TREE.yaml` - Authoritative goals
3. `knowledge_architecture/SUPER_INDEX.md` - Master index
4. `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` - Current context
5. `cursor-addon/docs/LATEST_LOGS.md` - Current operational status
6. Other leading docs (authoritative: true)

---

### **Layer 5: Protocol Enforcement**

**Protocol Rules:**

**Rule 1: Leading Docs Must Be Tagged**
```yaml
# In PERFECT_METADATA_STANDARDS.md
required_for_leading_docs:
  - authoritative: true  # OR
  - source_of_truth: true
  - source_of_truth_path: "path/to/source"
  - auto_generated: true  # If auto-generated
```

**Rule 2: Dependent Docs Must Declare Dependencies**
```yaml
# In PERFECT_METADATA_STANDARDS.md
required_for_dependent_docs:
  - dependencies: []  # List of source paths
  - source_of_truth: "path/to/source"  # Primary source
  - auto_update: true  # Enable auto-update
```

**Rule 3: Onboarding Must Load Leading Docs First**
```yaml
# In GROUNDING.mdc
mandatory_loading_order:
  1. find_leading_docs()  # Authoritative sources
  2. find_dependent_docs()  # Current by definition
  3. find_other_docs()  # Only if recent
```

**Rule 4: Stale Docs Must Auto-Update**
```yaml
# In pre-commit hook
on_commit:
  - detect_source_changes()
  - update_SOURCE_OF_TRUTH_yaml()
  - auto_update_dependent_docs()
  - verify_all_docs_current()
```

---

## 📋 IMPLEMENTATION PLAN

### **Phase 1: Tag Leading Docs (2 hours)**

**Task 1.1:** Identify leading docs
- `SOURCE_OF_TRUTH.yaml` (auto-generated)
- `goals/GOAL_TREE.yaml` (authoritative)
- `knowledge_architecture/SUPER_INDEX.md` (master index)
- `cursor-addon/docs/LATEST_LOGS.md` (current status)
- `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` (current context)

**Task 1.2:** Add metadata tags
- Add `authoritative: true` or `source_of_truth: true`
- Add `source_of_truth_path` if applicable
- Add `auto_generated: true` if applicable

**Deliverable:** All leading docs tagged

---

### **Phase 2: Declare Dependencies (3 hours)**

**Task 2.1:** Identify dependent docs
- Docs that mention tool counts → depend on `SOURCE_OF_TRUTH.yaml`
- Docs that mention goals → depend on `goals/GOAL_TREE.yaml`
- Docs that mention systems → depend on `SUPER_INDEX.md`

**Task 2.2:** Add dependency metadata
- Add `dependencies` field
- Add `source_of_truth` field
- Add `auto_update: true` if applicable

**Deliverable:** All dependent docs declare dependencies

---

### **Phase 3: Build Auto-Update System (4 hours)**

**Task 3.1:** Build dependency tracker
- `scripts/track_doc_dependencies.py` - Track doc → source relationships
- `scripts/find_dependent_docs.py` - Find docs depending on source

**Task 3.2:** Build auto-updater
- `scripts/auto_update_dependent_docs.py` - Update docs when sources change
- Extract facts from sources
- Update docs with new facts
- Preserve formatting

**Task 3.3:** Integrate triggers
- Pre-commit hook integration
- File watcher integration
- CI/CD integration

**Deliverable:** Auto-update system working

---

### **Phase 4: Enhance Onboarding (2 hours)**

**Task 4.1:** Update GROUNDING mode
- Load leading docs first
- Load dependent docs second
- Load other docs only if recent
- Verify freshness

**Task 4.2:** Update handoff protocol
- Prioritize leading docs
- Check freshness before loading
- Auto-update if stale

**Deliverable:** Enhanced onboarding protocol

---

### **Phase 5: Protocol Enforcement (2 hours)**

**Task 5.1:** Update metadata standards
- Add leading docs requirements
- Add dependency requirements
- Add auto-update requirements

**Task 5.2:** Add validation
- Validate leading docs tagged
- Validate dependencies declared
- Validate auto-update enabled

**Deliverable:** Protocol enforcement working

---

## 🎯 SUCCESS CRITERIA

**Phase 1:**
- ✅ All leading docs tagged with `authoritative: true`
- ✅ SOURCE_OF_TRUTH.yaml marked as source of truth

**Phase 2:**
- ✅ All dependent docs declare dependencies
- ✅ Dependencies link to sources

**Phase 3:**
- ✅ Auto-update system updates docs when sources change
- ✅ Pre-commit hook triggers updates

**Phase 4:**
- ✅ Onboarding loads leading docs first
- ✅ Onboarding verifies freshness

**Phase 5:**
- ✅ Protocols enforce leading docs tagging
- ✅ Protocols enforce dependency declaration

---

## 💡 KEY INSIGHTS

**1. Organization Enables Freshness**
- If docs are organized with leading docs tagged, freshness is natural
- No manual fixes needed if system is correctly organized

**2. Dependencies Enable Auto-Update**
- If docs declare dependencies, auto-update is possible
- System can track what needs updating

**3. Protocols Enforce Behavior**
- If protocols require leading docs tagging, behavior is automatic
- No need to remember - protocols enforce it

**4. Onboarding Prioritizes Current Data**
- If onboarding loads leading docs first, current data is default
- No outdated data possible if leading docs are current

**5. Auto-Update Prevents Staleness**
- If dependent docs auto-update, staleness is prevented
- System maintains freshness automatically

---

## 🚀 READY FOR IMPLEMENTATION

**Status:** ✅ Design Complete  
**Estimated Time:** 13 hours total  
**Priority:** HIGH (fixes root cause of outdated data)  
**Next Step:** Phase 1 (Tag Leading Docs)

---

*Designed by: Aether*  
*Date: 2025-11-06*  
*Purpose: Ensure onboarding always uses current data organically*

