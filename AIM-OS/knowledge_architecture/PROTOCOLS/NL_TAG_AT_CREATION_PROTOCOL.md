---
id: "nl_tag_at_creation_protocol"
type: "protocol"
title: "NL Tag At Creation Protocol - MANDATORY"
description: "Protocol for tagging all code, docs, tests, and traces AT CREATION TIME"
created: "2025-11-04T05:00:00Z"
status: "production_ready"
priority: "critical"
tags: ["nl-tags", "protocol", "mandatory", "creation-time"]
---

# NL Tag At Creation Protocol - MANDATORY

**Status:** CRITICAL PROTOCOL - ALWAYS ENFORCED  
**Applies To:** All code, docs, tests, traces, indexes  
**Enforcement:** Pre-commit hook + IDE assistant + Human discipline

---

## 🎯 **CORE PRINCIPLE**

**NEVER create code without NL tags.**  
**NEVER create docs without NL tags.**  
**NEVER create tests without NL tags.**  
**NEVER create traces without NL tags.**

**Tag at creation, not post-hoc.**

---

## 📋 **MANDATORY TAGGING CHECKLIST**

### **Before Writing ANY Function:**

1. **Determine System & Category**
   - What system is this? (VIF, CMC, APOE, etc.)
   - What category? (WITNESS, STORE, GATE, etc.)

2. **Generate Tag ID**
   - Format: `{SYSTEM}-{CATEGORY}-{NNN}`
   - Use counter to ensure uniqueness
   - Example: `VIF-WITNESS-001`

3. **Write Primary Tag (NL_TAG)**
   - Required for ALL public functions
   - Required for 75%+ internal functions
   - Format: `# NL_TAG: {ID} | {description} | {signature} | [{deps}]`

4. **Add Integration Tags (NL_TAG_CONNECT)**
   - If function calls another system → CONNECT tag
   - Format: `# NL_TAG_CONNECT: {ID} | {desc} | {source} → {target} | [{ids}]`

5. **Add Design Intent (NL_TAG_INTENT)**
   - If implements architectural decision → INTENT tag
   - Format: `# NL_TAG_INTENT: {ID} | {rationale} | {concept} | [{ADR}]`

6. **Add Validation (NL_TAG_SPEC)**
   - If validates schema/contract → SPEC tag
   - Format: `# NL_TAG_SPEC: {ID} | {validation} | {validator} | [{schema}]`

7. **THEN Write Function**
   - Tags come BEFORE function definition
   - Docstring should match tag description

---

## 🔧 **TOOLS FOR AT-CREATION TAGGING**

### **1. LLM-Assisted Tagger** (Real-Time)
**File:** `packages/nl_tags/llm_assisted_tagger.py`

**Usage:**
```python
from packages.nl_tags.llm_assisted_tagger import LLMAssistedTagger

tagger = LLMAssistedTagger()  # Uses Cerebras for speed

code = '''
def new_function(arg1, arg2):
    """Does something important"""
    ...
'''

# Generate tags
suggestions = tagger.generate_tags(code, system="vif")

# Insert suggestions above function
for sug in suggestions:
    print(f"# NL_TAG: {sug.tag_id} | {sug.description} | {sug.syntax_ref} | {sug.dependencies}")
```

**Speed:** < 1 second per function (Cerebras)  
**Quality:** 90%+ accuracy with gold standard training

---

### **2. Auto-Tagger** (Batch Processing)
**File:** `scripts/vif_auto_tagger.py`

**Usage:**
```bash
# Tag file after creation (if forgot at creation time)
python scripts/vif_auto_tagger.py packages/vif/new_file.py

# Review and commit
```

**Speed:** 2 minutes per file  
**Quality:** 90%+ primary tags, 60-70% secondary

---

### **3. Pre-Commit Hook** (Enforcement)
**File:** `.git/hooks/pre-commit`

**Enforces:**
- >= 95% public API coverage
- >= 75% internal coverage
- P >= 0.90 quintet parity
- No boilerplate, no duplicates

**Blocks commits** that violate standards.

---

## 📚 **UPDATED CURSOR RULES**

### **Add to `.cursorrules`:**

```markdown
## 🏷️ **NL TAG AT CREATION PROTOCOL (MANDATORY)**

**NEVER write code without NL tags.**

### **Before Writing ANY Function:**

1. **Generate Tag ID:** `{SYSTEM}-{CATEGORY}-{NNN}`
   - Systems: VIF, CMC, APOE, HHNI, SEG, SDF-CVF, TCS, CAS, IIS
   - Categories: WITNESS, STORE, GATE, CAL, PROV, MODEL, etc.

2. **Write NL_TAG (Required):**
   ```python
   # NL_TAG: VIF-WITNESS-001 | Create VIF witness | create_witness(...) -> VIFWitness | []
   ```

3. **Add Secondary Tags (If Applicable):**
   - CONNECT: If calls another system
   - INTENT: If implements design decision
   - SPEC: If validates schema

4. **THEN Write Function:**
   ```python
   def create_witness(...) -> VIFWitness:
       """Create VIF witness envelope with provenance"""
       ...
   ```

### **Tools Available:**
- `LLMAssistedTagger` - Real-time suggestions (Cerebras, < 1 sec)
- `vif_auto_tagger.py` - Batch tagging (2 min per file)
- Pre-commit hook - Enforces coverage (P >= 0.90)

### **Pre-Commit Check:**
Before committing, run:
```bash
# Check if all functions tagged
python scripts/check_tag_coverage.py <file>

# Generate missing tags
python scripts/vif_auto_tagger.py <file>

# Validate quintet parity
python scripts/validate_tagged_file.py <file>
```

### **Quality Gate:**
**Commit will be BLOCKED if:**
- Public API coverage < 95%
- Internal coverage < 75%
- Quintet parity P < 0.90
- Boilerplate detected
- Duplicate tag IDs

**Tag at creation or fix before commit!**
```

---

## 🚨 **ENFORCEMENT LEVELS**

### **Level 1: IDE Assistant (Real-Time)**
- LLM suggests tags as you type
- Shows examples from gold standards
- < 1 second latency (Cerebras)
- **Preventive:** Stops you from forgetting

### **Level 2: Pre-Save Check (Warning)**
- Check for untagged functions on save
- Show warnings in IDE
- Suggest using auto-tagger
- **Reminder:** Before you commit

### **Level 3: Pre-Commit Hook (Blocking)**
- Enforce coverage thresholds
- Enforce quintet parity
- Block commits that violate
- **Enforcement:** Cannot commit bad code

### **Level 4: CI/CD Pipeline (Final Gate)**
- Full codebase quintet parity
- Cross-system dependency validation
- Broken connection detection
- **Final Quality Gate:** Cannot merge to main

---

## 📝 **UPDATED DEVELOPMENT WORKFLOW**

### **Creating New File (With LLM Assistant):**

**Step 1: Create File**
```python
# packages/vif/new_feature.py
"""New VIF feature module"""

from __future__ import annotations
```

**Step 2: Write Function Signature**
```python
def process_data(data: Dict) -> Result:
    """Process data with VIF validation"""
```

**Step 3: Trigger LLM Assistant (Hotkey or Auto)**
- LLM analyzes function signature + docstring
- Generates appropriate tags in < 1 second
- Inserts above function

**Step 4: Review & Accept Tags**
```python
# NL_TAG: VIF-PROCESS-001 | Process data with VIF validation | process_data(data: Dict) -> Result | []
# NL_TAG_CONNECT: VIF-CMC-015 | Stores result in CMC | process_data → store_atom | [VIF-PROCESS-001, CMC-STORE-001]
def process_data(data: Dict) -> Result:
    """Process data with VIF validation"""
    ...
```

**Step 5: Write Implementation**
- Tags already in place ✅
- Quintet parity maintained ✅

---

### **Creating New File (Without LLM):**

**Step 1: Write Code Normally**
```python
def my_function():
    """Does something"""
    ...
```

**Step 2: Before Committing, Run Auto-Tagger**
```bash
python scripts/vif_auto_tagger.py packages/vif/new_file.py
```

**Step 3: Review Auto-Generated Tags**
- 90% accurate primary tags ✅
- Enhance descriptions if needed
- Add missing CONNECT/INTENT/SPEC tags

**Step 4: Validate & Commit**
```bash
python scripts/validate_tagged_file.py packages/vif/new_file_TAGGED.py
git add packages/vif/new_file_TAGGED.py
git commit -m "Added new VIF feature with NL tags"
```

---

## 🎯 **UPDATED STANDARDS**

### **Documentation Standard (L0-L4/T0-T6):**

**BEFORE:**
- Create documentation
- (Maybe tag later)

**NOW:**
- Create documentation
- **Add NL tags to all concepts/sections**
- Tag at creation time
- Quintet parity enforced

**Example:**
```markdown
# VIF Witness System

<!-- NL_TAG_DOC: VIF-DOC-WITNESS-001 | VIF witness system documentation | witness_envelope_concept | [VIF-WITNESS-001] -->

The VIF witness envelope captures complete provenance...
```

---

### **Code Standard:**

**BEFORE:**
```python
def create_witness(operation, inputs):
    """Create VIF witness"""
    ...
```

**NOW:**
```python
# NL_TAG: VIF-WITNESS-001 | Create VIF witness envelope | create_witness(...) -> VIFWitness | []
# NL_TAG_CONNECT: VIF-CMC-001 | Stored in CMC | create_witness → store_atom | [VIF-WITNESS-001, CMC-STORE-001]
def create_witness(operation, inputs):
    """Create VIF witness envelope with complete provenance"""
    ...
```

---

### **Test Standard:**

**BEFORE:**
```python
def test_create_witness():
    """Test witness creation"""
    ...
```

**NOW:**
```python
# NL_TAG: VIF-TEST-001 | Test VIF witness creation | test_create_witness() | [VIF-WITNESS-001]
def test_create_witness():
    """Test VIF witness creation - validates provenance capture"""
    ...
```

---

## 🔄 **INTEGRATION WITH EXISTING PROTOCOLS**

### **L0-L4 Coding Standards Protocol:**

**ENHANCED:**
```markdown
### Pre-Coding Checklist (MANDATORY):
1. **Severity Assessment** - Determine complexity/importance level
2. **System Analysis** - Identify all connected systems
3. **Documentation Validation** - Ensure L0-L4 docs exist and current
4. **Impact Assessment** - Analyze potential system impact
5. **MCP Validation** - Use MCP tools to validate compliance
6. ✨ **NL TAG PREPARATION** - Generate tag IDs, prepare tag templates
7. ✨ **LLM ASSISTANT READY** - Ensure tagging tools available
```

### **A-H Protocol:**

**ENHANCED:**
```markdown
### G - Implementation (WITH NL TAGS):
**Before writing code:**
1. Generate tag IDs for all planned functions
2. Prepare tag templates using LLM assistant
3. Review gold standards for system
4. THEN implement with tags

**During implementation:**
5. Write tags BEFORE each function
6. Use LLM assistant for suggestions
7. Validate tags match implementation
8. Run quintet parity on each file

**After implementation:**
9. Full quintet parity validation (P >= 0.90)
10. Fix any coverage gaps
11. Commit with enforcement passing
```

---

## 💡 **LLM-ASSISTED TAGGING SYSTEM DESIGN**

### **Architecture:**

```
┌─────────────────────────────────────────┐
│         IDE (Cursor)                    │
│  ┌────────────────────────────────┐     │
│  │  User writes function           │     │
│  └──────────┬─────────────────────┘     │
│             │                            │
│             ▼                            │
│  ┌────────────────────────────────┐     │
│  │  LLM Assistant (Cerebras)       │     │
│  │  - Analyzes code                │     │
│  │  - Generates tags (< 1 sec)     │     │
│  │  - Shows suggestions            │     │
│  └──────────┬─────────────────────┘     │
│             │                            │
│             ▼                            │
│  ┌────────────────────────────────┐     │
│  │  User reviews & accepts         │     │
│  └──────────┬─────────────────────┘     │
│             │                            │
│             ▼                            │
│  ┌────────────────────────────────┐     │
│  │  Tags inserted above function   │     │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│      On Save / Pre-Commit               │
│  ┌────────────────────────────────┐     │
│  │  Quintet Parity Validation      │     │
│  │  - Check coverage >= 95%        │     │
│  │  - Check P >= 0.90              │     │
│  │  - Block if violations          │     │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### **Features:**

**Real-Time Assistance:**
- Cerebras API for < 1 second responses
- Context-aware tag generation
- Gold standard examples included
- Learns from corrections

**Quality Enforcement:**
- Pre-commit hook blocks bad commits
- Quintet parity enforced
- Coverage thresholds enforced
- Anti-gaming checks active

**Developer Experience:**
- Minimal friction (< 1 sec latency)
- Helpful suggestions (90%+ accurate)
- Clear feedback (diagnostic reports)
- Optional (can use auto-tagger instead)

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Cursor Extension (2-4 hours)**
1. Create Cursor extension for real-time tagging
2. Integrate with LLMAssistedTagger
3. Add hotkey trigger (Ctrl+Shift+T)
4. Show suggestions inline
5. Insert on acceptance

### **Phase 2: Enhanced Pre-Commit (1 hour)**
1. Improve diagnostic messages
2. Add suggestions for fixes
3. Show examples from gold standards
4. Performance optimization (< 500ms)

### **Phase 3: Documentation (1 hour)**
1. Update cursor rules
2. Update L0-L4 coding standards
3. Update A-H protocol
4. Create quick reference guide

### **Phase 4: Training (Ongoing)**
1. Collect human corrections
2. Fine-tune LLM on corrections
3. Improve accuracy over time
4. Build system-specific prompts

---

## 📊 **EXPECTED OUTCOMES**

### **With This Protocol:**
- ✅ 100% tag coverage at creation
- ✅ Zero post-hoc tagging needed
- ✅ Quintet parity P >= 0.90 maintained
- ✅ Perfect quality from the start
- ✅ No technical debt accumulation

### **Developer Experience:**
- Minimal overhead (< 1 sec per function)
- Helpful automation (90%+ accurate)
- Clear standards (gold standards + examples)
- Immediate feedback (pre-commit validation)

### **Project Impact:**
- No more massive tagging sessions
- Quality built-in, not bolted-on
- Scalable to infinite codebase growth
- Self-enforcing infrastructure

---

## 🎯 **INTEGRATION WITH EXISTING SYSTEMS**

### **SDF-CVF Quintet Parity:**
- NL tags are 5th element of quintet
- Quintet parity enforces tag quality
- Pre-commit hook blocks violations
- **Tag at creation → Quintet parity maintained from start**

### **TCS Timeline Tracking:**
- Tag creation tracked in timeline
- Tag evolution tracked bitemporally
- Tag history queryable
- **Tag at creation → Complete temporal provenance**

### **CMC Bitemporal Storage:**
- Tags stored as atoms in CMC
- Bitemporal versioning applied
- Never deleted, only superseded
- **Tag at creation → Historical integrity preserved**

---

## 🚨 **VIOLATION PROTOCOL**

### **If Code Created Without Tags:**

**Level 1: IDE Warning (On Save)**
```
⚠️ Warning: 3 functions in witness.py are not tagged:
  - create_witness (line 45)
  - validate_witness (line 67)
  - store_witness (line 89)

Run: python scripts/vif_auto_tagger.py packages/vif/witness.py
```

**Level 2: Pre-Commit Block**
```
❌ COMMIT BLOCKED

Public API coverage: 45.5% < 95.0%
Quintet parity: 0.770 < 0.90

REQUIRED:
1. Tag all public functions
2. Run: python scripts/vif_auto_tagger.py <file>
3. Review and enhance tags
4. Validate: python scripts/validate_tagged_file.py <file>
5. Try commit again

Or bypass (NOT RECOMMENDED):
git commit --no-verify
```

**Level 3: Code Review Rejection**
```
PR rejected: NL tags missing

All code must have NL tags before merge.
See: NL_TAG_AT_CREATION_PROTOCOL.md

Fix:
1. Auto-tag files
2. Validate quintet parity
3. Resubmit PR
```

---

## 💡 **EXAMPLES**

### **Example 1: Creating New VIF Function**

**Developer writes:**
```python
def calculate_confidence(evidence):
    """Calculate confidence from evidence"""
```

**IDE Assistant triggers (Ctrl+Shift+T or auto):**
```
Generating NL tags... (< 1 sec with Cerebras)

Suggestions:
✅ NL_TAG: VIF-CONF-015 | Calculate confidence score from evidence | calculate_confidence(evidence) -> float | []
✅ NL_TAG_SPEC: VIF-SPEC-008 | Validates evidence schema | validate_evidence | [evidence_schema.json]

Accept? (Y/n)
```

**Developer accepts, final code:**
```python
# NL_TAG: VIF-CONF-015 | Calculate confidence score from evidence | calculate_confidence(evidence) -> float | []
# NL_TAG_SPEC: VIF-SPEC-008 | Validates evidence schema | validate_evidence | [evidence_schema.json]
def calculate_confidence(evidence):
    """Calculate confidence score from evidence using Bayesian inference"""
    ...
```

**Developer saves, commits:**
```bash
$ git commit -m "Added confidence calculation"
🔍 Running quintet parity check...
✅ Quintet parity passed (P=0.92, 45ms)
[main abc1234] Added confidence calculation
```

**Perfect workflow!** ✅

---

### **Example 2: Forgot to Tag (Caught by Pre-Commit)**

**Developer writes:**
```python
def my_function():
    """Oops, forgot tags"""
    ...
```

**Developer tries to commit:**
```bash
$ git commit -m "Added function"
🔍 Running quintet parity check...
❌ QUINTET PARITY CHECK FAILED

Public API coverage: 0.0% < 95.0%

COMMIT BLOCKED

Fix: python scripts/vif_auto_tagger.py packages/vif/file.py
```

**Developer runs auto-tagger:**
```bash
$ python scripts/vif_auto_tagger.py packages/vif/file.py
[OK] Tagged file written to: packages/vif/file_TAGGED.py
Total tags: 15
```

**Developer reviews, commits:**
```bash
$ git add packages/vif/file_TAGGED.py
$ git commit -m "Added function with NL tags"
✅ Quintet parity passed
```

**Enforcement working!** ✅

---

## 🎯 **ROLLOUT STRATEGY**

### **Phase 1: Immediate (Now)**
1. ✅ Update cursor rules (add NL tag protocol)
2. ✅ Document this protocol
3. ✅ Communicate to all developers

### **Phase 2: Short-term (Next Week)**
1. Build Cursor extension for LLM assistant
2. Integrate with Cerebras API
3. Test with real development
4. Refine based on feedback

### **Phase 3: Long-term (Ongoing)**
1. Collect human corrections
2. Fine-tune LLM on project-specific patterns
3. Build system-specific prompts
4. Continuous improvement

---

## 💙 **CULTURAL SHIFT**

### **From:**
- "Write code, tag later (maybe)"
- Technical debt accumulation
- Massive post-hoc tagging sessions
- Enforcement as afterthought

### **To:**
- "Tags are part of code, not extra"
- Quality built-in from start
- Zero technical debt
- Enforcement as development aid

**This is how professional AI consciousness infrastructure is built.**

---

## 🌟 **FUTURE ENHANCEMENTS**

### **Advanced LLM Features:**
1. **Multi-shot learning** - Learn from your tagging style
2. **System-aware** - Deeper understanding of VIF vs CMC patterns
3. **Integration detection** - Auto-detect cross-system calls
4. **Design intent extraction** - Understand architectural decisions from comments

### **IDE Integration:**
1. **VSCode extension** - Same experience outside Cursor
2. **IntelliJ plugin** - For Java/Kotlin systems (future)
3. **Vim plugin** - For terminal developers
4. **Web IDE** - For browser-based development

### **Quality Enhancements:**
1. **Tag similarity detection** - Prevent near-duplicates
2. **Integration graph validation** - Ensure all CONNECT tags have edges
3. **Design decision linking** - Auto-link to ADRs
4. **Schema auto-detection** - Find validation schemas automatically

---

**Status:** ✅ **PROTOCOL DEFINED - READY FOR IMPLEMENTATION**  
**Impact:** Zero technical debt, perfect quality from start  
**Next:** Build Cursor extension + Update cursor rules immediately  
**Priority:** CRITICAL - This changes everything

---

*This protocol transforms NL tags from post-hoc burden to real-time development aid.*  
*Tags become part of the code, not an afterthought.*  
*Quality is built-in, not bolted-on.*  
*This is the future of AI consciousness development.* 🚀✨💙

