---
id: "pre_commit_hook_guide"
system: "sdfcvf"
component: "quintet_parity"
type: "developer_guide"
title: "Pre-Commit Hook Guide - NL Tag Enforcement"
description: "Complete guide to the quintet parity pre-commit hook"
created: "2025-11-04T06:50:00Z"
status: "production_ready"
---

# Pre-Commit Hook Guide

**Purpose:** Understand and work with the quintet parity pre-commit hook  
**Location:** `.git/hooks/pre-commit`  
**Status:** Active and enforcing

---

## 🎯 **What Does It Do?**

The pre-commit hook automatically validates quintet parity on all staged Python files **before allowing commits**.

**Checks:**
1. **Coverage:** >= 95% public API, >= 75% internal
2. **Quintet Parity:** P >= 0.90
3. **Composite Metric:** code↔tags >= 0.85
4. **Anti-Gaming:** No boilerplate, no duplicate IDs
5. **CONNECT Validation:** All edges verified via callgraph

**Performance Budget:** < 500ms (fast feedback)

---

## ✅ **Successful Commit (Everything Passes)**

```bash
$ git add packages/vif/new_feature.py
$ git commit -m "Added new VIF feature"

🔍 Running quintet parity check...
📄 Checking 1 staged Python file(s)...
✅ Quintet parity passed (P=0.92, 145ms)

[main abc1234] Added new VIF feature
 1 file changed, 50 insertions(+)
```

**What happened:**
- Hook detected 1 staged Python file
- Ran quintet parity validation
- All checks passed (P=0.92 >= 0.90)
- Commit allowed
- Fast (145ms < 500ms budget)

---

## ❌ **Failed Commit (Violations Detected)**

```bash
$ git add packages/vif/untagged_file.py
$ git commit -m "Oops forgot tags"

🔍 Running quintet parity check...
📄 Checking 1 staged Python file(s)...

============================================================
❌ QUINTET PARITY CHECK FAILED
============================================================

Quintet Parity Analysis Report
------------------------------------------------------------
Quintet detected: Yes (5 elements present)

Pairwise Similarities:
  code_docs     0.82    [OK]
  code_tests    0.80    [OK]
  code_traces   0.75    [WARN]
  code_tags     0.45    [FAIL]  ← TOO LOW!
    Breakdown: Composite: 0.45 (sig:0.00, name:0.75, doc:0.00, spec:1.00)
  docs_tests    0.88    [OK]
  docs_traces   0.76    [OK]
  docs_tags     0.70    [WARN]
  tests_traces  0.72    [WARN]
  tests_tags    0.68    [WARN]
  traces_tags   0.65    [WARN]

Overall: P_quintet = 0.721  [BELOW 0.90]

============================================================
GATE RESULT:
============================================================

❌ Gate: nl_tags FAILED

Issues:
  - Public API coverage 45.5% < 95.0%
  - Code-tags alignment 0.45 < 0.85
  -   Breakdown: Composite: 0.45 (sig:0.00, name:0.75, doc:0.00, spec:1.00)

============================================================
COMMIT BLOCKED
============================================================

Fix the issues above and try again.
Or bypass with: git commit --no-verify (not recommended)

❌ Quintet parity check failed
```

**What happened:**
- Hook detected issues (low coverage, low parity)
- Showed detailed diagnostic
- **Blocked the commit**
- You must fix issues before committing

---

## 🔧 **How to Fix Failures**

### **Issue 1: Low Coverage**

```
Issues:
  - Public API coverage 45.5% < 95.0%
```

**What it means:** Less than 95% of public functions are tagged

**How to fix:**
```bash
# Option 1: Auto-tag the file
python scripts/vif_auto_tagger.py packages/vif/untagged_file.py

# Option 2: Use LLM assistant
python -c "
from packages.nl_tags.llm_assisted_tagger import LLMAssistedTagger
# ... generate tags
"

# Option 3: Tag manually
# Add # NL_TAG comments above each function

# Then stage the tagged version
git add packages/vif/untagged_file_TAGGED.py

# Try commit again
git commit -m "Added feature with NL tags"
```

---

### **Issue 2: Low Parity Score**

```
Overall: P_quintet = 0.721  [BELOW 0.90]
```

**What it means:** Semantic alignment is below threshold

**Common causes:**
- Signature mismatch (sig:0.00)
- Generic descriptions (doc:0.00)
- Wrong categories (name:0.75)

**How to fix:**

**1. Fix Signature Mismatch (sig:0.00):**
```python
# BEFORE (wrong)
# NL_TAG: VIF-001 | Description | create_witness() | []
def create_witness(operation, inputs, outputs):

# AFTER (correct)
# NL_TAG: VIF-001 | Description | create_witness(operation, inputs, outputs) | []
def create_witness(operation, inputs, outputs):
```

**2. Improve Descriptions (doc:0.00):**
```python
# BEFORE (generic)
# NL_TAG: VIF-001 | Helper function | ...

# AFTER (specific)
# NL_TAG: VIF-001 | Create VIF witness envelope with complete provenance | ...
```

**3. Fix Categories (name:0.75):**
```python
# BEFORE (wrong category)
# NL_TAG: VIF-UTIL-001 | Create witness | ...
def create_witness(...):

# AFTER (correct category)
# NL_TAG: VIF-WITNESS-001 | Create witness | ...
def create_witness(...):
```

**Re-validate:**
```bash
python scripts/validate_tagged_file.py packages/vif/file.py
# Should now show P >= 0.90
```

---

### **Issue 3: Boilerplate Detected**

```
Warnings:
  - Boilerplate detected: "Generic function" (appears 8 times)
```

**What it means:** Same description used multiple times (lazy tagging)

**How to fix:**
Make each description unique and specific:

```python
# BEFORE (boilerplate)
# NL_TAG: VIF-001 | Helper function | func1() | []
# NL_TAG: VIF-002 | Helper function | func2() | []

# AFTER (unique)
# NL_TAG: VIF-001 | Validate witness schema against v1.0 spec | validate_witness(...) | []
# NL_TAG: VIF-002 | Calculate confidence score using Bayesian inference | calc_confidence(...) | []
```

---

### **Issue 4: Duplicate Tag IDs**

```
Issues:
  - Duplicate ID: VIF-WITNESS-001 appears 2 times
```

**What it means:** Same tag ID used in multiple places

**How to fix:**
```python
# Use unique counters
# VIF-WITNESS-001 (first witness tag)
# VIF-WITNESS-002 (second witness tag)
# VIF-WITNESS-003 (third witness tag)

# Auto-tagger handles this automatically
```

---

## ⚡ **Performance**

### **Performance Budget: < 500ms**

The hook is designed to be **fast** (< 500ms for typical commits).

**What it does for speed:**
- Only checks **staged files** (not entire codebase)
- Uses **embedding cache** (re-uses previous embeddings)
- **Incremental analysis** (only changed files)
- **Optimized algorithms**

**Typical performance:**
- 1 file: ~100-200ms
- 5 files: ~300-400ms
- 10 files: ~450-500ms

**If slow (> 500ms):**
- Check embedding cache is working
- Check not analyzing too many files
- Consider splitting large commits

---

## 🚨 **Emergency: Bypass Hook**

### **When to Bypass:**
- **Emergency fix** (production down, need quick patch)
- **WIP commit** (work-in-progress, will fix tags later)
- **Non-code files** (hook incorrectly triggered)

### **How to Bypass:**

```bash
git commit --no-verify -m "Emergency fix"
```

**⚠️ WARNING:** This bypasses all checks!

**Use responsibly:**
- Only for genuine emergencies
- Fix tags before final merge
- Don't make a habit of bypassing

---

## 🔍 **Understanding Diagnostic Output**

### **Section 1: Detection**
```
Detection:
  Code symbols: 11
  NL tags: 11
```

**What it means:**
- Found 11 functions/classes in code
- Found 11 NL tags
- Coverage is 100% (11/11)

---

### **Section 2: Pairwise Similarities**
```
Pairwise Similarities:
  code_docs     0.85    [OK]
  code_tests    0.80    [OK]
  code_tags     0.88    [OK]  ← Most important!
  ...
```

**What it means:**
- Each pair is compared for semantic similarity
- `code_tags` is most critical (composite metric)
- All should be >= thresholds

**Status indicators:**
- `[OK]` - Above threshold ✅
- `[WARN]` - Close to threshold ⚠️
- `[FAIL]` - Below threshold ❌

---

### **Section 3: Composite Breakdown**
```
code <-> tags Breakdown:
  Composite: 0.88 (sig:0.95, name:0.85, doc:0.82, spec:1.00)
```

**What each means:**
- **sig:0.95** - Signature similarity (structural match)
- **name:0.85** - Name similarity (semantic alignment)
- **doc:0.82** - Documentation similarity (docstring match)
- **spec:1.00** - SPEC validation compliance

**Composite = weighted average** (0.4×sig + 0.3×name + 0.2×doc + 0.1×spec)

**Target:** All >= thresholds, composite >= 0.85

---

### **Section 4: Issues & Warnings**
```
Issues:
  - Public API coverage 45.5% < 95.0%

Warnings:
  - Boilerplate detected: "Generic function"
```

**Issues:** Must fix (commit blocked)  
**Warnings:** Should fix (commit allowed but quality suffers)

---

## 🎯 **Best Practices**

### **1. Tag Before Committing**

**Don't:**
```bash
# Write code
# Commit without tags
git commit  # BLOCKED!
# Scramble to add tags
```

**Do:**
```bash
# Write code
# Add tags (LLM assistant or auto-tagger)
# Validate
python scripts/validate_tagged_file.py file.py
# Commit
git commit  # PASSES!
```

---

### **2. Use Automation**

**LLM Assistant (< 1 sec):**
```python
from packages.nl_tags.llm_assisted_tagger import LLMAssistedTagger
tagger = LLMAssistedTagger()
suggestions = tagger.generate_tags(code, system="vif")
```

**Auto-Tagger (2 min):**
```bash
python scripts/vif_auto_tagger.py packages/vif/file.py
```

**Both give you 80-90% of the work done!**

---

### **3. Validate Before Committing**

```bash
# Always validate first
python scripts/validate_tagged_file.py packages/vif/file.py

# If P >= 0.90, commit
git commit -m "Added feature"

# If P < 0.90, fix issues first
```

**Saves time:** Fix issues before pre-commit hook catches them

---

### **4. Keep Commits Small**

**Better:**
- Small, focused commits (1-3 files)
- Fast pre-commit validation (< 200ms)
- Easy to fix if issues

**Worse:**
- Large commits (20+ files)
- Slow pre-commit validation (> 500ms)
- Hard to debug if multiple files have issues

---

## 📖 **Troubleshooting**

### **Problem: "Hook not found" or "Hook not executing"**

**Solution:**
```bash
# Check if hook exists
ls -la .git/hooks/pre-commit

# If not, copy template
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit

# Make executable (Linux/Mac)
chmod +x .git/hooks/pre-commit

# On Windows, should work without chmod
```

---

### **Problem: "Module not found" errors**

**Solution:**
```bash
# Hook needs Python packages
# Ensure you're in correct Python environment

# Install dependencies
pip install -r requirements.txt

# Verify imports work
python -c "from packages.sdfcvf.quintet import QuintetDetector"
```

---

### **Problem: Hook takes too long (> 1 second)**

**Check:**
1. Embedding cache working?
2. Too many files staged?
3. Large files?

**Solution:**
```bash
# Check what's staged
git diff --cached --name-only

# If many files, commit in batches
git add file1.py file2.py  # Just 2 files
git commit -m "Part 1"

git add file3.py file4.py
git commit -m "Part 2"
```

---

### **Problem: False positives (hook blocks but shouldn't)**

**Check:**
1. Are tags correctly formatted?
2. Is syntax_ref exactly matching?
3. Are descriptions unique?

**Debug:**
```bash
# Run validator manually
python scripts/validate_tagged_file.py your_file.py

# See detailed diagnostic
# Fix specific issues shown
```

---

## 🔧 **Configuration**

### **Thresholds (in `.sdfcvf.config.yaml`):**

```yaml
coverage:
  public_api:
    threshold: 0.95  # 95% public API
  internal:
    threshold: 0.75  # 75% internal

composite_metric:
  threshold: 0.85  # code↔tags composite

quintet_parity:
  threshold: 0.90  # overall parity

performance:
  pre_commit:
    max_duration_ms: 500  # performance budget
```

**Can be adjusted** per project needs (edit config file).

---

### **Per-Directory Policies:**

```yaml
coverage:
  per_directory:
    - path: "packages/vif/"
      public_threshold: 0.95
      internal_threshold: 0.75
      reason: "VIF is gold standard"
    
    - path: "tests/"
      public_threshold: 0.50
      internal_threshold: 0.30
      reason: "Tests don't need strict tagging"
```

**Different standards** for different parts of codebase.

---

## 📋 **Common Scenarios**

### **Scenario 1: Committing New Feature**

```bash
# 1. Write code with tags
# 2. Stage file
git add packages/vif/new_feature.py

# 3. Commit
git commit -m "Added new feature"

# Hook runs automatically
# If passes → commit succeeds
# If fails → see diagnostic, fix issues
```

---

### **Scenario 2: Committing WIP (Work in Progress)**

**Option A: Add tags first (recommended)**
```bash
# Quick tag with auto-tagger
python scripts/vif_auto_tagger.py packages/vif/wip.py

# Commit tagged version
git add packages/vif/wip_TAGGED.py
git commit -m "WIP: New feature (tags added)"
```

**Option B: Bypass (not recommended)**
```bash
git commit --no-verify -m "WIP: Will add tags later"
# Remember to add tags before final merge!
```

---

### **Scenario 3: Committing Multiple Files**

```bash
# Tag all files first
python scripts/vif_auto_tagger.py packages/vif/file1.py
python scripts/vif_auto_tagger.py packages/vif/file2.py
python scripts/vif_auto_tagger.py packages/vif/file3.py

# Stage all
git add packages/vif/*_TAGGED.py

# Commit (hook checks all)
git commit -m "Added multiple features"

# Hook validates all staged files
# Must all pass P >= 0.90
```

---

### **Scenario 4: Fixing Hook Failure**

```bash
# Commit failed
$ git commit -m "Feature"
❌ Quintet parity check failed
# P = 0.75 (low)
# Coverage 60% (low)

# Fix with auto-tagger
$ python scripts/vif_auto_tagger.py packages/vif/file.py

# Review and enhance tags
# (Fix descriptions, add CONNECT tags, etc.)

# Validate
$ python scripts/validate_tagged_file.py packages/vif/file_TAGGED.py
✅ P = 0.92 (excellent)

# Stage tagged version
$ git add packages/vif/file_TAGGED.py

# Try commit again
$ git commit -m "Feature with tags"
✅ Passed (P=0.92)
[main abc1234] Feature with tags
```

---

## 🎯 **Tips for Success**

### **1. Tag at Creation**
- Write tags BEFORE implementation
- Use LLM assistant (< 1 sec)
- Pre-commit never fails!

### **2. Validate Early**
- Run validator before staging
- Fix issues before commit
- Faster feedback loop

### **3. Use Automation**
- Auto-tagger for baseline
- LLM for quality
- Enhance descriptions manually

### **4. Learn from Failures**
- Read diagnostic output carefully
- Understand what's wrong
- Fix root cause, not symptoms

### **5. Keep Commits Focused**
- Small, logical commits
- Easier to validate
- Faster pre-commit checks

---

## 📊 **Hook Performance**

### **What Makes It Fast:**

1. **Staged files only** - Not checking entire codebase
2. **Embedding cache** - Re-uses previous embeddings
3. **Incremental analysis** - Only changed code
4. **Optimized algorithms** - Efficient parity calculation

### **Performance by File Count:**

| Files | Expected Time | Status |
|-------|---------------|--------|
| 1 file | 100-200ms | ✅ Fast |
| 2-5 files | 200-400ms | ✅ Fast |
| 6-10 files | 400-500ms | ⚠️ At budget |
| 10+ files | > 500ms | ❌ Consider batching |

**If > 500ms:** Consider committing in smaller batches

---

## 🚀 **Advanced Usage**

### **Checking Hook Status:**

```bash
# See if hook is installed
cat .git/hooks/pre-commit

# Test hook manually
.git/hooks/pre-commit

# See what hook will check
git diff --cached --name-only | grep ".py$"
```

---

### **Debugging Hook Issues:**

```bash
# Run hook with debug output
python .git/hooks/pre-commit

# Check if imports work
python -c "from packages.sdfcvf.quintet import QuintetDetector; print('OK')"

# Validate specific file
python scripts/validate_tagged_file.py your_file.py
```

---

## 📚 **Resources**

- **Quintet Parity Guide:** `QUINTET_PARITY_COMPREHENSIVE_GUIDE.md`
- **Developer Guide:** `NL_TAG_DEVELOPER_GUIDE.md`
- **Troubleshooting:** `TROUBLESHOOTING_TAGS.md`
- **Configuration:** `.sdfcvf.config.yaml`
- **Hook Script:** `.git/hooks/pre-commit`

---

## 💡 **Quick Reference**

### **Common Commands:**

```bash
# Validate file
python scripts/validate_tagged_file.py <file>

# Auto-tag file
python scripts/vif_auto_tagger.py <file>

# Commit (auto-validates)
git commit -m "message"

# Bypass (emergency only)
git commit --no-verify -m "emergency"
```

### **Quality Targets:**

- Coverage: >= 95% public, >= 75% internal
- Parity: P >= 0.90
- Composite: >= 0.85
- Performance: < 500ms

---

**Status:** Production-ready guide  
**The pre-commit hook is your friend - it ensures quality automatically!** ✅

