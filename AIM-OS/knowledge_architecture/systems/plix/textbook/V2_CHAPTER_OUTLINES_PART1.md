# PLIX Textbook v2.0: Detailed Chapter Outlines

**Status:** 📋 **IN PROGRESS**  
**Version:** 2.0.0 (Planned)  
**Date:** 2025-01-27  
**Purpose:** Detailed outlines for all 30 v2.0 chapters

---

## 📋 **PART I: FOUNDATIONS** (Chapters 1-5)

### **Chapter 1: The Question: What is Pure Language?**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag system introduction (canonical identity concept)
- ➕ Add three surface forms overview (Human-PLIX, JSON, S-form)
- ➕ Add tag-based identity examples

**Sections:**
1. The Problem We Face (keep)
2. What Makes Language "Pure"? (keep)
3. PLIx as Pure Language (enhance with tags)
4. Why Pure Language Matters (enhance with tag examples)
5. **NEW:** Tag System: The Foundation of Identity

---

### **Chapter 2: Intent vs Execution: The Fundamental Separation**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag-based identity (how tags enable separation)
- ➕ Add bitemporal model introduction
- ➕ Add tag examples showing intent-execution separation

**Sections:**
1. Defining Intent (keep)
2. Defining Execution (keep)
3. The Gap Between Them (keep)
4. The Bridge: PLIx (enhance with tags)
5. **NEW:** Tags Enable Separation (tag-based identity)

---

### **Chapter 3: The Language of Meaning and Trust**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag registry as trust foundation
- ➕ Add authority tiers and trust levels
- ➕ Add tag-based trust examples

**Sections:**
1. What is Meaning? (keep)
2. What is Trust? (keep)
3. How PLIx Enables Them (enhance with tags)
4. Philosophical Implications (keep)
5. **NEW:** Tag Registry: Foundation of Trust

---

### **Chapter 4: PLIx as the Language of AI Consciousness**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag system enables consciousness (canonical identity)
- ➕ Add intent-aware memory via tags
- ➕ Add tag-based self-awareness examples

**Sections:**
1. What is AI Consciousness? (keep)
2. How PLIx Enables It (enhance with tags)
3. The Transformative Vision (keep)
4. The Ultimate Why (keep)
5. **NEW:** Tags: Canonical Identity for Consciousness

---

### **Chapter 5: NEW - The Tag System: Canonical Identity** ⭐ **CRITICAL**
**Status:** 🆕 **NEW CHAPTER**  
**Word Count:** 3,000-3,500  
**Priority:** ⚠️ **HIGHEST** - Foundational for all subsequent chapters

**Sections:**

**5.1 Tag Format: The URN Scheme**
- Format: `plix://namespace/path#rev@hash`
- Components: namespace, path, revision, hash
- Examples: database, tool, witness tags
- Why URN scheme matters

**5.2 Tag Components Explained**
- Namespace: Entity category (`db`, `tool`, `witness`)
- Path: Hierarchical path (`table/users`, `mcp/pg.migrate`)
- Revision: Optional revision identifier
- Hash: Optional content hash for verification
- Examples of each component

**5.3 Tag Types: Entity, Capability, Evidence**
- Entity tags: `plix://db/table/users`
- Capability tags: `plix://tool/mcp/pg.migrate`
- Evidence tags: `plix://witness/schema_before`
- When to use each type

**5.4 Tag Resolution: Multi-Source Lookup**
- Resolution priority: Registry → HHNI → SEG → CMC
- Cache-first resolution
- Fallback mechanisms
- Resolution examples

**5.5 Tag Identity: Why Tags Matter**
- Canonical identity enables separation
- Tags enable timelessness
- Tags enable verifiability
- Tags enable consciousness

**5.6 Tag Examples: Real-World Usage**
- Database migration tags
- Tool capability tags
- Evidence witness tags
- Complete contract examples with tags

**Learning Objectives:**
- Understand tag format and components
- Know when to use each tag type
- Understand tag resolution process
- See tags in real-world examples

**Cross-References:**
- Chapter 15: Tag Registry (lifecycle management)
- Chapter 6: Three Surface Forms (tag usage in each form)
- Spec Section 2.1: Tag System

---

## 📋 **PART II: ARCHITECTURE** (Chapters 6-10)

### **Chapter 6: PLIX Grammar: Three Surface Forms** ⭐ **CRITICAL - RENAME & ENHANCE**
**Status:** 🔄 **RENAME from "CNL Grammar"**  
**Word Count:** 3,000-3,500 (was 2,000-2,500)  
**Priority:** ⚠️ **HIGHEST**

**Sections:**

**6.1 Human-PLIX: Indentation-Based Syntax**
- Indentation-based structure (YAML/Python-like)
- Optional delimiters (`{}`) for deep nesting
- Human-readable, developer-friendly
- Examples: Basic to complex contracts

**6.2 Canonical JSON: Machine-Executable Format**
- JSON format (JSON Schema Draft 2020-12)
- Machine-executable, AIP-compilable
- Validated via JSON Schema
- Examples: Same contracts in JSON

**6.3 S-Form: Minimal, Diff-Friendly Format**
- S-expression format (Lisp-like)
- Minimal, diff-friendly for version control
- Preserves all semantic information
- Examples: Same contracts in S-form

**6.4 When to Use Which Form**
- Human-PLIX: Development, readability
- Canonical JSON: Tooling, APIs, compilation
- S-form: Version control, diffs, minimal representation
- Decision tree for choosing form

**6.5 Round-Trip Conversion**
- Conversion invariants (semantic preservation)
- Conversion process for each pair
- Conversion examples
- Why round-trip matters

**6.6 Grammar Specification (EBNF)**
- Complete EBNF grammar reference
- Grammar rules for each form
- Grammar enhancements (logical, quantified, temporal)
- Parser requirements

**Learning Objectives:**
- Understand all three surface forms
- Know when to use each form
- Understand conversion rules
- See examples in all three forms

**Cross-References:**
- Chapter 16: Parser Implementation (parsing all three forms)
- Spec Section 3: Syntax (complete grammar)
- Spec Section 3.4: Round-Trip Conversion

---

### **Chapter 7: Enhanced Constraint Language** ⭐ **MAJOR ENHANCEMENT**
**Status:** 🔄 **MAJOR EXPANSION**  
**Word Count:** 3,000-3,500 (was basic constraints only)  
**Priority:** ⚠️ **HIGH**

**Sections:**

**7.1 Basic Constraints (Review)**
- Comparison operators (`==`, `!=`, `<=`, `>=`, `<`, `>`)
- Simple expressions
- Examples: Basic pre/postconditions

**7.2 Logical Constraints (NEW)**
- Logical operators (`AND`, `OR`, `NOT`)
- Constraint composition
- Nested logical operators
- Examples: Complex preconditions

**7.3 Quantified Constraints (NEW)**
- Universal quantifier (`FORALL`)
- Existential quantifier (`EXISTS`)
- Quantified expressions
- Examples: Database constraints, collection constraints

**7.4 Temporal Constraints (NEW)**
- Temporal operators (`EVENTUALLY`, `ALWAYS`, `WITHIN`)
- Temporal expressions
- Time-based conditions
- Examples: Timeout constraints, eventual consistency

**7.5 Constraint Composition**
- Combining constraint types
- Nested constraints
- Best practices
- Examples: Complex constraint expressions

**7.6 Constraint Evaluation**
- How constraints are evaluated
- Constraint context
- Constraint failure handling
- Examples: Evaluation scenarios

**Learning Objectives:**
- Master all constraint types
- Compose complex constraints
- Understand constraint evaluation
- Apply constraints effectively

**Cross-References:**
- Chapter 10: Error Taxonomy (constraint violation errors)
- Spec Section 3.1: Enhanced Constraint Language
- Spec Section 4.3: Type System (constraint types)

---

### **Chapter 8: Formal Validation: Alloy, TLA+, and Invariant Verification**
**Status:** ✅ Keep v1.0, enhance with errors  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add error taxonomy integration
- ➕ Add error handling in formal verification
- ➕ Add constraint violation verification

**Sections:**
1. Alloy Integration (keep)
2. TLA+ Integration (keep)
3. Invariant Verification (keep)
4. Formal Validation Workflow (keep)
5. **NEW:** Error Handling in Formal Verification

---

### **Chapter 9: Compiler Architecture: PLIx → IR → Execution Plans**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 3,000-3,500 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag resolution in compiler
- ➕ Add registry integration in compilation
- ➕ Add three surface forms → IR conversion

**Sections:**
1. PLIx IR Design (keep)
2. Lowering Process (enhance with tags)
3. Target Compilation (keep)
4. APOE Integration (keep)
5. **NEW:** Tag Resolution in Compiler
6. **NEW:** Three Surface Forms → IR Conversion

---

### **Chapter 10: NEW - Error Taxonomy and Handling** ⭐
**Status:** 🆕 **NEW CHAPTER**  
**Word Count:** 2,500-3,000  
**Priority:** ⚠️ **HIGH**

**Sections:**

**10.1 Error Categories**
- Network Errors (`NET_001`, `NET_002`, `NET_003`)
- Policy Errors (`POL_001`, `POL_002`, `POL_003`)
- Constraint Errors (`CON_001`, `CON_002`, `CON_003`)
- Contract Errors (`CTR_001`-`CTR_005`)
- Proof Errors (`PRF_001`-`PRF_003`)
- Auth Errors (`AUT_001`-`AUT_003`)
- Resource Errors (`RES_001`-`RES_003`)
- Execution Errors (`EXE_001`-`EXE_006`)

**10.2 Error Handling Clauses**
- `on_error:` syntax
- Error type matching
- Error action types
- Error configuration

**10.3 Error Actions**
- `retry`: Retry with backoff
- `compensate`: Execute compensation
- `fail`: Fail immediately
- `escalate`: Escalate to human
- `fallback`: Use fallback step

**10.4 Error Handling Examples**
- Network timeout handling
- Policy denied handling
- Constraint violation handling
- Contract failure handling

**10.5 Error Handling Best Practices**
- When to retry vs compensate
- When to escalate vs fail
- Error handling patterns
- Common pitfalls

**Learning Objectives:**
- Understand complete error taxonomy
- Know all error handling actions
- Apply error handling effectively
- Follow error handling best practices

**Cross-References:**
- Chapter 7: Enhanced Constraints (constraint errors)
- Chapter 17: Runtime Implementation (error execution)
- Spec Section 3.1: Error Taxonomy

---

**Status:** 📋 **IN PROGRESS**  
**Next:** Continue with Part III-VII outlines

