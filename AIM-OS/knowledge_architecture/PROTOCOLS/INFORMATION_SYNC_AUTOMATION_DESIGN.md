---
id: "information_sync_automation_design"
type: "automation_design"
title: "Information Sync Automation System - Design & Implementation"
description: "Comprehensive automation system for keeping documentation in sync with code automatically"
created: "2025-11-06T21:35:00Z"
updated: "2025-11-06T21:35:00Z"
author: "aether"
status: "design_complete"
tags: ["automation", "documentation_sync", "source_of_truth", "information_decay"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Information Sync Automation System - Design & Implementation

**Date:** 2025-11-06  
**Problem:** Documentation shows 59 tools, code has 81 tools - information decays  
**Solution:** Automatic sync system that detects code changes and updates docs  
**Status:** Design Complete ✅ - Ready for Implementation

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** Information becomes outdated because:
- Code changes (81 tools) but docs don't update (still say 59)
- No automatic sync mechanism
- Multiple sources of truth conflict
- Manual updates forgotten

**Solution:** 5-layer automation system:
1. **Source of Truth Detection** - Extract facts from code automatically
2. **Documentation Validation** - Compare docs to source of truth
3. **Automatic Update Generation** - Generate doc updates automatically
4. **Organic Update Triggers** - Pre-commit hooks, CI/CD, onboarding checks
5. **Single Source of Truth File** - `SOURCE_OF_TRUTH.yaml` as master reference

**Impact:** Zero manual updates needed, docs always accurate

---

## 📊 CURRENT STATE ANALYSIS

### **Existing Automation (What We Have)**

**✅ Tag Catalog Generator** (`scripts/generate_tag_catalog.py`)
- Scans code for NL tags
- Generates catalogs automatically
- **Works:** ✅

**✅ README Updater** (`scripts/update_readmes_with_tag_info.py`)
- Updates READMEs with tag info
- **Works:** ✅

**✅ Tag Reference Validator** (`scripts/validate_tag_references.py`)
- Validates tag references in docs
- **Works:** ✅

**✅ MCP Tools Verifier** (`scripts/verify_mcp_tools.py`)
- Tests MCP tools
- **Missing:** Tool count detection

### **Missing Automation (What We Need)**

**❌ MCP Tool Count Detector**
- Extract tool count from `lucid_mcp_server.py`
- Update docs automatically

**❌ Source of Truth Generator**
- Create `SOURCE_OF_TRUTH.yaml` from code
- Single master reference

**❌ Documentation Sync Validator**
- Compare docs to source of truth
- Report mismatches

**❌ Automatic Doc Updater**
- Update docs when code changes
- Pre-commit hook integration

**❌ Onboarding Check**
- Verify docs current during onboarding
- Alert if outdated

---

## 🏗️ ARCHITECTURE DESIGN

### **Layer 1: Source of Truth Detection**

**Script:** `scripts/detect_source_of_truth.py`

**Functionality:**
```python
"""
Detect source of truth from code

Scans codebase for facts:
- MCP tool count (from lucid_mcp_server.py)
- Cursor command count (from .cursor/commands/)
- System count (from packages/)
- Documentation file count
- Test count
- etc.
"""

def detect_mcp_tool_count() -> int:
    """Extract MCP tool count from lucid_mcp_server.py"""
    # Parse @tool decorators
    # Count unique tool functions
    # Return count

def detect_cursor_command_count() -> int:
    """Count Cursor commands"""
    # Scan .cursor/commands/*.md
    # Return count

def generate_source_of_truth() -> Dict:
    """Generate SOURCE_OF_TRUTH.yaml"""
    return {
        "mcp_tools": {
            "count": detect_mcp_tool_count(),
            "source": "lucid_mcp_server.py",
            "last_updated": datetime.now().isoformat()
        },
        "cursor_commands": {
            "count": detect_cursor_command_count(),
            "source": ".cursor/commands/",
            "last_updated": datetime.now().isoformat()
        },
        # ... more facts
    }
```

**Output:** `SOURCE_OF_TRUTH.yaml`

---

### **Layer 2: Documentation Validation**

**Script:** `scripts/validate_docs_against_source.py`

**Functionality:**
```python
"""
Validate documentation against source of truth

Scans docs for claims (e.g., "59 tools") and compares to SOURCE_OF_TRUTH.yaml
"""

def find_claims_in_docs() -> List[Claim]:
    """Find numeric claims in documentation"""
    # Scan markdown files
    # Find patterns like "59 tools", "81 MCP tools"
    # Extract claim + file + line

def validate_claims(claims: List[Claim], source: Dict) -> List[Mismatch]:
    """Compare claims to source of truth"""
    mismatches = []
    for claim in claims:
        if claim.type == "mcp_tool_count":
            if claim.value != source["mcp_tools"]["count"]:
                mismatches.append(Mismatch(claim, source["mcp_tools"]["count"]))
    return mismatches

def generate_report(mismatches: List[Mismatch]) -> str:
    """Generate validation report"""
    # Markdown report with:
    # - Files with outdated claims
    # - Current vs claimed values
    # - Suggested fixes
```

**Output:** Validation report + list of files to update

---

### **Layer 3: Automatic Update Generation**

**Script:** `scripts/auto_update_docs.py`

**Functionality:**
```python
"""
Automatically update documentation

Reads validation report and updates docs automatically
"""

def update_doc_claims(file_path: str, mismatches: List[Mismatch]) -> str:
    """Update outdated claims in a doc file"""
    # Read file
    # Replace outdated claims with correct values
    # Preserve formatting
    # Return updated content

def generate_updates(source: Dict, mismatches: List[Mismatch]) -> List[Update]:
    """Generate list of doc updates needed"""
    updates = []
    for mismatch in mismatches:
        updates.append(Update(
            file=mismatch.file,
            line=mismatch.line,
            old_value=mismatch.claimed_value,
            new_value=mismatch.correct_value
        ))
    return updates

def apply_updates(updates: List[Update], dry_run: bool = False):
    """Apply updates to docs"""
    for update in updates:
        if dry_run:
            print(f"Would update {update.file}:{update.line}")
        else:
            update_file(update.file, update.line, update.new_value)
```

**Output:** Updated documentation files

---

### **Layer 4: Organic Update Triggers**

**Pre-Commit Hook:** `.git/hooks/pre-commit`

**Functionality:**
```bash
#!/bin/bash
# Pre-commit hook: Validate docs before commit

# Detect source of truth
python scripts/detect_source_of_truth.py

# Validate docs
python scripts/validate_docs_against_source.py

# If mismatches found:
# - Option 1: Auto-fix and commit
# - Option 2: Block commit and show report
# - Option 3: Warn but allow commit
```

**CI/CD Integration:** `.github/workflows/doc-sync.yml`

**Functionality:**
```yaml
name: Documentation Sync Validation

on:
  push:
    paths:
      - 'lucid_mcp_server.py'
      - '.cursor/commands/**'
      - 'packages/**'

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Detect Source of Truth
        run: python scripts/detect_source_of_truth.py
      - name: Validate Documentation
        run: python scripts/validate_docs_against_source.py
      - name: Auto-Update Docs
        run: python scripts/auto_update_docs.py --auto-fix
      - name: Create PR
        # Create PR with doc updates
```

**Onboarding Check:** Enhanced GROUNDING mode

**Functionality:**
```python
# In GROUNDING mode protocol:
def check_doc_freshness():
    """Check if docs are current during onboarding"""
    source = load_source_of_truth()
    mismatches = validate_docs_against_source()
    if mismatches:
        warn_user(f"⚠️ {len(mismatches)} outdated claims found in docs")
        suggest_update()
```

---

### **Layer 5: Single Source of Truth File**

**File:** `SOURCE_OF_TRUTH.yaml`

**Structure:**
```yaml
# AIM-OS Source of Truth
# Auto-generated from code - DO NOT EDIT MANUALLY
# Last updated: 2025-11-06T21:35:00Z

mcp_tools:
  count: 81
  source: "lucid_mcp_server.py"
  detection_method: "@tool decorator count"
  last_updated: "2025-11-06T21:35:00Z"
  categories:
    core_aimos: 6
    scor: 3
    snapshot: 4
    timeline: 3
    goal_timeline: 3
    # ... more categories

cursor_commands:
  count: 15
  source: ".cursor/commands/"
  detection_method: "*.md file count"
  last_updated: "2025-11-06T21:35:00Z"

systems:
  count: 9
  source: "packages/"
  detection_method: "package count"
  last_updated: "2025-11-06T21:35:00Z"
  list:
    - cmc
    - hhni
    - vif
    # ... more systems

documentation:
  total_files: 1200
  t_level_docs: 45
  l_level_docs: 200
  last_updated: "2025-11-06T21:35:00Z"

tests:
  total: 1442
  passing: 1442
  coverage: 0.85
  last_updated: "2025-11-06T21:35:00Z"
```

**Usage:**
- Onboarding: Load SOURCE_OF_TRUTH.yaml first
- Validation: Compare docs to SOURCE_OF_TRUTH.yaml
- Updates: Update SOURCE_OF_TRUTH.yaml when code changes
- Documentation: Reference SOURCE_OF_TRUTH.yaml in docs

---

## 🔧 IMPLEMENTATION PLAN

### **Phase 1: Source of Truth Detection (2 hours)**

**Task 1.1:** Build `detect_source_of_truth.py`
- Extract MCP tool count from `lucid_mcp_server.py`
- Extract Cursor command count
- Extract system count
- Generate `SOURCE_OF_TRUTH.yaml`

**Task 1.2:** Test detection accuracy
- Verify tool count matches reality (81)
- Verify command count matches reality
- Verify system count matches reality

**Deliverable:** `SOURCE_OF_TRUTH.yaml` auto-generated

---

### **Phase 2: Documentation Validation (2 hours)**

**Task 2.1:** Build `validate_docs_against_source.py`
- Scan docs for numeric claims
- Compare to SOURCE_OF_TRUTH.yaml
- Generate mismatch report

**Task 2.2:** Test validation
- Find all outdated claims
- Verify report accuracy

**Deliverable:** Validation report showing mismatches

---

### **Phase 3: Automatic Update Generation (3 hours)**

**Task 3.1:** Build `auto_update_docs.py`
- Read validation report
- Update doc files automatically
- Preserve formatting

**Task 3.2:** Test updates
- Verify updates are correct
- Verify formatting preserved
- Test dry-run mode

**Deliverable:** Auto-update script working

---

### **Phase 4: Organic Triggers (2 hours)**

**Task 4.1:** Pre-commit hook
- Integrate validation into git hooks
- Auto-fix or warn on commit

**Task 4.2:** CI/CD integration
- GitHub Actions workflow
- Auto-update docs on code changes

**Task 4.3:** Onboarding check
- Enhanced GROUNDING mode
- Check doc freshness during onboarding

**Deliverable:** Automatic triggers working

---

### **Phase 5: Testing & Refinement (1 hour)**

**Task 5.1:** End-to-end test
- Change code (add tool)
- Run detection
- Run validation
- Run update
- Verify docs updated

**Task 5.2:** Documentation
- Document automation system
- Update onboarding protocols
- Create usage guide

**Deliverable:** Complete automation system

---

## 📋 SUCCESS CRITERIA

**Phase 1:**
- ✅ SOURCE_OF_TRUTH.yaml generated automatically
- ✅ Tool count accurate (81)
- ✅ Command count accurate
- ✅ System count accurate

**Phase 2:**
- ✅ All outdated claims found
- ✅ Validation report accurate
- ✅ Mismatches clearly identified

**Phase 3:**
- ✅ Docs update automatically
- ✅ Formatting preserved
- ✅ Updates correct

**Phase 4:**
- ✅ Pre-commit hook works
- ✅ CI/CD integration works
- ✅ Onboarding check works

**Phase 5:**
- ✅ End-to-end test passes
- ✅ Documentation complete
- ✅ System production-ready

---

## 🎯 USAGE EXAMPLES

### **Manual Run:**
```bash
# Detect source of truth
python scripts/detect_source_of_truth.py

# Validate docs
python scripts/validate_docs_against_source.py

# Auto-update docs
python scripts/auto_update_docs.py --auto-fix
```

### **Pre-Commit Hook:**
```bash
# Automatically runs before commit
# Validates docs and warns if outdated
```

### **CI/CD:**
```yaml
# Automatically runs on code changes
# Updates docs and creates PR
```

### **Onboarding:**
```python
# Automatically checks during GROUNDING mode
# Warns if docs outdated
```

---

## 💡 FUTURE ENHANCEMENTS

**1. Multi-Fact Detection**
- Detect more facts (test counts, coverage, etc.)
- Expand SOURCE_OF_TRUTH.yaml

**2. Smart Claim Detection**
- Use NLP to find claims in prose
- Not just numeric patterns

**3. Historical Tracking**
- Track how facts change over time
- Show trends in SOURCE_OF_TRUTH.yaml

**4. Documentation Generation**
- Auto-generate docs from SOURCE_OF_TRUTH.yaml
- Keep docs in sync automatically

---

## 🚀 READY FOR IMPLEMENTATION

**Status:** ✅ Design Complete  
**Estimated Time:** 10 hours total  
**Priority:** HIGH (fixes information decay)  
**Next Step:** Build Phase 1 (Source of Truth Detection)

---

*Designed by: Aether*  
*Date: 2025-11-06*  
*Purpose: Fix information decay through automation*

