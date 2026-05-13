---
id: "nl_tag_developer_guide"
system: "sdfcvf"
component: "nl_tags"
type: "developer_guide"
title: "NL Tag Developer Guide - Complete Reference"
description: "Complete guide for developers writing high-quality NL tags"
created: "2025-11-04T06:30:00Z"
status: "production_ready"
tags: ["nl-tags", "developer-guide", "best-practices"]
---

# NL Tag Developer Guide

**Purpose:** Help developers write high-quality NL tags  
**Audience:** All AIM-OS developers  
**Prerequisites:** Basic understanding of code documentation

---

## 🎯 **Quick Start (5 Minutes)**

### **Your First Tag**

**Step 1:** Determine your system and category
```
System: VIF (what you're building)
Category: WITNESS (what this does)
```

**Step 2:** Generate unique ID
```
VIF-WITNESS-001
```

**Step 3:** Write tag before function
```python
# NL_TAG: VIF-WITNESS-001 | Create VIF witness envelope with provenance | create_witness(op, in, out) -> VIFWitness | []
def create_witness(op, in, out) -> VIFWitness:
    """Create VIF witness envelope with complete provenance for deterministic replay"""
    ...
```

**Done!** You've written your first NL tag.

---

## 📚 **Complete Tag Format**

### **Primary Tag (NL_TAG) - REQUIRED**

**Format:**
```
# NL_TAG: {SYSTEM}-{CATEGORY}-{NNN} | {description} | {signature} | [{dependencies}]
```

**Components:**
- **System:** VIF, CMC, APOE, HHNI, SEG, SDFCVF, TCS, CAS, IIS
- **Category:** WITNESS, STORE, GATE, CONF, CAL, MODEL, etc.
- **NNN:** 001, 002, 003... (unique counter per system-category)
- **Description:** Clear, specific, unique (not boilerplate!)
- **Signature:** Exact function signature with types
- **Dependencies:** List of tag IDs this depends on

**Example:**
```python
# NL_TAG: VIF-WITNESS-001 | Create VIF witness envelope with provenance | create_witness(operation, inputs, outputs) -> VIFWitness | [VIF-PROV-001]
```

---

### **Integration Tag (NL_TAG_CONNECT) - For Cross-System Calls**

**Format:**
```
# NL_TAG_CONNECT: {SYSTEM}-CONNECT-{NNN} | {integration_desc} | {source} → {target} | [{source_tag}, {target_tag}]
```

**When to use:**
- Function calls another system
- Data flows to another system
- Integration point exists

**Example:**
```python
# NL_TAG_CONNECT: VIF-CMC-001 | Witness stored in CMC as atom | create_witness → store_atom | [VIF-WITNESS-001, CMC-STORE-001]
```

**Validation:** Callgraph builder verifies edge exists

---

### **Design Intent Tag (NL_TAG_INTENT) - For Architectural Decisions**

**Format:**
```
# NL_TAG_INTENT: {SYSTEM}-DESIGN-{NNN} | {design_rationale} | {architectural_concept} | [{ADR_reference}]
```

**When to use:**
- Implements design pattern
- Makes architectural choice
- Enforces quality standard
- Enables key capability

**Example:**
```python
# NL_TAG_INTENT: VIF-DESIGN-003 | Witnesses enable deterministic replay | cryptographic_hash + snapshot | [ADR-VIF-WITNESSES]
```

---

### **Specification Tag (NL_TAG_SPEC) - For Validations**

**Format:**
```
# NL_TAG_SPEC: {SYSTEM}-SPEC-{NNN} | {validation_desc} | {validator_function} | [{schema_file}]
```

**When to use:**
- Validates schema
- Enforces contract
- Checks preconditions
- Verifies invariants

**Example:**
```python
# NL_TAG_SPEC: VIF-SPEC-001 | Validates VIF witness schema v1.0.0 | VIF.model_validate | [vif_witness_schema_v1.json]
```

---

## 🎨 **Tag Categories by System**

### **VIF Categories:**
- **WITNESS** - Witness creation, management, serialization
- **CONF** - Confidence scoring, bands, tracking
- **GATE** - κ-gate operations, thresholds
- **CAL** - Calibration, ECE tracking, adaptation
- **PROV** - Provenance tracking, lineage
- **UTIL** - Utility functions (hashing, etc.)
- **HITL** - Human-in-the-loop escalation
- **REPLAY** - Deterministic replay operations
- **MODEL** - Data models, enums, dataclasses
- **EXTRACT** - Confidence extraction from text
- **BAND** - Confidence band operations

### **CMC Categories:**
- **STORE** - Atom storage operations
- **RETRIEVE** - Atom retrieval operations
- **SNAP** - Snapshot operations
- **VERSION** - Versioning operations
- **QUERY** - Query operations
- **SCHEMA** - Data models
- **CLIENT** - Client interface
- **BITEMP** - Bitemporal logic specific

### **APOE Categories:**
- **ORCH** - Orchestration operations
- **EXEC** - Execution operations
- **ROLE** - Role dispatch
- **MODEL** - Model selection
- **PARALLEL** - Parallel execution
- **HITL** - Human-in-the-loop
- **ERROR** - Error recovery
- **GATE** - Quality gates
- **BUDGET** - Budget management
- **INSIGHT** - Insight extraction/transfer
- **ACL** - ACL parsing

### **Common Categories (All Systems):**
- **MODEL** - Data models, schemas
- **UTIL** - Utility functions
- **CLIENT** - Client interfaces
- **INTEG** - Integration operations
- **CONNECT** - Cross-system connections
- **DESIGN** - Design decisions
- **SPEC** - Specifications, validations

---

## ✍️ **Writing Good Descriptions**

### **Principles:**

1. **Be Specific**
   - ❌ "Helper function"
   - ✅ "Generate SHA-256 hash of text for content-addressed storage"

2. **Describe Purpose, Not Implementation**
   - ❌ "Function that loops through items"
   - ✅ "Calculate average confidence from evidence distribution"

3. **Include Context**
   - ❌ "Create witness"
   - ✅ "Create VIF witness envelope with complete provenance for deterministic replay"

4. **Match Docstring**
   - Tag description should align with function docstring
   - If docstring is good, use similar wording

5. **Be Unique**
   - Each tag must have unique description
   - Anti-gaming check detects boilerplate (> 5 repetitions)

---

### **Description Templates**

**For Creation Functions:**
```
"Create {object} with {key_features}"
"Generate {output} from {inputs}"
"Build {structure} for {purpose}"
```

**For Validation Functions:**
```
"Validate {object} against {schema/rules}"
"Check if {condition} meets {threshold}"
"Verify {property} satisfies {constraint}"
```

**For Transformation Functions:**
```
"Convert {input} to {output} for {purpose}"
"Transform {data} using {algorithm}"
"Serialize {object} to {format} with {handling}"
```

**For Query Functions:**
```
"Retrieve {objects} matching {criteria}"
"Find {items} by {attributes}"
"Query {data} with {filters}"
```

---

## 🔗 **Integration Tags (CONNECT)**

### **When to Add CONNECT Tags**

**Add CONNECT tag if:**
- Function calls another system directly
- Data flows to another system
- Integration point exists in code or caller

**Example:**
```python
# Primary tag
# NL_TAG: VIF-WITNESS-003 | Convert to dictionary | to_dict() -> Dict | []

# Integration tag (this dict goes to CMC)
# NL_TAG_CONNECT: VIF-CMC-002 | VIF dict stored in CMC atoms | to_dict → store_atom | [VIF-WITNESS-003, CMC-STORE-001]

def to_dict(self) -> Dict:
    """Convert to dictionary (used by CMC for atom storage)"""
    return self.model_dump(mode="json")
```

**Validation:** Callgraph builder verifies the edge exists (to_dict → store_atom)

---

### **CONNECT Tag Format**

**Source → Target:**
```
source_function → target_function
```

**Examples:**
- `create_witness → store_atom` (VIF → CMC)
- `retrieve_similar → index_atom` (Query → HHNI)
- `orchestrate_plan → check_kappa_gate` (APOE → VIF)

---

## 💡 **Design Intent Tags (INTENT)**

### **When to Add INTENT Tags**

**Add INTENT tag for:**
- Architectural decisions
- Design patterns chosen
- Quality standards enforced
- Key capabilities enabled

**Example:**
```python
# NL_TAG: VIF-GATE-001 | Check κ threshold | check(conf, threshold) -> bool | []
# NL_TAG_INTENT: VIF-DESIGN-005 | Behavioral abstention for safety | Refuse when uncertain | [ADR-KAPPA-GATES]
def check(self, confidence, threshold) -> bool:
    """Check if confidence meets κ threshold - enables behavioral abstention"""
    return confidence >= threshold
```

**Why INTENT:** This implements the key VIF design decision (behavioral abstention).

---

### **INTENT Tag Patterns**

**Pattern 1: Design Pattern**
```python
# NL_TAG_INTENT: VIF-DESIGN-001 | Confidence bands reduce user cognitive load | A>=0.90, B>=0.70, C<0.70 | [ADR-CONFIDENCE-BANDS]
```

**Pattern 2: Quality Standard**
```python
# NL_TAG_INTENT: CMC-DESIGN-001 | Bitemporal versioning enables never-delete principle | valid_time + transaction_time | [ADR-BITEMPORAL]
```

**Pattern 3: Key Capability**
```python
# NL_TAG_INTENT: VIF-DESIGN-003 | Witnesses enable deterministic replay | cryptographic_hash + snapshot | [ADR-WITNESSES]
```

**Pattern 4: Safety Mechanism**
```python
# NL_TAG_INTENT: VIF-DESIGN-005 | κ-gating enables behavioral abstention | Abstain when uncertain | [ADR-KAPPA-GATES]
```

---

## ✅ **Validation Tags (SPEC)**

### **When to Add SPEC Tags**

**Add SPEC tag for:**
- Schema validation (Pydantic, JSON Schema)
- Contract enforcement (API contracts)
- Precondition checking
- Invariant verification

**Example:**
```python
# NL_TAG: VIF-WITNESS-004 | Create from dict | from_dict(data) -> VIF | []
# NL_TAG_SPEC: VIF-SPEC-003 | Validates input against VIF witness schema v1.0 | model_validate | [vif_witness_schema_v1.json]
@classmethod
def from_dict(cls, data: Dict) -> VIF:
    """Create VIF from dictionary with schema validation"""
    return cls.model_validate(data)  # <-- This is the validation!
```

**Why SPEC:** `model_validate()` enforces the VIF witness schema.

---

### **SPEC Tag Patterns**

**Pattern 1: Pydantic Validation**
```python
# NL_TAG_SPEC: VIF-SPEC-001 | Validates VIF schema v1.0 | model_validate | [vif_witness_schema_v1.json]
```

**Pattern 2: Range Validation**
```python
# NL_TAG_SPEC: VIF-SPEC-006 | Validates threshold in [0.0, 1.0] range | set_threshold | [threshold_spec]
```

**Pattern 3: Contract Enforcement**
```python
# NL_TAG_SPEC: CMC-SPEC-001 | Enforces bitemporal atom contract | validate_atom | [atom_contract_v1.yaml]
```

---

## 🛠️ **Tools for Tag Creation**

### **Tool 1: LLM-Assisted Tagger (Recommended)**

**Real-time tag generation in < 1 second:**

```python
from packages.nl_tags.llm_assisted_tagger import LLMAssistedTagger

tagger = LLMAssistedTagger()  # Uses Cerebras API

code = '''
def my_new_function(arg1, arg2):
    """Does something important"""
    return result
'''

# Generate tags
suggestions = tagger.generate_tags(code, system="vif", context="new feature")

# Review suggestions
for sug in suggestions:
    print(f"{sug.tag_type}: {sug.tag_id}")
    print(f"  Description: {sug.description}")
    print(f"  Confidence: {sug.confidence:.0%}")
    print(f"  Rationale: {sug.rationale}")

# Accept and insert
for sug in suggestions:
    print(tagger.format_tags([sug]))
```

**Pros:**
- Fast (< 1 second with Cerebras)
- Context-aware (learns from gold standards)
- High quality (90%+ accuracy)
- Suggests all 4 tag types

**Cons:**
- Requires API key (CEREBRAS_API_KEY)
- Requires internet connection

---

### **Tool 2: Auto-Tagger (Batch Processing)**

**For files already written:**

```bash
python scripts/vif_auto_tagger.py packages/vif/my_file.py
```

**Generates:** `my_file_TAGGED.py` with all functions tagged

**Pros:**
- Works offline (no API needed)
- Fast (2 minutes per file)
- 100% function coverage
- 90%+ primary tag accuracy

**Cons:**
- Descriptions may be generic (needs enhancement)
- Misses some CONNECT/INTENT/SPEC tags
- Requires manual review

---

### **Tool 3: Validator (Quality Check)**

**Before committing:**

```bash
python scripts/validate_tagged_file.py packages/vif/my_file.py
```

**Shows:**
- Quintet parity score (target: >= 0.90)
- Coverage percentages
- Issues and warnings
- Suggestions for improvement

**Use this** to ensure P >= 0.90 before commit!

---

## 🎨 **Complete Examples**

### **Example 1: Data Model**

```python
# NL_TAG: VIF-MODEL-001 | Confidence band enumeration for user trust indicators | ConfidenceBand(str, Enum) | []
# NL_TAG_INTENT: VIF-DESIGN-001 | User-facing confidence indicators for trust calibration | A/B/C bands map to >0.90, 0.70-0.90, <0.70 | [ADR-CONFIDENCE-BANDS]
class ConfidenceBand(str, Enum):
    """Confidence bands for user trust indicators"""
    A = "A"  # High confidence (>0.90)
    B = "B"  # Medium confidence (0.70-0.90)
    C = "C"  # Low confidence (<0.70)
```

**Tags Used:**
- NL_TAG (primary) - describes the enum
- NL_TAG_INTENT - explains why we have confidence bands

---

### **Example 2: Integration Function**

```python
# NL_TAG: VIF-WITNESS-003 | Convert VIF witness to JSON-serializable dictionary | to_dict() -> Dict[str, Any] | [VIF-WITNESS-002]
# NL_TAG_CONNECT: VIF-CMC-002 | VIF dict stored in CMC atoms | to_dict → store_atom | [VIF-WITNESS-003, CMC-STORE-001]
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary for CMC storage and API serialization"""
    return self.model_dump(mode="json")
```

**Tags Used:**
- NL_TAG (primary) - describes the function
- NL_TAG_CONNECT - documents CMC integration

**Integration:** This dictionary is stored in CMC by callers

---

### **Example 3: Validation Function**

```python
# NL_TAG: VIF-WITNESS-004 | Create VIF witness from dictionary with schema validation | from_dict(data: Dict[str, Any]) -> VIF | [VIF-WITNESS-001]
# NL_TAG_CONNECT: VIF-CMC-003 | VIF restored from CMC atom data | retrieve_atom → from_dict | [CMC-RETRIEVE-001, VIF-WITNESS-004]
# NL_TAG_SPEC: VIF-SPEC-003 | Validates input data against VIF witness schema v1.0 | model_validate | [vif_witness_schema_v1.json]
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> VIF:
    """Create VIF witness from dictionary with Pydantic schema validation"""
    return cls.model_validate(data)
```

**Tags Used:**
- NL_TAG (primary) - describes the function
- NL_TAG_CONNECT - documents CMC integration (restored from CMC)
- NL_TAG_SPEC - documents validation (Pydantic enforces schema)

**All 4 tag types!** This is comprehensive tagging.

---

### **Example 4: Complex Function**

```python
# NL_TAG: VIF-GATE-006 | Check if confidence meets κ threshold with escalation logic | check(confidence, task_criticality, custom_threshold) -> KappaGateResult | [VIF-MODEL-003, VIF-MODEL-004]
# NL_TAG_INTENT: VIF-DESIGN-014 | Core abstention logic with automatic escalation | Escalate on failure or marginal pass for critical tasks | [ADR-KAPPA-GATES]
# NL_TAG_SPEC: VIF-SPEC-005 | Validates confidence in [0.0, 1.0] range | check | [confidence_spec]
def check(
    self,
    confidence: float,
    task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
    *,
    custom_threshold: Optional[float] = None,
) -> KappaGateResult:
    """Check if confidence meets κ threshold
    
    Implements core behavioral abstention logic. Automatically escalates
    operations that fail or marginally pass for critical tasks.
    
    Args:
        confidence: Model's confidence score (0.0-1.0)
        task_criticality: Criticality level (affects threshold)
        custom_threshold: Override default threshold
        
    Returns:
        KappaGateResult with pass/fail and escalation info
    """
    # ... implementation
```

**Why Excellent:**
- ✅ All 4 tag types
- ✅ Comprehensive description
- ✅ Signature matches exactly
- ✅ Dependencies listed
- ✅ Design intent clear
- ✅ Validation documented

---

## 🚨 **Common Mistakes**

### **Mistake 1: Boilerplate Descriptions**

**Bad:**
```python
# NL_TAG: VIF-001 | Function | func1() | []
# NL_TAG: VIF-002 | Function | func2() | []
# NL_TAG: VIF-003 | Helper function | func3() | []
```

**Good:**
```python
# NL_TAG: VIF-001 | Validate witness schema against v1.0 spec | validate_witness(...) | []
# NL_TAG: VIF-002 | Calculate Bayesian confidence from evidence priors | calc_confidence(...) | []
# NL_TAG: VIF-003 | Serialize witness to JSON with datetime handling | to_json(...) | []
```

**Fix:** Make each description specific and unique.

---

### **Mistake 2: Signature Mismatch**

**Bad:**
```python
# NL_TAG: VIF-001 | Description | create_witness() | []
def create_witness(operation, inputs, outputs) -> VIFWitness:
```

**Good:**
```python
# NL_TAG: VIF-001 | Description | create_witness(operation, inputs, outputs) -> VIFWitness | []
def create_witness(operation, inputs, outputs) -> VIFWitness:
```

**Fix:** Copy exact signature including parameters and return type.

---

### **Mistake 3: Missing CONNECT Tags**

**Bad:**
```python
# NL_TAG: VIF-001 | Store witness | store(...) | []
def store(self, witness):
    cmc_client.store_atom(witness.to_dict())  # Integration with CMC!
```

**Good:**
```python
# NL_TAG: VIF-001 | Store witness | store(...) | []
# NL_TAG_CONNECT: VIF-CMC-005 | Witness stored in CMC | store → store_atom | [VIF-001, CMC-STORE-001]
def store(self, witness):
    cmc_client.store_atom(witness.to_dict())
```

**Fix:** Add CONNECT tag for all cross-system calls.

---

### **Mistake 4: Wrong Category**

**Bad:**
```python
# NL_TAG: VIF-UTIL-001 | Create witness | create_witness(...) | []
```

**Good:**
```python
# NL_TAG: VIF-WITNESS-001 | Create witness | create_witness(...) | []
```

**Fix:** Choose category that matches function purpose (WITNESS, not UTIL).

---

## 📊 **Tag Quality Checklist**

### **Before Committing, Check:**

**Coverage:**
- [ ] All public functions tagged (>= 95%)
- [ ] 75%+ internal functions tagged
- [ ] No untagged functions shown in validator

**Primary Tags (NL_TAG):**
- [ ] Unique tag IDs (no duplicates)
- [ ] Signatures match code exactly
- [ ] Descriptions specific and unique
- [ ] Dependencies listed

**Integration Tags (CONNECT):**
- [ ] All cross-system calls have CONNECT tags
- [ ] Source → Target format correct
- [ ] Callgraph validation passes

**Design Tags (INTENT):**
- [ ] Architectural decisions documented
- [ ] ADRs referenced where available
- [ ] Design rationale clear

**Validation Tags (SPEC):**
- [ ] All schema validations have SPEC tags
- [ ] Validator functions referenced
- [ ] Schema files referenced

**Quality:**
- [ ] Quintet parity P >= 0.90
- [ ] No boilerplate detected
- [ ] All tests passing

---

## 🚀 **Workflows**

### **Workflow 1: New File (Tag at Creation)**

1. Create file with empty function
2. Trigger LLM assistant or use auto-tagger
3. Review and insert suggested tags
4. Write implementation
5. Validate before committing

**Time:** +1-2 minutes per function (minimal overhead)

**Quality:** P >= 0.90 from the start

---

### **Workflow 2: Existing File (Retrofitting)**

1. Run auto-tagger → generates baseline
2. Review auto-generated tags
3. Enhance descriptions (be specific!)
4. Add missing CONNECT tags
5. Add missing INTENT tags
6. Add missing SPEC tags
7. Fix signature mismatches
8. Validate → should be P >= 0.90

**Time:** ~30-45 minutes per file

**Quality:** P >= 0.90 after enhancement

---

### **Workflow 3: Quick Fix (Single Function)**

1. Write tag manually using templates
2. Copy function signature exactly
3. Write specific description
4. Add secondary tags if needed
5. Save and validate

**Time:** ~2-3 minutes per function

**Quality:** Usually P >= 0.90 if careful

---

## 📚 **Learning Path**

### **Level 1: Beginner (First Week)**

1. Read this guide
2. Study gold standard: `packages/vif/witness_TAGGED.py`
3. Try auto-tagger on a small file
4. Review and enhance 5-10 tags
5. Validate and see results

**Goal:** Understand tag format and validation

---

### **Level 2: Intermediate (Week 2-3)**

1. Write tags manually for new functions
2. Use LLM assistant for suggestions
3. Add CONNECT tags for integrations
4. Add INTENT tags for design decisions
5. Achieve P >= 0.90 consistently

**Goal:** Write quality tags independently

---

### **Level 3: Advanced (Week 4+)**

1. Tag at creation time naturally
2. Achieve P >= 0.95 regularly
3. Help others with tag quality
4. Contribute to gold standards
5. Suggest tag system improvements

**Goal:** Master tagging, teach others

---

## 🎯 **Quick Reference Card**

### **Tag Formats:**

```
NL_TAG: {SYS}-{CAT}-{NNN} | {desc} | {sig} | [{deps}]
NL_TAG_CONNECT: {SYS}-CONNECT-{NNN} | {desc} | {src} → {tgt} | [{ids}]
NL_TAG_INTENT: {SYS}-DESIGN-{NNN} | {rationale} | {concept} | [{ADR}]
NL_TAG_SPEC: {SYS}-SPEC-{NNN} | {validation} | {validator} | [{schema}]
```

### **Common Commands:**

```bash
# Generate tags (auto)
python scripts/vif_auto_tagger.py packages/vif/file.py

# Generate tags (LLM)
python -c "from packages.nl_tags.llm_assisted_tagger import LLMAssistedTagger; ..."

# Validate quality
python scripts/validate_tagged_file.py packages/vif/file.py

# Commit (auto-validates)
git commit -m "Added feature with tags"
```

### **Quality Targets:**

- Coverage: >= 95% public, >= 75% internal
- Parity: P >= 0.90
- Composite: >= 0.85
- Signature: >= 0.90
- Name: >= 0.85
- Doc: >= 0.80
- Spec: >= 0.90

---

## 📖 **Additional Resources**

- **At-Creation Protocol:** `NL_TAG_AT_CREATION_PROTOCOL.md`
- **Quintet Parity Guide:** `QUINTET_PARITY_COMPREHENSIVE_GUIDE.md`
- **Troubleshooting:** `TROUBLESHOOTING_TAGS.md`
- **Tag Standard:** `PERFECT_NL_TAG_STANDARD_V2.md`
- **Gold Standards:** `packages/vif/*_TAGGED.py`
- **Tag Catalogs:** Each system has `NL_TAG_CATALOG.md`

---

## 💙 **Remember**

**Tags are not extra work - they're part of the code.**

With LLM assistant (< 1 sec) or auto-tagger (2 min), tagging is:
- Fast
- Easy
- High quality
- Self-enforcing

**Quality is built-in, not bolted-on.**

**You've got this!** 🚀

---

*Maintained by: SDF-CVF Team*  
*Last updated: 2025-11-04*  
*Questions? Check troubleshooting guide or ask in #sdfcvf*

