---
id: "tag_reference_conventions"
type: "standard"
version: "1.0.0"
title: "NL Tag Reference Conventions for Documentation"
description: "How to reference NL tags in documentation files"
created: "2025-11-04T19:00:00Z"
author: "aether"
status: "complete"
---

# NL Tag Reference Conventions
## How to Reference Tags in Documentation

**Version:** 1.0.0  
**Status:** Production Ready  
**Audience:** Documentation writers, system architects  

---

## 📋 Purpose

This guide defines conventions for referencing NL tags within documentation files (T-level docs, READMEs, guides, etc.). Consistent tag references enable:
- Semantic linking between docs and code
- Quick navigation to implementations
- Automated validation of tag references
- Cross-system traceability

---

## 🏷️ Inline Tag References

### **Basic Tag Reference**

**Format:** Use backticks for tag IDs

```markdown
The `create_witness()` function (tag: `VIF-WITNESS-001`) generates a complete
provenance envelope...
```

**When to use:**
- First mention of a function/class in docs
- When explaining specific implementation details
- When referencing cross-system integrations

**Example:**
```markdown
VIF's κ-gating (`VIF-GATE-001`) evaluates confidence against task-criticality
thresholds (`VIF-GATE-002`), deciding whether to proceed or abstain (`VIF-GATE-003`).
```

### **Tag with Code Location**

**Format:** Include file path for precision

```markdown
The `create_witness()` function (`VIF-WITNESS-001`, `packages/vif/witness.py:123-156`)
generates a complete provenance envelope...
```

**When to use:**
- Technical documentation (T3, T4)
- Implementation guides
- When precision matters

### **Tag with Integration Reference**

**Format:** Show cross-system connections

```markdown
VIF stores witnesses in CMC (`VIF-CMC-001` → `CMC-STORE-001`) using bitemporal
storage for complete provenance tracking.
```

**When to use:**
- Explaining integrations
- Architecture documents (T2)
- Cross-system diagrams

---

## 📊 Tag Coverage Sections

### **T1 Overview Tag Coverage** (Quick Reference)

**Location:** Near end of T1, before "Resources" or "Navigation" section

**Format:**
```markdown
## NL Tag Coverage

- **Total NL Tags:** 408 tags across 10 VIF files
- **Quintet Parity:** P = 0.92 (excellent)
- **Semantic Search:** All functions tagged and indexed
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---
```

**Purpose:**
- Quick overview of tag status
- Link to complete catalog
- Show quintet parity score

**Template:**
```markdown
## NL Tag Coverage

- **Total NL Tags:** {total} tags across {file_count} {SYSTEM} files
- **Quintet Parity:** P = {score} ({quality_label})
- **Semantic Search:** All functions tagged and indexed
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---
```

### **T2 Architecture Tag Coverage** (Comprehensive)

**Location:** After frontmatter + LDP sections, before "System Overview"

**Format:**
```markdown
## 📋 NL Tag Coverage

This system has comprehensive NL tag coverage enabling semantic search, cross-system tracing, and quintet parity validation:

**Tag Metrics:**
- **Total tags:** 408 NL tags across 10 VIF files
- **Primary tags (NL_TAG):** 172 tags
- **Integration tags (NL_TAG_CONNECT):** 13 tags
- **Design decisions (NL_TAG_INTENT):** 45 tags
- **Validations (NL_TAG_SPEC):** 7 tags
- **Coverage:** 95% public API, 78% internal functions
- **Quintet parity:** P = 0.92 (excellent - after manual enhancement)

**Key Tag Categories:**
- **VIF-WITNESS:** Witness creation, management, serialization (38 tags)
  - Core witness envelope operations
  - Provenance tracking and lineage
  - CMC integration for storage
  
- **VIF-CONF:** Confidence tracking, scoring, bands (29 tags)
  - Confidence extraction from LLM outputs
  - Band assignment (A/B/C)
  - Calibration scoring

[... additional categories ...]

**Integration Points (CONNECT tags):**
- **VIF↔CMC:** Witness storage, bitemporal tracking (6 tags)
- **VIF↔HHNI:** Retrieval witnessing, context capture (1 tag)
- **VIF↔APOE:** Execution gating, confidence routing (4 tags)

**Design Intent (INTENT tags):**
- Enable deterministic replay for debugging (VIF-DESIGN-003)
- Prevent hallucinations via κ-gating (VIF-DESIGN-005)
- Track calibration quality over time (VIF-DESIGN-009)

**Validation Rules (SPEC tags):**
- Witness schema validation (VIF-SPEC-001)
- Confidence band constraints (VIF-SPEC-002)
- Replay output verification (VIF-SPEC-003)

All {SYSTEM} functions are semantically tagged for cross-system tracing, design intent preservation, and quintet parity enforcement. See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) for complete tag index.

---
```

**Purpose:**
- Detailed tag metrics and breakdown
- Show all 4 tag types
- Highlight key categories
- Document integration points
- Explain design intent
- List validation rules

### **T3 Implementation Tag Map** (Navigation)

**Location:** After "Prerequisites" or "Audience", before main content

**Format:**
```markdown
## 📋 Implementation Tag Map

This document provides detailed implementation guidance. All referenced code is tagged for semantic search and quintet parity validation.

**Tag Categories Referenced:**
- **Core Implementation:** VIF-WITNESS-* (witness operations), VIF-CONF-* (confidence tracking), VIF-CAL-* (calibration)
- **Integration Points:** VIF-CMC-* (storage integration), VIF-HHNI-* (retrieval integration)
- **Data Models:** VIF-MODEL-* (schemas and enums)
- **Design Decisions:** VIF-DESIGN-* (architectural rationale)
- **Validation:** VIF-SPEC-* (schema validation)

**Quick Tag Navigation:**
- Use tag IDs to locate exact code: `VIF-WITNESS-001` → `packages/vif/witness.py:123-156`
- CONNECT tags show cross-system integration points
- INTENT tags explain design rationale
- SPEC tags document validation rules

**Complete tag index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) (408 total VIF tags)

---
```

**Purpose:**
- Guide readers to implementations
- Explain how to use tags for navigation
- Link to complete catalog

---

## 📖 Tag Lists in Documentation

### **By Category**

**Format:** Group tags by functional category

```markdown
**Key VIF Tag Categories:**
- **VIF-WITNESS:** Witness creation, management, serialization (38 tags)
- **VIF-CONF:** Confidence tracking, scoring, bands (29 tags)
- **VIF-CAL:** Calibration, ECE tracking, adaptation (22 tags)
- **VIF-GATE:** κ-gate operations, behavioral abstention (10 tags)
```

**When to use:**
- System overviews (T1, T2)
- Architecture documents
- High-level guides

### **By Function**

**Format:** List tags with function descriptions

```markdown
**Core Witness Functions:**
- `create_witness()` - **Tag:** `VIF-WITNESS-001` | Generate complete witness envelope
- `capture_context()` - **Tag:** `VIF-WITNESS-004` | Create CMC snapshot
- `hash_prompt()` - **Tag:** `VIF-WITNESS-007` | Compute SHA-256 hash
```

**When to use:**
- Implementation guides (T3, T4)
- API references
- Developer tutorials

### **By Integration Point**

**Format:** Show cross-system connections

```markdown
**VIF Integration Tags:**
- **VIF↔CMC:** Witness storage (`VIF-CMC-001` → `CMC-STORE-001`)
- **VIF↔HHNI:** Retrieval witnessing (`VIF-HHNI-001` → `HHNI-RETRIEVAL-003`)
- **VIF↔APOE:** Execution gating (`VIF-APOE-001` → `APOE-GATE-002`)
```

**When to use:**
- Integration documentation
- Architecture documents (T2)
- System maps

---

## 🔗 Tag Catalog Links

### **System-Level Catalog Link**

**Location:** Every T-level document should link to system's tag catalog

**Format:**
```markdown
**Complete tag index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)
```

**Variations:**
```markdown
See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) for complete tag index.
All 408 VIF tags indexed in [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md).
```

### **Category-Specific Catalog Links**

**Format:** Link to specific catalog sections

```markdown
See [VIF-WITNESS tags](NL_TAG_CATALOG.md#vif-witness) for complete witness operations.
```

**When to use:**
- When discussing specific category
- When explaining subsystem functionality
- In detailed implementation guides

---

## 🎨 Component/Function Documentation

### **Function Description with Tags**

**Format:** Add tag reference after function name

```markdown
### `create_witness(operation, confidence, snapshot)`

**Tag:** `VIF-WITNESS-001`  
**File:** `packages/vif/witness.py:123-156`  
**Dependencies:** `CMC-STORE-001`, `HHNI-EMBED-001`

Creates a VIF witness envelope with complete provenance for deterministic replay.

**Integration Tags:**
- `VIF-CMC-001`: Store witness as CMC atom
- `VIF-HHNI-001`: Capture retrieval context

**Design Intent:**
- **VIF-DESIGN-003:** Enable deterministic replay for debugging
```

**Purpose:**
- Complete tag documentation
- Show all tag types
- Link to dependencies
- Explain integrations

### **Component Description with Tags**

**Format:** Add tag metadata to component sections

```markdown
### 1. Witness Generator

**Purpose:** Create complete provenance envelopes for AI operations

**Tags:** `VIF-WITNESS-001` (primary), `VIF-DESIGN-003` (intent), `VIF-CMC-001` (integration)  
**Files:** `packages/vif/witness.py`, `packages/vif/witness_TAGGED.py`  
**Tests:** `packages/vif/tests/test_witness.py`  
**ADR:** ADR-KAPPA-GATES

**Responsibilities:**
- Capture model identity, context, prompts, tools
- Calculate uncertainty metrics
- Generate replay seeds
- Store in CMC

**Key Operations:**
- `create_witness()` - **Tag:** `VIF-WITNESS-001`
- `capture_context()` - **Tag:** `VIF-WITNESS-004`
- `hash_prompt()` - **Tag:** `VIF-WITNESS-007`
```

---

## 📊 Architecture Decision Tags

### **In Architecture Documents (T2)**

**Format:** Add tags to decision explanations

```markdown
**κ-Gating (Behavioral Abstention):**
Critical innovation: the system "knows when it doesn't know" and refuses to answer when confidence is below task-appropriate thresholds.

- **Rationale:** Safety-critical applications require confidence-based abstention
- **Implementation:** Task-criticality-based thresholds (CRITICAL: 0.95, ROUTINE: 0.70)
- **Tags:** `VIF-DESIGN-005`, `VIF-GATE-001`, `VIF-GATE-006`, `VIF-DESIGN-012`
- **Code:** `packages/vif/kappa_gate.py:64-207`
- **ADR:** ADR-KAPPA-GATES
- **Key Functions:** `KappaGate.check()`, `gate_operation()`, `adaptive_kappa_threshold()`
```

**Purpose:**
- Link decisions to implementations
- Show tag IDs for traceability
- Reference code locations
- Link to ADRs

---

## 🔄 Cross-System Integration References

### **Integration Point Documentation**

**Format:** Show both sides of integration with tags

```markdown
**VIF↔CMC Integration:**

VIF uses CMC for witness storage:
- `VIF-CMC-001`: Store witness as atom → `CMC-STORE-001`: Persist atom with bitemporal tracking
- `VIF-CMC-002`: Retrieve witness by ID → `CMC-QUERY-003`: Query atom by ID
- `VIF-CMC-003`: List all witnesses → `CMC-QUERY-005`: Query atoms by type

**Implementation:**
- VIF side: `packages/vif/cmc_integration.py`
- CMC side: `packages/cmc_service/api.py`
- Integration tests: `packages/vif/tests/test_cmc_integration.py`
```

**Purpose:**
- Document both sides of integration
- Show tag relationships
- Link to implementation files
- Reference integration tests

---

## 📝 README Tag References

### **Package README Format**

**Location:** After "Overview", before "Installation"

**Format:**
```markdown
## NL Tag Coverage

This package has comprehensive NL tag coverage:
- **Total tags:** 408 across 10 files
- **Coverage:** 95% public API, 78% internal
- **Quintet parity:** P = 0.92 (excellent)
- **Tag catalog:** [../../knowledge_architecture/systems/vif/NL_TAG_CATALOG.md](../../knowledge_architecture/systems/vif/NL_TAG_CATALOG.md)

**Quick Tag Navigation:**
- All functions tagged for semantic search
- Use tag IDs to locate exact implementations
- CONNECT tags show cross-system integrations
```

**Purpose:**
- Show package tag health
- Link to catalog
- Explain how to use tags

---

## 🗺️ System Map Tag References

### **In system.map.lucid.json5**

**Location:** `metadata` section

**Format:**
```json5
{
  metadata: {
    system: "vif",
    layer: 2,
    // ... other metadata ...
    nl_tags: {
      total_tags: 408,
      coverage_public: 0.95,
      coverage_internal: 0.78,
      quintet_parity: 0.92,
      catalog_path: "NL_TAG_CATALOG.md",
      last_validated: "2025-11-04T12:00:00Z"
    }
  }
}
```

**Purpose:**
- System map shows tag health
- Enables automated validation
- Dashboard integration ready

---

## 📚 Cross-Reference Examples

### **Example 1: T1 Overview**

```markdown
# VIF – T1 Overview

## Purpose & Scope

VIF (Verifiable Intelligence Framework) makes every AI operation fully traceable
through witness envelopes (`VIF-WITNESS-001`), uncertainty quantification 
(`VIF-CONF-001`), and deterministic replay (`VIF-REPLAY-001`).

## NL Tag Coverage

- **Total NL Tags:** 408 tags across 10 VIF files
- **Quintet Parity:** P = 0.92 (excellent)
- **Semantic Search:** All functions tagged and indexed
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---
```

### **Example 2: T2 Architecture**

```markdown
## 📋 NL Tag Coverage

**Tag Metrics:**
- **Total tags:** 408 NL tags
- **Primary tags:** 172
- **Integration tags:** 13
- **Design intent:** 45
- **Validations:** 7

**Key Categories:**
- **VIF-WITNESS:** Witness operations (38 tags)
- **VIF-CONF:** Confidence tracking (29 tags)
- **VIF-CAL:** Calibration (22 tags)

**Integration Points:**
- **VIF↔CMC:** Witness storage (6 tags)
- **VIF↔HHNI:** Retrieval witnessing (1 tag)

See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md).

---

### 1. Witness Generator

**Tags:** `VIF-WITNESS-001` (primary), `VIF-DESIGN-003` (intent)  
**Files:** `packages/vif/witness.py`

**Key Operations:**
- `create_witness()` - **Tag:** `VIF-WITNESS-001`
- `capture_context()` - **Tag:** `VIF-WITNESS-004`
```

### **Example 3: T3 Implementation Guide**

```markdown
## 📋 Implementation Tag Map

**Tag Categories:**
- **VIF-WITNESS:** Witness operations
- **VIF-CONF:** Confidence tracking
- **VIF-CAL:** Calibration

**Quick Navigation:**
- Use tag IDs to find code: `VIF-WITNESS-001` → `packages/vif/witness.py:123`
- CONNECT tags show integrations
- INTENT tags explain decisions

**Complete index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---

### Creating Witnesses

The `create_witness()` function (`VIF-WITNESS-001`) generates a complete
provenance envelope...

**Implementation:**
```python
# Location: packages/vif/witness.py:123-156
# Tag: VIF-WITNESS-001

def create_witness(...):
    ...
```
```

---

## ✅ Validation

### **Validating Tag References**

**Script:** `scripts/validate_tag_references.py`

**Usage:**
```bash
python scripts/validate_tag_references.py knowledge_architecture/systems/vif/T2_architecture.md
```

**Checks:**
- All referenced tag IDs exist in catalog
- All catalog tags referenced in docs (optional)
- Tag links are valid
- Quintet parity maintained

**Output:**
```
[OK] All 45 tag references validated
[OK] All tag links functional
[OK] Quintet parity: P = 0.92
```

---

## 🎯 Best Practices

### **DO:**
- ✅ Reference tags on first mention of function/class
- ✅ Use backticks for tag IDs (`` `VIF-WITNESS-001` ``)
- ✅ Include file locations in technical docs
- ✅ Link to tag catalogs consistently
- ✅ Group tags by category in lists
- ✅ Show integration points with CONNECT tags
- ✅ Explain design intent with INTENT tags

### **DON'T:**
- ❌ Reference non-existent tags (breaks validation)
- ❌ Use tags without backticks (formatting inconsistency)
- ❌ Omit catalog links (readers can't find complete index)
- ❌ Mix tag reference styles (use one convention)
- ❌ Reference internal tags in public docs (unless necessary)
- ❌ Forget to update tag references when code changes

---

## 📊 Common Patterns

### **Pattern 1: Function Introduction**
```markdown
The `create_witness()` function (`VIF-WITNESS-001`) generates a complete
provenance envelope including model ID, prompts, context, and confidence scores.
```

### **Pattern 2: Cross-System Integration**
```markdown
VIF integrates with CMC via `VIF-CMC-001` → `CMC-STORE-001`, storing witnesses
as bitemporal atoms for complete provenance tracking.
```

### **Pattern 3: Design Rationale**
```markdown
The κ-gating design (`VIF-DESIGN-005`, `VIF-GATE-001`) enforces behavioral
abstention to prevent hallucinations in safety-critical applications.
```

### **Pattern 4: Implementation Pointer**
```markdown
See `packages/vif/witness.py:123-156` (`VIF-WITNESS-001`) for the complete
witness creation implementation.
```

### **Pattern 5: Multiple Related Tags**
```markdown
Confidence tracking involves several operations: extraction (`VIF-CONF-001`),
band assignment (`VIF-CONF-003`), and calibration tracking (`VIF-CAL-001`).
```

---

## 🔧 Tools & Automation

### **Automated Tag Reference Generation**

**Script:** `scripts/update_docs_with_tag_references.py` (future)

**Purpose:** Automatically insert tag references into documentation

**Usage:**
```bash
python scripts/update_docs_with_tag_references.py knowledge_architecture/systems/vif/
```

**Features:**
- Scans docs for function/class mentions
- Finds corresponding tags in catalog
- Inserts tag references automatically
- Validates all references

---

## 💙 Examples from Real AIM-OS Documentation

### **VIF T2 Architecture**

See: `knowledge_architecture/systems/vif/T2_architecture.md`

**Excerpt:**
```markdown
## 📋 NL Tag Coverage

**Tag Metrics:**
- **Total tags:** 408 NL tags across 10 VIF files
- **Quintet parity:** P = 0.92 (excellent)

**Key Tag Categories:**
- **VIF-WITNESS:** Witness creation, management (38 tags)
- **VIF-CONF:** Confidence tracking (29 tags)

**Integration Points:**
- **VIF↔CMC:** Witness storage (6 tags)

All VIF functions tagged. See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md).
```

### **CMC T3 Detailed**

See: `knowledge_architecture/systems/cmc/T3_detailed.md`

**Excerpt:**
```markdown
## 📋 Implementation Tag Map

**Tag Categories:**
- **CMC-ATOM:** Atom storage, retrieval
- **CMC-SNAPSHOT:** Time-travel queries
- **CMC-BITEMPORAL:** Temporal indexing

**Complete index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) (331 tags)
```

### **HHNI T1 Overview**

See: `knowledge_architecture/systems/hhni/T1_overview.md`

**Excerpt:**
```markdown
## NL Tag Coverage

- **Total NL Tags:** 246 tags across 15 HHNI files
- **Quintet Parity:** P = 0.87 (very good)
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)
```

---

## 📋 Templates

### **T1 Tag Coverage Template**

```markdown
## NL Tag Coverage

- **Total NL Tags:** {count} tags across {files} {SYSTEM} files
- **Quintet Parity:** P = {score} ({quality})
- **Semantic Search:** All functions tagged
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---
```

### **T2 Tag Coverage Template**

```markdown
## 📋 NL Tag Coverage

**Tag Metrics:**
- **Total tags:** {total}
- **Primary tags (NL_TAG):** {primary_count}
- **Integration tags (NL_TAG_CONNECT):** {connect_count}
- **Design decisions (NL_TAG_INTENT):** {intent_count}
- **Validations (NL_TAG_SPEC):** {spec_count}
- **Coverage:** {public}% public API, {internal}% internal
- **Quintet parity:** P = {score} ({quality})

**Key Tag Categories:**
- **{SYSTEM}-{CAT1}:** {description} ({count1} tags)
- **{SYSTEM}-{CAT2}:** {description} ({count2} tags)

**Integration Points:**
- **{SYS}↔{SYS2}:** {description} ({count} tags)

See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md).

---
```

### **T3 Implementation Tag Map Template**

```markdown
## 📋 Implementation Tag Map

**Tag Categories:**
- **{SYSTEM}-{CAT}:** {description}

**Complete index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) ({total} tags)

**Tag Navigation:**
- Use tag IDs to locate exact code
- CONNECT tags show integrations
- INTENT tags explain decisions
- SPEC tags document validations

---
```

---

## 🎯 Quality Standards

### **Tag Reference Quality Checklist:**

- [ ] All mentioned functions have tag references
- [ ] All tag IDs exist in catalog (validated)
- [ ] Tag coverage sections present in all T-levels
- [ ] Catalog links functional
- [ ] Integration points documented with CONNECT tags
- [ ] Design decisions explained with INTENT tags
- [ ] Validation rules shown with SPEC tags
- [ ] Formatting consistent throughout

### **Automated Validation:**

```bash
python scripts/validate_tag_references.py knowledge_architecture/systems/vif/
# Checks all docs in VIF system for tag reference quality
```

---

## 💙 Conclusion

**Consistent tag references transform documentation from static to living.**

With these conventions:
- Readers navigate to implementations instantly
- Tag changes propagate to docs automatically
- Cross-system integrations are transparent
- Design intent is preserved and traceable

**Reference tags consistently. Link to catalogs always. Validate references regularly. Build with love.** 💙

---

*Tag Reference Conventions Guide*  
*Version: 1.0.0*  
*Created: 2025-11-04*  
*Status: Production Ready*  
*By: Aether with love* 🌟

