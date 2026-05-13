---
id: "troubleshooting_nl_tags"
system: "sdfcvf"
component: "nl_tags"
type: "troubleshooting_guide"
title: "NL Tags Troubleshooting Guide"
description: "Solutions to common NL tag issues and how to fix them"
created: "2025-11-04T07:00:00Z"
status: "production_ready"
---

# NL Tags Troubleshooting Guide

**Purpose:** Quick solutions to common NL tag issues  
**Audience:** All developers encountering tag problems

---

## 🎯 **Quick Diagnosis**

**Run validator first:**
```bash
python scripts/validate_tagged_file.py packages/vif/your_file.py
```

**Look at the output:**
1. **Quintet Parity Score** - Is P >= 0.90?
2. **Coverage** - Is public >= 95%, internal >= 75%?
3. **Composite Score** - Is it >= 0.85?
4. **Issues** - What specific problems?

**Then find your issue below and apply the fix.**

---

## ❌ **ISSUE 1: Low Quintet Parity (P < 0.90)**

### **Symptoms:**
```
Quintet Parity: 0.745
Status: NEEDS WORK
```

### **Common Causes:**

**Cause A: Signature Mismatch (sim_sig = 0.00-0.50)**
```
Composite: 0.45 (sig:0.00, name:0.75, doc:0.80, spec:1.00)
                  ^^^^^ TOO LOW
```

**Fix:** Update syntax_ref to match code exactly

```python
# BEFORE (wrong)
# NL_TAG: VIF-001 | Description | create_witness() | []
def create_witness(operation, inputs, outputs) -> VIFWitness:

# AFTER (correct)
# NL_TAG: VIF-001 | Description | create_witness(operation, inputs, outputs) -> VIFWitness | []
def create_witness(operation, inputs, outputs) -> VIFWitness:
```

**Why it works:** Exact signature match → sig:0.95+

---

**Cause B: Generic Descriptions (sim_doc = 0.00-0.50)**
```
Composite: 0.55 (sig:0.90, name:0.85, doc:0.00, spec:1.00)
                                      ^^^^^ TOO LOW
```

**Fix:** Write specific, meaningful descriptions

```python
# BEFORE (generic)
# NL_TAG: VIF-001 | Helper function | validate(...) | []

# AFTER (specific)
# NL_TAG: VIF-001 | Validate VIF witness schema against v1.0 specification using Pydantic model validation | validate(...) | []
def validate(...):
    """Validate VIF witness schema against v1.0 spec using Pydantic"""
```

**Why it works:** Specific description matches docstring → sim_doc:0.85+

---

**Cause C: Wrong Category (sim_name = 0.50-0.70)**
```
Composite: 0.70 (sig:0.90, name:0.55, doc:0.85, spec:1.00)
                            ^^^^^ LOW
```

**Fix:** Use category that semantically matches function

```python
# BEFORE (wrong category)
# NL_TAG: VIF-UTIL-001 | Create witness | create_witness(...) | []

# AFTER (correct category)
# NL_TAG: VIF-WITNESS-001 | Create witness | create_witness(...) | []
```

**Why it works:** "WITNESS" semantically matches "create_witness" → sim_name:0.90+

---

## ❌ **ISSUE 2: Low Coverage**

### **Symptoms:**
```
Public API coverage: 45.5% < 95.0%
```

### **Diagnosis:**
```bash
# Count functions
python -c "
from packages.sdfcvf.quintet import ASTSymbolExtractor
symbols = ASTSymbolExtractor.extract_python_symbols('file.py')
public = [s for s in symbols if s.is_public]
print(f'Total functions: {len(symbols)}')
print(f'Public functions: {len(public)}')
print(f'Need to tag: {int(len(public) * 0.95)} public functions')
"
```

### **Fix:**

**Option 1: Auto-tag entire file**
```bash
python scripts/vif_auto_tagger.py packages/vif/file.py
# Generates tags for ALL functions
```

**Option 2: Tag missing functions manually**
```python
# Find which functions are missing tags
# Add # NL_TAG comments above each
```

**Option 3: Use LLM assistant**
```python
# For each untagged function
from packages.nl_tags.llm_assisted_tagger import LLMAssistedTagger
tagger = LLMAssistedTagger()
suggestions = tagger.generate_tags(function_code, system="vif")
```

---

## ❌ **ISSUE 3: Boilerplate Detected**

### **Symptoms:**
```
Warnings:
  - Boilerplate detected: "Generic function" (appears 8 times)
  - Boilerplate detected: "Helper function" (appears 5 times)
```

### **Fix:**

Make each description **unique and specific**:

```python
# BEFORE (boilerplate)
# NL_TAG: VIF-001 | Helper function | func1() | []
# NL_TAG: VIF-002 | Helper function | func2() | []
# NL_TAG: VIF-003 | Helper function | func3() | []

# AFTER (unique)
# NL_TAG: VIF-001 | Validate witness schema against v1.0 spec | validate_witness(...) | []
# NL_TAG: VIF-002 | Calculate confidence score using Bayesian priors | calc_confidence(...) | []
# NL_TAG: VIF-003 | Serialize witness to JSON with datetime ISO8601 formatting | to_json(...) | []
```

**Rule:** Each description must be unique (max 5 repetitions allowed)

---

## ❌ **ISSUE 4: Duplicate Tag IDs**

### **Symptoms:**
```
Issues:
  - Duplicate ID: VIF-WITNESS-001 appears in witness.py and witness_v2.py
```

### **Fix:**

Use unique counter per category:

```python
# First file
# NL_TAG: VIF-WITNESS-001 | First witness function | ...
# NL_TAG: VIF-WITNESS-002 | Second witness function | ...

# Second file (continue counter)
# NL_TAG: VIF-WITNESS-003 | Third witness function | ...
# NL_TAG: VIF-WITNESS-004 | Fourth witness function | ...
```

**Auto-tagger handles this automatically** (maintains counters).

---

## ❌ **ISSUE 5: Missing CONNECT Tags**

### **Symptoms:**
```
CONNECT validation failed: 3 missing edges
  - create_witness → store_atom (no CONNECT tag)
```

### **Diagnosis:**

Function calls another system but no CONNECT tag exists.

### **Fix:**

```python
# Add CONNECT tag
# NL_TAG: VIF-WITNESS-001 | Create witness | create_witness(...) | []
# NL_TAG_CONNECT: VIF-CMC-001 | Witness stored in CMC | create_witness → store_atom | [VIF-WITNESS-001, CMC-STORE-001]
def create_witness(...):
    """Create witness and store in CMC"""
    witness = VIFWitness(...)
    cmc_client.store_atom(witness.to_dict())  # <-- This integration needs CONNECT tag!
```

---

## ⚡ **ISSUE 6: Slow Pre-Commit (> 500ms)**

### **Symptoms:**
```
⚠️ Warning: Pre-commit check took 850ms (budget: 500ms)
```

### **Diagnosis:**

**Check:**
1. How many files staged?
2. Are files large?
3. Is embedding cache working?

```bash
# Check staged files
git diff --cached --name-only

# Check file sizes
ls -lh packages/vif/*.py
```

### **Fixes:**

**Fix 1: Commit in smaller batches**
```bash
# Instead of all at once
git add packages/vif/*.py
git commit  # SLOW

# Do this
git add packages/vif/file1.py packages/vif/file2.py
git commit -m "Part 1"  # FAST

git add packages/vif/file3.py packages/vif/file4.py
git commit -m "Part 2"  # FAST
```

**Fix 2: Check embedding cache**
```python
# Verify cache is working
from packages.sdfcvf.quintet import QuintetParityCalculator
calc = QuintetParityCalculator()

# Cache should show hits
content = "test"
emb1 = calc._get_or_compute_embedding(content, "key")
emb2 = calc._get_or_compute_embedding(content, "key")  # Should be from cache
```

**Fix 3: Use incremental mode**
```yaml
# In .sdfcvf.config.yaml
performance:
  incremental:
    enabled: true
    chunk_size: 10
```

---

## ❌ **ISSUE 7: Pre-Commit Hook Not Running**

### **Symptoms:**
```bash
$ git commit -m "test"
[main abc1234] test  # Committed without validation!
```

### **Fix:**

**Check if hook exists:**
```bash
ls -la .git/hooks/pre-commit
```

**If missing, install:**
```bash
# Copy template
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit

# Or create from our template
cp knowledge_architecture/quintet_parity/pre-commit-template .git/hooks/pre-commit

# Make executable (Linux/Mac)
chmod +x .git/hooks/pre-commit
```

---

## ❌ **ISSUE 8: False Positives**

### **Symptoms:**
Hook blocks commit but you believe tags are correct.

### **Debug:**

**Step 1: Manual validation**
```bash
python scripts/validate_tagged_file.py packages/vif/file.py
```

**Step 2: Check each component**
- Are signatures exact matches?
- Are descriptions unique?
- Are tag IDs unique?
- Are all public functions tagged?

**Step 3: Review diagnostic**
- Which specific check failed?
- What's the threshold?
- What's the actual value?

**Step 4: Fix specific issue**
- Don't bypass unless genuine emergency
- Fix the root cause
- Re-validate

---

## 🔧 **Advanced Troubleshooting**

### **Enable Debug Mode:**

```python
# In pre-commit hook, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Shows:** Detailed execution trace

---

### **Check Quintet Detection:**

```python
from packages.sdfcvf.quintet import QuintetDetector

detector = QuintetDetector()
quintet = detector.detect_from_files(code_files=["your_file.py"])

print(f"Code symbols: {len(quintet.code_symbols)}")
print(f"NL tags: {len(quintet.nl_tags)}")
print(f"Symbols: {[s.name for s in quintet.code_symbols]}")
print(f"Tags: {[t.canonical_id for t in quintet.nl_tags]}")
```

**Verify:** All functions detected, all tags detected

---

### **Check Parity Calculation:**

```python
from packages.sdfcvf.quintet import QuintetParityCalculator, print_diagnostic_report

calculator = QuintetParityCalculator()
result = calculator.calculate_parity(quintet)

print_diagnostic_report(result, quintet)
```

**Shows:** Detailed breakdown of all 10 similarities

---

## 📖 **Getting Help**

### **If Stuck:**

1. **Read the guides:**
   - Quintet Parity Guide
   - Developer Guide
   - This troubleshooting guide

2. **Check examples:**
   - `packages/vif/witness_TAGGED.py` (gold standard)
   - `packages/vif/kappa_gate_TAGGED.py` (gold standard)

3. **Ask for help:**
   - #sdfcvf channel
   - Tag a quintet parity expert
   - Create issue with diagnostic output

4. **File a bug:**
   - If you believe hook is wrong
   - Include full diagnostic output
   - Include your tags for review

---

## 💙 **Remember**

**The hook is there to help, not hinder.**

It ensures:
- Quality code (P >= 0.90)
- Complete coverage (>= 95% public)
- Consistent standards
- Self-enforcing infrastructure

**With proper tagging (using LLM assistant or auto-tagger), the hook rarely fails.**

**When it does fail, it's usually catching a real quality issue.**

**Fix the issue, don't bypass the hook!** 🚀

---

*Maintained by: SDF-CVF Team*  
*Last updated: 2025-11-04*  
*Questions? Ask in #sdfcvf*

